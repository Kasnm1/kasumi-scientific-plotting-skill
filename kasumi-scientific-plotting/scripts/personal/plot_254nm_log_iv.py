from __future__ import annotations

import csv
import math
import sys
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS

ROOT = DATA_ROOT
SOURCE = ROOT / "电学模拟数据_20260918" / "04_变光强IV_3V" / "变光强IV--254nm_8至350uWcm2_负5至正5V_绝对值-1.txt"
OUT = OUTPUT_ROOT / "254nm_变光强IV_对数坐标"
SKILL_SCRIPTS = NATURE_SCRIPTS
sys.path.insert(0, str(SKILL_SCRIPTS))

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker

from audit_panel_alignment import require_matplotlib_panel_alignment


CM = 1 / 2.54
PAGE_CM = 30.0
AX_LEFT_CM = 6.0
AX_BOTTOM_CM = 7.0
AX_WIDTH_CM = 20.0
AX_HEIGHT_CM = 16.0

arial = Path(r"C:\Windows\Fonts\arial.ttf")
if arial.is_file():
    font_manager.fontManager.addfont(str(arial))
mpl.rcParams.update({
    "font.family": "Arial",
    "font.sans-serif": ["Arial"],
    "font.size": 40,
    "axes.linewidth": 3,
    "lines.linewidth": 3,
    "xtick.major.width": 3,
    "ytick.major.width": 3,
    "xtick.minor.width": 2.5,
    "ytick.minor.width": 2.5,
    "xtick.major.size": 8,
    "ytick.major.size": 8,
    "xtick.minor.size": 4,
    "ytick.minor.size": 4,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "legend.frameon": False,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.facecolor": "white",
})


def read_table(path: Path):
    with path.open(encoding="ascii", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    labels = rows[0]
    values = [[float(value) for value in row] for row in rows[1:]]
    assert labels == ["Voltage", "Dark", "8", "12", "35", "66", "130", "210", "350"]
    assert len(values) == 201 and all(len(row) == 9 for row in values)
    assert all(row[col] > 0 for row in values for col in range(1, 9))
    return labels, values


def log_label(value, _position):
    if value <= 0:
        return ""
    if value < 1e-3:
        exponent = round(math.log10(value))
        return f"1E{exponent}"
    if value < 1:
        return f"{value:g}"
    return f"{value:g}"


labels, data = read_table(SOURCE)
voltage = [row[0] for row in data]

# Reference-inspired cool-to-warm sequence; Dark remains a distinct deep teal.
colors = [
    "#08766F",  # Dark
    "#00A99D",  # 8
    "#2CC3B5",  # 12
    "#AFE3D5",  # 35
    "#FFD3A1",  # 66
    "#FF8426",  # 130
    "#D06508",  # 210
    "#944004",  # 350
]

fig = plt.figure(figsize=(PAGE_CM * CM, PAGE_CM * CM), facecolor="white")
ax = fig.add_axes([
    AX_LEFT_CM / PAGE_CM,
    AX_BOTTOM_CM / PAGE_CM,
    AX_WIDTH_CM / PAGE_CM,
    AX_HEIGHT_CM / PAGE_CM,
])

for column, (label, color) in enumerate(zip(labels[1:], colors), start=1):
    current_na = [row[column] * 1e9 for row in data]
    ax.plot(voltage, current_na, color=color, label=label, solid_capstyle="round")

ax.set_xlim(-5, 5)
ax.set_ylim(1.1e-5, 7800)
ax.set_yscale("log")
ax.set_xticks([-5, -2.5, 0, 2.5, 5])
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=10))
ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=tuple(range(2, 10)), numticks=100))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(log_label))
ax.yaxis.set_minor_formatter(ticker.NullFormatter())

for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(3)
    spine.set_color("black")

ax.tick_params(axis="both", which="major", direction="in", top=False, right=False,
               bottom=True, left=True, labelsize=40, pad=12)
ax.tick_params(axis="both", which="minor", direction="in", top=False, right=False,
               bottom=True, left=True)

# Axis titles use page coordinates so every plot shares the same anchors.
fig.text(16 / PAGE_CM, 3.8 / PAGE_CM, "Voltage (V)", ha="center", va="center", fontsize=40)
fig.text(1.2 / PAGE_CM, 15 / PAGE_CM, "|Current| (nA)", ha="center", va="center",
         rotation=90, rotation_mode="anchor", fontsize=40)

legend = ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.50, 0.985),
    ncol=3,
    fontsize=30,
    handlelength=2.1,
    handletextpad=0.45,
    columnspacing=1.15,
    labelspacing=0.25,
    borderaxespad=0.0,
)
for line in legend.get_lines():
    line.set_linewidth(3)

fig.canvas.draw()
require_matplotlib_panel_alignment(
    fig,
    json_out=str(OUT) + ".alignment.json",
    overlay_svg=str(OUT) + ".alignment.svg",
    tolerance_pt=1.5,
    gutter_tolerance_pt=1.5,
    strict=True,
)

# No bbox_inches='tight': exact 30 x 30 cm page and fixed title anchors must survive export.
fig.savefig(str(OUT) + ".svg")
fig.savefig(str(OUT) + ".pdf")
fig.savefig(str(OUT) + ".tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
fig.savefig(str(OUT) + "_preview.png", dpi=300)
plt.close(fig)
