"""EXPLORATORY minimizer study 2 (not a gate attempt). Step 1: offline analysis of a crash_repro.py dump.
No likelihood evaluations. Uses the installed Py-BOBYQA 1.5.0's own build_interpolation_matrix.
Usage: python crash_analyze.py <diag_json>
"""
import sys, json, itertools
import numpy as np, scipy.linalg as LA
from pybobyqa.model import build_interpolation_matrix

R = json.load(open(sys.argv[1]))
names = R['sampled']; n = len(names)
print(f"label={R['label']} outcome={R['outcome']} n_evals={len(R['evals'])} result={R.get('result')}")
kw = R['solve_kwargs']
print('solve kwargs (except objfun):', {k: v for k, v in kw.items() if k not in ('x0', 'bounds')})
lb, ub = np.array(kw['bounds'][0]), np.array(kw['bounds'][1])
print('scaled bounds relative to x0 (lower, upper), in units of rhobeg-scaled widths:')
for j, p in enumerate(names):
    print(f'  {p:9s} [{lb[j]:+10.3f}, {ub[j]:+10.3f}]  within 1.0 of x0: {abs(lb[j]) < 1 or ub[j] < 1}')

# monomial labels for the columns of the full-quadratic interpolation matrix (Py-BOBYQA ordering)
cols = [f'{p}' for p in names]
for j in range(n):
    for i in range(j + 1):
        cols.append(f'{names[i]}^2/2' if i == j else f'{names[i]}*{names[j]}')


def analyse(snap, tag):
    P = np.array(snap['points']); kopt = snap['kopt']; npt = len(P)
    xopt = P[kopt]
    Y = np.delete(P, kopt, axis=0) - xopt          # rows = y_t = x_t - xopt
    d2 = np.sum(Y ** 2, axis=1)
    approx_delta = np.sqrt(np.max(d2))
    A, ls, rs = build_interpolation_matrix(Y.T, approx_delta=approx_delta)
    print(f'--- {tag}: npt={npt} kopt={kopt} ok={snap["ok"]} evals so far={snap["n_evals_so_far"]} '
          f'approx_delta={approx_delta:.4g} A shape={A.shape}')
    # duplicates / near-duplicates
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1)); np.fill_diagonal(D, np.inf)
    i, j = np.unravel_index(np.argmin(D), D.shape)
    print(f'  min pairwise distance between interpolation points: {D[i, j]:.3e} (points {i},{j}); '
          f'exact duplicates: {int(np.sum(D == 0) // 2)}')
    print(f'  distances to xopt: min {np.sqrt(d2.min()):.3e} max {np.sqrt(d2.max()):.3e}')
    if A.shape[0] == A.shape[1] and A.shape[0] == (n + 1) * (n + 2) // 2 - 1:
        zero_cols = [cols[c] for c in range(A.shape[1]) if np.all(A[:, c] == 0)]
        nnz = {cols[c]: int(np.sum(A[:, c] != 0)) for c in range(A.shape[1])}
        print(f'  exactly-zero columns of A: {zero_cols}')
        print('  columns with <= 2 nonzero entries:', {k: v for k, v in nnz.items() if v <= 2})
    lu, piv = LA.lu_factor(A, check_finite=False)
    dg = np.abs(np.diag(lu))
    zero_piv = np.where(dg == 0)[0]
    print(f'  LU: exactly-zero pivots at (1-based diagonal numbers) {list(zero_piv + 1)}'
          + (f' -> columns {[cols[c] for c in zero_piv]}' if A.shape[0] == len(cols) else ''))
    print(f'  LU: smallest |pivot| {dg.min():.3e}; next {np.sort(dg)[1]:.3e}')
    sv = LA.svdvals(A)
    print(f'  singular values: max {sv[0]:.3e}, smallest 4 {np.array2string(sv[-4:], precision=3)}; '
          f'cond {sv[0] / max(sv[-1], 1e-300):.3e}')
    U, S, Vt = LA.svd(A)
    v = Vt[-1]
    top = np.argsort(-np.abs(v))[:6]
    if A.shape[0] == len(cols):
        print('  null-space direction of A (largest components): '
              + ', '.join(f'{cols[c]}:{v[c]:+.3f}' for c in top))
    # per-coordinate structure of the point set
    nz = (np.abs(Y) > 0)
    print('  number of points (excl. xopt) with nonzero displacement in each coordinate:',
          {names[c]: int(nz[:, c].sum()) for c in range(n)})
    return P, Y, A


snaps = R['snapshots']
print(f'number of interpolate_model calls: {len(snaps)}; ok flags: {[s["ok"] for s in snaps]}')
# compare consecutive snapshots: which points changed
for s in range(1, len(snaps)):
    P0 = np.array(snaps[s - 1]['points']); P1 = np.array(snaps[s]['points'])
    ch = [int(k) for k in np.where(np.any(P0 != P1, axis=1))[0]]
    print(f'  snapshot {s}: points changed vs previous: {ch}; kopt {snaps[s-1]["kopt"]}->{snaps[s]["kopt"]}; '
          f'xbase changed: {snaps[s-1]["xbase"] != snaps[s]["xbase"]}')
print('events:')
for e in R['events']:
    if e['type'] == 'tr_step':
        d = np.array(e['d'])
        print(f"  nf={e['nf']} TR step |d|={np.linalg.norm(d):.4f} delta={e['delta']:.4g} rho={e['rho']:.4g} "
              f"kopt={e['kopt']} exact-zero comps={[names[c] for c in np.where(d == 0)[0]]} "
              f"d={np.array2string(d, precision=4)}")
    else:
        print('  ', {k: v for k, v in e.items()})
print('evaluations after initialisation (i, f, scaled x):')
npt = len(snaps[0]['points']) if snaps else 0
for ev in R['evals'][max(npt - 1, 0):]:
    print(f"  {ev['i']:4d} f={ev['f']:.7f} x={np.array2string(np.array(ev['x']), precision=4)}")
print(f"f(x0) = {R['evals'][0]['f']:.10f}; min f over evals = {min(e['f'] for e in R['evals']):.10f}; "
      f"mean eval time {np.mean([e['dt'] for e in R['evals']]):.2f} s")
if snaps:
    analyse(snaps[0], 'first snapshot (after initialisation)')
    if len(snaps) > 1:
        analyse(snaps[-2], 'last successful snapshot')
    analyse(snaps[-1], 'LAST snapshot')
