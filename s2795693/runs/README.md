# Experimental Runs

This directory contains **raw outputs from benchmark experiments**.

## Contents

Typical contents include:

- raw timing logs
- PETSc output
- intermediate result files

## Purpose

This directory represents the **raw data stage** of the workflow:

scripts/ → runs/ → analysis_output/

It is used to:

- store unprocessed experimental results
- provide traceability for reported performance data
- allow re-analysis without rerunning experiments

## Notes

- Files here are not cleaned or processed
- Naming should reflect:
  - configuration (e.g. ranks × threads)
  - node count
  - experiment type


## Reproducibility

All runs in this directory should be reproducible using scripts in `scripts/`.