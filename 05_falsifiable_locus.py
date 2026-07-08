import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import curve_fit
Om0, Orad0, H0 = 0.315, 9.24e-5, 67.4
c_km=299792.458
a=np.logspace(-6,0,4000); lna=np.log(a); dx=lna[1]-lna[0]; z=1/a-1
psi=0.015*(1+z)**2.7/(1+((1+z)/2.9)**5.6); S=psi/np.trapezoid(psi,lna)
def rho(tau):
    r=np.zeros(len(a))
    for i in range(1,len(a)): r[i]=r[i-1]+dx*(S[i-1]-r[i-1]/tau)
    return r/r[-1]
def mu(r):
    E=np.sqrt(Om0*a**-3+Orad0*a**-4+(1-Om0-Orad0)*r)
    o=np.argsort(z); zs=z[o]
    Dc=cumulative_trapezoid(c_km/(H0*E[o]),zs,initial=0)
    return zs,5*np.log10(np.maximum((1+zs)*Dc,1e-10))+25
def cplshape(w0,wa): return a**(-3*(1+w0+wa))*np.exp(-3*wa*(1-a))
def proj(r):
    zt,mt=mu(r); sel=(zt>=0.01)&(zt<=2.3)
    def mod(zq,w0,wa):
        zz,mm=mu(cplshape(w0,wa)); return np.interp(zq,zz,mm)
    p,_=curve_fit(mod,zt[sel],mt[sel],p0=[-0.85,-0.45],maxfev=3000)
    return p
print("ECF-MD14 falsifiable locus segment (CPL projection) across tau = 2.1 +0.6/-0.4:")
for tau in [1.7,1.9,2.1,2.3,2.7]:
    r=rho(tau); p=proj(r)
    late=a>1/11; i=np.argmax(r[late]); idx=np.where(late)[0][i]; zp=1/a[idx]-1
    print(f"  tau={tau:.1f}:  (w0, wa) = ({p[0]:+.3f}, {p[1]:+.3f})   rho_DE peak z={zp:.2f}")
