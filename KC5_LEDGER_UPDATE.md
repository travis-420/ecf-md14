# Kill condition 5 — ledger update against Liepold & Ma (2024)

**Date:** July 10, 2026
**Status:** Ledger update only. No model quantity is refit; no data enter any
likelihood. This entry formally locates the current best dynamical census of
local supermassive-black-hole mass density against the pre-registered
coupled-Soltan requirement (kill condition 5). Companion script:
`16_kc5_ledger_update.py`.

## The frozen requirement (recap, unchanged)

The CCBH identification (k = 2.19–2.40) requires, via coupled-Soltan closure,
a local SMBH mass density

    rho_req(eta = 0.1) = (4.2 – 5.2) x 10^6 Msun/Mpc^3,

with radiative efficiency pre-registered over eta in [0.057, 0.2]. Because
the (1 − eta)/eta prefactor is common to every accretion epoch, it factors
out of the coupled integral exactly, so the window rescales as
rho_req(eta) = rho_req(0.1) x [(1 − eta)/eta] / 9:

| eta | required window (10^6 Msun/Mpc^3) |
|---|---|
| 0.057 | 7.7 – 9.6 |
| 0.10 (fiducial) | 4.2 – 5.2 |
| 0.167 | 2.3 – 2.9 |
| 0.20 (pre-registered ceiling) | 1.9 – 2.3 |

## The new external measurement

Liepold & Ma 2024 (ApJL 971, L29), volume-limited dynamical census (MASSIVE
survey): rho_bh = 1.8 (+0.8 / −0.5) x 10^6 Msun/Mpc^3 — itself a factor ~1.8
above older bulge-relation censuses (~1.0 x 10^6). The census literature is
moving upward, toward the window.

## Location (computed, not eyeballed)

- **At fiducial eta = 0.1:** L&M falls short of the window's lower edge by
  ~3.0 sigma (3.6 sigma from window center), using the measurement's upper
  error. Quantified tension.
- **At the pre-registered ceiling eta = 0.2:** the window is (1.87–2.31) x
  10^6 and the L&M central value sits +0.08 sigma from its lower edge —
  essentially exact overlap.
- **Mapping the L&M 68% band onto eta:** consistency with the window center
  requires eta in [0.167, 0.287]; with the window's lower edge, eta in
  [0.152, 0.264]. The pre-registered range [0.057, 0.2] intersects this only
  in its top sliver, eta ≈ 0.15–0.20.

## Verdict (frozen wording)

**KC5 does NOT fire, in either direction.** But the honest summary is
sharper than "consistent": survival currently depends on the top sliver of
the pre-registered efficiency range. If the true rho_bh is the L&M central
value, the CCBH mechanism requires a rapidly-spinning SMBH population with
mean radiative efficiency eta ≈ 0.15–0.22 — at and slightly beyond the
pre-registered ceiling. Independent (hedged) support exists: X-ray
reflection spin measurements find many near-extremal AGN spins, for which
thin-disk eta approaches 0.2–0.3; but that subsample is selection-biased
toward bright accretors and does not measure the population mean.

## No-goalpost clause

The eta range [0.057, 0.2] was pre-registered and is NOT extended by this
entry. If future census convergence forces eta > 0.2, that is to be recorded
as KC5 tension/failure unless an independent, census-external measurement of
the population-mean efficiency justifies a revision — proposed BEFORE the
census result that would require it, not after.

## Firing thresholds (restated against the new landscape)

- **Fires (low side):** a census converging robustly (>3 sigma) below
  ~1.9 x 10^6 — below the window across the ENTIRE pre-registered eta range.
  L&M's central value is at this boundary; its error bar is not yet close to
  deciding it.
- **Fires (high side):** convergence above ~9.6 x 10^6 (the eta = 0.057
  ceiling), which would overshoot the mechanism's budget.
- Current three-way landscape for context: dynamical census 1.8 x 10^6 <
  ECF fiducial window 4.2–5.2 x 10^6 < GWB-implied ~7.4 x 10^6. The
  census-vs-PTA discrepancy is a live problem in the field independent of
  ECF (flagged by Liepold & Ma themselves and sharpened by the 2026
  energetic-ceiling analyses); its resolution moves this ledger whichever
  way it goes.

## Watch list

- Mingarelli et al. 2026, GWB energetic ceilings (arXiv:2601.18859) — uses
  the L&M mass function; sharpens the census-vs-PTA tension.
- The Sato-Polito et al. line ("where are the PTA black holes?").
- Next-generation volume-limited dynamical censuses (MASSIVE extensions).
- IPTA DR3 amplitude (also the KC6-candidate referee).

## Ledger

- 2026-07-08 (NOTE, Addendum): KC5 stated; standard census ~1.0 x 10^6 noted
  as 4–5x below fiducial window.
- 2026-07-10 (this entry): L&M 2024 located; NOT FIRED; 3-sigma tension at
  fiducial eta = 0.1; overlap confined to eta ≈ 0.15–0.20; no-goalpost
  clause frozen.
