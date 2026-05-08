# Figure Quality Standards for Academic Papers

Figures are the visual arguments of a paper. A poorly rendered figure is as damaging as a broken proof — reviewers notice immediately and it signals lack of rigor.

## SVG/PDF Figure Quality Requirements

### Mandatory Standards

Every figure in an academic paper MUST meet these quality standards:

1. **Vector format only**: SVG or PDF. Never PNG, JPEG, or screenshots for diagrams/charts. Raster formats are acceptable ONLY for photographs or complex heatmaps where vectorization degrades readability.

2. **Font consistency**: All text in figures (axis labels, legends, annotations) must use the same font family as the paper body. For LaTeX papers: Computer Modern or the paper's chosen font. For Word papers: Times New Roman or match body font.

3. **Minimum font size**: 7pt for the smallest text element in a figure (after scaling to column width). Axis labels ≥ 8pt. Title/heading ≥ 9pt.

4. **Line width**: ≥ 0.5pt for data lines, ≥ 0.75pt for axes. Hairline (≤ 0.25pt) lines disappear in print and on low-res screens.

5. **Color accessibility**: All figures must pass WCAG 2.1 AA contrast for text, AND be distinguishable in grayscale. Use colorblind-safe palettes (see below). Never rely solely on color to convey meaning — always add shape/pattern/label redundancy.

6. **Resolution floor for raster**: If raster is unavoidable (photos, heatmaps), minimum 300 DPI at print size. For supplementary high-res: 600 DPI.

### SVG-Specific Requirements

```python
# When generating SVGs programmatically (matplotlib, plotly, d3, etc.)

# REQUIRED SVG attributes:
# - viewBox for proper scaling
# - xmlns="http://www.w3.org/2000/svg"
# - font-family matching paper body
# - No hardcoded pixel widths — use relative units or viewBox scaling

# Matplotlib SVG export (recommended settings):
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(3.5, 2.5))  # Single column width for IEEE
ax.plot(x, y, linewidth=1.5)
ax.set_xlabel("Epoch", fontsize=9)
ax.set_ylabel("Accuracy (%)", fontsize=9)
ax.tick_params(labelsize=7)

# Critical: embed fonts in SVG
fig.savefig("fig1.svg", format="svg", bbox_inches="tight",
            metadata={"Date": None})  # Remove date for reproducibility
```

### PDF Figure Requirements

```python
# PDF export for LaTeX inclusion
fig.savefig("fig1.pdf", format="pdf", bbox_inches="tight",
            dpi=300,  # Minimum for any raster elements
            pad_inches=0.05)

# LaTeX inclusion:
# \includegraphics[width=\columnwidth]{fig1.pdf}  % Single column
# \includegraphics[width=0.48\textwidth]{fig1.pdf}  % Double column
```

### Colorblind-Safe Palettes

Use these verified palettes. Never use red-green区分 without additional markers.

```
Recommended (perceptually uniform, colorblind-safe):
- viridis (matplotlib default) — good for heatmaps/sequential data
- cet.C1 (colorcet) — good for categorical data
- Wong palette: #0072B2, #E69F00, #009E73, #CC79A7, #F0E442, #D55E00, #56B4E9
- IBM palette: #648FFF, #785EF0, #DC267F, #FE6100, #FFB000

Forbidden:
- Red-green diverging (deuteranopia confusion)
- Rainbow jet (perceptually non-uniform, misleading)
- Default Excel colors (unprofessional, accessibility issues)
```

## Figure Types and Standards

### Architecture/Overview Diagrams

```
Quality checklist:
- [ ] All components labeled with descriptive names (not "Component A")
- [ ] Data flow direction indicated with arrows
- [ ] Input/output boundaries clearly marked
- [ ] Color encoding is consistent across the paper
- [ ] SVG format, not rasterized
- [ ] Caption fully describes the diagram without requiring body text
- [ ] Works in grayscale print
```

### Result Charts (Line/Bar/Scatter)

```
Quality checklist:
- [ ] Axis labels include units
- [ ] Error bars or confidence intervals shown (std dev, min-max, or 95% CI)
- [ ] Legend does not overlap data
- [ ] Grid lines are subtle (0.25pt, gray, not black)
- [ ] Font sizes meet minimums (7pt smallest, 9pt labels)
- [ ] Line styles differ (solid/dashed/dotted) for grayscale readability
- [ ] Markers differ (circle/square/triangle) for accessibility
- [ ] Multiple datasets are clearly distinguishable
- [ ] Y-axis starts at 0 for bar charts (unless there's a reason not to)
- [ ] Captions describe the key takeaway, not just "Results"
```

