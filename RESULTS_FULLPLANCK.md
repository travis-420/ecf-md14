# Full-likelihood run — results (kill condition 2)

**Date:** 2026-07-08
**Protocol:** `SETUP_MACBOOK.md`
**Data combination:** Planck 2018 high-ℓ plik-lite TTTEEE (clik-free native) + τ prior
N(0.0544, 0.0073²) replacing low-ℓ EE + DESI DR2 BAO (all tracers) + Pantheon+ SN.
**Cosmology:** one massive ν, Σmₙ = 0.06 eV; halofit=mead.

---

## VERDICT — kill condition 2 does NOT fire

The ECF preference **held and sharpened** under the full likelihood:

> **~2.8σ (compressed prior)  →  ~3.4σ (full likelihood)** — inside the pre-registered 3–4σ band.

ECF is favoured over ΛCDM at **Δχ² = −11.64 for one extra parameter (≈3.4σ)**, and it
beats CPL while spending one fewer parameter (CPL: Δχ² = −8.85 for two extra params, ≈2.5σ).
The full likelihood did **not** erase the preference, so the note does not require the
kill-condition-2 update — the honest update is that the preference is confirmed/sharpened.

---

## 1. Best-fit comparison (direct minimization — `--minimize`)

| model | −log post | χ²_total | χ²_CMB | χ²_BAO | χ²_SN | Δχ² vs ΛCDM | extra params | significance |
|-------|----------:|---------:|-------:|-------:|------:|------------:|:-----------:|:------------:|
| ΛCDM  | 986.022   | 2005.532 | 587.422 | 12.451 | 1405.658 | —        | —  | —      |
| CPL (w₀,wₐ) | 982.806 | 1996.686 | 583.390 | 10.259 | 1403.037 | **−8.85** | 2 | ~2.5σ |
| **ECF (τ_ecf)** | **981.939** | **1993.893** | 581.964 | 9.380 | 1402.550 | **−11.64** | 1 | **~3.4σ** |

Significance (Wilks, χ² survival function):
- CPL: Δχ² = 8.846, 2 dof → p = 0.012 → **2.51σ**
- ECF: Δχ² = 11.638, 1 dof → p = 6.5×10⁻⁴ → **3.41σ**

ECF improves the fit in **every** data block individually (CMB, BAO, and SN all drop),
not just in aggregate.

### Best-fit dark-energy parameters (at the minima)
- **CPL:** w₀ = **−0.8475**, wₐ = **−0.5776**  (thawing / evolving DE: w₀ > −1, wₐ < 0 — the canonical DESI signature)
- **ECF:** τ_ecf = **2.1938**  (consistent with the pre-registered reference value 2.1)

---

## 2. Marginalized posteriors (MCMC)

### τ_ecf — ECF model  (certified converged, see §3)
Pooled 6-chain MPI run, 30% burn-in removed, **88,094 weighted samples**:

| quantity | value |
|----------|-------|
| mean     | **2.584** |
| median   | 2.405 |
| std      | 0.774 |
| 68% CI   | **[1.894, 3.277]**  (+0.87 / −0.51 about median) |
| 95% CI   | [1.581, 4.604] |
| prior    | [0.3, 6.0] |

The posterior is a clean unimodal peak (mode ≈ 2.1–2.4) with a positive-skew right tail.
The 95% lower bound (1.58) sits far above the prior floor (0.3) → **the data constrain
τ_ecf**; this is a detection, not a prior-return. H₀ in the ECF model = 67.98.

### w₀, wₐ — CPL model
30% burn-in removed:

| param | mean | 68% CI |
|-------|-----:|--------|
| w₀ | −0.835 | [−0.890, −0.781] |
| wₐ | −0.626 | [−0.854, −0.400] |

wₐ is bounded away from 0 at ~2.7σ (marginalized) — evolving DE preferred over w₀-only.

---

## 3. Convergence proof (R−1)

