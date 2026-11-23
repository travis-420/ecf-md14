"""ECF-MD14 physics: tau -> w(a) table. EXACT mirror of the validated pipeline
(leaky integrator of the Madau-Dickinson 2014 SFR, per-e-fold sourcing).
This file is the ground truth. Do not modify the numerics."""
import numpy as np
from scipy.signal import lfilter

_N = 2500
_lna = np.linspace(np.log(1/31.0), 0.0, _N)
_a = np.exp(_lna); _dx = _lna[1]-_lna[0]; _z = 1/_a - 1
_psi = 0.015*(1+_z)**2.7/(1+((1+_z)/2.9)**5.6)
_S = _psi/np.trapezoid(_psi, _lna)

def rho_de(tau):
    """rho_DE(a)/rho_DE(a=1) on the internal a-grid."""
    r = lfilter([0.0,_dx],[1.0,-(1.0-_dx/tau)],_S)
    return _a.copy(), r/max(r[-1],1e-30)

def w_of_a_table(tau, w_clip=(-3.0, 0.5)):
    """(a, w) table for CAMB DarkEnergyPPF.set_w_a_table. Ascending a.
    w is clipped only where Omega_DE is negligible (a<~0.05)."""
    a, r = rho_de(tau)
    w = -1.0 - np.gradient(np.log(np.maximum(r,1e-300)), _lna)/3.0
    return a, np.clip(w, *w_clip)
