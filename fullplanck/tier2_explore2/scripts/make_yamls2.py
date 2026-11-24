"""EXPLORATORY minimizer study 2 (not a gate attempt). Base-minimization yamls for steps 3 and 4.

Logic copied from fullplanck/tier2_rerun/make_yamls.py (session 2, read-only), which implements
AMENDMENT_TIER2_MINIMIZER.md section 2. Changed only:
  - seed base 2000 -> 9000 (s1..s7 use seeds 9001..9007, as the brief for this study requires;
    s0 gets 9000 by the same formula, which has no effect because s0's `ref` values are fixed numbers);
  - outputs -> fullplanck/tier2_explore2/ (yamls/, chains/), tag prefix 'base_';
  - the fit list is restricted to the three models this study may touch, all at FIXED Sigma-mnu = 0.06 eV:
      fit1_lcdm_mnufixed (lcdm.yaml), fit2_ecf_mnufixed (ecf_full.yaml),
      cpl_mnufixed (cpl_full.yaml as shipped; NOT fit 5, which has free Sigma-mnu).
    No free-Sigma-mnu model can be produced by this script (asserted).
Unchanged: likelihoods, theory and extra_args, priors, start-point (`ref`) distributions of section 2.3,
s0 = certified July best fit, covmats (session 2's byte-identical copies), rhoend 0.005, best_of 1.
"""
import copy, os, sys, yaml

KIT = '/Users/420-420/ecf-md14/fullplanck'
COV = os.path.join(KIT, 'tier2_rerun', 'covmats')   # read-only; SHA-256 checked in logs/session_start.log
OUT = os.path.join(KIT, 'tier2_explore2')
PACKAGES = '/Users/420-420/Downloads/ecf-fullplanck-kit/packages'
RHOEND = 0.005
SEED_BASE = 9000

REF_DIST = {   # identical to session 2 (AMENDMENT_TIER2_MINIMIZER.md section 2.3); mnu deliberately absent
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
}

FITS = {  # fit id: (kit yaml, covmat, certified minimum file for s0)
    'fit1_lcdm_mnufixed': ('lcdm.yaml',     'lcdm.covmat', 'lcdm'),
    'fit2_ecf_mnufixed':  ('ecf_full.yaml', 'ecf.covmat',  'ecf'),
    'cpl_mnufixed':       ('cpl_full.yaml', 'cpl.covmat',  'cpl'),
}


def read_min(name):
    with open(os.path.join(KIT, 'chains', f'{name}.minimum.txt')) as f:
        h = f.readline().lstrip('#').split(); v = [float(x) for x in f.readline().split()]
    return dict(zip(h, v))


def make(fit, start):
    kit_yaml, covmat, certname = FITS[fit]
    with open(os.path.join(KIT, kit_yaml)) as f:
        info = copy.deepcopy(yaml.safe_load(f))
    (tname, tinfo), = info['theory'].items()
    if 'python_path' in tinfo:
        assert tinfo['python_path'] == '.'
        tinfo['python_path'] = KIT
    assert tinfo['extra_args']['mnu'] == 0.06 and 'mnu' not in info['params'], 'fixed Sigma-mnu only'
    sampled = [p for p, pi in info['params'].items() if isinstance(pi, dict) and 'prior' in pi]
    assert 'mnu' not in sampled
    if start == 0:
        cert = read_min(certname)
        for p in sampled:
            info['params'][p]['ref'] = cert[p]
    else:
        for p in sampled:
            info['params'][p]['ref'] = copy.deepcopy(REF_DIST[p])
    info['sampler'] = {'minimize': {'best_of': 1, 'seed': SEED_BASE + start,
                                    'covmat': os.path.join(COV, covmat),
                                    'override_bobyqa': {'rhoend': RHOEND}}}
    info['output'] = os.path.join(OUT, 'chains', f'base_{fit}_s{start}')
    info['packages_path'] = PACKAGES
    out = os.path.join(OUT, 'yamls', f'base_{fit}_s{start}.yaml')
    with open(out, 'w') as f:
        yaml.safe_dump(info, f, sort_keys=False)
    return out


if __name__ == '__main__':
    for fit in sys.argv[1].split(','):
        assert fit in FITS, f'not allowed in this study: {fit}'
        for s in range(int(sys.argv[2])):
            print(make(fit, s))
