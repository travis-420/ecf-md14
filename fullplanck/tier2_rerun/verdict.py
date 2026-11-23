"""Tier 2 RERUN verdict script. Implements AMENDMENT_TIER2_MINIMIZER.md (commit 1fd858e):
  section 1 (selection rule), 2.4 (converged starts, window, "stopped short", 4-of-8 rule),
  section 3 (G1 criteria; July-suboptimal, readout-drift, rerun-worse clauses; G1 spread guard;
  precedence rules), section 4 (reporting), and section 5 (R1-R4 outcome rules, minimizer-limited
  rule), with R1-R4 thresholds as frozen in PREREG_NEUTRINO_TIER2.md.
Written and frozen (SHA-256 recorded) BEFORE any rerun fit was launched; not edited afterwards.

Usage:
  python verdict.py g1      -> section 4 reporting for fits 1, 2 and the section 3 G1 verdict
  python verdict.py final   -> the same, then (only if G1 PASS) section 4 for fits 3-5 and section 5
  optional: --root DIR --nstarts N   (used only for the self-test on session-1 outputs)

Quantities (section 0): total chi2 = `chi2` column of .minimum.txt (plik-lite + DESI DR2 + Pantheon+);
-log posterior = `minuslogpost`; -2 log posterior = 2 * minuslogpost;
tau-prior term = 2 * minuslogprior__tau_prior (chi2 units).
A start is converged iff its log contains 'Run 1/1 converged.' and the process exit line 'EXIT=0 '
(written by run_starts.sh)."""
import argparse, glob, math, os, re, sys

KIT = '/Users/420-420/ecf-md14/fullplanck'
FITS = {1: 'fit1_lcdm_mnufixed', 2: 'fit2_ecf_mnufixed', 3: 'fit3_lcdm_mnufree',
        4: 'fit4_ecf_mnufree', 5: 'fit5_cpl_mnufree'}
L_CMB, L_BAO, L_SN = ('chi2__planck_2018_highl_plik.TTTEEE_lite_native', 'chi2__bao.desi_dr2',
                      'chi2__sn.pantheonplus')
# Frozen constants
G1_TOL = 0.5            # section 3 / prereg G1 tolerance (chi2 units)
WINDOW = 0.25           # section 2.4: in window iff -log post - best <= 0.25
MIN_IN_WINDOW = 4       # section 2.4: fewer than 4 in-window converged starts -> minimizer-failed
SPREAD_GUARD = 0.5      # section 3: S > 0.5 for fit 1 or 2 -> minimizer-failed for G1
CLAUSE = 0.25           # section 3: July-suboptimal / rerun-worse threshold on -log post
TWO_LN_57 = 2 * math.log(5.7)   # section 4
R_D1, R_D2 = -9.0, -2.0                     # prereg R1/R2/R3 Delta chi2 boundaries
TAU68, TAU95 = (1.894, 3.277), (1.581, 4.604)  # prereg certified tau_ecf intervals


def read_min(p):
    with open(p) as f:
        h = f.readline().lstrip('#').split(); v = [float(x) for x in f.readline().split()]
    return dict(zip(h, v))


def load_start(root, fit, k):
    """One start: log-derived convergence, start point, seed, settings; minimum.txt values."""
    name = f'{FITS[fit]}_s{k}'
    d = {'start': k, 'name': name, 'converged': False, 'have_min': False, 'log': False}
    logp = f'{root}/logs/{name}.log'
    if os.path.exists(logp):
        log = open(logp).read(); d['log'] = True
        d['conv_line'] = 'Run 1/1 converged.' in log
        d['exit0'] = re.search(r'^EXIT=0 start=', log, re.M) is not None
        m = re.search(r'^EXIT=(\S+) start=(\S+) end=(\S+)', log, re.M)
        d['exit'], d['t_start'], d['t_end'] = (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)
        d['converged'] = d['conv_line'] and d['exit0']
        m = re.search(r'SEEDED with seed (\d+)', log); d['seed'] = int(m.group(1)) if m else None
        m = re.search(r"will start from.*\n\[minimize\] (\{.*\})", log)
        d['start_point'] = ({kk: float(vv) for kk, vv in
                             re.findall(r"'(\w+)': np\.float64\(([-+0-9.eE]+)\)", m.group(1))} if m else None)
    upd = f'{root}/chains/{name}.minimize.updated.yaml'
    if os.path.exists(upd):
        u = open(upd).read()
        m = re.search(r'rhoend:\s*(\S+)', u); d['rhoend'] = float(m.group(1)) if m else None
    mp = f'{root}/chains/{name}.minimum.txt'
    if os.path.exists(mp):
        d.update(read_min(mp)); d['have_min'] = True
        d['chi2_sum3'] = d[L_CMB] + d[L_BAO] + d[L_SN]
    return d


