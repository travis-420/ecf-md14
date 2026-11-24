"""EXPLORATORY minimizer study (not a gate attempt) -- restart polishing driver.

For one session-2 start (fit1/fit2 only; fixed Sigma-mnu = 0.06 eV), repeatedly rerun the cobaya 3.6.2
`minimize` sampler starting from the previous endpoint:
  round 0  = the session-2 endpoint (read-only: fullplanck/tier2_rerun/chains/<fit>_s<k>.minimum, 10 sig. digits)
  round r  = cobaya minimize started at the round r-1 endpoint (full double precision), same yaml as session 2
             (read-only: fullplanck/tier2_rerun/yamls/<fit>_s<k>.yaml) except: `ref` = previous endpoint (fixed
             numbers), output -> fullplanck/tier2_explore/chains/, and the sampler block given by VARIANT.
Stop after MAXR rounds, or when a round improves -log posterior by less than TOL, or (never mid-round) when the
wall-clock deadline has passed before a round would start.
Usage: python polish.py <tag> <fit_id> <k> <deadline_epoch> <variant> [start_from_json]
"""
import sys, os, time, json, copy
import numpy as np, yaml
from cobaya.run import run

RERUN = '/Users/420-420/ecf-md14/fullplanck/tier2_rerun'
EXP = '/Users/420-420/ecf-md14/fullplanck/tier2_explore'
FITS_ALLOWED = ('fit1_lcdm_mnufixed', 'fit2_ecf_mnufixed')

VARIANTS = {
    # step 2: identical minimizer settings to session 2 (rhoend 0.005, rest cobaya 3.6.2 defaults, best_of 1)
    'bobyqa_rhoend0.005': {'override_bobyqa': {'rhoend': 0.005}},
    # step 3, alternative A: same as above but Py-BOBYQA full quadratic interpolation model,
    # npt = (n+1)(n+2)/2 (n = number of sampled params; 36 for fit 1, 45 for fit 2). Filled in main().
    'bobyqa_rhoend0.005_nptfull': {'override_bobyqa': {'rhoend': 0.005, 'npt': 'FULL'}},
    # step 3, alternative B (as run): alternative A plus Py-BOBYQA's built-in soft restarts, so that an
    # interpolation (linear-algebra) failure triggers a soft restart instead of an exit; Py-BOBYQA stops after
    # 1 consecutive restart that does not lower f; auto-detected restarts off.
    'bobyqa_rhoend0.005_nptfull_softrestart': {'override_bobyqa': {
        'rhoend': 0.005, 'npt': 'FULL',
        'user_params': {'restarts.use_restarts': True, 'restarts.use_soft_restarts': True,
                        'restarts.max_unsuccessful_restarts': 1, 'restarts.auto_detect': False}}},
    # (not run) scipy.optimize.minimize Powell (bounded), via cobaya `method: scipy`.
    # ftol is relative in scipy Powell: 1e-8 * ~2*982 ~ 2e-5 absolute per iteration (~ the step-1 noise floor);
    # xtol 1e-4 in cobaya's scaled units (conditional widths); maxfev 3000 as a safety cap.
    'scipy_powell': {'method': 'scipy',
                     'override_scipy': {'method': 'Powell',
                                        'options': {'xtol': 1e-4, 'ftol': 1e-8, 'maxfev': 3000}}},
}
MAXR = 5
TOL = 0.001


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


def main(tag, fit, k, deadline, variant, start_json=None):
    assert fit in FITS_ALLOWED, 'fits 1 and 2 only'
    k = int(k); deadline = float(deadline)
    with open(os.path.join(RERUN, 'yamls', f'{fit}_s{k}.yaml')) as f:
        base = yaml.safe_load(f)
    assert 'mnu' not in base['params'] and base['theory'][list(base['theory'])[0]]['extra_args']['mnu'] == 0.06
    sampled = [p for p, pi in base['params'].items() if isinstance(pi, dict) and 'prior' in pi]
    if start_json:
        with open(start_json) as f:
            st = json.load(f)[f'{fit}_s{k}']
        mlp_prev, x_prev = st['mlp'], st['x']
        src = f'{start_json} (key {fit}_s{k})'
    else:
        mlp_prev, x_prev = read_getdist_min(os.path.join(RERUN, 'chains', f'{fit}_s{k}.minimum'))
        x_prev = {p: x_prev[p] for p in sampled}
        src = f'{RERUN}/chains/{fit}_s{k}.minimum'
    rec0 = {'tag': tag, 'fit': fit, 'start': k, 'round': 0, 'mlp': mlp_prev, 'x': x_prev, 'source': src}
    print('ROUND0 ' + json.dumps(rec0), flush=True)
    for r in range(1, MAXR + 1):
        if time.time() > deadline:
            print(f'DEADLINE reached before round {r}; stopping (not started).', flush=True)
            break
        info = copy.deepcopy(base)
        for p in sampled:
            info['params'][p]['ref'] = float(x_prev[p])
        smp = {'best_of': 1, 'seed': base['sampler']['minimize']['seed'],
               'covmat': base['sampler']['minimize']['covmat']}
        smp.update(copy.deepcopy(VARIANTS[variant]))
        if smp.get('override_bobyqa', {}).get('npt') == 'FULL':
            n = len(sampled)
            smp['override_bobyqa']['npt'] = (n + 1) * (n + 2) // 2
        info['sampler'] = {'minimize': smp}
        info['output'] = os.path.join(EXP, 'chains', f'{tag}_{fit}_s{k}_r{r}')
        with open(os.path.join(EXP, 'yamls', f'{tag}_{fit}_s{k}_r{r}.yaml'), 'w') as f:
            yaml.safe_dump(info, f, sort_keys=False)
        t0 = time.time()
        upd, sampler = run(info)
        dt = time.time() - t0
        prod = sampler.products()
        res = prod['result_object']
        m = prod['minimum']
        mlp = float(m['minuslogpost'])
        rec = {'tag': tag, 'fit': fit, 'start': k, 'round': r, 'variant': variant,
               'mlp': mlp, 'chi2': float(m['chi2']),
               'chi2_cmb': float(m['chi2__planck_2018_highl_plik.TTTEEE_lite_native']),
               'chi2_bao': float(m['chi2__bao.desi_dr2']), 'chi2_sn': float(m['chi2__sn.pantheonplus']),
               'tauterm': 2 * float(m['minuslogprior__tau_prior']),
               'x': {p: float(m[p]) for p in sampled},
               'nf': int(getattr(res, 'nf', getattr(res, 'nfev', -1)) or -1),
               'flag': str(getattr(res, 'flag', getattr(res, 'status', None))),
               'msg': str(getattr(res, 'msg', getattr(res, 'message', ''))),
               'converged_cobaya': (bool(res.flag == res.EXIT_SUCCESS) if hasattr(res, 'EXIT_SUCCESS')
                                    else bool(res.success)),
               'improvement': mlp_prev - mlp, 'wall_s': dt}
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
