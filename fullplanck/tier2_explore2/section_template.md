

---

# Exploratory minimizer study 2 (not a gate attempt) — executed 2026-11-24, 02:38–«END» UTC

**EXPLORATORY. This is not a gate attempt and it counts toward nothing.** It is not a G0 or G1 run, it
produces no R1–R4 outcome, and **no G1 verdict is declared anywhere in this section.** Three models were built and
fitted, all with **Σmν fixed at 0.06 eV**: fit 1, fit 2, and the July CPL model (`fullplanck/cpl_full.yaml` as
shipped).
- **The CPL runs are not fit 5.** Fit 5 has free Σmν.
- **No model with free Σmν was built, evaluated or fitted, and no fit 3, 4 or 5 was run.** Every yaml this study wrote
  was checked at the end: Σmν fixed at 0.06 eV and never a parameter (`logs/session_end.log`).
- No amendment, commit or push was made.

This section is appended. The sections above are unchanged byte-for-byte: SHA-256 of the first 62486 bytes =
`249511e0342ede647f794a7cb74e9769e33a95c51a5227ca996921e0177ac49b`, which is the hash of the whole file before this
append (`fullplanck/tier2_explore2/logs/session_start.log`; re-checked in `logs/session_end.log`).

Every number below comes from a command logged under `fullplanck/tier2_explore2/logs/` (paths below are relative to
`fullplanck/tier2_explore2/`). The round tables were generated from the run logs by `scripts/tables2.py`
(`logs/tables_*.log`) and pasted in verbatim by `scripts/assemble2.py`.

«SUMMARY»

## Scope, inputs and execution

- **Brief (owner's, this session).** The aim is a polish procedure that:
  - (a) never crashes;
  - (b) brings all 8 starts of fit 1 and of fit 2 into agreement, target S ≤ 0.1;
  - (c) works end to end from fresh random starts;
  - (d) still works with more parameters.

  Steps, in order:
  1. diagnose the crash;
  2. try at most four candidates on session 2's 16 endpoints, using the first study's round and stop rule;
  3. run an end-to-end test of the best candidate on fits 1 and 2 (seeds 9001–9007);
  4. run a dimension test on CPL with Σmν fixed;
  5. recommend a procedure.

  Seeds 2001–2007 and 3001–3007 were not used. The fresh starts use seeds 9001–9007. 4-hour wall-time cap.
- **Read-only inputs:**
  - `fullplanck/tier2_rerun/` (session 2): yamls, `chains/*.minimum`, covmats;
  - `fullplanck/tier2_explore/` (first study): the step3A yaml of fit 2 s1, scripts read for reference;
  - `fullplanck/chains/*.minimum.txt` (certified s0 points).

  Nothing in these directories was written (`logs/session_end.log`).
- **Unchanged:** likelihood stack, kit code, priors and environment. The environment is the July venv:
  - Python 3.12.12, numpy 2.1.3, scipy 1.14.1, camb 1.6.6, cobaya 3.6.2, Py-BOBYQA 1.5.0 (`logs/session_start.log`);
  - no package installed or upgraded.

  Kit-file and covmat SHA-256 values at session start are in `logs/session_start.log`. Session 2's covmat copies are
  byte-identical to those listed in `AMENDMENT_TIER2_MINIMIZER.md` §2.3.
- **Execution:**
  - each start is its own Python process calling `cobaya.run`, with `OMP_NUM_THREADS=1`;
  - same 16-core machine (Apple M3 Max, 64 GB);
  - outputs go to `fullplanck/tier2_explore2/`.

  Wall times depend on load, which was heavy: up to 72 concurrent processes on 16 cores, at different `nice` levels
  (see Notes). Evaluations are therefore the load-independent cost. Median wall time per evaluation per process was
  5–10 s, against a median of 2.9 s in step 1 with 3 processes (`logs/load_stats.log`). `caffeinate` ran for the
  whole session and was stopped at the end.

«STEP1»

## Step 2 — four candidates on session 2's 16 endpoints

**Procedure, identical for every candidate.**
- **Rounds:** round 0 is session 2's endpoint (`tier2_rerun/chains/*.minimum`, 10 significant digits, as in the first
  study). Round r reruns cobaya `minimize` from the round r−1 endpoint.
