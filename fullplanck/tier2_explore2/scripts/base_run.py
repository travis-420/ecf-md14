"""EXPLORATORY minimizer study 2 (not a gate attempt). Base minimization for steps 3 and 4.

Runs cobaya 3.6.2 `minimize` on one yaml made by make_yamls2.py (AMENDMENT_TIER2_MINIMIZER.md section 2
settings, seeds 9000+k), unchanged, and dumps the result with full double precision to
logs/base_<fit>_s<k>.json so that a polish can start exactly at the endpoint. The Py-BOBYQA result object is
captured by a pass-through wrapper (no behavioural change) so that the evaluation count is known even if the
run fails. Fixed Sigma-mnu models only (asserted).
Usage: python base_run.py <fit> <k>
"""
import sys, os, json, time, traceback
import numpy as np, yaml
from cobaya.run import run
import cobaya.samplers.minimize.minimize as CM

EXP2 = '/Users/420-420/ecf-md14/fullplanck/tier2_explore2'
fit, k = sys.argv[1], int(sys.argv[2])
assert fit in ('fit1_lcdm_mnufixed', 'fit2_ecf_mnufixed', 'cpl_mnufixed')
LAST = {}
_solve = CM.pybobyqa.solve
def solve(**kw):
    r = _solve(**kw); LAST['res'] = r; return r
CM.pybobyqa.solve = solve

with open(os.path.join(EXP2, 'yamls', f'base_{fit}_s{k}.yaml')) as f:
    info = yaml.safe_load(f)
th = info['theory'][list(info['theory'])[0]]
assert th['extra_args']['mnu'] == 0.06 and 'mnu' not in info['params']
sampled = [p for p, pi in info['params'].items() if isinstance(pi, dict) and 'prior' in pi]
t0 = time.time()
rec = {'fit': fit, 'start': k, 'yaml': f'yamls/base_{fit}_s{k}.yaml', 'seed': info['sampler']['minimize']['seed']}
try:
    upd, sampler = run(info)
    prod = sampler.products(); m = prod['minimum']; res = prod['result_object']
    rec.update({'status': 'converged' if res.flag == res.EXIT_SUCCESS else 'not_converged',
                'mlp': float(m['minuslogpost']), 'chi2': float(m['chi2']),
                'chi2_cmb': float(m['chi2__planck_2018_highl_plik.TTTEEE_lite_native']),
                'chi2_bao': float(m['chi2__bao.desi_dr2']), 'chi2_sn': float(m['chi2__sn.pantheonplus']),
                'tauterm': 2 * float(m['minuslogprior__tau_prior']),
                'x': {p: float(m[p]) for p in sampled}, 'nf': int(res.nf), 'flag': int(res.flag), 'msg': res.msg,
                'x0': {p: float(v) for p, v in zip(sampled, sampler.initial_points[0])}})
except Exception as e:
    traceback.print_exc()
    r = LAST.get('res')
    rec.update({'status': 'failed', 'error': str(e).splitlines()[0],
                'nf': None if r is None else int(r.nf), 'flag': None if r is None else int(r.flag),
                'msg': None if r is None else r.msg})
rec['wall_s'] = time.time() - t0
with open(os.path.join(EXP2, 'logs', f'base_{fit}_s{k}.json'), 'w') as f:
    json.dump(rec, f)
print('BASE ' + json.dumps(rec), flush=True)
sys.exit(0 if rec['status'] == 'converged' else 1)
