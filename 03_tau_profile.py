import numpy as np
exec(open('/home/claude/gateb/gateb2.py').read().split("rl=fit('LCDM'")[0])
from scipy.optimize import minimize
c0=np.load('/home/claude/gateb/b2.npy')[0]
print("tau profile under full anchored fit (min over Om,H0,wb at each tau):")
for tau in [1.0,1.4,1.8,2.1,2.5,3.0,3.8,5.0]:
    r=minimize(lambda p:chi2('ECF',[p[0],p[1],p[2],tau]),[0.312,67.8,0.02245],
               method='Powell',options={'xtol':1e-6,'ftol':1e-9})
    print(f"  tau={tau:4.1f}  chi2={r.fun:8.2f}  dchi2 vs LCDM={r.fun-c0:+7.2f}")
