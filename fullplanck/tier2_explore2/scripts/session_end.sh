#!/bin/zsh
# EXPLORATORY minimizer study 2 (not a gate attempt) -- end-of-session integrity checks.
# Usage: session_end.sh <stage>   (stage = pre_append | post_append)
cd /Users/420-420/ecf-md14
E=fullplanck/tier2_explore2
PY=/Users/420-420/Downloads/ecf-fullplanck-kit/venv312/bin/python
echo "== $1 $(date -u +%FT%TZ) ($(date '+%H:%M:%S %Z'))"
echo "-- files in read-only dirs newer than this session's start stamp (expect none):"
find fullplanck/tier2 fullplanck/tier2_rerun fullplanck/tier2_explore fullplanck/chains -newer $E/logs/session_start.stamp -print
echo "-- kit files newer than start stamp (expect none):"
find fullplanck -maxdepth 1 -type f -newer $E/logs/session_start.stamp -print
find fullplanck/__pycache__ -newer $E/logs/session_start.stamp -print 2>/dev/null
echo "-- git"; git rev-parse HEAD; git status --porcelain; git diff --stat HEAD
echo "-- RESULTS_NEUTRINO_TIER2.md: size, whole-file SHA-256, SHA-256 of first 62486 bytes (expect 249511e0342ede647f794a7cb74e9769e33a95c51a5227ca996921e0177ac49b)"
wc -c RESULTS_NEUTRINO_TIER2.md; shasum -a 256 RESULTS_NEUTRINO_TIER2.md; head -c 62486 RESULTS_NEUTRINO_TIER2.md | shasum -a 256
echo "-- every yaml written by this study: sampled params and Sigma-mnu setting (expect mnu fixed 0.06, never sampled):"
$PY -I -B - <<'EOF'
import glob, yaml, collections
c = collections.Counter(); bad = []
for p in sorted(glob.glob('/Users/420-420/ecf-md14/fullplanck/tier2_explore2/yamls/*.yaml')
                + glob.glob('/Users/420-420/ecf-md14/fullplanck/tier2_explore2/chains/*.updated.yaml')):
    y = yaml.safe_load(open(p)); th = y['theory'][list(y['theory'])[0]]
    ok = ('mnu' not in y['params']) and th.get('extra_args', {}).get('mnu') == 0.06
    c[ok] += 1
    if not ok: bad.append(p)
print(f'yamls checked: {sum(c.values())}; fixed mnu=0.06 and mnu not a parameter: {c[True]}; violations: {bad}')
EOF
echo "-- outputs whose name suggests fits 3-5 (expect none):"; ls $E/chains $E/yamls $E/logs | grep -iE "fit3|fit4|fit5|mnufree" || echo none
echo "-- running study processes:"; ps -Ao pid,command | grep -E "[p]olish2.py|[b]ase_run.py|[c]rash_repro.py" | wc -l
