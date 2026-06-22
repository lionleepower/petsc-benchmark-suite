# 1M Case Summary

The 1M case corresponds to `small`, with `m = 1000`, `n = 1000`, and `N = 1,000,000` unknowns.

- Fastest 1M runtime: 3.844 seconds at C=128 total cores, ppn=128, threads=1, job 13997004.
- Slowest 1M runtime: 248.0 seconds at C=1 total cores, ppn=1, threads=1, job 13997004.
- Matrix type: not recorded in the available CSV outputs.
- Memory usage: not recorded in the available CSV outputs.
- Failed or missing 1M runs from the script's 36 rank/thread combinations: none found.

## Runtime by Total Core Count

| total cores C | runs | fastest s | median s | slowest s | N/C | validity |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 2 | 245.7 | 246.8 | 248.0 | 1,000,000 | too_large_per_core |
| 2 | 4 | 83.55 | 156.8 | 231.4 | 500,000 | valid |
| 4 | 6 | 48.91 | 78.84 | 230.5 | 250,000 | valid |
| 8 | 8 | 43.32 | 65.98 | 226.4 | 125,000 | valid |
| 16 | 9 | 27.10 | 70.22 | 215.4 | 62,500 | valid |
| 32 | 10 | 23.02 | 29.80 | 216.5 | 31,250 | valid |
| 64 | 11 | 8.107 | 16.55 | 195.6 | 15,625 | valid |
| 128 | 12 | 3.844 | 10.70 | 208.4 | 7,812 | too_small_per_core |

## Runtime by Matrix Type

The matrix type was not recorded by `run_ex2_size_grid.sbatch`, and the local `runs/size_grid` directory does not contain PETSc log files from which it could be recovered.

## Supervisor Email Paragraph

For the 1M unknown case (`1000 x 1000`), I found 62 completed timing rows across the one-node rank/thread grid. The fastest recorded runtime was 3.844 seconds at 128 total cores, while the slowest was 248.0 seconds at 1 total core. Aggregated by total core count, the best runtime improved from 245.7 seconds at C=1 to 3.844 seconds at C=128, although the C=128 case has `N/C = 7,812.5`, which falls below the suggested lower bound of 10,000 unknowns per core.
