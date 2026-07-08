import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.signal import lfilter

# ---- RSD compilation (independent surveys; none used in our joint fit) ----
# 6dFGS + MGS confirmed from source papers; BOSS/eBOSS consensus values as
# commonly tabulated (re-verify vs Alam et al. 2021 Table 3 before publication)
z_d = np.array([0.067, 0.15, 0.38, 0.51, 0.70, 0.85, 1.48])
f8  = np.array([0.423, 0.49, 0.500, 0.455, 0.448, 0.315, 0.462])
e8  = np.array([0.055, 0.145, 0.047, 0.039, 0.043, 0.095, 0.045])

Orad=9.24e-5
Nl=2500; lna=np.linspace(np.log(1/31),0,Nl); ag=np.exp(lna); dxl=lna[1]-lna[0]; zg=1/ag-1
psi=0.015*(1+zg)**2.7/(1+((1+zg)/2.9)**5.6)
S=psi/np.trapezoid(psi,lna)

def fDE_ecf(tau):
    r=lfilter([0.0,dxl],[1.0,-(1.0-dxl/tau)],S); return r/max(r[-1],1e-30)

models={
 'LCDM     ':(0.3022, np.ones(Nl)),
 'ECF-MD14 ':(0.312,  fDE_ecf(2.10)),
 'CPL      ':(0.311,  ag**(-3*(1-0.863-0.477))*np.exp(-3*(-0.477)*(1-ag))),
}

def growth(Om,fDE):
    E2=Om*ag**-3+Orad*ag**-4+(1-Om-Orad)*fDE
    dlnH=0.5*np.gradient(np.log(E2),lna)
    E2i=interp1d(lna,E2,kind='cubic'); dHi=interp1d(lna,dlnH,kind='cubic')
    x0=lna[0]
    def rhs(x,y):
        D,Dp=y; Omv=Om*np.exp(-3*x)/E2i(x)
        return [Dp,-(2+dHi(x))*Dp+1.5*Omv*D]
    sol=solve_ivp(rhs,[x0,0],[ag[0],ag[0]],t_eval=lna[lna>=x0],rtol=1e-8,atol=1e-12)
    zz=1/np.exp(sol.t)-1
    return zz[::-1], (sol.y[1]/sol.y[0])[::-1], (sol.y[0])[::-1], sol.y[0][-1]  # z asc, f, D, D(today)

print(f"{'model':<10} {'chi2 (7 pts)':>12} {'fit amp sig8':>13} {'sig8(today) vs LCDM':>20}")
res={}
D0_ref=None
for nm,(Om,fDE) in models.items():
    zz,f,D,D0=growth(Om,fDE)
    Dn=D/D[0]*1  # normalize at earliest point common (same IC -> D itself comparable)
    g=np.interp(z_d,zz,f*D/D0)         # shape f*D/D(0)
    A=np.sum(f8*g/e8**2)/np.sum(g*g/e8**2)
    chi2=np.sum(((f8-A*g)/e8)**2)
    if D0_ref is None: D0_ref=D0
    supp=100*(D0/D0_ref-1)
    res[nm]=(chi2,A,g)
    print(f"{nm:<10} {chi2:>12.2f} {A:>13.3f} {supp:>+19.2f}%")

print(f"\n(sig8(today) column: growth since a=1e-3 at FIXED early amplitude, relative to LCDM)")
print(f"(S8 tension context: weak lensing prefers amplitude ~6-9% below Planck-LCDM)")
print(f"\nper-point (data vs amplitude-fitted model predictions):")
print(f"{'z':>6} {'data':>7} {'err':>6} | {'LCDM':>6} {'ECF':>6} {'CPL':>6}")
for i,z in enumerate(z_d):
    row=[res[k][1]*res[k][2][i] for k in models]
    print(f"{z:>6.3f} {f8[i]:>7.3f} {e8[i]:>6.3f} | {row[0]:>6.3f} {row[1]:>6.3f} {row[2]:>6.3f}")
