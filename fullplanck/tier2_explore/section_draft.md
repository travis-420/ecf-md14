

---

# Exploratory minimizer study (not a gate attempt) — executed 2026-11-23, 21:59–23:25 UTC

**EXPLORATORY. This is not a gate attempt and it counts toward nothing.** It is not a G0 or G1 run, it
produces no R1–R4 outcome, and **no G1 verdict is declared anywhere in this section.** Only fits 1 and 2
(Σmν = 0.06 eV fixed) were run. **No fit 3, 4 or 5 was run, and no model with free Σmν was built or
evaluated.** No amendment, commit or push was made.

This section is appended. The sections above are unchanged byte-for-byte: SHA-256 of the first 29793 bytes
= `cf576d3a20c7eea437dcbc03b6fb217a611c5a1cbfa08a06a46a9b762e194daf`, which is the hash of the whole file
before this append (`fullplanck/tier2_explore/logs/session_start.log`; re-checked in
`logs/session_end.log`). Every number below comes from a command logged under
`fullplanck/tier2_explore/logs/`. Tables were generated from those logs by `scripts/make_tables.py`
(`logs/tables_*.log`), not typed by hand.

## Purpose and scope

Session 2 failed G1 on the spread guard. Fit 2's eight starts all converged at `rhoend` 0.005, yet ended
up to 0.2005 apart in −log posterior and 0.8739 apart in total χ² (S). The goal here is a minimizer
procedure under which independent starts of fit 1 and of fit 2 genuinely agree, so that a later
amendment can freeze it. The owner's brief fixed the order: (1) noise floor; (2) restart polishing of
session 2's 16 endpoints; (3) only if (2) leaves S above 0.3 for either fit, at most two alternatives
that the installed software supports.

- **Inputs, read-only:** session 2's yamls (`fullplanck/tier2_rerun/yamls/fit{1,2}_*_s{0..7}.yaml`),
  endpoints (`tier2_rerun/chains/*.minimum`, which carry 10 significant digits; `*.minimum.txt` for
  round-0 χ² values) and covmat (`tier2_rerun/covmats/`). Nothing in `fullplanck/tier2/` or
  `fullplanck/tier2_rerun/` was written (checked at the end).
- **Unchanged:** likelihood stack, kit code, priors and environment. Every run loads the session-2 yaml
  unchanged except for the start point (`ref`), the `sampler` block and the output path. The environment
  is the same July venv (Python 3.12.12, numpy 2.1.3, scipy 1.14.1, camb 1.6.6, cobaya 3.6.2,
  Py-BOBYQA 1.5.0). No package was installed or upgraded.
- **Outputs:** `fullplanck/tier2_explore/` (scripts, yamls of every round, chains, logs).
- **Execution:** each start is its own Python process (`scripts/polish.py`, which calls `cobaya.run`),
  with `OMP_NUM_THREADS=1`, on the same 16-core machine as sessions 1 and 2. Wall times depend on load,
  so evaluations (Py-BOBYQA `nf`) are the load-independent cost. Steps 2, 3A and 3B overlapped in time:
  - 22:17–22:22Z: up to 17 processes;
  - 22:31–22:42Z: up to 18 processes;
  - otherwise 16 or fewer.
  `caffeinate -dims` ran for the session and was stopped at the end.

### What the installed software supports (read from the installed source)

- **cobaya 3.6.2 `samplers/minimize/minimize.py`:**
  - `method` can be `bobyqa` (default), `scipy` or `iminuit`; `iminuit` is not installed.
  - For bobyqa, cobaya fixes `rhobeg: 1.0` and `maxfun = max_evals` (default 1e6 × d), then passes
    `override_bobyqa` verbatim to `pybobyqa.solve`.
  - Steps are scaled diagonally by the covmat's conditional widths, with no rotation.
  - A start counts as converged only on Py-BOBYQA `EXIT_SUCCESS` (scipy: `success`). A single-start run
    that fails raises `Minimization failed!`. Hitting `maxfun` is a failure.
- **Py-BOBYQA 1.5.0 `pybobyqa.solve`** accepts `rhobeg`, `rhoend`, `npt` (2n+1 by default, up to the
  full quadratic (n+1)(n+2)/2), `maxfun`, `nsamples`, `objfun_has_noise`, `seek_global_minimum`,
  `scaling_within_bounds` and `user_params`. `user_params` covers `restarts.*` (hard or soft restarts,
  `max_unsuccessful_restarts`, `auto_detect`), `noise.*`, `tr_radius.*`, `init.*`, `slow.*`, among others.
