#!/usr/bin/env bash
#SBATCH --account=m25oc-s2795693
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --job-name=petsc_ex2_grid
#SBATCH --output=%x.%j.out
#SBATCH --error=%x.%j.err
#SBATCH --nodes=1
#SBATCH --time=01:30:00
#SBATCH --hint=nomultithread
#SBATCH --distribution=block:block
##SBATCH --exclusive

set -euo pipefail

module purge
module load PrgEnv-gnu
module load cray-mpich

# Always write outputs under the project root
PROJECT_ROOT="/work/m25oc/m25oc/s2795693/petsc_omp"
cd "${PROJECT_ROOT}"

RUN_DIR="${PROJECT_ROOT}/runs/rank_thread_grid"
RES_DIR="${PROJECT_ROOT}/results/rank_thread_grid"
mkdir -p "${RUN_DIR}" "${RES_DIR}"

# PETSc paths
ROOT="/mnt/lustre/a2fs-work4/work/m25oc/m25oc/s2795693/petsc_omp"
export PETSC_DIR="${ROOT}/src/petsc"
export PETSC_ARCH="arch-omp-opt"

# Fixed problem size
M=800
N=800

# Default to 1 for a full-grid smoke test; override at submission time:
#   REPEAT=5 or other nums?  sbatch run_ex2_grid.sbatch
REPEAT="${REPEAT:-1}"

# Single ARCHER2 node has 128 physical cores
MAX_CORES="${MAX_CORES:-128}"

export OMP_PLACES=cores
export OMP_PROC_BIND=close

# Avoid overwriting previous runs by including JobID in filename
OUTCSV="${RES_DIR}/grid_ex2_${PETSC_ARCH}_m${M}_n${N}_job${SLURM_JOB_ID}.csv"
echo "timestamp,jobid,nodelist,nodes,ranks,threads,total_cores,rep,time_sec,iterations,error_norm,logfile" > "${OUTCSV}"

ts() { date -Iseconds; }

echo "============================================================"
echo "PETSc ex2 rank x thread grid study"
echo "JobID=${SLURM_JOB_ID}"
echo "PROJECT_ROOT=${PROJECT_ROOT}"
echo "RUN_DIR=${RUN_DIR}"
echo "RES_DIR=${RES_DIR}"
echo "PETSC_DIR=${PETSC_DIR}"
echo "PETSC_ARCH=${PETSC_ARCH}"
echo "Mesh: M=${M}, N=${N}"
echo "REPEAT=${REPEAT}  MAX_CORES=${MAX_CORES}"
echo "NodeList=${SLURM_JOB_NODELIST:-UNKNOWN}"
echo "CSV=${OUTCSV}"
echo "============================================================"

# Build ex2 once (faster with -j)
cd "${PETSC_DIR}/src/ksp/ksp/tutorials"
make -j PETSC_DIR="${PETSC_DIR}" PETSC_ARCH="${PETSC_ARCH}" ex2

RANKS_LIST=(1 2 4 8 16 32 64 128)
THREADS_LIST=(1 2 4 8 16 32 64 128)

for R in "${RANKS_LIST[@]}"; do
  (( R > MAX_CORES )) && continue

  MAX_T=$(( MAX_CORES / R ))
  (( MAX_T < 1 )) && continue

  for T in "${THREADS_LIST[@]}"; do
    (( T > MAX_T )) && continue

    P=$(( R * T ))

    export OMP_NUM_THREADS="${T}"
    export SRUN_CPUS_PER_TASK="${T}"

    echo "------------------------------------------------------------"
    echo "[CONFIG] ranks=${R} threads=${T} total_cores=${P}"
    echo "  OMP_NUM_THREADS=${OMP_NUM_THREADS} SRUN_CPUS_PER_TASK=${SRUN_CPUS_PER_TASK}"
    echo "------------------------------------------------------------"

    for rep in $(seq 1 "${REPEAT}"); do
      LOG="${RUN_DIR}/ex2_${PETSC_ARCH}_r${R}_t${T}_p${P}_m${M}_n${N}_rep${rep}.log"

      echo "[RUN] $(ts) r=${R} t=${T} p=${P} rep=${rep}"
      echo "  logfile=${LOG}"

      srun --nodes=1 --ntasks="${R}" --cpus-per-task="${T}" --exact \
           --hint=nomultithread --distribution=block:block \
           "${PETSC_DIR}/src/ksp/ksp/tutorials/ex2" \
           -m "${M}" -n "${N}" -ksp_converged_reason -log_view \
        | tee "${LOG}"

      TIMESEC="$(awk '/Time \(sec\):/{t=$3} END{print t}' "${LOG}")"
      ITER="$(awk '/Norm of error/{iter=$NF} END{print iter}' "${LOG}")"
      ERRNORM="$(awk '/Norm of error/{err=$(NF-3)} END{print err}' "${LOG}")"

      # Guard against partial/failed logs (prevents writing empty time values to CSV)
      if [[ -z "${TIMESEC}" ]]; then
        echo "[ERROR] No 'Time (sec):' parsed from ${LOG} (r=${R} t=${T} rep=${rep})."
        echo "[ERROR] Aborting to avoid corrupting CSV."
        exit 1
      fi

      echo "$(ts),${SLURM_JOB_ID},${SLURM_JOB_NODELIST:-UNKNOWN},${SLURM_JOB_NUM_NODES},${R},${T},${P},${rep},${TIMESEC},${ITER},${ERRNORM},${LOG}" >> "${OUTCSV}"
    done
  done
done

echo "============================================================"
echo "Completed"
echo "CSV written: ${OUTCSV}"
echo "Logs under: ${RUN_DIR}"
echo "============================================================"