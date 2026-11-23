#!/bin/zsh
# Usage: run_starts.sh <omp_threads> yaml1 yaml2 ...   (runs each cobaya minimization in parallel)
T2=/Users/420-420/ecf-md14/fullplanck/tier2
COB=/Users/420-420/Downloads/ecf-fullplanck-kit/venv312/bin/cobaya-run
NT=$1; shift
cd $T2
for y in "$@"; do
  n=$(basename $y .yaml)
  ( start=$(date -u +%FT%TZ)
    OMP_NUM_THREADS=$NT PYTHONDONTWRITEBYTECODE=1 $COB $y > logs/$n.log 2>&1
    echo "EXIT=$? start=$start end=$(date -u +%FT%TZ)" >> logs/$n.log ) &
done
wait
echo "all done: $@"
