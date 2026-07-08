import numpy as np
from scipy.integrate import solve_ivp, cumulative_trapezoid
from scipy.optimize import curve_fit

Om0, Orad0, H0 = 0.315, 9.24e-5, 67.4
c_km=299792.458; OmDE=1-Om0-Orad0
N=4000; lna=np.linspace(np.log(1e-6),0.0,N); a=np.exp(lna); dx=lna[1]-lna[0]
z=1/a-1
E2L = Om0*a**-3 + Orad0*a**-4 + OmDE

# Madau-Dickinson 2014 cosmic star-formation rate density (fixed, measured -- NO free shape)
psi = 0.015*(1+z)**2.7/(1+((1+z)/2.9)**5.6)

S_A = psi/np.trapezoid(psi,lna)                       # sourcing per e-fold
S_B = (psi/np.sqrt(E2L)); S_B/=np.trapezoid(S_B,lna)  # sourcing per unit time (dt = dlna/H)

def rho_of(S,tau):
    r=np.zeros(N)
    for i in range(1,N): r[i]=r[i-1]+dx*(S[i-1]-r[i-1]/tau)
    return r/max(r[-1],1e-30)
def w_of(r): return -1-np.gradient(np.log(np.maximum(r,1e-300)),lna)/3
def mu_of(r):
    E=np.sqrt(Om0*a**-3+Orad0*a**-4+OmDE*r)
    o=np.argsort(z); zs=z[o]
    Dc=cumulative_trapezoid(c_km/(H0*E[o]),zs,initial=0)
    return zs,5*np.log10(np.maximum((1+zs)*Dc,1e-10))+25
def shape_CPL(w0,wa): return a**(-3*(1+w0+wa))*np.exp(-3*wa*(1-a))
def fit_cpl(r):
    zt,mt=mu_of(r); sel=(zt>=0.01)&(zt<=2.3)
    def mod(zq,w0,wa):
        zz,mm=mu_of(shape_CPL(w0,wa)); return np.interp(zq,zz,mm)
    p,_=curve_fit(mod,zt[sel],mt[sel],p0=[-0.8,-0.5],maxfev=3000)
    return p
def zpeak(r):
    late=a>1/11; i=np.argmax(r[late]); idx=np.where(late)[0][i]
    return 0.0 if idx>=N-2 else 1/a[idx]-1

# DESI DR2+CMB+Pantheon+ central values and ~1-sigma
W0c,W0s=-0.838,0.055; WAc,WAs=-0.62,0.205

for name,S in [("MD14 source, per e-fold",S_A),("MD14 source, per unit time",S_B)]:
    best=None; rows=[]
    for tau in np.arange(0.20,3.001,0.05):
        r=rho_of(S,tau); p=fit_cpl(r)
        d=np.hypot((p[0]-W0c)/W0s,(p[1]-WAc)/WAs)
        rows.append((tau,p[0],p[1],zpeak(r),d))
        if best is None or d<best[4]: best=(tau,p[0],p[1],zpeak(r),d)
    tau,w0,wa,zp,d = best
    inbox = (abs(w0-W0c)<=W0s) and (abs(wa-WAc)<=WAs)
    print(f"{name}")
    print(f"  best tau = {tau:.2f}")
    print(f"  w0 = {w0:+.3f}   (DESI: -0.838 +/- 0.055)")
    print(f"  wa = {wa:+.3f}   (DESI: -0.620 +/- 0.205)")
    print(f"  rho_DE peak at z = {zp:.2f}   (DESI-preferred: ~0.5)")
    print(f"  distance from DESI central = {d:.2f} sigma   |  inside 1-sigma box: {'YES' if inbox else 'no'}")
    # show neighborhood
    print(f"  neighborhood:")
    for row in rows:
        if abs(row[0]-tau)<=0.16:
            print(f"    tau={row[0]:.2f}: w0={row[1]:+.3f} wa={row[2]:+.3f} zpk={row[3]:.2f} d={row[4]:.2f}s")
    print()
