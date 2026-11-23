"""G0 max |E_camb/E_ref - 1| over all checkpoints, same computation as test_module.py,
for the gate file (fullplanck/reference_checkpoints.csv) and the July kit reference."""
import sys, numpy as np, camb
sys.path.insert(0, '/Users/420-420/ecf-md14/fullplanck')
from ecf_physics import w_of_a_table
for label, path in [('fullplanck/ (gate)', '/Users/420-420/ecf-md14/fullplanck/reference_checkpoints.csv'),
                    ('July kit (supplementary)', '/Users/420-420/Downloads/ecf-fullplanck-kit/reference_checkpoints.csv')]:
    ref = np.genfromtxt(path, delimiter=',', names=True); ds = []
    for tau in (1.5, 2.10, 3.0):
        a, w = w_of_a_table(tau)
        pars = camb.set_params(H0=67.79, ombh2=0.02245, omch2=0.312*0.6779**2-0.02245,
                               mnu=0.0, nnu=3.046, tau=0.054, As=2.1e-9, ns=0.965)
        pars.DarkEnergy = camb.dark_energy.DarkEnergyPPF(); pars.DarkEnergy.set_w_a_table(a, w)
        res = camb.get_background(pars)
        for row in ref[np.isclose(ref['tau'], tau)]:
            ds.append(abs(res.hubble_parameter(row['z'])/res.hubble_parameter(0.0)/row['E'] - 1))
    print(f'{label}: n_checkpoints={len(ds)}  max |E_camb/E_ref-1| = {100*max(ds):.5f}%')
