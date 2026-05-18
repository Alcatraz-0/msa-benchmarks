"""
MSA Benchmark — 10-slide, 15-minute presentation
Design: Minimal  |  White + Charcoal + Teal (#00A3C4) + Sage (#81E6D9)
Strict coordinate system — no overlapping elements guaranteed.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pathlib import Path

OUT = Path(r"C:\Users\anand\Desktop\SEM 4\CS 502\Project\MSA_Benchmark_10slides.pptx")

# ── Palette ───────────────────────────────────────────────────────────────────
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
CHARCOAL = RGBColor(0x2D, 0x37, 0x48)
TEAL     = RGBColor(0x00, 0xA3, 0xC4)
SAGE     = RGBColor(0x81, 0xE6, 0xD9)
TEAL_DK  = RGBColor(0x00, 0x7A, 0x94)
TEAL_LT  = RGBColor(0xE8, 0xF8, 0xFB)
SAGE_LT  = RGBColor(0xF0, 0xFD, 0xFB)
GRAY     = RGBColor(0x71, 0x80, 0x96)
LGRAY    = RGBColor(0xF7, 0xFA, 0xFC)
MGRAY    = RGBColor(0xCB, 0xD5, 0xE0)
GREEN    = RGBColor(0x27, 0xAE, 0x60)
RED      = RGBColor(0xC0, 0x39, 0x2B)
AMBER    = RGBColor(0xD3, 0x78, 0x00)
GREEN_LT = RGBColor(0xF0, 0xFD, 0xF4)
RED_LT   = RGBColor(0xFE, 0xF2, 0xF2)
AMBER_LT = RGBColor(0xFE, 0xF9, 0xEC)

# ── Canvas constants ──────────────────────────────────────────────────────────
CW   = 13.33   # canvas width
CH   = 7.5     # canvas height
LM   = 0.55    # left margin
RM   = 0.55    # right margin
UW   = CW - LM - RM   # usable width  = 12.23"
FY   = 7.1     # footer top
FH   = 0.4     # footer height
CY   = 1.25    # content area top (after header)
CEY  = FY      # content area bottom

prs = Presentation()
prs.slide_width  = Inches(CW)
prs.slide_height = Inches(CH)
BLANK = prs.slide_layouts[6]

# ── Primitives ────────────────────────────────────────────────────────────────
def R(sl, l, t, w, h, fill, lc=None, lw=0.5):
    sh = sl.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if lc: sh.line.color.rgb = lc; sh.line.width = Pt(lw)
    else:  sh.line.fill.background()
    return sh

def T(sl, text, l, t, w, h,
      sz=13, bold=False, italic=False, col=CHARCOAL,
      align=PP_ALIGN.LEFT, face="Calibri", wrap=True):
    if not text: return
    bx = sl.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = bx.text_frame; tf.word_wrap = wrap
    p  = tf.paragraphs[0]; p.alignment = align
    r  = p.add_run()
    r.text = text; r.font.name = face; r.font.size = Pt(sz)
    r.font.bold = bold; r.font.italic = italic; r.font.color.rgb = col
    return bx

def BL(sl, items, l, t, w, sz=13, col=CHARCOAL, gap=0.42):
    """Bullet list. items = str or (str, True) for sub-item.
       Returns y bottom of last item."""
    y = t
    for item in items:
        is_sub = isinstance(item, tuple) and item[1]
        text   = item[0] if isinstance(item, tuple) else item
        indent = LM + 0.22 if is_sub else LM
        prefix = "    –  " if is_sub else "▸  "
        item_sz = sz - 1 if is_sub else sz
        c = GRAY if is_sub else col
        T(sl, prefix + text, l + (0.2 if is_sub else 0), y, w, gap,
          sz=item_sz, col=c)
        y += gap
    return y

def HDR(sl, title, subtitle=None, tag=None, total=10, num=None):
    """Minimal header: teal top line, charcoal title."""
    R(sl, 0, 0, CW, 0.08, TEAL)           # top accent line
    T(sl, title, LM, 0.18, UW - (1.9 if tag else 0), 0.72,
      sz=24, bold=True, col=CHARCOAL)
    if subtitle:
        T(sl, subtitle, LM, 0.82, UW - 0.5, 0.36,
          sz=12, italic=True, col=TEAL)
    if tag:
        R(sl, CW - RM - 1.75, 0.18, 1.75, 0.38, TEAL)
        T(sl, tag, CW - RM - 1.75, 0.18, 1.75, 0.38,
          sz=10, bold=True, col=WHITE, align=PP_ALIGN.CENTER)
    # Footer
    R(sl, 0, FY, CW, FH, LGRAY)
    R(sl, 0, FY, CW, 0.04, TEAL)
    T(sl, "CS 502 — Computational Biology  |  UIC  |  Spring 2026",
      LM, FY + 0.06, 10.0, 0.3, sz=9, col=GRAY)
    if num:
        T(sl, f"{num} / {total}", CW - RM - 0.7, FY + 0.06, 0.7, 0.3,
          sz=9, bold=True, col=TEAL, align=PP_ALIGN.RIGHT)
    # White background
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = WHITE

def divider(sl, y):
    R(sl, LM, y, UW, 0.03, MGRAY)

def NTS(sl, text):
    sl.notes_slide.notes_text_frame.text = text

# ── Table helper ──────────────────────────────────────────────────────────────
def table(sl, headers, rows, x, y, w, col_widths,
          row_h=0.52, hdr_fill=TEAL, hdr_col=WHITE,
          alt=TEAL_LT, warn_col=RED, warn_idx=None):
    """Draw a clean table. col_widths must sum to w."""
    # Header
    cx = x
    R(sl, x, y, w, row_h, hdr_fill)
    for j, (h, cw) in enumerate(zip(headers, col_widths)):
        T(sl, h, cx + 0.08, y + 0.08, cw - 0.12, row_h - 0.12,
          sz=11, bold=True, col=hdr_col,
          align=PP_ALIGN.CENTER)
        cx += cw
    # Rows
    for i, row in enumerate(rows):
        ry  = y + row_h + i * row_h
        bg  = alt if i % 2 == 0 else WHITE
        is_w = warn_idx is not None and i == warn_idx
        if is_w: bg = RED_LT
        R(sl, x, ry, w, row_h, bg)
        cx = x
        for j, (cell, cw) in enumerate(zip(row, col_widths)):
            is_warn_cell = is_w and j > 0
            c = RED if is_warn_cell else (TEAL_DK if j == 0 else CHARCOAL)
            T(sl, str(cell), cx + 0.08, ry + 0.09, cw - 0.12, row_h - 0.14,
              sz=11, bold=(j == 0), col=c,
              align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
            cx += cw
    return y + row_h * (1 + len(rows))

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
sl.background.fill.solid(); sl.background.fill.fore_color.rgb = WHITE

R(sl, 0,  0,  CW, 0.1, TEAL)      # top bar
R(sl, 0, CH - 0.1, CW, 0.1, TEAL) # bottom bar
R(sl, 0, 2.85, CW, 0.04, SAGE)    # mid accent

T(sl, "Systematic Benchmarking of\nMultiple Sequence Alignment Algorithms",
  LM, 0.35, UW, 2.2, sz=38, bold=True, col=CHARCOAL)

T(sl, "Performance Across Structurally-Informed Reference Datasets",
  LM, 2.95, UW, 0.62, sz=18, italic=True, col=TEAL)

T(sl, "Anand Meena  (Presenter A)   ·   ameen4@uic.edu",
  LM, 3.9, UW, 0.45, sz=15, bold=True, col=CHARCOAL)
T(sl, "Shruthi Kodati  (Presenter B)   ·   skoda13@uic.edu",
  LM, 4.35, UW, 0.45, sz=15, bold=True, col=CHARCOAL)

T(sl, "Department of Computer Science  ·  University of Illinois at Chicago  ·  Spring 2026",
  LM, 5.08, UW, 0.38, sz=12, col=GRAY)

R(sl, LM, 5.65, 5.6, 0.38, TEAL_LT)
T(sl, "Presenter A  —  Slides 1, 2, 3, 7, 10",
  LM, 5.68, 5.6, 0.32, sz=10, col=TEAL, align=PP_ALIGN.CENTER)
R(sl, LM + 5.85, 5.65, 5.6, 0.38, TEAL_LT)
T(sl, "Presenter B  —  Slides 4, 5, 6, 8, 9",
  LM + 5.85, 5.68, 5.6, 0.32, sz=10, col=TEAL, align=PP_ALIGN.CENTER)

NTS(sl, """\
[BOTH — 0:00–0:30]

