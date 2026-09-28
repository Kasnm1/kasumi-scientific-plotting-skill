# Bundled personal examples

Everything under `assets/personal-examples/data/` is demonstration material, not a new measurement.

- The I-V tables are simulated.
- `guangxiangy_optimized.txt` is a historically adjusted spectrum and is not raw experimental evidence.
- The scripts under `scripts/personal/` reproduce prior examples. Several synthesize I-t, rise/fall, spectral, or polarization data from model assumptions.
- Preserve `SIMULATED_REHEARSAL`, `MODEL_DERIVED`, or an equally explicit provenance label in every generated table and parameter report.
- Do not use the example currents, noise, response times, polarization ratios, periods, or axis limits as defaults for measured data.

Set `FIGURE_DATA_ROOT` to replace the bundled examples and `FIGURE_OUTPUT_ROOT` to select a delivery directory. Without an output override, the examples write to `outputs/` under the current working directory.
