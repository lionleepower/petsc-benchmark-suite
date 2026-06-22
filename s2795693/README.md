# Benchmarking the PETSc OpenMP Backend

This repository studies how PETSc's OpenMP backend behaves relative to MPI-only execution, with ARCHER2 as the main target platform and a local Linux or WSL environment as a learning and smoke-test platform.

The benchmark application is based on PETSc's `src/ksp/ksp/tutorials/ex2.c`, a 2D five-point finite-difference linear solver example. In this repository, the original reference source is kept separately as [`resources/ex2`](/home/leyan/leyan/s2795693/resources/ex2:1).

## Repository Layout

- `README.md`: project entry point and setup notes
- `resources/`: reference source material, including the PETSc `ex2`-style example
- `scripts/`: ARCHER2-oriented environment and Slurm job scripts
- `runs/`: raw benchmark logs
- `analysis_output/`: processed results, plots, and summaries
- `PP_report/`: dissertation preparation report and figures
- `meetings/`: project notes and supervision records

## Learning Goals

This repository can support two different workflows:

1. Local learning workflow: understand PETSc, MPI, OpenMP, and the `ex2` problem on a small machine such as Ubuntu or WSL.
2. HPC reproduction workflow: rebuild PETSc with the required options and run benchmark sweeps on ARCHER2 or a similar Slurm cluster.

The local workflow is for correctness, API familiarity, and small runs. The HPC workflow is for performance experiments and reproducible benchmark data.

## Learning Preferences

For ongoing script-learning support in this repository:

- Prefer explanations in Chinese, while preserving key English technical terms such as `parameter expansion`, `array`, `field separator`, `Slurm`, and `OpenMP`.
- When the learner asks Bash or Slurm syntax questions, continue appending concise answers and examples to [`tutorial/BASH_QUESTION_LOG.md`](/home/leyan/leyan/jobSkill/petsc-benchmark-suite/s2795693/tutorial/BASH_QUESTION_LOG.md:1) so it becomes a cumulative reference.
- Keep explanations learner-friendly and connect syntax back to the actual repository scripts whenever possible.

## Environment Modes

### Local WSL or Linux Learning Environment

Use this mode when you want to:

- inspect and understand the `ex2` code
- confirm that a PETSc installation works
- run small single-process or small MPI tests
- practice compile and run commands before touching Slurm

Typical requirements:

- `gcc`, `g++`, `make`
- `mpicc`, `mpirun`
- a PETSc build or installation visible through `PETSC_DIR` and usually `PETSC_ARCH`
- optional: `cmake`, `git`, `python3`

### ARCHER2 or Another HPC Cluster

Use this mode when you want to:

- rebuild PETSc with cluster compiler wrappers
- test MPI-only and MPI+OpenMP configurations
- run `sbatch` scripts in `scripts/`
- collect timing data for scaling and benchmark analysis

Typical requirements:

- Slurm commands such as `sbatch`, `squeue`, `srun`
- compiler and MPI modules supplied by the cluster
- PETSc configured with OpenMP support
- correct project/account settings in the job scripts

Do not try to install ARCHER2 modules locally. Cluster module names such as `PrgEnv-gnu` and `cray-mpich` are cluster-specific and should only be loaded on the target system.

## Dependency Checklist

### Required for Local Learning

- C compiler: `gcc`
- MPI compiler wrapper: `mpicc`
- MPI launcher: `mpirun`
- PETSc headers and libraries
- OpenMP-capable compiler support

### Required for HPC Reproduction

- PETSc source tree or installation on the cluster
- Slurm
- cluster MPI implementation
- compiler wrappers used when PETSc was configured

### Optional but Helpful

- `g++`
- `cmake`
- `git`
- `python3`
- profiling or analysis tools provided by the cluster

## Quick Environment Checks

Run these commands before attempting to build or run anything:

```bash
pwd
echo "$HOME"
command -v gcc g++ make cmake mpicc mpirun srun pkg-config petsc-config git python3
printf "PETSC_DIR=%s\nPETSC_ARCH=%s\n" "$PETSC_DIR" "$PETSC_ARCH"
pkg-config --list-all | grep -i petsc || true
printf '' | gcc -fopenmp -dM -E - | grep OPENMP || true
```

