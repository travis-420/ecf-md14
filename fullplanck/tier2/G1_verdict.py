"""Gate G1 verdict (PREREG_NEUTRINO_TIER2.md): fits 1 and 2 vs the certified minima.
Criteria: |chi2(fit1) - 2005.5316| <= 0.5, |chi2(fit2) - 1993.8933| <= 0.5, |Dchi2 - (-11.64)| <= 0.5,
with certified values read from fullplanck/chains/*.minimum.txt. chi2 = total likelihood chi2 column.
'Best' start evaluated under both readings: (A) lowest minimized objective (minuslogpost; cobaya's
best_of rule, as in the certified July runs); (B) lowest chi2."""
import glob, re
KIT = '/Users/420-420/ecf-md14/fullplanck'
def read_min(p):
    with open(p) as f:
        h = f.readline().lstrip('#').split(); v = [float(x) for x in f.readline().split()]
    return dict(zip(h, v))
cert = {'fit1': read_min(f'{KIT}/chains/lcdm.minimum.txt'), 'fit2': read_min(f'{KIT}/chains/ecf.minimum.txt')}
runs = {}
for fit, pre in [('fit1', 'fit1_lcdm_mnufixed'), ('fit2', 'fit2_ecf_mnufixed')]:
    runs[fit] = []
    for p in sorted(glob.glob(f'{KIT}/tier2/chains/{pre}_s*.minimum.txt')):
        d = read_min(p); d['start'] = int(re.search(r'_s(\d+)\.min', p).group(1)); runs[fit].append(d)
    print(f'\n{fit} ({pre}) per start:  minuslogpost | chi2 | minuslogprior__0 | minuslogprior__tau_prior')
    for d in sorted(runs[fit], key=lambda d: d['start']):
        print(f"  s{d['start']}: {d['minuslogpost']:.4f} | {d['chi2']:.4f} | {d['minuslogprior__0']:.4f} | {d['minuslogprior__tau_prior']:.4f}")
    c = cert[fit]
    print(f"  certified: {c['minuslogpost']:.4f} | {c['chi2']:.4f} | {c['minuslogprior__0']:.4f} | {c['minuslogprior__tau_prior']:.4f}")
cD = cert['fit2']['chi2'] - cert['fit1']['chi2']
print(f'\ncertified chi2: fit1 {cert["fit1"]["chi2"]:.4f}, fit2 {cert["fit2"]["chi2"]:.4f}, Dchi2 {cD:.4f}')
verdicts = {}
for rule, key in [('A (lowest minuslogpost)', 'minuslogpost'), ('B (lowest chi2)', 'chi2')]:
    b1 = min(runs['fit1'], key=lambda d: d[key]); b2 = min(runs['fit2'], key=lambda d: d[key])
    d1 = b1['chi2'] - cert['fit1']['chi2']; d2 = b2['chi2'] - cert['fit2']['chi2']
    D = b2['chi2'] - b1['chi2']; dD = D - cD
    p1, p2, pD = abs(d1) <= 0.5, abs(d2) <= 0.5, abs(dD) <= 0.5
    print(f'\nRule {rule}: fit1 best s{b1["start"]}, fit2 best s{b2["start"]}')
    print(f'  fit1 chi2 {b1["chi2"]:.4f}  vs certified: {d1:+.4f}  -> {"pass" if p1 else "FAIL"}')
    print(f'  fit2 chi2 {b2["chi2"]:.4f}  vs certified: {d2:+.4f}  -> {"pass" if p2 else "FAIL"}  (tau_ecf {b2["tau_ecf"]:.4f})')
    print(f'  Dchi2 {D:.4f}  vs certified {cD:.4f}: {dD:+.4f}  -> {"pass" if pD else "FAIL"}')
    verdicts[rule] = p1 and p2 and pD
    print(f'  G1 under rule {rule}: {"PASS" if verdicts[rule] else "FAIL"}')
print(f'\nG1 VERDICT: {"PASS" if all(verdicts.values()) else ("FAIL under both readings" if not any(verdicts.values()) else "rule-dependent")}')
# Diagnostic: the minimized objective itself
b1 = min(runs['fit1'], key=lambda d: d['minuslogpost']); b2 = min(runs['fit2'], key=lambda d: d['minuslogpost'])
print('\nDiagnostic (minimized objective, not a G1 criterion):')
print(f'  fit1 best minuslogpost {b1["minuslogpost"]:.4f} vs certified {cert["fit1"]["minuslogpost"]:.4f}: {b1["minuslogpost"]-cert["fit1"]["minuslogpost"]:+.4f}')
print(f'  fit2 best minuslogpost {b2["minuslogpost"]:.4f} vs certified {cert["fit2"]["minuslogpost"]:.4f}: {b2["minuslogpost"]-cert["fit2"]["minuslogpost"]:+.4f}')
dpost = 2*(b2['minuslogpost']-b1['minuslogpost']); cdpost = 2*(cert['fit2']['minuslogpost']-cert['fit1']['minuslogpost'])
print(f'  2*D(minuslogpost): this run {dpost:.4f}, certified {cdpost:.4f}, diff {dpost-cdpost:+.4f}')
for fit in ('fit1', 'fit2'):
    r = runs[fit]
    print(f'  {fit}: spread over starts  minuslogpost {max(d["minuslogpost"] for d in r)-min(d["minuslogpost"] for d in r):.4f}, '
          f'chi2 {max(d["chi2"] for d in r)-min(d["chi2"] for d in r):.4f}')
    near = [d for d in r if d['minuslogpost'] - min(x['minuslogpost'] for x in r) <= 0.1]
    print(f'  {fit}: starts within 0.1 of best minuslogpost: {[f"s{d["start"]}" for d in near]}, '
          f'their chi2 range {min(d["chi2"] for d in near):.4f}-{max(d["chi2"] for d in near):.4f}')
