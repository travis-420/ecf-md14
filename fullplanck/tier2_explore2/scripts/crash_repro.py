"""EXPLORATORY minimizer study 2 (not a gate attempt). Step 1: reproduce and instrument the Py-BOBYQA crash.

Runs cobaya 3.6.2 `minimize` with the exact configuration of the first study's step3A fit2 s1 round 1
(read-only: fullplanck/tier2_explore/yamls/step3A_fit2_ecf_mnufixed_s1_r1.yaml), with only the output path
changed, and optional diagnostic variations (start-point shift, rhobeg, npt, maxfun). Fits 1/2 only
(fixed Sigma-mnu = 0.06 eV); asserted.

Instrumentation (monkeypatches; no change to cobaya/Py-BOBYQA behaviour):
  * pybobyqa.solve is wrapped to record every objective call (scaled x, f) and the solve() kwargs;
  * pybobyqa.solver.Controller is subclassed to record TR steps, replaced points, geometry steps;
  * pybobyqa.model.Model.interpolate_model is wrapped to snapshot the interpolation set before each call.
Everything is dumped to <out_json>. Analysis is done offline by crash_analyze.py.

Usage: python crash_repro.py <label> <src_yaml> [--shift-sigma S --shift-seed K] [--rhobeg R] [--npt N]
                             [--maxfun M] [--seed K] [--x0json '{...}']
"""
import sys, os, json, copy, time, argparse, traceback
import numpy as np, yaml

EXP2 = '/Users/420-420/ecf-md14/fullplanck/tier2_explore2'
ap = argparse.ArgumentParser()
ap.add_argument('label'); ap.add_argument('src_yaml')
ap.add_argument('--shift-sigma', type=float, default=0.0)
ap.add_argument('--shift-seed', type=int, default=0)
ap.add_argument('--rhobeg', type=float, default=None)
ap.add_argument('--npt', type=int, default=None)
ap.add_argument('--maxfun', type=int, default=None)
ap.add_argument('--seed', type=int, default=None)
ap.add_argument('--x0json', default=None, help='JSON dict of fixed start values (overrides ref)')
a = ap.parse_args()

import pybobyqa, pybobyqa.solver as PS, pybobyqa.controller as PC, pybobyqa.model as PM
from cobaya.run import run

REC = {'label': a.label, 'src_yaml': a.src_yaml, 'evals': [], 'events': [], 'snapshots': [], 'solve_kwargs': None}

_orig_solve = pybobyqa.solve
def rec_solve(**kw):
    objfun = kw.pop('objfun')
    REC['solve_kwargs'] = {k: (v.tolist() if isinstance(v, np.ndarray) else
                               [np.asarray(b).tolist() for b in v] if k == 'bounds' else v)
                           for k, v in kw.items()}
    def wrapped(x, *args):
        t0 = time.time(); f = objfun(x, *args)
        REC['evals'].append({'i': len(REC['evals']) + 1, 'x': np.asarray(x).tolist(), 'f': float(f),
                             'dt': time.time() - t0})
        return f
    return _orig_solve(objfun=wrapped, **kw)
pybobyqa.solve = rec_solve
import cobaya.samplers.minimize.minimize as CM
CM.pybobyqa.solve = rec_solve  # cobaya calls pybobyqa.solve via the module attribute

class RecController(PC.Controller):
    def trust_region_step(self, params):
        d, gopt, H, gnew, crvmin = super().trust_region_step(params)
        REC['events'].append({'type': 'tr_step', 'nf': self.nf, 'd': d.tolist(), 'delta': self.delta,
                              'rho': self.rho, 'kopt': int(self.model.kopt), 'xopt': self.model.xopt().tolist(),
                              'gopt': gopt.tolist(), 'H': H.tolist(), 'crvmin': float(crvmin)})
        return d, gopt, H, gnew, crvmin
    def choose_point_to_replace(self, d, skip_kopt=True):
        knew, ei = super().choose_point_to_replace(d, skip_kopt)
        REC['events'].append({'type': 'choose_replace', 'nf': self.nf, 'skip_kopt': skip_kopt,
                              'knew': None if knew is None else int(knew), 'exit': None if ei is None else ei.message()})
        return knew, ei
    def geometry_step(self, knew, adelt, number_of_samples, params):
        REC['events'].append({'type': 'geometry_step', 'nf': self.nf, 'knew': int(knew), 'adelt': adelt})
        return super().geometry_step(knew, adelt, number_of_samples, params)
    def soft_restart(self, *args, **kw):
        REC['events'].append({'type': 'soft_restart', 'nf': self.nf})
        return super().soft_restart(*args, **kw)
    def reduce_rho(self, current_iter, params):
        super().reduce_rho(current_iter, params)
        REC['events'].append({'type': 'reduce_rho', 'nf': self.nf, 'rho': self.rho, 'delta': self.delta})
