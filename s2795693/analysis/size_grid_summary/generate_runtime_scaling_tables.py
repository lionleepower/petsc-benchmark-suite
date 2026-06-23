#!/usr/bin/env python3
"""Generate report-ready runtime scaling tables by problem size."""

from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RUNTIME_RESULTS = SCRIPT_DIR / "runtime_results.csv"
OUTPUT_MD = SCRIPT_DIR / "runtime_scaling_tables.md"
OUTPUT_CSV = SCRIPT_DIR / "runtime_scaling_tables_all.csv"

SCALE_ORDER = ["small", "medium-small", "medium", "large", "very-large"]
TABLE_LABELS = {
    "small": "Table 1a",
    "medium-small": "Table 1b",
    "medium": "Table 1c",
    "large": "Table 1d",
    "very-large": "Table 1e",
}
GROUP_COLUMNS = [
    "scale",
    "m",
    "n",
    "unknowns",
    "nodes",
    "ppn",
    "threads",
    "mpi_ranks",
    "total_cores",
    "unknowns_per_core",
    "matrix_type",
]


def parse_float(value: str) -> float:
    return float(value.replace(",", ""))


def parse_int(value: str) -> int:
    return int(float(value.replace(",", "")))


def read_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["status"] != "completed" or not row["runtime_seconds"]:
                continue
            rows.append(
                {
                    "scale": row["scale"],
                    "m": parse_int(row["m"]),
                    "n": parse_int(row["n"]),
                    "unknowns": parse_int(row["unknowns"]),
                    "nodes": parse_int(row["nodes"]),
                    "ppn": parse_int(row["ppn"]),
                    "threads": parse_int(row["threads"]),
                    "mpi_ranks": parse_int(row["mpi_ranks"]),
                    "total_cores": parse_int(row["total_cores"]),
                    "unknowns_per_core": parse_float(row["unknowns_per_core"]),
                    "matrix_type": row["matrix_type"] or "",
                    "runtime_seconds": parse_float(row["runtime_seconds"]),
                }
            )
    return rows


def aggregate_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[float]] = defaultdict(list)
    metadata: dict[tuple[object, ...], dict[str, object]] = {}

    for row in rows:
        key = tuple(row[column] for column in GROUP_COLUMNS)
        grouped[key].append(float(row["runtime_seconds"]))
        metadata[key] = {column: row[column] for column in GROUP_COLUMNS}

    baseline_by_scale: dict[str, float] = {}
    for key, runtimes in grouped.items():
        row = metadata[key]
        if (
            int(row["nodes"]) == 1
            and int(row["ppn"]) == 1
            and int(row["threads"]) == 1
            and int(row["total_cores"]) == 1
        ):
            baseline_by_scale[str(row["scale"])] = statistics.mean(runtimes)

    aggregated: list[dict[str, object]] = []
    for key, runtimes in grouped.items():
        row = dict(metadata[key])
        runtime_mean = statistics.mean(runtimes)
        runtime_std = statistics.stdev(runtimes) if len(runtimes) > 1 else math.nan
        baseline = baseline_by_scale[str(row["scale"])]
        speedup = baseline / runtime_mean
        efficiency = speedup / int(row["total_cores"])
        row.update(
            {
                "runtime_mean_s": runtime_mean,
                "runtime_std_s": runtime_std,
                "runtime_min_s": min(runtimes),
                "runtime_max_s": max(runtimes),
                "speedup": speedup,
                "efficiency": efficiency,
                "cu": int(row["nodes"]) * runtime_mean / 3600,
                "n_runs": len(runtimes),
            }
        )
        aggregated.append(row)

    scale_rank = {scale: index for index, scale in enumerate(SCALE_ORDER)}
    return sorted(
        aggregated,
        key=lambda row: (
            scale_rank.get(str(row["scale"]), 999),
            int(row["total_cores"]),
            int(row["nodes"]),
            int(row["ppn"]),
            int(row["threads"]),
            int(row["mpi_ranks"]),
        ),
    )


def fmt_int(value: object) -> str:
    return f"{int(value):,}"


def fmt_number(value: object, digits: int = 2) -> str:
    number = float(value)
    if math.isnan(number):
        return "-"
    return f"{number:,.{digits}f}"