def analyse(root, fit, nstarts):
    """Sections 1 and 2.4 for one fit."""
    starts = [load_start(root, fit, k) for k in range(nstarts)]
    conv = [s for s in starts if s['converged'] and s['have_min']]
    r = {'fit': fit, 'starts': starts, 'n_conv': len(conv), 'nstarts': nstarts,
         'conv_no_min': [s['start'] for s in starts if s['converged'] and not s['have_min']]}
    if not conv:
        r.update(sel=None, best=None, inwin=[], n_in=0, S=None, S_all=None)
        return r
    sel = min(conv, key=lambda s: s['minuslogpost'])            # section 1
    best = sel['minuslogpost']
    for s in starts:
        if s['have_min']:
            s['dbest'] = s['minuslogpost'] - best
        if s['converged'] and s['have_min']:
            s['in_window'] = s['dbest'] <= WINDOW                  # section 2.4
    inwin = [s for s in conv if s['in_window']]
    r.update(sel=sel, best=best, inwin=inwin, n_in=len(inwin),
             S=max(s['chi2'] for s in inwin) - min(s['chi2'] for s in inwin),
             S_all=max(s['chi2'] for s in conv) - min(s['chi2'] for s in conv))
    return r


def fmt(x, n=4):
    return '—' if x is None else f'{x:.{n}f}'


def report(r):
    """Section 4 reporting for one fit."""
    fit = r['fit']
    print(f'\n### Fit {fit} ({FITS[fit]})')
    print(f"converged starts: {r['n_conv']} of {r['nstarts']}; in window: {r['n_in']}; "
          f"stopped short: {sum(1 for s in r['starts'] if s.get('in_window') is False)}")
    if r['conv_no_min']:
        print(f"WARNING: converged per log but no .minimum.txt: {r['conv_no_min']}")
    extra = [k for k in ('tau_ecf', 'mnu', 'w', 'wa') if any(k in s for s in r['starts'])]
    hdr = ['start', 'seed', 'rhoend', 'exit', 'converged', 'status', '-log post', '-log post - best',
           '-2 log post', 'total chi2', 'chi2 CMB', 'chi2 BAO', 'chi2 SN', 'tau-prior term (2x)'] + extra
    print('| ' + ' | '.join(hdr) + ' |'); print('|' + '---|' * len(hdr))
    for s in r['starts']:
        if not s['log']:
            print(f"| s{s['start']} | (no log) |"); continue
        status = ('not converged' if not s['converged'] else
                  ('in window' if s.get('in_window') else 'stopped short'))
        if s is r['sel']:
            status += ' (SELECTED)'
        if s['have_min']:
            vals = [fmt(s['minuslogpost']), fmt(s['dbest']), fmt(2 * s['minuslogpost']), fmt(s['chi2']),
                    fmt(s[L_CMB]), fmt(s[L_BAO]), fmt(s[L_SN]), fmt(2 * s['minuslogprior__tau_prior'])]
            vals += [fmt(s.get(k), 5) for k in extra]
        else:
            vals = ['—'] * (8 + len(extra))
        print(f"| s{s['start']} | {s.get('seed')} | {s.get('rhoend')} | {s.get('exit')} | "
              f"{s['converged']} | {status} | " + ' | '.join(vals) + ' |')
    print('start points (from each run log):')
    for s in r['starts']:
        print(f"  s{s['start']}: {s.get('start_point')}")
    for s in r['starts']:
        if s['have_min'] and abs(s['chi2'] - s['chi2_sum3']) > 1e-3:
            print(f"  NOTE s{s['start']}: chi2 column {s['chi2']} != sum of three {s['chi2_sum3']}")
    if r['sel'] is None:
        print('selected start: NONE (no converged start)'); return
    sel = r['sel']
    print(f"selected start (section 1): s{sel['start']}  -log post = {sel['minuslogpost']:.4f}  "
          f"total chi2 = {sel['chi2']:.4f}" + ''.join(f'  {k} = {sel[k]:.5f}' for k in extra if k in sel))
    print(f"S (in-window spread of total chi2) = {r['S']:.4f}   over in-window starts "
          f"{['s%d' % s['start'] for s in r['inwin']]}")
    print(f"spread of total chi2 over ALL converged starts (reporting only) = {r['S_all']:.4f}")
    print(f"minimizer-failed by 4-of-8 rule: {'YES' if r['n_in'] < MIN_IN_WINDOW else 'no'} "
          f"({r['n_in']} in-window converged; requirement >= {MIN_IN_WINDOW})")