- **scipy 1.14.1 `minimize`** (Powell, Nelder-Mead, L-BFGS-B, COBYQA, …) is reachable through cobaya's
  `method: scipy` / `override_scipy`.

## Step 1 — noise floor (`scripts/noise_floor.py`; `logs/step1_noise_floor_fit{1,2}.log`)

**Points.** These are session 2's selected (lowest −log posterior) endpoints:
- fit 1 s4: −log post 986.005632, total χ² 2005.404620, τ-prior term 0.864324;
- fit 2 s6: −log post 981.872941, total χ² 1994.085310, τ-prior term 0.456326.

**Perturbations.** Every sampled parameter is multiplied by (1 ± ε·u_i), with u_i = ±1 drawn from a
seeded generator:
- 10 directions × 2 signs = **20 perturbations per size**;
- ε = 1e-6 and 1e-4.

**Evaluations.** `model.logposterior(…, cached=False)` in the session-2 model. The centre was evaluated
3 times (first, middle, last); all 3 values were bit-identical in both fits.

**Scatter relative to the centre value.** "2nd diff" is f(+)+f(−)−2f(0) over the 10 pairs: smooth
curvature plus noise. "Antisym." is (f(+)−f(−))/2: the linear (gradient) part.

| point | ε | −log post: std / max−min | −log post 2nd diff: mean / std | −log post antisym.: std | total χ²: std / max−min | total χ² 2nd diff: mean / std | total χ² antisym.: std |
|---|---:|---|---|---:|---|---|---:|
| fit 1 (s4) | 1e-6 | 1.03e-5 / 3.30e-5 | 1.36e-5 / 5.36e-6 | 8.21e-6 | 2.49e-4 / 5.71e-4 | 2.69e-5 / 1.07e-5 | 2.48e-4 |
| fit 1 (s4) | 1e-4 | 2.51e-2 / 6.73e-2 | 7.90e-2 / 5.01e-2 | 2.35e-4 | 5.61e-2 / 1.82e-1 | 1.55e-1 / 1.00e-1 | 2.44e-2 |
| fit 2 (s6) | 1e-6 | 3.42e-5 / 1.30e-4 | 1.73e-5 / 3.50e-5 | 2.28e-5 | 1.89e-4 / 5.42e-4 | 3.43e-5 / 6.99e-5 | 1.77e-4 |
| fit 2 (s6) | 1e-4 | 2.53e-2 / 7.72e-2 | 8.80e-2 / 5.01e-2 | 3.15e-3 | 5.49e-2 / 1.64e-1 | 1.73e-1 / 1.00e-1 | 2.24e-2 |

What this says about how small S can get:
- **Evaluation noise is tiny.** At ε = 1e-6, −log posterior scatters by at most 3.3e-5 (fit 1) and
  1.3e-4 (fit 2) peak to peak, and this includes the smooth part. The symmetric (noise-plus-curvature)
  part has std 5e-6 and 3.5e-5. Repeat evaluations are exact.
- **Total χ² moves linearly near the posterior minimum.** Its ε = 1e-6 scatter (std about 2e-4) is
  almost entirely antisymmetric. Total χ² is not stationary at the −log-posterior minimum, because the
  τ and A_planck prior terms balance its gradient. Its symmetric part (std 1e-5 and 7e-5) is at the
  noise level.
- **At ε = 1e-4 the scatter is smooth curvature, not noise.** The second differences are positive, with
  mean 0.079 and 0.088, while the antisymmetric part is small. A 1e-4 relative move is not small for this
  posterior.
- **So noise does not limit S at the 0.3 or 0.5 level.** It sits 3–4 orders of magnitude below.
  Empirically, S tracks how far the starts are from agreeing in −log posterior. Fit 1 had −log-post
  spread 0.0124 with S = 0.2128 in step 2, and spread 6e-5 with S = 0.0188 in step 3A round 1 (below).
  What limits S is convergence, not noise.

## Step 2 — restart polishing with session 2's settings (`logs/step2_*.log`, `logs/tables_step2.log`)