### Ablation/Comparison Tables

```
Quality checklist:
- [ ] Best result in bold, second best underlined (IEEE style)
- [ ] Standard deviations reported (mean±std or with † footnote)
- [ ] Statistical significance marked (†, *, **)
- [ ] Horizontal lines: only top, bottom, and below header (booktabs style)
- [ ] No vertical lines (IEEE/ACM standard)
- [ ] Consistent decimal places within each column
- [ ] Column alignment: text left, numbers right, centered only for single-digit
```

### Heatmaps/Confusion Matrices

```
Quality checklist:
- [ ] Colorbar with labeled values
- [ ] Per-cell values displayed (if ≤ 10x10)
- [ ] Diagonal highlighted or emphasized
- [ ] Color scale is perceptually uniform (viridis, not jet)
- [ ] Row/column labels readable at column width
```

## Figure Generation Workflow

### Opencode Figure Generation Best Practices

When using opencode to generate figures for academic papers:

1. **Always generate SVG first**, then convert to PDF if needed for LaTeX.

2. **Set figure size in data coordinates**, not pixels. Use `figsize=(3.5, 2.5)` for single-column IEEE or `figsize=(7.16, 4)` for double-column.

3. **Never use `plt.show()`** — always `plt.savefig()` with explicit format and DPI settings.

4. **Test SVG rendering** by opening in a browser before including in the paper. Common issues:
   - Missing fonts (embed or specify fallback)
   - Incorrect viewBox (elements clipped)
   - Overlapping text (adjust positions)
   - Transparent backgrounds that look gray in some viewers

5. **Include a reproduce script** as supplementary material. Every figure should be reproducible from a script with `python fig_distance_emb.py`.

6. **Use consistent style across all figures** in the same paper:
   ```python
   # paper_style.py — shared style for all figures
   import matplotlib.pyplot as plt
   import matplotlib as mpl

   PAPER_STYLE = {
       'font.family': 'serif',
       'font.serif': ['Computer Modern', 'Times New Roman', 'DejaVu Serif'],
       'font.size': 9,
       'axes.labelsize': 9,
       'axes.titlesize': 10,
       'xtick.labelsize': 7,
       'ytick.labelsize': 7,
       'legend.fontsize': 7,
       'figure.figsize': (3.5, 2.5),
       'figure.dpi': 300,
       'lines.linewidth': 1.5,
       'lines.markersize': 4,
       'axes.linewidth': 0.75,
       'grid.linewidth': 0.25,
       'grid.alpha': 0.5,
       'savefig.bbox': 'tight',
       'savefig.pad_inches': 0.05,
   }

   def setup_paper_style():
       plt.rcParams.update(PAPER_STYLE)
   ```

## Common Figure Failures and Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| Blurry in print | PNG/JPEG at < 300 DPI | Regenerate as SVG/PDF |
| Text too small | No font size check | Ensure ≥ 7pt at column width |
| Invisible lines | Line width < 0.5pt | Set ≥ 0.75pt for axes, ≥ 1pt for data |
| Red-green confusion | Accessibility violation | Use viridis/Wong + shape markers |
| Font mismatch | System font in SVG | Use `font.serif` in rcParams |
| Cropped elements | No `bbox_inches='tight'` | Add `bbox_inches='tight'`, `pad_inches=0.05` |
| Grayscale unreadable | Color-only encoding | Add markers + line styles |
| Overlapping labels | Auto-layout failure | Manual adjustment or `tight_layout()` |
| Date in metadata | `metadata={"Date": None}` | Strip date for reproducibility |
| Giant file size | Embedded raster in SVG | Export pure vector or verify no base64 |

## Reviewer Figure Red Flags

These will get your paper flagged immediately:

1. **"Figure X is unreadable"** → Font too small, lines too thin, or PNG artifact
2. **"The diagram is unclear"** → No arrow direction, no labels, or rasterized diagram
3. **"What do the colors mean?"** → Missing legend or color-only encoding
4. **"The results seem cherry-picked"** → Y-axis not starting from 0 on bar chart, cropped range misleading
5. **"I cannot distinguish the lines"** → Color-only differentiation without markers/styles
6. **"This looks like a screenshot"** → PNG/JPEG used instead of vector format