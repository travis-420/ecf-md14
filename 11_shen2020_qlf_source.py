import numpy as np
exec(open('/home/claude/gateb/gateb2.py').read().split("rl=fit('LCDM'")[0])
from scipy.optimize import minimize
from scipy.signal import lfilter

# ---- Shen et al. 2020 bolometric QLF, global fits A and B (Table 4, verified from paper) ----
zref=2.0; xz=(1+zg)/(1+zref)
def U_shen(fit):
    if fit=='B':
        g1=0.3653*xz**(-0.6006)
        b0,b1,b2=2.4709,-0.9963,1.0716
        c0,c1,c2=12.9656,-0.5758,0.4698
        d0,d1=-3.6276,-0.3444
    else:  # fit A
        t=1+zg
        g1=0.8569-0.2614*t+0.0200*(2*t**2-1)
        b0,b1,b2=2.5375,-1.0425,1.1201
        c0,c1,c2=13.0088,-0.5759,0.4554
        d0,d1=-3.5426,-0.3936
    g2=2*b0/(xz**b1+xz**b2)
    logLs=2*c0/(xz**c1+xz**c2)
    logphis=d0+d1*(1+zg)
    ll=np.linspace(8,16,320)                    # log10 L/Lsun, AGN floor 1e8 Lsun
    LL=10**ll[None,:]; Ls=10**logLs[:,None]
    r=LL/Ls
    phi=10**logphis[:,None]/(r**g1[:,None]+r**g2[:,None])
    U=np.trapezoid(LL*phi,ll,axis=1)
    U[zg>7.0]=0.0                               # LF constrained only to z=7
    return np.maximum(U,0.0)

h_f=0.6736; E2fid=0.315*ag**-3+(w_rad/h_f**2)*ag**-4+(1-0.315-w_rad/h_f**2)
c0L=np.load('/home/claude/gateb/b2.npy')[0]

def run(name,U):
    i2=np.argmin(np.abs(zg-2)); i1=np.argmin(np.abs(zg-1))
    print(f"\n{name}:  U(z=2)/U(0)={U[i2]/U[-1]:.1f}   U(z=1)/U(0)={U[i1]/U[-1]:.1f}   (SFR: 8.8, 4.4)")
    S=U/np.sqrt(E2fid); S=S/np.trapezoid(S,lna)
    def fDE(k):
        if k>=2.999: r=np.concatenate([[0],np.cumsum(0.5*(S[1:]+S[:-1])*dxl)])
        else:
            tau=1/(3-k); r=lfilter([0.0,dxl],[1.0,-(1.0-dxl/tau)],S)
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
    r3=minimize(lambda p:chi2(p,kfix=3.0),[0.312,67.8,0.02245],method='Powell',options={'xtol':1e-6,'ftol':1e-9})
    best=None
    for x0 in [[0.312,67.8,0.02245,2.5],[0.31,68,0.0225,2.65],[0.315,67.5,0.0224,2.3]]:
        r=minimize(chi2,x0,method='Powell',options={'xtol':1e-6,'ftol':1e-9,'maxiter':40000})
        if best is None or r.fun<best.fun: best=r
    kb=best.x[3]
    f,rho=fDE(kb)
    w0=-1-np.gradient(np.log(np.maximum(rho,1e-300)),lna)[-1]/3
    late=ag>1/11; ip=np.argmax(rho[late]); idx=np.where(late)[0][ip]
    zpk=0.0 if idx>=Nl-2 else 1/ag[idx]-1
    print(f"  k=3 exact: dchi2={r3.fun-c0L:+7.2f}")
    print(f"  free-k:    dchi2={best.fun-c0L:+7.2f}   k={kb:.3f}   w0={w0:+.3f}   rho-peak z={zpk:.2f}")
    print(f"  profile:")
    for k in [2.2,2.4,2.5,2.6,2.7,2.8,2.9]:
        r=minimize(lambda p:chi2(p,kfix=k),[best.x[0],best.x[1],best.x[2]],method='Powell',options={'xtol':1e-6,'ftol':1e-9})
        print(f"    k={k:.2f}  dchi2={r.fun-c0L:+7.2f}")

print("benchmarks: LCDM=0 | SFR source: -3.11 (k=1.91) | bracket steep: -6.38 (k=2.57) | phenomenological: -7.61")
run('Shen2020 GLOBAL FIT B (Lacy et al. source)', U_shen('B'))
run('Shen2020 GLOBAL FIT A (robustness)', U_shen('A'))