**Procedure.** For each of the 16 session-2 endpoints, cobaya `minimize` was rerun starting at that
endpoint (`ref` = endpoint values), with session 2's sampler settings unchanged:
- bobyqa, `rhoend` 0.005, `rhobeg` 1.0 (fixed by cobaya), default `npt` = 2n+1, `ignore_prior: False`;
- same covmat, `best_of: 1`, same seed field (unused for a fixed `ref`).

The rerun was then repeated from each new endpoint, up to 5 rounds. A start stopped after the first round
that improved its −log post by less than 0.001. In the tables, `=` means that start had already stopped.

@@TABLES_STEP2@@

**Step 2 result.**
- **Every start stopped on the 0.001 rule, after 1–3 rounds.** None reached 5 rounds.
- **One negative gain.** Fit 1 s2 shows a gain of −0.000003. Round 0 is session 2's recorded value,
  986.0058913; round 1 restarted from the stored 10-digit endpoint and returned 986.0058940. The
  2.7e-6 difference is below the step-1 noise scale (`logs/step2_fit1_lcdm_mnufixed_s2.log`).
- **Fit 1:** S went 0.4022 → 0.3788 → 0.2128 → 0.2128, and the −log-post spread 0.0194 → 0.0124.
- **Fit 2:** S went 0.8739 → 0.6948 → 0.6611 → 0.6611, and the spread 0.2005 → 0.0583. **Fit 2 ends with
  S = 0.6611 > 0.3**, so step 3 ran.
- **Cost:** fit 1, 561 evaluations in total (32–230 per start); fit 2, 1106 (44–304 per start).
  Wall time per start was at most 7.2 min (fit 1) and 16.2 min (fit 2) (`logs/summary_step2.log`).
- **The stops are stalls, not convergence.** Starts stopped with gains < 0.001 while still 0.012
  (fit 1 s0) and 0.058 (fit 2 s5) above the best start, about 1000× the step-1 noise.
- **Likely mechanism (inference, not tested here).** With npt = 2n+1, each restart begins from a
  coordinate-aligned interpolation set in cobaya's diagonally scaled space. So its model initially
  carries no information about parameter correlations, and it can stop in a correlated valley.
  Alternative A below is consistent with this.

**Order note.** Step 3A was launched at 22:17:54Z, while two fit-2 starts of step 2 (s2, s3) were still
polishing. By then the six other fit-2 starts had already stopped, spanning total χ² 1993.9517–1994.6128.
So step 2 could not end with fit-2 S below 0.661, and the step-3 condition was already fixed
(`logs/step3A_launch.log`). The final fit-2 S of step 2 is 0.6611.

## Step 3 — two alternatives (S stayed above 0.3 for fit 2)

Both alternatives were applied to **both** fits, because a procedure to be frozen must serve fit 1 and
fit 2 alike. Both start from the same 16 session-2 endpoints as step 2 and use the same rounds and stop
rule (≤ 5 rounds; stop when a round gains < 0.001). Only the sampler block changes. In the tables, `!`
marks a start that crashed (see below); its last completed value is shown but is **not** a result of
the alternative, and it is excluded from the spread and from S.

### Alternative A — Py-BOBYQA full quadratic model (`logs/step3A_*.log`, `logs/tables_step3A.log`)

**Settings:** `override_bobyqa: {rhoend: 0.005, npt: (n+1)(n+2)/2}`. That is npt = 36 for fit 1 (n = 7)
and 45 for fit 2 (n = 8). Everything else is as in step 2.

@@TABLES_STEP3A@@

**Alternative A results.**
- **Fit 1:** after one round, all 8 starts agree to **6e-5 in −log post**, with **S = 0.0188** (total χ²
  2005.4314–2005.4503). One start (s1) crashed in round 2, after its round-1 result had already agreed.
  Over the 7 other starts after round 2: spread 9e-5, S = 0.0177. Cost: 106–114 evaluations per round
  per start, 1294 in total; at most 8.1 min per start.
- **Fit 2: every one of the 8 starts crashed**, in round 1 (s1, s3, s4), round 2 (s0, s6, s7) or round 3
  (s2, s5). Completed results:
  - round 1: 5 starts, spread 0.0075, S = 0.2723;
  - round 2: 2 starts (s2, s5), which agree to 1.4e-4 in −log post (981.86738, 981.86724), S = 0.0375.
  - These are the lowest fit-2 −log posteriors found in the study.
