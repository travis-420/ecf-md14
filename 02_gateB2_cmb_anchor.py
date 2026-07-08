import numpy as np, pandas as pd
from scipy.linalg import cho_factor, cho_solve
from scipy.signal import lfilter
from scipy.optimize import minimize

c_km=299792.458; w_gam=2.469e-5; w_rad=w_gam*(1+0.2271*3.046)  # massless-nu

# ---------- data ----------
rows=[l.split() for l in open('/home/claude/gateb/desi_dr2_mean.txt') if not l.startswith('#')]
z_bao=np.array([float(r[0]) for r in rows]); v_bao=np.array([float(r[1]) for r in rows])
q_bao=[r[2] for r in rows]; Cinv_bao=np.linalg.inv(np.loadtxt('/home/claude/gateb/desi_dr2_cov.txt'))
df=pd.read_csv('/home/claude/gateb/pp.dat',sep=r'\s+'); mask=df['zHD'].values>0.01
z_sn=df['zHD'].values[mask]; m_sn=df['m_b_corr'].values[mask]
cv=np.fromfile('/home/claude/gateb/pp.cov',sep=' '); n=int(cv[0])
cho=cho_factor(cv[1:].reshape(n,n)[np.ix_(mask,mask)])
ones=np.ones(len(z_sn)); A11=ones@cho_solve(cho,ones)

# CMB compressed prior (Planck 2018 TT,TE,EE+lowE, wCDM set; arXiv 1808.05724)
v_cmb=np.array([1.7493,301.462,0.02239]); sig=np.array([0.00465,0.090,0.00015])
corr=np.array([[1,0.47,-0.66],[0.47,1,-0.34],[-0.66,-0.34,1]])
Cinv_cmb=np.linalg.inv(corr*np.outer(sig,sig))

# ---------- redshift grids ----------
z1=np.linspace(0,3,2400); z2=np.logspace(np.log10(3.002),np.log10(1300),900)
zf=np.concatenate([z1,z2])
Nl=2500; lna=np.linspace(np.log(1/31),0,Nl); ag=np.exp(lna); dxl=lna[1]-lna[0]; zg=1/ag-1
psi=0.015*(1+zg)**2.7/(1+((1+zg)/2.9)**5.6); S_ef=psi/np.trapezoid(psi,lna)

def zstar_HS(wb,wm):
    g1=0.0783*wb**-0.238/(1+39.5*wb**0.763); g2=0.560/(1+21.1*wb**1.81)
    return 1048*(1+0.00124*wb**-0.738)*(1+g1*wm**g2)
def zdrag_EH(wb,wm):
    b1=0.313*wm**-0.419*(1+0.607*wm**0.674); b2=0.238*wm**0.223
    return 1291*wm**0.251/(1+0.659*wm**0.828)*(1+b1*wb**b2)
al=np.logspace(-8,0,3000)
def rs_at(z_end,wb,wm,h):
    ae=1/(1+z_end); m=al<=ae; a=al[m]
    E=np.sqrt((wm/a**3+w_rad/a**4)/h**2)     # DE negligible in this regime
    cs=1/np.sqrt(3*(1+(3*wb/(4*w_gam))*a))
    return c_km/(100*h)*np.trapezoid(cs/(a**2*E),a)

# calibrate integrals once at Planck 2018 best fit (r*=144.43, rd=147.09 Mpc)
_wb,_Om,_h=0.02237,0.3153,0.6736; _wm=_Om*_h**2
cal_s=144.43/rs_at(zstar_HS(_wb,_wm),_wb,_wm,_h)
cal_d=147.09/rs_at(zdrag_EH(_wb,_wm),_wb,_wm,_h)
print(f"calibration factors  r*: {cal_s:.5f}   rd: {cal_d:.5f}  (pipeline vs CAMB at Planck point)")

def fDE_ecf(tau):
    r=lfilter([0.0,dxl],[1.0,-(1.0-dxl/tau)],S_ef); r=r/max(r[-1],1e-30)
    f=np.interp(zf,zg[::-1],r[::-1]); f[zf>30]=0.0
    return f

