# Dark energy as a delayed response to cosmic structure formation: a one-parameter model confronted with DESI DR2, Pantheon+, and Planck distance priors

**Author:** Steven "Travis" Maurer, independent researcher
**Analysis assistance:** Numerical implementation and drafting assisted by Claude (Anthropic). All results are reproducible from the scripts accompanying this note.
**Date:** July 7, 2026
**Status:** Research note for public timestamping prior to the final DESI cosmology release. Not peer reviewed.

---

## Abstract

Recent DESI baryon acoustic oscillation (BAO) measurements, combined with supernova and CMB data, show a 3–4σ preference for an evolving dark energy equation of state, with best-fit reconstructions favoring a dark energy density that peaks near z ≈ 0.5 and an equation of state that crosses w = −1 — behavior that minimally coupled scalar fields cannot produce. We test a one-parameter phenomenological model in which the dark energy density is a delayed integral response ("leaky integrator") to the cosmic star-formation history: ρ′_DE(N) = S(N) − ρ_DE(N)/τ, where N = ln a, the source S is fixed to the measured Madau–Dickinson star-formation rate density (zero shape freedom), and τ is the sole new parameter. The model structurally guarantees a peaked ρ_DE and a phantom crossing. Fit jointly to DESI DR2 BAO (13 measurements), Pantheon+ supernovae (1,590 SNe, full systematic covariance), and Planck 2018 compressed distance priors, the model achieves Δχ² = −7.6 relative to ΛCDM with one additional parameter (τ = 2.1 +0.6/−0.4 e-folds), outperforming the two-parameter w₀wₐCDM parametrization in absolute fit quality (Δχ² = −6.4). It ranks first on AIC (−5.6) and ties ΛCDM on BIC (−0.2), while w₀wₐCDM is BIC-disfavored (+8.4). The preference is distributed nearly evenly across the three independent probes, survives removal of any single BAO tracer, and survives excision of all z < 0.1 supernovae. At the best-fit τ, the model's dark energy density peaks at z = 0.52. This is a ~2.8σ result and is not a detection; it is a falsifiable consistency, with kill conditions stated explicitly below. *(v1.1 update: kill condition 2 has since been executed — under the full Planck plik-lite likelihood the preference sharpened to Δχ² = −11.6, ≈3.4σ, and BIC now favors the model; see Addendum II.)*

---

## Status of this result (read first)

This note reports a **~2.8σ preference**, not a discovery. The claim being timestamped is narrower and stronger than "the model is correct": it is that a specific one-parameter, empirically sourced model **currently matches or exceeds the fit quality of the standard two-parameter evolving dark energy parametrization** on real published data, is **not penalized by Occam-style information criteria**, and makes **specific numerical predictions** (Section 7) that upcoming data releases will confirm or destroy. Two earlier variants of this idea were tested during this analysis and **failed**; they are documented in Section 6.4 because negative results constrain the idea's flexibility. The physical mechanism is unknown: τ is measured, not derived. No comprehensive literature search has been performed; conceptually adjacent prior work exists (memory-kernel/nonlocal cosmologies; cosmologically coupled black hole proposals) and priority is not claimed for the general idea, only documentation of this specific model, source, and test.

---

## 1. Motivation

The DESI DR2 BAO measurements, in combination with CMB and Type Ia supernova data, prefer an evolving dark energy equation of state over a cosmological constant at ~3–4σ depending on the supernova compilation. Two features of the preferred solutions are notable. First, the best-fit w₀wₐ reconstructions correspond to a dark energy density that **rises, peaks near z ≈ 0.5, and then declines** — the peak position is tightly constrained by the data even where the sharpness is not. Second, the equation of state **crosses w = −1** (phantom in the past, quintessence-like today), which no single minimally coupled scalar field can do.

Both features arise automatically in a model where dark energy is not an ingredient but a **delayed response to the universe's history of structure formation**. Cosmic star formation (a tracer of gravitational collapse, black hole formation, and accretion) rose, peaked at z ≈ 1.9, and has declined since. If dark energy integrates that history with a finite memory, its density necessarily rises while the source is strong, peaks after the source declines, and then drains — producing a peaked ρ_DE with a built-in phantom crossing, with no tuning.

