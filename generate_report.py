"""
Generate the CS 502 Final Report as a Word (.docx) document.
Times New Roman 12pt body, 10pt captions/tables, 1.25-inch side margins.
Target: 4-6 pages including figures and tables.
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path

FIG_DIR  = Path(r'C:\Users\anand\Desktop\SEM 4\CS 502\Project\figures')
OUT_PATH = Path(r'C:\Users\anand\Desktop\SEM 4\CS 502\Project\MSA_Benchmark_Final_Report.docx')

# ── Utility helpers ────────────────────────────────────────────────────────────
def font(run, name='Times New Roman', size=12, bold=False, italic=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic

def para(doc, text='', align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         sb=0, sa=5, size=12, bold=False, italic=False, indent=None):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after  = Pt(sa)
    if indent is not None:
        p.paragraph_format.first_line_indent = Inches(indent)
    if text:
        r = p.add_run(text)
        font(r, size=size, bold=bold, italic=italic)
    return p

def heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8 if level == 1 else 5)
    p.paragraph_format.space_after  = Pt(2)
    r = p.add_run(text.upper() if level == 1 else text)
    font(r, size=12 if level == 1 else 11, bold=True)

def figure(doc, fname, width=4.8, caption='', fig_num=None):
    path = FIG_DIR / fname
    if path.exists():
        ip = doc.add_paragraph()
        ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ip.paragraph_format.space_before = Pt(4)
        ip.paragraph_format.space_after  = Pt(0)
        ip.add_run().add_picture(str(path), width=Inches(width))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after  = Pt(6)
    if fig_num:
        r = cp.add_run(f'Figure {fig_num}. ')
        font(r, size=10, bold=True)
    r2 = cp.add_run(caption)
    font(r2, size=10, italic=True)

def shade_cell(cell, fill='D9E1F2'):
    tcPr = cell._tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)

def add_table(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.style = 'Table Grid'
    hcells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hcells[i].text = h
        shade_cell(hcells[i])
        for p2 in hcells[i].paragraphs:
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p2.runs:
                font(r, size=10, bold=True)
    for row_vals in rows:
        row = tbl.add_row()
        for i, val in enumerate(row_vals):
            row.cells[i].text = str(val)
            for p2 in row.cells[i].paragraphs:
                p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p2.runs:
                    font(r, size=10)
    if col_widths:
        for row in tbl.rows:
            for i, cell in enumerate(row.cells):
                if i < len(col_widths):
                    cell.width = Inches(col_widths[i])
    return tbl

# ── Build document ─────────────────────────────────────────────────────────────
doc = Document()
for sec in doc.sections:
    sec.top_margin    = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin   = Inches(1.25)
    sec.right_margin  = Inches(1.25)

# Default paragraph style: TNR 12
doc.styles['Normal'].font.name = 'Times New Roman'
doc.styles['Normal'].font.size = Pt(12)

# ── Title block ────────────────────────────────────────────────────────────────
tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tp.paragraph_format.space_after = Pt(4)
r = tp.add_run('Systematic Benchmarking of Multiple Sequence Alignment\n'
               'Algorithms on Structurally-Informed Reference Datasets')
font(r, size=15, bold=True)

ap = doc.add_paragraph()
ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
ap.paragraph_format.space_after = Pt(1)
r = ap.add_run('Anand Meena')
font(r, size=12)
r = ap.add_run('  |  ')
font(r, size=12)
r = ap.add_run('ameen4@uic.edu')
font(r, size=11, italic=True)

ap2 = doc.add_paragraph()
ap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
ap2.paragraph_format.space_after = Pt(2)
r = ap2.add_run('Shruthi Kodati')
font(r, size=12)
r = ap2.add_run('  |  ')
font(r, size=12)
r = ap2.add_run('skoda13@uic.edu')
font(r, size=11, italic=True)

cp2 = doc.add_paragraph()
cp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
cp2.paragraph_format.space_after = Pt(10)
r = cp2.add_run('CS 502 — Computational Biology  |  Spring 2026')
font(r, size=11)

# ── Abstract ──────────────────────────────────────────────────────────────────
heading(doc, 'Abstract')
para(doc,
     'We present a systematic evaluation of seven widely-used multiple sequence alignment '
     '(MSA) tools—MAFFT FFT-NS-2, MAFFT L-INS-i, MUSCLE5, Clustal Omega, Kalign3, '
     'T-Coffee, and FAMSA—across 2,885 protein families from four reference benchmarks: '
     'BAliBASE 3.0, OXBench, SABRE, and PREFAB4. Alignments were scored using Sum-of-Pairs '
     '(SP) and Total Column (TC) metrics with structure-based masking. A Friedman test '
     'confirmed highly significant global differences (chi^2 = 935.73, p < 10^-199). '
     'On BAliBASE 3.0, MUSCLE5 achieved the highest mean SP (0.761), followed by '
     'T-Coffee (0.746) and MAFFT L-INS-i (0.743). Nemenyi post-hoc tests identified '
     'three performance tiers: {MUSCLE5}, {T-Coffee, MAFFT L-INS-i}, and '
     '{MAFFT FFT-NS-2, Kalign3}. T-Coffee failed 11% of problems due to O(N^2) '
     'scalability limits. FAMSA provided the best accuracy-speed trade-off among '
     'high-accuracy tools (median 0.19 s, SP = 0.718). Rankings generalized across '
     'all four benchmarks, supporting MUSCLE5 as the top single-threaded aligner '
     'when accuracy is prioritized.',
     indent=0.3, sa=4)

# ── Introduction ──────────────────────────────────────────────────────────────
heading(doc, 'Introduction')
para(doc,
     'Multiple sequence alignment (MSA) is a foundational step in phylogenetic '
     'reconstruction, homology modelling, and conserved domain detection. The field '
     'has converged on several dominant tools embodying different algorithmic strategies: '
     'progressive alignment (Clustal Omega, FAMSA, Kalign3) achieves near-linear scaling '
     'by building a guide tree; iterative refinement (MAFFT L-INS-i, MUSCLE5) escapes '
     'local optima through repeated realignment; and consistency-based methods (T-Coffee) '
     'use pairwise alignment libraries to generate position-specific scoring matrices. '
     'Despite numerous prior benchmarks, comprehensive multi-dataset comparisons with '
     'rigorous statistical testing across diverse evolutionary challenges remain scarce.',
     indent=0.3, sa=4)

para(doc,
     'Our project began with four aligners (MAFFT FFT-NS-2, MAFFT L-INS-i, MUSCLE5, and '
     'Clustal Omega) on BAliBASE 3.0 alone. After completing the core run we expanded scope '
     'in three directions: (i) added Kalign3, T-Coffee, and FAMSA to capture the full '
     'spectrum of progressive, consistency-based, and modern column-reuse algorithms; '
     '(ii) added OXBench, SABRE, and PREFAB4 to assess generalization beyond BAliBASE; '
     'and (iii) extended the statistical analysis with Friedman, Nemenyi post-hoc, '
     'and bootstrap confidence intervals.',
     indent=0.3, sa=4)

para(doc,
     'We hypothesize that (1) iterative and consistency-based tools significantly outperform '
     'progressive methods on structurally challenging families; (2) accuracy gaps narrow '
     'for closely related sequences; and (3) FAMSA provides the optimal speed-accuracy '
     'trade-off among broadly applicable tools. To test these hypotheses we benchmarked '
     'all seven tools on 2,885 curated reference alignments, applied Wilcoxon signed-rank '
     'tests with Bonferroni/BH correction, Nemenyi post-hoc analysis, and bootstrap '
     'confidence intervals stratified by reference set and sequence identity.',
     indent=0.3, sa=4)

# ── Methods ───────────────────────────────────────────────────────────────────
heading(doc, 'Methods')

heading(doc, 'Datasets', level=2)
para(doc,
     'Four benchmarks were used. BAliBASE 3.0 (BB3) contains 386 manually curated structural '
     'alignments in six reference sets: RV11 (<25% identity, <40 sequences), RV12 (<25% '
     'identity, >40 sequences), RV20 (N/C-terminal extensions), RV30 (internal insertions), '
     'RV40 (transmembrane proteins), and RV50 (circular permutations). OXBench provides '
     '395 alignments from 3D structural superposition; SABRE contains 423 diverse structural '
     'families; PREFAB4 contains 1,681 pairwise-guided benchmark pairs. '
     'In all cases, the reference alignments serve as structural ground truth: BAliBASE 3.0 '
     'and OXBench alignments are derived from 3D crystal structure superposition, anchoring '
     'column-level correctness to atomic coordinates rather than sequence similarity. '
     'This evaluation convention follows the systematic MSA benchmarking framework of '
     'Santus et al. (2025), implemented in the nf-core/multiplesequencealign pipeline '
     '(https://github.com/nf-core/multiplesequencealign), who likewise use '
     'structurally-derived reference alignments as ground truth for SP and TC scoring '
     'across multiple tools and datasets '
     '(NAR Genomics and Bioinformatics, doi:10.1093/nargab/lqaf104).',
     indent=0.3, sa=4)

heading(doc, 'Tools and Execution', level=2)
para(doc,
     'All tools were run under WSL2 (Ubuntu 22.04) pinned to a single CPU thread for '
     'comparability: MAFFT v7.5 (FFT-NS-2: --retree 2; L-INS-i: --maxiterate 1000 '
     '--localpair), MUSCLE5 v5.1 (-threads 1), Clustal Omega v1.2.4 (--force), '
     'Kalign3 v3.3.5 (--nthreads 1), T-Coffee v13.46 (-output fasta_aln), and '
     'FAMSA v2.5.2 (-t 1). Per-problem timeouts: 200 s (BB3/OXBench/SABRE) and '
     '300 s (PREFAB4). Peak RSS was recorded via /usr/bin/time -v.',
     indent=0.3, sa=4)

heading(doc, 'Scoring and Statistics', level=2)
para(doc,
     'The official bali_score binary failed to compile under modern WSL due to glibc '
     'version mismatches, so we reimplemented SP and TC scoring natively in Python '
     'following the original methodology and validated outputs by manual inspection '
     'against published BAliBASE numbers. SP score counts the fraction of reference '
     'residue pairs co-aligned in the test; TC score counts perfectly reproduced '
     'reference columns. For BB3, OXBench, and SABRE (drive5 format), only uppercase '
     'residues in the reference—structurally well-defined core blocks—contribute. '
     'BAliBASE references are stored as MSF files while OXBench, SABRE, and PREFAB4 '
     'use FASTA; we wrote format-specific parsers that converge on a common '
     'OrderedDict representation before scoring. Reference and test sequences are '
     'matched on normalized FASTA identifiers; problems where any reference sequence '
     'is missing from the test are reported as failures.',
     indent=0.3, sa=4)
para(doc,
     'All pairwise comparisons used Wilcoxon signed-rank tests corrected by '
     'Bonferroni and Benjamini-Hochberg (FDR 5%) procedures. Effect sizes used '
     'Cliff\'s delta (negligible |delta| < 0.147, small < 0.33). Global significance '
     'was assessed by Friedman test; Nemenyi post-hoc identified indistinguishable '
     'groups. Bootstrap 95% CIs (10,000 resamples) were computed overall and per '
     'reference set. Runtime differences used Wilcoxon tests on log-transformed times.',
     indent=0.3, sa=4)

# ── Results ───────────────────────────────────────────────────────────────────
heading(doc, 'Results')

heading(doc, 'Overall Accuracy on BAliBASE 3.0', level=2)
para(doc,
     'MUSCLE5 achieved the highest mean SP score (0.761 +/- 0.174), followed by T-Coffee '
     '(0.746 +/- 0.182) and MAFFT L-INS-i (0.743 +/- 0.188). FAMSA and Clustal Omega '
     'occupied a middle tier (SP ~0.718), while MAFFT FFT-NS-2 and Kalign3 were lowest '
     '(0.688 and 0.692, respectively). TC score rankings were consistent. The Friedman '
     'test on SP scores yielded chi^2 = 935.73 (df = 6, p = 7.07 x 10^-199), '
     'decisively rejecting equal performance across tools (Figure 1). All 21 pairwise '
     'BH-corrected comparisons were significant except MAFFT FFT-NS-2 vs. Kalign3 '
     '(p = 0.524, Cliff\'s delta = -0.019, negligible). Nemenyi post-hoc tests '
     'identified three statistically indistinguishable tiers: (1) MUSCLE5; '
     '(2) T-Coffee and MAFFT L-INS-i (p = 0.847); (3) MAFFT FFT-NS-2 and Kalign3 '
     '(p = 0.843); with Clustal Omega and FAMSA forming an intermediate cluster '
     '(p = 0.471 between each other). Effect sizes were modest throughout '
     '(maximum |delta| = 0.22 for MUSCLE5 vs. Kalign3), indicating consistent '
     'but practically small per-problem differences.',
     indent=0.3, sa=4)

figure(doc, 'fig1_accuracy_overall.png', width=4.8,
       caption='SP and TC score distributions on BAliBASE 3.0 (n=386). '
               'Boxes show IQR; lines are medians; whiskers extend 1.5x IQR.',
       fig_num=1)

# Table 1 – Summary
tp2 = para(doc, 'Table 1. Accuracy and runtime summary on BAliBASE 3.0 (n = 386). '
                'Runtime is median wall-clock time (s). Memory is median peak RSS (MB).',
           italic=True, size=10, sa=2, sb=6)

add_table(doc,
    headers=['Aligner', 'SP Mean±SD', 'TC Mean±SD', 'Runtime (s)', 'Mem (MB)', 'N ok'],
    rows=[
        ('MUSCLE5',        '0.761±0.174', '0.399±0.245', '0.52',  '112.5', '386'),
        ('T-Coffee',       '0.746±0.182', '0.394±0.248', '5.30',  '512.0', '342'),
        ('MAFFT L-INS-i',  '0.743±0.188', '0.379±0.238', '0.88',  ' 13.4', '386'),
        ('Clustal Omega',  '0.718±0.201', '0.363±0.240', '0.64',  ' 16.3', '386'),
        ('FAMSA',          '0.718±0.199', '0.357±0.257', '0.19',  ' 17.1', '386'),
        ('Kalign3',        '0.692±0.209', '0.322±0.245', '0.06',  '  5.3', '385'),
        ('MAFFT FFT-NS-2', '0.688±0.205', '0.315±0.233', '0.55',  ' 23.3', '386'),
    ],
    col_widths=[1.5, 1.1, 1.1, 0.9, 0.8, 0.6])
para(doc, sa=4)

heading(doc, 'Performance by Reference Set, Runtime, and Cross-Dataset Generalization', level=2)
para(doc,
     'Performance varied across BAliBASE reference sets (Figure 2). All tools performed '
     'best on RV12 (easy pairs, SP range 0.798-0.859) and worst on RV11 (difficult '
     'low-identity large families, SP range 0.431-0.605). On RV11, MUSCLE5 led '
     '(SP = 0.605) and MAFFT FFT-NS-2 was lowest (0.431). On RV40 (transmembrane), '
     'differences narrowed (SP 0.619-0.670), suggesting all tools are similarly challenged '
     'by hydrophobic-repeat structure. Bootstrap 95% CIs confirmed these orderings are stable.'
     '\n'
     'Runtime profiles differed by orders of magnitude (Table 1). Kalign3 was fastest '
     '(median 0.06 s), FAMSA second (0.19 s). T-Coffee was 88x slower than FAMSA '
     '(median 5.30 s) and timed out on 44/386 problems (11%), exclusively in large-sequence '
     'reference sets (>30 sequences). The Pareto frontier (Figure 2, right) highlights '
     'MUSCLE5 and FAMSA as optimal: FAMSA matches Clustal Omega accuracy at 3x lower '
     'runtime; MUSCLE5 achieves best accuracy at modest cost.'
     '\n'
     'Rankings generalized across all four benchmarks (Table 2). On OXBench, performance '
     'was uniformly high (SP 0.882-0.898) due to closely related families. On SABRE, '
     'MUSCLE5 led (SP = 0.600) and differences widened. PREFAB4 revealed severe '
     'scalability limits: Clustal Omega timed out on 82% of 50-sequence problems '
     '(completing only 369/1681); T-Coffee completed 1596/1681. Among tools completing '
     'all PREFAB4 problems, MAFFT L-INS-i led (SP = 0.694).',
     indent=0.3, sa=4)

figure(doc, 'fig4_pareto.png', width=4.6,
       caption='Pareto frontier: mean SP score vs. log10(median runtime). '
               'Upper-left is optimal (high accuracy, low runtime).',
       fig_num=2)

# Table 2 – Cross dataset
tp3 = para(doc, 'Table 2. Mean SP score by dataset (successful completions only).',
           italic=True, size=10, sa=2, sb=6)

add_table(doc,
    headers=['Aligner', 'BAliBASE (n=386)', 'OXBench (n=395)', 'SABRE (n=423)', 'PREFAB4'],
    rows=[
        ('MUSCLE5',        '0.761', '0.898', '0.600', '0.690 (n=1681)'),
        ('MAFFT L-INS-i',  '0.743', '0.886', '0.575', '0.694 (n=1681)'),
        ('T-Coffee',       '0.746', '0.898', '0.597', '0.680 (n=1596)'),
        ('FAMSA',          '0.718', '0.896', '0.565', '0.659 (n=1681)'),
        ('Clustal Omega',  '0.718', '0.889', '0.551', '0.696 (n=369)'),
        ('MAFFT FFT-NS-2', '0.688', '0.882', '0.537', '0.650 (n=1681)'),
        ('Kalign3',        '0.692', '0.886', '0.522', '0.617 (n=1681)'),
    ],
    col_widths=[1.3, 1.2, 1.2, 1.2, 1.1])
para(doc, sa=4)

# ── Discussion ────────────────────────────────────────────────────────────────
heading(doc, 'Discussion')

para(doc,
     'Our results support all three hypotheses. Hypothesis 1 is confirmed: iterative '
     '(MUSCLE5, MAFFT L-INS-i) and consistency-based (T-Coffee) tools consistently '
     'outranked progressive methods on BAliBASE, SABRE, and PREFAB4. However, effect '
     'sizes were small (maximum Cliff\'s delta = 0.22), indicating that practical '
     'per-alignment differences are modest for most families. Hypothesis 2 is supported '
     'by the OXBench data, where all tools converged to SP > 0.88 on closely related '
     'families. Hypothesis 3 is partially supported: FAMSA provides faster throughput '
     'than all high-accuracy tools while matching Clustal Omega in accuracy, but '
     'MUSCLE5 retains a meaningful advantage at only 2.7x higher median runtime '
     '(0.52 s vs. 0.19 s), making the trade-off modest for small-to-medium families.',
     indent=0.3, sa=4)

para(doc,
     'The scalability failure of T-Coffee (11% time-out on BB3, elevated on PREFAB4) '
     'is the most practically significant finding. Its O(N^2) pairwise complexity makes '
     'it infeasible for families with >40 sequences under typical time budgets, a severe '
     'constraint for genome-scale pipelines. By contrast, FAMSA and Kalign3 completed '
     'every problem in under 0.5 s regardless of family size. Clustal Omega\'s 82% '
     'failure rate on PREFAB4 (50-sequence problems, 300 s timeout) was unexpected '
     'and may reflect HMM overhead without profile reuse. These findings underscore '
     'that tool selection must account for the distribution of family sizes in the '
     'target dataset—not just accuracy on curated benchmarks.',
     indent=0.3, sa=4)

para(doc,
     'For practitioners we recommend: (1) accuracy-first workflows with <40 sequences: '
     'MUSCLE5; (2) accuracy with moderate speed for <30 sequences: MAFFT L-INS-i; '
     '(3) genome-scale pipelines across all family sizes: FAMSA; (4) speed-only '
     'requirements: Kalign3; (5) small critical alignments where completeness is '
     'guaranteed: T-Coffee. Study limitations include the restriction to protein '
     'benchmarks with structural references; RNA or very long sequences may rank '
     'differently. All tools were run single-threaded; multi-threaded MUSCLE5 and '
     'MAFFT would be proportionally faster, potentially widening their advantage '
     'over progressive methods in wall-clock terms.',
     indent=0.3, sa=4)

# ── References ────────────────────────────────────────────────────────────────
heading(doc, 'References')

refs = [
    '1.  Katoh K, Standley DM. MAFFT multiple sequence alignment software version 7: '
    'improvements in performance and usability. Mol Biol Evol. 2013;30(4):772-780. '
    'doi:10.1093/molbev/mst010',

    '2.  Edgar RC. MUSCLE5: High-accuracy alignment ensembles enable unbiased assessments '
    'of sequence homology and phylogeny. Nat Commun. 2022;13:6968. '
    'doi:10.1038/s41467-022-34630-w',

    '3.  Sievers F, Wilm A, Dineen D, et al. Fast, scalable generation of high-quality '
    'protein multiple sequence alignments using Clustal Omega. Mol Syst Biol. '
    '2011;7:539. doi:10.1038/msb.2011.75',

    '4.  Lassmann T. Kalign 3: multiple sequence alignment of large data sets. '
    'Bioinformatics. 2020;36(6):1928-1929. doi:10.1093/bioinformatics/btz795',

    '5.  Notredame C, Higgins DG, Heringa J. T-Coffee: A novel method for fast and '
    'accurate multiple sequence alignment. J Mol Biol. 2000;302(1):205-217. '
    'doi:10.1006/jmbi.2000.4042',

    '6.  Deorowicz S, Debudaj-Grabysz A, Gudys A. FAMSA: Fast and accurate multiple '
    'sequence alignment of huge protein families. Sci Rep. 2016;6:33964. '
    'doi:10.1038/srep33964',

    '7.  Thompson JD, Koehl P, Ripp R, Poch O. BAliBASE 3.0: Latest developments of '
    'the multiple sequence alignment benchmark. Proteins. 2005;61(1):127-136. '
    'doi:10.1002/prot.20527',

    '8.  Raghava GPS, Searle SMJ, Audley PC, Barber JD, Barton GJ. OXBench: A benchmark '
    'for evaluation of protein multiple sequence alignment accuracy. BMC Bioinformatics. '
    '2003;4:47. doi:10.1186/1471-2105-4-47',

    '9.  Blackshields G, Wallace IM, Larkin M, Higgins DG. Analysis and comparison of '
    'benchmarks for multiple sequence alignment. In Silico Biol. 2006;6(4):321-339.',

    '10. Edgar RC. PREFAB (Protein Reference Alignment Benchmark). 2004. '
    'https://www.drive5.com/bench/ [Accessed 2026]',

    '11. Demsar J. Statistical comparisons of classifiers over multiple data sets. '
    'J Mach Learn Res. 2006;7:1-30.',

    '12. Wilcoxon F. Individual comparisons by ranking methods. Biometrics. 1945;1(6):80-83.',

    '13. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and '
    'powerful approach to multiple testing. J R Stat Soc B. 1995;57(1):289-300.',
]

for ref_text in refs:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.left_indent  = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(ref_text)
    font(r, size=10)

doc.save(str(OUT_PATH))
print(f'Saved: {OUT_PATH}')
print(f'Size:  {OUT_PATH.stat().st_size / 1024:.1f} KB')
