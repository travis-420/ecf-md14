# Amendment to PREREG_NEUTRINO_TIER2.md: minimizer settings and selection rule

**Status:** drafted 2026-11-23, after session 1's G1 failure and BEFORE any rerun. The git
timestamp of the commit that adds this file governs. It amends `PREREG_NEUTRINO_TIER2.md` (frozen
at `068a9ab`), as already amended by `AMENDMENT_TIER2_PRIOR.md` (`37b8f12`). It governs a
**fresh session** that reruns G1 and then, only if G1 passes, fits 3, 4 and 5.

## Session 1 results stay on record

Session 1's G0 and G1 results are recorded as-is in `RESULTS_NEUTRINO_TIER2.md` and are **not
overwritten**. The rerun writes to a new output directory (`fullplanck/tier2_rerun/`). Its results
are appended to `RESULTS_NEUTRINO_TIER2.md` as a new, separately dated section, and session 1's
sections stay unchanged. Session 1 ran no free-Σmν fit, and none of its results count toward any
R1–R4 outcome.

## 0. Definitions, used everywhere in this amendment and in the results

- **Total χ²** = χ²(plik-lite TTTEEE native) + χ²(DESI DR2 BAO) + χ²(Pantheon+). This is cobaya's
  `chi2` column in `.minimum.txt`.
  - It **excludes** the Gaussian τ prior term.
  - It also excludes every other prior term: the A_planck Gaussian prior and the flat-prior
    normalizations.
  - Every χ² comparison, certified or rerun, uses this same quantity, so every comparison is
    like-for-like.
- **Confirmation that the certified values use this convention.** In each certified minimum file,
  the `chi2` column equals the sum of the three likelihood columns, and the τ prior is a separate
  column (`minuslogprior__tau_prior`):

  | file | sum of the three likelihood χ² | `chi2` | separate τ-prior column |
  |---|---|---:|---:|
  | `lcdm.minimum.txt` | 587.42243 + 12.450954 + 1405.6582 = 2005.5316 | **2005.5316** | 0.35721506 |
  | `ecf.minimum.txt` | 581.96364 + 9.3800487 + 1402.5496 = 1993.8933 | **1993.8933** | 0.3388505 |

  The certified values are also consistent with `minuslogpost = chi2/2 + minuslogprior`:
  1002.7658 − 16.744098 = 986.0217 (ΛCDM) and 996.94665 − 15.00728 = 981.9394 (ECF).
- **−log posterior** = cobaya's `minuslogpost`, the objective the minimizer minimizes, and
  **−2 log posterior** = 2 × `minuslogpost`.
  - −2 log posterior = total χ² + 2 × `minuslogprior`.
  - `minuslogprior` is the τ prior term plus the A_planck Gaussian prior plus the constant flat-prior
    normalizations.
  - Those constants are identical for every start of a given model, and for the July run of the same
    model. So within-fit and July-vs-rerun comparisons of −log posterior are like-for-like.
  - Cross-model differences of −2 log posterior include the models' different normalization
    constants. They are reported (§4) and used by no rule.

## 1. Selection rule

**For each fit, the selected result is the successful start (§2.4) with the lowest −log posterior,
which is the minimized objective. The total χ² reported for that fit is the total χ² at that
start.** The headline χ², Δχ², and the τ_ecf used for R1–R3 all come from the selected start. This
is the rule cobaya's `best_of` applies, and the one the certified July minimizations used.

**This replaces the lowest-χ² rule in an earlier, uncommitted draft of this amendment.** Selecting
on total χ² is biased. Near the minimum, the posterior is nearly flat along a direction where
likelihood χ² trades off against the τ prior. Picking the start with the lowest χ² favours whichever
start drifted furthest along that direction, toward a larger τ-prior penalty, rather than the start
that best minimized the objective.

Session 1 shows this. All five fit-1 starts lie within 0.078 of the best −log posterior, yet their
total χ² spans 0.98 (2004.78–2005.76). Their τ-prior term spans 0.2854–0.8150, which is 0.57–1.63
in χ² units.

**This rule was not chosen to pass G1.** Session 1 evaluated both readings of "best", and **both
failed G1**:

| reading | fit 1 χ² − certified | fit 2 χ² − certified | Δχ² − (−11.6383) | G1 |
|---|---:|---:|---:|---|
| lowest −log posterior (this rule) | −0.0815 | +0.4415 | **+0.5230** | FAIL |
| lowest total χ² | **−0.7477** | **−0.5665** | +0.1812 | FAIL |

