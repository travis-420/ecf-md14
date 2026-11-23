"""Collect per-start minimizer results for given fits; prints every start and the best (lowest minuslogpost)."""
import sys, glob, re, os
T2 = '/Users/420-420/ecf-md14/fullplanck/tier2'
KEYS = ['minuslogpost', 'chi2', 'chi2__planck_2018_highl_plik.TTTEEE_lite_native', 'chi2__bao.desi_dr2',
        'chi2__sn.pantheonplus', 'minuslogprior', 'H0', 'omch2', 'ombh2', 'ns', 'logA', 'tau', 'A_planck',
        'tau_ecf', 'mnu', 'w', 'wa']
SHORT = {'chi2__planck_2018_highl_plik.TTTEEE_lite_native': 'chi2_CMB', 'chi2__bao.desi_dr2': 'chi2_BAO',
         'chi2__sn.pantheonplus': 'chi2_SN'}
def read_min(path):
    with open(path) as f:
        hdr = f.readline().lstrip('#').split(); vals = [float(v) for v in f.readline().split()]
    return dict(zip(hdr, vals))
out = {}
for fit in sys.argv[1].split(','):
    rows = []
    for p in sorted(glob.glob(f'{T2}/chains/{fit}_s*.minimum.txt')):
        s = re.search(r'_s(\d+)\.minimum\.txt$', p).group(1)
        log = open(f'{T2}/logs/{fit}_s{s}.log').read()
        ok = 'Run 1/1 converged.' in log and 'EXIT=0' in log
        d = read_min(p); d['start'] = int(s); d['converged'] = ok
        rows.append(d)
    rows.sort(key=lambda d: d['start'])
    print(f'\n### {fit}: {len(rows)} starts')
    cols = [k for k in KEYS if k in rows[0]]
    print('start | converged | ' + ' | '.join(SHORT.get(c, c) for c in cols))
    for d in rows:
        print(f"s{d['start']} | {d['converged']} | " + ' | '.join(f'{d[c]:.6g}' if abs(d[c]) < 1e-2 or c in ('ombh2',) else f'{d[c]:.4f}' for c in cols))
    best = min(rows, key=lambda d: d['minuslogpost'])
    print(f"BEST: s{best['start']}  minuslogpost={best['minuslogpost']:.4f}  chi2={best['chi2']:.4f}"
          + ''.join(f"  {k}={best[k]:.4f}" for k in ('tau_ecf', 'mnu', 'w', 'wa', 'H0') if k in best))
    spread = max(d['chi2'] for d in rows) - min(d['chi2'] for d in rows)
    print(f'chi2 spread across starts (max-min) = {spread:.4f}')
    out[fit] = best
