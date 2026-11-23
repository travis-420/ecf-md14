# Pre-registration: free-neutrino-mass robustness, Tier 2 (full plik-lite likelihood)

**Frozen:** on commit of this file to github.com/travis-420/ecf-md14, BEFORE any
free-Σmν fit at Tier 2 is executed. The git timestamp of that commit governs.
Drafted 2026-11-23 UTC.

## Question

The certified Track A result (full-Planck stack: Δχ² = −11.64 vs ΛCDM, τ_ecf = 2.405
+0.87/−0.51) was obtained at fixed Σmν = 0.06 eV. Does the ECF preference survive when
Σmν is a free parameter in the same full likelihood, or is the one-parameter advantage
absorbed by neutrino-mass freedom, with which late-time expansion is partially
degenerate?

## Prior result this run supersedes in rigor (caveat leads)

A Tier 1 run (2026-07-16, compressed Planck distance priors + DESI DR2 BAO + Pantheon+,
not public, not blind-replicated) found Δχ²(ECF+mν − ΛCDM+mν) = −7.02 against a
pre-registered survival threshold of −6.0, τ_ecf = 2.118. Its own registered limitation:
the compressed CMB prior cannot constrain Σmν (both fits ran to the 0.6 eV prior edge
for <0.4 units of χ²). Tier 1 is indicative only. Tier 2 is the certifiable version.

## Likelihood stack (identical to the certified v1.15/v1.16 kit except Σmν)

- planck_2018_highl_plik.TTTEEE_lite_native
- Gaussian optical-depth prior N(0.0544, 0.0073)
- bao.desi_dr2
- sn.pantheonplus
- Theory: CAMB via the published kit (fullplanck/ecf_theory_cobaya.py, ecf_physics.py).
  Neutrino settings (number of massive species, hierarchy) are copied unchanged from
  the certified kit's yaml files, with only Σmν freed; the settings used are recorded
  verbatim in the results file at gate G1.
- Σmν prior: flat [0.0, 1.0] eV.

Registered limitations, stated now:
1. No Planck lensing likelihood, to match the certified stack. Σmν constraints will be
   weaker than published Planck+lensing values; this run does not measure Σmν, it
   measures whether ECF's advantage survives Σmν freedom.
2. Pantheon+ is used to match the certified stack. The SN-Unite host-mass issue
   (queue item 3′) is a separate gate and is not addressed here.

## Gates before any free-Σmν fit (never proceed past a failed gate)

- G0 — Physics gate: test_module.py must PASS against reference_checkpoints.csv
  (all checkpoints < 0.3%).
- G1 — Baseline reproduction: minimizer runs of ΛCDM and ECF at fixed Σmν = 0.06 eV
  must reproduce the certified best-fit χ² values from the published
  fullplanck/chains/*.minimum.txt files within |Δχ²| ≤ 0.5 each, and the
  certified Δχ² = −11.64 within ±0.5. If G1 fails, stop and diagnose; no free-Σmν
  result from this session counts.

## Fits to run (cobaya minimizer, multiple starts; best χ² kept)

1. ΛCDM, Σmν = 0.06 fixed — gate G1
2. ECF, Σmν = 0.06 fixed — gate G1
3. ΛCDM + free Σmν — the equal-parameter rival to fit 2
4. ECF + free Σmν
5. CPL + free Σmν — context only, no threshold

Headline numbers come from minimizer best-fit χ². MCMC chains, if run, are reported
as-is (posteriors on τ_ecf and Σmν) and do not change any outcome below.

## Pre-registered outcomes (frozen before running)

- **R1 — SURVIVES:** Δχ²(ECF+mν − ΛCDM+mν) ≤ −9.0 AND best-fit τ_ecf inside the
  certified 68% interval [1.894, 3.277]. Logged as "robust to free Σmν (full
  plik-lite likelihood, no lensing)"; no stronger language.
- **R2 — WEAKENED:** −9.0 < Δχ² ≤ −2.0, or τ_ecf outside the certified 68% but inside
  the 95% [1.581, 4.604]. Logged as weakened; the v2.0 note carries the
  neutrino-degeneracy caveat prominently, with the measured Δχ².
- **R3 — FAILS (fires):** Δχ² > −2.0, or best-fit τ_ecf outside the certified 95%
  interval. This does not retroactively kill the certified fixed-Σmν result (its
  scope was declared), but the v2.0 note MUST state in its abstract-level caveats
  that the ECF preference is not robust to free Σmν.
- **R4 — equal-parameter readout (no threshold, reported verbatim):** at equal
  parameter count, does the data prefer spending the extra parameter on τ_ecf
  (fit 2) or on Σmν (fit 3)? Report χ²(fit 2) − χ²(fit 3).

Threshold rationale: −2 is the AIC break-even for one parameter. −9.0 retains about
77% of the certified −11.64, close to the 79% Tier 1's −6.0 kept of its −7.61
baseline, so the two tiers are graded on nearly the same scale.

## Verification

Results are single-machine until blind-replicated under VERIFICATION.md's protocol
(verifier gets code and configs, not results; proves data fetch; never simulates).
No public claim beyond "indicative" before that replication.

No goalposts move after this line.