What to look for:

- `gcc`, `make`, `mpicc`, and `mpirun` should resolve to real executables for local MPI work.
- `srun` may be missing on a local machine; that is normal outside a Slurm cluster.
- `petsc-config`, `pkg-config`, `PETSC_DIR`, or `PETSC_ARCH` should give you some way to locate PETSc. If all of them are empty, PETSc is probably not ready yet.
- The OpenMP check should print an `_OPENMP` macro if the compiler supports `-fopenmp`.

## PETSc Discovery

PETSc can appear in several different ways depending on how it was installed.

### Method 1: Environment Variables

```bash
echo "$PETSC_DIR"
echo "$PETSC_ARCH"
```

If PETSc was built from source, common usage is:

```bash
make PETSC_DIR="$PETSC_DIR" PETSC_ARCH="$PETSC_ARCH" ex2
```

### Method 2: `pkg-config`

```bash
pkg-config --cflags --libs petsc
```

If this succeeds, PETSc is likely installed in a system or user prefix rather than only kept as a source tree build.

### Method 3: `petsc-config`

```bash
petsc-config --prefix
```

Not every PETSc installation provides this helper.

### Method 4: Cluster Module or Existing Build Scripts

On ARCHER2-style systems, PETSc may be found indirectly through:

- loaded compiler and MPI modules
- a PETSc source directory under a project path
- `PETSC_DIR` and `PETSC_ARCH` exported inside job scripts

In this repository, the existing scripts assume PETSc lives outside the repository in a cluster filesystem path and is built before benchmark jobs are run.

## Build Guidance

### Local Learning Build

This repository does not currently contain a standalone local Makefile. The simplest local path is:

1. Ensure PETSc is already installed or built.
2. Use PETSc's own example build flow from the PETSc tutorial directory.
3. Start with small problem sizes.

If you have a PETSc source tree build:

```bash
cd "$PETSC_DIR/src/ksp/ksp/tutorials"
make PETSC_DIR="$PETSC_DIR" PETSC_ARCH="$PETSC_ARCH" ex2
```

If you instead have a packaged PETSc installation, the exact compile command may differ. In that case, first inspect:

```bash
pkg-config --cflags --libs petsc
```

Missing dependency checklist for a local machine:

- Missing `mpicc`: install an MPI implementation such as Open MPI or MPICH.
- Missing PETSc headers or libraries: install PETSc packages or build PETSc from source.
- Missing OpenMP support: use a compiler build with `-fopenmp` support.

Suggested install commands depend on your platform and are intentionally not run automatically here.

### HPC PETSc Build

The repository's current configuration notes point to a PETSc build with OpenMP enabled. The intended configure shape is:

```bash
cd "$PETSC_DIR"
./configure \
  --PETSC_ARCH="$PETSC_ARCH" \
  --with-debugging=0 \
  COPTFLAGS="-O3" CXXOPTFLAGS="-O3" FOPTFLAGS="-O3" \
  --with-cc=cc --with-cxx=CC --with-fc=ftn \
  --with-openmp=1 \
  --with-openmp-kernels=1 \
  --download-fblaslapack
make -j 8 all
```

This shape matches the intent of [`scripts/config.txt`](/home/leyan/leyan/s2795693/scripts/config.txt:1), although that file currently needs cleanup before it should be treated as authoritative.

## Minimal Run Examples

### Local Single-Process Run

After building `ex2` in a PETSc tutorial directory:

```bash
./ex2 -m 8 -n 7 -ksp_converged_reason
```

What this does:

- builds a small 2D five-point stencil problem
- solves `Ax = b`
- prints convergence information and the final error norm

### Local MPI Run

```bash
mpirun -n 2 ./ex2 -m 8 -n 7 -ksp_converged_reason
```

Use a small process count first. This is a correctness check, not a benchmark.

### Local OpenMP-Aware MPI Run

