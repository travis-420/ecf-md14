#!/bin/zsh
# EXPLORATORY minimizer study (not a gate attempt). Fits 1 and 2 only.
# Usage: launch.sh <tag> <variant> <deadline_epoch> [start_json]   -> 16 polish.py processes in parallel, OMP_NUM_THREADS=1
EXP=/Users/420-420/ecf-md14/fullplanck/tier2_explore
PY=/Users/420-420/Downloads/ecf-fullplanck-kit/venv312/bin/python
TAG=$1; VAR=$2; DL=$3; SJ=$4
cd $EXP
for fit in fit1_lcdm_mnufixed fit2_ecf_mnufixed; do
  for k in 0 1 2 3 4 5 6 7; do
    ( st=$(date -u +%FT%TZ)
      OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 $PY -I -B scripts/polish.py $TAG $fit $k $DL $VAR $SJ > logs/${TAG}_${fit}_s${k}.log 2>&1
      echo "EXIT=$? start=$st end=$(date -u +%FT%TZ)" >> logs/${TAG}_${fit}_s${k}.log ) &
  done
done
wait
echo "all done: $TAG $(date -u +%FT%TZ)"
