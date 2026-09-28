# Kasumi personal scientific-figure contract

This is a personal visual contract, not a universal journal style. Current user instructions override it.

## Base layout

- Canvas: 30 × 30 cm. Plot area: 20 × 16 cm, normally 6 cm from the left and 7 cm from the bottom.
- Arial. Axis titles and tick labels: 40 pt. In-plot legend and outside condition text: 30 pt.
- Four-sided black frame. Axes and ordinary curves: 3 pt. Major ticks: inward, 8 pt long, shown on the left and bottom only.
- White background and no grid. Keep the page dimensions fixed; do not use tight cropping that changes the physical canvas.
- Put the legend inside near the top without a frame. Keep the test condition above the frame at the right when needed.
- Export a 300 dpi PNG preview, 600 dpi TIFF, editable-text SVG, and PDF when requested.

## I-t

- 254 nm: `#8A80DB`. 324 nm: `#E797B9`.
- Gradient area fills run from pale near the baseline to stronger near the signal. They encode signal area, not uncertainty.
- Avoid blended overlap between multiple filled curves. The confirmed 1/3/5 V example uses pale green, pink, and blue-purple, but do not generalize it to unrelated conditions without checking.
- Use the actual period and complete cycles. Never stretch the trace to obtain a desired edge time.

## I-V

- Use absolute current on a logarithmic axis only when explicitly requested; preserve the original signed current in the source record.
- Historical axis limits and legend anchors belong to their examples, not to every dataset.

## Spectrum

- Preferred visual language: pale blue-purple line and layered circular markers, with an optional peak line and data-derived peak/FWHM labels.
- Distinguish photocurrent from responsivity. Responsivity requires valid incident-power data.
- Compute FWHM from the supplied data and state the baseline definition; never copy it from an example.

## Rise/fall

- Normalized current; omit the Y-axis title and Y ticks while retaining the four-sided frame.
- Show 10%/90% guide lines and pale response-time windows only when the thresholds and response definition are valid for the supplied trace.
- The bundled 811/897 μs, 3 ms pulse, and 4.1 ms view are simulation settings, not personal-style defaults.

## NEP and D*

- A compact 30 × 22 cm page may retain the 20 × 16 cm plot area.
- Use pale blue for NEP and pale purple for D*. Show frequency decade ticks as ordinary numbers when requested.
- Preserve the supplied NEP unit. Do not silently change `W/√Hz` to `W` or vice versa.
