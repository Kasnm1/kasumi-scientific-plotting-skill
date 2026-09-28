---
name: kasumi-scientific-plotting
description: Create, revise, audit, and export scientific figures using Kasumi's personal photodetector style, publication-oriented Python or R workflows, built-in image generation for scientific schematics, or an explicitly requested licensed Origin workflow. Use for I-V, I-t, spectra, rise/fall, polarization, general manuscript charts, multi-panel figures, mechanism diagrams, graphical abstracts, and figure QA. Do not use for statistics-only analysis or to invent, smooth, normalize, or replace experimental data without explicit authorization.
---

# Kasumi Scientific Plotting

Use one route per deliverable unless the user explicitly requests a mixed figure. Current user instructions, project-level rules, target-journal requirements, and verified data semantics take precedence over every bundled default.

## Non-negotiable data boundary

- Inspect the input file and map X/Y columns, units, conditions, replicates, missing values, and transformations before drawing.
- Never invent measurements, error bars, sample sizes, significance, response times, peaks, or mechanisms.
- Do not smooth, interpolate, normalize, baseline-correct, remove points, fit, or convert units unless the user requests it or the transformation is already part of a documented analysis. Record every transformation.
- Bundled personal example data and scripts are simulations or historically adjusted examples. Use them only for an explicit simulation or style-reproduction request, and keep the provenance label in generated data and reports.
- A generated schematic is never a quantitative data panel. Distinguish evidence, hypothesis, and visual explanation.

## Choose the route

### Personal photodetector figures (default for the owner's I-V/I-t work)

Use Python/Matplotlib. Read [the personal style contract](references/personal/personal-style.md) before rendering. For an example-specific reproduction, also read [the example provenance](references/personal/example-provenance.md).

Apply this route to I-V, I-t, wavelength or frequency response, spectral photocurrent, polarization, and rise/fall figures when the user asks for the personal template. The personal physical dimensions override generic journal dimensions. Reuse example scripts under `scripts/personal/` only as style or simulation references; for measured data, implement an explicit input mapping rather than replacing the data with the example model.

### General manuscript and multi-panel figures

Read [the figure contract](references/publication/core/contract.md) and [the default publication stance](references/publication/core/stance.md). Use Python by default for this owner's workspace unless the current request or project rules choose R. Then read only the matching backend guide:

- Python: [Python backend](references/publication/backend/python.md)
- R: [R backend](references/publication/backend/r.md)

For multi-panel planning, read [multi-panel evidence architecture](references/publication/multipanel-evidence-architecture.md). For template adaptation, read [asset adaptation](references/publication/asset-adaptation.md). Load other material in `references/publication/` only when the figure type, journal, legend, or export task needs it.

### Mechanism diagrams and graphical abstracts

Read [the graphical-abstract workflow](references/publication/ai-graphical-abstract-workflow.md). Use the built-in image-generation capability when available; do not call third-party image-generation services, request API keys, or imply that generated artwork is measured evidence. Use local SVG/Matplotlib when the user needs editable labels or exact relationships. Verify every label, arrow, entity count, causal direction, and scientific claim after generation.

### Origin and EditaPlot (explicit request only)

Use this route only when the user explicitly asks for Origin, OriginPro, OPJU, or the EditaPlot engine. Read [the Origin route](references/origin/personal-origin.md) and the applicable EditaPlot references under `references/origin/editaplot/` before rendering.

Require the user's own licensed Windows Origin installation. Never install, activate, patch, bypass, or redistribute Origin. The fixed personal I-t renderer is `scripts/origin/render_it_origin.py`; the template is `assets/origin/Kasumi_IT_30cm_v1.otpu`. The broader `scripts/editaplot/` wrapper requires a separately supplied EditaPlot engine and must pass its doctor check before use. Do not use mouse automation.

## Render, audit, and deliver

1. Freeze the figure-level claim, source mapping, axes/units, transformations, palette semantics, output size, and formats.
2. Render from the verified source while preserving raw data.
3. Read [the QA contract](references/publication/qa-contract.md). For generated or revised Python/R figures, run the relevant tools under `scripts/publication/`:
   - `validate_figure.py` for source checks;
   - `audit_panel_alignment.py` for comparable multi-panel geometry;
   - `audit_pdf_text.py` for actual PDF font sizes;
   - `audit_figure_collisions.py` for clipping and overlaps.
4. Inspect every final export at its physical delivery size. Automated checks do not replace visual review.
5. Deliver the plotting source, a PNG preview, editable PDF or SVG when applicable, requested TIFF, and provenance/parameter records. Never report success from a preview alone.

Treat `FIX BEFORE DELIVERY`, a failed command, missing output, or an unauditable mandatory check as a blocker. Preserve the original input and write outputs to the current project or a user-specified destination, not into the installed Skill.
