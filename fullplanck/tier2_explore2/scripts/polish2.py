"""EXPLORATORY minimizer study 2 (not a gate attempt). Restart-polish driver (steps 2, 3, 4).

Adapted from the first study's fullplanck/tier2_explore/scripts/polish.py (read-only). Same round and stop rule:
  round 0 = the start's existing endpoint;
  round r = cobaya 3.6.2 `minimize` started exactly at the round r-1 endpoint (`ref` = fixed numbers, full double
            precision), on the same yaml as the run that produced round 0, except the `sampler` block (VARIANT) and
            the output path;
  stop after MAXR = 5 rounds, or when a round lowers -log posterior by less than TOL = 0.001, or (never mid-round)
  if the deadline has passed before a round would start.
Differences from the first study's driver (bookkeeping only):
  * a failed round (Py-BOBYQA/scipy not successful -> cobaya raises 'Minimization failed!', or any exception) is
    caught and logged as a 'CRASH' record with the solver's flag/message/evaluation count, and the start stops;
    the first study let the process die with the same effect;
  * no `seed` in the polish sampler block (the start point is fixed, so cobaya draws nothing);
  * source 'base' reads round 0 from this study's base_run.py JSON (full double precision).
Sources:  'session2' -> yaml fullplanck/tier2_rerun/yamls/<fit>_s<k>.yaml, round 0 from
                        fullplanck/tier2_rerun/chains/<fit>_s<k>.minimum (10 significant digits) -- as the first study;
          'base'     -> yaml tier2_explore2/yamls/base_<fit>_s<k>.yaml, round 0 from tier2_explore2/logs/base_<fit>_s<k>.json.
Fixed Sigma-mnu models only (asserted): fit1_lcdm_mnufixed, fit2_ecf_mnufixed, cpl_mnufixed.
Usage: python polish2.py <tag> <fit> <k> <deadline_epoch> <variant> <source>
"""
import sys, os, time, json, copy, traceback
import numpy as np, yaml
from cobaya.run import run
import cobaya.samplers.minimize.minimize as CM

KIT = '/Users/420-420/ecf-md14/fullplanck'
RERUN = os.path.join(KIT, 'tier2_rerun')
EXP2 = os.path.join(KIT, 'tier2_explore2')
FITS_ALLOWED = ('fit1_lcdm_mnufixed', 'fit2_ecf_mnufixed', 'cpl_mnufixed')
MAXR = 5
TOL = 0.001

VARIANTS = {
    # candidate (i): Py-BOBYQA npt = (n+1)(n+2)/2 - 1 (36-1 = 35 for fit 1, 45-1 = 44 for fit 2, 55-1 = 54 for CPL)
    'c1_nptfullm1': {'override_bobyqa': {'rhoend': 0.005, 'npt': 'FULLM1'}},
    # candidate (ii): full npt = (n+1)(n+2)/2 with a smaller initial trust radius; cobaya sets rhobeg 1.0 and then
    # applies override_bobyqa with recursive_update, so this replaces it (no conflict, read from minimize.py)
    'c2_nptfull_rhobeg0.1': {'override_bobyqa': {'rhoend': 0.005, 'npt': 'FULL', 'rhobeg': 0.1}},
    # candidate (iii): scipy.optimize.minimize Powell (bounded) via cobaya `method: scipy`; options exactly as
    # pre-configured (never run) in the first study's polish.py: xtol 1e-4 (scaled units), ftol 1e-8 (relative,
    # ~2e-5 absolute), maxfev 3000 as a cap.
    'c3_powell': {'method': 'scipy',
                  'override_scipy': {'method': 'Powell', 'options': {'xtol': 1e-4, 'ftol': 1e-8, 'maxfev': 3000}}},
    # candidate (iv) (only if (i)-(iii) all fail): full npt, cobaya's rhobeg 1.0, but Py-BOBYQA's initial interpolation
    # set built from fully random (non-orthogonal) unit directions instead of +-coordinate/pair points. Step 1 found that
    # any initial set containing antipodal pairs x0 +- delta*v_i gives every other point a Lagrange polynomial with zero
    # gradient at x0, which makes trsbox_geometry return x_opt; random non-orthogonal directions have no such pairs.
    # Py-BOBYQA draws these directions from numpy's global RNG, so the driver seeds it with np_seed_base + k
    # before every round (9100 + k; outside the reserved/used ranges), which makes each round deterministic.
    'c4_nptfull_randdirs': {'override_bobyqa': {'rhoend': 0.005, 'npt': 'FULL',
                                                'user_params': {'init.random_initial_directions': True,
                                                                'init.random_directions_make_orthogonal': False}},
                            'np_seed_base': 9100},
}

LAST = {}
_solve = CM.pybobyqa.solve
def _rec_solve(**kw):
    r = _solve(**kw); LAST['res'] = r; return r
CM.pybobyqa.solve = _rec_solve
_smin = CM.optimize.minimize
def _rec_smin(*a, **kw):
    r = _smin(*a, **kw); LAST['res'] = r; return r
CM.optimize.minimize = _rec_smin


def read_getdist_min(path):
    vals = {}
    with open(path) as f:
        lines = f.read().splitlines()
    mlp = float(lines[0].split('=')[1])
    for ln in lines[3:]:
        p = ln.split()
        if len(p) >= 3 and p[0].isdigit():
            vals[p[2]] = float(p[1])
    return mlp, vals