- **The crash.** Py-BOBYQA exits with `EXIT_LINALG_ERROR`, "Singular matrix in mini-model interpolation
  (main loop)". The LU factorization reports an exactly zero pivot ("Diagonal number 39 is exactly zero",
  fit 2 s1). cobaya then raises `Minimization failed!`, and the round's result is lost.
- **Always at the same point.** Across A and B there were 20 crashes (`logs/crash_evalcounts.log`).
  Each happened at the same evaluation count of its run, within the first iterations after Py-BOBYQA's
  npt-point initialisation:
  - all 16 fit-2 crashes at evaluation 48 (npt = 45);
  - all 4 fit-1 crashes at evaluation 37 (npt = 36).
  A round that got past that point always completed.
- **Not reproduced in isolation.** A synthetic check (`scripts/synthetic_npt_check.py`,
  `logs/step3_synthetic_npt_check.log`) ran Py-BOBYQA directly on a quadratic built from the gradient and
  Hessian Py-BOBYQA printed at the fit-2 s1 crash, with the same `rhobeg`, `rhoend` and npt, with and
  without 3e-5 noise. It did **not** reproduce the error. The cause was not identified in this session.

### Alternative B — A plus Py-BOBYQA's built-in soft restarts (`logs/step3B_*.log`, `logs/tables_step3B.log`)

**Settings:** `override_bobyqa: {rhoend: 0.005, npt: (n+1)(n+2)/2, user_params: {restarts.use_restarts: True,
restarts.use_soft_restarts: True, restarts.max_unsuccessful_restarts: 1, restarts.auto_detect: False}}`.

**Why.** With restarts on, Py-BOBYQA answers an interpolation failure with a soft restart instead of an
exit. It also soft-restarts each time ρ reaches `rhoend`, and stops after one consecutive restart that
does not lower f.

@@TABLES_STEP3B@@

**Alternative B results.**
- **Fit 1:** after one round, all 8 starts agree to 6e-5 in −log post (986.00534–986.00541), with
  **S = 0.0146** (total χ² 2005.4314–2005.4460). Three starts (s1, s3, s5) then crashed in round 2.
  Cost:
  - round 1: 193–532 evaluations per start, 2415 over 8 starts (A: 872);
  - in total: 2832 evaluations, at most 18.9 min per start.
- **Fit 2: soft restarts did not prevent the crash.** The failure moved into Py-BOBYQA's geometry step:
  `EXIT_LINALG_ERROR`, "Error when calculating geometry-improving step". Py-BOBYQA raises this from a
  ValueError, which its source comments attribute to NaN/inf in the model gradient or Hessian.
  - The same three starts as in A (s1, s3, s4) crashed in round 1, at evaluation 48, with no result.
  - s0, s2, s6 and s7 crashed in round 2, and s5 in round 3.
- **Fit 2, completed results:**
  - round 1: 5 starts, spread 0.0046, S = 0.1812;
  - each start's last completed round: 5 starts, spread 0.0029, S = 0.1426 (`logs/final_analysis.log`).
- **The best fit-2 agreement in the study.** Two independent starts, s0 and s2, agree to 1e-5 in
  −log post (981.86689 and 981.86690), with total χ² 1994.1613 and 1994.1641. These are the lowest
  fit-2 values found.
- **Fit 2 cost:** 296–1041 evaluations for a round-1 pass, at most 52.3 min per start, 3355 evaluations
  in total.
- **Where B added nothing.** When a soft restart did not lower f, B returned exactly A's endpoint: fit 2
  s5 in rounds 1–2 and s6 in round 1; fit 1 s0, s2, s4 and s7 in round 1.

## The procedure I would freeze

**No procedure tested here is ready to freeze.** On fit 2, each of the three polishing schemes fails in
one of two ways:
- **Step 2 runs cleanly but stalls** (S = 0.6611).
- **A and B make starts agree when they complete, but crash deterministically.** Under A every fit-2
  start crashed in some round, and s1, s3 and s4 never completed one. B crashed in the same three, and
  more.

Two consequences follow:
- With a frozen version of A or B, whether fit 2 meets the 4-of-8 rule and the spread guard would depend
  on which starts happen to crash.