def chi2(model,p):
    Om,H0,wb=p[0],p[1],p[2]
    if not(0.18<Om<0.48 and 52<H0<83 and 0.0192<wb<0.0258): return 1e12
    h=H0/100; wm=Om*h*h; Orad=w_rad/h**2; ODE=1-Om-Orad
    if model=='LCDM': f=np.ones_like(zf)
    elif model=='ECF':
        tau=p[3]
        if not 0.15<tau<8: return 1e12
        f=fDE_ecf(tau)
    else:
        w0,wa=p[3],p[4]
        if not(-1.9<w0<-0.25 and -3<wa<1.3): return 1e12
        a=1/(1+zf); f=np.minimum(a**(-3*(1+w0+wa))*np.exp(-3*wa*(1-a)),1e12)
    E=np.sqrt(np.maximum(Om*(1+zf)**3+Orad*(1+zf)**4+ODE*f,1e-12))
    I=np.concatenate([[0],np.cumsum(0.5*(1/E[1:]+1/E[:-1])*np.diff(zf))])  # dimensionless
    DC=c_km/H0*I                                            # Mpc
    # SN
    mu=5*np.log10(np.maximum((1+z_sn)*np.interp(z_sn,zf,DC),1e-9))+25
    d=m_sn-mu; Cd=cho_solve(cho,d); c2=d@Cd-(ones@Cd)**2/A11
    # BAO
    rd=cal_d*rs_at(zdrag_EH(wb,wm),wb,wm,h)
    DMb=np.interp(z_bao,zf,DC); Eb=np.interp(z_bao,zf,E)
    pr=np.empty(len(z_bao))
    for i,q in enumerate(q_bao):
        if q=='DM_over_rs': pr[i]=DMb[i]/rd
        elif q=='DH_over_rs': pr[i]=c_km/(H0*Eb[i])/rd
        else: pr[i]=(DMb[i]**2*c_km*z_bao[i]/(H0*Eb[i]))**(1/3)/rd
    r=v_bao-pr; c2+=r@Cinv_bao@r
    # CMB
    zs=zstar_HS(wb,wm); rst=cal_s*rs_at(zs,wb,wm,h)
    DMs=c_km/H0*np.interp(zs,zf,I)
    vec=np.array([np.sqrt(Om)*H0/c_km*DMs, np.pi*DMs/rst, wb])-v_cmb
    return c2+vec@Cinv_cmb@vec

def fit(model,x0s):
    best=None
    for x0 in x0s:
        r=minimize(lambda p:chi2(model,p),x0,method='Powell',
                   options={'xtol':1e-6,'ftol':1e-9,'maxiter':40000})
        if best is None or r.fun<best.fun: best=r
    return best

rl=fit('LCDM',[[0.315,67.4,0.02237],[0.30,69,0.0225]])
print(f"\nSANITY LCDM+CMB: chi2={rl.fun:.2f}  Om={rl.x[0]:.4f} H0={rl.x[1]:.2f} wb={rl.x[2]:.5f}")
h=rl.x[1]/100; print(f"   implied rd = {cal_d*rs_at(zdrag_EH(rl.x[2],rl.x[0]*h*h),rl.x[2],rl.x[0]*h*h,h):.2f} Mpc  (Planck ~147)")

re=fit('ECF',[[0.315,67.5,0.02237,1.6],[0.31,68,0.0224,2.4],[0.32,67,0.0224,1.0]])
rc=fit('CPL',[[0.31,67.5,0.02238,-0.85,-0.6],[0.31,66,0.0224,-0.75,-1.0],[0.315,68,0.0224,-1.0,0.0],[0.30,65,0.0224,-0.6,-1.6]])

N=len(z_sn)+len(z_bao)+3; lnN=np.log(N)
print(f"\n{'='*80}\nGATE B.2: DESI DR2 BAO + Pantheon+ SN + Planck compressed CMB   (N={N})\n{'='*80}")
print(f"{'model':<10}{'k':>3}{'chi2':>10}{'dchi2':>8}{'dAIC':>8}{'dBIC':>8}   best fit")
c0=rl.fun
for nm,k,r_,ps in [('LCDM',4,rl,f"Om={rl.x[0]:.3f} H0={rl.x[1]:.2f}"),
                   ('ECF-MD14',5,re,f"Om={re.x[0]:.3f} H0={re.x[1]:.2f} tau={re.x[3]:.2f}"),
                   ('CPL',6,rc,f"Om={rc.x[0]:.3f} H0={rc.x[1]:.2f} w0={rc.x[3]:.3f} wa={rc.x[4]:.3f}")]:
    dA=(r_.fun+2*k)-(c0+2*4); dB=(r_.fun+k*lnN)-(c0+4*lnN)
    print(f"{nm:<10}{k:>3}{r_.fun:>10.2f}{r_.fun-c0:>8.2f}{dA:>8.2f}{dB:>8.2f}   {ps}")
np.save('/home/claude/gateb/b2.npy',np.array([rl.fun,re.fun,rc.fun,re.x[3]]))
