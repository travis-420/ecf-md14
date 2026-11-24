"""EXPLORATORY minimizer study (not a gate attempt) -- round-by-round summary from polish.py logs.

Usage: python summarize.py <tag>
Round 0 = session-2 endpoint (values from fullplanck/tier2_rerun/chains/<fit>_s<k>.minimum.txt, read-only),
unless the tag's ROUND0 records came from a start_json (then round 0 = that json's values).
A start that stopped (stop rule, or deadline) carries its last value forward into later rounds (marked '=').
Per round and fit: each start's -log post, total chi2, tau-prior term (2*minuslogprior__tau_prior);
spread of -log post (max-min over all 8); S = max-min total chi2 over all 8; also the 0.25-window count and
in-window S (session-2 definitions, reporting only); evaluations and wall time of that round.
"""
import sys, os, json, glob
import numpy as np

EXP = '/Users/420-420/ecf-md14/fullplanck/tier2_explore'
RERUN = '/Users/420-420/ecf-md14/fullplanck/tier2_rerun'
CERT = {'fit1_lcdm_mnufixed': {'chi2': 2005.5316, 'mlp': 986.0217},
        'fit2_ecf_mnufixed': {'chi2': 1993.8933, 'mlp': 981.93936}}
CERT_DCHI2 = -11.6383


def read_mintxt(path):
    with open(path) as f:
        h = f.readline().lstrip('#').split(); v = [float(x) for x in f.readline().split()]
    return dict(zip(h, v))


def load(tag):
    data = {}
    for fit in CERT:
        for k in range(8):
            fn = os.path.join(EXP, 'logs', f'{tag}_{fit}_s{k}.log')
            recs, status, exitline, errline = {}, 'running', '', ''
            if os.path.exists(fn):
                for ln in open(fn):
                    if ln.startswith('ROUND0 '):
                        r0 = json.loads(ln[7:])
                        if r0['source'].endswith('.minimum'):
                            m = read_mintxt(os.path.join(RERUN, 'chains', f'{fit}_s{k}.minimum.txt'))
                            r0.update(chi2=m['chi2'], tauterm=2 * m['minuslogprior__tau_prior'],
                                      chi2_cmb=m['chi2__planck_2018_highl_plik.TTTEEE_lite_native'],
                                      chi2_bao=m['chi2__bao.desi_dr2'], chi2_sn=m['chi2__sn.pantheonplus'])
                        recs[0] = r0
                    elif ln.startswith('ROUND '):
                        r = json.loads(ln[6:]); recs[r['round']] = r
                    elif ln.startswith('STOP') or ln.startswith('DEADLINE'):
                        status = ln.strip()
                    elif ln.startswith('EXIT='):
                        exitline = ln.strip()
                    elif 'Error (linear algebra)' in ln or 'LoggedError' in ln:
                        errline = ln.strip()
            if exitline and not exitline.startswith('EXIT=0'):
                status = f'CRASHED during round {max(recs) + 1 if recs else 1} ({errline[:90]})'
            data[(fit, k)] = (recs, status, exitline)
    return data