The speculative motivation for the author (a broader set of conjectures termed the Entropic Coherence Framework, involving horizon thermodynamics and information saturation) is **not** tested here and should not be conflated with this note's content. What is tested is the minimal phenomenological reduction below.

## 2. The model

Let N = ln a. The dark energy density obeys a sourced-decay ("leaky integrator") equation:

    dρ_DE/dN = S(N) − ρ_DE(N)/τ

equivalently ρ_DE(N) = ∫ S(N′) e^−(N−N′)/τ dN′. The source is **fixed** to the Madau–Dickinson (2014) cosmic star-formation rate density,

    ψ(z) = 0.015 (1+z)^2.7 / [1 + ((1+z)/2.9)^5.6]  M⊙ yr⁻¹ Mpc⁻³,

normalized over the integration range (the overall amplitude is absorbed into Ω_DE, fixed by flatness). Sourcing per e-fold (S ∝ ψ) is the baseline; sourcing per unit time (S ∝ ψ/H) was tested as a robustness variant. **τ is the only new parameter.** The background is flat FLRW with fixed physical radiation density (massless neutrinos, N_eff = 3.046); ρ_DE → 0 before star formation begins, so early-universe physics (BBN, recombination, sound horizon) is untouched by construction.

Structural consequences, independent of τ: ρ_DE rises while S > ρ_DE/τ (giving w < −1), peaks when S = ρ_DE/τ, then declines (w > −1). The phantom crossing coincides with the density peak. The model **cannot** reproduce arbitrary w(z); it lives on a one-dimensional locus in the (w₀, wₐ) plane (Section 7), terminating at ΛCDM as τ → ∞.

Dark energy perturbations are neglected (smooth DE); the analysis is background-level only.

## 3. Data

- **DESI DR2 BAO:** 13 measurements (D_M/r_d, D_H/r_d, D_V/r_d across seven tracers, z = 0.295–2.33) with the official covariance, from the `desi_bao_dr2` files in the CobayaSampler/bao_data repository (DESI Collaboration 2025, arXiv:2503.14738).
- **Pantheon+ SNe:** 1,590 supernovae with z_HD > 0.01 and the full 1701×1701 statistical+systematic covariance (Brout et al. 2022; PantheonPlusSH0ES/DataRelease repository). The absolute magnitude M_B is profiled analytically. No SH0ES calibrator information is used.
- **Planck 2018 compressed distance priors:** (R, ℓ_A, ω_b) = (1.7493 ± 0.0047, 301.462 ± 0.090, 0.02239 ± 0.00015) with the published correlation matrix — the wCDM-derived set of Chen, Huang & Wang (2019, arXiv:1808.05724), appropriate for dark energy studies.

## 4. Method

Distances use a composite redshift grid to z = 1300. z* uses the Hu–Sugiyama fitting formula and z_drag the Eisenstein–Hu formula; sound horizons r*(ω_b, ω_m) and r_d(ω_b, ω_m) are computed by direct integration and calibrated once, multiplicatively, to the CAMB values at the Planck 2018 best-fit point (calibration factors 1.0058 and 0.9801, applied identically to all models). Free parameters: (Ω_m, H₀, ω_b) plus M_B (profiled) for ΛCDM; +τ for ECF-MD14; +（w₀, wₐ) for w₀wₐCDM (CPL). Minimization by multi-start Powell. The parameter count k includes M_B. N = 1,606 data points.

**Sanity anchor:** the ΛCDM joint fit returns Ω_m = 0.302, H₀ = 68.46, ω_b = 0.02254, r_d = 147.4 Mpc, and (for the late-time-only fit) Ω_m = 0.304 with χ²/dof = 0.886 on Pantheon+ — consistent with published analyses.

## 5. Results

**Gate B — BAO + SNe (no CMB):**

| Model | k | χ² | Δχ² | ΔAIC | ΔBIC | best fit |
|---|---|---|---|---|---|---|
| ΛCDM | 3 | 1416.81 | — | 0 | 0 | Ω_m = 0.304 |
| ECF-MD14 | 4 | 1411.66 | −5.16 | −3.16 | +2.22 | τ = 2.47 |
| ECF-MD14 (per-time) | 4 | 1412.36 | −4.45 | −2.45 | +2.93 | τ = 1.17 |
| CPL | 5 | 1412.22 | −4.60 | −0.60 | +10.16 | w₀ = −0.896, wₐ = −0.184 |

