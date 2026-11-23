"""Pre-minimizer model check (diagnostic, not a gate).
1. Re-evaluates chi2 at the certified best-fit points (fullplanck/chains/*.minimum.txt).
2. Confirms the free-mnu models evaluated at mnu=0.06 reproduce the fixed-mnu models.
3. Dumps the CAMB neutrino settings actually used (verbatim from CAMBparams).
4. Times one likelihood evaluation."""
import sys, time, numpy as np
from cobaya.model import get_model
from cobaya.yaml import yaml_load_file

KIT = '/Users/420-420/ecf-md14/fullplanck'
Y = KIT + '/tier2/yamls/'


def load_min(name):
    with open(f'{KIT}/chains/{name}.minimum.txt') as f:
        hdr = f.readline().lstrip('#').split()
        vals = [float(v) for v in f.readline().split()]
    return dict(zip(hdr, vals))


def nu_dump(model):
    tr = [t for n, t in model.theory.items() if n.endswith('camb.transfers')][0]
    p = tr.current_state['results'][0]
    out = {
        'num_nu_massless': p.num_nu_massless,
        'num_nu_massive': p.num_nu_massive,
        'nu_mass_eigenstates': p.nu_mass_eigenstates,
        'nu_mass_degeneracies': list(p.nu_mass_degeneracies[:p.nu_mass_eigenstates]),
        'nu_mass_fractions': list(p.nu_mass_fractions[:p.nu_mass_eigenstates]),
        'nu_mass_numbers': list(p.nu_mass_numbers[:p.nu_mass_eigenstates]),
        'omnuh2': p.omnuh2,
        'share_delta_neff': p.share_delta_neff,
        'N_eff': p.N_eff,
        'MassiveNuMethod': str(p.MassiveNuMethod),
        'YHe': p.YHe,
        'DarkEnergy': type(p.DarkEnergy).__name__,
        'NonLinearModel.halofit_version': p.NonLinearModel.halofit_version,
    }
    return out


def evaluate(model, point, label):
    sampled = list(model.parameterization.sampled_params())
    pt = {k: point[k] for k in sampled}
    t0 = time.time()
    lp = model.logposterior(pt)
    dt = time.time() - t0
    chi2s = {n: -2 * l for n, l in zip(model.likelihood, lp.loglikes)}
    chi2 = sum(chi2s.values())
    print(f'  [{label}] chi2_total = {chi2:.4f}  minuslogpost = {-lp.logpost:.4f}  '
          f'({dt:.1f} s)')
    for n, c in chi2s.items():
        print(f'      chi2__{n} = {c:.4f}')
    return chi2, chi2s, -lp.logpost


cert = {'lcdm': load_min('lcdm'), 'ecf': load_min('ecf'), 'cpl': load_min('cpl')}

for fit, base in [('fit1_lcdm_mnufixed', 'lcdm'), ('fit2_ecf_mnufixed', 'ecf'),
                  ('fit3_lcdm_mnufree', 'lcdm'), ('fit4_ecf_mnufree', 'ecf'),
                  ('fit5_cpl_mnufree', 'cpl')]:
    print(f'\n=== {fit}  (yaml {fit}_s0.yaml)')
    info = yaml_load_file(Y + f'{fit}_s0.yaml')
    info.pop('sampler'); info.pop('output')
    model = get_model(info)
    print('  sampled params:', list(model.parameterization.sampled_params()))
    (tname, tinfo), = info['theory'].items()
    print(f'  theory {tname} extra_args (yaml): {tinfo["extra_args"]}')
    pt = dict(cert[base])
    c = cert[base]
    if 'mnu' in model.parameterization.sampled_params():
        for m in (0.06, 0.0, 0.3):
            pt['mnu'] = m
            chi2, _, mlp = evaluate(model, pt, f'certified {base} min, mnu={m}')
            if m == 0.06:
                print(f'      vs certified {base} chi2 {c["chi2"]:.4f}: '
                      f'diff = {chi2 - c["chi2"]:+.5f}')
            print('      CAMB neutrino settings:', nu_dump(model))
    else:
        chi2, _, mlp = evaluate(model, pt, f'certified {base} min')
        print(f'      vs certified {base} chi2 {c["chi2"]:.4f}: diff = {chi2 - c["chi2"]:+.5f}; '
              f'minuslogpost vs {c["minuslogpost"]:.4f}: diff = {mlp - c["minuslogpost"]:+.5f}')
        print('      CAMB neutrino settings:', nu_dump(model))
    # timing of a fresh (uncached) evaluation
    pt2 = dict(pt); pt2['H0'] = pt['H0'] + 0.1
    t0 = time.time(); model.logposterior({k: pt2[k] for k in model.parameterization.sampled_params()})
    print(f'  timing: one uncached logposterior evaluation = {time.time() - t0:.2f} s')
