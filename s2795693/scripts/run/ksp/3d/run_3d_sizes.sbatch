#!/usr/bin/env bash
#SBATCH --account=m25oc-s2795693
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --job-name=3d_grid
#SBATCH --output=%x.%j.out
#SBATCH --error=%x.%j.err
#SBATCH --nodes=1
#SBATCH --time=12:00:00
#SBATCH --hint=nomultithread
#SBATCH --distribution=block:block
##SBATCH --exclusive

set -euo pipefail

module purge
module load PrgEnv-gnu
module load cray-mpich

# Project root (always write outputs under project)
PROJECT_ROOT="/work/m25oc/m25oc/s2795693/petsc_omp"
cd "${PROJECT_ROOT}"

RUN_DIR="${PROJECT_ROOT}/runs/ksp_3d"
RES_DIR="${PROJECT_ROOT}/results/ksp_3d"
mkdir -p "${RUN_DIR}" "${RES_DIR}"

# PETSc paths
ROOT="/mnt/lustre/a2fs-work4/work/m25oc/m25oc/s2795693/petsc_omp"
export PETSC_DIR="${ROOT}/src/petsc"
export PETSC_ARCH="arch-omp-opt"

# Ensure PETSc shared libs are found at runtime and set Cray target if missing
export LD_LIBRARY_PATH="${PETSC_DIR}/${PETSC_ARCH}/lib:${LD_LIBRARY_PATH:-}"
export CRAY_CPU_TARGET="${CRAY_CPU_TARGET:-x86-64}"

# 3D problem size 
SIZE_TABLE="${SIZE_TABLE:-${PROJECT_ROOT}/scripts/ksp/3Dproblem_sizes.csv}"

# Start conservatively by default. Override at submission time, for example:
#   SCALES="large very-large" sbatch scripts/run_ex2_size_grid.sbatch
#   SCALES="small medium-small medium large very-large" REPEAT=3 sbatch scripts/run_ex2_size_grid.sbatch
SCALES="${SCALES:-small}"

# Repeat count and core limits
REPEAT="${REPEAT:-1}"

# Make 10,000 < N/C < 1,000,000
MAX_RANGE="${MAX_RANGE:-1000000}"
MIN_RANGE="${MIN_RANGE:-10000}"


export OMP_PLACES=cores
export OMP_PROC_BIND=close

OUTCSV="${RES_DIR}/grid_3d_${PETSC_ARCH}_job${SLURM_JOB_ID}.csv"
echo "timestamp,jobid,nodelist,nodes,scale,m,n,p,unknowns,ppn,threads,total_cores,unknowns_per_core,rep,time_sec,iterations,error_norm,logfile" > "${OUTCSV}"

ts() { date -Iseconds; }
want_scale() {
  local needle="$1"
  local scale
  for scale in ${SCALES}; do
    [[ "${scale}" == "${needle}" ]] && return 0
  done
  return 1
}


PPN="${PPN:-16 32 64 128}"
THREADS="${THREADS:-1 2 4 8}"
NODES="${SLURM_JOB_NUM_NODES:-1}"

read -r -a PPN_LIST <<< "${PPN}"
read -r -a THREADS_LIST <<< "${THREADS}"

ran_any_scale=0

contains_thread(){
    local needle="$1"
    local t
    for t in "${THREADS_LIST[@]}";do
        [[ "${t}" == "${needle}" ]] && return 0
    done
    return 1
    
}

echo "============================================================"
echo "PETSc 3D stencil rank x thread grid study"
echo "JobID=${SLURM_JOB_ID}"
echo "PROJECT_ROOT=${PROJECT_ROOT}"
echo "RUN_DIR=${RUN_DIR}"
echo "RES_DIR=${RES_DIR}"
echo "PETSC_DIR=${PETSC_DIR}"
echo "PETSC_ARCH=${PETSC_ARCH}"
echo "SIZE_TABLE=${SIZE_TABLE}"
echo "SCALES=${SCALES}"
echo "REPEAT=${REPEAT}  MAX_RANGE=${MAX_RANGE}  MIN_RANGE=${MIN_RANGE}"
echo "PPN=${PPN}"
echo "THREADS=${THREADS}"
echo "NODES=${NODES}"
echo "NodeList=${SLURM_JOB_NODELIST:-UNKNOWN}"
echo "CSV=${OUTCSV}"
echo "============================================================"


# Build the executable from src/script/3d-stencil.c
SRC_PROG="${PROJECT_ROOT}/src/script/3d-stencil.c"
EXE="${PROJECT_ROOT}/src/script/3d-stencil"