**Gate B.2 — BAO + SNe + CMB (main result):**

| Model | k | χ² | Δχ² | ΔAIC | ΔBIC | best fit |
|---|---|---|---|---|---|---|
| ΛCDM | 4 | 1420.11 | — | 0 | 0 | Ω_m = 0.302, H₀ = 68.46 |
| **ECF-MD14** | **5** | **1412.50** | **−7.61** | **−5.61** | **−0.23** | **Ω_m = 0.312, H₀ = 67.79, τ = 2.10** |
| CPL | 6 | 1413.72 | −6.39 | −2.39 | +8.38 | w₀ = −0.863, wₐ = −0.477 |

Adding the CMB anchor **strengthened** the preference (−5.2 → −7.6). The one-parameter model exceeds the two-parameter CPL fit in absolute χ² while using one fewer degree of freedom; it ranks first on AIC and is not penalized by BIC. The τ profile is a clean two-sided parabola: τ = 2.1 +0.6/−0.4 (Δχ² = 1), with τ ≈ 1 excluded by Δχ² ≈ +22 and τ ≈ 5 by ≈ +14 relative to the minimum. Translation: Δχ² = 7.6 for one degree of freedom corresponds to ~2.8σ; CPL's 6.4 for two corresponds to ~2.0σ. Three independent estimates of τ (2.47 late-time only; 1.65 projected against published DESI+CMB central values; 2.10 full anchored fit) are mutually consistent. Best-fit H₀ = 67.8 is Planck-concordant; like all thawing-type models including CPL, this does not alleviate the Hubble tension.

## 6. Robustness diagnostics

**6.1 Dataset decomposition.** The −7.61 splits nearly evenly: SNe −2.65, BAO −2.69, CMB −2.27. Pairwise ablations: BAO+CMB only, −5.45; BAO+SNe only, −5.16. Every pair of probes independently prefers the model.

**6.2 Leave-one-tracer-out (BAO).** Dropping each tracer and refitting both models: BGS −7.69, LRG1 −7.99, **LRG2 −4.29**, LRG3+ELG1 −6.87, ELG2 −7.18, QSO −7.68, Lya −8.66. LRG2 (z = 0.706) carries the largest single share, consistent with known discussion of the DESI LRG region, but a ~2σ preference survives its complete removal. No single point of failure. Removing Lya strengthens the preference, because Lya is the one measurement the model fits slightly worse than ΛCDM (pull 0.04σ → −0.95σ) — i.e., the model pays a visible price somewhere, as a physical (non-overfit) shape should. Under ΛCDM the largest tensions (LRG1 D_H −1.6σ, LRG2 D_H −1.8σ, LRG3 D_M −1.1σ) all shrink under ECF-MD14.

**6.3 Supernova structure.** Excising all z < 0.1 SNe (the calibration-sensitive rung; 630 removed) leaves Δχ² = −6.62. Binned Hubble residuals relative to ΛCDM are positive at low z and negative at intermediate/high z; the model's predicted Δμ(z) reproduces this sign pattern bin-by-bin (undershooting the 0.5–0.8 bin, overshooting 0.25–0.5, each at ~1–1.7σ). The SN preference is broad-based, not driven by one bin.

**6.4 Failed variants (negative results).** (i) Sourcing by the **linear growth rate** (S ∝ f·Ω_m) cannot reach the data-preferred region at any τ: its locus is confined to |wₐ| ≲ 0.4 at the relevant w₀, and it is observationally degenerate with CPL in distances (< 1 milli-mag) while fitting no better. Rejected. (ii) A **local Plinko/hidden-fluctuation picture** motivating early versions is excluded on general grounds (Bell-type constraints) and was abandoned before this analysis. The surviving model is therefore not infinitely flexible: the source choice matters, and the collapse-weighted/star-formation source is the one that works.

**6.5 Source-convention robustness.** Per-e-fold and per-unit-time sourcing both land in the data-preferred region (Gate B: −5.16 and −4.45; the per-time variant was not rerun with the CMB anchor — a known gap).

## 7. Falsifiable predictions and kill conditions

