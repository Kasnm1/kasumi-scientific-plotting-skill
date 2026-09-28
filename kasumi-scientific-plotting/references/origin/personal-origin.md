# Licensed Origin routes

Use Origin only when the user explicitly requests it. Python is the default for the personal template.

## Fixed personal I-t renderer

1. Inspect the source table without modifying it.
2. Resolve X columns, Y columns, legend labels, axis titles, condition text, any unit multiplier, and minor-tick count.
3. Run `scripts/origin/render_it_origin.py` with explicit mappings and an output directory.
4. Verify `result.opju`, `result.tif`, and `render_report.json` and visually inspect the TIFF.

Contract: 30 × 30 cm page; 20 × 20 cm Origin layer positioned at left 6.003 cm and top 5.004 cm; Arial; 40 pt axes/ticks/legend; 30 pt condition; 3 pt axes and curves; inward 8 pt major ticks; white background; no grid; editable OPJU and 300 dpi TIFF.

The bundled OTPU is a user template, not Origin software. The user must supply a legally installed and activated Origin environment plus the `originpro` runtime.

## EditaPlot route

For general Origin charts, read these files before rendering:

- `references/origin/editaplot/origin-safety.md`
- `references/origin/editaplot/figure-contract.md`
- `references/origin/editaplot/verification.md`
- `references/origin/editaplot/data-contracts.md` and `chart-selection.md` for a new table

Run `python scripts/editaplot/editaplot.py doctor --engine-home <engine-root>` first. The public Skill contains the compatibility wrapper, palette metadata, and safety references; it does not contain the separate rendering engine or Origin. Stop if the doctor reports a manual blocker. Never claim an Origin result from a PNG alone.