(Source: `fullplanck/tier2/logs/G1_verdict.log`. Certified values: fit 1 = 2005.5316,
fit 2 = 1993.8933, Δχ² = −11.6383, quoted as −11.64 in the pre-registration.)

## 2. Minimizer settings

### 2.1 Stopping tolerance: `rhoend` 0.05 → **0.005**

Everything else stays at the cobaya 3.6.2 `minimize` defaults used in July and in session 1:
bobyqa, `rhobeg` 1.0 (fixed by cobaya), `ignore_prior: False` (−log posterior is minimized),
default `max_evals` and `confidence_for_unbounded`, and `best_of: 1` per process.

**Why, using session 1's measured spread at `rhoend` 0.05** (`fullplanck/tier2/logs/G1_verdict.log`,
`G1_collect.log`):

| fit | starts | −log post spread | total χ² spread | notes |
|---|---:|---:|---:|---|
| 1 (ΛCDM) | 5 | 0.0776 | **0.9808** | all 5 starts within 0.078 of the best −log post |
| 2 (ECF) | 5 | 1.9599 | **3.6105** | s1 stopped 1.96 above the best; without s1: −log post 0.2607, χ² 1.7212 |

In fit 1, the five starts reached the same −log-posterior minimum to within 0.078, yet the total χ²
read off at their stopping points still spans 0.98. That readout scatter is about twice the G1
tolerance of 0.5. `rhoend` is the final trust-region radius, in units of the certified covmat's
conditional widths. Making it 10× smaller shrinks the region where the minimizer can stop, and so
the χ² readout scatter at the selected start.

As a design target only, and assuming that scatter scales linearly with the stopping radius,
fit 1's 0.98 spread would fall to about 0.1. That is an assumption, not a measured number. The
rerun's own measured spread (§4) is what gets reported, and what the G1 spread guard (§3) and the
minimizer-limited rule (§5) use.

### 2.2 Number of starts: **8 per fit**, for each of fits 1–5

### 2.3 Start points and seeding

- **s0: the certified July best-fit point.** Every sampled parameter is set to its value in
  `fullplanck/chains/{lcdm,ecf,cpl}.minimum.txt`, as tracked in the repository at `37b8f12`:
  - fit 1 and fit 3: `lcdm.minimum.txt`
  - fit 2 and fit 4: `ecf.minimum.txt`
  - fit 5: `cpl.minimum.txt`
  - fits 3–5 also start at Σmν = 0.06 eV, the certified fixed value.
- **s1–s7: random starts.** Each is drawn with cobaya `seed = 2000 + k` for start s*k*. That gives
  seeds 2001–2007, which are new and not reused from session 1. The same *k* uses the same seed in
  every fit, so random starts are paired across models.
  - Each draw comes from these start-point (`ref`) distributions. They set only where the minimizer
    starts; they are not part of any prior:

    | param | distribution | param | distribution |
    |---|---|---|---|
    | logA | normal(3.044, 0.02) | A_planck | normal(1.0, 0.0025) |
    | ns | normal(0.965, 0.006) | tau_ecf | uniform[1.5, 4.5] |
    | H0 | normal(67.7, 1.0) | w | normal(−0.86, 0.10) |
    | ombh2 | normal(0.02237, 0.0002) | wa | normal(−0.5, 0.30) |
    | omch2 | normal(0.1195, 0.0015) | mnu | uniform[1e-5, 0.6] eV |
    | tau | normal(0.0544, 0.01) | | |

  - A draw with non-finite posterior is redrawn by cobaya, which is deterministic given the seed.

- **Step scaling (covmat):** the certified chain covariance for each model, used only to scale
  the minimizer's steps:

  | file | source | SHA-256 |
  |---|---|---|
  | `lcdm.covmat` | July kit | 6389f86fbd59fb43acb95f4c6192460bcc423c9bfc009459fa2cf67a7402b1ce |
  | `ecf.covmat` | `fullplanck/chains/` | 5590b82f782cb4daa455daccef51f13c537a2305da4deb984b00fe89dd8c5b97 |
  | `cpl.covmat` | July kit | 3daad637a048f6cab7aeffb739f9e7df270c67f051aa954033a4c8b4e161ba12 |

  Σmν's step scale comes from `proposal: 0.05` eV.

### 2.4 Successful (converged) starts

