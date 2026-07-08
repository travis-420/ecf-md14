import numpy as np
exec(open('/home/claude/gateb/gateb2.py').read().split("rl=fit('LCDM'")[0])
from scipy.optimize import minimize
from scipy.linalg import cho_factor, cho_solve

Cfull=cv[1:].reshape(n,n)

def chi2v(model,p,keep=None,snmask=None,use_sn=True,use_cmb=True,ret_parts=False):
    Om,H0,wb=p[0],p[1],p[2]
    if not(0.18<Om<0.48 and 52<H0<83 and 0.0192<wb<0.0258): return 1e12
    h=H0/100; wm=Om*h*h; Orad=w_rad/h**2; ODE=1-Om-Orad
    if model=='LCDM': f=np.ones_like(zf)
    elif model=='ECF':
        tau=p[3]
        if not 0.15<tau<8: return 1e12
        f=fDE_ecf(tau)
    E=np.sqrt(np.maximum(Om*(1+zf)**3+Orad*(1+zf)**4+ODE*f,1e-12))
    I=np.concatenate([[0],np.cumsum(0.5*(1/E[1:]+1/E[:-1])*np.diff(zf))])
    DC=c_km/H0*I
    parts={}
    c2=0.0
    if use_sn:
        if snmask is None: zs_,ms_,cho_,ones_,A11_=z_sn,m_sn,cho,ones,A11
        else:
            zs_=df['zHD'].values[snmask]; ms_=df['m_b_corr'].values[snmask]
            cho_=SN2_cho; ones_=np.ones(len(zs_)); A11_=ones_@cho_solve(cho_,ones_)
        mu=5*np.log10(np.maximum((1+zs_)*np.interp(zs_,zf,DC),1e-9))+25
        d=ms_-mu; Cd=cho_solve(cho_,d); csn=d@Cd-(ones_@Cd)**2/A11_
        c2+=csn; parts['SN']=csn
    rd=cal_d*rs_at(zdrag_EH(wb,wm),wb,wm,h)
    idx=np.arange(13) if keep is None else keep
    DMb=np.interp(z_bao[idx],zf,DC); Eb=np.interp(z_bao[idx],zf,E)
    pr=np.empty(len(idx))
    for j,i in enumerate(idx):
        q=q_bao[i]
        if q=='DM_over_rs': pr[j]=DMb[j]/rd
        elif q=='DH_over_rs': pr[j]=c_km/(H0*Eb[j])/rd
        else: pr[j]=(DMb[j]**2*c_km*z_bao[i]/(H0*Eb[j]))**(1/3)/rd
    Cb=np.loadtxt('/home/claude/gateb/desi_dr2_cov.txt')[np.ix_(idx,idx)]
    r=v_bao[idx]-pr; cb=r@np.linalg.inv(Cb)@r; c2+=cb; parts['BAO']=cb
    if use_cmb:
        zs=zstar_HS(wb,wm); rst=cal_s*rs_at(zs,wb,wm,h)
        DMs=c_km/H0*np.interp(zs,zf,I)
        vec=np.array([np.sqrt(Om)*H0/c_km*DMs,np.pi*DMs/rst,wb])-v_cmb
        cc=vec@Cinv_cmb@vec; c2+=cc; parts['CMB']=cc
    if ret_parts: return c2,parts,(pr,idx)
    return c2

def refit(model,x0,**kw):
    r=minimize(lambda p:chi2v(model,p,**kw),x0,method='Powell',
               options={'xtol':1e-5,'ftol':1e-8,'maxiter':30000})
    return r

xL=[0.3022,68.46,0.02254]; xE=[0.312,67.79,0.02245,2.10]
rL=refit('LCDM',xL); rE=refit('ECF',xE)
_,pL,(prdL,_)=chi2v('LCDM',rL.x,ret_parts=True)
_,pE,(prdE,_)=chi2v('ECF',rE.x,ret_parts=True)
print("PART 1: where the -7.6 lives (chi2 by dataset at each best fit)")
print(f"{'':10}{'SN':>10}{'BAO':>10}{'CMB':>10}{'total':>10}")
print(f"{'LCDM':10}{pL['SN']:>10.2f}{pL['BAO']:>10.2f}{pL['CMB']:>10.2f}{rL.fun:>10.2f}")
print(f"{'ECF':10}{pE['SN']:>10.2f}{pE['BAO']:>10.2f}{pE['CMB']:>10.2f}{rE.fun:>10.2f}")
print(f"{'delta':10}{pE['SN']-pL['SN']:>+10.2f}{pE['BAO']-pL['BAO']:>+10.2f}{pE['CMB']-pL['CMB']:>+10.2f}{rE.fun-rL.fun:>+10.2f}")

