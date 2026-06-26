#!/usr/bin/env bash
#SBATCH --account=m25oc-s2795693
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --job-name=petsc_ex2_omp
#SBATCH --output=%x.%j.out
#SBATCH --error=%x.%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=8
#SBATCH --time=00:10:00

set -euo pipefail

module purge
module load PrgEnv-gnu
module load cray-mpich

ROOT="/mnt/lustre/a2fs-work4/work/m25oc/m25oc/s2795693/petsc_omp"
export PETSC_DIR="${ROOT}/src/petsc"
export PETSC_ARCH="arch-omp-opt"

# OpenMP settings (this matters here)
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OMP_PLACES=cores
export OMP_PROC_BIND=close

cd "${PETSC_DIR}/src/ksp/ksp/tutorials"

make PETSC_DIR="${PETSC_DIR}" PETSC_ARCH="${PETSC_ARCH}" ex2

srun --hint=nomultithread \
     --distribution=block:block \
     --cpus-per-task="${SLURM_CPUS_PER_TASK}" \
     ./ex2 -m 200 -n 200 -ksp_converged_reason -log_view