A start counts as converged, and counts toward selection, only if cobaya logs
`Run 1/1 converged.` (pybobyqa `EXIT_SUCCESS`) and the process exits 0. Unconverged starts are
still reported.

**Window and "stopped short".** A converged start is *in the window* if its −log posterior is
within 0.25 of that fit's best (lowest) −log posterior. That is 0.5 in −2 log posterior, the G1
tolerance in χ² units. A converged start outside the window is flagged **"stopped short"**. It is
reported and counted in the report, but it is excluded from the spread S (§4, §5). The selected
start (§1) is always in the window, by definition.

**4-of-8 rule.** If a fit has **fewer than 4 in-window converged starts out of 8**, it is recorded
as *minimizer-failed*:
- for fits 1–2, G1 is recorded as failed and the run stops;
- for fits 3–5, no R1–R4 outcome is declared.

This window and the 4-in-window requirement are **fixed before any rerun data exists**. They were
written after session 1, which ran 5 starts per fit at `rhoend` 0.05, and before any start of the
rerun had been executed.

For reference, applied to session 1's starts (`fullplanck/tier2/logs/G1_verdict.log`):
- **Fit 1:** all 5 starts are in the window, with −log posterior 0.0001–0.0776 above the best.
- **Fit 2:** only 3 are in the window.
  - In: s2 (best), s4 (+0.1324), s0 (+0.1748).
  - Stopped short: s3 (+0.2607) and s1 (+1.9599).
  - So fit 2 would have fallen below a 4-in-window requirement.

### 2.5 Unchanged from session 1

- **Likelihood stack:** unchanged.
- **Kit code:** `fullplanck/` at `37b8f12`.
- **Neutrino settings:** `num_massive_neutrinos: 1`, CAMB defaults.
- **Σmν prior:** flat [1e-5, 1.0] eV, per `37b8f12`.
- **Environment:** the July venv, with Python 3.12.12, numpy 2.1.3, scipy 1.14.1, camb 1.6.6 and
  cobaya 3.6.2.

Execution details such as thread count and parallelism are not part of the protocol.

## 3. G1: tolerance unchanged, plus July-suboptimal, readout-drift and rerun-worse clauses and a spread guard

G1's criteria and tolerance are **exactly as frozen**. Using the total χ² at each fit's selected
start (§0, §1):
- |χ²(fit 1) − 2005.5316| ≤ 0.5
- |χ²(fit 2) − 1993.8933| ≤ 0.5
- |Δχ²(fit 2 − fit 1) − (−11.6383)| ≤ 0.5

All three must hold.

**July-suboptimal clause.** This fires whenever condition (b) holds for fit 1 or fit 2, whatever the
direction or size of that fit's total χ² difference from the certified value:
- (b) the selected −log posterior is lower than the certified July `minuslogpost` by more than 0.25
  (equivalently, −2 log posterior lower by more than 0.5, the G1 tolerance in χ² units).

Condition (a), which an earlier version of this draft also required (selected total χ² lower than
the certified July total χ² by more than 0.5), is no longer required.

The certified July `minuslogpost` values are 986.0217 for fit 1 and 981.9394 for fit 2. Condition (b)
requires the rerun to have actually found a better minimum of the objective. A χ² readout that drifted
along the flat direction is not enough.

If the clause fires:
- G1 is recorded as **FAILED: July certified value suboptimal**.
- The run stops, and fits 3–5 are not run.
- The certified numbers are re-derived and corrected publicly in an erratum before any further
  Tier 2 run.

If the July-suboptimal clause does not fire, there are three cases:
- If the selected −log posterior of fit 1 or fit 2 is more than 0.25 above its certified July
  `minuslogpost`, the rerun-worse case below applies, whether or not the G1 criteria pass.
- If the selected −log posterior of both fit 1 and fit 2 is within 0.25 of its certified July
  `minuslogpost`, and any G1 criterion fails, the July readout-drift case below applies.
- If both are within 0.25 and all three G1 criteria pass, G1 passes, unless the 4-of-8 rule (§2.4)
  or the G1 spread guard records fit 1 or fit 2 as minimizer-failed (see the precedence rule below).

**G1 is never loosened to pass.**

For reference, session 1 would not have triggered this clause under the selection rule in §1:
- fit 1: total χ² −0.0815 vs certified, −log posterior −0.0153;
- fit 2: total χ² +0.4415, −log posterior −0.0191.

