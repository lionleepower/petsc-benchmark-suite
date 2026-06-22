# Analysis Output

This directory contains processed results and visualisations derived from raw experimental runs.

## Contents

Typical files include:

- data (processed CSV files, cleaned / aggregated results)
- plots (e.g. speedup curves, runtime comparisons)
- map(Profilling data)

## Purpose

This directory represents the **analysis stage** of the workflow:

runs/ → analysis_output/

Raw data from `runs/` is processed into:

- meaningful performance metrics
- visualisations for interpretation
- figures used in the report

## Notes

- Data here should be reproducible from `runs/` using scripts or notebooks (if available)
- Figures should correspond clearly to those referenced in the report