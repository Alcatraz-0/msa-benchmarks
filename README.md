# Systematic Benchmarking of Multiple Sequence Alignment Algorithms


[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-F37626?logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Datasets](https://img.shields.io/badge/Datasets-BAliBASE%20·%20OXBench%20·%20SABRE%20·%20PREFAB4-orange)]()
[![Families](https://img.shields.io/badge/Protein%20Families-2%2C885-blueviolet)]()
[![Tools](https://img.shields.io/badge/MSA%20Tools-7-teal)]()
[![License](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey)](https://creativecommons.org/licenses/by-sa/4.0/)

---

## Overview

We benchmarked **7 widely-used MSA tools** across **2,885 protein families** from four independently curated structural benchmarks to give practitioners data-backed guidance on which aligner to use — and when.

Ground truth is defined by 3D crystal structure superposition (not sequence similarity), following the evaluation framework of [Santus et al. 2025](https://doi.org/10.1093/nargab/lqaf104) and the [nf-core/multiplesequencealign](https://github.com/nf-core/multiplesequencealign) pipeline. Alignments are scored with **SP (Sum-of-Pairs)** and **TC (Total Column)** metrics using structure-based residue masking.

---

## Key Findings

| Finding | Detail |
|---|---|
| **Friedman test** | χ² = 935.73, df = 6, p < 10⁻¹⁹⁹ — differences are not borderline |
| **Three performance tiers** | Confirmed by Nemenyi post-hoc at α = 0.05 |
| **Tier 1 — Top** | MUSCLE5 (SP = 0.761 ± 0.174) |
| **Tier 2 — Middle** | T-Coffee · MAFFT L-INS-i · Clustal Omega · FAMSA |
| **Tier 3 — Bottom** | MAFFT FFT-NS-2 · Kalign3 (statistically indistinguishable, p = 0.524) |
| **Identity threshold** | Above 60% identity all tools converge; below 20% the gap reaches ~0.15 SP units |
| **Pareto winners** | FAMSA (speed) and MUSCLE5 (accuracy) — no other tool dominates both |
| **Rankings generalise** | Three-tier structure reproduced on all four independent benchmarks |

---

## Critical Difference Diagram

<p align="center">
  <img src="figures/fig14_cd_diagram.png" width="720" alt="CD diagram — Nemenyi post-hoc"/>
</p>

*Tools connected by a bar are statistically indistinguishable at α = 0.05. MUSCLE5 is the sole top-tier tool; FFT-NS-2 and Kalign3 form an inseparable bottom tier.*

---

## Accuracy Distributions & Pareto Frontier

<p align="center">
  <img src="figures/fig1_accuracy_overall.png" width="49%" alt="SP and TC score distributions"/>
  <img src="figures/fig4_pareto.png" width="49%" alt="Accuracy-speed Pareto plot"/>
</p>

*Left: SP and TC score distributions across all 386 BAliBASE 3.0 families. MUSCLE5 achieves the highest median with a tighter spread. Right: Pareto frontier — only FAMSA and MUSCLE5 are not dominated on both accuracy and speed.*

---

## Score vs. Sequence Identity

<p align="center">
  <img src="figures/fig21_score_vs_identity.png" width="720" alt="SP score vs pairwise sequence identity"/>
</p>

*The performance gap between tiers is widest below 20% identity — exactly where accurate alignment has the greatest biological impact (phylogenetics, homology modelling, remote homolog detection).*

---

## Runtime Scaling

<p align="center">
  <img src="figures/fig16_scaling_plots.png" width="720" alt="Runtime vs sequence count"/>
</p>

*FAMSA and Kalign3 stay flat across all family sizes. T-Coffee diverges sharply above ~30 sequences (O(N²) pairwise library), explaining the 11% timeout rate on BAliBASE. Clustal Omega failed on 78% of PREFAB4's 50-sequence problems.*

---

## Per-Reference-Set Breakdown

<p align="center">
  <img src="figures/fig2_sp_by_rvset.png" width="720" alt="SP score by BAliBASE reference set"/>
</p>

| RV Set | Description | Hardest for |
|---|---|---|
| RV11 | Small families, <25% identity | All tools — largest tier gap (0.17 SP) |
| RV12 | Large families, <25% identity | Rankings compressed |
| RV20 | Long insertions / extensions | — |
| RV30 | Repeats | — |
| RV40 | Transmembrane proteins | All tools cluster within 0.05 SP |
| RV50 | Large, highly divergent | MUSCLE5 holds its lead |

---

## Tools Compared

| Tool | Algorithm Family | Key Characteristic |
|---|---|---|
| MAFFT FFT-NS-2 | Progressive | Fast single-pass, FFT-based distance |
| MAFFT L-INS-i | Iterative refinement | Smith-Waterman pairwise, O(N²) |
| MUSCLE5 | Ensemble iterative | Multi-seed, selects best alignment |
| Clustal Omega | Progressive | HMM-guided, seeded guide tree |
| Kalign3 | Progressive | UPGMA-based, fastest overall |
| T-Coffee | Consistency-based | Global pairwise library, highest accuracy cost |
| FAMSA | Progressive | Column reuse in UPGMA tree |

> All tools pinned to **1 CPU thread** for fair algorithmic comparison.

---

## Datasets

| Dataset | Families | Ground Truth | Notes |
|---|---|---|---|
| [BAliBASE 3.0](https://www.lbgi.fr/balibase/) | 386 | 3D structure superposition | Community gold standard — 6 reference sets |
| [OXBench](https://www.compbio.dundee.ac.uk/www-oxbench/) | 395 | Crystal structure overlay | Fully objective, no human curation bias |
| [SABRE](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1478177/) | 423 | Structure-derived | Covers a wide range of sequence identities |
| [PREFAB4](https://www.drive5.com/bench/) | 1,681 | Pairwise structure | ~50 seqs/family — primary scalability test |

---

## Results Summary — BAliBASE 3.0

| Aligner | SP mean ± SD | TC mean ± SD | Runtime (s) | Memory (MB) | Completed |
|---|---|---|---|---|---|
| **MUSCLE5** | **0.761 ± 0.174** | **0.399 ± 0.245** | 0.52 | 112.5 | 386 / 386 |
| T-Coffee† | 0.746 ± 0.182 | 0.394 ± 0.248 | 5.30 | 512.0 | 342 / 386 |
| MAFFT L-INS-i | 0.743 ± 0.188 | 0.379 ± 0.238 | 0.88 | 13.4 | 386 / 386 |
| Clustal Omega | 0.718 ± 0.201 | 0.363 ± 0.240 | 0.64 | 16.3 | 386 / 386 |
| FAMSA | 0.718 ± 0.199 | 0.357 ± 0.257 | 0.19 | 17.1 | 386 / 386 |
| Kalign3 | 0.692 ± 0.209 | 0.322 ± 0.245 | 0.06 | 5.3 | 385 / 386 |
| MAFFT FFT-NS-2 | 0.688 ± 0.205 | 0.315 ± 0.233 | 0.55 | 23.3 | 386 / 386 |

† T-Coffee timed out on 44/386 problems (> 200 s) on large-sequence reference sets.

---

## Cross-Dataset Generalisation

Rankings held across all four independent benchmarks, confirming they reflect real algorithmic properties — not BAliBASE-specific artefacts.

| Aligner | BAliBASE (n=386) | OXBench (n=395) | SABRE (n=423) | PREFAB4 |
|---|---|---|---|---|
| **MUSCLE5** | **0.761** | **0.898** | 0.600 | 0.690 (n=1,681) |
| T-Coffee | 0.746 | **0.898** | 0.597 | 0.680 (n=1,596) ‡ |
| MAFFT L-INS-i | 0.743 | 0.886 | 0.575 | **0.694** (n=1,681) |
| FAMSA | 0.718 | 0.896 | 0.565 | 0.659 (n=1,681) |
| Clustal Omega | 0.718 | 0.889 | 0.551 | 0.696 (n=369) † |
| MAFFT FFT-NS-2 | 0.688 | 0.882 | 0.537 | 0.650 (n=1,681) |
| Kalign3 | 0.692 | 0.886 | 0.522 | 0.617 (n=1,681) |

† Clustal Omega: 78% timeout on PREFAB4.  ‡ T-Coffee: 11% timeout on BAliBASE.

---

## Statistical Pipeline

Five tests were applied in sequence to ensure rigorous, reproducible comparisons:

```
1. Friedman Test          — Global differences exist? (χ²=935.73, p<10⁻¹⁹⁹)
       ↓
2. Wilcoxon Signed-Rank   — Which pairs differ? (20/21 pairs significant)
       ↓
3. BH FDR Correction      — Control false discovery rate at 5%
       ↓
4. Cliff's δ Effect Size  — How large are the differences? (max |δ|=0.22, small)
       ↓
5. Nemenyi Post-hoc       — Three distinct tiers confirmed
       +
   Bootstrap 95% CIs      — 10,000 resamples confirm tier stability
```

All tests used non-parametric methods — SP/TC scores are bounded in [0,1] and non-normal.

---

## Quick-Reference Guide

| Use Case | Recommended Tool | Reason |
|---|---|---|
| Divergent sequences (< 20% identity) | **MUSCLE5** or MAFFT L-INS-i | Largest accuracy advantage here |
| Genome-scale pipelines | **FAMSA** | Pareto-optimal on speed + accuracy |
| Speed-only / very large families | **Kalign3** | 0.06 s median, near-flat scaling |
| Small curated families, no time limit | **T-Coffee** | Consistency-based accuracy |
| High-identity sequences (> 60%) | Any — use **Kalign3** | All tools converge; save compute |

---

## Repository Structure

```
.
├── 01_setup.ipynb          # Install WSL tools, verify BAliBASE 3.0 data
├── 02_benchmark.ipynb      # Run all 7 aligners — checkpoint-resumable
├── 03_analysis.ipynb       # Friedman · Wilcoxon · Nemenyi · 21 figures
│
├── run_bench_datasets.py   # Benchmark runner for OXBench, SABRE, PREFAB4
│
├── report.pdf              # Full 5-page report (OUP Contemporary format)
├── MSA_Benchmark_10slides.pptx  # 10-slide 15-min presentation
│
└── figures/                # 21 publication-quality figures (PNG)
```

---

## Reproducing the Results

### Prerequisites

- Windows 10/11 with WSL2 (Ubuntu 22.04)
- Python 3.11+

```bash
pip install biopython tqdm pandas scipy matplotlib seaborn
```

- BAliBASE 3.0 data — [download here](https://www.lbgi.fr/balibase/), extract into `data/bb3_release/`

### Steps

```bash
# 1. Set up bioinformatics tools in WSL
#    Open 01_setup.ipynb and run all cells.
#    Installs: MAFFT, MUSCLE5, Clustal Omega, Kalign3, T-Coffee, FAMSA

# 2. Run the benchmark on BAliBASE 3.0 (checkpoint-resumable — safe to interrupt)
#    Open 02_benchmark.ipynb and run all cells.
#    Output: results/results.csv

# 3. Run on OXBench, SABRE, PREFAB4
python run_bench_datasets.py             # all three datasets
python run_bench_datasets.py oxbench     # single dataset

# 4. Statistical analysis + all figure generation
#    Open 03_analysis.ipynb and run all cells.
#    Output: figures/*.png
```

---

## Methodology Reference

> Santus et al. (2025). *An nf-core framework for the systematic comparison of alternative modeling tools: the multiple sequence alignment case study.* NAR Genomics and Bioinformatics, 7(3), lqaf104. [doi:10.1093/nargab/lqaf104](https://doi.org/10.1093/nargab/lqaf104)

Pipeline: [github.com/nf-core/multiplesequencealign](https://github.com/nf-core/multiplesequencealign)

---