- **Yaml:** session 2's yaml for that start, unchanged except for `ref` (the endpoint), the `sampler` block (no seed:
  the start is fixed, so cobaya draws nothing) and the output path.
- **Stop rule:** at most 5 rounds; a start stops after the first round that lowers −log posterior by less than 0.001.
- **Failed rounds:** a round that fails (Py-BOBYQA or scipy not successful, so cobaya raises `Minimization failed!`)
  is recorded, and the start stops with no result for that round.
- **"Produces a result":** a start ended on the stop rule or the 5-round cap.
- **Driver:** `scripts/polish2.py`. Launch logs with driver hashes: `logs/step2_and_base_launch.log`,
  `logs/step2_c4_launch.log`. The as-run driver for (i)–(iii) is preserved as `logs/polish2_asrun_c1c2c3.py.txt`; (iv)
  only added a variant and an RNG seed hook.

**Candidates.** Each changes only the polish `sampler` block, with everything else as in session 2:

| tag | candidate | settings |
|---|---|---|
| c1 | (i) | bobyqa, `rhoend` 0.005, **npt = (n+1)(n+2)/2 − 1** (35 for fit 1, 44 for fit 2), `rhobeg` 1.0 (cobaya's) |
| c2 | (ii) | bobyqa, `rhoend` 0.005, **npt = (n+1)(n+2)/2** (36, 45), **`rhobeg` 0.1** |
| c3 | (iii) | **scipy Powell** (`method: scipy`), options as pre-configured but never run in the first study's driver: `xtol` 1e-4, `ftol` 1e-8, `maxfev` 3000 |
| c4 | (iv) | bobyqa, `rhoend` 0.005, **npt = (n+1)(n+2)/2**, `rhobeg` 1.0, Py-BOBYQA `init.random_initial_directions: True`, `init.random_directions_make_orthogonal: False`; numpy global RNG seeded 9100 + k before every round |

- **(ii): passing `rhobeg` causes no conflict.** cobaya 3.6.2 builds the Py-BOBYQA arguments with `rhobeg: 1.0` and then
  applies `override_bobyqa` with `recursive_update` (`samplers/minimize/minimize.py`), so the override replaces it.
  `rhobeg` 0.1 was fixed before any candidate ran.
- **(iv) ran because (i)–(iii) had all failed (b):**
  - Once some fit-2 starts of each had finished, the S over those finished starts alone already exceeded 0.1:
    (i) 0.2242, (ii) 0.1357, (iii) 0.2193.
  - It is designed from step 1: Py-BOBYQA's non-orthogonal random directions contain no antipodal pairs, so no
    initial Lagrange polynomial has zero gradient at x0.
  - Py-BOBYQA has no seed argument and draws these directions from numpy's global RNG, so the driver seeds that RNG
    (9100–9107, outside every reserved range). The offline check showed a seeded run is bitwise deterministic.
  - Decision log: `logs/decision_rule.log`.
- **How the best candidate is chosen** was written down before any candidate round had completed
  (`logs/decision_rule.log`):
  - (a) is met if no start of either fit has a failed round;
  - (b) is met if all 8 starts of each fit produce a result and S ≤ 0.1 for each fit;
  - among candidates meeting both, the one with the fewest evaluations is best;
  - if none meets both: the candidate meeting (a) with the smallest max(S fit 1, S fit 2).

### Step 2 summary (from the tables below)

«STEP2SUMMARY»

### Step 2 tables

Cell = −log post / total χ² / τ-prior term (2 × `minuslogprior__tau_prior`). Round 0 shows −log post only, as read from
the starting endpoint. `=`: start already stopped. `!`: start failed in or before this round (excluded). `...`: still
running, or stopped by me, at the time the table was generated. Evals and min are per start over all its rounds; min =
wall minutes under the load described above.

{{FILE:logs/tables_step2_c1.log}}

{{FILE:logs/tables_step2_c2.log}}

{{FILE:logs/tables_step2_c3.log}}

{{FILE:logs/tables_step2_c4.log}}

«STEP3»

«STEP4»

«STEP5»

«NOTES»
