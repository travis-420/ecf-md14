"""EXPLORATORY minimizer study 2 (not a gate attempt). Markdown tables and summaries generated from logs only.

polish logs: logs/<tag>_<fit>_s<k>.log (polish2.py: ROUND0/ROUND/CRASH/STOP/DEADLINE lines + launcher EXIT line)
base logs:   logs/base_<fit>_s<k>.json (base_run.py) + logs/base_<fit>_s<k>.log (EXIT line)
Usage: python tables2.py polish <tag> <round0-label> <fit,fit,...>
       python tables2.py base <fit,fit,...>
Cell = -log post / total chi2 / tau-prior term (2*minuslogprior__tau_prior) after that round.
'=' start had already stopped (stop rule) -> value carried forward; '!' start failed (crash) in or before this round
-> value is NOT a result of the procedure and is excluded; '...' still running.
A start 'produces a result' if it ended on the stop rule or the 5-round cap (not on a crash, not on a deadline).
Window (AMENDMENT_TIER2_MINIMIZER.md section 2.4, applied for reporting only): -log post within 0.25 of the best.
"""
import sys, os, json, re
import numpy as np

EXP2 = '/Users/420-420/ecf-md14/fullplanck/tier2_explore2'
NAMES = {'fit1_lcdm_mnufixed': 'Fit 1 (ΛCDM, Σmν = 0.06 eV fixed)', 'fit2_ecf_mnufixed': 'Fit 2 (ECF, Σmν = 0.06 eV fixed)',
         'cpl_mnufixed': 'CPL, Σmν = 0.06 eV FIXED (cpl_full.yaml as shipped; not fit 5)'}


def parse_polish(tag, fit, k):
    p = os.path.join(EXP2, 'logs', f'{tag}_{fit}_s{k}.log')
    recs, crash, status, ex = {}, None, 'running', None
    if not os.path.exists(p):
        return recs, crash, 'not started', ex
    for ln in open(p):
        if ln.startswith('ROUND0 '):
            recs[0] = json.loads(ln[7:])
        elif ln.startswith('ROUND '):
            r = json.loads(ln[6:]); recs[r['round']] = r
        elif ln.startswith('CRASH '):
            crash = json.loads(ln[6:])
        elif ln.startswith('STOP') or ln.startswith('DEADLINE'):
            status = ln.strip()
        elif ln.startswith('EXIT='):
            ex = ln.strip()
    if crash is not None:
        status = 'CRASH'
    elif status == 'running' and ex is not None:
        status = 'operator-stopped during a round (' + ex.split()[0] + '); no result for that round'
    return recs, crash, status, ex


def wall_minutes(ex):
    m = re.search(r'start=(\S+) end=(\S+)', ex or '')
    if not m:
        return None
    from datetime import datetime
    f = lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    return (f(m.group(2)) - f(m.group(1))).total_seconds() / 60