Because the model has one parameter, its CPL projection is a **curve**, not a plane. The measured τ = 2.1 +0.6/−0.4 confines the model to the segment:

| τ | (w₀, wₐ) | ρ_DE peak |
|---|---|---|
| 1.7 | (−0.836, −0.474) | z = 0.61 |
| 1.9 | (−0.854, −0.461) | z = 0.56 |
| **2.1** | **(−0.869, −0.449)** | **z = 0.52** |
| 2.3 | (−0.881, −0.440) | z = 0.48 |
| 2.7 | (−0.900, −0.426) | z = 0.42 |

At the best-fit τ the density peak lands at z = 0.52, coinciding with the peak position the DESI data independently constrain (z ≈ 0.5). The dated kill conditions:

1. **DESI final cosmology release (expected ~2027) and Euclid:** if the tightened (w₀, wₐ) contours exclude the segment above at high confidence — in particular if wₐ settles below ≈ −0.9 at w₀ ≈ −0.85, or if the reconstructed ρ_DE peak moves decisively away from z ≈ 0.4–0.6 — the model is falsified.
2. **Full-likelihood analysis:** if a CAMB/Cobaya-level analysis with the complete Planck likelihood (replacing the compressed priors) erases the Δχ² preference, the result reported here is void. **Status (2026-07-08): executed — did not fire.** The preference held and sharpened to ≈3.4σ; see Addendum II.
3. **Sub-percent w(z) reconstruction:** the model's w(z) has specific curvature beyond CPL; data resolving w(z) at the ~0.01 level can distinguish them.
4. **Reversion of the anomaly:** if the DESI evolving-DE preference dissolves with more data, the model becomes unnecessary (Occam-retired, τ → ∞ limit), though not logically falsified.
5. **CCBH-conditional (see Addendum):** if the kernel is interpreted as cosmologically coupled black holes, k = 3 is already excluded by this analysis, and any viable sourcing requires a black-hole mass-growth history with late-time decline intermediate between star formation (too shallow) and the luminous quasar luminosity density (too steep) — a factor of roughly 8–16 from z = 1 to 0. Quantitatively (see Addendum): the coupled Soltan integral with the measured coupling k = 2.19–2.40 requires a local SMBH mass density of (4.2–5.2)×10⁶ M⊙ Mpc⁻³ at fiducial radiative efficiency η = 0.1 (range ≈(1.9–9.6)×10⁶ across η = 0.057–0.2) — a factor of 4–5 above the standard bulge-relation census (≈1.0×10⁶) and 60–70% of the GWB-motivated estimate (≈7.4×10⁶). Confirmation of the standard census excludes the CCBH identification except at maximal radiative efficiency (η ≈ 0.3); a census near (4–7)×10⁶ supports it. The phenomenological kernel itself survives either outcome, with mechanism unknown.

## 8. Limitations

The compressed CMB prior captures most but not all of the full Planck likelihood; published w₀wₐCDM significances are higher with the full likelihood, and absolute significances here run correspondingly low for all models — **relative** model comparisons are the robust content. Massless neutrinos are assumed; sound horizons use fitting-formula epochs with a documented single-point calibration. Dark energy perturbations, growth observables, and ISW contributions are not modeled. The Madau–Dickinson source has its own uncertainties, and a black-hole-accretion-history source variant remains untested with the CMB anchor. A shared systematic across probes that no ablation can detect remains possible. The mechanism — why collapsed-structure formation would source vacuum energy with a ~2 e-fold delay — is entirely open; absent a derivation of τ and of the coupling, this is phenomenology.

## 9. Reproducibility

All numbers in this note are generated by the scripts accompanying it (Python 3.12; numpy, scipy, pandas). Data are fetched at run time from the official public repositories (CobayaSampler/bao_data; PantheonPlusSH0ES/DataRelease); no data are redistributed. Total runtime: minutes on a single CPU.

## Addendum (same day): mechanism identification and its first confrontation

