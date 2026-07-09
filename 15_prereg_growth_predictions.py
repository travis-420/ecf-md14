# 15_prereg_growth_predictions.py
# Generates the pre-registered growth predictions in PREREGISTRATION_GROWTH.md.
# Machinery adapted from 14_growth_fsigma8_check.py (same kernel, same growth ODE).
# Standalone: no data files required.
#
# Conventions:
#   - per-e-fold leaky integrator, MD14 source (identical to published model)
#   - smooth dark energy (no DE perturbations) -- the declared approximation
#   - "fixed early amplitude": common growth IC at a = 1/31; sigma8(z) ratios
#     are D(z) ratios at matched primordial amplitude
#   - Om conventions: ECF at Gate B.2 best fit Om = 0.312; LCDM at 0.3022
#   - tau values: certified full-Planck posterior median 2.405, 68% edges
#     1.894 / 3.277, and full-likelihood best fit 2.194

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.signal import lfilter

Orad = 9.24e-5
Nl = 2500
lna = np.linspace(np.log(1/31), 0, Nl)
ag = np.exp(lna); dxl = lna[1] - lna[0]; zg = 1/ag - 1
psi = 0.015*(1+zg)**2.7/(1+((1+zg)/2.9)**5.6)
S = psi/np.trapezoid(psi, lna)

def fDE_ecf(tau):
    r = lfilter([0.0, dxl], [1.0, -(1.0 - dxl/tau)], S)
    return r/max(r[-1], 1e-30)

def growth(Om, fDE):
    E2 = Om*ag**-3 + Orad*ag**-4 + (1 - Om - Orad)*fDE
    dlnH = 0.5*np.gradient(np.log(E2), lna)
    E2i = interp1d(lna, E2, kind='cubic'); dHi = interp1d(lna, dlnH, kind='cubic')
    x0 = lna[0]
    def rhs(x, y):
        D, Dp = y; Omv = Om*np.exp(-3*x)/E2i(x)
        return [Dp, -(2 + dHi(x))*Dp + 1.5*Omv*D]
    sol = solve_ivp(rhs, [x0, 0], [ag[0], ag[0]], t_eval=lna[lna >= x0],
                    rtol=1e-8, atol=1e-12)
    zz = 1/np.exp(sol.t) - 1
    return zz[::-1], (sol.y[1]/sol.y[0])[::-1], (sol.y[0])[::-1], sol.y[0][-1]

# DESI DR2 tracer effective redshifts (BGS, LRG1, LRG2, LRG3, ELG2, QSO)
z_desi = np.array([0.295, 0.510, 0.706, 0.920, 1.317, 1.491])

Om_L, Om_E = 0.3022, 0.312
TAUS = [1.894, 2.194, 2.405, 3.277]

zzL, fL, DL, D0L = growth(Om_L, np.ones(Nl))
rL = np.interp(z_desi, zzL, fL*DL)

print("PRE-REGISTERED PREDICTION 1:")
print("fsigma8(z)_ECF / fsigma8(z)_LCDM at fixed early amplitude")
print(f"{'z_eff':>6}", *(f"tau={t:<6}" for t in TAUS))
ratios = {}
for tau in TAUS:
    zz, f, D, D0 = growth(Om_E, fDE_ecf(tau))
    ratios[tau] = np.interp(z_desi, zz, f*D)/rL
for i, z in enumerate(z_desi):
    print(f"{z:>6.3f}", *(f"{ratios[t][i]:>10.4f}" for t in TAUS))

print("\nPRE-REGISTERED PREDICTION 2:")
print("sigma8(today)_ECF / sigma8(today)_LCDM - 1, fixed early amplitude")
for tau in TAUS:
    _, _, _, D0 = growth(Om_E, fDE_ecf(tau))
    _, _, _, D0m = growth(Om_L, fDE_ecf(tau))
    print(f"tau={tau}:  full (Om=0.312): {100*(D0/D0L-1):+.2f}%"
          f"   DE-history only (Om=0.3022): {100*(D0m/D0L-1):+.2f}%")

# Consistency anchor vs the published note (tau = 2.10 gave "+1.5%"):
_, _, _, D0 = growth(Om_E, fDE_ecf(2.10))
print(f"\nAnchor check, tau=2.10 full: {100*(D0/D0L-1):+.2f}%  (note says +1.5%)")