def polish_tables(tag, r0label, fits):
    out = []
    for fit in fits:
        data = {k: parse_polish(tag, fit, k) for k in range(8)}
        maxr = max([max(d[0]) if d[0] else 0 for d in data.values()] + [0])
        maxr_show = maxr + (1 if any(d[1] is not None and d[1]['round'] == maxr + 1 for d in data.values()) else 0)
        out.append(f'\n**{tag}, {NAMES[fit]}.** Cell = −log post / total χ² / τ-prior term.\n')
        out.append('| start | ' + ' | '.join([f'round 0 ({r0label})'] + [f'round {r}' for r in range(1, maxr_show + 1)])
                   + ' | outcome | evals | min |')
        out.append('|' + '---|' * (maxr_show + 5))
        per_round = {r: [] for r in range(maxr_show + 1)}
        final = []
        for k in range(8):
            recs, crash, status, ex = data[k]
            last = max(recs) if recs else None
            cells = []
            for r in range(maxr_show + 1):
                if r in recs:
                    x = recs[r]; cells.append(f'{x["mlp"]:.5f} / {x["chi2"]:.4f} / {x["tauterm"]:.4f}' if r else
                                              f'{x["mlp"]:.5f}' + (f' / {x["chi2"]:.4f} / {x["tauterm"]:.4f}' if 'chi2' in x else ''))
                    per_round[r].append((k, x, True))
                elif crash is not None:
                    cells.append('!'); per_round[r].append((k, recs.get(last), False))
                elif status in ('running', 'not started') or status.startswith('operator-stopped'):
                    cells.append('...'); per_round[r].append((k, None, False))
                else:
                    cells.append('='); per_round[r].append((k, recs[last], True))
            if crash is not None:
                oc = (f'**failed in round {crash["round"]}** at evaluation {crash.get("nf")}: '
                      f'{(crash.get("msg") or crash.get("error") or "")[:70]}')
            elif status.startswith('STOP: round'):
                g = re.search(r'round (\d+) improved -log post by (\S+)', status)
                oc = f'round {g.group(1)} gain {float(g.group(2)):.6f} < 0.001 → stop'
            elif status.startswith('STOP: reached'):
                oc = '5-round cap'
            elif status.startswith('DEADLINE'):
                oc = 'deadline: next round not started'
            else:
                oc = status
            nfs = [recs[r].get('nf') or 0 for r in recs if r > 0] + ([crash.get('nf') or 0] if crash else [])
            wm = wall_minutes(ex)
            out.append(f'| s{k} | ' + ' | '.join(cells) + f' | {oc} | {sum(nfs)} | ' + (f'{wm:.1f}' if wm is not None else '…') + ' |')
            produced = crash is None and (status.startswith('STOP'))
            final.append((k, recs.get(last) if last is not None else None, produced, crash, sum(nfs), wm))
        rows = {'n': [], 'sp': [], 'S': [], 'sel': [], 'ev': []}
        for r in range(maxr_show + 1):
            ok = [x for x in per_round[r] if x[1] is not None and x[2] and 'chi2' in x[1]]
            rows['n'].append(f'{len(ok)}/8')
            if len(ok) >= 2:
                m = np.array([x[1]['mlp'] for x in ok]); c = np.array([x[1]['chi2'] for x in ok]); ib = int(np.argmin(m))
                rows['sp'].append(f'{np.ptp(m):.5f}'); rows['S'].append(f'**{np.ptp(c):.4f}**'); rows['sel'].append(f's{ok[ib][0]}: {c[ib]:.4f}')
            else:
                rows['sp'].append('n/a'); rows['S'].append('n/a'); rows['sel'].append('n/a')
            ev = [x[1].get('nf') or 0 for x in per_round[r] if x[1] is not None and x[2] and x[1].get('round') == r and r > 0]
            evc = [d[1].get('nf') or 0 for d in data.values() if d[1] is not None and d[1]['round'] == r]
            rows['ev'].append('—' if r == 0 else f'{sum(ev) + sum(evc)} ({len(ev) + len(evc)} starts ran it'
                              + (f', {len(evc)} failed' if evc else '') + ')')
        out.append('| starts entering spread and S (completed, not failed) | ' + ' | '.join(rows['n']) + ' | | | |')
        out.append('| spread of −log post (max − min) | ' + ' | '.join(rows['sp']) + ' | | | |')
        out.append('| **S** = max − min total χ² | ' + ' | '.join(rows['S']) + ' | | | |')
        out.append('| lowest −log post start: its total χ² | ' + ' | '.join(rows['sel']) + ' | | | |')
        out.append('| evaluations in this round | ' + ' | '.join(rows['ev']) + ' | | | |')
        # final-state summary
        prod = [f for f in final if f[2] and f[1] is not None]
        ncrash = sum(1 for f in final if f[3] is not None)
        nrun = sum(1 for f in final if not f[2] and f[3] is None)
        tot_ev = sum(f[4] for f in final); wms = [f[5] for f in final if f[5] is not None]
        line = (f'SUMMARY {tag} {fit}: starts failed (crash) {ncrash}/8; starts producing a result {len(prod)}/8; '
                f'still running/not finished {nrun}; evaluations total {tot_ev}, per start '
                f'{min(f[4] for f in final)}–{max(f[4] for f in final)}; wall per start (min) '
                + (f'{min(wms):.1f}–{max(wms):.1f}' if wms else 'n/a'))
        if len(prod) >= 2:
            m = np.array([f[1]['mlp'] for f in prod]); c = np.array([f[1]['chi2'] for f in prod])
            best = m.min(); inw = [f for f in prod if f[1]['mlp'] - best <= 0.25]
            ci = np.array([f[1]['chi2'] for f in inw]); ib = int(np.argmin(m))
            line += (f'; final −log post spread {np.ptp(m):.5f}; S (all result starts) {np.ptp(c):.4f}; '
                     f'in window (≤0.25) {len(inw)}/8, S in window {np.ptp(ci):.4f}; lowest −log post s{prod[ib][0]} '
                     f'{m[ib]:.5f} with total χ² {c[ib]:.4f}; total χ² range {c.min():.4f}–{c.max():.4f}')
        out.append('\n' + line)
    return '\n'.join(out)


