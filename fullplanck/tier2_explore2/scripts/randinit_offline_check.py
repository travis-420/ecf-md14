"""EXPLORATORY minimizer study 2 (not a gate attempt). Offline check (no likelihood): Py-BOBYQA 1.5.0 with
npt = (n+1)(n+2)/2 and init.random_initial_directions=True, numpy global RNG seeded -> (1) runs, (2) is
deterministic given the seed, (3) the initial set's Lagrange polynomials have nonzero gradient at x0.
Uses D1's recorded objective values only to define a smooth quadratic stand-in (gradient/Hessian Py-BOBYQA printed)."""
import json, numpy as np, pybobyqa, warnings
from pybobyqa.model import Model
warnings.simplefilter('ignore')
n = 8; npt = (n + 1) * (n + 2) // 2
rng = np.random.default_rng(0); Q = np.linalg.qr(rng.standard_normal((n, n)))[0]
H = Q @ np.diag([0.04, 0.4, 0.75, 1.0, 1.9, 3.8, 10, 24]) @ Q.T; g = rng.standard_normal(n) * 0.05
f = lambda x: 981.87 + g @ x + 0.5 * x @ H @ x
lb, ub = -7 * np.ones(n), 15 * np.ones(n)
res = []
for rep in range(2):
    np.random.seed(9101)
    pts = []
    def fr(x):
        pts.append(x.copy()); return f(x)
    r = pybobyqa.solve(fr, np.zeros(n), bounds=(lb, ub), rhobeg=1.0, rhoend=0.005, npt=npt,
                       user_params={'init.random_initial_directions': True}, do_logging=False)
    res.append((r.flag, r.nf, r.f, np.array(pts)))
    print(f'rep {rep}: flag={r.flag} ({r.msg[:40]}) nf={r.nf} f-f*={r.f - (981.87 - 0.5 * g @ np.linalg.solve(H, g)):.2e}')
print('deterministic given the seed (same points, bitwise):', res[0][1] == res[1][1] and np.array_equal(res[0][3], res[1][3]))
P = res[0][3][:npt]
m = Model(npt, np.zeros(n), f(P[0]), lb, ub, None, 1, do_logging=False)
for k in range(1, npt): m.change_point(k, P[k], f(P[k]))
gn = [np.linalg.norm(m.lagrange_polynomial(k)[1]) for k in range(1, npt)]
print(f'initial random set: |grad L_k(x0)| min {min(gn):.3e} max {max(gn):.3e}; distances to x0 '
      f'{np.linalg.norm(P[1:], axis=1).min():.3f}-{np.linalg.norm(P[1:], axis=1).max():.3f}')
gn = np.array(gn); print('per-point |grad L_k(x0)| (k=1..npt-1):', np.array2string(gn, precision=2, max_line_width=200))
print('points with |grad| < 1e-8:', [int(k) + 1 for k in np.where(gn < 1e-8)[0]], 'of', npt - 1)
# is the pattern +-q_i (antipodal pairs)? check P[k] + P[k+n] for k=1..n
print('antipodal pairs among first 2n points:', [bool(np.allclose(P[k], -P[k + n])) for k in range(1, n + 1)])