**July readout-drift case.** This applies if ANY of the three G1 criteria fails (fit 1 χ², fit 2
χ², or the Δχ² criterion) while the selected −log posterior of BOTH fit 1 and fit 2 is within 0.25
of its certified July `minuslogpost`. Then:
- G1 is recorded as **FAILED: certified χ² is a drifted readout**.
- The run stops, and fits 3–5 are not run.
- The certified χ² values, and the headline Δχ² = −11.64, are re-derived at the rerun's selected
  minima and corrected publicly in an erratum before any further Tier 2 run.

**G1 is never loosened to pass.**

Session 1's reading-A result would have fired this clause. Under the selection rule in §1:
- the χ² differences from certified were −0.0815 (fit 1) and +0.4415 (fit 2);
- the Δχ² difference was +0.5230, so the Δχ² criterion fails;
- both −log posteriors were within 0.25 of July's (−0.0153 and −0.0191).

That check applies this clause alone. Session 1 ran 5 starts at `rhoend` 0.05, and its fit 2 would
also have fallen short of the 4-in-window requirement in §2.4.

**Rerun-worse case.** This applies if the selected −log posterior of fit 1 or fit 2 is HIGHER than
its certified July `minuslogpost` by more than 0.25. The rerun did not reach July's minimum. Then:
- that fit is recorded as minimizer-failed;
- G1 is recorded as failed;
- the run stops, and fits 3–5 are not run;
- no erratum follows from that fit's own result, whatever its χ² reads. This does not cancel a
  July-suboptimal erratum triggered by the other fit (see the precedence rules below).

**G1 spread guard.** If S (the in-window spread of total χ², §4) of fit 1 or fit 2 exceeds 0.5,
the G1 tolerance, that fit is recorded as minimizer-failed for G1, with the same consequences and the
same precedence as a 4-of-8 failure: G1 is recorded as failed, the run stops, the readout-drift clause
is not declared, and no erratum follows from that run; the July-suboptimal clause still fires if its
condition holds. This guard is fixed before any rerun data exists. It can never turn a G1 failure
into a pass. If a rerun is recorded as minimizer-failed, any later amendment must improve the
minimizer itself (settings, algorithm, or number of starts). It may not narrow the 0.25 window,
raise the 0.5 guard, or lower the 4-of-8 requirement.

Session 1's S values under this guard are below. They use the §2.4 window, with 5 starts per fit
at `rhoend` 0.05:
- **Fit 1:** S = 0.9808. All 5 starts are in the window, with total χ² 2004.7839–2005.7647.
- **Fit 2:** S = 0.7132. The in-window starts are s2, s4 and s0, with total χ² 1994.3348–1995.0480.

Both exceed 0.5, so both fits would have been recorded as minimizer-failed for G1.

**Errata quote S.** Any erratum under this section quotes each corrected χ² value together with that
fit's S (§4), taken from the run that produced the corrected value.

**Precedence when a fit is minimizer-failed by the 4-of-8 rule (§2.4) or the G1 spread guard, and a
named clause also applies.** Record both labels. Then:
- **July-suboptimal clause:** it still fires, and its erratum still follows. A single converged start
  with a lower −log posterior proves July was not at the minimum. But the corrected certified values
  must come from a re-derivation in which fits 1 and 2 each satisfy the 4-of-8 rule and the G1 spread
  guard.
- **Readout-drift clause:** it is NOT declared when fit 1 or fit 2 is minimizer-failed (by the
  4-of-8 rule or the G1 spread guard), because a minimizer-failed fit's χ² readout is not trusted.
  G1 is recorded as **failed: minimizer-failed**, and no erratum follows from that run.

**Precedence when the July-suboptimal clause and the rerun-worse case both apply.** This is the
case where one fit's selected −log posterior is more than 0.25 below July's and the other's is more
than 0.25 above. Record both labels. The July-suboptimal erratum still follows. But the corrected
certified values must come from a re-derivation in which neither fit 1 nor fit 2 is minimizer-failed,
by the 4-of-8 rule (§2.4), the rerun-worse case, or the G1 spread guard.

## 4. Reporting, for every fit (1–5)

Report:
- **the number of converged starts out of 8**, and how many of them are in the window versus
  flagged "stopped short" (§2.4);
- every start: its start point, converged or not, in-window or "stopped short", −log posterior,
  −log posterior minus the fit's best, **−2 log posterior**, total χ², the three per-likelihood χ²
  values, the τ-prior term (2 × `minuslogprior__tau_prior`, in χ² units), and τ_ecf / Σmν / w, wa
  where present;
