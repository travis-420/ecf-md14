

---

# Exploratory minimizer study 2 (not a gate attempt) — executed 2026-11-24, 02:38–05:30 UTC

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

| candidate | fit | starts with a failed round | starts producing a result | no result: deadline / stopped / running | −log post spread (final) | **S** (final, starts with a result) | in window (≤0.25) | evaluations: total (per start) | wall min per start |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| c1 | fit1 | 0/8 | 8/8 | 0 | 0.00010 | **0.0205** | 8/8 | 1420 (108–222) | 18.8–34.5 |
| c1 | fit2 | 0/8 | 8/8 | 0 | 0.00884 | **0.2416** | 8/8 | 2882 (266–492) | 53.9–82.0 |
| c2 | fit1 | 0/8 | 8/8 | 0 | 0.00009 | **0.0159** | 8/8 | 1084 (73–194) | 12.8–31.1 |
| c2 | fit2 | 0/8 | 8/8 | 0 | 0.00523 | **0.1994** | 8/8 | 2318 (186–495) | 41.7–81.3 |
| c3 | fit1 | 0/8 | 5/8 | 3 | 0.00135 | **0.1038** | 5/8 | 8011 (190–2155) | 24.6–135.7 |
| c3 | fit2 | 0/8 | 5/8 | 3 | 0.02646 | **0.5372** | 5/8 | 3169 (0–1680) | 23.0–159.9 |
| c4 | fit1 | 0/8 | 8/8 | 0 | 0.00003 | **0.0105** | 8/8 | 1428 (108–223) | 11.1–19.5 |
| c4 | fit2 | 0/8 | 8/8 | 0 | 0.01946 | **0.4262** | 8/8 | 3694 (136–770) | 19.1–70.8 |

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

