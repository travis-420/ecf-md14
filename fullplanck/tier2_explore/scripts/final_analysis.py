"""EXPLORATORY minimizer study (not a gate attempt) -- final per-procedure summary (reporting only, no G1 verdict).
Usage: python final_analysis.py step2 step3A step3B
For each procedure and fit: each start's LAST COMPLETED round (a crashed round has no result); starts with no completed
round of the procedure (crashed in round 1) are listed as 'no result'. Spread and S over starts with >= 1 completed round.
Also: the lowest -log posterior found anywhere in this study for each fit, and comparisons with the certified values.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summarize import load, CERT, CERT_DCHI2

best_any = {}
for tag in sys.argv[1:]:
    data = load(tag)
    print(f'\n######## {tag}')
    res = {}
    for fit in CERT:
        rows = []
        for k in range(8):
            recs, status, ex = data[(fit, k)]
            done = [r for r in recs if r > 0]
            crashed = status.startswith('CRASHED')
            if not done:
                print(f'{fit} s{k}: no completed round ({status})'); continue
            r = max(done); rec = recs[r]
            rows.append((k, r, rec, crashed))
            print(f'{fit} s{k}: last completed round {r}: mlp {rec["mlp"]:.5f} chi2 {rec["chi2"]:.4f} tau {rec["tauterm"]:.4f}'
                  f' ({"later round crashed" if crashed else status})')
            for rr in done:
                b = best_any.get(fit)
                if b is None or recs[rr]['mlp'] < b[0]:
                    best_any[fit] = (recs[rr]['mlp'], recs[rr]['chi2'], recs[rr]['tauterm'], tag, k, rr)
        if len(rows) >= 2:
            m = np.array([x[2]['mlp'] for x in rows]); c = np.array([x[2]['chi2'] for x in rows])
            ib = int(np.argmin(m))
            res[fit] = (rows[ib][0], m[ib], c[ib])
            print(f'{fit}: starts with a result {len(rows)}/8; spread(-log post) {np.ptp(m):.5f}; S {np.ptp(c):.4f} '
                  f'(chi2 {c.min():.4f}..{c.max():.4f}); lowest mlp s{rows[ib][0]} {m[ib]:.5f} ({m[ib] - CERT[fit]["mlp"]:+.5f} vs July) '
                  f'chi2 {c[ib]:.4f} ({c[ib] - CERT[fit]["chi2"]:+.4f} vs certified {CERT[fit]["chi2"]})')
    if len(res) == 2:
        a, b = res['fit1_lcdm_mnufixed'], res['fit2_ecf_mnufixed']
        print(f'{tag}: dchi2 at lowest-mlp starts = {b[2] - a[2]:.4f} ({b[2] - a[2] - CERT_DCHI2:+.4f} vs certified {CERT_DCHI2})')

print('\n######## lowest -log posterior found anywhere in this study (any procedure, any completed round)')
for fit, (m, c, t, tag, k, r) in best_any.items():
    print(f'{fit}: mlp {m:.5f} ({m - CERT[fit]["mlp"]:+.5f} vs July {CERT[fit]["mlp"]}) at {tag} s{k} round {r}; total chi2 {c:.4f} '
          f'({c - CERT[fit]["chi2"]:+.4f} vs certified {CERT[fit]["chi2"]}); tau-prior term {t:.4f}')
if len(best_any) == 2:
    d = best_any['fit2_ecf_mnufixed'][1] - best_any['fit1_lcdm_mnufixed'][1]
    print(f'dchi2 between these two points = {d:.4f} ({d - CERT_DCHI2:+.4f} vs certified {CERT_DCHI2})')