def cross(ra, rb, la, lb):
    if ra['sel'] is None or rb['sel'] is None:
        print(f'  ({la}, {lb}): not available (no selected start)'); return
    d = 2 * (ra['sel']['minuslogpost'] - rb['sel']['minuslogpost'])
    print(f'  ({la}, {lb}): Delta(-2 log posterior) = {d:.4f};  net of 2 ln 5.7 ({TWO_LN_57:.4f}): '
          f'{d - TWO_LN_57:.4f}')


def g1_decide(d_mlp, crit, mf):
    """Section 3 decision. d_mlp: {1: x or None, 2: x or None} = selected -log post - certified.
    crit: {'fit1': bool, 'fit2': bool, 'dchi2': bool} or None if a fit has no selected start.
    mf: {1: [reasons], 2: [reasons]} from the 4-of-8 rule and the G1 spread guard.
    Returns (G1 label, list of fit labels, erratum text, proceed_to_fits_3_5)."""
    mf = {f: list(v) for f, v in mf.items()}
    subopt = [f for f in (1, 2) if d_mlp[f] is not None and d_mlp[f] < -CLAUSE]
    worse = [f for f in (1, 2) if d_mlp[f] is not None and d_mlp[f] > CLAUSE]
    for f in worse:
        mf[f].append('rerun-worse case (selected -log posterior more than 0.25 above July)')
    within_both = all(d_mlp[f] is not None and abs(d_mlp[f]) <= CLAUSE for f in (1, 2))
    any_mf = any(mf[f] for f in (1, 2))
    fit_labels = [f'fit {f}: minimizer-failed — ' + '; '.join(mf[f]) for f in (1, 2) if mf[f]]
    erratum = 'none'
    if subopt:
        g1 = 'FAILED: July certified value suboptimal'
        erratum = (f'erratum follows (July-suboptimal clause fired by fit(s) {subopt}): the certified numbers '
                   'are re-derived and corrected publicly before any further Tier 2 run; the corrected '
                   'certified values must come from a re-derivation in which fits 1 and 2 each satisfy '
                   'the 4-of-8 rule and the G1 spread guard' +
                   (' and neither fit is minimizer-failed by the rerun-worse case' if worse else '') +
                   '; errata quote S')
    elif any_mf:
        if within_both and crit is not None and not all(crit.values()):
            g1 = 'failed: minimizer-failed'
            erratum = 'none (readout-drift clause NOT declared because a fit is minimizer-failed)'
        else:
            g1 = 'failed (G1 recorded as failed; see minimizer-failed fit labels)'
            erratum = 'none from this run'
    elif crit is not None and not all(crit.values()):
        # here: no suboptimal, no worse, both selected -> both within 0.25
        assert within_both
        g1 = 'FAILED: certified χ² is a drifted readout'
        erratum = ('erratum follows (readout-drift clause): the certified chi2 values and the headline '
                   'Delta chi2 = -11.64 are re-derived at the rerun\'s selected minima and corrected '
                   'publicly before any further Tier 2 run; errata quote S')
    else:
        assert within_both and crit is not None and all(crit.values())
        g1 = 'PASS'
    return g1, fit_labels, erratum, g1 == 'PASS'