**c1, Fit 1 (ΛCDM, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | outcome | evals | min |
|---|---|---|---|---|---|---|
| s0 | 986.01818 | 986.00533 / 2005.4409 / 0.8323 | 986.00533 / 2005.4409 / 0.8323 | round 2 gain 0.000000 < 0.001 → stop | 221 | 34.5 |
| s1 | 986.00698 | 986.00536 / 2005.4433 / 0.8305 | 986.00536 / 2005.4433 / 0.8305 | round 2 gain 0.000000 < 0.001 → stop | 215 | 33.6 |
| s2 | 986.00589 | 986.00543 / 2005.4511 / 0.8186 | = | round 1 gain 0.000464 < 0.001 → stop | 108 | 18.9 |
| s3 | 986.02498 | 986.00541 / 2005.4474 / 0.8264 | 986.00536 / 2005.4489 / 0.8256 | round 2 gain 0.000045 < 0.001 → stop | 220 | 34.4 |
| s4 | 986.00562 | 986.00542 / 2005.4306 / 0.8426 | = | round 1 gain 0.000202 < 0.001 → stop | 108 | 18.8 |
| s5 | 986.00690 | 986.00542 / 2005.4486 / 0.8226 | 986.00542 / 2005.4486 / 0.8226 | round 2 gain 0.000000 < 0.001 → stop | 218 | 34.0 |
| s6 | 986.00597 | 986.00540 / 2005.4395 / 0.8328 | = | round 1 gain 0.000572 < 0.001 → stop | 108 | 18.9 |
| s7 | 986.01012 | 986.00540 / 2005.4439 / 0.8286 | 986.00540 / 2005.4439 / 0.8286 | round 2 gain 0.000000 < 0.001 → stop | 222 | 34.5 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.00010 | 0.00010 | | | |
| **S** = max − min total χ² | n/a | **0.0205** | **0.0205** | | | |
| lowest −log post start: its total χ² | n/a | s0: 2005.4409 | s0: 2005.4409 | | | |
| evaluations in this round | — | 897 (8 starts ran it) | 523 (5 starts ran it) | | | |

SUMMARY c1 fit1_lcdm_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 1420, per start 108–222; wall per start (min) 18.8–34.5; final −log post spread 0.00010; S (all result starts) 0.0205; in window (≤0.25) 8/8, S in window 0.0205; lowest −log post s0 986.00533 with total χ² 2005.4409; total χ² range 2005.4306–2005.4511

**c1, Fit 2 (ECF, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | round 3 | outcome | evals | min |
|---|---|---|---|---|---|---|---|
| s0 | 981.88652 | 981.87114 / 1994.0805 / 0.4838 | 981.87110 / 1994.0827 / 0.4820 | = | round 2 gain 0.000047 < 0.001 → stop | 267 | 54.0 |
| s1 | 981.88093 | 981.87423 / 1994.3072 / 0.2612 | 981.87361 / 1994.3069 / 0.2651 | = | round 2 gain 0.000613 < 0.001 → stop | 308 | 59.1 |
| s2 | 981.92850 | 981.86706 / 1994.1588 / 0.4040 | 981.86692 / 1994.1580 / 0.4032 | = | round 2 gain 0.000137 < 0.001 → stop | 381 | 70.5 |
| s3 | 982.07342 | 981.87411 / 1994.0327 / 0.5383 | 981.86693 / 1994.1644 / 0.3999 | 981.86683 / 1994.1645 / 0.4003 | round 3 gain 0.000105 < 0.001 → stop | 492 | 82.0 |
| s4 | 981.87483 | 981.86945 / 1994.0921 / 0.4637 | 981.86815 / 1994.2271 / 0.3406 | 981.86794 / 1994.2238 / 0.3431 | round 3 gain 0.000205 < 0.001 → stop | 416 | 74.6 |
| s5 | 981.94752 | 981.86785 / 1994.2180 / 0.3516 | 981.86785 / 1994.2180 / 0.3516 | = | round 2 gain 0.000000 < 0.001 → stop | 323 | 61.3 |
| s6 | 981.87294 | 981.87170 / 1994.0912 / 0.4540 | 981.87099 / 1994.0948 / 0.4513 | = | round 2 gain 0.000716 < 0.001 → stop | 266 | 53.9 |
| s7 | 981.91492 | 981.87858 / 1994.3442 / 0.2333 | 981.87594 / 1994.3263 / 0.2489 | 981.87567 / 1994.3243 / 0.2503 | round 3 gain 0.000276 < 0.001 → stop | 429 | 76.1 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.01152 | 0.00902 | 0.00884 | | | |
| **S** = max − min total χ² | n/a | **0.3115** | **0.2436** | **0.2416** | | | |
| lowest −log post start: its total χ² | n/a | s2: 1994.1588 | s2: 1994.1580 | s3: 1994.1645 | | | |
| evaluations in this round | — | 1400 (8 starts ran it) | 1082 (8 starts ran it) | 400 (3 starts ran it) | | | |

SUMMARY c1 fit2_ecf_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 2882, per start 266–492; wall per start (min) 53.9–82.0; final −log post spread 0.00884; S (all result starts) 0.2416; in window (≤0.25) 8/8, S in window 0.2416; lowest −log post s3 981.86683 with total χ² 1994.1645; total χ² range 1994.0827–1994.3243

**c2, Fit 1 (ΛCDM, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | outcome | evals | min |
|---|---|---|---|---|---|---|
| s0 | 986.01818 | 986.00540 / 2005.4492 / 0.8233 | 986.00533 / 2005.4493 / 0.8231 | round 2 gain 0.000077 < 0.001 → stop | 194 | 31.1 |
| s1 | 986.00698 | 986.00543 / 2005.4537 / 0.8196 | 986.00540 / 2005.4430 / 0.8299 | round 2 gain 0.000031 < 0.001 → stop | 152 | 25.2 |
| s2 | 986.00589 | 986.00540 / 2005.4422 / 0.8302 | = | round 1 gain 0.000496 < 0.001 → stop | 75 | 13.2 |
| s3 | 986.02498 | 986.00534 / 2005.4452 / 0.8301 | 986.00534 / 2005.4452 / 0.8301 | round 2 gain 0.000000 < 0.001 → stop | 183 | 29.7 |
| s4 | 986.00562 | 986.00541 / 2005.4407 / 0.8317 | = | round 1 gain 0.000217 < 0.001 → stop | 73 | 12.8 |
| s5 | 986.00690 | 986.00533 / 2005.4416 / 0.8332 | 986.00533 / 2005.4416 / 0.8332 | round 2 gain 0.000000 < 0.001 → stop | 147 | 24.4 |
| s6 | 986.00597 | 986.00542 / 2005.4335 / 0.8370 | = | round 1 gain 0.000553 < 0.001 → stop | 78 | 13.6 |
| s7 | 986.01012 | 986.00540 / 2005.4442 / 0.8278 | 986.00540 / 2005.4445 / 0.8272 | round 2 gain 0.000002 < 0.001 → stop | 182 | 29.5 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.00010 | 0.00009 | | | |
| **S** = max − min total χ² | n/a | **0.0202** | **0.0159** | | | |
| lowest −log post start: its total χ² | n/a | s5: 2005.4416 | s0: 2005.4493 | | | |
| evaluations in this round | — | 726 (8 starts ran it) | 358 (5 starts ran it) | | | |

SUMMARY c2 fit1_lcdm_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 1084, per start 73–194; wall per start (min) 12.8–31.1; final −log post spread 0.00009; S (all result starts) 0.0159; in window (≤0.25) 8/8, S in window 0.0159; lowest −log post s0 986.00533 with total χ² 2005.4493; total χ² range 2005.4335–2005.4493

**c2, Fit 2 (ECF, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | round 3 | round 4 | round 5 | outcome | evals | min |
|---|---|---|---|---|---|---|---|---|---|
| s0 | 981.88652 | 981.88283 / 1993.9743 / 0.6144 | 981.87966 / 1993.9935 / 0.5865 | 981.87794 / 1994.0074 / 0.5700 | 981.87350 / 1994.0323 / 0.5417 | 981.87233 / 1994.0417 / 0.5266 | 5-round cap | 495 | 81.3 |
| s1 | 981.88093 | 981.86879 / 1994.2434 / 0.3299 | 981.86824 / 1994.2304 / 0.3418 | = | = | = | round 2 gain 0.000545 < 0.001 → stop | 213 | 46.2 |
| s2 | 981.92850 | 981.86711 / 1994.1772 / 0.3861 | 981.86711 / 1994.1772 / 0.3861 | = | = | = | round 2 gain 0.000000 < 0.001 → stop | 235 | 49.5 |
| s3 | 982.07342 | 981.86732 / 1994.1388 / 0.4222 | 981.86710 / 1994.1415 / 0.4199 | = | = | = | round 2 gain 0.000214 < 0.001 → stop | 318 | 60.4 |
| s4 | 981.87483 | 981.86823 / 1994.1327 / 0.4243 | 981.86745 / 1994.1365 / 0.4259 | = | = | = | round 2 gain 0.000771 < 0.001 → stop | 224 | 47.9 |
| s5 | 981.94752 | 981.89368 / 1994.4626 / 0.1632 | 981.86718 / 1994.1741 / 0.3890 | 981.86718 / 1994.1741 / 0.3889 | = | = | round 3 gain 0.000002 < 0.001 → stop | 385 | 70.3 |
| s6 | 981.87294 | 981.86987 / 1994.1046 / 0.4574 | 981.86966 / 1994.1054 / 0.4570 | = | = | = | round 2 gain 0.000209 < 0.001 → stop | 186 | 41.7 |
| s7 | 981.91492 | 981.86917 / 1994.2545 / 0.3190 | 981.86851 / 1994.2412 / 0.3310 | = | = | = | round 2 gain 0.000657 < 0.001 → stop | 262 | 53.2 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.02658 | 0.01256 | 0.01084 | 0.00640 | 0.00523 | | | |
| **S** = max − min total χ² | n/a | **0.4883** | **0.2476** | **0.2337** | **0.2088** | **0.1994** | | | |
| lowest −log post start: its total χ² | n/a | s2: 1994.1772 | s3: 1994.1415 | s3: 1994.1415 | s3: 1994.1415 | s3: 1994.1415 | | | |
| evaluations in this round | — | 1146 (8 starts ran it) | 781 (8 starts ran it) | 181 (2 starts ran it) | 114 (1 starts ran it) | 96 (1 starts ran it) | | | |

SUMMARY c2 fit2_ecf_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 2318, per start 186–495; wall per start (min) 41.7–81.3; final −log post spread 0.00523; S (all result starts) 0.1994; in window (≤0.25) 8/8, S in window 0.1994; lowest −log post s3 981.86710 with total χ² 1994.1415; total χ² range 1994.0417–1994.2412

**c3, Fit 1 (ΛCDM, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | outcome | evals | min |
|---|---|---|---|---|---|---|
| s0 | 986.01818 | 986.00647 / 2005.5124 / 0.7562 | 986.00621 / 2005.5097 / 0.7753 | round 2 gain 0.000259 < 0.001 → stop | 1258 | 102.0 |
| s1 | 986.00698 | 986.00689 / 2005.4611 / 0.8080 | = | round 1 gain 0.000091 < 0.001 → stop | 190 | 24.6 |
| s2 | 986.00589 | 986.00554 / 2005.4684 / 0.8044 | = | round 1 gain 0.000355 < 0.001 → stop | 976 | 87.6 |
| s3 | 986.02498 | 986.00541 / 2005.4466 / 0.8271 | = | deadline: next round not started | 2155 | 135.7 |
| s4 | 986.00562 | 986.00559 / 2005.4060 / 0.8630 | = | round 1 gain 0.000031 < 0.001 → stop | 269 | 31.5 |
| s5 | 986.00690 | 986.00546 / 2005.4512 / 0.8187 | = | deadline: next round not started | 1280 | 106.5 |
| s6 | 986.00597 | 986.00576 / 2005.4564 / 0.8072 | = | round 1 gain 0.000208 < 0.001 → stop | 259 | 31.6 |
| s7 | 986.01012 | 986.00751 / 2005.3415 / 0.9369 | = | deadline: next round not started | 1624 | 117.3 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.00210 | 0.00210 | | | |
| **S** = max − min total χ² | n/a | **0.1709** | **0.1682** | | | |
| lowest −log post start: its total χ² | n/a | s3: 2005.4466 | s3: 2005.4466 | | | |
| evaluations in this round | — | 7498 (8 starts ran it) | 513 (1 starts ran it) | | | |

SUMMARY c3 fit1_lcdm_mnufixed: starts failed (crash) 0/8; starts producing a result 5/8; still running/not finished 3; evaluations total 8011, per start 190–2155; wall per start (min) 24.6–135.7; final −log post spread 0.00135; S (all result starts) 0.1038; in window (≤0.25) 5/8, S in window 0.1038; lowest −log post s2 986.00554 with total χ² 2005.4684; total χ² range 2005.4060–2005.5097

**c3, Fit 2 (ECF, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | outcome | evals | min |
|---|---|---|---|---|---|---|
| s0 | 981.88652 | 981.89048 / 1993.9652 / 0.6341 | = | round 1 gain -0.003955 < 0.001 → stop | 426 | 63.6 |
| s1 | 981.88093 | 981.88170 / 1994.3184 / 0.2452 | = | round 1 gain -0.000770 < 0.001 → stop | 121 | 26.8 |
| s2 | 981.92850 | ... | ... | operator-stopped during a round (EXIT=143); no result for that round | 0 | 159.9 |
| s3 | 982.07342 | 981.86751 / 1994.1985 / 0.3683 | = | deadline: next round not started | 1680 | 149.7 |
| s4 | 981.87483 | 981.87762 / 1994.1158 / 0.4457 | = | round 1 gain -0.002792 < 0.001 → stop | 105 | 23.0 |
| s5 | 981.94752 | ... | ... | operator-stopped during a round (EXIT=143); no result for that round | 0 | 159.9 |
| s6 | 981.87294 | 981.87775 / 1994.0991 / 0.4547 | = | round 1 gain -0.004817 < 0.001 → stop | 108 | 23.7 |
| s7 | 981.91492 | 981.90243 / 1994.5006 / 0.1625 | 981.90407 / 1994.5024 / 0.1638 | round 2 gain -0.001641 < 0.001 → stop | 729 | 100.4 |
| starts entering spread and S (completed, not failed) | 0/8 | 6/8 | 6/8 | | | |
| spread of −log post (max − min) | n/a | 0.03492 | 0.03656 | | | |
| **S** = max − min total χ² | n/a | **0.5353** | **0.5372** | | | |
| lowest −log post start: its total χ² | n/a | s3: 1994.1985 | s3: 1994.1985 | | | |
| evaluations in this round | — | 3068 (6 starts ran it) | 101 (1 starts ran it) | | | |

SUMMARY c3 fit2_ecf_mnufixed: starts failed (crash) 0/8; starts producing a result 5/8; still running/not finished 3; evaluations total 3169, per start 0–1680; wall per start (min) 23.0–159.9; final −log post spread 0.02646; S (all result starts) 0.5372; in window (≤0.25) 5/8, S in window 0.5372; lowest −log post s4 981.87762 with total χ² 1994.1158; total χ² range 1993.9652–1994.5024

**c4, Fit 1 (ΛCDM, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | outcome | evals | min |
|---|---|---|---|---|---|---|
| s0 | 986.01818 | 986.00542 / 2005.4452 / 0.8273 | 986.00540 / 2005.4379 / 0.8333 | round 2 gain 0.000021 < 0.001 → stop | 219 | 19.3 |
| s1 | 986.00698 | 986.00540 / 2005.4459 / 0.8262 | 986.00540 / 2005.4459 / 0.8262 | round 2 gain 0.000000 < 0.001 → stop | 215 | 19.1 |
| s2 | 986.00589 | 986.00540 / 2005.4445 / 0.8294 | = | round 1 gain 0.000487 < 0.001 → stop | 110 | 11.2 |
| s3 | 986.02498 | 986.00539 / 2005.4360 / 0.8369 | 986.00539 / 2005.4360 / 0.8369 | round 2 gain 0.000000 < 0.001 → stop | 222 | 19.5 |
| s4 | 986.00562 | 986.00540 / 2005.4430 / 0.8297 | = | round 1 gain 0.000227 < 0.001 → stop | 111 | 11.3 |
| s5 | 986.00690 | 986.00541 / 2005.4414 / 0.8293 | 986.00541 / 2005.4414 / 0.8293 | round 2 gain 0.000000 < 0.001 → stop | 223 | 19.5 |
| s6 | 986.00597 | 986.00541 / 2005.4465 / 0.8281 | = | round 1 gain 0.000566 < 0.001 → stop | 108 | 11.1 |
| s7 | 986.01012 | 986.00541 / 2005.4430 / 0.8294 | 986.00538 / 2005.4428 / 0.8296 | round 2 gain 0.000025 < 0.001 → stop | 220 | 19.4 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.00003 | 0.00003 | | | |
| **S** = max − min total χ² | n/a | **0.0105** | **0.0105** | | | |
| lowest −log post start: its total χ² | n/a | s3: 2005.4360 | s7: 2005.4428 | | | |
| evaluations in this round | — | 884 (8 starts ran it) | 544 (5 starts ran it) | | | |

SUMMARY c4 fit1_lcdm_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 1428, per start 108–223; wall per start (min) 11.1–19.5; final −log post spread 0.00003; S (all result starts) 0.0105; in window (≤0.25) 8/8, S in window 0.0105; lowest −log post s7 986.00538 with total χ² 2005.4428; total χ² range 2005.4360–2005.4465

**c4, Fit 2 (ECF, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (session-2 endpoint) | round 1 | round 2 | round 3 | round 4 | round 5 | outcome | evals | min |
|---|---|---|---|---|---|---|---|---|---|
| s0 | 981.88652 | 981.88646 / 1993.9534 / 0.6436 | = | = | = | = | round 1 gain 0.000065 < 0.001 → stop | 136 | 19.1 |
| s1 | 981.88093 | 981.87677 / 1994.3092 / 0.2518 | 981.87313 / 1994.3066 / 0.2733 | 981.87234 / 1994.3034 / 0.2779 | = | = | round 3 gain 0.000788 < 0.001 → stop | 425 | 51.1 |
| s2 | 981.92850 | 981.89233 / 1993.8995 / 0.7045 | 981.86709 / 1994.1520 / 0.4123 | 981.86699 / 1994.1519 / 0.4124 | = | = | round 3 gain 0.000096 < 0.001 → stop | 510 | 57.4 |
| s3 | 982.07342 | 981.86985 / 1994.1177 / 0.4396 | 981.86760 / 1994.1253 / 0.4353 | 981.86737 / 1994.1342 / 0.4327 | = | = | round 3 gain 0.000234 < 0.001 → stop | 556 | 60.1 |
| s4 | 981.87483 | 981.86815 / 1994.1174 / 0.4387 | 981.86815 / 1994.1174 / 0.4387 | = | = | = | round 2 gain 0.000000 < 0.001 → stop | 278 | 36.8 |
| s5 | 981.94752 | 981.88468 / 1994.4094 / 0.2018 | 981.87937 / 1994.3662 / 0.2288 | 981.87826 / 1994.3575 / 0.2363 | 981.87561 / 1994.3345 / 0.2547 | 981.87418 / 1994.3209 / 0.2624 | 5-round cap | 770 | 70.8 |
| s6 | 981.87294 | 981.87101 / 1994.0905 / 0.4617 | 981.87035 / 1994.0961 / 0.4584 | = | = | = | round 2 gain 0.000662 < 0.001 → stop | 280 | 37.0 |
| s7 | 981.91492 | 981.89567 / 1994.4532 / 0.1587 | 981.88893 / 1994.4344 / 0.1828 | 981.88444 / 1994.4082 / 0.2014 | 981.88137 / 1994.3836 / 0.2134 | 981.88012 / 1994.3796 / 0.2233 | 5-round cap | 739 | 69.3 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.02752 | 0.02184 | 0.01946 | 0.01946 | 0.01946 | | | |
| **S** = max − min total χ² | n/a | **0.5537** | **0.4810** | **0.4548** | **0.4302** | **0.4262** | | | |
| lowest −log post start: its total χ² | n/a | s4: 1994.1174 | s2: 1994.1520 | s2: 1994.1519 | s2: 1994.1519 | s2: 1994.1519 | | | |
| evaluations in this round | — | 1384 (8 starts ran it) | 1057 (7 starts ran it) | 687 (5 starts ran it) | 286 (2 starts ran it) | 280 (2 starts ran it) | | | |

SUMMARY c4 fit2_ecf_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 3694, per start 136–770; wall per start (min) 19.1–70.8; final −log post spread 0.01946; S (all result starts) 0.4262; in window (≤0.25) 8/8, S in window 0.4262; lowest −log post s2 981.86699 with total χ² 1994.1519; total χ² range 1993.9534–1994.3796

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

| candidate | fit | starts with a failed round | starts producing a result | no result: deadline / stopped / running | −log post spread (final) | **S** (final, starts with a result) | in window (≤0.25) | evaluations: total (per start) | wall min per start |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| e2e | fit1 | 0/8 | 8/8 | 0 | 0.00012 | **0.0250** | 8/8 | 981 (71–243) | 6.5–19.3 |
| e2e | fit2 | 0/8 | 8/8 | 0 | 0.00241 | **0.1618** | 8/8 | 2370 (95–500) | 12.7–43.0 |

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

**base, Fit 1 (ΛCDM, Σmν = 0.06 eV fixed).** AMENDMENT_TIER2_MINIMIZER.md §2 settings, seeds 9000+k.

| start | start point | status | −log post | −log post − best | total χ² | χ²_CMB | χ²_BAO | χ²_SN | τ-prior term | extra | evals | min |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| s0 | certified July best fit (seed 9000, inert) | converged | 986.0182 | 0.0128 | 2005.5291 | 587.4169 | 12.4571 | 1405.6551 | 0.7140 |  | 50 | 9.2 |
| s1 | random, seed 9001 | converged | 986.0055 | 0.0001 | 2005.4358 | 587.1507 | 12.7013 | 1405.5838 | 0.8357 |  | 198 | 32.3 |
| s2 | random, seed 9002 | converged | 986.0072 | 0.0018 | 2005.5406 | 587.2359 | 12.7299 | 1405.5747 | 0.7412 |  | 263 | 39.5 |
| s3 | random, seed 9003 | converged | 986.0311 | 0.0257 | 2005.8569 | 587.6228 | 12.6361 | 1405.5980 | 0.5051 |  | 175 | 29.4 |
| s4 | random, seed 9004 | converged | 986.0062 | 0.0008 | 2005.4368 | 587.0955 | 12.7801 | 1405.5613 | 0.8445 |  | 310 | 44.8 |
| s5 | random, seed 9005 | converged | 986.0058 | 0.0004 | 2005.4439 | 587.1769 | 12.6764 | 1405.5906 | 0.8130 |  | 183 | 30.4 |
| s6 | random, seed 9006 | converged | 986.0054 | 0.0000 | 2005.4403 | 587.1827 | 12.6637 | 1405.5938 | 0.8327 |  | 260 | 39.2 |
| s7 | random, seed 9007 | converged | 986.0058 | 0.0003 | 2005.4198 | 587.1946 | 12.6185 | 1405.6067 | 0.8497 |  | 228 | 35.9 |

SUMMARY base fit1_lcdm_mnufixed: converged 8/8; in window (≤0.25) 8/8; −log post spread 0.02568; S in window 0.4371; S all converged 0.4371; lowest −log post s6 986.00542, total χ² 2005.4403; evaluations 1667 total, 50–310 per start

**base, Fit 2 (ECF, Σmν = 0.06 eV fixed).** AMENDMENT_TIER2_MINIMIZER.md §2 settings, seeds 9000+k.

| start | start point | status | −log post | −log post − best | total χ² | χ²_CMB | χ²_BAO | χ²_SN | τ-prior term | extra | evals | min |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| s0 | certified July best fit (seed 9000, inert) | converged | 981.8865 | 0.0176 | 1993.9537 | 582.0550 | 9.3166 | 1402.5821 | 0.6445 | tau_ecf 2.15362 | 211 | 46.8 |
| s1 | random, seed 9001 | converged | 981.9039 | 0.0349 | 1994.1049 | 582.2729 | 9.2399 | 1402.5920 | 0.3846 | tau_ecf 2.12915 | 225 | 49.0 |
| s2 | random, seed 9002 | converged | 982.1851 | 0.3162 | 1994.8338 | 582.8749 | 9.3816 | 1402.5772 | 0.0004 | tau_ecf 2.16986 | 449 | 79.1 |
| s3 | random, seed 9003 | converged | 981.8743 | 0.0053 | 1994.0296 | 582.1738 | 9.2132 | 1402.6426 | 0.5481 | tau_ecf 2.10086 | 398 | 73.5 |
| s4 | random, seed 9004 | converged | 982.0432 | 0.1743 | 1994.9511 | 583.1031 | 9.2315 | 1402.6165 | 0.0094 | tau_ecf 2.11857 | 481 | 81.7 |
| s5 | random, seed 9005 | converged | 981.8690 | 0.0000 | 1994.1372 | 582.2833 | 9.2200 | 1402.6339 | 0.4008 | tau_ecf 2.10664 | 426 | 76.8 |
| s6 | random, seed 9006 | converged | 981.8785 | 0.0095 | 1994.3522 | 582.4875 | 9.2183 | 1402.6464 | 0.2355 | tau_ecf 2.10103 | 418 | 76.0 |
| s7 | random, seed 9007 | converged | 981.9380 | 0.0690 | 1994.6427 | 582.7409 | 9.3075 | 1402.5942 | 0.1063 | tau_ecf 2.14686 | 539 | 90.0 |

SUMMARY base fit2_ecf_mnufixed: converged 8/8; in window (≤0.25) 7/8; −log post spread 0.31618; S in window 0.9975; S all converged 0.9975; lowest −log post s5 981.86897, total χ² 1994.1372; evaluations 3147 total, 211–539 per start

**Polish rounds** (`logs/tables_step3_polish.log`). Round 0 = the base endpoint.

**e2e, Fit 1 (ΛCDM, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (base endpoint) | round 1 | round 2 | outcome | evals | min |
|---|---|---|---|---|---|---|
| s0 | 986.01818 | 986.00563 / 2005.4780 / 0.7997 | 986.00540 / 2005.4383 / 0.8321 | round 2 gain 0.000234 < 0.001 → stop | 243 | 19.3 |
| s1 | 986.00551 | 986.00540 / 2005.4407 / 0.8300 | = | round 1 gain 0.000114 < 0.001 → stop | 76 | 6.9 |
| s2 | 986.00720 | 986.00548 / 2005.4568 / 0.8166 | 986.00539 / 2005.4415 / 0.8308 | round 2 gain 0.000094 < 0.001 → stop | 163 | 13.7 |
| s3 | 986.03110 | 986.00535 / 2005.4483 / 0.8233 | 986.00535 / 2005.4483 / 0.8233 | round 2 gain 0.000000 < 0.001 → stop | 192 | 15.8 |
| s4 | 986.00622 | 986.00547 / 2005.4233 / 0.8514 | = | round 1 gain 0.000750 < 0.001 → stop | 83 | 7.5 |
| s5 | 986.00580 | 986.00540 / 2005.4392 / 0.8338 | = | round 1 gain 0.000399 < 0.001 → stop | 74 | 6.8 |
| s6 | 986.00542 | 986.00540 / 2005.4399 / 0.8339 | = | round 1 gain 0.000018 < 0.001 → stop | 71 | 6.5 |
| s7 | 986.00576 | 986.00541 / 2005.4447 / 0.8312 | = | round 1 gain 0.000350 < 0.001 → stop | 79 | 7.2 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.00029 | 0.00012 | | | |
| **S** = max − min total χ² | n/a | **0.0547** | **0.0250** | | | |
| lowest −log post start: its total χ² | n/a | s3: 2005.4483 | s3: 2005.4483 | | | |
| evaluations in this round | — | 763 (8 starts ran it) | 218 (3 starts ran it) | | | |

SUMMARY e2e fit1_lcdm_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 981, per start 71–243; wall per start (min) 6.5–19.3; final −log post spread 0.00012; S (all result starts) 0.0250; in window (≤0.25) 8/8, S in window 0.0250; lowest −log post s3 986.00535 with total χ² 2005.4483; total χ² range 2005.4233–2005.4483

**e2e, Fit 2 (ECF, Σmν = 0.06 eV fixed).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (base endpoint) | round 1 | round 2 | round 3 | round 4 | round 5 | outcome | evals | min |
|---|---|---|---|---|---|---|---|---|---|
| s0 | 981.88652 | 981.88323 / 1993.9737 / 0.6153 | 981.88193 / 1993.9673 / 0.6130 | 981.86716 / 1994.1684 / 0.3931 | 981.86716 / 1994.1684 / 0.3931 | = | round 4 gain 0.000000 < 0.001 → stop | 421 | 39.4 |
| s1 | 981.90386 | 981.86867 / 1994.1092 / 0.4477 | 981.86795 / 1994.1272 / 0.4321 | = | = | = | round 2 gain 0.000718 < 0.001 → stop | 232 | 26.3 |
| s2 | 982.18515 | 981.86729 / 1994.2044 / 0.3622 | 981.86703 / 1994.1910 / 0.3750 | = | = | = | round 2 gain 0.000257 < 0.001 → stop | 241 | 27.2 |
| s3 | 981.87425 | 981.87169 / 1994.0505 / 0.5145 | 981.87064 / 1994.0642 / 0.4989 | 981.86945 / 1994.0816 / 0.4797 | 981.86945 / 1994.0816 / 0.4797 | = | round 4 gain 0.000000 < 0.001 → stop | 378 | 36.9 |
| s4 | 982.04325 | 981.86835 / 1994.2379 / 0.3350 | 981.86833 / 1994.2386 / 0.3348 | = | = | = | round 2 gain 0.000012 < 0.001 → stop | 259 | 28.6 |
| s5 | 981.86897 | 981.86808 / 1994.1480 / 0.4065 | = | = | = | = | round 1 gain 0.000888 < 0.001 → stop | 95 | 12.7 |
| s6 | 981.87847 | 981.87726 / 1994.3454 / 0.2435 | 981.87165 / 1994.2911 / 0.2916 | 981.86984 / 1994.2651 / 0.3067 | 981.86868 / 1994.2440 / 0.3281 | 981.86860 / 1994.2434 / 0.3282 | round 5 gain 0.000077 < 0.001 → stop | 500 | 43.0 |
| s7 | 981.93800 | 981.86911 / 1994.2552 / 0.3227 | 981.86848 / 1994.2419 / 0.3348 | = | = | = | round 2 gain 0.000629 < 0.001 → stop | 244 | 23.8 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.01594 | 0.01490 | 0.00281 | 0.00241 | 0.00241 | | | |
| **S** = max − min total χ² | n/a | **0.3717** | **0.3238** | **0.1835** | **0.1625** | **0.1618** | | | |
| lowest −log post start: its total χ² | n/a | s2: 1994.2044 | s2: 1994.1910 | s2: 1994.1910 | s2: 1994.1910 | s2: 1994.1910 | | | |
| evaluations in this round | — | 992 (8 starts ran it) | 666 (7 starts ran it) | 335 (3 starts ran it) | 285 (3 starts ran it) | 92 (1 starts ran it) | | | |

SUMMARY e2e fit2_ecf_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 2370, per start 95–500; wall per start (min) 12.7–43.0; final −log post spread 0.00241; S (all result starts) 0.1618; in window (≤0.25) 8/8, S in window 0.1618; lowest −log post s2 981.86703 with total χ² 1994.1910; total χ² range 1994.0816–1994.2434

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

| candidate | fit | starts with a failed round | starts producing a result | no result: deadline / stopped / running | −log post spread (final) | **S** (final, starts with a result) | in window (≤0.25) | evaluations: total (per start) | wall min per start |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| cpl | cpl | 0/8 | 8/8 | 0 | 0.03564 | **0.2812** | 8/8 | 4419 (320–794) | 31.6–53.9 |

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

**base, CPL, Σmν = 0.06 eV FIXED (cpl_full.yaml as shipped; not fit 5).** AMENDMENT_TIER2_MINIMIZER.md §2 settings, seeds 9000+k.

| start | start point | status | −log post | −log post − best | total χ² | χ²_CMB | χ²_BAO | χ²_SN | τ-prior term | extra | evals | min |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| s0 | certified July best fit (seed 9000, inert) | converged | 982.8039 | 0.0058 | 1996.6809 | 583.3860 | 10.2594 | 1403.0355 | 0.3656 | w -0.84751, wa -0.57811 | 57 | 14.6 |
| s1 | random, seed 9001 | converged | 982.8549 | 0.0569 | 1996.8123 | 583.4441 | 10.4271 | 1402.9412 | 0.2577 | w -0.85460, wa -0.55753 | 390 | 67.8 |
| s2 | random, seed 9002 | converged | 982.7980 | 0.0000 | 1996.5124 | 583.4956 | 9.9418 | 1403.0750 | 0.5341 | w -0.84608, wa -0.56424 | 321 | 57.9 |
| s3 | random, seed 9003 | converged | 982.8220 | 0.0239 | 1996.6769 | 583.5467 | 10.1946 | 1402.9355 | 0.3967 | w -0.85470, wa -0.55371 | 362 | 63.3 |
| s4 | random, seed 9004 | converged | 982.8675 | 0.0695 | 1996.9181 | 583.3278 | 10.0442 | 1403.5461 | 0.2356 | w -0.82380, wa -0.65657 | 336 | 59.6 |
| s5 | random, seed 9005 | converged | 982.8297 | 0.0316 | 1996.3901 | 583.1594 | 9.8551 | 1403.3756 | 0.7323 | w -0.83002, wa -0.62780 | 388 | 67.1 |
| s6 | random, seed 9006 | converged | 982.8484 | 0.0503 | 1996.4437 | 583.5069 | 10.0372 | 1402.8995 | 0.6416 | w -0.85791, wa -0.51996 | 427 | 72.2 |
| s7 | random, seed 9007 | converged | 982.8731 | 0.0750 | 1997.1009 | 583.7716 | 10.1660 | 1403.1633 | 0.1032 | w -0.83976, wa -0.60521 | 292 | 54.6 |

SUMMARY base cpl_mnufixed: converged 8/8; in window (≤0.25) 8/8; −log post spread 0.07501; S in window 0.7107; S all converged 0.7107; lowest −log post s2 982.79805, total χ² 1996.5124; evaluations 2573 total, 57–427 per start

**Polish rounds** (`logs/tables_step4_polish.log`). Round 0 = the base endpoint.

**cpl, CPL, Σmν = 0.06 eV FIXED (cpl_full.yaml as shipped; not fit 5).** Cell = −log post / total χ² / τ-prior term.

| start | round 0 (base endpoint) | round 1 | round 2 | round 3 | round 4 | round 5 | outcome | evals | min |
|---|---|---|---|---|---|---|---|---|---|
| s0 | 982.80389 | 982.79454 / 1996.5883 / 0.4175 | 982.79066 / 1996.4852 / 0.5132 | 982.78977 / 1996.4854 / 0.5235 | = | = | round 3 gain 0.000900 < 0.001 → stop | 371 | 34.7 |
| s1 | 982.85492 | 982.79790 / 1996.5568 / 0.4716 | 982.79748 / 1996.5556 / 0.4718 | = | = | = | round 2 gain 0.000417 < 0.001 → stop | 336 | 32.7 |
| s2 | 982.79805 | 982.79446 / 1996.5044 / 0.5268 | 982.78970 / 1996.4971 / 0.5080 | 982.78852 / 1996.4871 / 0.5161 | 982.78839 / 1996.4866 / 0.5164 | = | round 4 gain 0.000131 < 0.001 → stop | 474 | 40.0 |
| s3 | 982.82197 | 982.79727 / 1996.4491 / 0.5697 | 982.79697 / 1996.4597 / 0.5581 | = | = | = | round 2 gain 0.000301 < 0.001 → stop | 320 | 31.6 |
| s4 | 982.86753 | 982.83047 / 1996.6302 / 0.4648 | 982.82504 / 1996.6265 / 0.4633 | 982.82309 / 1996.6131 / 0.4719 | 982.81712 / 1996.5391 / 0.5189 | 982.81697 / 1996.5537 / 0.5040 | round 5 gain 0.000149 < 0.001 → stop | 703 | 49.9 |
| s5 | 982.82968 | 982.80921 / 1996.4069 / 0.6396 | 982.80480 / 1996.4048 / 0.6323 | 982.80219 / 1996.4307 / 0.5969 | 982.79975 / 1996.4323 / 0.5902 | 982.79791 / 1996.4601 / 0.5621 | 5-round cap | 794 | 53.9 |
| s6 | 982.84836 | 982.83802 / 1996.4565 / 0.6386 | 982.83387 / 1996.4716 / 0.6138 | 982.83112 / 1996.4777 / 0.6033 | 982.82522 / 1996.4712 / 0.6046 | 982.82403 / 1996.4955 / 0.5706 | 5-round cap | 657 | 47.9 |
| s7 | 982.87306 | 982.85175 / 1997.0098 / 0.1384 | 982.83975 / 1996.9635 / 0.1697 | 982.82888 / 1996.9133 / 0.2123 | 982.81190 / 1996.8147 / 0.2539 | 982.80399 / 1996.7409 / 0.2898 | 5-round cap | 764 | 52.6 |
| starts entering spread and S (completed, not failed) | 0/8 | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | | | |
| spread of −log post (max − min) | n/a | 0.05728 | 0.05005 | 0.04260 | 0.03683 | 0.03564 | | | |
| **S** = max − min total χ² | n/a | **0.6029** | **0.5588** | **0.4825** | **0.3824** | **0.2812** | | | |
| lowest −log post start: its total χ² | n/a | s2: 1996.5044 | s2: 1996.4971 | s2: 1996.4871 | s2: 1996.4866 | s2: 1996.4866 | | | |
| evaluations in this round | — | 1321 (8 starts ran it) | 1051 (8 starts ran it) | 794 (6 starts ran it) | 733 (5 starts ran it) | 520 (4 starts ran it) | | | |

SUMMARY cpl cpl_mnufixed: starts failed (crash) 0/8; starts producing a result 8/8; still running/not finished 0; evaluations total 4419, per start 320–794; wall per start (min) 31.6–53.9; final −log post spread 0.03564; S (all result starts) 0.2812; in window (≤0.25) 8/8, S in window 0.2812; lowest −log post s2 982.78839 with total χ² 1996.4866; total χ² range 1996.4597–1996.7409

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