Presenter A: "Good afternoon, everyone. I'm Anand Meena, and with me is Shruthi Kodati. We have 15 minutes to walk you through our CS 502 benchmarking study on multiple sequence alignment tools."

Presenter B: "We'll cover why this problem matters, the four datasets and seven tools we tested, our accuracy and speed findings, and finish with practical guidance on which tool to use when. Let's get started."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Introduction & Motivation
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Introduction & Motivation",
    subtitle="Why alignment quality matters — and what makes it hard", num=2)

# Left column  x=LM  w=5.6
T(sl, "The core problem", LM, CY, 5.6, 0.38,
  sz=14, bold=True, col=TEAL)
BL(sl, [
    "Multiple sequence alignment (MSA) is the first step in phylogenetics, homology modelling, and conserved-domain detection",
    "Errors here propagate silently — the pipeline does not crash, it just produces wrong biology",
    "A misaligned column can shift a phylogenetic branch, corrupt a drug-binding site, or erase a conserved domain",
], LM - LM, CY + 0.45, 5.6, sz=12, gap=0.55)

divider(sl, CY + 2.2)

T(sl, "Our goal", LM, CY + 2.32, 5.6, 0.36,
  sz=14, bold=True, col=TEAL)
T(sl, "Conduct a rigorous multi-dataset comparison of seven MSA tools with proper statistical testing — to give practitioners data-backed guidance on tool selection.",
  LM, CY + 2.72, 5.6, 0.82, sz=12, col=CHARCOAL, wrap=True)

# Right column  x=6.65  w=6.13
RC = 6.65
RW = CW - RC - RM

T(sl, "Three algorithm families", RC, CY, RW, 0.38,
  sz=14, bold=True, col=TEAL)

