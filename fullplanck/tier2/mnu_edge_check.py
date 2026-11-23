"""Diagnostic: behaviour of the registered stack as mnu -> 0 (not a gate)."""
import numpy as np, camb
from cobaya.model import get_model
from cobaya.yaml import yaml_load_file
KIT = '/Users/420-420/ecf-md14/fullplanck'
# (a) The G0 test_module configuration: camb.set_params(mnu=0.0, nnu=3.046), default num_massive_neutrinos=1
p = camb.set_params(H0=67.79, ombh2=0.02245, omch2=0.312*0.6779**2-0.02245, mnu=0.0, nnu=3.046,
                    tau=0.054, As=2.1e-9, ns=0.965)
print(f'test_module config: num_nu_massless={p.num_nu_massless} num_nu_massive={p.num_nu_massive} '
      f'nu_mass_eigenstates={p.nu_mass_eigenstates} omnuh2={p.omnuh2} N_eff={p.N_eff}')
p = camb.set_params(H0=67.79, ombh2=0.02245, omch2=0.312*0.6779**2-0.02245, mnu=0.0, nnu=3.046,
                    num_massive_neutrinos=0, tau=0.054, As=2.1e-9, ns=0.965)
print(f'same with num_massive_neutrinos=0: num_nu_massless={p.num_nu_massless} num_nu_massive={p.num_nu_massive} N_eff={p.N_eff}')
# (b) chi2 vs mnu near the lower prior edge at the certified best-fit points
def load_min(name):
    with open(f'{KIT}/chains/{name}.minimum.txt') as f:
        hdr = f.readline().lstrip('#').split(); vals = [float(v) for v in f.readline().split()]
    return dict(zip(hdr, vals))
for fit, base in [('fit3_lcdm_mnufree', 'lcdm'), ('fit4_ecf_mnufree', 'ecf')]:
    info = yaml_load_file(f'{KIT}/tier2/yamls/{fit}_s0.yaml'); info.pop('sampler'); info.pop('output')
    model = get_model(info); c = load_min(base)
    tr = [t for n, t in model.theory.items() if n.endswith('camb.transfers')][0]
    print(f'\n{fit} at certified {base} best-fit point (other params fixed):')
    for m in (0.0, 1e-8, 1e-6, 1e-4, 1e-3, 0.01, 0.03, 0.06):
        pt = {k: c[k] for k in model.parameterization.sampled_params() if k != 'mnu'}; pt['mnu'] = m
        lp = model.logposterior(pt)
        P = tr.current_state['results'][0]
        print(f'  mnu={m:<8g} chi2_total={-2*sum(lp.loglikes):12.4f}  N_eff={P.N_eff:.4f}  '
              f'num_nu_massless={P.num_nu_massless:.4f} num_nu_massive={P.num_nu_massive}')