def base_table(fits):
    out = []
    for fit in fits:
        out.append(f'\n**base, {NAMES[fit]}.** AMENDMENT_TIER2_MINIMIZER.md §2 settings, seeds 9000+k.\n')
        out.append('| start | start point | status | −log post | −log post − best | total χ² | χ²_CMB | χ²_BAO | χ²_SN | τ-prior term | extra | evals | min |')
        out.append('|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|')
        R = []
        for k in range(8):
            p = os.path.join(EXP2, 'logs', f'base_{fit}_s{k}.json')
            ex = None
            lp = os.path.join(EXP2, 'logs', f'base_{fit}_s{k}.log')
            if os.path.exists(lp):
                for ln in open(lp):
                    if ln.startswith('EXIT='):
                        ex = ln.strip()
            R.append((k, json.load(open(p)) if os.path.exists(p) else None, ex))
        conv = [r for r in R if r[1] and r[1]['status'] == 'converged']
        best = min(r[1]['mlp'] for r in conv) if conv else None
        for k, b, ex in R:
            sp = 'certified July best fit (seed 9000, inert)' if k == 0 else f'random, seed {9000 + k}'
            wm = wall_minutes(ex)
            if b is None:
                out.append(f'| s{k} | {sp} | running | | | | | | | | | | |'); continue
            if b['status'] != 'converged':
                out.append(f'| s{k} | {sp} | **{b["status"]}**: {b.get("msg")} | | | | | | | | | {b.get("nf")} | '
                           + (f'{wm:.1f}' if wm else '') + ' |'); continue
            extra = ', '.join(f'{p} {b["x"][p]:.5f}' for p in ('tau_ecf', 'w', 'wa') if p in b['x'])
            out.append(f'| s{k} | {sp} | converged | {b["mlp"]:.4f} | {b["mlp"] - best:.4f} | {b["chi2"]:.4f} | '
                       f'{b["chi2_cmb"]:.4f} | {b["chi2_bao"]:.4f} | {b["chi2_sn"]:.4f} | {b["tauterm"]:.4f} | {extra} | '
                       f'{b["nf"]} | ' + (f'{wm:.1f}' if wm else '') + ' |')
        if len(conv) >= 2:
            m = np.array([r[1]['mlp'] for r in conv]); c = np.array([r[1]['chi2'] for r in conv])
            inw = [r for r in conv if r[1]['mlp'] - best <= 0.25]; ci = np.array([r[1]['chi2'] for r in inw])
            ib = int(np.argmin(m))
            out.append(f'\nSUMMARY base {fit}: converged {len(conv)}/8; in window (≤0.25) {len(inw)}/8; '
                       f'−log post spread {np.ptp(m):.5f}; S in window {np.ptp(ci):.4f}; S all converged {np.ptp(c):.4f}; '
                       f'lowest −log post s{conv[ib][0]} {m[ib]:.5f}, total χ² {c[ib]:.4f}; evaluations '
                       f'{sum(r[1]["nf"] for r in conv)} total, {min(r[1]["nf"] for r in conv)}–{max(r[1]["nf"] for r in conv)} per start')
    return '\n'.join(out)


def summary_rows(tags, fits):
    out = ['| candidate | fit | starts with a failed round | starts producing a result | no result: deadline / stopped / running | '
           '−log post spread (final) | **S** (final, starts with a result) | in window (≤0.25) | evaluations: total (per start) | wall min per start |',
           '|---|---|---:|---:|---:|---:|---:|---:|---|---|']
    for tag in tags:
        for fit in fits:
            fin = []
            for k in range(8):
                recs, crash, status, ex = parse_polish(tag, fit, k)
                last = max(recs) if recs else None
                nfs = [recs[r].get('nf') or 0 for r in recs if r > 0] + ([crash.get('nf') or 0] if crash else [])
                fin.append((recs.get(last), crash is not None, status.startswith('STOP'), sum(nfs), wall_minutes(ex)))
            prod = [f for f in fin if f[2] and not f[1] and f[0] is not None]
            run = sum(1 for f in fin if not f[1] and not f[2])
            wm = [f[4] for f in fin if f[4] is not None]
            if len(prod) >= 2:
                m = np.array([f[0]['mlp'] for f in prod]); c = np.array([f[0]['chi2'] for f in prod])
                inw = sum(1 for f in prod if f[0]['mlp'] - m.min() <= 0.25)
                sp, S, iw = f'{np.ptp(m):.5f}', f'**{np.ptp(c):.4f}**', f'{inw}/8'
            else:
                sp = S = iw = 'n/a'
            out.append(f'| {tag} | {fit.split("_")[0]} | {sum(f[1] for f in fin)}/8 | {len(prod)}/8 | {run} | {sp} | {S} | {iw} | '
                       f'{sum(f[3] for f in fin)} ({min(f[3] for f in fin)}–{max(f[3] for f in fin)}) | '
                       + (f'{min(wm):.1f}–{max(wm):.1f}' if wm else 'n/a') + ' |')
    return '\n'.join(out)


if __name__ == '__main__':
    if sys.argv[1] == 'summary':
        print(summary_rows(sys.argv[2].split(','), sys.argv[3].split(',')))
    elif sys.argv[1] == 'polish':
        print(polish_tables(sys.argv[2], sys.argv[3], sys.argv[4].split(',')))
    else:
        print(base_table(sys.argv[2].split(',')))