def main(tag):
    data = load(tag)
    maxr = max((max(v[0]) if v[0] else 0) for v in data.values())
    sel = {}
    for fit in CERT:
        print(f'\n===== {tag} {fit} =====')
        for k in range(8):
            recs, status, ex = data[(fit, k)]
            done = [r for r in recs if r > 0]
            print(f's{k}: rounds run {len(done)}; ' + (status or 'running') + (f'; {ex}' if ex else ''))
        for r in range(0, maxr + 1):
            rows = []
            for k in range(8):
                recs, status, ex = data[(fit, k)]
                if not recs:
                    continue
                rr = max(x for x in recs if x <= r)
                rec = recs[rr]
                fresh = rr == r
                rows.append((k, rec, fresh))
            if len(rows) < 8:
                print(f'-- round {r}: only {len(rows)} starts have data'); continue
            mlps = np.array([x[1]['mlp'] for x in rows]); chi2s = np.array([x[1]['chi2'] for x in rows])
            best = mlps.min(); inw = mlps - best <= 0.25
            ib = int(np.argmin(mlps))
            pending = [k for k in range(8) if data[(fit, k)][1] == 'running' and max(data[(fit, k)][0]) < r]
            print(f'-- round {r}' + (f'  (still running for starts {pending}; their round-{r} values not yet available)' if pending else ''))
            print('   start |    -log post | -logpost-best |     total chi2 |  tau-prior term |  chi2_CMB  chi2_BAO  chi2_SN | nf  wall_s  conv')
            for k, rec, fresh in rows:
                crashed = data[(fit, k)][1].startswith('CRASHED') and r > max(data[(fit, k)][0])
                mark = '!' if crashed else (' ' if fresh else '=')
                extra = (f"| {rec.get('nf', ''):>4} {rec.get('wall_s', 0):7.0f}  {rec.get('converged_cobaya', '')}"
                         if fresh and r > 0 else '|')
                print(f'   s{k}{mark}   | {rec["mlp"]:12.5f} | {rec["mlp"] - best:13.5f} | {rec["chi2"]:14.4f} | {rec["tauterm"]:15.4f} | '
                      f'{rec["chi2_cmb"]:9.4f} {rec["chi2_bao"]:8.4f} {rec["chi2_sn"]:10.4f} {extra}')
            okm = np.array([not (data[(fit, k)][1].startswith('CRASHED') and r > max(data[(fit, k)][0])) for k, _, _ in rows])
            if not okm.all():
                print(f'   ! = start crashed in an earlier-or-this round; value shown is its last completed round (NOT a result of this procedure).'
                      f' Over the {okm.sum()} non-crashed starts: spread(-log post) = {np.ptp(mlps[okm]):.5f}, S = {np.ptp(chi2s[okm]):.4f}')
            print(f'   spread(-log post, all 8) = {np.ptp(mlps):.5f};  S (total chi2 max-min, all 8) = {np.ptp(chi2s):.4f};'
                  f'  in 0.25 window: {inw.sum()}/8, in-window S = {np.ptp(chi2s[inw]):.4f}')
            print(f'   lowest -log post: s{rows[ib][0]} {mlps[ib]:.5f} (vs July {CERT[fit]["mlp"]}: {mlps[ib] - CERT[fit]["mlp"]:+.5f});'
                  f' its total chi2 {chi2s[ib]:.4f} (vs certified {CERT[fit]["chi2"]}: {chi2s[ib] - CERT[fit]["chi2"]:+.4f});'
                  f' mean chi2 over 8 = {chi2s.mean():.4f} ({chi2s.mean() - CERT[fit]["chi2"]:+.4f}); median {np.median(chi2s):.4f}')
            fresh_runs = [rec for k, rec, fresh in rows if fresh and r > 0]
            if fresh_runs:
                nfs = [x.get('nf', 0) for x in fresh_runs]; ws = [x.get('wall_s', 0) for x in fresh_runs]
                print(f'   round {r} cost over the {len(fresh_runs)} starts that ran it: evaluations (pybobyqa nf) total {sum(nfs)}, '
                      f'per start min/median/max {min(nfs)}/{int(np.median(nfs))}/{max(nfs)}; wall per start min/median/max '
                      f'{min(ws) / 60:.1f}/{np.median(ws) / 60:.1f}/{max(ws) / 60:.1f} min')
            sel.setdefault(fit, {})[r] = (rows[ib][0], mlps[ib], chi2s[ib], np.ptp(chi2s), chi2s.mean())
    print('\n===== cross-fit (lowest -log post start of each fit; reporting only, no gate) =====')
    for r in sorted(set(sel.get('fit1_lcdm_mnufixed', {})) & set(sel.get('fit2_ecf_mnufixed', {}))):
        a = sel['fit1_lcdm_mnufixed'][r]; b = sel['fit2_ecf_mnufixed'][r]
        print(f'round {r}: chi2(fit2)-chi2(fit1) = {b[2] - a[2]:.4f} (certified {CERT_DCHI2}: {b[2] - a[2] - CERT_DCHI2:+.4f});'
              f' using 8-start means: {b[4] - a[4]:.4f} ({b[4] - a[4] - CERT_DCHI2:+.4f})')
    # cumulative cost per start
    print('\n===== cumulative cost per start (all rounds of this tag) =====')
    for fit in CERT:
        tot = []
        for k in range(8):
            recs = data[(fit, k)][0]
            nf = sum(v.get('nf', 0) for r, v in recs.items() if r > 0); w = sum(v.get('wall_s', 0) for r, v in recs.items() if r > 0)
            tot.append((nf, w)); print(f'{fit} s{k}: rounds {len([r for r in recs if r > 0])}, evaluations {nf}, wall {w / 60:.1f} min')
        print(f'{fit}: total evaluations {sum(t[0] for t in tot)}; max per-start wall {max(t[1] for t in tot) / 60:.1f} min')


if __name__ == '__main__':
    main(sys.argv[1])