- Fits 3–5 have more parameters (npt 45, 55, 66) and were deliberately left untested.

**What I would freeze, once one more exploratory session (fits 1–2 only) has removed the crash: A, as a
polish stage after the amendment's base minimization.**
1. **Base minimization:** exactly `AMENDMENT_TIER2_MINIMIZER.md` §2:
   - 8 starts: s0 = certified July best fit; s1–s7 drawn with seeds 2001–2007 from the §2.3 start-point
     distributions;
   - bobyqa, `rhoend` 0.005, default `npt`, `rhobeg` 1.0, `ignore_prior: False`, §2.3 covmats,
     `best_of: 1`.
2. **Polish round:** for each start, rerun cobaya `minimize` from its current endpoint (`ref` = endpoint,
   full double precision), with `override_bobyqa: {rhoend: 0.005, npt: (n+1)(n+2)/2}`. Here n is the
   number of sampled parameters, so npt = 36 for fit 1, 45 for fit 2, 45 for fit 3, 55 for fit 4 and 66
   for fit 5. Everything else is as in item 1.
3. **Stopping rule:** repeat item 2 from the new endpoint until a round lowers −log posterior by less
   than 0.001, with at most 5 rounds.
4. **Result:** a start's result is its last completed polish round. Selection (§1), the window and the
   4-of-8 rule (§2.4), and S and the spread guard (§3) are unchanged.

**Cost measured here** (16–18 processes on 16 cores, `OMP_NUM_THREADS=1`):
- **Fit 1:** 105–114 evaluations per polish round (3.3–4.9 min); 1–2 rounds; 106–220 evaluations and at
  most 8.1 min per start.
- **Fit 2:** 135–224 evaluations per polish round (8.1–12.3 min). The two starts that completed two
  rounds used 354–362 evaluations and at most 21.1 min. Source: `logs/nf_per_round.log`,
  `logs/summary_step3A.log`.
- **Base run on top** (session 2, logged start/end times): 2–11 min for fit 1, 9–36 min for fit 2.
- **Fits 3–5:** not measured.

**What A achieved where it completed:**
- **Fit 1:** all 8 starts within 6e-5 in −log post after one round, S = 0.0188 (B: 0.0146).
- **Fit 2:** s2 and s5, the only starts to complete two A rounds, are within 1.4e-4 of each other, with
  S = 0.0375 between them.
- **Fit 2, last-completed-round view:** over the 5 fit-2 starts with any completed A round, taking each
  start's last completed round: spread 0.0100, S = 0.2557 (`logs/final_analysis.log`). That
  "last completed round" view is a rule I wrote after seeing the crashes. It is reported for
  information and is not a pass of anything.

**Cheapest next tests of the crash** (not run here, because the brief allowed two alternatives):
- `npt` = (n+1)(n+2)/2 − 1, which makes Py-BOBYQA use its minimum-change-Hessian interpolation system
  instead of the square full-quadratic one. Whether that avoids the zero pivot is untested.
- scipy Powell as the polish method (`method: scipy`, `override_scipy: {method: Powell}`).

## Where the converged total χ² of fits 1 and 2 sits relative to the certified values (no G1 verdict)

Reporting only. No G1 verdict is declared, and no certified value is changed. Sources:
`logs/final_analysis.log`, `logs/certified_compare.log`.

- **Fit 1 (converged across starts here).** Under A and B, all 8 starts agree after one polish round:
  - −log post 986.00534–986.00543, which is −0.01636 to −0.01627 relative to July's 986.0217;
  - total χ² 2005.4314–2005.4503, which is **0.0813–0.1002 below** the certified 2005.5316;
  - the lowest −log post found, 986.00533 (A s3, round 2), has total χ² 2005.4395 (−0.0921).
- **Fit 2 (not converged across all starts here).**
  - The lowest −log post found is 981.86689 (B s0, round 1), −0.07247 relative to July's 981.93936. Its
    total χ² is 1994.1613, **+0.2680** relative to the certified 1993.8933.
  - Five completed A/B results lie within 0.0005 of that −log post: B s0, B s2, A s5, B s5 and A s2.
    Their total χ² is 1994.1554–1994.1929, **+0.2621 to +0.2996** relative to certified.
  - All 13 completed A/B fit-2 start-rounds span 1994.0650–1994.3373 (+0.1717 to +0.4440).
