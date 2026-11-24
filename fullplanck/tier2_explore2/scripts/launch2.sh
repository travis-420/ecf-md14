#!/bin/zsh
# EXPLORATORY minimizer study 2 (not a gate attempt). Fixed Sigma-mnu models only.
# polish: launch2.sh polish <tag> <variant> <deadline_epoch> <source> <nice> <fit1,fit2,...>   (8 starts per fit)
# base:   launch2.sh base   <nice> <fit1,fit2,...>                                           (8 starts per fit)
# polish_after_base: launch2.sh polish_after_base <tag> <variant> <deadline_epoch> <nice> <fits>  (waits per start)
# Each start is its own process, OMP_NUM_THREADS=1, log logs/<tag>_<fit>_s<k>.log with an EXIT line appended.
EXP2=/Users/420-420/ecf-md14/fullplanck/tier2_explore2
PY=/Users/420-420/Downloads/ecf-fullplanck-kit/venv312/bin/python
cd $EXP2
MODE=$1
if [[ $MODE == polish ]]; then
  TAG=$2; VAR=$3; DL=$4; SRC=$5; NI=$6; FITS=(${(s:,:)7})
  for fit in $FITS; do for k in 0 1 2 3 4 5 6 7; do
    ( st=$(date -u +%FT%TZ)
      OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n $NI $PY -I -B scripts/polish2.py $TAG $fit $k $DL $VAR $SRC > logs/${TAG}_${fit}_s${k}.log 2>&1
      echo "EXIT=$? start=$st end=$(date -u +%FT%TZ)" >> logs/${TAG}_${fit}_s${k}.log ) &
  done; done
  wait; echo "all done: $TAG $(date -u +%FT%TZ)"
elif [[ $MODE == polish_after_base ]]; then
  # same as polish (source 'base'), but each start waits for its own base run to finish (its JSON to appear);
  # a base start that did not converge is recorded and not polished
  TAG=$2; VAR=$3; DL=$4; NI=$5; FITS=(${(s:,:)6})
  for fit in $FITS; do for k in 0 1 2 3 4 5 6 7; do
    ( until [[ -f logs/base_${fit}_s${k}.json ]]; do sleep 20; done
      if grep -q '"status": "converged"' logs/base_${fit}_s${k}.json; then
        st=$(date -u +%FT%TZ)
        OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n $NI $PY -I -B scripts/polish2.py $TAG $fit $k $DL $VAR base > logs/${TAG}_${fit}_s${k}.log 2>&1
        echo "EXIT=$? start=$st end=$(date -u +%FT%TZ)" >> logs/${TAG}_${fit}_s${k}.log
      else
        echo "NOT POLISHED: base run did not converge ($(date -u +%FT%TZ))" > logs/${TAG}_${fit}_s${k}.log
      fi ) &
  done; done
  wait; echo "all done: $TAG $(date -u +%FT%TZ)"
elif [[ $MODE == base ]]; then
  NI=$2; FITS=(${(s:,:)3})
  for fit in $FITS; do for k in 0 1 2 3 4 5 6 7; do
    ( st=$(date -u +%FT%TZ)
      OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n $NI $PY -I -B scripts/base_run.py $fit $k > logs/base_${fit}_s${k}.log 2>&1
      echo "EXIT=$? start=$st end=$(date -u +%FT%TZ)" >> logs/base_${fit}_s${k}.log ) &
  done; done
  wait; echo "all done: base $FITS $(date -u +%FT%TZ)"
fi
