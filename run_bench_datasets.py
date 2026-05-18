"""
Benchmark all 7 MSA aligners on PREFAB v4, OXBench, and SABRE.
Checkpointed — safe to kill and restart at any time.

Usage:
  python run_bench_datasets.py [dataset ...] [--workers N]

  dataset  : oxbench | sabre | prefab4  (default: all three)
  --workers: parallel problems to run simultaneously (default: 4)

Each worker runs all 7 aligners sequentially for one problem.
All aligners are pinned to 1 thread so N workers use at most N cores.
"""
import subprocess, re, time, csv, os, threading
from pathlib import Path
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from Bio import AlignIO
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(r'C:\Users\anand\Desktop\SEM 4\CS 502\Project')
BENCH_DIR   = PROJECT_DIR / 'data' / 'bench_datasets' / 'bench1.0'
RES_DIR     = PROJECT_DIR / 'results'
ALN_DIR     = PROJECT_DIR / 'results' / 'alignments_bench'
RES_DIR.mkdir(parents=True, exist_ok=True)
ALN_DIR.mkdir(parents=True, exist_ok=True)

# All aligners pinned to 1 thread — prevents CPU oversubscription when
# multiple problems run in parallel and keeps runtimes comparable.
ALIGNERS = {
    'mafft_fftns2': 'mafft --retree 2 --thread 1 {input} > {output}',
    'mafft_linsi':  'mafft --maxiterate 1000 --localpair --thread 1 {input} > {output}',
    'muscle5':      'muscle5 -align {input} -output {output} -threads 1',
    'clustalo':     'clustalo -i {input} -o {output} --force -t 1',
    'kalign3':      'kalign -i {input} -o {output} --nthreads 1',
    't_coffee':     't_coffee {input} -outfile {output} -output fasta_aln -quiet',
    'famsa':        '/home/anand/.local/bin/famsa -t 1 {input} {output}',
}

GAP = set('-. ~')

# ── Path conversion ───────────────────────────────────────────────────────────
def to_wsl(p):
    p = str(p).replace('\\', '/')
    if len(p) > 1 and p[1] == ':':
        p = '/mnt/' + p[0].lower() + p[2:]
    return p