- the selected start (§1), with its −log posterior and its total χ²;
- **S, the in-window spread:** max − min total χ² over that fit's in-window converged starts
  (§2.4). This is the spread used by §3 and §5.
- For transparency, also the max − min total χ² over *all* converged starts, including those that
  stopped short. This number is reporting only, and no rule uses it.
- **Cross-model −2 log posterior differences** (reporting only; no rule uses them). For the pairs
  (fit 2, fit 1) and (fit 4, fit 3), at the selected starts, report:
  - Δ(−2 log posterior) = 2 × (`minuslogpost` of the first fit − `minuslogpost` of the second);
  - the same difference net of the constant flat τ_ecf prior-volume term:
    Δ(−2 log posterior) − 2 ln 5.7, where 2 ln 5.7 = 3.4809.

  **Where the 3.4809 comes from.** τ_ecf has a flat prior on [0.3, 6.0] (`fullplanck/ecf_full.yaml`),
  which is 5.7 wide. That adds ln 5.7 = 1.7405 to ECF's `minuslogprior`, and 2 ln 5.7 = 3.4809 to
  its −2 log posterior.

  **Check against the certified minimum files.** `minuslogprior__0` is −15.346131 for ECF and
  −17.101313 for ΛCDM, a difference of 1.755182. The expected difference is:
  - ln 5.7 = 1.740466, plus
  - the A_planck Gaussian-prior difference at the two best-fit A_planck values (1.0010684 and
    1.0009786): 0.5[(0.0010684/0.0025)² − (0.0009786/0.0025)²] = 0.014706;
  - total 1.755172.

  The residual, 0.000010, comes from the files' 8-significant-digit A_planck values. All other flat
  priors are identical in the two models. In the (fit 4, fit 3) pair, the Σmν flat prior is the same
  in both fits and cancels.

  Reference values:

  | pair | source | Δ(−2 log posterior) | net of 2 ln 5.7 |
  |---|---|---:|---:|
  | (fit 2, fit 1) | July certified | −8.1647 | −11.6456 |
  | (fit 2, fit 1) | session 1, selected starts (§1 rule) | −8.1721 | −11.6530 |
  | (fit 4, fit 3) | July / session 1 | not available (never run) | not available |

  - The July −8.1647 is 2 × (981.93936 − 986.0217).
  - The session-1 −8.1721 is from `fullplanck/tier2/logs/G1_verdict.log`.
  - The July net value differs from the certified Δχ² (−11.6383) by −0.0073. That is the τ-prior
    difference, 2 × (0.3388505 − 0.35721506) = −0.0367, plus the A_planck-prior difference,
    2 × 0.014706 = +0.0294.

−2 log posterior and the τ-prior term are **reporting only**, and no rule uses them. The rules are
stated in terms of −log posterior, which is used by:
- the selection rule (§1);
- the window and the 4-of-8 rule (§2.4), whose window also defines the spread S used in §3 and §5;
- the G1 clauses (§3).

## 5. Outcome rules: thresholds unchanged

Every R1–R4 threshold stays **exactly as frozen** in `PREREG_NEUTRINO_TIER2.md`:
- **R1:** Δχ²(fit 4 − fit 3) ≤ −9.0, AND τ_ecf in [1.894, 3.277].
- **R2:** −9.0 < Δχ² ≤ −2.0, OR τ_ecf outside [1.894, 3.277] but inside [1.581, 4.604].
- **R3:** Δχ² > −2.0, OR τ_ecf outside [1.581, 4.604].
- **R4:** χ²(fit 2) − χ²(fit 3), reported verbatim.

Here Δχ² and τ_ecf come from the selected starts.

**Minimizer-limited rule** (the owner's instruction from session 1, frozen here):
- Let S = max(S of fit 3, S of fit 4).
  - Each fit's S is its in-window spread (§2.4, §4): computed only over converged starts whose
    −log posterior is within 0.25 of that fit's best.
  - Starts flagged "stopped short" are excluded from S.
- If Δχ²(fit 4 − fit 3) lies within S of the −9.0 boundary or the −2.0 boundary, the R1/R2/R3
  verdict is reported as **minimizer-limited** and not declared.
- If fit 3 or fit 4 has fewer than 4 in-window converged starts, it is minimizer-failed (§2.4), and
  no R1–R4 outcome is declared.
- This rule changes no threshold. Its spread definition is fixed before any rerun data exists.

No goalposts move.
