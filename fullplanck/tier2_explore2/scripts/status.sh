#!/bin/zsh
# compact progress view (reads logs only)
cd /Users/420-420/ecf-md14/fullplanck/tier2_explore2; setopt nullglob
date -u +%FT%TZ; uptime | sed 's/.*load/load/'
for t in c1 c2 c3 c4 e2e cpl; do
  files=(logs/${t}_*.log); (( ${#files} )) || continue; n=${#files}
  echo "$t: logs $n, ROUND lines $(cat $files | grep -c '^ROUND '), CRASH $(cat $files | grep -c '^CRASH '), STOP $(cat $files | grep -c '^STOP'), EXIT $(cat $files | grep -c '^EXIT=')"
  grep -h '^CRASH ' $files | cut -c1-200
done
echo "base: json $(ls logs/base_*.json 2>/dev/null | wc -l | tr -d ' ')/24; statuses: $(cat logs/base_*.json 2>/dev/null | grep -o '"status": "[a-z_]*"' | sort | uniq -c | tr '\n' ' ')"