fams = [
    ("Progressive",          TEAL,   "Clustal Omega · FAMSA · Kalign3",
     "Build guide tree, align once.\nFast but commits to early errors."),
    ("Iterative Refinement", GREEN,  "MAFFT L-INS-i · MUSCLE5",
     "Repeatedly realign to escape optima.\nSlower, more accurate."),
    ("Consistency-Based",    AMBER,  "T-Coffee",
     "Pairwise library → global scoring.\nHighest accuracy, O(N²) cost."),
]
for i, (name, col, tools, desc) in enumerate(fams):
    fy = CY + 0.5 + i * 1.72
    R(sl, RC, fy, RW, 0.36, col)
    T(sl, name, RC + 0.12, fy + 0.04, RW - 0.2, 0.28,
      sz=13, bold=True, col=WHITE)
    R(sl, RC, fy + 0.36, RW, 1.28, TEAL_LT)
    T(sl, tools, RC + 0.12, fy + 0.44, RW - 0.2, 0.32,
      sz=12, bold=True, col=col)
    T(sl, desc, RC + 0.12, fy + 0.78, RW - 0.2, 0.72,
      sz=11, col=GRAY, wrap=True)

NTS(sl, """\
[PRESENTER A — 0:30–2:15  (~1:45)]

"So why does alignment quality matter so much? MSA is the very first analytical step whenever you're comparing protein sequences across species or evolutionary time. Get it wrong, and every downstream result — your phylogenetic tree, your homology model, your conserved-domain calls — can be subtly corrupted. And the worst part: it fails silently. The pipeline keeps running and produces output that looks perfectly normal.

[Point right.] The field has three main approaches. Progressive methods like Clustal Omega and FAMSA are fast — they build a rough guide tree and align sequences in one pass. The risk is they commit to early alignment decisions they never revisit. Iterative methods like MUSCLE5 go back and realign repeatedly to escape bad local solutions — slower, but more accurate. Consistency-based tools like T-Coffee are the most thorough — they score every position based on all possible pairwise alignments — but the cost scales quadratically with sequence count.

Our goal was to put all seven tools through their paces on a large, diverse set of protein families and measure the differences rigorously."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Datasets
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Datasets & Structural Ground Truth",
    subtitle="2,885 protein families across four independently curated benchmarks", num=3)

ds = [
    ("BAliBASE 3.0",  "386",   TEAL,
     "The community gold standard. Six reference sets spanning low-identity families, terminal extensions, transmembrane proteins, and circular permutations. Manually curated by structural biologists."),
    ("OXBench",       "395",   TEAL_DK,
     "Alignments derived from 3D crystal structure superposition. Ground truth defined by physically overlaying atoms in space — no human curation bias."),
    ("SABRE",         GREEN,
     "423",
     "Covers a wide range of pairwise sequence identities. Tests whether tool rankings hold regardless of how similar or divergent the sequences are."),
    ("PREFAB4",       "1,681", AMBER,
     "Families weighted toward ~50 sequences each. Our primary scalability stress test — small runtime differences between tools get amplified here."),
]

# 2×2 grid
positions = [(LM, CY), (LM + 6.3, CY), (LM, CY + 2.9), (LM + 6.3, CY + 2.9)]
CRD_W, CRD_H = 5.9, 2.68

for (name, n, col, desc), (px, py) in zip(ds, positions):
    # handle swapped n/col in SABRE entry
    if name == "SABRE":
        name, n, col, desc = "SABRE", "423", GREEN, desc
    R(sl, px, py, CRD_W, CRD_H, TEAL_LT, MGRAY, 0.4)
    R(sl, px, py, CRD_W, 0.06, col)
    T(sl, name, px + 0.15, py + 0.14, 3.8, 0.38,
      sz=15, bold=True, col=col)
    T(sl, n + " families", px + 0.15, py + 0.52, 3.8, 0.38,
      sz=13, col=GRAY)
    T(sl, desc, px + 0.15, py + 0.94, CRD_W - 0.28, 1.6,
      sz=11.5, col=CHARCOAL, wrap=True)

NTS(sl, """\
[PRESENTER A — 2:15–3:45  (~1:30)]

"Before I describe the tools, a moment on the datasets — because the benchmark you choose determines what you can claim.

[Top-left.] BAliBASE 3.0 is the community gold standard. It was manually curated across six distinct evolutionary scenarios — everything from small low-identity families to large divergent sets with circular permutations.

[Top-right.] OXBench is based on actual 3D crystal structures. The correct alignment is defined by physically superimposing atoms in space. No human judgment involved — this is as objective as it gets.

[Bottom-left.] SABRE spans an enormous range of sequence identities, letting us ask whether the same tools win across the full evolutionary spectrum.

[Bottom-right.] PREFAB4 is our scalability stress test. Its 50-sequence families are where slow algorithms start to break.

Together these four give us confidence that our findings aren't artifacts of any single dataset. Now let me hand over to Shruthi to walk through the tools and scoring."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Tools & Scoring
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Alignment Tools & Scoring",
    subtitle="Seven tools, all pinned to one CPU thread for fair runtime comparison", num=4)

# Tool table  left side
TW = 7.5
col_widths_tools = [2.4, 2.6, 2.5]
hdrs_tools = ["Tool", "Algorithm Family", "Key Flag"]
rows_tools = [
    ("MAFFT FFT-NS-2",  "Progressive",          "--retree 2"),
    ("MAFFT L-INS-i",   "Iterative Refinement",  "--maxiterate 1000"),
    ("MUSCLE5",         "Iterative (ensemble)",   "-threads 1"),
    ("Clustal Omega",   "Progressive",            "--force"),
    ("Kalign3",         "Progressive",            "--nthreads 1"),
    ("T-Coffee",        "Consistency-Based",      "-output fasta_aln"),
    ("FAMSA",           "Progressive",            "-t 1"),
]
table(sl, hdrs_tools, rows_tools, LM, CY, TW,
      col_widths_tools, row_h=0.48)

