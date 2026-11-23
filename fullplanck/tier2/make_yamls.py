"""Generate the Tier 2 minimizer yamls from the certified kit yamls (PREREG_NEUTRINO_TIER2.md).

Every run file is derived from fullplanck/{lcdm,ecf_full,cpl_full}.yaml by loading it
and applying ONLY the modifications listed below, so any difference from the certified
kit is explicit:

  ALL fits:
    - sampler: mcmc -> minimize (cobaya defaults kept: bobyqa, rhoend 0.05,
      ignore_prior False), best_of 1 per process, explicit seed, and covmat = the
      certified chain covmat for that model (used only to scale minimizer steps).
    - output -> tier2/chains/<fit>_s<k>; packages_path -> the July install.
    - ECF only: theory python_path '.' -> absolute fullplanck/ path, so the kit's own
      ecf_theory_cobaya.py / ecf_physics.py are imported (no copies).
  start s0: kit `ref` values unchanged (the exact kit start point; mnu ref 0.06).
  starts s1..: `ref` replaced by the START-POINT distributions in REF_DIST below. `ref`
    sets only where the minimizer starts. It is not part of the prior or likelihood.
  free-Sigma-mnu fits (3,4,5): `mnu` removed from theory extra_args and added as a
    sampled parameter with flat prior [0.0, 1.0] eV (the pre-registered prior). All other
    neutrino settings (num_massive_neutrinos: 1, CAMB defaults) are unchanged.
"""
import copy, os, sys, yaml

KIT = '/Users/420-420/ecf-md14/fullplanck'
T2 = os.path.join(KIT, 'tier2')
PACKAGES = '/Users/420-420/Downloads/ecf-fullplanck-kit/packages'

# Start-point distributions (scale roughly 1.5-2x the certified posterior widths; the
# dark-energy and mnu parameters are spread across their plausible range).
REF_DIST = {
    'logA':     {'dist': 'norm', 'loc': 3.044,   'scale': 0.02},
    'ns':       {'dist': 'norm', 'loc': 0.965,   'scale': 0.006},
    'H0':       {'dist': 'norm', 'loc': 67.7,    'scale': 1.0},
    'ombh2':    {'dist': 'norm', 'loc': 0.02237, 'scale': 0.0002},
    'omch2':    {'dist': 'norm', 'loc': 0.1195,  'scale': 0.0015},
    'tau':      {'dist': 'norm', 'loc': 0.0544,  'scale': 0.01},
    'A_planck': {'dist': 'norm', 'loc': 1.0,     'scale': 0.0025},
    'tau_ecf':  {'dist': 'uniform', 'min': 1.5,  'max': 4.5},
    'w':        {'dist': 'norm', 'loc': -0.86,   'scale': 0.10},
    'wa':       {'dist': 'norm', 'loc': -0.5,    'scale': 0.30},
    'mnu':      {'dist': 'uniform', 'min': 0.0,  'max': 0.6},
}

MNU_PARAM = {'prior': {'min': 0.0, 'max': 1.0}, 'ref': 0.06, 'proposal': 0.05,
             'latex': r'\Sigma m_\nu'}

FITS = {  # fit id: (kit yaml, free mnu?, covmat)
    'fit1_lcdm_mnufixed': ('lcdm.yaml',     False, 'lcdm.covmat'),
    'fit2_ecf_mnufixed':  ('ecf_full.yaml', False, 'ecf.covmat'),
    'fit3_lcdm_mnufree':  ('lcdm.yaml',     True,  'lcdm.covmat'),
    'fit4_ecf_mnufree':   ('ecf_full.yaml', True,  'ecf.covmat'),
    'fit5_cpl_mnufree':   ('cpl_full.yaml', True,  'cpl.covmat'),
}


def make(fit, start):
    kit_yaml, free_mnu, covmat = FITS[fit]
    with open(os.path.join(KIT, kit_yaml)) as f:
        info = yaml.safe_load(f)
    info = copy.deepcopy(info)
    # theory: locate extra_args
    (tname, tinfo), = info['theory'].items()
    if 'python_path' in tinfo:
        assert tinfo['python_path'] == '.'
        tinfo['python_path'] = KIT
    extra = tinfo['extra_args']
    if free_mnu:
        assert extra.pop('mnu') == 0.06
        info['params']['mnu'] = copy.deepcopy(MNU_PARAM)
    if start > 0:
        for p, pinfo in info['params'].items():
            if isinstance(pinfo, dict) and 'prior' in pinfo:
                pinfo['ref'] = copy.deepcopy(REF_DIST[p])
    info['sampler'] = {'minimize': {'best_of': 1, 'seed': 1000 + start,
                                    'covmat': os.path.join(T2, 'covmats', covmat)}}
    info['output'] = os.path.join(T2, 'chains', f'{fit}_s{start}')
    info['packages_path'] = PACKAGES
    out = os.path.join(T2, 'yamls', f'{fit}_s{start}.yaml')
    with open(out, 'w') as f:
        yaml.safe_dump(info, f, sort_keys=False)
    return out


if __name__ == '__main__':
    fits = sys.argv[1].split(',')
    nstarts = int(sys.argv[2])
    for fit in fits:
        for s in range(nstarts):
            print(make(fit, s))
