#!/usr/bin/env bash
#SBATCH --account=m25oc-s2795693
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --job-name=ex2_mpi_min
#SBATCH --output=%x.%j.out
#SBATCH --error=%x.%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --hint=nomultithread

set -e

module purge
module load PrgEnv-gnu
module load cray-mpich

# ====== edit here if needed ======
PROJECT_ROOT="/work/m25oc/m25oc/s2795693/petsc_omp"
PETSC_ROOT="${PROJECT_ROOT}/src/petsc"
PETSC_ARCH="arch-mpi-opt"

M=800
N=800

RANKS_LIST=(1 2 4 8 16 32 64 128)
# ==================================

export OMP_NUM_THREADS=1

cd "${PETSC_ROOT}/src/ksp/ksp/tutorials"

for R in "${RANKS_LIST[@]}"; do
    echo "====================================="
    echo "Running with ${R} MPI ranks"
    echo "====================================="

    srun --ntasks="${R}" --cpus-per-task=1 \
         ./ex2 -m ${M} -n ${N} -log_view
done