from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

try:
    import originpro as op
except ModuleNotFoundError:  # Optional Windows-only dependency.
    op = None


PAGE_CM = 30.0
TIF_DPI = 300
TIF_WIDTH_PX = round(PAGE_CM / 2.54 * TIF_DPI)


def parse_args() -> argparse.Namespace:
    skill_root = Path(__file__).resolve().parents[2]
    default_template = skill_root / "assets" / "origin" / "Kasumi_IT_30cm_v1.otpu"
    parser = argparse.ArgumentParser(description="Render a personal Origin I-t figure.")
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--x-columns", required=True, help="Comma-separated X column names.")
    parser.add_argument("--y-columns", required=True, help="Comma-separated Y column names.")
    parser.add_argument("--legend-labels", required=True, help="Comma-separated legend labels.")
    parser.add_argument("--x-title", required=True)
    parser.add_argument("--y-title", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--template",
        type=Path,
        default=default_template,
    )
    parser.add_argument(
        "--y-scale",
        type=float,
        default=1.0,
        help="Explicit multiplicative Y conversion; default 1 means no conversion.",
    )
    parser.add_argument(
        "--minor-ticks",
        type=int,
        default=1,
        choices=range(0, 5),
    )
    parser.add_argument("--keep-origin-open", action="store_true")
    return parser.parse_args()


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        frame = pd.read_excel(path)
    elif suffix in {".csv", ".txt", ".tsv", ".dat"}:
        frame = pd.read_csv(path, sep=None, engine="python")
    else:
        raise ValueError(f"Unsupported input format: {suffix}")
    if frame.empty:
        raise ValueError("Input table is empty.")
    return frame


