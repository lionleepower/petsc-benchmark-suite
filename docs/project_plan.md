# Project Plan – PETSc Benchmark and Optimisation Suite

## 1. Project Overview

This project aims to build a reproducible benchmarking and performance analysis framework for PETSc-based solver workloads on modern HPC systems.

The main objective is to investigate how solver performance varies under different parallel configurations, including:

- MPI-only execution
- Hybrid MPI + OpenMP execution
- Different compiler environments
- Different runtime configurations

The project is designed as an HPC engineering portfolio project demonstrating:

- experiment design for parallel applications
- performance benchmarking on supercomputing systems
- scaling analysis and interpretation
- reproducible scientific computing workflows

Primary evaluation platform: **ARCHER2 (HPE Cray EX)**.

---

## 2. Target Workload

The initial benchmark workload will be the PETSc example application:

`ex2`

This example represents a simplified PDE solver workflow and provides a convenient baseline for exploring parallel scaling behaviour.

Reasons for choosing this workload:

- lightweight and reproducible
- commonly used in PETSc demonstrations
- suitable for controlled scaling experiments

Future extensions may include additional PETSc examples.

---

## 3. Experiment Design

The benchmarking experiments are divided into four main categories.

### 3.1 Strong Scaling

Objective:

Evaluate how runtime changes as the number of MPI processes increases while keeping the problem size fixed.

Typical process counts:

- 1
- 2
- 4
- 8
- 16
- 32
- 64

Metrics collected:

- total runtime
- speedup
- parallel efficiency

Outputs:

- runtime vs process count
- speedup plot
- efficiency plot

---

### 3.2 Hybrid MPI + OpenMP Experiments

Objective:

Compare pure MPI execution with hybrid MPI + OpenMP execution under a fixed total core count.

Typical configurations:

| MPI Ranks | OpenMP Threads |
|----------|---------------|
| 128 | 1 |
| 64 | 2 |
| 32 | 4 |
| 16 | 8 |

Metrics collected:

- runtime
- scaling behaviour
- overhead from thread management

Outputs:

- hybrid runtime comparison
- discussion of performance trade-offs

---

### 3.3 Compiler Environment Comparison

Objective:

Evaluate the performance impact of different compiler environments.

Candidate environments:

- `PrgEnv-gnu`
- `PrgEnv-cray`

Metrics collected:

- runtime differences
- scalability differences

Outputs:

- runtime comparison plots
- discussion of compiler effects

---

### 3.4 Profiling and Bottleneck Analysis

Objective:

Identify performance bottlenecks in the benchmark application.

Potential tools:

- CrayPat
- Score-P
- perf

Focus areas:

- communication overhead
- load imbalance
- memory bandwidth utilisation
- threading inefficiencies

Outputs:

- profiling summaries
- interpretation of performance bottlenecks

---

## 4. Benchmark Workflow

The experiment workflow follows a reproducible pipeline:

1. Prepare the HPC environment
2. Submit Slurm benchmark jobs
3. Collect raw runtime outputs
4. Convert outputs to structured CSV datasets
5. Generate scaling plots
6. Interpret performance results

The automation scripts are located in the `scripts/` directory.

---

## 5. Repository Organisation

The project repository is structured to separate experiments, analysis, and results.

Main directories:

- `slurm/`  
  HPC job submission scripts

- `scripts/`  
  Result parsing and plotting utilities

- `results/raw/`  
  Raw benchmark outputs

- `results/processed/`  
  Structured datasets extracted from logs

- `results/plots/`  
  Generated figures

- `analysis/`  
  Additional analysis notebooks

- `docs/`  
  Project documentation and experiment logs

---

## 6. Development Milestones

The project development is divided into several milestones.

### Milestone 1 – Repository Setup

Tasks:

- create repository structure
- write README
- organise benchmark scripts
- establish experiment log

---

### Milestone 2 – Baseline Benchmark

Tasks:

- run initial PETSc benchmark
- collect runtime results
- verify experiment reproducibility

Outputs:

- baseline runtime dataset

---

### Milestone 3 – Strong Scaling Study

Tasks:

- run scaling experiments for increasing MPI process counts
- generate runtime and speedup plots

Outputs:

- strong scaling analysis

---

### Milestone 4 – Hybrid Parallel Experiments

Tasks:

- evaluate MPI + OpenMP configurations
- compare hybrid performance against pure MPI

Outputs:

- hybrid scaling plots

---

### Milestone 5 – Profiling Analysis

Tasks:

- run profiling tools
- identify performance bottlenecks

Outputs:

- profiling summary

---

### Milestone 6 – Final Repository Refinement

Tasks:

- improve documentation
- refine plotting scripts
- summarise experimental findings

Outputs:

- complete reproducible benchmark repository

---

## 7. Expected Outcomes

At the completion of the project, the repository will provide:

- a reproducible PETSc benchmark workflow
- scaling performance analysis
- hybrid parallel performance comparison
- profiling-based performance insights

The repository will serve as a demonstration of practical HPC engineering skills.

---

## 8. Future Extensions

Possible future improvements include:

- multi-node scaling experiments
- roofline-style performance analysis
- benchmarking additional PETSc workloads
- GPU-enabled PETSc experiments