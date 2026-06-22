# Experimental Environment and Configuration

This document summarises the software environment, PETSc configuration, and benchmark setup used in the preliminary experiments for this project.

## Platform

All preliminary experiments were carried out on **ARCHER2**, the UK national supercomputing service.

ARCHER2 consists of 5,860 compute nodes with a total of 750,080 CPU cores.  
Each standard node contains:

- 2 × AMD EPYC 7742 processors
- 64 cores per processor
- 128 cores per node
- 2.25 GHz clock frequency

The project focuses primarily on node-level and small-scale multi-node CPU benchmarking.

## Software Environment

The main software environment used for the preliminary study was:

- `PrgEnv-gnu/8.4.0`
- `gcc/11.2.0`
- `cray-mpich/8.1.27`

The system environment also includes architecture-specific optimisation support such as:

- `craype-x86-rome`
- `cray-libsci`

Compilation was performed using the Cray compiler wrappers:

- `cc`
- `CC`
- `ftn`

with optimisation enabled using:

- `-O3`

and debugging disabled.

## PETSc Configuration

The experiments used **PETSc 3.24.4** with OpenMP support enabled.

Key PETSc configuration options:

- `--with-openmp=1`
- `--with-openmp-kernels=1`

This setup enables OpenMP parallelism in supported PETSc kernels while remaining compatible with MPI-based distributed-memory execution.

## Benchmark Application

The benchmark application is based on the PETSc example:

- `src/ksp/ksp/tutorials/ex2.c`

This example constructs a sparse linear system arising from a 2D five-point finite difference discretisation and solves it using a Krylov subspace (KSP) solver with PETSc parallel matrix and vector interfaces.

The preliminary experiments used a problem size of:

- `800 × 800`

corresponding to:

- `640,000` unknowns

This relatively small problem size was chosen for initial validation and exploratory benchmarking. Larger problem sizes may be used in later stages of the dissertation work.

## Execution Modes

Two execution modes were considered.

### MPI-only mode

In MPI-only mode, scaling is evaluated by increasing the number of MPI ranks, for example:

- 1
- 2
- 4
- 8
- 16
- 32
- 64
- 128

### Hybrid MPI+OpenMP mode

In hybrid mode, combinations of MPI ranks and OpenMP threads are evaluated.

For the single-node study, configurations were chosen such that:


- ranks × threads = total cores
- total cores ≤ 128