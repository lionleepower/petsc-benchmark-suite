#!/usr/bin/env bash
#SBATCH --account=m25oc-s2795693
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --job-name=petsc_ex2_n1_fixed128
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

PROJECT_ROOT="/work/m25oc/m25oc/s2795693/petsc_omp"
cd "${PROJECT_ROOT}"

RUN_DIR="${PROJECT_ROOT}/runs/fixed128_multinode"
RES_DIR="${PROJECT_ROOT}/results/fixed128_multinode"
mkdir -p "${RUN_DIR}" "${RES_DIR}"

ROOT="/mnt/lustre/a2fs-work4/work/m25oc/m25oc/s2795693/petsc_omp"
export PETSC_DIR="${ROOT}/src/petsc"
export PETSC_ARCH="arch-omp-opt"

M=800
N=800
REPEAT="${REPEAT:-1}"
TOTAL_CORES=128
THREADS_LIST=(1 2 4 8)

export OMP_PLACES=cores
export OMP_PROC_BIND=close

OUTCSV="${RES_DIR}/fixed128_ex2_${PETSC_ARCH}_nodes1_m${M}_n${N}_job${SLURM_JOB_ID}.csv"
echo "timestamp,jobid,nodelist,nodes,ranks,ranks_per_node,threads,total_cores,rep,time_sec,iterations,error_norm,logfile" > "${OUTCSV}"

ts() { date -Iseconds; }

echo "============================================================"
echo "PETSc ex2 fixed-128-core multinode supplement"
echo "JobID=${SLURM_JOB_ID}"
echo "PROJECT_ROOT=${PROJECT_ROOT}"
echo "RUN_DIR=${RUN_DIR}"
echo "RES_DIR=${RES_DIR}"
echo "PETSC_DIR=${PETSC_DIR}"
echo "PETSC_ARCH=${PETSC_ARCH}"
echo "Mesh: M=${M}, N=${N}"
echo "Nodes=1  TOTAL_CORES=${TOTAL_CORES}"
echo "THREADS_LIST=${THREADS_LIST[*]}"
echo "REPEAT=${REPEAT}"
echo "NodeList=${SLURM_JOB_NODELIST:-UNKNOWN}"
echo "CSV=${OUTCSV}"
echo "============================================================"

cd "${PETSC_DIR}/src/ksp/ksp/tutorials"
make -j PETSC_DIR="${PETSC_DIR}" PETSC_ARCH="${PETSC_ARCH}" ex2
cd "${PROJECT_ROOT}"

for T in "${THREADS_LIST[@]}"; do
  R=$(( TOTAL_CORES / T ))
  RPERNODE=$(( R / 1 ))

  export OMP_NUM_THREADS="${T}"
  export SRUN_CPUS_PER_TASK="${T}"

  echo "------------------------------------------------------------"
  echo "[CONFIG] nodes=1 ranks=${R} ranks_per_node=${RPERNODE} threads=${T} total_cores=${TOTAL_CORES}"
  echo "  OMP_NUM_THREADS=${OMP_NUM_THREADS} SRUN_CPUS_PER_TASK=${SRUN_CPUS_PER_TASK}"
  echo "------------------------------------------------------------"

  for rep in $(seq 1 "${REPEAT}"); do
    LOG="${RUN_DIR}/ex2_${PETSC_ARCH}_nodes1_r${R}_rpn${RPERNODE}_t${T}_p${TOTAL_CORES}_m${M}_n${N}_rep${rep}.log"

    echo "[RUN] $(ts) nodes=1 r=${R} rpn=${RPERNODE} t=${T} p=${TOTAL_CORES} rep=${rep}"
    echo "  logfile=${LOG}"

    srun --nodes=1 --ntasks="${R}" --ntasks-per-node="${RPERNODE}" \
         --cpus-per-task="${T}" --exact \
         --hint=nomultithread --distribution=block:block \
         "${PETSC_DIR}/src/ksp/ksp/tutorials/ex2" \
         -m "${M}" -n "${N}" -ksp_converged_reason -log_view \
      | tee "${LOG}"

    TIMESEC="$(awk '/Time \(sec\):/{t=$3} END{print t}' "${LOG}")"
    ITER="$(awk '/Norm of error/{iter=$NF} END{print iter}' "${LOG}")"
    ERRNORM="$(awk '/Norm of error/{err=$(NF-3)} END{print err}' "${LOG}")"

    if [[ -z "${TIMESEC}" ]]; then
      echo "[ERROR] No 'Time (sec):' parsed from ${LOG} (nodes=1 r=${R} t=${T} rep=${rep})."
      exit 1
    fi

    echo "$(ts),${SLURM_JOB_ID},${SLURM_JOB_NODELIST:-UNKNOWN},1,${R},${RPERNODE},${T},${TOTAL_CORES},${rep},${TIMESEC},${ITER},${ERRNORM},${LOG}" >> "${OUTCSV}"
  done
done

echo "============================================================"
echo "Completed fixed-128-core nodes=1 experiment"
echo "CSV written: ${OUTCSV}"
echo "Logs under: ${RUN_DIR}"
echo "============================================================"