```bash
export OMP_NUM_THREADS=2
export OMP_PLACES=cores
export OMP_PROC_BIND=close
mpirun -n 2 ./ex2 -m 8 -n 7 -ksp_converged_reason
```

Whether this exercises PETSc's OpenMP backend meaningfully depends on how PETSc was configured.

### Slurm Run on a Cluster

The existing scripts are cluster-oriented examples, for example:

```bash
sbatch scripts/run_ex2_grid.sbatch
```

Before using them, check:

- the account code in `#SBATCH --account`
- the cluster filesystem path used for `PROJECT_ROOT`
- the `PETSC_DIR` and `PETSC_ARCH` values exported by the script

## Understanding Output

Typical useful outputs include:

- `Norm of error ... iterations ...`
- `-ksp_converged_reason`
- `-log_view`

Interpretation:

- `Norm of error`: how close the computed solution is to the constructed exact solution
- `iterations`: how many Krylov iterations were needed
- `-ksp_converged_reason`: why the solver stopped
- `-log_view`: PETSc timing and operation summary, useful for benchmark scripting

In this example, PETSc commonly builds the right-hand side from an exact solution vector of all ones, then solves the system and compares the computed answer to that known solution.

## Benchmark Reproduction Notes

The benchmark workflow in this repository is:

1. Build a PETSc configuration with the required MPI and OpenMP options.
2. Compile the `ex2` tutorial program from the PETSc tree.
3. Run a selected Slurm script from `scripts/`.
4. Store raw logs under `runs/`.
5. Process results into `analysis_output/`.

The current scripts focus on:

- MPI-only runs
- hybrid rank-thread sweeps
- fixed-total-core comparisons across 1, 2, and 4 nodes

They are suitable as reference material, but not yet as beginner-first teaching scripts. Later tutorial stages will introduce simpler local scripts first.

## Size-grid Benchmark Summary

Raw size-grid benchmark results are stored under `runs/size_grid/`. The current cleaned summaries are stored under `analysis/size_grid_summary/`.

The size-grid study is organised problem-size-first. For each problem size, the useful comparison is:

```text
problem size N -> total cores C -> N/C -> runtime
```

The supervisor's current problem-size criterion is:

```text
10,000 < N/C < 1,000,000
```

where `N = m * n` is the number of mathematical unknowns in the 2D `ex2` grid, and `C = nodes * ppn * threads` is the total core count.

The configured problem sizes are:

| scale | grid | unknowns |
| --- | ---: | ---: |
| small | 1000 x 1000 | 1,000,000 |
| medium-small | 2240 x 2240 | 5,017,600 |
| medium | 3160 x 3160 | 9,985,600 |
| large | 4500 x 4500 | 20,250,000 |
| very-large | 6400 x 6400 | 40,960,000 |

## Current Repository-Specific Notes

- Real repository root in the present environment: `/home/leyan/leyan/s2795693`
- Reference example source in this repository: [`resources/ex2`](/home/leyan/leyan/s2795693/resources/ex2:1)
- Existing benchmark scripts are HPC-first and assume PETSc exists outside the repository
- Some script documentation mentions files that are not currently present
- `scripts/config.txt` currently contains merge-conflict residue and should be treated cautiously

## Related Files

- [scripts/README.md](/home/leyan/leyan/s2795693/scripts/README.md:1): ARCHER2-oriented script overview
- [scripts/ENVIRONMENT.md](/home/leyan/leyan/s2795693/scripts/ENVIRONMENT.md:1): environment notes from the current project
- [runs/README.md](/home/leyan/leyan/s2795693/runs/README.md:1): raw run output notes
- [analysis_output/README.md](/home/leyan/leyan/s2795693/analysis_output/README.md:1): processed output notes

## Next Teaching Steps

The next recommended stage is to create a dedicated `tutorial/` directory that:

- explains the 2D Poisson-style model behind `ex2`
- maps every important mathematical expression to the source code
- introduces simpler teaching examples without modifying `resources/ex2`
- adds small, readable helper scripts for environment checks, local builds, local MPI runs, and later Slurm benchmarking
