# Independent Blind Replication Record — ECF-MD14 Analysis

**Date:** 2026-07-07 (execution date: Tue Jul 7, 2026, UTC)

> This document records an independent re-execution of the analysis
> scripts against freshly fetched public data. The replicating session
> was provided the code but not the original results, and was
> instructed to ignore two numeric annotations present in script
> print-strings. This record verifies computational reproducibility
> only. It does not constitute endorsement of the model, the
> methodology, or any scientific interpretation.

---

## 2. Environment

Computed live in the replication session:

- Python 3.12.3
- numpy 2.4.4
- scipy 1.17.1
- pandas 3.0.2
- Execution date: Tue Jul 7 20:37–20:47 UTC 2026 (Ubuntu 24, Linux container)

## 3. Data provenance

Four files fetched via `curl -sL` from:

1. `https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt` → `desi_dr2_mean.txt`
2. `https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt` → `desi_dr2_cov.txt`
3. `https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES.dat` → `pp.dat`
4. `https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES_STAT%2BSYS.cov` → `pp.cov`

Fetch checkpoint (reported from disk via `wc -c`, `wc -l`, `grep | head`, verified again at record-writing time):

| File | Bytes |
|---|---|
| desi_dr2_mean.txt | 472 |
| desi_dr2_cov.txt | 2,547 |
| pp.dat | 579,283 |
| pp.cov | 33,284,960 |

- `pp.dat` line count: 1,702 (1 header + 1,701 data rows)
- First data line of `desi_dr2_mean.txt` after header: `0.29500000 7.94167639 DV_over_rs`

## 4. Verbatim stdout of all four scripts

### 4.1 likelihood.py (Gate B: DESI DR2 BAO + Pantheon+ SN)

```
SN after z>0.01 cut: 1590   BAO points: 13

SANITY  LCDM: chi2=1416.81  Om=0.3037  beta=29.672
        chi2/dof = 0.886   (published Pantheon+ LCDM Om ~ 0.32-0.35 SN-only; BAO pulls ~0.30)

==============================================================================
GATE B: joint fit to DESI DR2 BAO (13 pts) + Pantheon+ SN (1590 pts)
==============================================================================
model         k      chi2   dchi2       AIC    dAIC       BIC    dBIC   best-fit
LCDM          3   1416.81    0.00   1422.81    0.00   1438.95    0.00   Om=0.304
ECF-MD14      4   1411.66   -5.16   1419.66   -3.16   1441.17    2.22   Om=0.316 tau=2.47
ECF-MD14/H    4   1412.36   -4.45   1420.36   -2.45   1441.88    2.93   Om=0.324 tau=1.17
CPL           5   1412.22   -4.60   1422.22   -0.60   1449.11   10.16   Om=0.304 w0=-0.896 wa=-0.184

(dAIC/dBIC negative = better than LCDM; ~2 'positive evidence', ~6 'strong')
```

### 4.2 gateb2.py (Gate B.2: DESI DR2 BAO + Pantheon+ SN + Planck compressed CMB)

```
calibration factors  r*: 1.00579   rd: 0.98014  (pipeline vs CAMB at Planck point)

SANITY LCDM+CMB: chi2=1420.11  Om=0.3022 H0=68.46 wb=0.02254
   implied rd = 147.36 Mpc  (Planck ~147)

================================================================================
GATE B.2: DESI DR2 BAO + Pantheon+ SN + Planck compressed CMB   (N=1606)
================================================================================
model       k      chi2   dchi2    dAIC    dBIC   best fit
LCDM        4   1420.11    0.00    0.00    0.00   Om=0.302 H0=68.46
ECF-MD14    5   1412.50   -7.61   -5.61   -0.23   Om=0.312 H0=67.79 tau=2.10
CPL         6   1413.72   -6.39   -2.39    8.38   Om=0.311 H0=67.70 w0=-0.863 wa=-0.477
```

### 4.3 prof2.py (tau profile)

```
calibration factors  r*: 1.00579   rd: 0.98014  (pipeline vs CAMB at Planck point)
tau profile under full anchored fit (min over Om,H0,wb at each tau):
  tau= 1.0  chi2= 1434.73  dchi2 vs LCDM= +14.62
  tau= 1.4  chi2= 1419.05  dchi2 vs LCDM=  -1.06
  tau= 1.8  chi2= 1413.06  dchi2 vs LCDM=  -7.05
  tau= 2.1  chi2= 1412.50  dchi2 vs LCDM=  -7.61
  tau= 2.5  chi2= 1413.03  dchi2 vs LCDM=  -7.08
  tau= 3.0  chi2= 1414.37  dchi2 vs LCDM=  -5.74
  tau= 3.8  chi2= 1416.69  dchi2 vs LCDM=  -3.42
  tau= 5.0  chi2= 1426.73  dchi2 vs LCDM=  +6.62
```

### 4.4 diag.py (diagnostics)