def fmt_runtime(value: object) -> str:
    number = float(value)
    if math.isnan(number):
        return "-"
    return f"{number:,.2f}"


def fmt_efficiency(value: object) -> str:
    return f"{float(value) * 100:.1f}%"


def fmt_cu(value: object) -> str:
    return f"{float(value):.4f}"


def problem_size_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: dict[str, dict[str, object]] = {}
    for row in rows:
        scale = str(row["scale"])
        seen.setdefault(
            scale,
            {
                "scale": scale,
                "m": row["m"],
                "n": row["n"],
                "unknowns": row["unknowns"],
            },
        )
    return [seen[scale] for scale in SCALE_ORDER if scale in seen]


def markdown_table(headers: list[str], body: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return lines


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    lines: list[str] = [
        "# Table 1: Runtime Scaling Tables by Problem Size",
        "",
        "Source data: `runtime_results.csv`.",
        "",
        "Rows are aggregated from raw runs using the grouping fields `scale`, `m`, `n`, `unknowns`, `nodes`, `ppn`, `threads`, `mpi_ranks`, `total_cores`, `unknowns_per_core`, and `matrix_type`.",
        "",
        "`speedup = baseline runtime / runtime mean`, where the baseline is the same problem size with `nodes=1`, `ppn=1`, `threads=1`, and `total_cores=1`.",
        "",
        "`efficiency = speedup / total cores`. Values above 100% can occur in measured data as superlinear speedup or measurement/baseline effects; they are not capped.",
        "",
        "`CUs = nodes × runtime mean / 3600`, using the ARCHER2-style accounting assumption that 1 CU is 1 node for 1 hour, regardless of whether 1 core or 128 cores are used.",
        "",
        "## Problem Size Overview",
        "",
    ]

    overview_body = [
        [str(row["scale"]), fmt_int(row["m"]), fmt_int(row["n"]), fmt_int(row["unknowns"])]
        for row in problem_size_rows(rows)
    ]
    lines.extend(markdown_table(["scale", "m", "n", "unknowns"], overview_body))

    table_headers = [
        "total cores",
        "nodes",
        "ppn",
        "MPI ranks",
        "threads",
        "unknowns/core",
        "runtime mean/s",
        "speedup",
        "efficiency",
        "CUs",
    ]

    for scale in SCALE_ORDER:
        scale_rows = [row for row in rows if row["scale"] == scale]
        if not scale_rows:
            continue
        first = scale_rows[0]
        table_label = TABLE_LABELS[scale]
        lines.extend(
            [
                "",
                f"## {table_label}. Runtime scaling for {scale} problem size",
                "",
                f"scale: `{scale}`",
                "",
                f"problem size: {fmt_int(first['m'])} × {fmt_int(first['n'])}",
                "",
                f"unknowns: {fmt_int(first['unknowns'])}",
                "",
            ]
        )
        body = []
        for row in scale_rows:
            body.append(
                [
                    fmt_int(row["total_cores"]),
                    fmt_int(row["nodes"]),
                    fmt_int(row["ppn"]),
                    fmt_int(row["mpi_ranks"]),
                    fmt_int(row["threads"]),
                    fmt_int(round(float(row["unknowns_per_core"]))),
                    fmt_runtime(row["runtime_mean_s"]),
                    fmt_number(row["speedup"], 2),
                    fmt_efficiency(row["efficiency"]),
                    fmt_cu(row["cu"]),
                ]
            )
        lines.extend(markdown_table(table_headers, body))

    path.write_text("\n".join(lines) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = GROUP_COLUMNS + [
        "runtime_mean_s",
        "runtime_std_s",
        "runtime_min_s",
        "runtime_max_s",
        "speedup",
        "efficiency",
        "cu",
        "n_runs",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = read_rows(RUNTIME_RESULTS)
    aggregated = aggregate_rows(rows)
    write_csv(OUTPUT_CSV, aggregated)
    write_markdown(OUTPUT_MD, aggregated)
    print(f"read rows: {len(rows)}")
    print(f"aggregated rows: {len(aggregated)}")
    print(f"wrote CSV: {OUTPUT_CSV}")
    print(f"wrote Markdown: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
