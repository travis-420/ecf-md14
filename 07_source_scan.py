import numpy as np
from scipy.integrate import solve_ivp, cumulative_trapezoid
from scipy.optimize import curve_fit
from scipy.special import erfc
from scipy.interpolate import interp1d

Om0, Orad0, H0 = 0.315, 9.24e-5, 67.4
c_km=299792.458; OmDE=1-Om0-Orad0
N=4000; lna=np.linspace(np.log(1e-6),0.0,N); a=np.exp(lna); dx=lna[1]-lna[0]

# ---- LCDM background growth (feedback shown small yesterday; scan-level OK) ----
E2L = Om0*a**-3 + Orad0*a**-4 + OmDE
dlnH = 0.5*np.gradient(np.log(E2L),lna)
E2i=interp1d(lna,E2L,kind='cubic'); dHi=interp1d(lna,dlnH,kind='cubic')
x0=np.log(1e-3)
def rhs(x,y):
    D,Dp=y; Omv=Om0*np.exp(-3*x)/E2i(x)
    return [Dp, -(2+dHi(x))*Dp + 1.5*Omv*D]
xs=lna[lna>=x0]
sol=solve_ivp(rhs,[x0,0],[1e-3,1e-3],t_eval=xs,rtol=1e-8,atol=1e-12)
Dn=np.empty(N); m=lna>=x0-1e-12
Dn[m]=np.interp(lna[m],sol.t,sol.y[0]); Dn[~m]=sol.y[0][0]*np.exp(lna[~m]-x0)
Dn/=Dn[-1]
f_lin=np.empty(N); f_lin[m]=np.interp(lna[m],sol.t,sol.y[1]/sol.y[0])
OmA=Om0*a**-3/E2L; f_lin[~m]=OmA[~m]**0.55

# ---- Sources ----
S_lin = f_lin*OmA; S_lin/=np.trapezoid(S_lin,lna)      # yesterday's (linear growth)
def S_collapse(sig_eff, dc=1.686):                      # collapsed-structure / BH-formation proxy
    F = erfc(dc/(np.sqrt(2)*sig_eff*np.maximum(Dn,1e-12)))
    S = np.gradient(F,lna); S=np.maximum(S,0)
    n=np.trapezoid(S,lna)
    return S/n if n>0 else S

# ---- Kernel = leaky integrator, optional lag:  rho' = S(lna-lag) - rho/tau ----
def rho_of(S, tau, lag=0.0):
    if lag>0:
        Ssh=np.interp(lna-lag, lna, S, left=0.0); Ssh=np.maximum(Ssh,0)
    else: Ssh=S
    r=np.zeros(N)
    for i in range(1,N):
        r[i]=r[i-1]+dx*(Ssh[i-1]-r[i-1]/tau)
    return r/max(r[-1],1e-30)

def w_of(r): return -1-np.gradient(np.log(np.maximum(r,1e-300)),lna)/3
def mu_of(r):
    E=np.sqrt(Om0*a**-3+Orad0*a**-4+OmDE*r); z=1/a-1
    o=np.argsort(z); zs=z[o]
    Dc=cumulative_trapezoid(c_km/(H0*E[o]),zs,initial=0)
    return zs,5*np.log10(np.maximum((1+zs)*Dc,1e-10))+25
def shape_CPL(w0,wa): return a**(-3*(1+w0+wa))*np.exp(-3*wa*(1-a))
def fit_cpl(r):
    zt,mt=mu_of(r); sel=(zt>=0.01)&(zt<=2.3)
    def mod(z,w0,wa):
        zz,mm=mu_of(shape_CPL(w0,wa)); return np.interp(z,zz,mm)
    try:
        p,_=curve_fit(mod,zt[sel],mt[sel],p0=[-0.8,-0.4],maxfev=2000)
        return p
    except Exception: return [np.nan,np.nan]

def zpeak(r):
    late = a>1/(1+10)          # only look z<10
    i=np.argmax(r[late]); idx=np.where(late)[0][i]
    if idx>=N-2: return 0.0    # still rising today
    return 1/a[idx]-1

# DESI DR2+CMB+Pantheon+ 1-sigma window
W0LO,W0HI=-0.893,-0.783; WALO,WAHI=-0.81,-0.40

print(f"{'source':>18} {'tau':>5} {'lag':>4} | {'w(z=0)':>7} {'w0_fit':>7} {'wa_fit':>7} {'z_peak':>6} | in DESI box?")
print("-"*88)
hits=[]
# baseline from yesterday
for tau in [1.0,2.0]:
    r=rho_of(S_lin,tau); p=fit_cpl(r); w0z=w_of(r)[-1]
    tag = "YES" if (W0LO<=p[0]<=W0HI and WALO<=p[1]<=WAHI) else "no"
    print(f"{'linear-growth':>18} {tau:5.2f} {0:4.1f} | {w0z:7.3f} {p[0]:7.3f} {p[1]:7.3f} {zpeak(r):6.2f} | {tag}")

for sig in [1.5,2.0,2.5,3.0,4.0]:
    S=S_collapse(sig)
    for tau in [0.3,0.5,0.75,1.0,1.5,2.0]:
        r=rho_of(S,tau); p=fit_cpl(r); w0z=w_of(r)[-1]
        ok = (W0LO<=p[0]<=W0HI and WALO<=p[1]<=WAHI)
        tag="YES" if ok else "no"
        if ok: hits.append((f"collapse s={sig}",tau,0.0,p[0],p[1],zpeak(r)))
        print(f"{'collapse s='+str(sig):>18} {tau:5.2f} {0:4.1f} | {w0z:7.3f} {p[0]:7.3f} {p[1]:7.3f} {zpeak(r):6.2f} | {tag}")

# a couple of lagged variants (delayed response to collapse)
for sig,lagv,tau in [(2.0,0.3,0.3),(2.0,0.6,0.3),(2.5,0.5,0.5),(3.0,0.5,0.3)]:
    S=S_collapse(sig); r=rho_of(S,tau,lag=lagv); p=fit_cpl(r); w0z=w_of(r)[-1]
    ok=(W0LO<=p[0]<=W0HI and WALO<=p[1]<=WAHI)
    tag="YES" if ok else "no"
    if ok: hits.append((f"collapse s={sig} lag",tau,lagv,p[0],p[1],zpeak(r)))
    print(f"{'lag collapse s='+str(sig):>18} {tau:5.2f} {lagv:4.1f} | {w0z:7.3f} {p[0]:7.3f} {p[1]:7.3f} {zpeak(r):6.2f} | {tag}")

print()
print(f"Variants landing inside the DESI DR2+CMB+SN 1-sigma box: {len(hits)}")
for h in hits: print("  ",h)