def validate_columns(
    frame: pd.DataFrame,
    x_columns: list[str],
    y_columns: list[str],
    legend_labels: list[str],
) -> None:
    if len(x_columns) == 1 and len(y_columns) > 1:
        x_columns[:] = x_columns * len(y_columns)
    if not (len(x_columns) == len(y_columns) == len(legend_labels)):
        raise ValueError("X columns, Y columns, and legend labels must have equal counts.")
    missing = [name for name in x_columns + y_columns if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    for name in dict.fromkeys(x_columns + y_columns):
        numeric = pd.to_numeric(frame[name], errors="coerce")
        if numeric.notna().sum() < 2:
            raise ValueError(f"Column is not numeric: {name}")


def origin_text(value: str) -> str:
    return value.replace("²", r"\+(2)").replace("³", r"\+(3)")


def build_legend(labels: list[str]) -> str:
    return "    ".join(f"\\l({index}) {origin_text(label)}" for index, label in enumerate(labels, 1))


def style_label(layer, name: str, text: str, size: int) -> None:
    label = layer.label(name)
    if label is None:
        label = layer.add_label(text)
    label.text = origin_text(text)
    label.set_float("fsize", size)
    label.lt_exec(f"{name}.font=font(Arial); {name}.showframe=0;")


def render(args: argparse.Namespace) -> dict[str, object]:
    if op is None:
        raise RuntimeError(
            "Origin rendering requires the optional 'originpro' package and a "
            "licensed Windows Origin/OriginPro installation."
        )
    source = args.input_file.resolve()
    template = args.template.resolve()
    output_dir = args.output_dir.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if not template.is_file():
        raise FileNotFoundError(template)
    if not math.isfinite(args.y_scale):
        raise ValueError("y-scale must be finite.")

    frame = load_table(source)
    x_columns = split_values(args.x_columns)
    y_columns = split_values(args.y_columns)
    legend_labels = split_values(args.legend_labels)
    validate_columns(frame, x_columns, y_columns, legend_labels)

    working = pd.DataFrame()
    x_indices: list[int] = []
    y_indices: list[int] = []
    for index, (x_name, y_name) in enumerate(zip(x_columns, y_columns), 1):
        x_out = f"X{index}_{x_name}"
        y_out = f"Y{index}_{y_name}"
        working[x_out] = pd.to_numeric(frame[x_name], errors="coerce")
        working[y_out] = pd.to_numeric(frame[y_name], errors="coerce") * args.y_scale
        x_indices.append(len(working.columns) - 2)
        y_indices.append(len(working.columns) - 1)

    output_dir.mkdir(parents=True, exist_ok=True)
    opju = output_dir / "result.opju"
    tif = output_dir / "result.tif"
    report = output_dir / "render_report.json"

    op.set_show(True)
    op.new()
    completed = False
    try:
        book = op.new_book("w", lname="I-t source data")
        sheet = book[0]
        sheet.from_df(working, addindex=False)
        graph = op.new_graph(lname="Personal I-t figure", template=str(template))
        layer = graph[0]

        for plot_index, (x_index, y_index) in enumerate(zip(x_indices, y_indices)):
            plot = layer.add_plot(sheet, coly=y_index, colx=x_index, type="l")
            plot.set_cmd("-sxs 1", "-sys 1")
            plot.set_float("line.width", 3)
            plot.set_int("symbol.kind", 0)

        graph.activate()
        formatting = f"""
        page.updatetoprinter=0;
        page.cntrl=16;
        layer.unit=3;
        layer.left=6.003;
        layer.top=5.004;
        layer.width=20;
        layer.height=20;
        layer.fixed=1;
        layer.color=0;
        layer.tickL=8;
        layer.tickW=3;
        layer.x.thickness=3;
        layer.y.thickness=3;
        layer.x.showAxes=3;
        layer.y.showAxes=3;
        layer.x.showLabels=1;
        layer.y.showLabels=1;
        layer.x.showGrids=0;
        layer.y.showGrids=0;
        layer.x.ticks=1;
        layer.y.ticks=1;
        layer.x.rescale=3;
        layer.y.rescale=3;
        layer.x.majorTicks=6;
        layer.y.majorTicks=6;
        layer.x.minorTicks={args.minor_ticks};
        layer.y.minorTicks={args.minor_ticks};
        layer.x.label.font=font(Arial);
        layer.y.label.font=font(Arial);
        layer.x.label.formula$="";
        layer.y.label.formula$="";
        layer.x.label.divideBy=1;
        layer.y.label.divideBy=1;
        layer.x.label.numFormat=1;
        layer.y.label.numFormat=1;
        layer.x.label.decPlaces=-1;
        layer.y.label.decPlaces=-1;
        """
        if not op.lt_exec(formatting):
            raise RuntimeError("Origin formatting command failed.")

        style_label(layer, "XB", args.x_title, 40)
        style_label(layer, "YL", args.y_title, 40)
        style_label(layer, "Text", build_legend(legend_labels), 40)
        style_label(layer, "Legend", args.condition, 30)

        layer.rescale()
        op.save(str(opju))
        exported = graph.save_fig(str(tif), type="tif", width=TIF_WIDTH_PX)
        if not exported or not tif.is_file() or tif.stat().st_size == 0:
            raise RuntimeError("Origin TIFF export failed.")

        with Image.open(tif) as image:
            tif_size = image.size
            tif_dpi = image.info.get("dpi")

        payload = {
            "source": str(source),
            "template": str(template),
            "x_columns": x_columns,
            "y_columns": y_columns,
            "legend_labels": legend_labels,
            "x_title": args.x_title,
            "y_title": args.y_title,
            "condition": args.condition,
            "y_scale": args.y_scale,
            "minor_ticks": args.minor_ticks,
            "opju": str(opju),
            "tif": str(tif),
            "tif_pixels": list(tif_size),
            "tif_dpi_metadata": [float(value) for value in tif_dpi] if tif_dpi else None,
            "raw_data_unchanged": True,
            "smoothing": False,
            "interpolation": False,
            "baseline_subtraction": False,
        }
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        completed = True
        return payload
    finally:
        if args.keep_origin_open and completed:
            op.detach()
        else:
            op.exit()


def main() -> int:
    try:
        result = render(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
