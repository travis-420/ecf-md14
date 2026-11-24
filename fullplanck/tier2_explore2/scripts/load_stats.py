"""EXPLORATORY minimizer study 2 (not a gate attempt). Wall seconds per likelihood evaluation, from logs only
(polish rounds: wall_s / nf of each completed round; base runs: wall_s / nf). Reported as min / median / max."""
import glob, json, numpy as np, os, re
E = '/Users/420-420/ecf-md14/fullplanck/tier2_explore2/logs'
def stats(v): v = np.array(v); return f'n={len(v)} min {v.min():.1f} median {np.median(v):.1f} max {v.max():.1f} s/eval'
for tag in ('c1', 'c2', 'c3', 'c4', 'e2e', 'cpl'):
    v = []
    for p in glob.glob(f'{E}/{tag}_*.log'):
        for ln in open(p):
            if ln.startswith('ROUND '):
                r = json.loads(ln[6:])
                if r.get('nf'): v.append(r['wall_s'] / r['nf'])
    if v: print(f'{tag:4s} polish rounds: {stats(v)}')
v = [json.load(open(p)) for p in glob.glob(f'{E}/base_*.json')]
v = [b['wall_s'] / b['nf'] for b in v if b.get('nf')]
if v: print(f'base runs: {stats(v)}')
d = json.load(open(f'{E}/diag_D1_repro.json')); print(f'step-1 D1 (3 processes running): {stats([e["dt"] for e in d["evals"]])} (per evaluation)')
