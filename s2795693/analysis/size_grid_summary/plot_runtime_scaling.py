#!/usr/bin/env python3
"""Plot runtime scaling by problem size using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import html
import math
import statistics
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "runtime_results.csv"
DEFAULT_OUTPUT = SCRIPT_DIR / "runtime_scaling.svg"
DEFAULT_AGGREGATE = SCRIPT_DIR / "runtime_scaling_aggregated.csv"

SCALE_ORDER = ["small", "medium-small", "medium", "large", "very-large"]
THREAD_ORDER = [1, 2, 4, 8]
THREAD_STYLES = {
    1: ("#1f77b4", "circle"),
    2: ("#ff7f0e", "square"),
    4: ("#2ca02c", "triangle"),
    8: ("#d62728", "diamond"),
}


def parse_number(value: str) -> float:
    return float(value.replace(",", ""))


def read_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("status") != "completed" or not row.get("runtime_seconds"):
                continue
            threads = int(row["threads"])
            if threads not in THREAD_ORDER:
                continue
            rows.append(
                {
                    "scale": row["scale"],
                    "unknowns": int(row["unknowns"]),
                    "m": int(row["m"]),
                    "n": int(row["n"]),
                    "nodes": int(row["nodes"]),
                    "ppn": int(row["ppn"]),
                    "threads": threads,
                    "mpi_ranks": int(row["mpi_ranks"]),
                    "total_cores": int(row["total_cores"]),
                    "runtime_seconds": parse_number(row["runtime_seconds"]),
                }
            )
    return rows


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = (str(row["scale"]), int(row["total_cores"]), int(row["threads"]))
        grouped[key].append(row)

    out: list[dict[str, object]] = []
    for (scale, total_cores, threads), group in grouped.items():
        runtimes = [float(row["runtime_seconds"]) for row in group]
        first = group[0]
        out.append(
            {
                "scale": scale,
                "unknowns": first["unknowns"],
                "m": first["m"],
                "n": first["n"],
                "threads": threads,
                "total_cores": total_cores,
                "median_runtime_seconds": statistics.median(runtimes),
                "mean_runtime_seconds": statistics.mean(runtimes),
                "min_runtime_seconds": min(runtimes),
                "max_runtime_seconds": max(runtimes),
                "repeat_count": len(runtimes),
            }
        )

    scale_rank = {scale: i for i, scale in enumerate(SCALE_ORDER)}
    return sorted(
        out,
        key=lambda row: (
            scale_rank.get(str(row["scale"]), 999),
            int(row["total_cores"]),
            int(row["threads"]),
        ),
    )


def write_aggregate(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "scale",
        "unknowns",
        "m",
        "n",
        "threads",
        "total_cores",
        "median_runtime_seconds",
        "mean_runtime_seconds",
        "min_runtime_seconds",
        "max_runtime_seconds",
        "repeat_count",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def scale_label(unknowns: int) -> str:
    return f"{unknowns / 1_000_000:.2f}M unknowns"


def nice_linear_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    if lo == hi:
        return [lo]
    raw_step = (hi - lo) / max(count - 1, 1)
    exponent = math.floor(math.log10(raw_step))
    fraction = raw_step / 10**exponent
    if fraction <= 1:
        nice_fraction = 1
    elif fraction <= 2:
        nice_fraction = 2
    elif fraction <= 5:
        nice_fraction = 5
    else:
        nice_fraction = 10
    step = nice_fraction * 10**exponent
    start = math.floor(lo / step) * step
    end = math.ceil(hi / step) * step
    ticks = []
    value = start
    while value <= end + step * 0.5:
        ticks.append(value)
        value += step
    return ticks


def log_ticks(lo: float, hi: float) -> list[float]:
    ticks: list[float] = []
    start = math.floor(math.log10(lo))
    end = math.ceil(math.log10(hi))
    for exponent in range(start, end + 1):
        for multiplier in (1, 2, 5):
            value = multiplier * 10**exponent
            if lo <= value <= hi:
                ticks.append(float(value))
    return ticks


def fmt_tick(value: float) -> str:
    if value >= 1000:
        return f"{value / 1000:g}k"
    if value >= 10:
        return f"{value:g}"
    return f"{value:.2g}"


def marker_svg(kind: str, x: float, y: float, color: str) -> str:
    if kind == "circle":
        return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}" />'
    if kind == "square":
        return f'<rect x="{x - 4:.2f}" y="{y - 4:.2f}" width="8" height="8" fill="{color}" />'
    if kind == "triangle":
        return (
            f'<path d="M {x:.2f} {y - 5:.2f} L {x + 5:.2f} {y + 4:.2f} '
            f'L {x - 5:.2f} {y + 4:.2f} Z" fill="{color}" />'
        )
    return (
        f'<path d="M {x:.2f} {y - 5:.2f} L {x + 5:.2f} {y:.2f} '
        f'L {x:.2f} {y + 5:.2f} L {x - 5:.2f} {y:.2f} Z" fill="{color}" />'
    )


def render_svg(rows: list[dict[str, object]], output: Path, yscale: str) -> None:
    width, height = 1500, 930
    margin_left, margin_right = 86, 40
    margin_top, margin_bottom = 130, 82
    gap_x, gap_y = 70, 92
    cols, rows_n = 3, 2
    panel_w = (width - margin_left - margin_right - gap_x * (cols - 1)) / cols
    panel_h = (height - margin_top - margin_bottom - gap_y * (rows_n - 1)) / rows_n
    x_ticks = [1, 2, 4, 8, 16, 32, 64, 128]
    x_min, x_max = math.log2(min(x_ticks)), math.log2(max(x_ticks))

    by_scale: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_scale[str(row["scale"])].append(row)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: Arial, Helvetica, sans-serif; fill: #222; }",
        ".title { font-size: 30px; font-weight: 700; }",
        ".subtitle { font-size: 16px; fill: #555; }",
        ".panel-title { font-size: 19px; font-weight: 700; }",
        ".axis-label { font-size: 15px; fill: #333; }",
        ".tick { font-size: 12px; fill: #555; }",
        ".grid { stroke: #ddd; stroke-width: 1; }",
        ".axis { stroke: #333; stroke-width: 1.4; }",
        ".series { fill: none; stroke-width: 2.7; }",
        "</style>",
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        '<text class="title" x="750" y="42" text-anchor="middle">Runtime vs Total Cores</text>',
        (
            f'<text class="subtitle" x="750" y="68" text-anchor="middle">'
            f'Median solve/runtime seconds by thread count; x-axis is nodes x ppn x threads; y-scale: {yscale}</text>'
        ),
    ]

    for idx, scale in enumerate(SCALE_ORDER):
        panel_rows = by_scale.get(scale, [])
        if not panel_rows:
            continue
        col, row_idx = idx % cols, idx // cols
        x0 = margin_left + col * (panel_w + gap_x)
        y0 = margin_top + row_idx * (panel_h + gap_y)
        runtimes = [float(row["median_runtime_seconds"]) for row in panel_rows]
        y_min, y_max = min(runtimes), max(runtimes)
        if yscale == "log":
            y_min = max(y_min * 0.85, 0.001)
            y_max = y_max * 1.18
            y_ticks = log_ticks(y_min, y_max)

            def y_pos(value: float) -> float:
                return y0 + panel_h - (
                    (math.log10(value) - math.log10(y_min))
                    / (math.log10(y_max) - math.log10(y_min))
                ) * panel_h

        else:
            pad = (y_max - y_min) * 0.08 if y_max > y_min else y_max * 0.1
            y_min = max(0.0, y_min - pad)
            y_max = y_max + pad
            y_ticks = [tick for tick in nice_linear_ticks(y_min, y_max) if y_min <= tick <= y_max]

            def y_pos(value: float) -> float:
                return y0 + panel_h - ((value - y_min) / (y_max - y_min)) * panel_h

        def x_pos(value: int) -> float:
            return x0 + ((math.log2(value) - x_min) / (x_max - x_min)) * panel_w

        unknowns = int(panel_rows[0]["unknowns"])
        title = html.escape(scale_label(unknowns))
        parts.append(f'<g transform="translate(0,0)">')
        parts.append(f'<text class="panel-title" x="{x0:.2f}" y="{y0 - 18:.2f}">{title}</text>')
        parts.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{panel_w:.2f}" height="{panel_h:.2f}" fill="#fafafa" stroke="#c8c8c8"/>')

        for tick in y_ticks:
            py = y_pos(tick)
            parts.append(f'<line class="grid" x1="{x0:.2f}" y1="{py:.2f}" x2="{x0 + panel_w:.2f}" y2="{py:.2f}"/>')
            parts.append(f'<text class="tick" x="{x0 - 9:.2f}" y="{py + 4:.2f}" text-anchor="end">{fmt_tick(tick)}</text>')

        for tick in x_ticks:
            px = x_pos(tick)
            parts.append(f'<line class="grid" x1="{px:.2f}" y1="{y0:.2f}" x2="{px:.2f}" y2="{y0 + panel_h:.2f}"/>')
            parts.append(f'<text class="tick" x="{px:.2f}" y="{y0 + panel_h + 20:.2f}" text-anchor="middle">{tick}</text>')

        parts.append(f'<line class="axis" x1="{x0:.2f}" y1="{y0 + panel_h:.2f}" x2="{x0 + panel_w:.2f}" y2="{y0 + panel_h:.2f}"/>')
        parts.append(f'<line class="axis" x1="{x0:.2f}" y1="{y0:.2f}" x2="{x0:.2f}" y2="{y0 + panel_h:.2f}"/>')

        for threads in THREAD_ORDER:
            series = [
                row
                for row in panel_rows
                if int(row["threads"]) == threads and int(row["total_cores"]) in x_ticks
            ]
            series.sort(key=lambda row: int(row["total_cores"]))
            if not series:
                continue
            color, marker = THREAD_STYLES[threads]
            points = [
                (x_pos(int(row["total_cores"])), y_pos(float(row["median_runtime_seconds"])))
                for row in series
            ]
            path = " ".join(
                ("M" if i == 0 else "L") + f" {x:.2f} {y:.2f}" for i, (x, y) in enumerate(points)
            )
            parts.append(f'<path class="series" d="{path}" stroke="{color}"/>')
            for x, y in points:
                parts.append(marker_svg(marker, x, y, color))
        parts.append("</g>")

    label_x = margin_left + (width - margin_left - margin_right) / 2
    label_y = height - 24
    parts.append(f'<text class="axis-label" x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="middle">Total cores = nodes x ppn x threads</text>')
    parts.append(
        f'<text class="axis-label" x="24" y="{height / 2:.2f}" text-anchor="middle" transform="rotate(-90 24 {height / 2:.2f})">Runtime / solve time (seconds)</text>'
    )

    legend_x = margin_left + 2 * (panel_w + gap_x) + 38
    legend_y = margin_top + panel_h + gap_y + 30
    parts.append(f'<text class="panel-title" x="{legend_x:.2f}" y="{legend_y:.2f}">Threads</text>')
    for i, threads in enumerate(THREAD_ORDER):
        color, marker = THREAD_STYLES[threads]
        y = legend_y + 30 + i * 30
        parts.append(f'<line x1="{legend_x:.2f}" y1="{y:.2f}" x2="{legend_x + 34:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="2.7"/>')
        parts.append(marker_svg(marker, legend_x + 17, y, color))
        parts.append(f'<text class="axis-label" x="{legend_x + 48:.2f}" y="{y + 5:.2f}">T = {threads}</text>')

    parts.append("</svg>")
    output.write_text("\n".join(parts) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--aggregate", type=Path, default=DEFAULT_AGGREGATE)
    parser.add_argument("--yscale", choices=["linear", "log"], default="linear")
    args = parser.parse_args()

    raw_rows = read_rows(args.input)
    aggregated = aggregate(raw_rows)
    write_aggregate(args.aggregate, aggregated)
    render_svg(aggregated, args.output, args.yscale)

    print(f"read rows: {len(raw_rows)}")
    print(f"aggregated rows: {len(aggregated)}")
    print(f"wrote aggregate: {args.aggregate}")
    print(f"wrote figure: {args.output}")


if __name__ == "__main__":
    main()