After the analysis above was frozen, the kernel was identified term-by-term with the population dynamics of cosmologically coupled black holes (CCBH; Croker & Weiner 2019; Farrah et al. 2023): a population of objects formed at a rate S per unit time, whose individual masses grow with the scale factor as a^k, has physical energy density obeying dρ_DE/dN = S/H − (3−k)·ρ_DE — exactly the leaky-integrator equation of Section 2, with the sourcing convention fixed to per-unit-time and τ = 1/(3−k). Under this identification the exponential kernel is derived (number dilution versus mass growth) rather than assumed, and the memory timescale measures the coupling, k = 3 − 1/τ. The identity was verified numerically to 9×10⁻⁴ (grid discretization). Confronting the identified model with the same joint dataset (methods as in Section 4):

| source (per-time) | decline z=1→0 | Δχ² vs ΛCDM | best-fit k |
|---|---|---|---|
| star formation (MD14) | ×4.4 | −3.11 | 1.91 |
| steepened representative shapes | ×11 / ×16 | −5.31 / −6.38 | 2.41 / 2.57 |
| Shen et al. (2020) QLF, global fit B | ×24 | +0.93 | 2.38 |
| Shen et al. (2020) QLF, global fit A | ×24 | +0.54 | 2.39 |
| X-ray-census (MH08-anchored), ×8 / ×12 | ×8 / ×12 | −4.62 / −5.58 | 2.19 / 2.40 |
| *(phenomenological per-e-fold model, Section 5)* | — | *−7.61* | — |

Findings. (i) The pure-vacuum-interior case k = 3 (zero new parameters) is excluded for every source tested (Δχ² = +34 to +59 for the measured sources). (ii) A directional prediction registered before the final test — that steeper late-time source decline improves the fit — held within the representative bracket but was falsified by the real quasar luminosity density, whose decline overshoots the optimum. (iii) The literal CCBH model sourced by either the star-formation history or the luminous quasar accretion history therefore does not reproduce the phenomenological preference of Section 5. The effective source required by the data has a late-time decline intermediate between the two (roughly a factor 8–16 from z = 1 to 0). A final, pre-registered sourcing test was then performed: the total X-ray-census accretion history (Merloni & Heinz 2008 class, which retains the obscured and radiatively inefficient growth the luminous QLF omits) was selected in advance on physical grounds, with the falsifier stated before implementation — viable only if its published late-time decline lies in the 8–16 window (it does: the X-ray emissivity evolution gives ×8–12), with an expected Δχ² of −5 to −7.5. Implemented as an anchored reconstruction (source peak fixed at z = 2 and declines fixed at the published ×8 and ×12, since MH08 publish no closed form), the result is Δχ² = −4.6 to −5.6 with k = 2.19–2.40 and ρ_DE peaking at z ≈ 0.42–0.45 — recovering 60–73% of the phenomenological preference, at the lower edge of the pre-registered band, with k = 3 again excluded (+25 to +38). Sourcing attempts stop here by design. Finally, the coupled Soltan integral (Lacy et al. 2024, their eq. 9) was evaluated with the Shen et al. (2020) fit-B luminosity density in absolute units. The pipeline reproduces the classical uncoupled result (5.3×10⁵ M⊙ Mpc⁻³ at η = 0.1, vs. 4.6×10⁵ in Marconi et al. 2004) and the published census-to-coupling mapping; the measured coupling k = 2.19–2.40 then requires a local SMBH mass density of (4.2–5.2)×10⁶ M⊙ Mpc⁻³ at η = 0.1 — four to five times the standard bulge-relation census and 60–70% of the GWB-motivated estimate. This is the model's cross-domain falsifier (kill condition 5). A growth-of-structure consistency check was also performed against seven independent RSD fσ₈ measurements (6dFGS, MGS, and BOSS/eBOSS consensus values — surveys disjoint from every dataset in the joint fit): with free amplitude, the shape χ² is 5.7 (ECF-MD14), 5.9 (CPL), 6.1 (ΛCDM) — all consistent, with no discrimination at current precision, so the model passes the fourth probe at zero parameter cost. At fixed early-time amplitude the model predicts σ₈ today 1.5% higher than ΛCDM (≈1.0% from its higher best-fit Ω_m, ≈0.5% from the dark-energy history itself, since a density peaked at z ≈ 0.5 and normalized today implies less dark energy in the deep past): this direction does not alleviate, and mildly deepens, the S₈ tension. A pre-registered expectation of growth suppression was incorrect (a sign error in qualitative reasoning) and is recorded here; the pre-registered pass condition — fitting the growth data at least as well as ΛCDM — was met. The residual gap (Δχ² ≈ 2–3) is attributable to reconstruction imprecision (the exact MH08 curve via the full Silverman-XLF chain is the named refinement), to the phenomenological model's extra freedom, or to missing physics; the present data do not distinguish these. Status: the CCBH identification supplies a derivation of the kernel form and one firm exclusion (k = 3), but no demonstrated mechanism for the fitted model. The theoretical viability of cosmological coupling itself remains contested (Mistele 2023; Wang & Wang 2023; Avelino 2023).

