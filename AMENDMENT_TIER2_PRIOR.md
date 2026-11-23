# Amendment to PREREG_NEUTRINO_TIER2.md: Σmν prior lower edge

**Status:** drafted 2026-11-23, BEFORE any free-Σmν fit (fits 3, 4, 5) was executed. The git
timestamp of the commit that adds this file governs. It amends `PREREG_NEUTRINO_TIER2.md` as frozen at
commit `068a9ab`.

When this was drafted, gate G0 had been run and passed. The G1 fixed-Σmν minimizations
(fits 1 and 2) were running, and their results had not been inspected. G1 is unaffected by this
amendment because Σmν is fixed at 0.06 eV in fits 1 and 2.

## The change

| | registered | amended |
|---|---|---|
| Σmν prior, lower edge | 0.0 eV | **1e-5 eV** |
| Σmν prior, upper edge | 1.0 eV | 1.0 eV (unchanged) |
| prior shape | flat | flat (unchanged) |

Nothing else changes.

## Reason: CAMB returns corrupted χ² at exactly Σmν = 0.0

In the registered stack (camb 1.6.6, cobaya 3.6.2, kit `extra_args` with
`num_massive_neutrinos: 1`), χ² evaluated at exactly Σmν = 0.0 is wrong whenever the model was
first evaluated at Σmν > 0. A minimizer run is always in that state, because every start has
Σmν > 0.

Mechanism: cobaya's CAMB wrapper (`cobaya/theories/camb/camb.py`, `CAMB.set`) builds
`_base_params` once, from the first point it evaluates, and copies it for every later call. With
a first point at Σmν > 0, the copy carries `num_nu_massive = 1`. When CAMB's `SetNeutrinoHierarchy`
is then called with `omnuh2 = 0`, it sets `num_nu_massless = 3.044` but does not reset
`num_nu_massive`. The result is an extra zero-mass "massive" state, **N_eff = 4.0587** instead of
3.044. The registered model's Σmν = 0 limit is three massless species with N_eff = 3.044.

The corrupted values are about 14,000–15,500 χ² units too high (numbers in the table below).
Fixed-Σmν fits are not affected.

## Measurement: χ² at Σmν = 1e-5 eV equals the correct Σmν = 0 value

**Script:** `fullplanck/tier2/mnu_amendment_measure.py`.
**Log:** `fullplanck/tier2/logs/mnu_amendment_measure.log`.
**Environment:** the July venv (Python 3.12.12, numpy 2.1.3, scipy 1.14.1, camb 1.6.6, cobaya 3.6.2)
and the July likelihood data. No fitting is involved; these are single likelihood evaluations.

**Models:** the free-Σmν models of fits 3 (ΛCDM + Σmν), 4 (ECF + Σmν) and 5 (CPL + Σmν), built
by `fullplanck/tier2/make_yamls.py` from the kit yamls. The script asserts the prior is the
registered [0.0, 1.0]. The likelihood stack is the registered one: plik-lite TTTEEE native,
τ prior, DESI DR2 BAO, Pantheon+.

**Test points:** two per model, all non-Σmν parameters held fixed:
1. the certified best-fit point of the matching fixed-Σmν model (`fullplanck/chains/{lcdm,ecf,cpl}.minimum.txt`);
2. the kit `ref` point (logA 3.044, ns 0.965, H0 67.7, ombh2 0.02237, omch2 0.1195, tau 0.0544,
   A_planck 1.0, and tau_ecf 2.1 or w −0.86, wa −0.5).

**Procedure at each point:**
- **Correct Σmν = 0 reference:** a freshly built model whose *first* evaluation is Σmν = 0.0.
  The read-back CAMBparams confirm `num_nu_massive = 0`, `num_nu_massless = 3.044`, N_eff = 3.044.
- **State (i), Σmν = 1e-5:** a second fresh model, first evaluated at Σmν = 0.06 (as every
  minimizer run is), then at Σmν = 1e-5. Read-back: `num_nu_massive = 1`,
  `num_nu_massless = 2.0293`, N_eff = 3.044.
- **State (ii), Σmν = 1e-5:** the Σmν = 0-initialized model, evaluated at 1e-5.
- **Defect:** the state-(i) model evaluated at exactly Σmν = 0.0, which reads back N_eff = 4.0587.

**Results** (total χ² = plik-lite + DESI DR2 + Pantheon+):

| model | test point | χ²(Σmν = 0, correct) | χ²(1e-5, state i) | diff (i) | diff (ii) | χ²(0.0, corrupted) |
|---|---|---:|---:|---:|---:|---:|
| ΛCDM + Σmν (fit 3) | certified ΛCDM best-fit | 2031.946442 | 2031.946442 | −0.000000 | −0.000000 | 17183.9401 |
| ΛCDM + Σmν (fit 3) | kit ref point | 2026.587261 | 2026.587261 | +0.000000 | +0.000000 | 16800.3127 |
| ECF + Σmν (fit 4) | certified ECF best-fit | 2023.218342 | 2023.218343 | +0.000001 | +0.000001 | 16979.9646 |
| ECF + Σmν (fit 4) | kit ref point | 2036.408237 | 2036.408237 | +0.000000 | +0.000000 | 17304.4489 |
| CPL + Σmν (fit 5) | certified CPL best-fit | 2025.150817 | 2025.150848 | +0.000032 | +0.000032 | 17052.1532 |
| CPL + Σmν (fit 5) | kit ref point | 1998.425423 | 1998.425400 | −0.000023 | −0.000023 | 16130.9485 |

**Max |χ²(1e-5) − χ²(0, correct)| over all 12 comparisons = 3.2 × 10⁻⁵.** The per-likelihood
components agree to the same level (see log). For scale, the G1 tolerance is 0.5, and the
narrowest outcome boundary is a whole χ² unit.

Supporting check (`fullplanck/tier2/logs/mnu_edge_check.log`): at the certified ΛCDM and ECF
best-fit points, χ² at Σmν = 1e-8, 1e-6 and 1e-4 eV equals the correct Σmν = 0 value to 4
decimals (2031.9464 and 2023.2183).

So for any parameter set, the amended prior [1e-5, 1.0] eV reaches the correct Σmν = 0 χ²
to within 3.2 × 10⁻⁵, and it never evaluates the corrupted point.

## What does not change

No threshold, gate or outcome rule in `PREREG_NEUTRINO_TIER2.md` changes:
- **G0, G1:** definitions and tolerances unchanged (test_module.py < 0.3%; |Δχ²| ≤ 0.5 per fit and
  on the certified Δχ² = −11.64).
- **R1–R4:** unchanged. R1 is Δχ² ≤ −9.0 with τ_ecf in [1.894, 3.277]. R2 is −9.0 < Δχ² ≤ −2.0,
  or τ_ecf outside the 68% interval but inside the 95% interval [1.581, 4.604]. R3 is Δχ² > −2.0,
  or τ_ecf outside the 95% interval. R4 reports χ²(fit 2) − χ²(fit 3).
- **Unchanged otherwise:** the likelihood stack, the fit list (1–5), the minimizer procedure,
  the neutrino settings (`num_massive_neutrinos: 1`, CAMB defaults `neutrino_hierarchy='degenerate'`,
  `nnu = 3.044`), and the Σmν upper edge (1.0 eV).

No goalposts move.