PS.Controller = RecController

_orig_interp = PM.Model.interpolate_model
def rec_interp(self, *args, **kw):
    snap = {'npt_so_far': None, 'points': self.points.tolist(), 'fvals': self.f_values.tolist(),
            'kopt': int(self.kopt), 'xbase': self.xbase.tolist(), 'sl': self.sl.tolist(), 'su': self.su.tolist(),
            'n_evals_so_far': len(REC['evals'])}
    out = _orig_interp(self, *args, **kw)
    snap['ok'] = bool(out[0])
    REC['snapshots'].append(snap)
    return out
PM.Model.interpolate_model = rec_interp

with open(a.src_yaml) as f:
    info = yaml.safe_load(f)
th = info['theory'][list(info['theory'])[0]]
assert 'mnu' not in info['params'] and th['extra_args']['mnu'] == 0.06, 'fixed Sigma-mnu models only'
sampled = [p for p, pi in info['params'].items() if isinstance(pi, dict) and 'prior' in pi]
smp = info['sampler']['minimize']
ob = smp.setdefault('override_bobyqa', {})
if a.rhobeg is not None: ob['rhobeg'] = a.rhobeg
if a.npt is not None: ob['npt'] = a.npt
if a.maxfun is not None: ob['maxfun'] = a.maxfun
if a.seed is not None: smp['seed'] = a.seed  # inert for fixed ref; only used by cobaya to draw from ref
if a.x0json:
    for p, v in json.loads(a.x0json).items():
        info['params'][p]['ref'] = float(v)
assert all(not isinstance(info['params'][p]['ref'], dict) for p in sampled), 'fixed start points only'
if a.shift_sigma:
    # shift the (fixed) start point by shift_sigma conditional widths in a seeded random +-1 pattern
    covp = smp['covmat']
    with open(covp) as f:
        hdr = f.readline().split()[1:]
    C = np.loadtxt(covp)
    idx = [hdr.index(p) for p in sampled]
    cond = 1 / np.sqrt(np.diag(np.linalg.inv(C[np.ix_(idx, idx)])))
    s = np.random.default_rng(a.shift_seed).choice([-1.0, 1.0], size=len(sampled))
    for j, p in enumerate(sampled):
        info['params'][p]['ref'] = float(info['params'][p]['ref'] + a.shift_sigma * s[j] * cond[j])
REC['x0_phys'] = {p: info['params'][p]['ref'] for p in sampled}
REC['sampled'] = sampled
info['output'] = os.path.join(EXP2, 'chains', f'diag_{a.label}')
with open(os.path.join(EXP2, 'yamls', f'diag_{a.label}.yaml'), 'w') as f:
    yaml.safe_dump(info, f, sort_keys=False)
print('CONFIG ' + json.dumps({'label': a.label, 'sampler': info['sampler'], 'x0': REC['x0_phys']}), flush=True)

t0 = time.time()
try:
    upd, sampler = run(info)
    res = sampler.products()['result_object']
    REC['outcome'] = 'completed'
except Exception as e:
    REC['outcome'] = 'exception: ' + str(e).splitlines()[0]
    res = None
    traceback.print_exc()
REC['wall_s'] = time.time() - t0
if res is not None:
    REC['result'] = {'flag': int(res.flag), 'msg': res.msg, 'nf': int(res.nf), 'f': float(res.f)}
# the scales cobaya used (scaled = (x - x0)/scale)
REC['cobaya_note'] = 'scaled x = (x_phys - x0)/scale, scale = min(cond. width from covmat, prior range/3)'
out = os.path.join(EXP2, 'logs', f'diag_{a.label}.json')
with open(out, 'w') as f:
    json.dump(REC, f)
print(f'SUMMARY label={a.label} outcome={REC["outcome"]} n_evals={len(REC["evals"])} '
      f'n_snapshots={len(REC["snapshots"])} wall_s={REC["wall_s"]:.1f} json={out}', flush=True)
