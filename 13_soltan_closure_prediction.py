import numpy as np
from scipy.optimize import brentq

# ---- Shen et al. 2020 global fit B, ABSOLUTE units ----
zg2=np.linspace(0.0,10.0,2001)
xz=(1+zg2)/3.0
g1=0.3653*xz**(-0.6006)
g2=2*2.4709/(xz**(-0.9963)+xz**(1.0716))
logLs=2*12.9656/(xz**(-0.5758)+xz**(0.4698))
logphis=-3.6276-0.3444*(1+zg2)
ll=np.linspace(8,16,400)
LL=10**ll[None,:]; Ls=10**logLs[:,None]
r=LL/Ls
phi=10**logphis[:,None]/(r**g1[:,None]+r**g2[:,None])   # Mpc^-3 dex^-1
U=np.trapezoid(LL*phi,ll,axis=1)*3.828e33                # erg/s/Mpc^3

# background (joint best fit; radiation negligible here)
Om=0.312; H0=67.8
H=(H0/3.0857e19)*np.sqrt(Om*(1+zg2)**3+(1-Om))           # s^-1
c=2.998e10; Msun=1.989e33

def rho_local(k,eta=0.1):
    # coupled Soltan (Lacy et al. eq.9 at z=0): each cohort grows by (1+z')^k
    integ=(1-eta)/(eta*c*c)*U*(1+zg2)**(k-1.0)/H
    return np.trapezoid(integ,zg2)/Msun                  # Msun/Mpc^3

print("VALIDATION")
print(f"  k=0 (standard Soltan), eta=0.10: rho = {rho_local(0.0):.3e} Msun/Mpc^3")
print(f"    (classic literature: ~2-5e5; Marconi+04: 4.6e5)")
for tgt,name in [(1.0e6,'standard census 1.0e6'),(7.4e6,'GWB census 7.4e6')]:
    kk=brentq(lambda k: rho_local(k)-tgt,0.0,4.0)
    print(f"  k required for {name} (eta=0.1): k = {kk:.2f}")
print(f"    (Lacy et al. published: low census -> k<~2; high census -> k=3 viable)")

print("\nTHE PREDICTION: local SMBH mass density required by our measured k")
print(f"  {'k':>5} | {'eta=0.057':>11} {'eta=0.10':>11} {'eta=0.20':>11}   (Msun/Mpc^3)")
for k in [2.0,2.19,2.30,2.40,2.57,3.0]:
    row=[rho_local(k,e) for e in (0.057,0.10,0.20)]
    tag=" <-- measured range" if 2.19<=k<=2.40 else ""
    print(f"  {k:>5.2f} | {row[0]:>11.2e} {row[1]:>11.2e} {row[2]:>11.2e}{tag}")

print("\nInversion at the measured k-range midpoint (k=2.30):")
print(f"  required census at eta=0.10: {rho_local(2.30,0.10):.2e}")
print(f"  ratio to standard 1.0e6:  x{rho_local(2.30,0.10)/1.0e6:.1f}")
print(f"  ratio to GWB 7.4e6:       x{rho_local(2.30,0.10)/7.4e6:.2f}")