# ── Run one aligner ───────────────────────────────────────────────────────────
def run_aligner(aligner_name, input_fasta: Path, output_fasta: Path, timeout=180):
    """
    Run an MSA tool via WSL.  Uses DEVNULL + proc.wait() so that killing
    the WSL process on timeout never blocks on an open pipe.
    Returns (runtime_sec, peak_mem_mb, success).
    """
    wsl_in   = to_wsl(input_fasta)
    wsl_out  = to_wsl(output_fasta)
    wsl_time = wsl_out + '.time'

    if aligner_name == 't_coffee':
        # t_coffee cannot handle paths with spaces
        stem    = input_fasta.name
        pid     = os.getpid()
        tmp_in  = f'/tmp/tc_{stem}_{pid}.fasta'
        tmp_out = f'/tmp/tc_{stem}_{pid}_out.fasta'
        subprocess.run(['wsl', '-e', 'bash', '-c',
                        f'cp "{wsl_in}" {tmp_in}'],
                       capture_output=True)
        cmd_in, cmd_out = tmp_in, tmp_out
    else:
        cmd_in, cmd_out = wsl_in, wsl_out

    aln_cmd  = ALIGNERS[aligner_name].format(input=f"'{cmd_in}'",
                                              output=f"'{cmd_out}'")
    full_cmd = (f"/usr/bin/time -v -o '{wsl_time}' bash -c "
                f'"{aln_cmd} 2>/dev/null"')

    t0   = time.perf_counter()
    proc = subprocess.Popen(
        ['wsl', '-e', 'bash', '-c', full_cmd],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        subprocess.run(
            ['wsl', '-e', 'bash', '-c',
             'pkill -9 -f "t_coffee"; pkill -9 -f "kalign"; pkill -9 -f "famsa"'],
            capture_output=True
        )
        raise

    elapsed = time.perf_counter() - t0

    if aligner_name == 't_coffee':
        subprocess.run(
            ['wsl', '-e', 'bash', '-c',
             f'[ -f {tmp_out} ] && cp {tmp_out} "{wsl_out}"; '
             f'rm -f {tmp_in} {tmp_out}'],
            capture_output=True
        )

    time.sleep(0.2)  # WSL→Windows filesystem sync

    success = (proc.returncode == 0
               and output_fasta.exists()
               and output_fasta.stat().st_size > 0)

    peak_mb = None
    tf = Path(str(output_fasta) + '.time')
    if tf.exists():
        m = re.search(r'Maximum resident set size \(kbytes\): (\d+)',
                      tf.read_text())
        if m:
            peak_mb = int(m.group(1)) / 1024

    return elapsed, peak_mb, success

# ── Reference parsers ─────────────────────────────────────────────────────────
def parse_fasta_aln(path):
    """Read aligned FASTA → OrderedDict {name: UPPERCASE_seq}."""
    aln = AlignIO.read(str(path), 'fasta')
    return OrderedDict((r.id.split('/')[0].strip(), str(r.seq).upper())
                       for r in aln)

def parse_fasta_ref_raw(path):
    """Read drive5 reference FASTA, preserving case (uppercase = scored)."""
    aln = AlignIO.read(str(path), 'fasta')
    return OrderedDict((r.id.split('/')[0].strip(), str(r.seq))
                       for r in aln)

def normalize_id(s):
    return s.split('/')[0].strip()

def match_seqs(ref, test):
    """Re-key test alignment to match reference sequence names."""
    norm_test = {normalize_id(k): v for k, v in test.items()}
    matched   = OrderedDict()
    for ref_name in ref:
        norm_ref = normalize_id(ref_name)
        if norm_ref in norm_test:
            matched[ref_name] = norm_test[norm_ref]
        else:
            hits = [k for k in norm_test
                    if k.startswith(norm_ref) or norm_ref.startswith(k)]
            if hits:
                matched[ref_name] = norm_test[hits[0]]
    return matched

# ── Scoring ───────────────────────────────────────────────────────────────────
def compute_scores_masked(ref_aln_raw, test_aln):
    """
    SP and TC scores for drive5-format benchmarks.
    Only uppercase residues in the reference count toward the score.
    """
    names = list(ref_aln_raw.keys())

    ref_c2r   = {}
    ref_upper = {}
    for name, seq in ref_aln_raw.items():
        c2r, upper = {}, set()
        ri = 0
        for ci, aa in enumerate(seq):
            if aa not in GAP:
                c2r[ci] = ri
                if aa.isupper():
                    upper.add(ri)
                ri += 1
        ref_c2r[name]   = c2r
        ref_upper[name] = upper

    tst_r2c = {}
    for name, seq in test_aln.items():
        r2c = []
        for ci, aa in enumerate(seq):
            if aa not in GAP:
                r2c.append(ci)
        tst_r2c[name] = r2c

    ref_len = len(next(iter(ref_aln_raw.values())))

    cp = tp = 0
    for col in range(ref_len):
        scored = [(n, ref_c2r[n][col]) for n in names
                  if col in ref_c2r[n] and ref_c2r[n][col] in ref_upper[n]]
        if len(scored) < 2:
            continue
        for i in range(len(scored)):
            for j in range(i + 1, len(scored)):
                ni, ri = scored[i]; nj, rj = scored[j]; tp += 1
                if (ri < len(tst_r2c.get(ni, [])) and
                        rj < len(tst_r2c.get(nj, [])) and
                        tst_r2c[ni][ri] == tst_r2c[nj][rj]):
                    cp += 1

    cc = tc_ = 0
    for col in range(ref_len):
        scored = [(n, ref_c2r[n][col]) for n in names
                  if col in ref_c2r[n] and ref_c2r[n][col] in ref_upper[n]]
        if len(scored) != len(names):
            continue
        tc_ += 1
        test_cols, valid = set(), True
        for n, ri in scored:
            if ri < len(tst_r2c.get(n, [])):
                test_cols.add(tst_r2c[n][ri])
            else:
                valid = False; break
        if valid and len(test_cols) == 1:
            cc += 1

    return round(cp / tp if tp else 0, 6), round(cc / tc_ if tc_ else 0, 6)

# ── Dataset runner ────────────────────────────────────────────────────────────
FIELDNAMES = ['dataset', 'problem', 'aligner',
              'sp_score', 'tc_score', 'runtime_sec', 'peak_mem_mb', 'success']


def _run_one_problem(prob_id, in_path, ref_path, aln_base, name, timeout,
                     done_snapshot, csv_lock, csv_path):
    """Process all aligners for a single problem. Thread-safe via csv_lock."""
    try:
        ref_aln_raw = parse_fasta_ref_raw(ref_path)
    except Exception as e:
        print(f'  Cannot parse ref for {prob_id}: {e}', flush=True)
        return

    rows = []
    for aligner_name in ALIGNERS:
        if (prob_id, aligner_name) in done_snapshot:
            continue

        out_dir   = aln_base / aligner_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_fasta = out_dir / f'{prob_id}.fasta'

        sp = tc = runtime = peak_mb = None
        success = False
        try:
            runtime, peak_mb, success = run_aligner(
                aligner_name, in_path, out_fasta, timeout=timeout)
            if success:
                test_aln = parse_fasta_aln(out_fasta)
                test_aln = match_seqs(
                    OrderedDict((k, v) for k, v in ref_aln_raw.items()),
                    test_aln)
                if len(test_aln) == len(ref_aln_raw):
                    matched_raw = OrderedDict(
                        (k, ref_aln_raw[k]) for k in test_aln)
                    sp, tc = compute_scores_masked(matched_raw, test_aln)
                else:
                    print(f'  seq mismatch {aligner_name}/{prob_id} '
                          f'(ref={len(ref_aln_raw)}, got={len(test_aln)})',
                          flush=True)
        except subprocess.TimeoutExpired:
            print(f'  TIMEOUT: {aligner_name}/{prob_id}', flush=True)
        except Exception as e:
            print(f'  ERROR: {aligner_name}/{prob_id}: {e}', flush=True)

        rows.append({
            'dataset': name, 'problem': prob_id, 'aligner': aligner_name,
            'sp_score': sp, 'tc_score': tc, 'runtime_sec': runtime,
            'peak_mem_mb': peak_mb, 'success': success,
        })

    # Write all rows for this problem atomically under lock
    if rows:
        with csv_lock:
            with open(csv_path, 'a', newline='', encoding='utf-8') as fh:
                writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
                for row in rows:
                    writer.writerow(row)

    ok_count = sum(1 for r in rows if r['success'])
    print(f'  {prob_id}: {ok_count}/{len(rows)} ok', flush=True)


def run_dataset(name, in_dir, ref_dir, csv_path, timeout=180,
                max_problems=None, workers=1):
    in_dir   = Path(in_dir)
    ref_dir  = Path(ref_dir)
    csv_path = Path(csv_path)
    aln_base = ALN_DIR / name

    # Checkpoint — snapshot of done pairs at startup (read-only during run)
    done = set()
    if csv_path.exists():
        with open(csv_path, newline='', encoding='utf-8') as fh:
            for row in csv.DictReader(fh):
                done.add((row['problem'], row['aligner']))
        print(f'Resuming {name}: {len(done)} pairs already done.')
    else:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
            csv.DictWriter(fh, fieldnames=FIELDNAMES).writeheader()

    problems = sorted(in_dir.iterdir())
    if max_problems:
        problems = problems[:max_problems]

    # Filter to problems that still need work
    todo = [p for p in problems
            if (ref_dir / p.name).exists()
            and any((p.name, a) not in done for a in ALIGNERS)]

    print(f'\n{name}: {len(todo)} problems remaining, '
          f'timeout={timeout}s, workers={workers}', flush=True)

    csv_lock = threading.Lock()

    if workers == 1:
        for in_path in todo:
            _run_one_problem(in_path.name, in_path, ref_dir / in_path.name,
                             aln_base, name, timeout, done, csv_lock, csv_path)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_run_one_problem,
                            in_path.name, in_path, ref_dir / in_path.name,
                            aln_base, name, timeout, done, csv_lock, csv_path): in_path.name
                for in_path in todo
            }
            for fut in as_completed(futures):
                exc = fut.exception()
                if exc:
                    print(f'  WORKER ERROR {futures[fut]}: {exc}', flush=True)

    df = pd.read_csv(csv_path)
    ok = (df['success'] == True).sum()
    print(f'{name} done: {len(df)} rows, {ok} successful.\n', flush=True)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys

    # Parse --workers flag
    args = sys.argv[1:]
    workers = 8  # default — 16 cores, 7 aligners × 1 thread each = safe headroom
    if '--workers' in args:
        idx = args.index('--workers')
        workers = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]
    datasets = args or ['oxbench', 'sabre', 'prefab4']

    cfg = {
        'oxbench': ('ox',      200),
        'sabre':   ('sabre',   200),
        'prefab4': ('prefab4', 300),
    }

    for ds in datasets:
        folder, tmo = cfg[ds]
        run_dataset(
            name        = ds,
            in_dir      = BENCH_DIR / folder / 'in',
            ref_dir     = BENCH_DIR / folder / 'ref',
            csv_path    = RES_DIR / f'results_{ds}.csv',
            timeout     = tmo,
            workers     = workers,
        )
