"""Generate the Tier 2 RERUN minimizer yamls (AMENDMENT_TIER2_MINIMIZER.md, commit 1fd858e).

Copied from fullplanck/tier2/make_yamls.py (session 1). Changed ONLY where the amendments require:
  - rhoend 0.05 -> 0.005 via sampler.minimize.override_bobyqa (minimizer amendment section 2.1).
    Everything else stays at cobaya 3.6.2 minimize defaults (bobyqa, rhobeg 1.0, ignore_prior False,
    default max_evals and confidence_for_unbounded), best_of 1 per process.
  - seed 1000+k -> 2000+k (section 2.3: s1..s7 use seeds 2001..2007). s0 gets 2000 by the same
    formula; cobaya 3.6.2 uses the seed only to draw the start point from `ref`
    (minimize.py: prior.reference(random_state=self._rng)), and s0's `ref` values are fixed
    numbers, so s0's seed has no effect.
  - s0 = the certified July best-fit point: every sampled parameter's `ref` is set to its value in
    fullplanck/chains/{lcdm,ecf,cpl}.minimum.txt (fit1/fit3: lcdm, fit2/fit4: ecf, fit5: cpl);
    fits 3-5 also start at mnu = 0.06 (section 2.3).
  - s1..s7: `ref` = the start-point distributions of section 2.3 (identical to session 1's
    REF_DIST except mnu uniform[1e-5, 0.6]).
  - free-mnu fits: flat prior [1e-5, 1.0] eV (AMENDMENT_TIER2_PRIOR.md, 37b8f12; section 2.5).
  - output, covmat paths -> fullplanck/tier2_rerun/ (covmats byte-identical, SHA-256 in section 2.3).
Unchanged: likelihoods, theory and extra_args, priors of all other params, packages_path.
"""
import copy, os, sys, yaml

KIT = '/Users/420-420/ecf-md14/fullplanck'
T2 = os.path.join(KIT, 'tier2_rerun')
PACKAGES = '/Users/420-420/Downloads/ecf-fullplanck-kit/packages'
RHOEND = 0.005
SEED_BASE = 2000

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
    'mnu':      {'dist': 'uniform', 'min': 1e-5, 'max': 0.6},
}

MNU_PARAM = {'prior': {'min': 1e-5, 'max': 1.0}, 'ref': 0.06, 'proposal': 0.05,
             'latex': r'\Sigma m_\nu'}

FITS = {  # fit id: (kit yaml, free mnu?, covmat, certified minimum file for s0)
    'fit1_lcdm_mnufixed': ('lcdm.yaml',     False, 'lcdm.covmat', 'lcdm'),
    'fit2_ecf_mnufixed':  ('ecf_full.yaml', False, 'ecf.covmat',  'ecf'),
    'fit3_lcdm_mnufree':  ('lcdm.yaml',     True,  'lcdm.covmat', 'lcdm'),
    'fit4_ecf_mnufree':   ('ecf_full.yaml', True,  'ecf.covmat',  'ecf'),
    'fit5_cpl_mnufree':   ('cpl_full.yaml', True,  'cpl.covmat',  'cpl'),
}


def read_min(name):
    with open(os.path.join(KIT, 'chains', f'{name}.minimum.txt')) as f:
        h = f.readline().lstrip('#').split(); v = [float(x) for x in f.readline().split()]
    return dict(zip(h, v))


def make(fit, start):
    kit_yaml, free_mnu, covmat, certname = FITS[fit]
    with open(os.path.join(KIT, kit_yaml)) as f:
        info = yaml.safe_load(f)
    info = copy.deepcopy(info)
    (tname, tinfo), = info['theory'].items()
    if 'python_path' in tinfo:
        assert tinfo['python_path'] == '.'
        tinfo['python_path'] = KIT
    extra = tinfo['extra_args']
    if free_mnu:
        assert extra.pop('mnu') == 0.06
        info['params']['mnu'] = copy.deepcopy(MNU_PARAM)
    sampled = [p for p, pi in info['params'].items() if isinstance(pi, dict) and 'prior' in pi]
    if start == 0:
        cert = read_min(certname)
        for p in sampled:
            info['params'][p]['ref'] = 0.06 if p == 'mnu' else cert[p]
    else:
        for p in sampled:
            info['params'][p]['ref'] = copy.deepcopy(REF_DIST[p])
    info['sampler'] = {'minimize': {'best_of': 1, 'seed': SEED_BASE + start,
                                    'covmat': os.path.join(T2, 'covmats', covmat),
                                    'override_bobyqa': {'rhoend': RHOEND}}}
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
