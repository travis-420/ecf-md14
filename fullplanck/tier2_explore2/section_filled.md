

---

# Exploratory minimizer study 2 (not a gate attempt) — executed 2026-11-24, 02:38–05:3x UTC

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

## Summary (plain statements)

- **Crash cause found** (step 1).
  - Py-BOBYQA 1.5.0's geometry-improving step returned the current best point x_opt itself. The interpolation set
    then held an exact duplicate point, so the full-quadratic system had a zero row: an exactly-zero LU pivot,
    `EXIT_LINALG_ERROR`.
  - It happens when the Lagrange polynomial of the point being replaced has zero gradient at x_opt. `trsbox_geometry`
    maximises |L| with a conjugate-gradient solver that starts from the gradient, so with a zero gradient it never
    moves.
  - With npt > 2n+1, every initial point beyond the 2n+1 "axis" points has exactly such a Lagrange polynomial, for as
    long as x_opt is still the start point.
  - Restarting exactly at a converged endpoint makes that the normal case, because nothing beats the start. The
    reproduction of fit 2 s1 failed at evaluation 48, exactly as in the first study. The geometry step there landed
    on x_opt.
  - Bounds, scaling and collinear distinct points are not involved.
- **No candidate met (a) and (b).**
  - **(a):** none of the four candidates had a failed round in step 2: (i) npt = (n+1)(n+2)/2 − 1,
    (ii) full npt with `rhobeg` 0.1, (iii) Powell, (iv) full npt with random directions. (iii)'s figures are partial: 6 of its 16 starts produced no result. Four hit the new-round deadline, and two were stopped by me at the time cap (see Notes).
  - **(b), fit 1:** met by (i), (ii) and (iv), with S = 0.0205, 0.0159 and 0.0105.
  - **(b), fit 2:** met by none. Best was (ii) at S = 0.1994; then (i) 0.2416, (iv) 0.4262, (iii) 0.5372, over the 5 of 8 starts that produced a result.
  - **What limits fit 2:** the 0.001 per-round stop rule ends starts while they are still up to 0.0026–0.0195 above
    the best start in −log post, depending on the candidate.
- **End to end from fresh starts** (step 3, candidate (ii), seeds 9001–9007):
  - no failure in 16 base runs and all their polish rounds;
  - fit 1: **S = 0.0250**, 8/8 in the window;
  - fit 2: **S = 0.1618**, 8/8 in the window.
- **Dimension test** (step 4, candidate (ii), CPL with Σmν FIXED at 0.06 eV, 9 parameters, **not fit 5**): no failure in 8 base runs or 31 polish rounds (npt = 55). Agreement is poor: −log-post spread 0.0356 and **S = 0.2812** (8/8 in the window). Three starts hit the 5-round cap while still descending, and one stopped on the 0.001 rule 0.0286 above the best.
- **Recommendation** (step 5): freeze (ii) as a polish stage after the amendment's base minimization, with "a failed
  polish round makes the start not converged" as the failure rule, if a procedure must be frozen now. It does not meet
  the fit-2 target of S ≤ 0.1. What the data say would close that gap is stated in step 5, untested.
- **No G1 verdict, no comparison with the certified July values, no fit 3–5.**

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

## Step 1 — the crash: cause found

Scripts `scripts/crash_repro.py` (instrumented cobaya run), `scripts/crash_analyze.py`, `scripts/crash_lagrange.py`
(offline, no likelihood calls). Logs: `logs/diag_D1_repro.log`, `logs/diag_D1_repro.json`, `logs/step1_analyze_D1.log`,
`logs/step1_lagrange.log`, `logs/step1_kopt_D2_D3.log`, `logs/diag_D2_shift0.3.log`, `logs/diag_D3_s2randomstart.log`.

