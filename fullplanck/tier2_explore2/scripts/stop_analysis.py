"""EXPLORATORY minimizer study 2 (not a gate attempt). For each candidate/fit: starts that ended on the 0.001 stop rule
-- their last-round gain and how far their final -log post is above the fit's best final -log post (from logs only)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tables2 import parse_polish
for tag, fits in [('c1', 'fit1_lcdm_mnufixed,fit2_ecf_mnufixed'), ('c2', 'fit1_lcdm_mnufixed,fit2_ecf_mnufixed'),
                  ('c4', 'fit1_lcdm_mnufixed,fit2_ecf_mnufixed'), ('e2e', 'fit1_lcdm_mnufixed,fit2_ecf_mnufixed'),
                  ('cpl', 'cpl_mnufixed')]:
    for fit in fits.split(','):
        F = [parse_polish(tag, fit, k) for k in range(8)]
        fin = [(k, f[0][max(f[0])]) for k, f in enumerate(F) if f[2].startswith('STOP')]
        best = min(r['mlp'] for k, r in fin)
        rule = [(k, r['improvement'], r['mlp'] - best) for (k, r), f in zip(fin, [F[k] for k, _ in fin]) if 'improved' in f[2]]
        cap = [(k, r['improvement'], r['mlp'] - best) for (k, r), f in zip(fin, [F[k] for k, _ in fin]) if 'reached' in f[2]]
        g = [x[1] for x in rule]; d = [x[2] for x in rule]
        print(f'{tag} {fit}: best {best:.5f}; stop-rule starts {len(rule)}: last gain {min(g):.6f}-{max(g):.6f}, '
              f'above best {min(d):.5f}-{max(d):.5f}; cap starts {[(k, round(gn, 5), round(dd, 5)) for k, gn, dd in cap]}; '
              f'per start above best: {[(k, round(dd, 5)) for k, _, dd in sorted(rule + cap)]}')
