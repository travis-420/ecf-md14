"""EXPLORATORY minimizer study 2 (not a gate attempt). Step 1: why did the geometry step return x_opt?
Offline, no likelihood evaluations: rebuilds Py-BOBYQA 1.5.0's own Model from the recorded interpolation set of
crash_repro.py run D1 and calls the installed lagrange_polynomial / trsbox_geometry exactly as
Controller.geometry_step does. Also checks the Lagrange-gradient structure of Py-BOBYQA's coordinate-direction
initial set for npt = 2n+1, (n+1)(n+2)/2 - 1 and (n+1)(n+2)/2 (point positions taken from D1's recorded
initial set; Lagrange polynomials do not depend on f for the full and npt<=2n+1 cases, and the min-change-Hessian
case is evaluated from a zero previous Hessian, i.e. its state right after initialisation).
"""
import json, sys, itertools
import numpy as np
import pybobyqa.trust_region as TR
from pybobyqa.model import Model
from pybobyqa.util import model_value

R = json.load(open('/Users/420-420/ecf-md14/fullplanck/tier2_explore2/logs/diag_D1_repro.json'))
names = R['sampled']; n = len(names)
print('pybobyqa.trust_region.USE_FORTRAN =', TR.USE_FORTRAN)
xl = np.array(R['solve_kwargs']['bounds'][0]); xu = np.array(R['solve_kwargs']['bounds'][1])
S1, S2 = R['snapshots'][1], R['snapshots'][2]


def build(points, fvals, npt):
    m = Model(npt, np.zeros(n), fvals[0], xl, xu, None, 1, do_logging=False)
    for k in range(1, npt):
        m.change_point(k, np.array(points[k]), fvals[k])
    return m


# interpolation set in force when the geometry step at nf=47 was computed: snapshot 2 with row 17 restored
P = np.array(S2['points']); F = np.array(S2['fvals'])
P[17] = np.array(S1['points'][17]); F[17] = S1['fvals'][17]
print('point 17 before the geometry step (scaled, rel. to x0):', P[17], ' -> pair of coordinates',
      [names[j] for j in np.where(P[17] != 0)[0]])
m = build(P, F, 45)
print('kopt =', m.kopt, ' xopt =', m.xopt())
c, g, H = m.lagrange_polynomial(17)
print(f'Lagrange polynomial of point 17 at xopt: c = {c:.3e}, |g| = {np.linalg.norm(g):.3e}, max|H| = {np.abs(H).max():.3e}')
big = [(names[i], names[j], H[i, j]) for i in range(n) for j in range(i, n) if abs(H[i, j]) > 1e-3 * np.abs(H).max()]
print('  Hessian entries above 1e-3 of max:', [(a, b, round(v, 4)) for a, b, v in big])
adelt = 0.14142135623730953
xnew = TR.trsbox_geometry(m.xopt(), c, g, H, m.sl, m.su, adelt)
print(f'trsbox_geometry(adelt={adelt:.4f}) returns step {np.array2string(xnew - m.xopt(), precision=3)}; '
      f'|L| there = {abs(c + model_value(g, H, xnew - m.xopt())):.3e}')
smin, _, _ = TR.trsbox(m.xopt(), g, H, m.sl, m.su, adelt); smax, _, _ = TR.trsbox(m.xopt(), -g, -H, m.sl, m.su, adelt)
print(f'  trsbox(min L) step norm {np.linalg.norm(smin):.3e}; trsbox(max L) step norm {np.linalg.norm(smax):.3e}')
# what |L| is attainable in the ball: best of +-adelt*(e_p +- e_q)/sqrt(2) over all pairs, and the eigen-direction
best = max((abs(c + model_value(g, H, adelt * (s1 * np.eye(n)[p] + s2 * np.eye(n)[q]) / np.sqrt(2))), names[p], names[q])
           for p, q in itertools.combinations(range(n), 2) for s1 in (1, -1) for s2 in (1, -1))
w, V = np.linalg.eigh(H)
print(f'  max |L| over the ball is at least {best[0]:.3e} (along {best[1]},{best[2]}); '
      f'|L| along top |eigen|-vector: {abs(c + model_value(g, H, adelt * V[:, np.argmax(np.abs(w))])):.3e}')

print('\nInitial (coordinate-direction) set as built by Py-BOBYQA with x_opt = x0 (D1 points):')
P0 = np.array(R['snapshots'][0]['points']); F0 = np.array(R['snapshots'][0]['fvals'])
for npt, lab in [(2 * n + 1, 'npt = 2n+1 (cobaya default)'), ((n + 1) * (n + 2) // 2 - 1, 'npt = (n+1)(n+2)/2 - 1'),
                 ((n + 1) * (n + 2) // 2, 'npt = (n+1)(n+2)/2')]:
    m0 = build(P0[:npt], F0[:npt], npt)
    gn = []
    for k in range(1, npt):
        c, g, H = m0.lagrange_polynomial(k)
        gn.append(np.linalg.norm(g))
    gn = np.array(gn)
    coord = gn[:2 * n]; pair = gn[2 * n:]
    print(f'  {lab:28s}: |grad L_k(x_opt)| coordinate points min {coord.min():.3e}; '
          + (f'pair points min {pair.min():.3e} max {pair.max():.3e} ({len(pair)} pair points)' if len(pair) else 'no pair points'))
    # furthest points from xopt and their Lagrange gradient: what a geometry step would target first
    d = np.sqrt(np.sum(P0[1:npt] ** 2, axis=1))
    kfar = 1 + int(np.argmax(d))
    print(f'      geometry step would target k={kfar} (distance {d.max():.3f}); |grad L_k| = {gn[kfar - 1]:.3e}')
