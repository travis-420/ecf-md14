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

«STEP3BODY»

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

«STEP4BODY»
