## Notes, deviations and integrity

- **Order of execution.**
  - Steps were decided in the brief's order.
  - The 24 base minimizations for steps 3 and 4 were *started* at 02:47:55Z, together with step-2 candidates (i)–(iii).
    They use only `AMENDMENT_TIER2_MINIMIZER.md` §2 settings (seeds 9000+k) and do not depend on which candidate
    wins.
  - Only the step-3/4 polish depends on the choice, and it started after the choice was logged.
  - The reason was the 4-hour cap: run one after another, the base runs (the fit-2 ones needed up to 539 evaluations)
    could not have finished in time.
- **Steps 3–4 candidate chosen before rule 2 was formally determined.**
  - Recorded at 04:09:23Z in `logs/decision_rule.log`, with the four conditions under which the final step-2 values
    would overturn it.
  - At the time no candidate could still meet (b). Waiting for every step-2 start to finish would have left no time
    for steps 3–4.
  - Check against the final values: «OVERTURN»
- **Scheduling (no effect on results).**
  - zsh's `BG_NICE` option (on by default) adds +5 per background level, and every start ran two levels deep
    (`logs/bgnice_check.log`). So the processes launched "at nice 0" actually ran at `nice` 10, and Powell (iii),
    launched at 15, ran at 20 throughout.
  - At 04:09Z, `renice -n 5` (an increment) took the 7 still-running (iv) fit-2 processes from 10 to 15, below
    steps 3–4 (still at 10) and above Powell (20) (`logs/renice_note.log`; the note's first lines misread the starting
    value and are corrected at its end).
  - Only the relative priorities matter, and they were as intended: steps 3–4 and the other candidates first, (iv)
    after 04:09Z, Powell last.
  - Wall times are load-dependent, with medians of 5–10 s per evaluation per process (`logs/load_stats.log`), against
    2.9 s in step 1 with 3 processes. Evaluations are the load-independent cost.
- **Seeds.**
  - No random draw used seeds 2001–2007 or 3001–3007.
  - The step-1 reproduction ran the first study's step3A yaml with its seed field changed from 2001 to 9001. The start
    point is fixed, so cobaya draws nothing, and the crash reproduced exactly.
  - Base runs: seeds 9000–9007. s0's 9000 has no effect, since its start is fixed.
  - Polish rounds: no cobaya seed.
  - Candidate (iv): numpy global RNG 9100–9107, for Py-BOBYQA's initial directions.
  - Offline checks: numpy RNGs 0 and 9101, on a quadratic stand-in with no likelihood.
- **Driver versions.**
  - `scripts/polish2.py` gained variant (iv) after (i)–(iii) had launched; the running processes were unaffected.
    The as-run copy for (i)–(iii) is `logs/polish2_asrun_c1c2c3.py.txt`.
  - SHA-256 at every launch: `logs/step2_and_base_launch.log`, `logs/step2_c4_launch.log`, `logs/step34_launch.log`.
  - `scripts/tables2.py` gained a summary mode while runs were going; it is reporting only.
- «PARTIAL»
- **Read-only directories.** `find fullplanck/tier2 fullplanck/tier2_rerun fullplanck/tier2_explore fullplanck/chains
  -newer logs/session_start.stamp` returned nothing (`logs/session_end.log`). No kit file and nothing in the
  pre-existing `fullplanck/__pycache__/` changed: every run used `python -I -B` with `PYTHONDONTWRITEBYTECODE=1`.
- **Tracked files.**
  - HEAD is still `81f7db8`.
  - This append is the only change made to a tracked file in this session. `RESULTS_NEUTRINO_TIER2.md` already
    carried the first exploratory study's uncommitted append at session start (`logs/session_start.log`).
  - Untracked: `fullplanck/tier2_explore2/` (new), plus `.DS_Store`, `fullplanck/__pycache__/` and
    `fullplanck/tier2_explore/`, all present at session start.
  - No commit, push or amendment.
- **Free Σmν.** Every yaml written by this study (inputs and cobaya's `.updated.yaml` outputs) was checked: Σmν fixed at
  0.06 eV in the theory block and never a parameter (`logs/session_end.log`). No file name refers to fits 3–5.
- **Wall time.** «WALL»
