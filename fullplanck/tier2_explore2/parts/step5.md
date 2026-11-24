## Step 5 — recommendation

**Plain statement: no candidate met (a) and (b).**
- All four met (a) in step 2: none of the 64 start-procedures had a failed round. «PARTIAL5»
- None met (b), because on fit 2 none brought all 8 starts within S ≤ 0.1. The closest was (ii), with S = 0.1994.
- From fresh starts (step 3), (ii) gave fit-2 S = «E2ES2».

**Procedure I would freeze, if a procedure must be frozen now: candidate (ii), as a polish stage after the
amendment's base minimization.** It is the best measured option under the selection rule written before the
candidates ran:
- no failure anywhere (ii) ran in this study («NOFAIL»);
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
«COST»

**Caveats that come with this recommendation:**
- **It does not meet this brief's fit-2 target.** Fit-2 S was 0.1994 (step 2) and «E2ES2» (step 3), above 0.1. Both
  are below the amendment's G1 spread guard of 0.5, but that is a fact about the guard, not a pass of anything.
- **Its crash avoidance is empirical, not structural.**
  - Why (ii) avoids the trap at the first ρ reduction, from Py-BOBYQA 1.5.0's source: after an unsuccessful step it
    fixes geometry only for points farther than max(2Δ, 10ρ) from x_opt (`solver.py`, line 588). With `rhobeg` 0.1,
    the first reduction (`reduce_rho`) gives ρ = √20 × 0.005 = 0.0224. So 10ρ = 0.224 exceeds the √2 × 0.1 = 0.141
    distance of the initial pair points, and no geometry step targets them. With `rhobeg` 1.0, ρ becomes 0.0707 and
    10ρ = 0.707 < √2, which is the D1 sequence.
  - At ρ = `rhoend` that protection is gone. A geometry step can still target an initial pair point if no evaluation
    has improved on the start by then.
  - That did not happen in any of the «NROUNDS» (ii) rounds run here, but it is not ruled out.
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