print("\nPART 2: BAO point-by-point pulls (data-model)/sigma")
sg=np.sqrt(np.diag(np.loadtxt('/home/claude/gateb/desi_dr2_cov.txt')))
print(f"{'z':>6} {'type':>12} {'LCDM pull':>10} {'ECF pull':>10}")
for i in range(13):
    print(f"{z_bao[i]:>6.3f} {q_bao[i]:>12} {(v_bao[i]-prdL[i])/sg[i]:>+10.2f} {(v_bao[i]-prdE[i])/sg[i]:>+10.2f}")

print("\nPART 3: leave-one-tracer-out  (dchi2 = ECF - LCDM, both refit)")
tr={0.295:'BGS',0.510:'LRG1',0.706:'LRG2',0.934:'LRG3+ELG1',1.321:'ELG2',1.484:'QSO',2.33:'Lya'}
for zt,nm in tr.items():
    keep=np.array([i for i in range(13) if abs(z_bao[i]-zt)>1e-6])
    a=refit('LCDM',rL.x,keep=keep); b=refit('ECF',rE.x,keep=keep)
    print(f"  drop {nm:<10} dchi2 = {b.fun-a.fun:+7.2f}   (full: -7.61)")

print("\nPART 4: dataset ablations")
a=refit('LCDM',rL.x,use_sn=False); b=refit('ECF',rE.x,use_sn=False)
print(f"  BAO+CMB only (no SN):   dchi2 = {b.fun-a.fun:+7.2f}")
print(f"  BAO+SN only  (no CMB):  dchi2 =   -5.16  (Gate B result)")

print("\nPART 5: SN robustness -- drop all z<0.1 (calibration-sensitive rung)")
snm=df['zHD'].values>0.1
SN2_cho=cho_factor(Cfull[np.ix_(snm,snm)])
a=refit('LCDM',rL.x,snmask=snm); b=refit('ECF',rE.x,snmask=snm)
print(f"  N_SN: {snm.sum()} (was {mask.sum()});  dchi2 = {b.fun-a.fun:+7.2f}")

print("\nPART 6: SN residuals vs LCDM, binned (diag errors, diagnostic only)")
muL=5*np.log10((1+z_sn)*np.interp(z_sn,zf,c_km/rL.x[1]*np.concatenate([[0],np.cumsum(0.5*(1/np.sqrt(rL.x[0]*(1+zf)**3+(w_rad/(rL.x[1]/100)**2)*(1+zf)**4+(1-rL.x[0]-w_rad/(rL.x[1]/100)**2))[1:]+1/np.sqrt(rL.x[0]*(1+zf)**3+(w_rad/(rL.x[1]/100)**2)*(1+zf)**4+(1-rL.x[0]-w_rad/(rL.x[1]/100)**2))[:-1])*np.diff(zf))])))+25
sig_d=df['m_b_corr_err_DIAG'].values[mask]
res=m_sn-muL; res-=np.average(res,weights=1/sig_d**2)
# ECF prediction curve relative to LCDM (mean-subtracted the same way)
h_=rE.x[1]/100; Or_=w_rad/h_**2
E_E=np.sqrt(rE.x[0]*(1+zf)**3+Or_*(1+zf)**4+(1-rE.x[0]-Or_)*fDE_ecf(rE.x[3]))
muE_f=5*np.log10(np.maximum((1+zf[1:])*np.interp(zf[1:],zf,c_km/rE.x[1]*np.concatenate([[0],np.cumsum(0.5*(1/E_E[1:]+1/E_E[:-1])*np.diff(zf))])),1e-9))+25
muL_f=5*np.log10(np.maximum((1+zf[1:])*np.interp(zf[1:],zf,c_km/rL.x[1]*np.concatenate([[0],np.cumsum(0.5*(1/np.sqrt(rL.x[0]*(1+zf)**3+(w_rad/(rL.x[1]/100)**2)*(1+zf)**4+(1-rL.x[0]-w_rad/(rL.x[1]/100)**2))[1:]+1/np.sqrt(rL.x[0]*(1+zf)**3+(w_rad/(rL.x[1]/100)**2)*(1+zf)**4+(1-rL.x[0]-w_rad/(rL.x[1]/100)**2))[:-1])*np.diff(zf))])),1e-9))+25
dmu=np.interp(z_sn,zf[1:],muE_f-muL_f); dmu-=np.average(dmu,weights=1/sig_d**2)
edges=[0.01,0.03,0.1,0.25,0.5,0.8,1.3,2.3]
print(f"{'z bin':>12} {'N':>5} {'data resid (mmag)':>18} {'ECF-LCDM pred':>14}")
for lo,hi in zip(edges[:-1],edges[1:]):
    m_=(z_sn>=lo)&(z_sn<hi)
    if m_.sum()<3: continue
    w=1/sig_d[m_]**2
    mr=np.average(res[m_],weights=w); er=1/np.sqrt(w.sum())
    mp=np.average(dmu[m_],weights=w)
    print(f"{lo:>5.2f}-{hi:<5.2f} {m_.sum():>5} {1000*mr:>+10.1f} +/- {1000*er:<5.1f} {1000*mp:>+12.1f}")