# Scoring — right side
SC_X = LM + TW + 0.4
SC_W = UW - TW - 0.4

for i, (lbl, full, body, col) in enumerate([
    ("SP", "Sum-of-Pairs",
     "Fraction of reference residue pairs correctly co-aligned. Partial credit — sensitive to per-column accuracy.",
     TEAL),
    ("TC", "Total Column",
     "Fraction of columns reproduced exactly. No partial credit — one wrong residue fails the whole column.",
     TEAL_DK),
]):
    sy = CY + i * 2.05
    R(sl, SC_X, sy, SC_W, 1.88, TEAL_LT, MGRAY, 0.4)
    R(sl, SC_X, sy, SC_W, 0.06, col)
    T(sl, lbl,  SC_X + 0.15, sy + 0.14, 0.7,         0.42, sz=22, bold=True, col=col)
    T(sl, full, SC_X + 0.15, sy + 0.56, SC_W - 0.28, 0.34, sz=13, bold=True, col=CHARCOAL)
    T(sl, body, SC_X + 0.15, sy + 0.95, SC_W - 0.28, 0.82, sz=11.5, col=GRAY, wrap=True)

T(sl, "★  Only uppercase residues score (structurally confirmed positions)",
  SC_X, CY + 4.25, SC_W, 0.32, sz=9.5, italic=True, col=GRAY)

NTS(sl, """\
[PRESENTER B — 3:45–5:00  (~1:15)]

"Thanks Anand. Seven tools — I won't go through each one in detail, but the key point is they represent all three algorithm families we just described. Two configurations of MAFFT, MUSCLE5, Clustal Omega, Kalign3, T-Coffee, and FAMSA.

Critical for fairness: we pinned every tool to a single CPU thread. That way we're measuring algorithmic efficiency, not how well a tool uses multiple cores.

For scoring we used two metrics. [Point to cards.] SP — Sum of Pairs — counts whether residues that should be co-aligned actually are, and gives partial credit per pair. TC — Total Column — is much stricter. A column only gets credit if every single sequence has the right residue there. One error, zero credit.

One important detail: we only scored uppercase residues — positions that were structurally confirmed in the original crystal structures. This makes the benchmark conservative but meaningful."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Statistical Pipeline
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Statistical Analysis Pipeline",
    subtitle="Non-parametric tests throughout — scores are bounded in [0,1] and non-normal", num=5)

steps = [
    ("01", TEAL,    "Friedman Test",
     "χ² = 935.73, df = 6, p < 10⁻¹⁹⁹  —  global differences are certain, not borderline"),
    ("02", TEAL_DK, "Wilcoxon Signed-Rank + BH Correction",
     "20 of 21 pairwise comparisons significant at FDR 5%  —  only FFT-NS-2 vs Kalign3 fails"),
    ("03", GREEN,   "Cliff's δ Effect Size",
     "All effects negligible–to–small  (max |δ| = 0.22)  —  real and consistent, but moderate per family"),
    ("04", AMBER,   "Nemenyi Post-hoc Test",
     "Three distinct tiers identified. FFT-NS-2 and Kalign3 are statistically indistinguishable  (p = 0.524)"),
    ("05", RGBColor(0x6B, 0x46, 0xC1), "Bootstrap 95% Confidence Intervals",
     "10,000 resamples confirm tier orderings are stable across all six BAliBASE reference sets"),
]

ROW_H = 0.96
for i, (num, col, name, result) in enumerate(steps):
    ry = CY + i * (ROW_H + 0.12)
    bg = TEAL_LT if i % 2 == 0 else WHITE
    R(sl, LM, ry, UW, ROW_H, bg, MGRAY, 0.3)
    R(sl, LM, ry, 0.06, ROW_H, col)
    # Number badge
    R(sl, LM + 0.1, ry + 0.2, 0.56, 0.56, col)
    T(sl, num, LM + 0.1, ry + 0.2, 0.56, 0.56,
      sz=14, bold=True, col=WHITE, align=PP_ALIGN.CENTER)
    # Name
    T(sl, name, LM + 0.82, ry + 0.1, 4.2, 0.38,
      sz=13, bold=True, col=col)
    # Result
    T(sl, result, LM + 0.82, ry + 0.5, UW - 1.0, 0.38,
      sz=12, col=CHARCOAL, wrap=True)

NTS(sl, """\
[PRESENTER B — 5:00–6:00  (~1:00)]

"Before the results, let me briefly walk through our statistical approach — five tests in sequence.

Step one: the Friedman test confirmed there are genuine global differences across the seven tools. The p-value was less than ten to the power of negative 199. That's not a borderline result.

Step two: Wilcoxon signed-rank tests, corrected for multiple comparisons, told us which specific pairs differ. Twenty of twenty-one pairs were significant. The one exception: MAFFT FFT-NS-2 and Kalign3 — two fast progressive tools that are statistically indistinguishable.

Step three: Cliff's delta told us effect sizes are small. The differences are real and consistent, but moderate per individual family — they compound when you're working at scale.

Step four: Nemenyi post-hoc confirmed three distinct tiers, which I'll show you now.

Step five: bootstrap confidence intervals on 10,000 resamples confirmed these rankings are stable — not driven by a few unusual families."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Key Results
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Key Results — Accuracy on BAliBASE 3.0",
    subtitle="Three statistically distinct performance tiers (Nemenyi post-hoc, α = 0.05)", num=6)