def res_info(res):
    if res is None:
        return {'nf': None, 'flag': None, 'msg': None}
    if hasattr(res, 'EXIT_SUCCESS'):   # Py-BOBYQA
        return {'nf': int(res.nf), 'flag': int(res.flag), 'msg': str(res.msg), 'nruns': int(res.nruns),
                'success': bool(res.flag == res.EXIT_SUCCESS)}
    return {'nf': int(res.nfev), 'flag': int(res.status), 'msg': str(res.message),
            'nit': int(getattr(res, 'nit', -1)), 'success': bool(res.success)}


def main(tag, fit, k, deadline, variant, source):
    assert fit in FITS_ALLOWED, 'fixed Sigma-mnu models only'
    k = int(k); deadline = float(deadline)
    if source == 'session2':
        assert fit != 'cpl_mnufixed'
        ypath = os.path.join(RERUN, 'yamls', f'{fit}_s{k}.yaml')
    elif source == 'base':
        ypath = os.path.join(EXP2, 'yamls', f'base_{fit}_s{k}.yaml')
    else:
        raise ValueError(source)
    with open(ypath) as f:
        base = yaml.safe_load(f)
    th = base['theory'][list(base['theory'])[0]]
    assert 'mnu' not in base['params'] and th['extra_args']['mnu'] == 0.06, 'fixed Sigma-mnu models only'
    sampled = [p for p, pi in base['params'].items() if isinstance(pi, dict) and 'prior' in pi]
    if source == 'session2':
        mlp_prev, x_prev = read_getdist_min(os.path.join(RERUN, 'chains', f'{fit}_s{k}.minimum'))
        x_prev = {p: x_prev[p] for p in sampled}
        src = f'{RERUN}/chains/{fit}_s{k}.minimum'
    else:
        with open(os.path.join(EXP2, 'logs', f'base_{fit}_s{k}.json')) as f:
            b = json.load(f)
        assert b['status'] == 'converged', f'base run not converged: {b["status"]}'
        mlp_prev, x_prev = b['mlp'], b['x']
        src = f'{EXP2}/logs/base_{fit}_s{k}.json'
    print('ROUND0 ' + json.dumps({'tag': tag, 'fit': fit, 'start': k, 'round': 0, 'mlp': mlp_prev, 'x': x_prev,
                                  'source': src, 'yaml': ypath}), flush=True)
    n = len(sampled)
    for r in range(1, MAXR + 1):
        if time.time() > deadline:
            print(f'DEADLINE reached before round {r}; stopping (not started).', flush=True)
            break
        info = copy.deepcopy(base)
        for p in sampled:
            info['params'][p]['ref'] = float(x_prev[p])
        smp = {'best_of': 1, 'covmat': base['sampler']['minimize']['covmat']}
        smp.update(copy.deepcopy(VARIANTS[variant]))
        np_seed = smp.pop('np_seed_base', None)
        ob = smp.get('override_bobyqa', {})
        if ob.get('npt') == 'FULL':
            ob['npt'] = (n + 1) * (n + 2) // 2
        elif ob.get('npt') == 'FULLM1':
            ob['npt'] = (n + 1) * (n + 2) // 2 - 1
        info['sampler'] = {'minimize': smp}
        info['output'] = os.path.join(EXP2, 'chains', f'{tag}_{fit}_s{k}_r{r}')
        with open(os.path.join(EXP2, 'yamls', f'{tag}_{fit}_s{k}_r{r}.yaml'), 'w') as f:
            yaml.safe_dump(info, f, sort_keys=False)
        LAST.clear()
        if np_seed is not None:
            np.random.seed(np_seed + k)   # Py-BOBYQA random initial directions (global numpy RNG)
            print(f'numpy global RNG seeded with {np_seed + k} before round {r}', flush=True)
        t0 = time.time()
        try:
            upd, sampler = run(info)
        except Exception as e:
            dt = time.time() - t0
            traceback.print_exc()
            rec = {'tag': tag, 'fit': fit, 'start': k, 'round': r, 'variant': variant, 'wall_s': dt,
                   'error': str(e).splitlines()[0]}
            rec.update(res_info(LAST.get('res')))
            print('CRASH ' + json.dumps(rec), flush=True)
            print(f'STOP: round {r} failed; start stops with no result for this round', flush=True)
            break
        dt = time.time() - t0
        prod = sampler.products()
        m = prod['minimum']
        mlp = float(m['minuslogpost'])
        rec = {'tag': tag, 'fit': fit, 'start': k, 'round': r, 'variant': variant,
               'mlp': mlp, 'chi2': float(m['chi2']),
               'chi2_cmb': float(m['chi2__planck_2018_highl_plik.TTTEEE_lite_native']),
               'chi2_bao': float(m['chi2__bao.desi_dr2']), 'chi2_sn': float(m['chi2__sn.pantheonplus']),
               'tauterm': 2 * float(m['minuslogprior__tau_prior']),
               'x': {p: float(m[p]) for p in sampled}, 'improvement': mlp_prev - mlp, 'wall_s': dt}
        rec.update(res_info(prod['result_object']))
        print('ROUND ' + json.dumps(rec), flush=True)
        imp = mlp_prev - mlp
        mlp_prev, x_prev = mlp, rec['x']
        if imp < TOL:
            print(f'STOP: round {r} improved -log post by {imp:.6f} < {TOL}', flush=True)
            break
    else:
        print(f'STOP: reached {MAXR} rounds', flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:])
