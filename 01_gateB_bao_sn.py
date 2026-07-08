import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.signal import lfilter
from scipy.optimize import minimize

# ================= DATA =================
# --- DESI DR2 BAO ---
rows=[l.split() for l in open('/home/claude/gateb/desi_dr2_mean.txt') if not l.startswith('#')]
z_bao=np.array([float(r[0]) for r in rows])
v_bao=np.array([float(r[1]) for r in rows])
q_bao=[r[2] for r in rows]
C_bao=np.loadtxt('/home/claude/gateb/desi_dr2_cov.txt')
Cinv_bao=np.linalg.inv(C_bao)

# --- Pantheon+ ---
import pandas as pd
df=pd.read_csv('/home/claude/gateb/pp.dat',sep=r'\s+')
mask=(df['zHD'].values>0.01)
z_sn=df['zHD'].values[mask]; m_sn=df['m_b_corr'].values[mask]
n_all=len(df)
cov_flat=np.fromfile('/home/claude/gateb/pp.cov',sep=' ')
n_hdr=int(cov_flat[0]); C_full=cov_flat[1:].reshape(n_hdr,n_hdr)
C_sn=C_full[np.ix_(mask,mask)]
cho=cho_factor(C_sn)
ones=np.ones(len(z_sn))
Cinv_1=cho_solve(cho,ones); A11=ones@Cinv_1
print(f"SN after z>0.01 cut: {len(z_sn)}   BAO points: {len(z_bao)}")

# ================= MODELS =================
Orad=9.24e-5
Nlna=2500; lna=np.linspace(np.log(1/31.0),0.0,Nlna); ag=np.exp(lna); dx=lna[1]-lna[0]
zg=1/ag-1
psi=0.015*(1+zg)**2.7/(1+((1+zg)/2.9)**5.6)     # Madau-Dickinson 2014, fixed
S_efold=psi/np.trapezoid(psi,lna)

zfine=np.linspace(0,3.0,3000)

def rho_ecf(tau, per_time=False, Om=0.3):
    if per_time:
        E2L=Om*ag**-3+Orad*ag**-4+(1-Om-Orad)   # weighting only; mild circularity, noted
        S=psi/np.sqrt(E2L); S=S/np.trapezoid(S,lna)
    else: S=S_efold
    r=lfilter([0.0,dx],[1.0,-(1.0-dx/tau)],S)
    return r/max(r[-1],1e-30)

def E_of_z(model,p):
    Om=p[0]
    if model=='LCDM': fDE=np.ones(Nlna)
    elif model=='CPL':
        w0,wa=p[2],p[3]
        fDE=ag**(-3*(1+w0+wa))*np.exp(-3*wa*(1-ag))
    elif model=='ECF':  fDE=rho_ecf(p[2])
    elif model=='ECFt': fDE=rho_ecf(p[2],per_time=True,Om=Om)
    E2=Om*ag**-3+Orad*ag**-4+(1-Om-Orad)*fDE
    E_g=np.sqrt(E2)
    Ez=np.interp(zfine,zg[::-1],E_g[::-1])
    I=np.concatenate([[0],np.cumsum(0.5*(1/Ez[1:]+1/Ez[:-1])*np.diff(zfine))])
    return Ez,I

def chi2(model,p):
    Om,beta=p[0],p[1]
    if Om<=0.05 or Om>=0.7 or beta<=5: return 1e12
    if model=='ECF' or model=='ECFt':
        if p[2]<0.05 or p[2]>8: return 1e12
    Ez,I=E_of_z(model,p)
    # SN (M profiled analytically)
    mu_t=5*np.log10(np.maximum((1+z_sn)*np.interp(z_sn,zfine,I),1e-12))
    d=m_sn-mu_t
    Cd=cho_solve(cho,d)
    c2_sn=d@Cd-(ones@Cd)**2/A11
    # BAO
    Iz=np.interp(z_bao,zfine,I); Ez_b=np.interp(z_bao,zfine,Ez)
    pred=np.empty(len(z_bao))
    for i,q in enumerate(q_bao):
        if q=='DM_over_rs': pred[i]=beta*Iz[i]
        elif q=='DH_over_rs': pred[i]=beta/Ez_b[i]
        else: pred[i]=beta*(Iz[i]**2*z_bao[i]/Ez_b[i])**(1/3)
    r=v_bao-pred
    return c2_sn + r@Cinv_bao@r

def fit(model,x0s):
    best=None
    for x0 in x0s:
        res=minimize(lambda p:chi2(model,p),x0,method='Powell',
                     options={'xtol':1e-6,'ftol':1e-8,'maxiter':20000})
        if best is None or res.fun<best.fun: best=res
    return best

# ---- sanity: LCDM ----
r=fit('LCDM',[[0.31,29.0],[0.35,28.0]])
print(f"\nSANITY  LCDM: chi2={r.fun:.2f}  Om={r.x[0]:.4f}  beta={r.x[1]:.3f}")
Ndat=len(z_sn)+len(z_bao)
print(f"        chi2/dof = {r.fun/(Ndat-3):.3f}   (published Pantheon+ LCDM Om ~ 0.32-0.35 SN-only; BAO pulls ~0.30)")
np.save('/home/claude/gateb/lcdm.npy',np.array([r.fun,*r.x]))

# ================= THE CONTEST =================
lc=np.load('/home/claude/gateb/lcdm.npy'); chi2_L=lc[0]
res_cpl=fit('CPL',[[0.31,29.5,-0.9,-0.5],[0.30,29.7,-0.8,-1.0],[0.32,29.5,-1.0,0.0],[0.30,29.6,-0.7,-1.5]])
res_ecf=fit('ECF',[[0.31,29.5,1.5],[0.30,29.7,0.8],[0.32,29.5,3.0]])
res_ect=fit('ECFt',[[0.31,29.5,1.2],[0.30,29.7,0.6],[0.32,29.5,2.5]])

Ndat=len(z_sn)+len(z_bao); lnN=np.log(Ndat)
print(f"\n{'='*78}\nGATE B: joint fit to DESI DR2 BAO (13 pts) + Pantheon+ SN (1590 pts)\n{'='*78}")
print(f"{'model':<12}{'k':>3}{'chi2':>10}{'dchi2':>8}{'AIC':>10}{'dAIC':>8}{'BIC':>10}{'dBIC':>8}   best-fit")
def row(name,k,c2,params):
    aic=c2+2*k; bic=c2+k*lnN
    return name,k,c2,aic,bic,params
rows=[row('LCDM',3,chi2_L,f"Om={lc[1]:.3f}"),
      row('ECF-MD14',4,res_ecf.fun,f"Om={res_ecf.x[0]:.3f} tau={res_ecf.x[2]:.2f}"),
      row('ECF-MD14/H',4,res_ect.fun,f"Om={res_ect.x[0]:.3f} tau={res_ect.x[2]:.2f}"),
      row('CPL',5,res_cpl.fun,f"Om={res_cpl.x[0]:.3f} w0={res_cpl.x[2]:.3f} wa={res_cpl.x[3]:.3f}")]
aic0=rows[0][3]; bic0=rows[0][4]
for n,k,c2,aic,bic,ps in rows:
    print(f"{n:<12}{k:>3}{c2:>10.2f}{c2-chi2_L:>8.2f}{aic:>10.2f}{aic-aic0:>8.2f}{bic:>10.2f}{bic-bic0:>8.2f}   {ps}")
print(f"\n(dAIC/dBIC negative = better than LCDM; ~2 'positive evidence', ~6 'strong')")
