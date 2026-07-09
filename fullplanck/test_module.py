"""GATE TEST -- must print PASS before any chains are run.
Feeds the tau=2.10 w(a) table to CAMB (background only, massless nu to match
the reference) and checks H(z)/H0 against reference_checkpoints.csv to 0.3%."""
import numpy as np, camb
from ecf_physics import w_of_a_table

ref = np.genfromtxt('reference_checkpoints.csv', delimiter=',', names=True)
ok = True
for tau in (1.5, 2.10, 3.0):
    a, w = w_of_a_table(tau)
    pars = camb.set_params(H0=67.79, ombh2=0.02245, omch2=0.312*0.6779**2-0.02245,
                           mnu=0.0, nnu=3.046, tau=0.054, As=2.1e-9, ns=0.965)
    pars.DarkEnergy = camb.dark_energy.DarkEnergyPPF()
    pars.DarkEnergy.set_w_a_table(a, w)
    res = camb.get_background(pars)
    sel = ref[np.isclose(ref['tau'], tau)]
    for row in sel:
        z, E_ref = row['z'], row['E']
        E_camb = res.hubble_parameter(z)/res.hubble_parameter(0.0)
        d = abs(E_camb/E_ref - 1)
        flag = "ok " if d < 0.003 else "FAIL"
        if d >= 0.003: ok = False
        print(f"tau={tau:4.2f} z={z:4.2f}  E_camb={E_camb:.5f}  E_ref={E_ref:.5f}  diff={100*d:.3f}%  {flag}")
print("\n" + ("PASS - proceed to chains" if ok else "FAIL - STOP. Debug before running anything."))