if [[ ! -f "${SRC_PROG}" ]]; then
  echo "[ERROR] 3d source not found: ${SRC_PROG}"
  exit 1
fi

echo "[BUILD] Compiling ${SRC_PROG} -> ${EXE}"
# Use system compiler (Cray wrappers) and link against PETSc libs; embed rpath for runtime
cc -O3 -fopenmp \
  -I"${PETSC_DIR}/include" -I"${PETSC_DIR}/${PETSC_ARCH}/include" \
  "${SRC_PROG}" -L"${PETSC_DIR}/${PETSC_ARCH}/lib" -Wl,-rpath,"${PETSC_DIR}/${PETSC_ARCH}/lib" -lpetsc -o "${EXE}"



while IFS=, read -r SCALE M N P UNKNOWNS; do
  [[ "${SCALE}" == "scale" ]] && continue
  [[ -z "${SCALE}" ]] && continue

  if ! want_scale "${SCALE}"; then
    continue
  fi

  ran_any_scale=1
  SCALE_RUN_DIR="${RUN_DIR}/${SCALE}"
  mkdir -p "${SCALE_RUN_DIR}"


  echo "============================================================"
  echo "[SCALE] ${SCALE}: M=${M} N=${N} P=${P} unknowns=${UNKNOWNS}"
  echo "Logs under: ${SCALE_RUN_DIR}"
  echo "============================================================"

  for R in "${PPN_LIST[@]}"; do
    T=$(( 128 / R )) 
    contains_thread "${T}" || continue

    C=$(( R * T * NODES))  
    
    (( UNKNOWNS >= MAX_RANGE * C )) && continue
    (( UNKNOWNS <= MIN_RANGE * C )) && continue

    NEED=$(( UNKNOWNS / C))

    export OMP_NUM_THREADS="${T}"
    export SRUN_CPUS_PER_TASK="${T}"
    export UNKNOWNS_PER_CORE="${NEED}"

    echo "------------------------------------------------------------"
    echo "[CONFIG] scale=${SCALE} nodes=${NODES} ppn=${R} threads=${T} total_cores=${C}"
    echo "  OMP_NUM_THREADS=${OMP_NUM_THREADS} SRUN_CPUS_PER_TASK=${SRUN_CPUS_PER_TASK}"
    echo "  unknowns_per_core=${NEED}"
    echo "------------------------------------------------------------"

    for rep in $(seq 1 "${REPEAT}"); do
      LOG="${SCALE_RUN_DIR}/3d_${PETSC_ARCH}_${SCALE}_ppn${R}_t${T}_cores${C}_m${M}_n${N}_p${P}_job${SLURM_JOB_ID}_rep${rep}.log"

      echo "[RUN] $(ts) scale=${SCALE} ppn=${R} threads=${T} total_cores=${C} rep=${rep}"
      echo "  logfile=${LOG}"

      srun --nodes="${NODES}" --ntasks-per-node="${R}" --cpus-per-task="${T}" --exact \
           --hint=nomultithread --distribution=block:block \
           "${EXE}" -m "${M}" -n "${N}" -p "${P}" -ksp_converged_reason -log_view \
        | tee "${LOG}"

      TIMESEC="$(awk '/Time \(sec\):/{t=$4} END{print t}' "${LOG}")"
      ITER="$(awk '/Norm of error/{iter=$NF} END{print iter}' "${LOG}")"
      ERRNORM="$(awk '/Norm of error/{err=$(NF-3)} END{print err}' "${LOG}")"

      if [[ -z "${TIMESEC}" ]]; then
        echo "[ERROR] No 'Time (sec):' parsed from ${LOG} (r=${R} t=${T} rep=${rep})."
        echo "[ERROR] Aborting to avoid corrupting CSV."
        exit 1
      fi

      echo "$(ts),${SLURM_JOB_ID},${SLURM_JOB_NODELIST:-UNKNOWN},${SLURM_JOB_NUM_NODES},${SCALE},${M},${N},${P},${UNKNOWNS},${R},${T},${C},${NEED},${rep},${TIMESEC},${ITER},${ERRNORM},${LOG}" >> "${OUTCSV}"
    done
  done
done < "${SIZE_TABLE}"


if (( ran_any_scale == 0 )); then
  echo "[ERROR] No matching scales found in ${SIZE_TABLE} for SCALES='${SCALES}'."
  exit 1
fi

echo "============================================================"
echo "Completed"
echo "CSV written: ${OUTCSV}"
echo "Logs under: ${RUN_DIR}"
echo "============================================================"
