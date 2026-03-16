#!/usr/bin/env python3
from pathlib import Path
import argparse
import csv
import re
from typing import Optional


FILENAME_RE = re.compile(
    r"ex2_(?P<arch>.+?)_r(?P<ranks>\d+)_t(?P<threads>\d+)_p(?P<total>\d+)_m(?P<m>\d+)_n(?P<n>\d+)_rep(?P<rep>\d+)\.log$"
)

TIME_RE = re.compile(r"Time \(sec\):\s+([0-9.eE+-]+)")
NORM_ITER_RE = re.compile(r"Norm of error\s+([0-9.eE+-]+)\s+iterations\s+(\d+)")
OMP_RE = re.compile(r"Using\s+(\d+)\s+OpenMP threads")
HOST_RE = re.compile(r"named\s+(\S+)\s+with\s+\d+\s+processes")
JOBID_RE = re.compile(r"JobID[=\s:]+(\d+)")


def parse_logfile(log_path: Path) -> dict:
    m = FILENAME_RE.match(log_path.name)
    if not m:
        raise ValueError(f"Filename does not match expected pattern: {log_path.name}")

    meta = m.groupdict()
    ranks = int(meta["ranks"])
    threads = int(meta["threads"])
    total = int(meta["total"])
    rep = int(meta["rep"])
    msize = int(meta["m"])
    nsize = int(meta["n"])
    arch = meta["arch"]

    if ranks * threads != total:
        raise ValueError(
            f"Inconsistent filename metadata in {log_path.name}: "
            f"ranks*threads={ranks*threads}, but p={total}"
        )

    text = log_path.read_text(encoding="utf-8", errors="ignore")

    time_match = TIME_RE.search(text)
    norm_match = NORM_ITER_RE.search(text)
    omp_match = OMP_RE.search(text)
    host_match = HOST_RE.search(text)
    jobid_match = JOBID_RE.search(text)

    if not time_match:
        raise ValueError(f"Could not parse Time (sec) from {log_path}")

    time_sec = float(time_match.group(1))

    error_norm: Optional[float] = None
    iterations: Optional[int] = None
    if norm_match:
        error_norm = float(norm_match.group(1))
        iterations = int(norm_match.group(2))

    omp_threads_reported: Optional[int] = None
    if omp_match:
        omp_threads_reported = int(omp_match.group(1))

    nodelist = host_match.group(1) if host_match else ""
    jobid = jobid_match.group(1) if jobid_match else ""

    return {
        "timestamp": "",
        "jobid": jobid,
        "nodelist": nodelist,
        "nodes": 1,
        "ranks": ranks,
        "threads": threads,
        "total_cores": total,
        "rep": rep,
        "time_sec": time_sec,
        "iterations": iterations if iterations is not None else "",
        "error_norm": error_norm if error_norm is not None else "",
        "logfile": str(log_path),
        "arch": arch,
        "m": msize,
        "n": nsize,
        "omp_threads_reported": omp_threads_reported if omp_threads_reported is not None else "",
    }


def expected_grid(max_cores: int = 128):
    pairs = []
    ranks_list = [1, 2, 4, 8, 16, 32, 64, 128]
    threads_list = [1, 2, 4, 8, 16, 32, 64, 128]
    for r in ranks_list:
        for t in threads_list:
            if r * t <= max_cores:
                pairs.append((r, t, r * t))
    return pairs


def main():
    ap = argparse.ArgumentParser(description="Rebuild PETSc ex2 hybrid CSV from log files.")
    ap.add_argument("--logdir", required=True, help="Directory containing rank_thread_grid log files")
    ap.add_argument("--outcsv", required=True, help="Output CSV path")
    ap.add_argument("--report", default=None, help="Optional text report path")
    args = ap.parse_args()

    logdir = Path(args.logdir)
    outcsv = Path(args.outcsv)
    report_path = Path(args.report) if args.report else outcsv.with_suffix(".report.txt")

    logs = sorted(logdir.glob("ex2_*.log"))
    if not logs:
        raise SystemExit(f"No log files found in {logdir}")

    rows = []
    errors = []

    for log in logs:
        try:
            row = parse_logfile(log)
            rows.append(row)
        except Exception as e:
            errors.append(f"{log.name}: {e}")

    rows.sort(key=lambda x: (x["total_cores"], x["ranks"], x["threads"], x["rep"]))

    outcsv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "timestamp", "jobid", "nodelist", "nodes",
        "ranks", "threads", "total_cores", "rep",
        "time_sec", "iterations", "error_norm", "logfile"
    ]

    with outcsv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

    # completeness check
    seen = {}
    for row in rows:
        key = (row["ranks"], row["threads"], row["total_cores"])
        seen.setdefault(key, 0)
        seen[key] += 1

    expected = expected_grid(128)
    missing_cfgs = [cfg for cfg in expected if cfg not in seen]

    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"logdir: {logdir}\n")
        f.write(f"outcsv: {outcsv}\n")
        f.write(f"parsed_rows: {len(rows)}\n")
        f.write(f"parse_errors: {len(errors)}\n\n")

        if errors:
            f.write("Parse errors:\n")
            for err in errors:
                f.write(f"  {err}\n")
            f.write("\n")

        f.write("Observed configurations:\n")
        for key in sorted(seen):
            f.write(f"  r={key[0]:>3} t={key[1]:>3} p={key[2]:>3} reps={seen[key]}\n")
        f.write("\n")

        if missing_cfgs:
            f.write("Missing expected configurations (for powers-of-two grid with p<=128):\n")
            for r, t, p in missing_cfgs:
                f.write(f"  r={r:>3} t={t:>3} p={p:>3}\n")
        else:
            f.write("No missing configurations in expected grid.\n")

    print(f"Wrote CSV: {outcsv}")
    print(f"Wrote report: {report_path}")
    print(f"Parsed rows: {len(rows)}")
    if errors:
        print(f"Parse errors: {len(errors)}")


if __name__ == "__main__":
    main()