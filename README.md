# PETSc Benchmark and Optimisation Suite

A reproducible HPC benchmarking project for evaluating the performance of PETSc-based solver workloads under different parallel configurations on modern supercomputing systems.

## Overview

This repository contains benchmarking, analysis, and automation workflows for studying the performance of PETSc example workloads under:

- MPI-only execution
- Hybrid MPI + OpenMP execution
- Different compiler environments
- Different runtime configurations

The project is designed as a portfolio-grade HPC engineering repository, with an emphasis on:

- reproducible benchmarking
- scaling analysis
- performance profiling
- optimisation methodology
- clear presentation of results

## Objectives

The main goals of this project are:

1. Evaluate the strong scaling behaviour of PETSc workloads
2. Compare MPI-only and hybrid MPI+OpenMP configurations
3. Investigate the effect of compiler and runtime choices
4. Identify bottlenecks using profiling tools
5. Build a reproducible analysis pipeline for HPC experiments

## Technical Stack

- PETSc
- MPI
- OpenMP
- Bash
- Python
- Slurm
- Matplotlib / pandas
- ARCHER2

## Target Workload

The current benchmark focus is PETSc example workloads such as `ex2`, used as a compact but realistic scientific computing test case.

The benchmark pipeline includes:

- job submission scripts
- parameter sweeps
- runtime collection
- CSV result generation
- scaling plot generation
- profiling summaries

## Repository Structure

```text
petsc-benchmark-suite/
├── README.md
├── .gitignore
├── LICENSE
├── docs/
│   ├── project_plan.md
│   ├── experiment_log.md
│   ├── methodology.md
│   └── profiling_notes.md
├── configs/
│   ├── strong_scaling.yaml
│   ├── hybrid_scaling.yaml
│   └── compiler_compare.yaml
├── scripts/
│   ├── collect_results.py
│   ├── plot_scaling.py
│   ├── plot_hybrid.py
│   ├── summarise_results.py
│   └── utils.py
├── slurm/
│   ├── run_strong_scaling.slurm
│   ├── run_hybrid_scaling.slurm
│   ├── run_compiler_compare.slurm
│   └── run_profile.slurm
├── analysis/
│   ├── scaling_analysis.ipynb
│   └── hybrid_analysis.ipynb
├── results/
│   ├── raw/
│   │   ├── strong_scaling/
│   │   ├── hybrid/
│   │   └── compiler_compare/
│   ├── processed/
│   │   ├── strong_scaling.csv
│   │   ├── hybrid.csv
│   │   └── compiler_compare.csv
│   └── plots/
│       ├── strong_scaling.png
│       ├── speedup.png
│       ├── efficiency.png
│       ├── hybrid_runtime.png
│       └── compiler_comparison.png
├── profiles/
│   ├── raw/
│   └── summaries/
│       └── profile_summary.md
└── src/
    ├── README.md
    └── run_ex2.sh
```

## Directory Details

- **docs/**  
  Project notes, methodology notes, experiment design, and interpretation summaries.

- **configs/**  
  Benchmark parameter files and configuration templates.

- **scripts/**  
  Helper scripts for parsing output, collecting results, plotting figures, and automating experiment workflows.

- **slurm/**  
  Batch job scripts for ARCHER2 runs.

- **analysis/**  
  Analysis scripts and notebooks for post-processing benchmark results.

- **results/**  
  Benchmark outputs, processed CSV files, and final plots.

- **profiles/**  
  Profiling outputs and summary reports.

- **src/**  
  Source-related helpers or workload launch scripts.


## Experimental Platform

Primary evaluation platform:

- ARCHER2
- HPE Cray EX
- Slurm-based job scheduling

Compiler environments explored in this project may include:

- PrgEnv-gnu
- PrgEnv-cray

## Experiment Categories
### 1. Strong Scaling

Test the runtime behaviour as the number of MPI ranks increases.

Typical process counts:
- 1
- 2
- 4
- 8
- 16
- 32
- 64
- 128

Main outputs:

- runtime vs process count
- speedup
- parallel efficiency

### 2. Hybrid MPI + OpenMP

Compare pure MPI and hybrid execution under a fixed total core budget.

Typical configurations:
- MPI=[1, 2, 4 , 8, 16, 32, 64 ,128] 
- OMP=[1, 2, 4, 8, 16 , 32, 64, 128]


Main outputs:
- runtime comparison
- hybrid scaling behaviour
- discussion of overheads and trade-offs

### 3. Compiler / Runtime Comparison

Evaluate performance differences under alternative compiler environments and runtime settings.

Examples:

- PrgEnv-gnu vs PrgEnv-cray
- different thread placement policies
- different OpenMP affinity settings

### 4. Profiling and Bottleneck Analysis

Use profiling tools to identify major performance bottlenecks such as:

- communication overhead
- load imbalance
- memory bandwidth pressure
- thread-level inefficiency

## Reproducibility

This repository is organised to make experiments reproducible.

General workflow:

- prepare the environment
- submit Slurm benchmark jobs
- collect raw outputs
- convert outputs into CSV format
- generate plots
- summarise performance observations

## Example Workflow
### Submit a benchmark job

```bash
sbatch slurm/run_strong_scaling.slurm
```
### Process results
```bash
python scripts/collect_results.py
```
### Generate plots
```bash
python scripts/plot_scaling.py
```

## Current Status

This project is under active development.

### Current completed components may include:

- baseline benchmark setup
- initial strong scaling runs
- runtime plot generation
- first-stage MPI vs hybrid comparisons

## Planned next steps:

- extend strong scaling dataset

- add hybrid experiment automation

- add profiling results

- compare compiler environments

- improve analysis summaries

## Example Outputs

Planned output figures include:

strong scaling runtime plot

speedup plot

efficiency plot

hybrid runtime comparison

compiler comparison plot

## Key Skills Demonstrated

This repository is intended to demonstrate practical HPC engineering skills, including:

MPI/OpenMP experiment design

PETSc-based benchmarking

Slurm workflow automation

performance analysis and interpretation

reproducible scientific computing practice

technical documentation for HPC projects

## Future Extensions

Potential future extensions include:

multi-node experiments

roofline-style interpretation

additional PETSc workloads

automated benchmarking dashboard

support for GPU-enabled workflows

## Author:
Leyan Li

MSc High Performance Computing with Data Science
The University of Edinburgh