def do_g1(root, nstarts):
    print('=' * 100); print('G1 (AMENDMENT_TIER2_MINIMIZER.md sections 1, 2.4, 3, 4)')
    cert = {1: read_min(f'{KIT}/chains/lcdm.minimum.txt'), 2: read_min(f'{KIT}/chains/ecf.minimum.txt')}
    assert round(cert[1]['chi2'], 4) == 2005.5316 and round(cert[2]['chi2'], 4) == 1993.8933
    assert round(cert[1]['minuslogpost'], 4) == 986.0217 and round(cert[2]['minuslogpost'], 4) == 981.9394
    cD = cert[2]['chi2'] - cert[1]['chi2']
    print(f"certified: fit 1 chi2 {cert[1]['chi2']:.4f}, -log post {cert[1]['minuslogpost']:.5f}; "
          f"fit 2 chi2 {cert[2]['chi2']:.4f}, -log post {cert[2]['minuslogpost']:.5f}; Delta chi2 {cD:.4f}")
    R = {f: analyse(root, f, nstarts) for f in (1, 2)}
    for f in (1, 2):
        report(R[f])
    print('\nCross-model -2 log posterior differences (reporting only; no rule uses them):')
    cross(R[2], R[1], 'fit 2', 'fit 1')
    print(f"  July certified (fit 2, fit 1): {2 * (cert[2]['minuslogpost'] - cert[1]['minuslogpost']):.4f}; "
          f"net {2 * (cert[2]['minuslogpost'] - cert[1]['minuslogpost']) - TWO_LN_57:.4f}")
    print('\n--- Section 3 ---')
    mf = {f: [] for f in (1, 2)}
    d_mlp = {}
    for f in (1, 2):
        if R[f]['n_in'] < MIN_IN_WINDOW:
            mf[f].append(f"4-of-8 rule ({R[f]['n_in']} in-window converged starts < {MIN_IN_WINDOW})")
        if R[f]['S'] is not None and R[f]['S'] > SPREAD_GUARD:
            mf[f].append(f"G1 spread guard (S = {R[f]['S']:.4f} > {SPREAD_GUARD})")
        d_mlp[f] = None if R[f]['sel'] is None else R[f]['sel']['minuslogpost'] - cert[f]['minuslogpost']
        print(f"fit {f}: selected -log post - certified July minuslogpost = {fmt(d_mlp[f])}  "
              f"(-2 log post: {fmt(None if d_mlp[f] is None else 2 * d_mlp[f])})")
    crit = None
    if R[1]['sel'] is not None and R[2]['sel'] is not None:
        c1, c2 = R[1]['sel']['chi2'], R[2]['sel']['chi2']
        d1, d2, dD = c1 - cert[1]['chi2'], c2 - cert[2]['chi2'], (c2 - c1) - cD
        crit = {'fit1': abs(d1) <= G1_TOL, 'fit2': abs(d2) <= G1_TOL, 'dchi2': abs(dD) <= G1_TOL}
        print(f"G1 criterion 1: |chi2(fit 1) - {cert[1]['chi2']:.4f}| = |{c1:.4f} - {cert[1]['chi2']:.4f}| "
              f"= {abs(d1):.4f} ({d1:+.4f}) -> {'pass' if crit['fit1'] else 'FAIL'}")
        print(f"G1 criterion 2: |chi2(fit 2) - {cert[2]['chi2']:.4f}| = |{c2:.4f} - {cert[2]['chi2']:.4f}| "
              f"= {abs(d2):.4f} ({d2:+.4f}) -> {'pass' if crit['fit2'] else 'FAIL'}")
        print(f"G1 criterion 3: Delta chi2 (fit 2 - fit 1) = {c2 - c1:.4f}; |Delta chi2 - ({cD:.4f})| = "
              f"{abs(dD):.4f} ({dD:+.4f}) -> {'pass' if crit['dchi2'] else 'FAIL'}")
    else:
        print('G1 criteria: not evaluable (a fit has no converged start)')
    for f in (1, 2):
        print(f"fit {f}: S = {fmt(R[f]['S'])} (guard {SPREAD_GUARD}); in-window converged = {R[f]['n_in']}; "
              f"July-suboptimal condition (b) [d < -{CLAUSE}]: "
              f"{'HOLDS' if d_mlp[f] is not None and d_mlp[f] < -CLAUSE else 'no'}; "
              f"rerun-worse [d > +{CLAUSE}]: {'HOLDS' if d_mlp[f] is not None and d_mlp[f] > CLAUSE else 'no'}")
    g1, fit_labels, erratum, proceed = g1_decide(d_mlp, crit, mf)
    print(f'\nG1 LABEL: {g1}')
    for lab in fit_labels:
        print(f'  {lab}')
    print(f'Erratum: {erratum}')
    print(f"Proceed to fits 3-5: {'YES' if proceed else 'NO (run stops)'}")
    return R, proceed