**Reproduction (D1).** The first study's step3A fit-2 s1 round-1 yaml was run unchanged except for the output path and
the `seed` field (2001 → 9001; the start point is fixed, so cobaya draws nothing with it). Instrumentation only
records: a pass-through wrapper on `pybobyqa.solve` logs every objective call, and subclassed/wrapped Py-BOBYQA
methods log trust-region steps, replaced points, geometry steps and the interpolation set. Result: Py-BOBYQA
`EXIT_LINALG_ERROR`, "Singular matrix in mini-model interpolation (main loop)", at evaluation 48, with
f(xmin) = 981.8809292 and the same approximate gradient printed in the first study's log. The reproduction is exact,
which also confirms that the seed field is inert.

**What happened, evaluation by evaluation** (cobaya's scaled coordinates, x0 = the session-2 endpoint = origin):
- 1–45: x0 and Py-BOBYQA's 44 initial points: x0 ± e_i (16 points at distance 1) and 28 "pair" points
  x0 + s_p e_p + s_q e_q (distance √2).
- 46: trust-region step, |d| = 1, f = 981.9146 (worse than f(x0) = 981.8809). ρ reduced 1 → 0.0707.
- 47: trust-region step, |d| = 0.5, f = 981.9104 (worse); it replaced point 40.
- Because 10ρ = 0.707 < √2, Py-BOBYQA ran a geometry-improving step on the point furthest from x_opt: k = 17,
  the (logA, ns) pair point, with radius 0.1414.
- 48: that geometry step evaluated **exactly at x_opt = x0** (scaled x = 0), f = f(x0).

**The interpolation set at the failure:**
- One exact duplicate: points 0 and 17, distance 0.
- No other near-duplicates: the closest distinct pair, one step earlier, was 0.95 apart.
- No collinear set of distinct points is involved. The duplicate gives the 44×44 full-quadratic system a zero row:
  exactly-zero LU pivots at diagonal numbers 39, 42 and 43, smallest singular value 6.5e-17, condition number 4.5e16.
- **Bounds:** none was within the initial trust radius (1.0). The nearest scaled bound was τ_ecf's lower bound,
  7.18 from x0; every other bound was at least 15.04 away (τ_ecf's upper bound). Not involved
  (`logs/step1_analyze_D1.log`).

**Why the geometry step returned x_opt** (`logs/step1_lagrange.log`). Rebuilding Py-BOBYQA's own `Model` from the
recorded points and calling its `lagrange_polynomial(17)`:
- the Lagrange polynomial of point 17 has value 0 and **gradient exactly 0** at x_opt;
- it is a pure cross term (Hessian entry −1.0 for (logA, ns); the next largest are −0.035 and −0.013).

Py-BOBYQA's `trsbox_geometry` maximises |L| by running `trsbox`, a truncated conjugate-gradient solver that starts
along −g, on +L and on −L. With g = 0 both return a zero step (norms 0.000), so the "geometry step" is x_opt itself,
although |L| ≥ 0.010 was available in that ball.

**Why it is generic, and what restarting at an endpoint has to do with it:**
- In Py-BOBYQA's coordinate-direction initial set, with x_opt still at x0, every pair point's Lagrange polynomial
  has zero gradient at x0:
  - npt = (n+1)(n+2)/2: exactly 0, for all 28 pair points;
  - npt = (n+1)(n+2)/2 − 1: at most 1.6e-17, for all 27 pair points (numerically zero);
  - npt = 2n+1 (cobaya's default): no pair points; coordinate-point gradients are 0.5.
- The pair points are also the furthest from x0 (√2 vs 1), so they are the first targets of a geometry step.
- The trap therefore needs only two things: npt > 2n+1, and no evaluation improving on f(x0) before the first
  geometry step.
- **Restarting exactly at a converged endpoint makes the second condition the normal case:** in D1 no evaluation
  ever beat f(x0).
- Two controls, each capped at 100 evaluations:
  - **D2:** the same endpoint shifted by 0.3 conditional widths (fixed ±1 pattern). The first trust-region step
    (evaluation 46) improved f, and x_opt moved. 19 geometry steps followed, none at x_opt, and the run reached the
    cap with no linear-algebra error.
  - **D3:** session 2's original random start for s1 (non-endpoint). It improved at evaluation 4. 13 geometry steps,
    cap reached, no error.
- **Scaling:** cobaya's diagonal scaling only sets the radius-1 geometry. The zero gradient is structural, the same
  at any scale.
- **The general reason** (offline checks `scripts/randinit_offline_check.py` and `…check2.py`, on a quadratic
  stand-in; logs `logs/step2_c4_offline_check*.log`):
  - Py-BOBYQA's initial sets contain x0 and antipodal pairs x0 ± δv_i along a basis.
  - Any quadratic that vanishes at x0 and at x0 ± δv_i has zero odd part along every v_i, so its gradient at x0 is
    zero.
  - So every initial point outside those 2n+1 has a zero-gradient Lagrange polynomial at x0, for coordinate *and*
    orthogonal random directions alike. Measured: all 28 of them, |grad| ≤ 5.2e-15.
  - Py-BOBYQA's non-orthogonal random directions (`init.random_directions_make_orthogonal: False`) contain no
    antipodal pairs. There, every initial Lagrange gradient is ≥ 0.39, and with numpy's global RNG seeded the run is
    bitwise deterministic.

**Not reproduced here:** the fit-1 crashes at evaluation 37, and the soft-restart variant's "Error when calculating
geometry-improving step". Py-BOBYQA raises the latter when the Lagrange model contains NaN/inf, which a singular
system would produce. Both are consistent with this mechanism, but neither was re-run.

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

Generated by `scripts/tables2.py summary` (`logs/tables_step2_summary.log`, generated from the final logs at 2026-11-24T05:29:07Z). Columns:
- **failed:** starts with a failed round;
- **result:** starts that produced a result;
- **no result:** starts that hit the new-round deadline, were stopped by me during a round, or were still running;
- **spread** and **S:** over the starts with a result, at their final round;
- **evaluations:** Py-BOBYQA `nf` or scipy `nfev`, summed over completed and failed rounds; a round still running counts 0;
- **wall min:** under the load described above.

{{FILE:logs/tables_step2_summary.log}}

**What the table shows.**
- **(a) no failed round: met by every candidate in step 2.**
  - None of the 64 start-procedures (4 candidates × 16 starts) had a failed round.
  - Every completed Py-BOBYQA round ended "Success: rho has reached rhoend"; every Powell round ended with scipy
    `success`.
  - (iii)'s figures are partial: 6 of its 16 starts produced no result (see Notes). None of its 16 completed rounds failed.
- **(b) all 8 starts agree with S ≤ 0.1: met by no candidate.**
  - **Fit 1, met by all three Py-BOBYQA candidates:** S = 0.0205 for (i), 0.0159 for (ii), 0.0105 for (iv), with
    −log-post spread ≤ 1.0e-4.
  - **Fit 2, missed by every candidate:**
    - (ii) came closest, with S = 0.1994 and spread 0.00523;
    - (i): S = 0.2416, spread 0.00884;
    - (iv): S 0.4262, with spread 0.0195. The range runs from s0, which stalled in round 1 at 981.88646 (total χ²
      1993.9534), to s7, which hit the 5-round cap at 981.88012 (total χ² 1994.3796) while still gaining 0.0012 in
      its last round;
    - (iii): S 0.5372, over the 5 of 8 starts that produced a result.
- **What limits fit 2 in every candidate: the 0.001 per-round stop rule ends starts while they still disagree.**
  - Fit-2 rounds keep "succeeding" (ρ reaches `rhoend`). Starts that ended on the 0.001 rule had last-round gains of
    0–0.0008, while lying up to 0.0088 (i), 0.0026 (ii) and 0.0195 (iv) above that candidate's best start
    (`logs/stop_analysis.log`). Example: (ii) s6 went 981.86987 → 981.86966 and stopped, 0.0026 above (ii)'s best.
  - Starts that hit the 5-round cap instead ((ii) s0; (iv) s5, s7) were still gaining 0.0012–0.0014 per round, at
    0.0052–0.0131 above the best.
  - Agreement in −log post must also be much tighter for fit 2 than for fit 1. Under (ii), s2, s3 and s5 agree to
    8e-5 in −log post (981.86710–981.86718), yet their total χ² spans 1994.1415–1994.1772, i.e. 0.036.
  - Under (ii) and (iv), the start from the certified July point (s0) ended furthest from the best start:
    - (ii) s0 used all 5 rounds and was still gaining 0.0012 per round, 0.0052 above (ii)'s best;
    - (iv) s0 stopped after round 1, 0.0195 above (iv)'s best.
    - Under (i), s0 ended 0.0043 above the best, behind s7 (0.0088) and s1 (0.0068) (`logs/stop_analysis.log`).
- **Powell (iii) can make a point worse, and then stops.**
  - In fit 2, 5 of its 7 completed rounds ended *above* their start points, with gains of −0.0008, −0.0016, −0.0028,
    −0.0040 and −0.0048 (`logs/powell_rounds.log`). In fit 1, none did.
  - Cause, read from scipy 1.14.1 `optimize/_optimize.py`: with finite bounds, `_linesearch_powell` minimises
    along each direction with `_minimize_scalar_bounded` over the whole feasible segment. α = 0 is never a candidate
    there, and the result replaces the current point unconditionally. The test `2·(fx − fval) ≤ ftol·(…)` is then
    met at once when fval > fx.
  - It is also the costliest: 9 completed fit-1 rounds took 190–2155 evaluations each, 8011 in total against 1084 for (ii); 7 completed fit-2 rounds took 101–1680 each (`logs/powell_rounds.log`); and two fit-2 rounds were still running 2 h 40 min after launch when I stopped them.
- **Cost of the Py-BOBYQA candidates:**
  - **Fit 1:** 1084 (ii), 1420 (i) and 1428 (iv) evaluations over 8 starts. Per start: 73–194, 108–222 and 108–223.
  - **Fit 2:** 2318 (ii) and 2882 (i) evaluations; per start 186–495 and 266–492.
  - **Per-round cost:**
    - npt = (n+1)(n+2)/2 needs 45 points before its first step (36 for fit 1). A fit-2 round cost 90–227 evaluations
      under (ii), 132–248 under (i) and 135–280 under (iv) (`logs/nf_per_round.log`);
    - with `rhobeg` 0.1 a fit-1 round is somewhat cheaper than with 1.0: 71–122 evaluations vs 103–119 (i) and
      107–113 (iv).

### Step 2 tables

Cell = −log post / total χ² / τ-prior term (2 × `minuslogprior__tau_prior`). Round 0 shows −log post only, as read from
the starting endpoint. `=`: start already stopped. `!`: start failed in or before this round (excluded). `...`: still
running, or stopped by me, at the time the table was generated. Evals and min are per start over all its rounds; min =
wall minutes under the load described above.

{{FILE:logs/tables_step2_c1.log}}

{{FILE:logs/tables_step2_c2.log}}

{{FILE:logs/tables_step2_c3.log}}

{{FILE:logs/tables_step2_c4.log}}

## Step 3 — end-to-end test of (ii) on fits 1 and 2, from fresh starts

**Procedure.**
- **Base minimization:** exactly `AMENDMENT_TIER2_MINIMIZER.md` §2 (`scripts/make_yamls2.py`, `scripts/base_run.py`):
  - 8 starts; s0 = the certified July best fit; s1–s7 drawn by cobaya with **seeds 9001–9007** from the §2.3
    start-point distributions;
  - bobyqa, `rhoend` 0.005, default npt, `rhobeg` 1.0, `ignore_prior: False`, §2.3 covmats, `best_of: 1`.
  - These yamls differ from session 2's only in `seed` and `output` (`logs/yaml_diff_vs_session2.log`: 16 files, 32
    changed lines).
- **Polish:** candidate (ii) from each start's base endpoint, at full double precision, with the step-2 round and stop
  rule (`logs/step34_launch.log`). Tag `e2e`.
- **S and the window:** S is max − min total χ² over the starts that produce a result. "In window" applies
  `AMENDMENT_TIER2_MINIMIZER.md` §2.4 for reporting only: −log post within 0.25 of the fit's best.

**Result.**

{{FILE:logs/tables_step3_summary.log}}

- **Failures:** none. All 16 base runs converged (`Run 1/1 converged`, Py-BOBYQA `EXIT_SUCCESS`), and no polish round
  failed (`EXIT_SUCCESS` in every round).
- **Fit 1:**
  - all 8 starts in the window;
  - **S = 0.0250** (total χ² 2005.4233–2005.4483);
  - −log-post spread 0.00012;
  - 1–2 polish rounds per start.
- **Fit 2:**
  - all 8 starts in the window;
  - **S = 0.1618** (total χ² 1994.0816–1994.2434);
  - −log-post spread 0.00241;
  - 1–5 polish rounds per start.
  - **Above the 0.1 target.** The same pattern as step 2: every start ended on the 0.001 rule (s6 only in its 5th
    round), with final −log post up to 0.0024 above the best start (s2, 981.86703) (`logs/stop_analysis.log`).
- **What the polish added over the base run alone** (`logs/tables_step3_base.log`):
  - fit 1: base S = 0.4371, polished 0.0250;
  - fit 2: base S in window = 0.9975 with 7/8 in the window (s2 was 0.3162 above the best), polished 0.1618 with 8/8.
- **Reproducibility check:** the base s0 runs start from the certified point with the same settings as session 2's
  s0, and reproduced session 2's s0 endpoints exactly: fit 1 986.0182 / 2005.5291, fit 2 981.8865 / 1993.9537.
- **Cost** (`logs/cost_step3.log`), base + polish:
  - **fit 1:** 1667 + 981 = 2648 evaluations, 257–426 per start;
  - **fit 2:** 3147 + 2370 = 5517 evaluations, 457–918 per start.
  - Wall times are in the tables; they are load-dependent.

**Base runs** (`scripts/tables2.py base`, `logs/tables_step3_base.log`):

{{FILE:logs/tables_step3_base.log}}

**Polish rounds** (`logs/tables_step3_polish.log`). Round 0 = the base endpoint.

{{FILE:logs/tables_step3_polish.log}}

## Step 4 — dimension test of (ii) on CPL with Σmν FIXED at 0.06 eV (this is NOT fit 5)

**This is not fit 5.**
- The model is `fullplanck/cpl_full.yaml` as shipped: w0waCDM (PPF), Σmν fixed at 0.06 eV in the theory block.
- It has 9 sampled parameters (logA, ns, H0, ombh2, omch2, tau, A_planck, w, wa).
- Fit 5 frees Σmν. No model with free Σmν was built or run.

**Procedure.** As step 3:
- base minimization with s0 = certified `fullplanck/chains/cpl.minimum.txt` and s1–s7 seeds 9001–9007 (§2.3
  distributions for w and wa included);
- covmat: `cpl.covmat` (§2.3);
- then the (ii) polish (npt = 55, `rhobeg` 0.1). Tag `cpl`.

**Result (CPL, Σmν fixed; not fit 5).**

{{FILE:logs/tables_step4_summary.log}}

- **Failures:** none.
  - All 8 base runs converged.
  - All 31 polish rounds ended "Success: rho has reached rhoend". Full npt here is 55 interpolation points.
  - So (ii) did not crash in 9 dimensions.
- **Agreement: poor.**
  - −log-post spread 0.0356; **S = 0.2812** (total χ² 1996.4597–1996.7409); 8/8 in the window.
  - Polishing improved on the base runs (base: spread 0.0750, S = 0.7107), but the starts did not converge together:
    - s5, s6 and s7 hit the 5-round cap while still gaining 0.0012–0.0079 per round;
    - s4 stopped on the 0.001 rule 0.0286 above the best start (s2, 982.78839).
  - In 9 dimensions, then, both the 0.001 per-round rule and the 5-round cap bind well before agreement.
- **Cost** (`logs/cost_step4.log`): base 2573 + polish 4419 = 6992 evaluations, 428–1182 per start. Polish: 2–5 rounds
  and 320–794 evaluations per start.

**Base runs** (`logs/tables_step4_base.log`):

{{FILE:logs/tables_step4_base.log}}

**Polish rounds** (`logs/tables_step4_polish.log`). Round 0 = the base endpoint.

{{FILE:logs/tables_step4_polish.log}}

## Step 5 — recommendation

**Plain statement: no candidate met (a) and (b).**
- All four met (a) in step 2: none of the 64 start-procedures had a failed round. (iii) is partial: 6 of its 16 starts produced no result, but none of its 16 completed rounds failed.
- None met (b), because on fit 2 none brought all 8 starts within S ≤ 0.1. The closest was (ii), with S = 0.1994.
- From fresh starts (step 3), (ii) gave fit-2 S = 0.1618.

**Procedure I would freeze, if a procedure must be frozen now: candidate (ii), as a polish stage after the
amendment's base minimization.** It is the best measured option under the selection rule written before the
candidates ran:
- no failure anywhere (ii) ran in this study (24 base runs, and 97 polish rounds of (ii) over 40 start-procedures: 16 in step 2, 16 in step 3, 8 in step 4);
- the smallest fit-2 S of the four candidates;
- the fewest fit-1 evaluations.

1. **Base minimization.** Exactly `AMENDMENT_TIER2_MINIMIZER.md` §2:
   - 8 starts: s0 = the certified July best fit; s1–s7 drawn from the §2.3 start-point distributions with the
     official seeds;
   - bobyqa, `rhoend` 0.005, default npt, `rhobeg` 1.0, `ignore_prior: False`, §2.3 covmats, `best_of: 1`;
   - a start whose base run does not converge is "not converged" (§2.4), as now.
2. **Polish round.** cobaya `minimize` started exactly at the start's current endpoint:
   - `ref` = the endpoint at full double precision, passed in-process or from a full-precision dump, not from the
     8–10-digit `.minimum` files;
   - same yaml and covmat, no seed;
   - `override_bobyqa: {rhoend: 0.005, npt: (n+1)(n+2)/2, rhobeg: 0.1}`. npt = 36 for fit 1, 45 for fits 2 and 3, 55
     for fit 4 and for CPL (9 parameters), and 66 for fit 5 (10 parameters).
3. **Stopping rule.** Repeat item 2 from the new endpoint until a round lowers −log posterior by less than 0.001, with
   at most 5 rounds.
4. **Result and failure rule.**
   - The start's result is its last polish round.
   - **If any polish round fails, the start is "not converged" (§2.4).** A round fails when Py-BOBYQA exits with any
     flag other than `EXIT_SUCCESS`, so cobaya raises `Minimization failed!`, or on any other exception.
   - A "not converged" start cannot be selected, does not enter S, and counts against the 4-of-8 rule. It is reported
     with its last completed round.
   - No retry, no substitute start, no fallback setting.
   - Selection (§1), the window and the 4-of-8 rule (§2.4), S and the spread guard (§3), and every threshold stay
     unchanged.

**Measured cost (this study, `OMP_NUM_THREADS=1`, one process per start, heavy load; evaluations are the
load-independent cost):**
- **Fit 1 (step 3, 7 parameters):** base 50–310 evaluations, polish 71–243 (1–2 rounds); per-start total 257–426;
  2648 for all 8 starts (`logs/cost_step3.log`).
- **Fit 2 (step 3, 8 parameters):** base 211–539, polish 95–500 (1–5 rounds); per-start total 457–918; 5517 for all 8.
- **CPL (step 4, 9 parameters):** base 57–427, polish 320–794 (2–5 rounds); per-start total 428–1182; 6992 for all 8
  (`logs/cost_step4.log`).
- **One (ii) polish round** costs 71–169 evaluations for fit 1, 90–227 for fit 2 and 111–225 for CPL, over steps 2–4
  (`logs/nf_per_round.log`).
- **Wall time per start in this session** (load-dependent):
  - base: 9.2–44.8 min (fit 1), 46.8–90.0 min (fit 2), 14.6–72.2 min (CPL);
  - polish: 6.5–19.3, 12.7–43.0 and 31.6–53.9 min.
  - Per-evaluation time at an official run's load (16 processes on 16 cores) was not measured here.

**Caveats that come with this recommendation:**
- **It does not meet this brief's fit-2 target.** Fit-2 S was 0.1994 (step 2) and 0.1618 (step 3), above 0.1. Both
  are below the amendment's G1 spread guard of 0.5, but that is a fact about the guard, not a pass of anything.
- **Its crash avoidance is empirical, not structural.**
  - Why (ii) avoids the trap at the first ρ reduction, from Py-BOBYQA 1.5.0's source: after an unsuccessful step it
    fixes geometry only for points farther than max(2Δ, 10ρ) from x_opt (`solver.py`, line 588). With `rhobeg` 0.1,
    the first reduction (`reduce_rho`) gives ρ = √20 × 0.005 = 0.0224. So 10ρ = 0.224 exceeds the √2 × 0.1 = 0.141
    distance of the initial pair points, and no geometry step targets them. With `rhobeg` 1.0, ρ becomes 0.0707 and
    10ρ = 0.707 < √2, which is the D1 sequence.
  - At ρ = `rhoend` that protection is gone. A geometry step can still target an initial pair point if no evaluation
    has improved on the start by then.
  - That did not happen in any of the 97 (ii) rounds run here, but it is not ruled out.
  - (iv)'s initialisation removes the cause structurally (no zero-gradient Lagrange polynomials at x0). The
    combination of (ii) and (iv), `rhobeg` 0.1 with random non-orthogonal directions, was not tested.
- **Fits 3–5 were not tested.**
  - The dimension test was CPL with Σmν fixed (9 parameters, npt 55); see step 4.
  - Fit 4 has 9 sampled parameters, like this CPL test. Fit 5 has 10.

**What the data say would close the fit-2 gap (not tested; for the owner's decision):**
- Fit-2 starts stop on the 0.001 per-round rule while still up to 0.0026 ((ii)), 0.0088 ((i)) or 0.0195 ((iv))
  above the best start; in CPL, 0.0286. Under (ii), even 8e-5 agreement in −log post left 0.036 in total χ².
- So a fit-2 S ≤ 0.1 needs the polish to continue until starts agree to about 1e-4 in −log post. Two ways to get
  there:
  - a per-round stop threshold of about 1e-4 instead of 0.001, with a larger round cap;
  - or a stop rule based on agreement across starts.
- Neither was run here, so neither is offered as tested.

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
  - Check against the final values: the decision stands (`logs/decision_overturn_check.log`):
    - (A) (ii) had no failed round;
    - (B) (ii)'s fit-2 s0 ended at total χ² 1994.0417, inside the stated range, giving (ii) a final fit-2 S of 0.1994;
    - (C) (iv) ended at fit-2 S = 0.4262 (`logs/tables_step2_summary.log`), above 0.1994;
    - (D) (i) ended at 0.2416, and (iii)'s fit-2 S over its finished starts was already 0.5372.
    - The decision used the values of the 04:08Z poll. (ii)'s last fit-2 start had in fact finished at 04:09:12Z, 11 s
      before the decision was logged; its final value is the one checked in (B).
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
- **(iii) Powell is partial.**
  - Fit-1 s3, s5 and s7, and fit-2 s3, each completed one round with a gain ≥ 0.001. They then met the 04:30Z deadline
    for new rounds, so they have no result.
  - Fit-2 s2 and s5 were still in their first Powell round 2 h 40 min after launch. I stopped them (SIGTERM, exit
    143) at 05:27:49Z to stay within the 4-hour cap (`logs/powell_stop.log`).
  - No evaluation count is logged for those two rounds, because the driver records counts only when a round returns.
  - (iii)'s fit-2 failure of (b) was already settled by its finished starts (S = 0.5372 over 5).
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
- **Wall time.** Session start 02:38:07Z (`logs/session_clock.log`). The last fit process ended at 05:27:49Z (the stopped Powell starts). The closing checks and this append followed (`logs/session_end.log`); the 4-hour cap was 06:38:07Z.
