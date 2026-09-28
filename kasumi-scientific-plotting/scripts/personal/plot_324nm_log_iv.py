from __future__ import annotations

import runpy
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS

# Reuse the frozen 254 nm renderer verbatim, changing only source/output paths.
script = Path(__file__).with_name("plot_254nm_log_iv.py")
source = script.read_text(encoding="utf-8")
source = source.replace(
    "变光强IV--254nm_8至350uWcm2_负5至正5V_绝对值-1.txt",
    "变光强IV--324nm_8至350uWcm2_负5至正5V_绝对值-1.txt",
).replace(
    '"254nm_变光强IV_对数坐标"',
    '"324nm_变光强IV_对数坐标"',
).replace(
    "bbox_to_anchor=(0.50, 0.985)",
    "bbox_to_anchor=(0.50, 1.015)",
)

compiled = compile(source, str(script), "exec")
exec(compiled, {"__name__": "__main__", "__file__": str(script)})