```
calibration factors  r*: 1.00579   rd: 0.98014  (pipeline vs CAMB at Planck point)
PART 1: where the -7.6 lives (chi2 by dataset at each best fit)
                  SN       BAO       CMB     total
LCDM         1406.24     11.59      2.28   1420.11
ECF          1403.60      8.89      0.01   1412.50
delta          -2.65     -2.69     -2.27     -7.61

PART 2: BAO point-by-point pulls (data-model)/sigma
     z         type  LCDM pull   ECF pull
 0.295   DV_over_rs      -0.02      +0.26
 0.510   DM_over_rs      +1.59      +1.87
 0.510   DH_over_rs      -1.57      -1.07
 0.706   DM_over_rs      -0.77      -0.31
 0.706   DH_over_rs      -1.76      -1.35
 0.934   DM_over_rs      -1.14      -0.52
 0.934   DH_over_rs      +0.72      +0.86
 1.321   DM_over_rs      -0.71      -0.44
 1.321   DH_over_rs      +0.59      +0.19
 1.484   DM_over_rs      +0.64      +0.73
 1.484   DH_over_rs      -0.10      -0.32
 2.330   DH_over_rs      +0.04      -0.95
 2.330   DM_over_rs      +0.11      +0.05

PART 3: leave-one-tracer-out  (dchi2 = ECF - LCDM, both refit)
  drop BGS        dchi2 =   -7.69   (full: -7.61)
  drop LRG1       dchi2 =   -7.99   (full: -7.61)
  drop LRG2       dchi2 =   -4.29   (full: -7.61)
  drop LRG3+ELG1  dchi2 =   -6.87   (full: -7.61)
  drop ELG2       dchi2 =   -7.18   (full: -7.61)
  drop QSO        dchi2 =   -7.68   (full: -7.61)
  drop Lya        dchi2 =   -8.66   (full: -7.61)

PART 4: dataset ablations
  BAO+CMB only (no SN):   dchi2 =   -5.45
  BAO+SN only  (no CMB):  dchi2 =   -5.16  (Gate B result)

PART 5: SN robustness -- drop all z<0.1 (calibration-sensitive rung)
  N_SN: 960 (was 1590);  dchi2 =   -6.62

PART 6: SN residuals vs LCDM, binned (diag errors, diagnostic only)
       z bin     N  data resid (mmag)  ECF-LCDM pred
 0.01-0.03    357      +10.2 +/- 12.4         +14.7
 0.03-0.10    273      +18.3 +/- 11.4         +11.7
 0.10-0.25    346       -4.5 +/- 9.8           -0.9
 0.25-0.50    404       -1.4 +/- 9.6          -10.5
 0.50-0.80    180      -47.0 +/- 17.4         -17.7
 0.80-1.30     14      +78.5 +/- 75.2         -17.8
 1.30-2.30     16      -17.2 +/- 77.7         -13.1
```

Note: several print-strings in the scripts contain fixed numeric annotations authored into the code (e.g., "(full: -7.61)", "dchi2 =   -5.16  (Gate B result)", and parenthetical reference values). These are part of the scripts' hard-coded output text, not values computed in this session, except where the live-computed numbers happen to coincide with them.

## 5. Summary table

All χ² values as computed live in this session, two decimals.

| Stage | Model | k | χ² | Δχ² vs ΛCDM | Best-fit parameters |
|---|---|---|---|---|---|
| Gate B (BAO+SN) | ΛCDM | 3 | 1416.81 | 0.00 | Ωm=0.304, β=29.672 |
| Gate B (BAO+SN) | ECF-MD14 | 4 | 1411.66 | −5.16 | Ωm=0.316, τ=2.47 |
| Gate B (BAO+SN) | ECF-MD14/H | 4 | 1412.36 | −4.45 | Ωm=0.324, τ=1.17 |
| Gate B (BAO+SN) | CPL | 5 | 1412.22 | −4.60 | Ωm=0.304, w0=−0.896, wa=−0.184 |
| Gate B.2 (BAO+SN+CMB) | ΛCDM | 4 | 1420.11 | 0.00 | Ωm=0.302, H0=68.46, ωb=0.02254 |
| Gate B.2 (BAO+SN+CMB) | ECF-MD14 | 5 | 1412.50 | −7.61 | Ωm=0.312, H0=67.79, τ=2.10 |
| Gate B.2 (BAO+SN+CMB) | CPL | 6 | 1413.72 | −6.39 | Ωm=0.311, H0=67.70, w0=−0.863, wa=−0.477 |

τ-profile (ECF, anchored fit; χ² at fixed τ, minimized over Ωm, H0, ωb):

| τ | χ² | Δχ² vs ΛCDM |
|---|---|---|
| 1.0 | 1434.73 | +14.62 |
| 1.4 | 1419.05 | −1.06 |
| 1.8 | 1413.06 | −7.05 |
| 2.1 | 1412.50 | −7.61 |
| 2.5 | 1413.03 | −7.08 |
| 3.0 | 1414.37 | −5.74 |
| 3.8 | 1416.69 | −3.42 |
| 5.0 | 1426.73 | +6.62 |

Per-dataset χ² at the Gate B.2 best fits — ΛCDM: SN 1406.24, BAO 11.59, CMB 2.28 (total 1420.11); ECF: SN 1403.60, BAO 8.89, CMB 0.01 (total 1412.50).

## 6. What the replicating session did NOT have access to

- The original run's results or output files.
- The research note or any accompanying write-up.
- Any target values, expected numbers, or prior outputs — with the sole exception of numeric annotations hard-coded into the scripts' print-strings (including but not limited to "(full: -7.61)" and "-5.16 (Gate B result)"), which the session was instructed to ignore and did not use as inputs to any computation.
- No web searches for expected or published results were performed.

All numbers in sections 4 and 5 were produced by executing the four scripts in this session against the freshly fetched data files listed in section 3.
