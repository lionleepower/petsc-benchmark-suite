#!/usr/bin/env bash
set -euo pipefail

module purge
module load PrgEnv-gnu
module load cray-mpich

echo "Compiler wrappers:"
which cc
which CC
which ftn
echo

echo "Versions:"
cc --version | head -n 1
echo "MPICH:"
mpirun --version 2>/dev/null | head -n 1 || true
echo

echo "Environment:"
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS:-unset}"
echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-unset}"
