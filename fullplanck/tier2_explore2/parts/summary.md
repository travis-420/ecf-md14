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
    (ii) full npt with `rhobeg` 0.1, (iii) Powell, (iv) full npt with random directions. «PARTIALSUM»
  - **(b), fit 1:** met by (i), (ii) and (iv), with S = 0.0205, 0.0159 and 0.0105.
  - **(b), fit 2:** met by none. Best was (ii) at S = 0.1994; then (i) 0.2416, (iv) «C4S2», (iii) «C3S2».
  - **What limits fit 2:** the 0.001 per-round stop rule ends starts while they are still up to 0.0026–0.0195 above
    the best start in −log post, depending on the candidate.
- **End to end from fresh starts** (step 3, candidate (ii), seeds 9001–9007):
  - no failure in 16 base runs and all their polish rounds;
  - fit 1: **S = 0.0250**, 8/8 in the window;
  - fit 2: **S = 0.1618**, 8/8 in the window.
- **Dimension test** (step 4, candidate (ii), CPL with Σmν FIXED at 0.06 eV, 9 parameters, **not fit 5**): «CPLSUM»
- **Recommendation** (step 5): freeze (ii) as a polish stage after the amendment's base minimization, with "a failed
  polish round makes the start not converged" as the failure rule, if a procedure must be frozen now. It does not meet
  the fit-2 target of S ≤ 0.1. What the data say would close that gap is stated in step 5, untested.
- **No G1 verdict, no comparison with the certified July values, no fit 3–5.**
