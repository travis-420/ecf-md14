"""EXPLORATORY minimizer study 2 (not a gate attempt). Per-start cost of base minimization + polish (from logs only).
Usage: python cost_e2e.py <tag> <fit,fit,...>"""
import sys, json, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tables2 import parse_polish, wall_minutes
E = '/Users/420-420/ecf-md14/fullplanck/tier2_explore2/logs'
tag = sys.argv[1]
for fit in sys.argv[2].split(','):
    rows = []
    for k in range(8):
        b = json.load(open(f'{E}/base_{fit}_s{k}.json'))
        recs, crash, status, ex = parse_polish(tag, fit, k)
        pnf = sum(recs[r].get('nf') or 0 for r in recs if r > 0) + ((crash.get('nf') or 0) if crash else 0)
        nr = max([r for r in recs if r > 0] or [0])
        pw = wall_minutes(ex)
        rows.append((k, b['nf'], b['wall_s'] / 60, pnf, nr, pw, status))
    for k, bn, bw, pn, nr, pw, st in rows:
        print(f'{tag} {fit} s{k}: base {bn} evals {bw:.1f} min; polish {pn} evals in {nr} rounds '
              + (f'{pw:.1f} min' if pw is not None else 'running') + f'; total {bn + pn} evals; status {st[:40]}')
    tot = [r[1] + r[3] for r in rows]
    print(f'{tag} {fit} TOTAL: base {sum(r[1] for r in rows)} + polish {sum(r[3] for r in rows)} = {sum(tot)} evals; '
          f'per start {min(tot)}-{max(tot)}; polish rounds per start {min(r[4] for r in rows)}-{max(r[4] for r in rows)}; '
          f'polish evals per start {min(r[3] for r in rows)}-{max(r[3] for r in rows)}')
