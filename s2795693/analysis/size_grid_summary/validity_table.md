# Validity Table

Criterion: `10,000 < N/C < 1,000,000`, where `N = m * n` and `C = nodes * ppn * threads`. Rows are organised problem-size-first, then total core count.

| scale | unknowns | C=1 | C=2 | C=4 | C=8 | C=16 | C=32 | C=64 | C=128 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| small | 1,000,000 | 1,000,000 too_large_per_core | 500,000 valid | 250,000 valid | 125,000 valid | 62,500 valid | 31,250 valid | 15,625 valid | 7,812 too_small_per_core |
| medium-small | 5,017,600 | 5,017,600 too_large_per_core | 2,508,800 too_large_per_core | 1,254,400 too_large_per_core | 627,200 valid | 313,600 valid | 156,800 valid | 78,400 valid | 39,200 valid |
| medium | 9,985,600 | 9,985,600 too_large_per_core | 4,992,800 too_large_per_core | 2,496,400 too_large_per_core | 1,248,200 too_large_per_core | 624,100 valid | 312,050 valid | 156,025 valid | 78,012 valid |
| large | 20,250,000 | 20,250,000 too_large_per_core | 10,125,000 too_large_per_core | 5,062,500 too_large_per_core | 2,531,250 too_large_per_core | 1,265,625 too_large_per_core | 632,812 valid | 316,406 valid | 158,203 valid |
| very-large | 40,960,000 | 40,960,000 too_large_per_core | 20,480,000 too_large_per_core | 10,240,000 too_large_per_core | 5,120,000 too_large_per_core | 2,560,000 too_large_per_core | 1,280,000 too_large_per_core | 640,000 valid | 320,000 valid |

This layout makes the intended top-left-to-down workflow visible: begin with smaller `N` and lower `C`, then extend only into cells whose `N/C` remains sensible and whose wall-clock time is affordable.