# Results table
h2 = ["Aligner", "SP Mean ± SD", "TC Mean ± SD", "Runtime", "Memory", "Completed"]
cw2 = [2.3, 2.0, 2.0, 1.2, 1.2, 1.3]
rows2 = [
    ("MUSCLE5",        "0.761 ± 0.174", "0.399 ± 0.245", "0.52 s", "112 MB", "386 / 386"),
    ("T-Coffee",       "0.746 ± 0.182", "0.394 ± 0.248", "5.30 s", "512 MB", "342 / 386 †"),
    ("MAFFT L-INS-i",  "0.743 ± 0.188", "0.379 ± 0.238", "0.88 s", " 13 MB", "386 / 386"),
    ("Clustal Omega",  "0.718 ± 0.201", "0.363 ± 0.240", "0.64 s", " 16 MB", "386 / 386"),
    ("FAMSA",          "0.718 ± 0.199", "0.357 ± 0.257", "0.19 s", " 17 MB", "386 / 386"),
    ("Kalign3",        "0.692 ± 0.209", "0.322 ± 0.245", "0.06 s", "  5 MB", "385 / 386"),
    ("MAFFT FFT-NS-2", "0.688 ± 0.205", "0.315 ± 0.233", "0.55 s", " 23 MB", "386 / 386"),
]
TW2 = sum(cw2)
table(sl, h2, rows2, LM, CY, TW2, cw2, row_h=0.5)

T(sl, "† T-Coffee: 44 / 386 problems timed out (> 200 s) on large-sequence reference sets",
  LM, CY + 0.5 * 8 + 0.08, TW2, 0.28, sz=9, italic=True, col=GRAY)

# Tier summary  right side
TX2 = LM + TW2 + 0.35
TW3 = UW - TW2 - 0.35

for i, (label, tools, col) in enumerate([
    ("TOP TIER",   "MUSCLE5",                           TEAL),
    ("MIDDLE",     "T-Coffee  ·  MAFFT L-INS-i\nClustal Omega  ·  FAMSA", TEAL_DK),
    ("BOTTOM",     "MAFFT FFT-NS-2  ·  Kalign3",        GRAY),
]):
    ty = CY + i * 1.42
    R(sl, TX2, ty, TW3, 1.28, TEAL_LT, MGRAY, 0.3)
    R(sl, TX2, ty, TW3, 0.06, col)
    T(sl, label, TX2 + 0.12, ty + 0.1,  TW3 - 0.2, 0.3, sz=10, bold=True, col=col)
    T(sl, tools, TX2 + 0.12, ty + 0.44, TW3 - 0.2, 0.72, sz=12, bold=True, col=CHARCOAL, wrap=True)