- **Difference.** Between the lowest −log-posterior points of the two fits, Δχ²(fit 2 − fit 1) =
  −11.2782, which is **+0.3601** from the certified −11.6383. Per procedure, at each one's own
  lowest −log-post starts: A −11.2841 (+0.3542), B −11.2781 (+0.3602).
- **In fit 2, lower −log post came with higher total χ²:**
  - session 2's selected s6: 981.87294 / 1994.0853, τ-prior term 0.4563;
  - lowest point found here: 981.86689 / 1994.1613, τ-prior term 0.4049.

## Plain statements

- **Nothing in this study brought fit 2's S under 0.5 with all 8 starts producing a result.** Step 2 is
  the only procedure in which all 8 fit-2 starts produced a result, and it ended at S = 0.6611. Under A
  and B, 3 of 8 fit-2 starts produced no result. Over the 5 that did, taking each start's last completed
  round, S = 0.2557 (A) and 0.1426 (B). Those 5-start figures rest on a rule written after seeing the
  crashes.
- **Fit 1:** step 2 brought S to 0.2128. A and B brought it to 0.0188 and 0.0146, with all 8 starts.
- **Evaluation noise is not the limit.** It is about 1e-5 to 1e-4 in −log post (step 1).
- **What does limit S here:**
  - With cobaya's default npt = 2n+1, restarts stall up to 0.058 above the best −log post.
  - With npt = (n+1)(n+2)/2, starts that complete converge together. But Py-BOBYQA 1.5.0 crashed
    (`EXIT_LINALG_ERROR`) at some round in all 16 fit-2 start-procedures (8 in A, 8 in B), 6 of them in
    round 1 with no result. It also crashed in 4 of 16 fit-1 start-procedures (A s1; B s1, s3, s5), all in
    round 2 after a completed round 1. The cause was not identified.

## Notes, deviations and integrity

- **Read-only directories.** `find fullplanck/tier2 fullplanck/tier2_rerun -newer
  fullplanck/tier2_explore/logs/session_start.log` returned nothing before the append
  (`logs/pre_append_checks.log`). `logs/session_end.log` repeats the check after the append.
- **Tracked files.** The brief says both "no edits to tracked files" and "append … to
  RESULTS_NEUTRINO_TIER2.md", which is tracked. The append is the only change to a tracked file.
  `git status --porcelain` before the append listed only untracked `.DS_Store`, `fullplanck/__pycache__/`
  and `fullplanck/tier2_explore/`; the first two were already present at session start
  (`logs/pre_append_checks.log`). The post-append state is in `logs/session_end.log`. HEAD is still
  `81f7db8`. No commit, push or amendment was made.
- **Bytecode file.** Step 1 ran Python with `-I`, which ignores `PYTHONDONTWRITEBYTECODE`. So it rewrote
  the untracked, pre-existing `fullplanck/__pycache__/ecf_theory_cobaya.cpython-312.pyc` (14:01 local).
  Every later run used `-I -B`. No tracked file is affected.
- **Driver versions.** `scripts/polish.py` gained the step-3 variants after step 2 had launched; the
  running step-2 processes were unaffected. The as-run step-2 driver is preserved as
  `scripts/polish_step2_asrun.py` (SHA-256 `f187484686a09c12253ad5e57b509ec821ed831369badd33ae1c41e865792253`,
  identical to the hash logged at step-2 launch). Hashes at each launch are in `logs/step{2,3A,3B}_launch.log`.
- **Deadlines.** Each step had a time after which no new round would start:
  - step 2: 23:30Z;
  - step 3A: 23:20Z;
  - step 3B: 23:50Z.
  No deadline was reached. Step 2 ended at 22:21:29Z, step 3A at 22:41:32Z and step 3B at 23:25:22Z
  (`logs/step*_launch.log`). Every start ended on the 0.001 rule or by crashing; none reached the
  5-round cap.
- **Not tried:** scipy Powell, which was configured in the driver but never run. The brief allowed at
  most two alternatives, and B used the second slot.
- **3-hour limit.** Session start 21:59:14Z (`logs/session_start.log`). All runs had ended by
  23:25:22Z, so the 3-hour limit (00:59Z) was not reached. The closing checks and the `caffeinate`
  stop are in `logs/session_end.log`.
