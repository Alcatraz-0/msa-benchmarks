# Project Extensions

## 1. Additional MSA Tools

Add to `ALIGNERS` dict in `02_benchmark.ipynb` and install in `01_setup.ipynb`.

### Kalign3 ✅
- Fast progressive aligner, good on divergent sequences
- Install: `apt-get install -y kalign`
- Command: `kalign -i {input} -o {output}`

### T-Coffee ✅
- Consistency-based, historically high accuracy
- Install: `apt-get install -y t-coffee`
- Command: `t_coffee {input} -outfile {output} -output fasta_aln`
- Note: 44/386 problems exceed 120s timeout (large RV20–RV50 problems)

### FAMSA ✅
- Extremely fast, designed for thousands of sequences
- Binary: https://github.com/refresh-bio/FAMSA/releases (v2.5.2 x64 tarball)
- Command: `famsa {input} {output}`

### FAMSA2
- Successor to FAMSA; claims 400× faster at protein-universe scale
- Same CLI interface as FAMSA — drop-in replacement for comparison
- Binary: https://github.com/refresh-bio/FAMSA/releases (latest)

### PROBCONS
- Probabilistic consistency-based; historical accuracy gold standard
- Install: `apt-get install -y probcons`
- Command: `probcons {input} > {output}`

### learnMSA2
- Deep learning + LLM embeddings; best-in-class on large protein families
- Represents the ML-based aligner category (none currently in the benchmark)
- Install: `pip install learnMSA`
- Paper: PMC11373405 (*Bioinformatics* 2024)

---

## 2. Additional Benchmark Datasets

All datasets below are downloaded and extracted to:
`data/bench_datasets/bench1.0/` (drive5 uniform FASTA format — uppercase = scored columns)

### PREFAB v4 ✅ Downloaded
- 1,681 problems, ~44 sequences/problem
- Used in MUSCLE5 paper — enables direct comparison to published numbers
- Path: `data/bench_datasets/bench1.0/prefab4/` (input: `in/`, reference: `ref/`)
- Scoring: Q-score on uppercase-only columns (same SP logic, uppercase mask applied)

### OXBench ✅ Downloaded
- **ox**: 395 problems, ~5 seqs/problem (core set)
- **oxx**: 395 problems, ~72 seqs/problem (extended set — harder)
- **oxm**: 336 problems (MUSTANG re-aligned references)
- Structural ground truth; widely used alongside BAliBASE (PubMed 14552658)
- Path: `data/bench_datasets/bench1.0/ox/`, `oxx/`, `oxm/`

### SABRE ✅ Downloaded
- 423 problems, ~4 seqs/problem
- Consistent alignments from structural superposition
- Path: `data/bench_datasets/bench1.0/sabre/`

### HomFam
- Used in Clustal Omega paper — large families, tests scalability
- Download: https://www.ebi.ac.uk/~gsarah/homfam/
- Note: some families have 1000s of sequences — L-INS-i will timeout

### QuanTest2
- Secondary-structure-based scoring; 997 Pfam families (2023)
- More modern than BAliBASE; useful for reviewers requesting non-structural benchmarks
- Paper: PMC9881607 (*BMC Bioinformatics* 2023)

---

## 3. Analysis

### Implemented ✅

| Analysis | Figure / Table |
|---|---|
| Overall accuracy box plots (SP & TC) | fig1 |
| SP score by reference set | fig2 |
| Runtime CDF | fig3 |
| Speed–accuracy Pareto | fig4 |
| SP score heatmap (aligner × RV set) | fig5 |
| TC score heatmap | fig6 |
| Memory usage box plot | fig7 |
| SP vs TC scatter | fig8 |
| Score distributions — violin plots | fig9 |
| Pairwise significance heatmap (−log10 p) | fig10 |
| Bootstrap 95% CIs on mean SP | fig11 |
| Win / Tie / Loss matrix | fig12 |
| Average rank by reference set | fig13 |
| Critical Difference diagram (Nemenyi) | fig14 |
| Parallel coordinates — SP per problem | fig15 |
| Computational scaling (runtime & memory vs size) | fig16 |
| Score degradation vs problem size | fig17 |
| Δ SP heatmap vs baseline | fig18 |
| Bootstrap 95% CIs per reference set | fig19 |
| Pairwise Wilcoxon + Cliff's delta | table_wilcoxon.csv |
| Friedman test + Kendall's W | printed output |
| Bonferroni / BH corrected p-values | table_wilcoxon_corrected.csv |
| Spearman SP↔TC rank correlation | printed output |
| Wilcoxon tests on runtime + rank-biserial r | table_wilcoxon_runtime.csv |
| Failure analysis | printed output |

### Pending

- **Score vs sequence identity** — correlates accuracy with pairwise identity; needs parsing
  BAliBASE `.xml` annotation files. Nearly universal in MSA papers.
- **bali_score cross-validation** — run the reference `bali_score` binary on ~20 problems
  to confirm the Python SP/TC implementation matches the official scorer.
  Source: IGBMC FTP; compile with `gcc` in WSL.
- **Exact Nemenyi post-hoc p-values** — Eisinga et al. (2017, DOI 10.1186/s12859-017-1486-2)
  give exact pairwise Friedman rank-sum p-values, more powerful than Bonferroni on ranks.
- **Error-bar plots per RV set** — mean ± CI per aligner per subset;
  supplements the per-RV bootstrap cell already in the notebook.

---

## 4. Methodology Validation

- **Thread-count audit** — confirm whether all seven aligners ran single-threaded.
  MAFFT L-INS-i and MUSCLE5 parallelise; wall-clock comparisons require consistent threading.
- **BAliBASE circularity note** — T-Coffee was partly tuned on BAliBASE references.
  A one-sentence caveat in the write-up is expected (Aniba et al. 2010, PMC2995051).
- **Tool version table** — *Genome Biology* benchmarking guidelines (PMC6584985) require
  exact versions and default parameters to be documented.
- **bali_score cross-validation** — see above.

---

## Implementation Order

1. ✅ Quick-win analysis cells (no new data)
2. ✅ CD diagram + Friedman + Kendall's W + multiple testing correction
3. ✅ Scaling plots (runtime/memory vs problem size)
4. ✅ Kalign3 + T-Coffee + FAMSA benchmarked (BAliBASE 3.0)
5. ✅ Δ SP heatmap, Wilcoxon on runtime, Bootstrap CIs per RV set
6. ✅ Score vs sequence identity (BAliBASE XML parsing)
7. ✅ Exact Nemenyi post-hoc p-values
8. ✅ Tool version table + methodology notes
9. ✅ PREFAB v4 + OXBench + SABRE downloaded
10. Run benchmark on PREFAB / OXBench / SABRE (needs scoring script update for uppercase mask)
11. bali_score cross-validation (IGBMC server currently unreachable)
12. FAMSA2 or PROBCONS (low effort drop-in)
13. learnMSA2 (ML baseline — significant setup effort)
14. HomFam / QuanTest2 (if time permits)