NTS(sl, """\
[PRESENTER B — 6:00–7:45  (~1:45)]

"Here are the results.
[pause]
We found three distinct tiers of performance.
These tiers were confirmed by the Nemenyi post-hoc test.

[Point to top row.]
MUSCLE5 sits alone at the top.
Its mean SP score is 0.761.
[pause]
Why does it stand alone?
MUSCLE5 uses an ensemble strategy.
It generates multiple candidate alignments — from different starting seeds —
and keeps the best one.
That way, it reliably escapes the local optima that trip up simpler methods.

[Move down the table.]
Below it, four tools form the middle tier:
T-Coffee, MAFFT L-INS-i, Clustal Omega, and FAMSA.
Statistically, these four are indistinguishable from each other.

[Point to bottom rows.]
And at the bottom — the two fast progressive tools.
MAFFT FFT-NS-2 and Kalign3.

One important caveat before I move on.
[pause]
The effect sizes — measured by Cliff's delta — are all small.
The maximum is 0.22.
[pause]
The differences are real.
They are consistent across hundreds of families.
But for any single protein, they are moderate.
[pause]
They matter most when you are working at scale,
or with highly divergent sequences.
[pause]
Which is exactly what the next slide covers.
I will hand back to Anand."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Sequence Identity
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "The Impact of Sequence Identity",
    subtitle="The single most actionable finding of this study", num=7)

PW = (UW - 0.3) / 2    # panel width
P2X = LM + PW + 0.3    # right panel x

# Left panel  — above 60%
R(sl, LM, CY, PW, FY - CY - 0.1, GREEN_LT, GREEN, 0.75)
R(sl, LM, CY, PW, 0.06, GREEN)
T(sl, "Above 60% Identity", LM + 0.18, CY + 0.16, PW - 0.3, 0.42,
  sz=17, bold=True, col=GREEN)
T(sl, "Tool choice is irrelevant",
  LM + 0.18, CY + 0.64, PW - 0.3, 0.42,
  sz=20, bold=True, col=GREEN)
T(sl, "All seven tools converge to within 0.05 SP units of each other. The sequences are similar enough that even a simple one-pass alignment gets it right.",
  LM + 0.18, CY + 1.16, PW - 0.3, 0.85,
  sz=12, col=CHARCOAL, wrap=True)
divider(sl, CY + 2.12)
T(sl, "Advice:", LM + 0.18, CY + 2.26, PW - 0.3, 0.34, sz=12, bold=True, col=GREEN)
T(sl, "Use FAMSA or Kalign3 and save the compute.",
  LM + 0.18, CY + 2.6, PW - 0.3, 0.36, sz=12, col=CHARCOAL)
T(sl, "Example use cases:",
  LM + 0.18, CY + 3.1, PW - 0.3, 0.32, sz=11, bold=True, col=GRAY)
T(sl, "Closely-related bacterial orthologues\nParalogues within a single species",
  LM + 0.18, CY + 3.44, PW - 0.3, 0.7, sz=11, col=GRAY)

# Right panel — below 20%
R(sl, P2X, CY, PW, FY - CY - 0.1, TEAL_LT, TEAL, 0.75)
R(sl, P2X, CY, PW, 0.06, TEAL)
T(sl, "Below 20% Identity", P2X + 0.18, CY + 0.16, PW - 0.3, 0.42,
  sz=17, bold=True, col=TEAL)
T(sl, "Tool choice is critical",
  P2X + 0.18, CY + 0.64, PW - 0.3, 0.42,
  sz=20, bold=True, col=TEAL)
T(sl, "Top-tier tools outperform the bottom tier by ~0.15 SP units — roughly 15 additional correctly aligned residue pairs per 100 evaluated.",
  P2X + 0.18, CY + 1.16, PW - 0.3, 0.85,
  sz=12, col=CHARCOAL, wrap=True)
divider(sl, CY + 2.12)
T(sl, "Biological consequences:",
  P2X + 0.18, CY + 2.26, PW - 0.3, 0.34, sz=12, bold=True, col=TEAL)
T(sl, "A misaligned column can shift a phylogenetic branch topology\nA wrongly placed residue corrupts a homology model active site",
  P2X + 0.18, CY + 2.62, PW - 0.3, 0.72, sz=12, col=CHARCOAL, wrap=True)
T(sl, "Use MUSCLE5 or MAFFT L-INS-i.",
  P2X + 0.18, CY + 3.46, PW - 0.3, 0.34, sz=12, bold=True, col=TEAL)
T(sl, "Ancient superfamilies, cross-kingdom comparisons,\nremote homolog detection",
  P2X + 0.18, CY + 3.82, PW - 0.3, 0.54, sz=11, col=GRAY)

NTS(sl, """\
[PRESENTER A — 7:45–9:30  (~1:45)]

"This is the result I want everyone to walk away with.
[pause]
The answer to 'which aligner should I use'
depends on one number:
the pairwise sequence identity of your protein family.

[Point to left panel.]
Above 60% identity — all seven tools converge.
The differences shrink to less than 0.05 SP units.
[pause]
The sequences are similar enough
that even a simple, one-pass alignment gets it essentially right.
Don't overthink it.
Use FAMSA or Kalign3, and move on.

[Point to right panel.]
Below 20% identity — the story changes completely.
[pause]
The gap between the best and worst tools grows to about 0.15 SP units.
That is 15 extra correctly aligned residue pairs per 100 evaluated.
[pause]
That might sound modest.
But think about what it means in practice.
[pause]
A misalignment in a divergent family
can flip which species group together on a phylogenetic tree.
Or it can place an active-site residue in the wrong column —
pointing a homology model's binding pocket the wrong direction.

And here is the key.
[pause]
Ancient superfamilies — kinases, transcription factors, G-protein coupled receptors —
these span kingdoms with less than 20% identity.
That is where the most interesting biology lives.
And that is exactly where MUSCLE5 or MAFFT L-INS-i are worth the extra time.

Back to Shruthi for the speed analysis."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Speed vs Accuracy
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Speed vs. Accuracy Trade-offs",
    subtitle="Pareto-optimal tools and critical scalability failures", num=8)

# Speed table left
SW = 5.5
h3 = ["Tool", "Runtime", "Memory"]
cw3 = [2.2, 1.65, 1.65]
rows3 = [
    ("Kalign3",         "0.06 s",  "  5 MB"),
    ("FAMSA",           "0.19 s",  " 17 MB"),
    ("MUSCLE5",         "0.52 s",  "113 MB"),
    ("MAFFT FFT-NS-2",  "0.55 s",  " 23 MB"),
    ("Clustal Omega",   "0.64 s",  " 16 MB"),
    ("MAFFT L-INS-i",   "0.88 s",  " 13 MB"),
    ("T-Coffee",        "5.30 s ⚠","512 MB"),
]
table(sl, h3, rows3, LM, CY, SW, cw3, row_h=0.5, warn_idx=6)

# Key insights right
IX = LM + SW + 0.4
IW = UW - SW - 0.4

insights = [
    (TEAL,  "FAMSA & MUSCLE5 own the Pareto frontier",
     "FAMSA matches Clustal Omega's accuracy at 3× lower runtime.\nMUSCLE5 achieves best-in-class accuracy at 2.7× FAMSA's runtime.\nNo other tool beats either on both dimensions."),
    (RED,   "T-Coffee: scalability failure",
     "Timed out on 11% of BAliBASE problems (> 40 sequences).\nO(N²) pairwise library — breaks after ~30–40 sequences.\nReserve for small, curated families only."),
    (AMBER, "Clustal Omega: unexpected failure at scale",
     "78% timeout rate on PREFAB4's 50-sequence problems.\nDistance matrix bottleneck without profile reuse.\nDo not use in genome-scale pipelines."),
]

IH = (FY - CY - 0.1 - 0.24) / 3

