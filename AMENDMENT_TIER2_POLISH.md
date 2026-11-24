# Amendment to PREREG_NEUTRINO_TIER2.md: polish stage for the minimizer (third attempt)

**Status:** drafted 2026-11-24 UTC, after two failed G1 attempts and two exploratory minimizer studies, and BEFORE any
third attempt. The git timestamp of the commit that adds this file governs.

It amends `PREREG_NEUTRINO_TIER2.md` (frozen at `068a9ab`), as already amended by:
- `AMENDMENT_TIER2_PRIOR.md` (`37b8f12`);
- `AMENDMENT_TIER2_MINIMIZER.md` (`1fd858e`), cited below as "1fd858e §n".

It governs a **third attempt in a fresh session**. The order is G0, then G1 (fits 1 and 2), then fits 3, 4 and 5 **only
if G1 passes**.

Every number below is quoted from `RESULTS_NEUTRINO_TIER2.md` (as committed at `e204973`) or from the study logs it
cites, with its source, except the arithmetic in §1, which is labelled as such.

## 1. Status and disclosure

**Two G1 attempts failed.**
- **Session 1.** Results section "Gate G1 — baseline reproduction at fixed Σmν = 0.06 eV: **FAIL**"; log
  `fullplanck/tier2/logs/G1_verdict.log`.
  - G1 failed under both readings of "best". Lowest −log posterior: Δχ² criterion +0.5230. Lowest total χ²: fit 1
    −0.7477, fit 2 −0.5665.
  - Under the spread guard later written into 1fd858e §3, both fits would have been minimizer-failed (S = 0.9808 and
    0.7132; 1fd858e §3).
- **Session 2** (rerun under 1fd858e). Results section "Session 2 — G1 rerun under AMENDMENT_TIER2_MINIMIZER.md";
  log `fullplanck/tier2_rerun/logs/G1_verdict.log`.
  - G1 was recorded as failed: fit 2 was minimizer-failed by the spread guard, with S = 0.8739 > 0.5. Fit 1 had
    S = 0.4022.
  - All three G1 χ² criteria passed: fit 1 −0.1270, fit 2 +0.1920, Δχ² +0.3190 against the certified values.
  - Selected −log posterior minus July: fit 1 −0.0161, fit 2 −0.0664. No §3 clause other than the spread guard
    applied.

**Two exploratory studies followed.** Neither was a gate attempt, and neither counts toward anything.
- Results section "Exploratory minimizer study (not a gate attempt) — executed 2026-11-23, 21:59–23:25 UTC". Outputs:
  `fullplanck/tier2_explore/`.
- Results section "Exploratory minimizer study 2 (not a gate attempt) — executed 2026-11-24, 02:38–05:30 UTC".
  Outputs: `fullplanck/tier2_explore2/`.

**Disclosure: the studies show where the converged total χ² of fits 1 and 2 sits relative to the certified values.**
The certified values (1fd858e §0, §3) are:
- fit 1 total χ² 2005.5316, `minuslogpost` 986.0217;
- fit 2 total χ² 1993.8933, `minuslogpost` 981.93936;
- Δχ² = −11.6383.

- **Study 1** (section "Where the converged total χ² of fits 1 and 2 sits relative to the certified values (no G1
  verdict)"; `fullplanck/tier2_explore/logs/final_analysis.log`, `certified_compare.log`):
  - **Fit 1:** all 8 starts agree. Total χ² 2005.4314–2005.4503, which is 0.0813–0.1002 *below* certified. −log post
    is −0.01636 to −0.01627 relative to July.
  - **Fit 2:** the lowest −log post found is 981.86689, −0.07247 relative to July. Its total χ² is 1994.1613, +0.2680
    relative to certified.
  - **Δχ²** between the two fits' lowest −log-post points: −11.2782, which is +0.3601 from the certified −11.6383.
