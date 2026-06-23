# Runtime Scaling Summary

This analysis uses `runtime_results.csv` and plots:

```text
total cores = nodes x ppn x threads
```

Only `T = 1, 2, 4, 8` are included in the figures. Repeated runs with the same `(scale, total_cores, threads)` are aggregated by median runtime, with mean/min/max/count saved separately.

## Figures

- Linear y-axis: `runtime_scaling.svg` / `runtime_scaling.png`
- Log y-axis: `runtime_scaling_logy.svg` / `runtime_scaling_logy.png`
- Aggregated data: `runtime_scaling_aggregated.csv`
- Reproducible script: `plot_runtime_scaling.py`

For the report, the log-y version is usually easier to read because the runtime range is large within each problem size.

## Fastest Observed Configuration

| Problem size | Fastest total cores | Threads | Median runtime (s) | Speedup vs 1 core |
| --- | ---: | ---: | ---: | ---: |
| 1.00M | 128 | 1 | 3.855 | 64.0x |
| 5.02M | 128 | 1 | 64.02 | 29.3x |
| 9.99M | 128 | 1 | 136.5 | 27.2x |
| 20.25M | 128 | 1 | 340.45 | 22.2x |
| 40.96M | 128 | 1 | 846.9 | 18.2x |

## Main Observations

- Runtime generally decreases as total cores increase, especially from 1 to 128 cores.
- `T=1` is the strongest overall configuration at high core counts. It is the fastest at 128 total cores for all five problem sizes.
- Hybrid runs can be competitive at intermediate core counts. For example, `T=4` is best around 16-32 cores for several larger cases.
- `T=8` is usually less attractive than `T=1`, `T=2`, or `T=4`, especially at higher core counts.
- For the 1M case, scaling is less smooth: small problems show more visible parallel overhead and irregularity.
- Larger problems show clearer scaling trends, but the speedup versus 1 core is still far below ideal 128x scaling, so communication/synchronisation overhead remains important.