| chain | sampler | R−1 (means) | criterion | status |
|-------|---------|------------:|-----------|:------:|
| ΛCDM  | mcmc, 1 chain (within-chain GR) | 0.0168 | < 0.02 | ✅ converged |
| CPL   | mcmc, 1 chain (within-chain GR) | 0.0173 | < 0.02 | ✅ converged |
| ECF   | mcmc, **6 MPI chains (cross-chain GR)** | **0.0190** | < 0.02 | ✅ converged |

- ECF cobaya cross-chain: `The run has converged!` — R−1(means) = 0.0190, R−1(bounds) = 0.129
  (bounds threshold Rminus1_cl_stop = 0.2, passed), 125,848 total accepted steps
  (~20,900 per chain × 6).
- ECF independent cross-check with GetDist on the 6 pooled chains:
  **worst-eigenvalue R−1 = 0.0187 < 0.02**.

**Note on ECF convergence method:** a single-process ECF chain stalled at R−1 ≈ 0.05
because of a tight H₀–τ_ecf degeneracy (covmat covariance 0.369) that a diagonal proposal
mixes through very slowly (acceptance climbed to 0.76 = steps too small). It was replaced
by a **6-chain MPI run seeded with the learned covariance matrix** (`chains/ecf.covmat`),
which converged cleanly. τ_ecf was stable across the entire stalled single chain
(segment means 2.55/2.58/2.47/2.60/2.59), so the central result was never in doubt — only
the formal R−1 certificate required the multi-chain run.

---

## 4. Validation trail (gates passed before any chain)

- **Physics gate** (`test_module.py`): CAMB reproduces the reference expansion history
  H(z)/H₀ for τ = 1.5, 2.1, 3.0 to **< 0.3%** (max diff 0.093%). → `PASS`.
- **ECF cobaya injection** (`test_cobaya_injection()`): the `DarkEnergyPPF` w(a) table
  injected through the cobaya theory wrapper reproduces the reference to the same 0.3%.
  → `PASS`.
- **ΛCDM sanity gate:** marginalized Ωm = 0.302 ± 0.004, H₀ = 68.34 ± 0.30,
  Ωbh² = 0.02252 ± 0.00013 — all consistent with published Planck+DESI+SN ΛCDM. → likelihood
  stack trusted.

---

## 5. Environment / reproducibility

- Python **3.12** (venv `venv312`), numpy **2.1.3**, scipy **1.14.1**, camb **1.6.6**, cobaya **3.6.2**.
- MPI: MPICH 5.0.1 + mpi4py 4.1.2 (Open MPI 5.0.9's PRRTE launcher segfaults on this macOS,
  so MPICH was used instead).
- Likelihood data installed under `./packages`.

**Fixes applied to the kit during execution (physics unchanged):**
1. Rebuilt the environment on Python 3.12 with numpy 2.1.3 / scipy 1.14.1 — the default
   Python 3.14 + scipy 1.18 stack crashes CAMB's BBN `Y_He` scalar shim
   (`RectBivariateSpline` returns a shape-(1,) array under numpy 2.5). camb 1.6.6 (identical
   Fortran) is unchanged, so the physics is identical.
2. `ecf.yaml` latex string `\tau_{\rm ECF}` was invalid unquoted YAML (the `{…}` parses as a
   flow map) → quoted.
3. `ecf_theory_cobaya.py` injection point was wrong for cobaya 3.6.2: `CAMB.set()` is called
   only from the `camb.transfers` helper, so `tau_ecf` must be claimed by that helper. Fixed
   by subclassing `CambTransfers` (advertises `tau_ecf`) and overriding `get_helper_theories`;
   the DarkEnergyPPF injection logic itself is unchanged and validated against the reference.

## 6. Artifacts

- Chains: `chains/{lcdm,cpl,ecf_mpi}.*.txt`  (single-chain `chains/ecf.1.txt` retained; superseded by MPI run)
- Minima: `chains/{lcdm,cpl,ecf}.minimum.txt`
- Configs: `lcdm.yaml`, `cpl_full.yaml`, `ecf_full.yaml`, `ecf_mpi.yaml`
- Learned proposal covariance: `chains/ecf.covmat`