- **Study 2, step 3: fresh starts** (seeds 9001–9007), base minimization plus the polish this amendment adopts.
  Sources: section "Step 3 — end-to-end test of (ii) on fits 1 and 2, from fresh starts";
  `fullplanck/tier2_explore2/logs/tables_step3_polish.log`, SUMMARY lines.
  - **Fit 1:** 8/8 starts in the window, no failure, S = 0.0250. Total χ² 2005.4233–2005.4483. Lowest −log post: s3,
    986.00535, with total χ² 2005.4483.
  - **Fit 2:** 8/8 in the window, no failure, S = 0.1618. Total χ² 1994.0816–1994.2434. Lowest −log post: s2,
    981.86703, with total χ² 1994.1910.
  - **Against the certified values:** all 8 fit-1 values lie below 2005.5316 and all 8 fit-2 values lie above
    1993.8933, as in study 1.
  - **Differences at the lowest −log-post starts.** These are arithmetic on the values quoted above, not a logged
    result:
    - fit 1: 2005.4483 − 2005.5316 = −0.0833;
    - fit 2: 1994.1910 − 1993.8933 = +0.2977;
    - Δχ² = 1994.1910 − 2005.4483 = −11.2573, which is +0.3810 from the certified −11.6383.

**The G1 outcome is therefore partly foreseeable.**
- The three χ² criteria passed in session 2.
- The tightest margin is the Δχ² criterion, against a tolerance of 0.5:
  - +0.3190 in session 2;
  - +0.3601 in study 1;
  - +0.3810 in study 2's step 3 (fresh starts; arithmetic above).

  Of the three, +0.3810 is the tightest.
- Both fits' −log posteriors were within 0.25 of July's in session 2 and in study 1, the regime in which the
  July-suboptimal clause does not fire.
- The spread S that failed session 2 was 0.0250 (fit 1) and 0.1618 (fit 2) with this polish in study 2's step 3,
  below the 0.5 guard.
- The third attempt uses new random starts (seeds 3001–3007), so its numbers will differ from every number above.
  What is known is the region; the outcome is not known.

This amendment was written with that knowledge. It changes no criterion in response to it.

**The third attempt runs regardless.** Every consequence in 1fd858e §3 stands, with its precedence rules:
- the July-suboptimal clause, including its **public erratum** re-deriving the certified numbers;
- the July readout-drift case, including its **public erratum** re-deriving the certified χ² values and the headline
  Δχ²;
- the rerun-worse case;
- the 4-of-8 rule and the G1 spread guard, with their "minimizer-failed" consequences.

Whichever applies is recorded and followed as 1fd858e §3 states it.

## 2. Compliance with 1fd858e §3

1fd858e §3 says: "If a rerun is recorded as minimizer-failed, any later amendment must improve the minimizer itself
(settings, algorithm, or number of starts). It may not narrow the 0.25 window, raise the 0.5 guard, or lower the 4-of-8
requirement."

**This amendment changes only the minimizer, by adding a polish stage after the base minimization (§4–§6 below).**
- It does not narrow the 0.25 window, raise the 0.5 guard or lower the 4-of-8 rule.
- **Unchanged:**
  - the selection rule (1fd858e §1);
  - the window and the 4-of-8 rule (§2.4), with "converged" extended to cover polish rounds as in §6 below;
  - the G1 criteria and tolerance (`PREREG_NEUTRINO_TIER2.md`, 1fd858e §3);
  - every §3 clause, case and precedence rule, and the spread guard;
  - the reporting requirements (§4), to which §7 below only adds per-round lines that no rule uses;
  - every R1–R4 threshold, and the minimizer-limited rule (§5).
- **Also unchanged** (1fd858e §2.5):
  - likelihood stack and kit code (`fullplanck/`);
  - Σmν prior: flat [1e-5, 1.0] eV;
  - neutrino settings;
  - environment: the July venv with Python 3.12.12, numpy 2.1.3, scipy 1.14.1, camb 1.6.6 and cobaya 3.6.2. The
    polish depends on Py-BOBYQA 1.5.0, the version installed in that venv
    (`fullplanck/tier2_explore2/logs/session_start.log`).

## 3. Base minimization

Exactly 1fd858e §2, with one change: **seeds 3001–3007 for s1–s7 (seed = 3000 + k).**
- **Settings:** bobyqa, `rhoend` 0.005, `rhobeg` 1.0 (fixed by cobaya), default npt, `ignore_prior: False`, default
  `max_evals` and `confidence_for_unbounded`, `best_of: 1` per process.
- **Starts:** 8 per fit.
  - **s0** = the certified July best fit (1fd858e §2.3): `fullplanck/chains/lcdm.minimum.txt` for fits 1 and 3,
    `ecf.minimum.txt` for fits 2 and 4, `cpl.minimum.txt` for fit 5. Fits 3–5 start at Σmν = 0.06 eV. s0 receives
    seed 3000 by the same formula; its `ref` values are fixed numbers, so the seed has no effect.
  - **s1–s7:** drawn from the 1fd858e §2.3 start-point distributions with seed 3000 + k. The same k uses the same seed
    in every fit.
