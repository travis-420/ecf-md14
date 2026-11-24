"""EXPLORATORY minimizer study (not a gate attempt) -- markdown round-by-round tables from polish.py logs.
Usage: python make_tables.py <tag> [<tag> ...]
Cell = -log post / total chi2 / tau-prior term (2*minuslogprior__tau_prior) after that round.
'=' : start had already stopped (stop rule) -> value carried forward; '!' : start crashed before/in this round ->
value is its last completed round and is NOT a result of the procedure; '...' : round still running (no value yet).
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summarize import load, CERT, CERT_DCHI2

NAMES = {'fit1_lcdm_mnufixed': 'Fit 1 (ΛCDM, Σmν = 0.06 eV fixed)', 'fit2_ecf_mnufixed': 'Fit 2 (ECF, Σmν = 0.06 eV fixed)'}


def table(tag):
    data = load(tag)
    out = []
    best_by_round = {}
    for fit in CERT:
        maxr = max(max(data[(fit, k)][0]) for k in range(8))
        out.append(f'\n**{tag}, {NAMES[fit]}.** Cell = −log post / total χ² / τ-prior term.\n')
        hdr = '| start | ' + ' | '.join(['round 0 (session-2 endpoint)'] + [f'round {r}' for r in range(1, maxr + 1)]) + ' | outcome |'
        out.append(hdr)
        out.append('|' + '---|' * (maxr + 3))
        per_round = {r: [] for r in range(maxr + 1)}
        for k in range(8):
            recs, status, ex = data[(fit, k)]
            crashed = status.startswith('CRASHED')
            last = max(recs)
            cells = []
            for r in range(maxr + 1):
                if r in recs:
                    rec = recs[r]; cells.append(f'{rec["mlp"]:.5f} / {rec["chi2"]:.4f} / {rec["tauterm"]:.4f}')
                    per_round[r].append((k, rec, True))
                else:
                    rec = recs[last]
                    if crashed:
                        cells.append('!'); per_round[r].append((k, rec, False))
                    elif status == 'running':
                        cells.append('...'); per_round[r].append((k, None, False))
                    else:
                        cells.append('='); per_round[r].append((k, rec, True))
            if crashed:
                oc = f'crashed in round {last + 1} (Py-BOBYQA linear-algebra error)'
            elif status.startswith('STOP'):
                oc = status.replace('STOP: ', '').replace('improved -log post by', 'gain').replace(' < 0.001', ' < 0.001 → stop')
            elif status.startswith('DEADLINE'):
                oc = 'deadline: next round not started'
            else:
                oc = 'still running'
            out.append(f'| s{k} | ' + ' | '.join(cells) + f' | {oc} |')
        # summary rows
        rows_sp, rows_S, rows_n, rows_ev, rows_sel = [], [], [], [], []
        for r in range(maxr + 1):
            ok = [x for x in per_round[r] if x[1] is not None and x[2]]
            allv = [x for x in per_round[r] if x[1] is not None]
            if len(ok) < 2:
                rows_sp.append('n/a'); rows_S.append('n/a'); rows_n.append(f'{len(ok)}/8'); rows_sel.append('n/a')
            else:
                m = np.array([x[1]['mlp'] for x in ok]); c = np.array([x[1]['chi2'] for x in ok])
                rows_sp.append(f'{np.ptp(m):.5f}'); rows_S.append(f'**{np.ptp(c):.4f}**'); rows_n.append(f'{len(ok)}/8')
                ib = int(np.argmin(m)); rows_sel.append(f's{ok[ib][0]}: {c[ib]:.4f}')
                best_by_round.setdefault(fit, {})[r] = (ok[ib][0], m[ib], c[ib], len(ok), np.ptp(c), c.min(), c.max())
            ev = [x[1].get('nf', 0) for x in per_round[r] if x[1] is not None and x[1].get('round') == r and r > 0]
            rows_ev.append(f'{sum(ev)} ({len(ev)} starts ran it)' if r > 0 else '—')
        out.append('| starts entering spread and S (completed, not crashed) | ' + ' | '.join(rows_n) + ' | |')
        out.append('| spread of −log post (max − min) | ' + ' | '.join(rows_sp) + ' | |')
        out.append('| **S** = max − min total χ² | ' + ' | '.join(rows_S) + ' | |')
        out.append('| lowest −log post start: its total χ² | ' + ' | '.join(rows_sel) + ' | |')
        out.append('| evaluations in this round (Py-BOBYQA nf) | ' + ' | '.join(rows_ev) + ' | |')
    return '\n'.join(out), best_by_round


if __name__ == '__main__':
    for tag in sys.argv[1:]:
        t, b = table(tag)
        print(t)
        f1, f2 = b.get('fit1_lcdm_mnufixed', {}), b.get('fit2_ecf_mnufixed', {})
        print(f'\n{tag} vs certified (reporting only, no G1 verdict):')
        for r in sorted(set(f1) & set(f2)):
            a, c = f1[r], f2[r]
            print(f'  round {r}: fit1 lowest-mlp s{a[0]} mlp {a[1]:.5f} ({a[1] - CERT["fit1_lcdm_mnufixed"]["mlp"]:+.5f} vs July) chi2 {a[2]:.4f} '
                  f'({a[2] - CERT["fit1_lcdm_mnufixed"]["chi2"]:+.4f}), range {a[5]:.4f}..{a[6]:.4f} over {a[3]} starts; '
                  f'fit2 lowest-mlp s{c[0]} mlp {c[1]:.5f} ({c[1] - CERT["fit2_ecf_mnufixed"]["mlp"]:+.5f}) chi2 {c[2]:.4f} '
                  f'({c[2] - CERT["fit2_ecf_mnufixed"]["chi2"]:+.4f}), range {c[5]:.4f}..{c[6]:.4f} over {c[3]} starts; '
                  f'dchi2 = {c[2] - a[2]:.4f} ({c[2] - a[2] - CERT_DCHI2:+.4f} vs {CERT_DCHI2})')