def r_decide(D, tau, S, mf_fits):
    """Section 5 / prereg R1-R3. Returns (label, details)."""
    in68 = TAU68[0] <= tau <= TAU68[1]
    in95 = TAU95[0] <= tau <= TAU95[1]
    conds = {'R1': D <= R_D1 and in68,
             'R2': (R_D1 < D <= R_D2) or ((not in68) and in95),
             'R3': D > R_D2 or (not in95)}
    det = (f'Delta chi2 = {D:.4f}; tau_ecf = {tau:.5f} (in 68% {list(TAU68)}: {in68}; in 95% {list(TAU95)}: '
           f'{in95}); S = max(S3, S4) = {fmt(S)}; |D - (-9.0)| = {abs(D - R_D1):.4f}, '
           f'|D - (-2.0)| = {abs(D - R_D2):.4f}; conditions holding: '
           f"{[k for k, v in conds.items() if v]}")
    if mf_fits:
        bad = [f for f in mf_fits if f in (3, 4)]
        if bad:
            return f'no R1–R4 outcome declared (fit(s) {mf_fits} minimizer-failed, section 2.4/5)', det
        return (f'AMBIGUOUS — not declared: fit 5 is minimizer-failed; section 2.4 says "for fits 3–5, no '
                f'R1–R4 outcome is declared", section 5 names only fits 3 and 4'), det
    if abs(D - R_D1) <= S or abs(D - R_D2) <= S:
        return 'minimizer-limited (R1/R2/R3 verdict not declared)', det
    held = [k for k, v in conds.items() if v]
    if len(held) == 1:
        lab = held[0]
        if lab == 'R1':
            lab += ' — SURVIVES: robust to free Σmν (full plik-lite likelihood, no lensing)'
        elif lab == 'R2':
            lab += ' — WEAKENED'
        else:
            lab += ' — FAILS (fires)'
        return lab, det
    return (f'AMBIGUOUS — not declared: conditions of {held} all hold and the protocol states no '
            f'precedence'), det


def do_final(root, nstarts):
    R12, proceed = do_g1(root, nstarts)
    print('\n' + '=' * 100); print('Fits 3-5 (sections 2.4, 4) and section 5')
    if not proceed:
        print('G1 did not pass: fits 3-5 are not evaluated.'); return
    R = {f: analyse(root, f, nstarts) for f in (3, 4, 5)}
    for f in (3, 4, 5):
        report(R[f])
    print('\nCross-model -2 log posterior differences (reporting only; no rule uses them):')
    cross(R12[2], R12[1], 'fit 2', 'fit 1')
    cross(R[4], R[3], 'fit 4', 'fit 3')
    print('\n--- Section 5 ---')
    mf_fits = [f for f in (3, 4, 5) if R[f]['n_in'] < MIN_IN_WINDOW]
    for f in (3, 4, 5):
        print(f"fit {f}: in-window converged = {R[f]['n_in']} -> "
              f"{'minimizer-failed' if f in mf_fits else 'ok'}; S = {fmt(R[f]['S'])}")
    if R[3]['sel'] is None or R[4]['sel'] is None:
        print('R1-R4: no R1–R4 outcome declared (fit 3 or 4 has no converged start)'); return
    D = R[4]['sel']['chi2'] - R[3]['sel']['chi2']
    tau = R[4]['sel']['tau_ecf']
    S = max(R[3]['S'], R[4]['S'])
    lab, det = r_decide(D, tau, S, mf_fits)
    print(det)
    print(f'R1/R2/R3 VERDICT: {lab}')
    if R12[2]['sel'] is not None:
        r4 = R12[2]['sel']['chi2'] - R[3]['sel']['chi2']
        print(f"R4 (verbatim, no threshold): chi2(fit 2) - chi2(fit 3) = {R12[2]['sel']['chi2']:.4f} - "
              f"{R[3]['sel']['chi2']:.4f} = {r4:.4f}" +
              ('' if not any(f in (3, 4) for f in mf_fits) else '  [not declared: fit 3/4 minimizer-failed]'))
    print(f"fit 5 (CPL + free mnu, context only): selected chi2 {fmt(R[5]['sel']['chi2'] if R[5]['sel'] else None)}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['g1', 'final'])
    ap.add_argument('--root', default=f'{KIT}/tier2_rerun')
    ap.add_argument('--nstarts', type=int, default=8)
    a = ap.parse_args()
    print(f'verdict.py mode={a.mode} root={a.root} nstarts={a.nstarts}')
    (do_g1 if a.mode == 'g1' else do_final)(a.root, a.nstarts)