- **Covmats:** the 1fd858e §2.3 covmats, with the SHA-256 values listed there. Σmν's step scale comes from
  `proposal: 0.05`.
- **Outputs:** `fullplanck/tier2_attempt3/`. The directories `fullplanck/tier2/`, `fullplanck/tier2_rerun/`,
  `fullplanck/tier2_explore/` and `fullplanck/tier2_explore2/` are read-only.

## 4. Polish stage, for every fit 1–5

This is candidate (ii) of study 2: section "Step 5 — recommendation", items 2–4. Every start whose base run converged is
polished. A base run that did not converge is not polished (§6).

**One polish round** is cobaya 3.6.2 `minimize`, started exactly at the start's current endpoint. Round 0 is the base
endpoint; round r starts at round r−1's endpoint.
- **Start point:** `ref` is the endpoint value of every sampled parameter **at full double precision**, passed
  in-process or from a full-precision dump. It is never read from the `.minimum` or `.minimum.txt` files, which carry
  8–10 significant digits.
- **Yaml:** the base run's yaml (likelihoods, theory, priors), unchanged except for `ref`, the `sampler` block and the
  output path. No seed: the start point is fixed, so cobaya draws nothing.
- **Sampler:** `minimize` with `best_of: 1`, the 1fd858e §2.3 covmat, `ignore_prior: False`, and
  **`override_bobyqa: {rhoend: 0.005, npt: (n+1)(n+2)/2, rhobeg: 0.1}`**. Everything else is at the cobaya 3.6.2
  defaults.
  - cobaya sets `rhobeg: 1.0` and then applies `override_bobyqa` with `recursive_update`, so the override replaces it
    (study 2, step 2).

| fit | model | sampled parameters | n | npt = (n+1)(n+2)/2 |
|---|---|---|---:|---:|
| 1 | ΛCDM, Σmν = 0.06 fixed | logA, ns, H0, ombh2, omch2, tau, A_planck | 7 | 36 |
| 2 | ECF, Σmν = 0.06 fixed | the 7 above + tau_ecf | 8 | 45 |
| 3 | ΛCDM + free Σmν | the 7 above + mnu | 8 | 45 |
| 4 | ECF + free Σmν | the 7 above + tau_ecf, mnu | 9 | 55 |
| 5 | CPL + free Σmν | the 7 above + w, wa, mnu | 10 | 66 |

These npt values are those listed in study 2's step 5, item 2.

## 5. Stop rule

- Repeat the polish round from the new endpoint until a round lowers −log posterior by **less than 0.001**, with
  **at most 10 rounds**.
- The gain of round r is the −log posterior at round r−1 minus the −log posterior at round r.
- Reaching the 10-round cap is not a failure. The start's result is chosen as below.

**A start's result.**
- A start's result is its completed round with the **lowest −log posterior**, counting the base result as round 0.
  Ties go to the later round.
- If a round ends above its start, its gain is negative. The start then stops under the 0.001 rule, and the earlier,
  lower round is the result.
- No round of this polish (candidate (ii)) ended above its start in study 2 (see below). So in the studies this rule
  coincides with taking the last round.
- The rule exists for the boundary situations described in §8.
- The failure rule (§6) is unchanged: a failed round still makes the start not converged.

**5 rounds is what the studies tested; 10 is an extension.** Both studies used at most 5 rounds (study 1, steps 2–3;
study 2, steps 2–4, "the first study's round and stop rule").

**Why the cap is raised.**
- **The 5-round cap bound in 9 dimensions** (study 2, section "Step 4 — dimension test of (ii) on CPL with Σmν FIXED at
  0.06 eV (this is NOT fit 5)"; `fullplanck/tier2_explore2/logs/stop_analysis.log`):
  - three of the 8 CPL starts (s5, s6, s7) hit the 5-round cap while still gaining 0.0012–0.0079 per round;
  - in that section's words, "both the 0.001 per-round rule and the 5-round cap bind well before agreement";
  - fit 4 has 9 sampled parameters, and fit 5 has 10.
  - The cap also bound once in fit 2, in study 2's step 2: (ii) s0 was still gaining 0.0012 per round (section
    "Step 2 summary").
