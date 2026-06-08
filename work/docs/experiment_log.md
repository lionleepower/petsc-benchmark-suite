
# docs/experiment_log.md

```markdown
# Experiment Log – PETSc Benchmark Suite

This document records all benchmark experiments performed in this project.

Each entry summarises:

- experiment configuration
- runtime environment
- results
- observations

The goal is to ensure experiments remain **reproducible** and **traceable**.

---

# Experiment Entries

---

## Experiment 001 – Repository Initialisation

**Date**

2026-03-11

**Objective**

Initial setup of the benchmarking repository and experiment workflow.

**Platform**

Local environment (WSL)

**Actions**

- created repository structure
- wrote README
- created project plan
- prepared experiment log

**Results**

No benchmark results yet.

**Observations**

Repository structure is now ready for running the first benchmark experiments.


---
## Experiment 002 – Benchmark Scripts Added

Date
2026-03-11

Objective
Organise existing benchmark scripts into repository.

Actions
- added MPI benchmark Slurm scripts
- added ARCHER2 environment configuration
- prepared repository for scaling experiments

Observations
Scripts previously used for experiments are now integrated into the repository structure.

Next Steps
Run new scaling experiments using the organised workflow.

---

## Experiment 002 – Baseline PETSc Run

**Date**

YYYY-MM-DD

**Objective**

Verify that the PETSc benchmark (`ex2`) runs correctly on the HPC platform.

**Platform**

ARCHER2

**Environment**

```

module purge
module load PrgEnv-gnu
module load cray-mpich

````

**Execution Configuration**

| Parameter | Value |
|----------|------|
| MPI ranks | X |
| OpenMP threads | 1 |
| Nodes | X |
| Job scheduler | Slurm |

**Command**

```bash
srun ./ex2
````

**Results**

| Metric     | Value     |
| ---------- | --------- |
| Runtime    | X seconds |
| Iterations | X         |
| Converged  | Yes/No    |

**Observations**

Example:

* application runs successfully
* runtime appears stable
* suitable as baseline benchmark

**Next Steps**

Run scaling experiments with multiple MPI ranks.

---


## Experiment 003 – Strong Scaling Study

**Date**

YYYY-MM-DD

**Objective**

Evaluate strong scaling behaviour of the PETSc workload.

**Platform**

ARCHER2

**Environment**

```
PrgEnv-gnu
MPI
```

**Experiment Design**

Fixed problem size.

Process counts tested:

```
1
2
4
8
16
32
64
```

**Results**

| MPI Ranks | Runtime (s) |
| --------- | ----------- |
| 1         |             |
| 2         |             |
| 4         |             |
| 8         |             |
| 16        |             |
| 32        |             |
| 64        |             |

**Derived Metrics**

| MPI Ranks | Speedup | Efficiency |
| --------- | ------- | ---------- |
| 1         | 1.0     | 1.0        |
| 2         |         |            |
| 4         |         |            |
| 8         |         |            |
| 16        |         |            |
| 32        |         |            |
| 64        |         |            |

**Observations**

Example:

* scaling is good up to 16 ranks
* communication overhead increases after 32 ranks

**Next Steps**

Generate scaling plots.




---

## Experiment 004 – Hybrid MPI + OpenMP

**Date**

YYYY-MM-DD

**Objective**

Compare hybrid MPI+OpenMP configurations.

**Platform**

ARCHER2

**Configurations Tested**

| MPI | OMP |
| --- | --- |
| 128 | 1   |
| 64  | 2   |
| 32  | 4   |
| 16  | 8   |

**Results**

| MPI | OMP | Runtime |
| --- | --- | ------- |
| 128 | 1   |         |
| 64  | 2   |         |
| 32  | 4   |         |
| 16  | 8   |         |

**Observations**

Example:

* hybrid configurations reduce MPI communication overhead
* thread scaling depends on OpenMP affinity settings

**Next Steps**

Investigate thread placement options.




---

## Experiment 005 – Compiler Comparison

**Date**

YYYY-MM-DD

**Objective**

Evaluate performance differences across compiler environments.

**Compiler Environments**

```
PrgEnv-gnu
PrgEnv-cray
```

**Results**

| Compiler | Runtime |
| -------- | ------- |
| GNU      |         |
| Cray     |         |

**Observations**

Example:

* Cray compiler shows slightly better vectorisation

---



## Experiment 006 – Profiling Analysis

**Date**

YYYY-MM-DD

**Objective**

Identify performance bottlenecks using profiling tools.

**Tool Used**

Example:

```
CrayPat
```

**Key Observations**

Example:

* majority of runtime spent in solver iterations
* communication overhead increases with MPI rank count

**Next Steps**

Investigate hybrid configuration impact on communication cost.

---

# Notes

General notes about the experiment process can be written here.

Examples:

* anomalies observed during runs
* cluster issues
* job failures
* debugging notes

```

