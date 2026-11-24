#!/bin/zsh
# EXPLORATORY minimizer study (not a gate attempt): end-of-session integrity checks. Run AFTER the append.
R=/Users/420-420/ecf-md14
EXP=$R/fullplanck/tier2_explore
echo "session end checks: $(date -u +%FT%TZ)"
echo "--- running polish/noise processes (expect none):"; pgrep -fl "polish.py|noise_floor.py" || echo none
echo "--- files in fullplanck/tier2 and fullplanck/tier2_rerun newer than logs/session_start.log (expect none):"
find $R/fullplanck/tier2 $R/fullplanck/tier2_rerun -newer $EXP/logs/session_start.log | head; echo "(end of list)"
echo "--- git:"; git -C $R rev-parse HEAD; git -C $R status --porcelain; git -C $R diff --stat
echo "--- RESULTS_NEUTRINO_TIER2.md: SHA-256 of first 29793 bytes (expect cf576d3a20c7eea437dcbc03b6fb217a611c5a1cbfa08a06a46a9b762e194daf):"
head -c 29793 $R/RESULTS_NEUTRINO_TIER2.md | shasum -a 256
wc -c $R/RESULTS_NEUTRINO_TIER2.md
echo "--- appended bytes identical to tier2_explore/section_final.md:"
tail -c +29794 $R/RESULTS_NEUTRINO_TIER2.md | cmp - $EXP/section_final.md && echo identical
echo "--- no fit 3/4/5 or free-mnu output in tier2_explore (expect none):"
ls $EXP/chains $EXP/yamls | grep -E "fit3|fit4|fit5|mnufree" || echo none
grep -l "mnu:" $EXP/yamls/*.yaml | xargs grep -L "mnu: 0.06" | head || true
echo "--- caffeinate:"; pkill -f "caffeinate -dims" ; sleep 1; pgrep -fl "caffeinate -dims" || echo "caffeinate -dims stopped"