- **A round cannot raise −log posterior.**
  - Py-BOBYQA 1.5.0 evaluates the start point first. Its current best point (x_opt) begins there and is replaced only
    by a point with a lower value, and it returns that point (read from the installed `pybobyqa/solver.py` and
    `model.py`).
  - So a round started exactly at the previous endpoint ends at or below that endpoint's −log posterior, up to the
    reproducibility of a single evaluation. Study 1, step 1 measured repeated evaluations at one point as
    bit-identical.
  - In study 2's round tables for (ii) (steps 2, 3 and 4), no round ends above its start.
  - So rounds 6–10 can lower a start's −log posterior or leave it unchanged. They cannot make its objective worse;
    they cost evaluations.

**Not tested:**
- rounds 6–10, which never ran in either study;
- whether starts that hit the 5-round cap (CPL s5–s7) would agree within 10 rounds;
- the value of S after more than 5 rounds;
- the cost of rounds 6–10;
- any polish round on a free-Σmν model (§8).

The per-round threshold stays at 0.001. Study 2 found that it stops some starts while they still disagree (§8), and
this amendment does not change it.

## 6. Failure rule

Study 2's step 5, item 4, unchanged.
- **What counts as a failed polish round:** Py-BOBYQA exits with any flag other than `EXIT_SUCCESS`, so cobaya does
  not log `Run 1/1 converged.` and raises `Minimization failed!`; or the round raises any other exception.
- **If any polish round of a start fails, the start is "not converged"** (1fd858e §2.4).
  - It cannot be selected, does not enter S, and counts against the 4-of-8 rule.
  - It is reported with its last completed round, or with its base result if round 1 failed.
- **No retry, no substitute start, no fallback setting.**
- **For 1fd858e §2.4, a start is converged only if both hold:**
  - its base run converged (`Run 1/1 converged.` and exit 0, as now);
  - and no polish round failed.
- A base run that did not converge is not polished; the start is not converged.
- The 4-of-8 rule, the spread guard and every §3 consequence then apply as written.

## 7. Reported values and the verdict script

**Reported values.** For every converged start, the values used by 1fd858e §1, §2.4, §3, §4 and §5 come from its
**result round** (§5): the completed round with the lowest −log posterior, counting the base result as round 0, with
ties going to the later round. These values are:
- −log posterior, total χ², the three per-likelihood χ², the τ-prior term;
- τ_ecf, Σmν, w and wa where present.

In addition to §4, the report gives for every start its base result, and for each polish round its −log posterior,
total χ² and evaluation count. This is reporting only; no rule uses these lines.

**Verdict script.** It implements 1fd858e §1, §2.4 (with §6 of this amendment), §3, §4 and §5.
- It is written, self-tested and then frozen before any fit of the third attempt runs: made read-only, with its
  SHA-256 recorded in a log. Its hash is re-verified immediately before the G1 verdict, and before the R1–R4 verdict
  if fits 3–5 run.
- **Self-tests, before freezing:**
  - on session 2's outputs (`fullplanck/tier2_rerun/`), which have no polish rounds. The script must reproduce
    session 2's published values, including S = 0.4022 and 0.8739 (section "Session 2 — G1 rerun …");
  - on study 2's fresh-start outputs (`fullplanck/tier2_explore2/`: `logs/base_fit{1,2}_*.json` and
    `logs/e2e_fit{1,2}_*.log`). It must reproduce study 2's step-3 values: S = 0.0250 and 0.1618, with 8/8 in the
    window for each fit (section "Step 3 …").
- **Self-tests are reporting only.** They check the script; they are not G1 results and count toward nothing.

## 8. Known limits, stated plainly

**Crash avoidance is empirical, not structural.**
- In study 2, candidate (ii) ran with no failure: 24 base runs and 97 polish rounds over 40 start-procedures
  (16 in step 2, 16 in step 3, 8 in step 4). Source: section "Step 5 — recommendation".
- Study 2 traced the earlier crash to Py-BOBYQA's geometry step returning x_opt. That happens when the Lagrange
  polynomial of the point being replaced has zero gradient there (section "Step 1 — the crash: cause found").
- `rhobeg` 0.1 avoids that trap at the first reduction of ρ: 10ρ = 0.224 is more than the 0.141 distance of the
  initial pair points. At ρ = `rhoend` that protection is gone (section "Step 5 — recommendation", caveats).
- If a polish round fails in the third attempt, §6 applies.

