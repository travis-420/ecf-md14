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
