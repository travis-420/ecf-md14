"""EXPLORATORY minimizer study (not a gate attempt) -- step 1: noise floor.

At a session-2 selected endpoint (fit 1: s4, fit 2: s6; read-only from fullplanck/tier2_rerun/chains/*.minimum,
10 significant digits), evaluate the posterior with cobaya (same yaml as session 2, read-only) at:
  - the point itself, 3 times (start, middle, end; cached=False) -> determinism / evaluation-order check;
  - for each relative size eps in (1e-6, 1e-4): 10 random sign vectors u (each component +-1, seeded),
    evaluated at x*(1 + eps*u) and x*(1 - eps*u)  -> 20 perturbations per size, all sampled params moved.
Reports per evaluation: -log post, total chi2 (plik-lite + DESI + Pantheon+), tau-prior term (2*minuslogprior__tau_prior),
and the scatter (std, max-min) of each relative to the centre, plus the symmetric-pair second difference
f(+)+f(-)-2f(0) and antisymmetric half-difference (f(+)-f(-))/2.
Usage: python noise_floor.py <fit1|fit2>
"""
import sys, os, time, copy, json
import numpy as np, yaml
from cobaya.model import get_model

RERUN = '/Users/420-420/ecf-md14/fullplanck/tier2_rerun'
OUT = '/Users/420-420/ecf-md14/fullplanck/tier2_explore'
FITS = {'fit1': ('fit1_lcdm_mnufixed', 4), 'fit2': ('fit2_ecf_mnufixed', 6)}
EPS = (1e-6, 1e-4)
NDIR = 10
SEED = {'fit1': 31001, 'fit2': 31002}


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


def main(which):
    fit, s = FITS[which]
    with open(os.path.join(RERUN, 'yamls', f'{fit}_s{s}.yaml')) as f:
        info = yaml.safe_load(f)
    info.pop('sampler'); info.pop('output')
    model = get_model(info)
    sampled = list(model.parameterization.sampled_params())
    mlp_file, vals = read_getdist_min(os.path.join(RERUN, 'chains', f'{fit}_s{s}.minimum'))
    x0 = np.array([vals[p] for p in sampled])
    print(f'# {which}: {fit}_s{s}; endpoint from {fit}_s{s}.minimum (-log post in file {mlp_file:.10f})')
    print('# sampled params:', sampled)
    print('# x0 =', json.dumps(dict(zip(sampled, x0.tolist()))))
    print(f'# OMP_NUM_THREADS={os.environ.get("OMP_NUM_THREADS")}')

    def ev(x, tag):
        t = time.time()
        r = model.logposterior(x, as_dict=True, cached=False)
        dt = time.time() - t
        mlp = -r['logpost']
        chi2 = -2 * sum(r['loglikes'].values())
        taut = -2 * r['logpriors']['tau_prior']
        print(f'{tag:28s} mlp={mlp:.6f} chi2={chi2:.6f} tauterm={taut:.6f} '
              + ' '.join(f'chi2_{k.split(".")[0][:6]}={-2*v:.6f}' for k, v in r['loglikes'].items())
              + f' dt={dt:.2f}s', flush=True)
        return mlp, chi2, taut

    rng = np.random.default_rng(SEED[which])
    res = {'centre': [ev(x0, 'centre#1')]}
    for k, eps in enumerate(EPS):
        rows = []
        for j in range(NDIR):
            u = rng.choice([-1.0, 1.0], size=len(x0))
            p = ev(x0 * (1 + eps * u), f'eps={eps:g} dir{j} +')
            m = ev(x0 * (1 - eps * u), f'eps={eps:g} dir{j} -')
            rows.append((p, m))
        res[eps] = rows
        res['centre'].append(ev(x0, f'centre#{k + 2}'))
    c = np.array(res['centre'])
    print('\n# SUMMARY', which)
    print(f'centre repeats (mlp, chi2, tauterm): ' + '; '.join(f'({a:.6f}, {b:.6f}, {t:.6f})' for a, b, t in c))
    print(f'centre repeat max-min: mlp {np.ptp(c[:, 0]):.2e}  chi2 {np.ptp(c[:, 1]):.2e}')
    f0 = c[0]
    for eps in EPS:
        rows = np.array(res[eps])  # (NDIR, 2, 3)
        allv = rows.reshape(-1, 3)
        d = allv - f0
        sec = rows[:, 0, :] + rows[:, 1, :] - 2 * f0
        asym = (rows[:, 0, :] - rows[:, 1, :]) / 2
        print(f'eps={eps:g}: 20 perturbations')
        print(f'   -log post  : std {np.std(d[:, 0]):.2e}  max-min {np.ptp(d[:, 0]):.2e}  max|f-f0| {np.max(np.abs(d[:, 0])):.2e}'
              f'  | 2nd diff mean {np.mean(sec[:, 0]):.2e} std {np.std(sec[:, 0]):.2e} | antisym std {np.std(asym[:, 0]):.2e}')
        print(f'   total chi2 : std {np.std(d[:, 1]):.2e}  max-min {np.ptp(d[:, 1]):.2e}  max|f-f0| {np.max(np.abs(d[:, 1])):.2e}'
              f'  | 2nd diff mean {np.mean(sec[:, 1]):.2e} std {np.std(sec[:, 1]):.2e} | antisym std {np.std(asym[:, 1]):.2e}')
        print(f'   tau term   : std {np.std(d[:, 2]):.2e}  max-min {np.ptp(d[:, 2]):.2e}')


if __name__ == '__main__':
    main(sys.argv[1])