**Fits 3–5 were not tested.**
- No model with free Σmν was built or run in either study.
- The closest test is CPL with Σmν fixed: 9 parameters, npt 55, no failure. Fit 5 has 10 parameters and npt 66.
- **Read from the installed source, not tested:**
  - Py-BOBYQA 1.5.0 does not move a start point away from a bound. `solve()` only clips x0 into the box
    (`pybobyqa/solver.py`, lines 809–818).
  - Its coordinate-direction initialisation steps −δ along each coordinate, unless the start is within 0.01δ of that
    coordinate's lower bound (`pybobyqa/controller.py`, `initialise_coordinate_directions`).
  - cobaya clips parameters to the prior bounds before evaluating (`samplers/minimize/minimize.py`,
    `inv_affine_transform`).
  - So a start whose Σmν lies above the 1e-5 eV edge by more than 0.01 and less than one initial trust radius (in
    cobaya's scaled units) would place one initial interpolation point outside the prior box. cobaya would evaluate
    that point at the edge.
  - This applies to the base stage (`rhobeg` 1.0), already frozen in 1fd858e, and to the polish (`rhobeg` 0.1).
  - Neither study exercised it. This amendment states it and changes nothing about it.
  - With this data combination the free-Σmν minimum may lie at or near the lower prior edge. The boundary behaviour
    described here may therefore well be exercised in fits 3–5. This is untested.

**Scatter measured in study 2** (S = max − min total χ² over in-window starts; spread = max − min −log posterior):

| model | n | step | S | −log-post spread | source (study 2 section) |
|---|---:|---|---:|---:|---|
| fit 1 | 7 | 2 (session-2 endpoints) | 0.0159 | 0.00009 | "Step 2 summary" |
| fit 1 | 7 | 3 (fresh starts) | 0.0250 | 0.00012 | "Step 3 …" |
| fit 2 | 8 | 2 | 0.1994 | 0.00523 | "Step 2 summary" |
| fit 2 | 8 | 3 | 0.1618 | 0.00241 | "Step 3 …" |
| CPL, Σmν fixed | 9 | 4 (fresh starts) | 0.2812 | 0.03564 | "Step 4 …" |

- **S grows with the number of parameters across the three models tested: 7 → 8 → 9.** Each step up is also a
  different model, so the studies do not separate dimension from model.
- **What limits S:** starts end on the 0.001 per-round rule while still apart. In fit 2 they were up to 0.0026 above
  the best start; in CPL, 0.0286 (`fullplanck/tier2_explore2/logs/stop_analysis.log`).
- **The fit-2 target was not met.** S ≤ 0.1 was study 2's design target, and fit 2 did not meet it. The G1 guard stays
  at 0.5.
- **No scatter has been measured for fits 3–5.** Under 1fd858e §5, the R1–R3 verdict is withheld if Δχ²(fit 4 − fit 3)
  lies within S of −9.0 or −2.0. An S like CPL's 0.2812 would withhold it for any Δχ² within 0.2812 of either
  boundary.

**Measured cost** (study 2, 5-round cap, `OMP_NUM_THREADS=1`, one process per start, heavy load; section "Step 5 —
recommendation"; `fullplanck/tier2_explore2/logs/cost_step3.log`, `cost_step4.log`, `nf_per_round.log`):

| model | base evaluations per start | polish evaluations per start (rounds) | per-start total | all 8 starts |
|---|---|---|---|---:|
| fit 1 | 50–310 | 71–243 (1–2) | 257–426 | 2648 |
| fit 2 | 211–539 | 95–500 (1–5) | 457–918 | 5517 |
| CPL, Σmν fixed | 57–427 | 320–794 (2–5) | 428–1182 | 6992 |

- **One polish round** costs 71–169 evaluations (fit 1), 90–227 (fit 2) and 111–225 (CPL).
- **Wall time per start** under study 2's load: base 9.2–44.8, 46.8–90.0 and 14.6–72.2 min; polish 6.5–19.3, 12.7–43.0
  and 31.6–53.9 min.
- **Not measured:** wall time at the load of an official run; the cost of rounds 6–10; the cost of fits 3–5.

## 9. Later amendments

If the third attempt records any fit as minimizer-failed, any later amendment must improve the minimizer itself
(settings, algorithm, or number of starts). It may not narrow the 0.25 window, raise the 0.5 guard, or lower the 4-of-8
requirement.

No goalposts move.
