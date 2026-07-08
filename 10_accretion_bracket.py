import numpy as np
exec(open('/home/claude/gateb/gateb2.py').read().split("rl=fit('LCDM'")[0])
from scipy.optimize import minimize
from scipy.signal import lfilter

h_f=0.6736; E2fid=0.315*ag**-3+(w_rad/h_f**2)*ag**-4+(1-0.315-w_rad/h_f**2)
def dpl(z,p1,zc,p2): return (1+z)**p1/(1+((1+z)/zc)**p2)

# Sources (per-time, CCBH-exact weighting): S = rho_dot_BH(z)/H
sources={
 'SFR (MD14)      ': psi,
 'BHARD-A (mild)  ': dpl(zg,3.5,3.1,8.0),   # peak z~2.0, z=1->0 drop x11
 'BHARD-B (steep) ': dpl(zg,4.0,3.2,9.0),   # peak z~2.1, z=1->0 drop x16
}
c0=np.load('/home/claude/gateb/b2.npy')[0]

def make_chi2(S_raw):
    S=S_raw/np.sqrt(E2fid); S=S/np.trapezoid(S,lna)
    def fDE(k):
        if k>=2.999:
            r=np.concatenate([[0],np.cumsum(0.5*(S[1:]+S[:-1])*dxl)])
        else:
            tau=1/(3-k)
            r=lfilter([0.0,dxl],[1.0,-(1.0-dxl/tau)],S)
        r=r/max(r[-1],1e-30)
        f=np.interp(zf,zg[::-1],r[::-1]); f[zf>30]=0.0
        return f,r
    def chi2(p,kfix=None):
        if kfix is None: Om,H0,wb,k=p
        else: Om,H0,wb=p; k=kfix
        if not(0.18<Om<0.48 and 52<H0<83 and 0.0192<wb<0.0258): return 1e12
        if kfix is None and not(0.3<k<2.999): return 1e12
        h=H0/100; wm=Om*h*h; Orad=w_rad/h**2; ODE=1-Om-Orad
        f,_=fDE(k)
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
    return chi2,fDE

print(f"benchmarks: LCDM=0 | SFR-CCBH free-k = -3.11 (k=1.91) | phenomenological per-efold = -7.61\n")
for name,Sr in sources.items():
    chi2,fDE=make_chi2(Sr)
    r3=minimize(lambda p:chi2(p,kfix=3.0),[0.312,67.8,0.02245],method='Powell',options={'xtol':1e-6,'ftol':1e-9})
    best=None
    for x0 in [[0.312,67.8,0.02245,2.2],[0.31,68,0.0225,1.9],[0.315,67.5,0.0224,2.5]]:
        r=minimize(chi2,x0,method='Powell',options={'xtol':1e-6,'ftol':1e-9,'maxiter':40000})
        if best is None or r.fun<best.fun: best=r
    kb=best.x[3]
    # w(z=0) at best fit
    f,rho=fDE(kb)
    w0=-1-np.gradient(np.log(np.maximum(rho,1e-300)),lna)[-1]/3
    late=ag>1/11; ip=np.argmax(rho[late]); idx=np.where(late)[0][ip]; zpk=0.0 if idx>=Nl-2 else 1/ag[idx]-1
    print(f"{name}: k=3 exact: dchi2={r3.fun-c0:+7.2f} | free-k: dchi2={best.fun-c0:+6.2f}  k={kb:.2f}  w0={w0:+.3f}  rho-peak z={zpk:.2f}")
    prof=[]
    for k in [1.9,2.1,2.3,2.5,2.7]:
        r=minimize(lambda p:chi2(p,kfix=k),[best.x[0],best.x[1],best.x[2]],method='Powell',options={'xtol':1e-6,'ftol':1e-9})
        prof.append(f"k={k}:{r.fun-c0:+.2f}")
    print(f"   profile: {'  '.join(prof)}\n")
