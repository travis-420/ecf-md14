"""Measurement for AMENDMENT_TIER2_PRIOR.md (diagnostic only; no fit).
For each free-mnu model (fits 3, 4, 5) and two test points per model, compares
  chi2(mnu = 1e-5 eV) against the correct chi2(mnu = 0.0)
where 'correct' means a freshly built cobaya model whose FIRST evaluation is mnu = 0.0
(so CAMB's cached base params have num_nu_massive = 0 and N_eff = 3.044).
1e-5 is evaluated in two cache states:
  (i)  model whose first evaluation was mnu = 0.06 (base params carry num_nu_massive = 1),
       i.e. the state every minimizer run is in, since all starts have mnu > 0;
  (ii) the mnu = 0-initialized model.
The corrupted chi2(0.0) in state (i) is also printed, to document the defect."""
import sys, numpy as np
sys.path.insert(0, '/Users/420-420/ecf-md14/fullplanck/tier2')
import yaml
from cobaya.model import get_model
import make_yamls as M

KIT = '/Users/420-420/ecf-md14/fullplanck'


def load_min(name):
    with open(f'{KIT}/chains/{name}.minimum.txt') as f:
        hdr = f.readline().lstrip('#').split(); vals = [float(v) for v in f.readline().split()]
    return dict(zip(hdr, vals))


def info_for(fit):
    # Build the fit's s0 info in memory exactly as make_yamls does, with the REGISTERED prior [0.0, 1.0].
    path = M.make(fit, 0)
    with open(path) as f:
        info = yaml.safe_load(f)
    assert info['params']['mnu']['prior'] == {'min': 0.0, 'max': 1.0}, info['params']['mnu']
    info.pop('sampler'); info.pop('output')
    return info


def ev(model, pt, mnu):
    p = {k: pt[k] for k in model.parameterization.sampled_params() if k != 'mnu'}
    p['mnu'] = mnu
    lp = model.logposterior(p)
    tr = [t for n, t in model.theory.items() if n.endswith('camb.transfers')][0]
    P = tr.current_state['results'][0]
    comps = [-2 * l for l in lp.loglikes]
    return sum(comps), comps, P.N_eff, P.num_nu_massive, P.num_nu_massless


ref_kit = {'logA': 3.044, 'ns': 0.965, 'H0': 67.7, 'ombh2': 0.02237, 'omch2': 0.1195,
           'tau': 0.0544, 'A_planck': 1.0, 'tau_ecf': 2.1, 'w': -0.86, 'wa': -0.5}
rows = []
for fit, base in [('fit3_lcdm_mnufree', 'lcdm'), ('fit4_ecf_mnufree', 'ecf'),
                  ('fit5_cpl_mnufree', 'cpl')]:
    info = info_for(fit)
    for ptname, pt in [(f'certified {base} best-fit', load_min(base)), ('kit ref point', ref_kit)]:
        m0 = get_model(info)                       # fresh; first evaluation at mnu = 0.0
        c0, comp0, ne0, nm0, nl0 = ev(m0, pt, 0.0)
        c0b, comp0b, ne0b, nm0b, nl0b = ev(m0, pt, 1e-5)   # state (ii)
        m6 = get_model(info)                       # fresh; first evaluation at mnu = 0.06
        c06, *_ = ev(m6, pt, 0.06)
        c5, comp5, ne5, nm5, nl5 = ev(m6, pt, 1e-5)        # state (i): minimizer-realistic
        cbad, _, nebad, nmbad, nlbad = ev(m6, pt, 0.0)     # corrupted edge
        names = list(m0.likelihood)
        print(f'\n== {fit} @ {ptname}')
        print(f'  chi2(mnu=0.0, clean model)          = {c0:.6f}   N_eff={ne0:.4f} num_nu_massive={nm0} num_nu_massless={nl0:.4f}')
        print(f'     components: ' + ', '.join(f'{n}={c:.6f}' for n, c in zip(names, comp0)))
        print(f'  chi2(mnu=1e-5, state i: base@0.06)  = {c5:.6f}   N_eff={ne5:.4f} num_nu_massive={nm5} num_nu_massless={nl5:.4f}')
        print(f'     components: ' + ', '.join(f'{n}={c:.6f}' for n, c in zip(names, comp5)))
        print(f'  chi2(mnu=1e-5, state ii: base@0.0)  = {c0b:.6f}   N_eff={ne0b:.4f} num_nu_massive={nm0b}')
        print(f'  diff  chi2(1e-5, i)  - chi2(0 clean) = {c5 - c0:+.6f}')
        print(f'  diff  chi2(1e-5, ii) - chi2(0 clean) = {c0b - c0:+.6f}')
        print(f'  [defect] chi2(mnu=0.0, state i)      = {cbad:.6f}   N_eff={nebad:.4f} num_nu_massive={nmbad} num_nu_massless={nlbad:.4f}')
        print(f'  [context] chi2(mnu=0.06)             = {c06:.6f}')
        rows.append((fit, ptname, c0, c5, c5 - c0, c0b - c0, cbad))
print('\nSUMMARY  fit | point | chi2(0 clean) | chi2(1e-5, minimizer state) | diff(i) | diff(ii) | chi2(0, corrupted)')
for r in rows:
    print(f'  {r[0]} | {r[1]} | {r[2]:.6f} | {r[3]:.6f} | {r[4]:+.6f} | {r[5]:+.6f} | {r[6]:.4f}')
print(f'max |diff| over all = {max(max(abs(r[4]), abs(r[5])) for r in rows):.3e}')
