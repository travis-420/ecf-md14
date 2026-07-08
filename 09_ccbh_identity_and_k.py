import numpy as np
exec(open('/home/claude/gateb/gateb2.py').read().split("rl=fit('LCDM'")[0])
from scipy.optimize import minimize
from scipy.signal import lfilter

# per-time (CCBH-exact) source: S = psi/H, LCDM weighting (fiducial), normalized
h_f=0.6736; E2fid=0.315*ag**-3+(w_rad/h_f**2)*ag**-4+(1-0.315-w_rad/h_f**2)
S_t=psi/np.sqrt(E2fid); S_t=S_t/np.trapezoid(S_t,lna)

# ---- STEP 1: identity check  (direct CCBH integral vs leaky integrator) ----
tau0=1.2; k0=3-1/tau0
rho_dir=np.zeros(Nl)
for i in range(Nl):
    m=lna<=lna[i]
    rho_dir[i]=np.trapezoid(S_t[m]*np.exp((k0-3)*(lna[i]-lna[m])),lna[m])
rho_dir/=rho_dir[-1]
r_leak=lfilter([0.0,dxl],[1.0,-(1.0-dxl/tau0)],S_t); r_leak/=r_leak[-1]
print(f"IDENTITY CHECK (k={k0:.3f} vs tau={tau0}): max|direct-leaky| = {np.max(np.abs(rho_dir-r_leak)):.2e}")

def fDE_k(k):
    if k>=2.999:  # pure integrator (k=3): cumulative accumulation
        r=np.concatenate([[0],np.cumsum(0.5*(S_t[1:]+S_t[:-1])*dxl)])
    else:
        tau=1/(3-k)
        r=lfilter([0.0,dxl],[1.0,-(1.0-dxl/tau)],S_t)
    r=r/max(r[-1],1e-30)
    f=np.interp(zf,zg[::-1],r[::-1]); f[zf>30]=0.0
    return f

def chi2_k(p,kfix=None):
    if kfix is None: Om,H0,wb,k=p
    else: Om,H0,wb=p; k=kfix
    if not(0.18<Om<0.48 and 52<H0<83 and 0.0192<wb<0.0258 and 0.3<k<2.999 or (kfix is not None and kfix>=2.999 and 0.18<Om<0.48 and 52<H0<83 and 0.0192<wb<0.0258)): return 1e12
    h=H0/100; wm=Om*h*h; Orad=w_rad/h**2; ODE=1-Om-Orad
    f=fDE_k(k)
    E=np.sqrt(np.maximum(Om*(1+zf)**3+Orad*(1+zf)**4+ODE*f,1e-12))
    I=np.concatenate([[0],np.cumsum(0.5*(1/E[1:]+1/E[:-1])*np.diff(zf))])
    DC=c_km/H0*I
    mu=5*np.log10(np.maximum((1+z_sn)*np.interp(z_sn,zf,DC),1e-9))+25
    d=m_sn-mu; Cd=cho_solve(cho,d); c2=d@Cd-(ones@Cd)**2/A11
    rd=cal_d*rs_at(zdrag_EH(wb,wm),wb,wm,h)
    DMb=np.interp(z_bao,zf,DC); Eb=np.interp(z_bao,zf,E)
    pr=np.empty(len(z_bao))
    for i,q in enumerate(q_bao):
        if q=='DM_over_rs': pr[i]=DMb[i]/rd
        elif q=='DH_over_rs': pr[i]=c_km/(H0*Eb[i])/rd
        else: pr[i]=(DMb[i]**2*c_km*z_bao[i]/(H0*Eb[i]))**(1/3)/rd
    rr=v_bao-pr; c2+=rr@Cinv_bao@rr
    zs=zstar_HS(wb,wm); rst=cal_s*rs_at(zs,wb,wm,h)
    DMs=c_km/H0*np.interp(zs,zf,I)
    vec=np.array([np.sqrt(Om)*H0/c_km*DMs,np.pi*DMs/rst,wb])-v_cmb
    return c2+vec@Cinv_cmb@vec

c0=np.load('/home/claude/gateb/b2.npy')[0]

# ---- STEP 2: zero-parameter pure-vacuum case k=3 exactly ----
r3=None
for x0 in [[0.312,67.8,0.02245],[0.30,69,0.0225]]:
    r=minimize(lambda p:chi2_k(p,kfix=3.0),x0,method='Powell',options={'xtol':1e-6,'ftol':1e-9})
    if r3 is None or r.fun<r3.fun: r3=r
print(f"\nk=3 EXACT (pure vacuum interiors, ZERO new params): chi2={r3.fun:.2f}  dchi2 vs LCDM={r3.fun-c0:+.2f}")

# ---- STEP 3: free-k CCBH fit ----
best=None
for x0 in [[0.312,67.8,0.02245,2.15],[0.31,68,0.0225,1.9],[0.315,67.5,0.0224,2.4]]:
    r=minimize(chi2_k,x0,method='Powell',options={'xtol':1e-6,'ftol':1e-9,'maxiter':40000})
    if best is None or r.fun<best.fun: best=r
kb=best.x[3]
print(f"free-k CCBH fit: chi2={best.fun:.2f}  dchi2={best.fun-c0:+.2f}")
print(f"  Om={best.x[0]:.3f} H0={best.x[1]:.2f} wb={best.x[2]:.5f}  ==>  k = {kb:.3f}  (tau_t = {1/(3-kb):.2f})")

# ---- STEP 4: k profile ----
print("\nk profile (min over Om,H0,wb at each k):")
for k in [1.6,1.8,2.0,2.1,2.2,2.3,2.5,2.7,2.9]:
    r=minimize(lambda p:chi2_k(p,kfix=k),[best.x[0],best.x[1],best.x[2]],method='Powell',options={'xtol':1e-6,'ftol':1e-9})
    print(f"  k={k:4.2f}  chi2={r.fun:8.2f}  dchi2 vs LCDM={r.fun-c0:+7.2f}")