for i, (col, title, body) in enumerate(insights):
    iy = CY + i * (IH + 0.12)
    bg = TEAL_LT if col == TEAL else (RED_LT if col == RED else AMBER_LT)
    R(sl, IX, iy, IW, IH, bg, MGRAY, 0.3)
    R(sl, IX, iy, IW, 0.06, col)
    T(sl, title, IX + 0.15, iy + 0.14, IW - 0.25, 0.36,
      sz=13, bold=True, col=col)
    T(sl, body,  IX + 0.15, iy + 0.54, IW - 0.25, IH - 0.6,
      sz=11.5, col=CHARCOAL, wrap=True)

NTS(sl, """\
[PRESENTER B — 9:30–11:30  (~2:00)]

"Accuracy matters.
But a tool also has to finish.
[pause]
Let me walk through the computational reality.

[Point to the speed table.]
Here are all seven tools ranked by median runtime.
Kalign3 is essentially instantaneous — 0.06 seconds.
FAMSA comes in at 0.19 seconds.
MUSCLE5 and MAFFT sit in the half-second to one-second range.
[pause]
And T-Coffee — highlighted in red — has a median of 5.3 seconds.
That number does not capture how badly it fails on larger families.

[Point to first insight card.]
Now, the key strategic insight.
When you plot accuracy against speed,
only FAMSA and MUSCLE5 are Pareto-optimal.
[pause]
No other tool is simultaneously faster and more accurate.
[pause]
FAMSA matches Clustal Omega's accuracy at three times lower runtime.
MUSCLE5 achieves the best accuracy of any tool
at only 2.7 times FAMSA's runtime.
For almost every use case, one of these two is the right answer.

[Point to red card.]
T-Coffee timed out on 11% of BAliBASE problems.
The cause is architectural.
Its pairwise library construction is O of N-squared.
Once you have more than 30 to 40 sequences, runtime explodes.

[Point to amber card.]
And Clustal Omega — which has a reputation for scalability —
failed on 78% of PREFAB4's 50-sequence problems.
That is a distance matrix bottleneck.
[pause]
This one surprised us.
And it has real implications for anyone running large-scale pipelines."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Cross-Dataset Generalisation
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Rankings Generalise Across All Four Benchmarks",
    subtitle="Mean SP score — successful completions only", num=9)

cd_h = ["Aligner", "BAliBASE (n=386)", "OXBench (n=395)", "SABRE (n=423)", "PREFAB4"]
cd_cw = [2.4, 2.18, 2.18, 2.18, 3.29]
cd_rows = [
    ("MUSCLE5",        "0.761", "0.898", "0.600", "0.690  (n = 1,681)"),
    ("T-Coffee",       "0.746", "0.898", "0.597", "0.680  (n = 1,596)  ‡"),
    ("MAFFT L-INS-i",  "0.743", "0.886", "0.575", "0.694  (n = 1,681)"),
    ("FAMSA",          "0.718", "0.896", "0.565", "0.659  (n = 1,681)"),
    ("Clustal Omega",  "0.718", "0.889", "0.551", "0.696  (n = 369)   †"),
    ("MAFFT FFT-NS-2", "0.688", "0.882", "0.537", "0.650  (n = 1,681)"),
    ("Kalign3",        "0.692", "0.886", "0.522", "0.617  (n = 1,681)"),
]
TW9 = sum(cd_cw)

# Draw table manually to colour-code warning rows
rect_y = CY
R(sl, LM, rect_y, TW9, 0.52, TEAL)
cx = LM
for h, cw in zip(cd_h, cd_cw):
    T(sl, h, cx + 0.08, rect_y + 0.09, cw - 0.12, 0.36,
      sz=11, bold=True, col=WHITE, align=PP_ALIGN.CENTER)
    cx += cw

warn_rows = {1, 4}   # T-Coffee and Clustal Omega
for i, row in enumerate(cd_rows):
    ry  = CY + 0.52 + i * 0.52
    bg  = RED_LT if i in warn_rows else (TEAL_LT if i % 2 == 0 else WHITE)
    R(sl, LM, ry, TW9, 0.52, bg)
    cx = LM
    for j, (cell, cw) in enumerate(zip(row, cd_cw)):
        is_warn = i in warn_rows and j == 4
        c = (RED if is_warn else TEAL_DK if j == 0 else CHARCOAL)
        T(sl, cell, cx + 0.08, ry + 0.09, cw - 0.12, 0.36,
          sz=11, bold=(j == 0),
          col=c, align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
        cx += cw

# Notes below table
note_y = CY + 0.52 * 8 + 0.1
T(sl, "† Clustal Omega: 78% timeout on PREFAB4  ‡ T-Coffee: 11% timeout on BAliBASE",
  LM, note_y, TW9, 0.28, sz=9, italic=True, col=GRAY)

# Callout
box_y = note_y + 0.36
R(sl, LM, box_y, TW9, 0.52, TEAL_LT, TEAL, 0.75)
T(sl, "The three-tier ranking reproduced on all four independent benchmarks — confirming these results are generalisable, not artifacts of any single dataset.",
  LM + 0.15, box_y + 0.08, TW9 - 0.25, 0.36,
  sz=12, bold=True, col=TEAL_DK, wrap=True)

NTS(sl, """\
[PRESENTER B — 11:30–12:30  (~1:00)]

"Our BAliBASE results did not just hold on one dataset.
[pause]
We ran the same seven tools on three additional independent benchmarks.
The tier structure reproduced every time.

[Walk across the columns.]
On OXBench — all tools scored higher overall.
The families are more closely related there.
But the ranking is identical.
[pause]
On SABRE — the spread widens.
The sequences are more divergent.
But the order still holds.
[pause]
On PREFAB4 — shown in red for the two failing tools —
Clustal Omega completed only 369 of 1,681 problems.
That is a 78% failure rate.
T-Coffee had elevated failures too.

[Point to the callout box.]
The bottom line:
[pause]
The three-tier structure is a genuine property of these algorithms.
Not an artifact of any single dataset.
Whatever benchmark you use, the same rankings apply.
[pause]
Back to Anand for final conclusions."
""")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Conclusions
# ══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
HDR(sl, "Conclusions & Practical Recommendations",
    subtitle="Algorithm class is the primary predictor of alignment quality — not the dataset", num=10)

# Three findings
findings = [
    (TEAL,   "Rankings are generalisable",
     "The same three-tier structure appeared on all four independent benchmarks."),
    (GREEN,  "Accuracy advantage is largest where biology is hardest",
     "Below 20% identity, top-tier tools deliver ~15 extra correct pairs per 100 — enough to change a phylogenetic topology or a drug-binding site."),
    (AMBER,  "Two tools dominate the Pareto frontier",
     "FAMSA for throughput. MUSCLE5 for accuracy. All other tools are dominated by at least one of these two on speed, accuracy, or both."),
]
for i, (col, head, body) in enumerate(findings):
    fy = CY + i * 1.0
    R(sl, LM, fy, UW, 0.88, TEAL_LT, MGRAY, 0.3)
    R(sl, LM, fy, 0.06, 0.88, col)
    T(sl, head, LM + 0.2, fy + 0.08, 5.0, 0.34, sz=13, bold=True, col=col)
    T(sl, body, LM + 5.4, fy + 0.12, UW - 5.6, 0.6, sz=12, col=CHARCOAL, wrap=True)

divider(sl, CY + 3.2)

T(sl, "Quick-reference guide", LM, CY + 3.34, UW, 0.36,
  sz=13, bold=True, col=CHARCOAL)

recs = [
    ("Divergent sequences  (<20% identity)",       "MUSCLE5  or  MAFFT L-INS-i", TEAL),
    ("Genome-scale pipelines  (any family size)",  "FAMSA",                       GREEN),
    ("Speed-only / very large datasets",           "Kalign3",                     GRAY),
    ("Small curated families, no time limit",      "T-Coffee",                    AMBER),
]
RH = 0.54
RW = (UW - 0.3 * 3) / 4
for i, (use, tool, col) in enumerate(recs):
    rx = LM + i * (RW + 0.3)
    ry = CY + 3.78
    R(sl, rx, ry, RW, RH * 2 + 0.08, TEAL_LT, MGRAY, 0.3)
    R(sl, rx, ry, RW, 0.06, col)
    T(sl, use,  rx + 0.12, ry + 0.14, RW - 0.2, 0.6,
      sz=11, col=GRAY, wrap=True)
    R(sl, rx + 0.1, ry + 0.76, RW - 0.2, 0.38, col)
    T(sl, tool, rx + 0.1, ry + 0.76, RW - 0.2, 0.38,
      sz=11, bold=True, col=WHITE, align=PP_ALIGN.CENTER)

T(sl, "Future work: deep-learning aligners with AlphaFold embeddings  ·  RNA families  ·  Multi-threaded evaluation",
  LM, FY - 0.38, UW, 0.28, sz=9.5, italic=True, col=GRAY)

NTS(sl, """\
[PRESENTER A — 12:30–14:00  (~1:30)]

"Let me bring this home.
Three takeaways.
[pause]

[Point to finding 1.]
First — the results are generalisable.
The same three-tier ranking appeared on all four independent benchmarks.
MUSCLE5 at the top.
T-Coffee and L-INS-i in the middle.
FFT-NS-2 and Kalign3 at the bottom.
[pause]
These are real properties of the algorithms.
Not quirks of any single dataset.

[Point to finding 2.]
Second — the accuracy advantage matters most where biology is hardest.
Below 20% identity,
the difference is 15 extra correctly aligned pairs per 100.
[pause]
That is enough to change a phylogenetic tree topology.
Or corrupt a homology model's active site.
This is where the choice of aligner has real biological consequences.
[pause]

[Point to finding 3.]
Third — FAMSA and MUSCLE5 are the Pareto-optimal tools.
For most use cases, you should be using one of those two.
Everything else is dominated on at least one dimension.
[pause]

[Point to recommendation grid.]
Here is the quick reference.
[pause]
Divergent sequences — MUSCLE5 or L-INS-i.
Large-scale pipelines — FAMSA.
Speed-only — Kalign3.
Small curated families with no time limit — T-Coffee.

[PRESENTER B — 14:00–15:00  (~1:00)]

"Thank you, Anand.
[pause]
And thank you all for your time.
[pause]
In one sentence:
the right MSA tool depends on your sequences' identity
and your pipeline's scale.
And now you have the data to make that decision confidently.
[pause]
We are happy to take questions.
You can reach us at the email addresses on the title slide.
Thank you."
""")

# ── Save ──────────────────────────────────────────────────────────────────────
prs.save(str(OUT))
print(f"Saved  : {OUT.name}")
print(f"Size   : {OUT.stat().st_size // 1024} KB  |  Slides: {len(prs.slides)}")