## Addendum II (July 8, 2026): full-likelihood test — kill condition 2 executed

Kill condition 2 was executed the day after v1.0, replacing the compressed CMB prior with the Planck 2018 high-ℓ plik-lite TTTEEE likelihood (clik-free native implementation) plus a Gaussian optical-depth prior τ = 0.0544 ± 0.0073 in place of low-ℓ EE, combined with the same DESI DR2 BAO and Pantheon+ likelihoods (Σmν = 0.06 eV, one massive neutrino). Gates passed before any chain ran: the CAMB implementation reproduces the reference expansion history to <0.3% at τ_ecf = 1.5/2.1/3.0, and the ΛCDM sanity chain recovers Ωm = 0.302 ± 0.004, H₀ = 68.34 ± 0.30, Ω_b h² = 0.02252 ± 0.00013, consistent with published Planck+DESI+SN values.

**Verdict: kill condition 2 does not fire. The preference held and sharpened — ≈2.8σ (compressed prior) → 3.4σ (full likelihood) — inside the pre-registered 3–4σ band.**

| model | χ²_tot | CMB | BAO | SN | Δχ² vs ΛCDM | extra params | significance (Wilks) |
|---|---|---|---|---|---|---|---|
| ΛCDM | 2005.53 | 587.42 | 12.45 | 1405.66 | — | — | — |
| CPL (w₀,wₐ) | 1996.69 | 583.39 | 10.26 | 1403.04 | −8.85 | 2 | 2.5σ (p = 0.012) |
| **ECF-MD14 (τ)** | **1993.89** | **581.96** | **9.38** | **1402.55** | **−11.64** | **1** | **3.4σ (p = 6.5×10⁻⁴)** |

ECF-MD14 improves every data block individually (CMB, BAO, SN) and out-fits the two-parameter CPL form with one fewer parameter. CPL's own fit (best-fit w₀ = −0.848, wₐ = −0.578; marginalized wₐ = −0.626 [−0.854, −0.400], nonzero at ~2.7σ) independently reproduces the published DESI evolving-DE signature, further validating the likelihood stack. The certified marginalized constraint, from a 6-chain MPI run (cross-chain R−1 = 0.0190 < 0.02; independent GetDist worst-eigenvalue check 0.0187; 88,094 weighted samples): **τ_ecf = 2.41 (+0.87/−0.51) at 68%** (mean 2.58 ± 0.77; 95% CI [1.58, 4.60]) — a clean unimodal peak bounded well away from both prior edges, i.e. a constraint, not a prior return. Best-fit τ_ecf = 2.194; H₀(ECF) = 67.98. Information criteria, adopting N = 2,217 data points (613 plik-lite bandpowers + 13 BAO + 1,590 SNe + 1 prior; ln N = 7.70): ΔAIC = −9.6 (ECF) vs −4.8 (CPL); **ΔBIC = −3.9 — ECF is now favored over ΛCDM by BIC** — vs +6.6 for CPL (disfavored); ΔBIC(ECF) remains negative (−4.2 to −2.4) for any N between 1,700 and 10,000. Residual caveats: plik-lite plus a τ prior approximates but does not equal the full clik low-ℓ + lensing likelihood, and 3.4σ remains strong evidence, not a detection. Complete tables, convergence proofs, environment details, and the three execution fixes (all environment-level; physics unchanged and re-validated against the reference) are recorded in RESULTS_FULLPLANCK.md in this repository.

## Acknowledgments

Analysis, numerical implementation, and drafting were performed with the assistance of Claude (Anthropic), including the adversarial testing that eliminated the failed variants in §6.4. Any errors are the author's own. This note is dedicated to Kathy, and to Leah,Mason,Linden and Brennan.
