"""EXPLORATORY minimizer study 2 (not a gate attempt). Offline (no likelihood): as randinit_offline_check.py but with
init.random_directions_make_orthogonal=False (fully random directions, no antipodal pairs). Same quadratic stand-in."""
import numpy as np, pybobyqa, warnings
from pybobyqa.model import Model
warnings.simplefilter('ignore')
n = 8
rng = np.random.default_rng(0); Q = np.linalg.qr(rng.standard_normal((n, n)))[0]
H = Q @ np.diag([0.04, 0.4, 0.75, 1.0, 1.9, 3.8, 10, 24]) @ Q.T; g = rng.standard_normal(n) * 0.05
f = lambda x: 981.87 + g @ x + 0.5 * x @ H @ x
fstar = 981.87 - 0.5 * g @ np.linalg.solve(H, g)
lb, ub = -7 * np.ones(n), 15 * np.ones(n)
for npt in ((n + 1) * (n + 2) // 2, (n + 1) * (n + 2) // 2 - 1):
    out = []
    for rep in range(2):
        np.random.seed(9101); pts = []
        def fr(x):
            pts.append(x.copy()); return f(x)
        r = pybobyqa.solve(fr, np.zeros(n), bounds=(lb, ub), rhobeg=1.0, rhoend=0.005, npt=npt,
                           user_params={'init.random_initial_directions': True,
                                        'init.random_directions_make_orthogonal': False}, do_logging=False)
        out.append((r, np.array(pts)))
    r, P = out[0]
    print(f'npt={npt}: flag={r.flag} ({r.msg[:35]}) nf={r.nf} f-f*={r.f - fstar:.2e}; deterministic: '
          f'{np.array_equal(out[0][1], out[1][1])}')
    m = Model(npt, np.zeros(n), f(P[0]), lb, ub, None, 1, do_logging=False)
    for k in range(1, npt): m.change_point(k, P[k], f(P[k]))
    gn = np.array([np.linalg.norm(m.lagrange_polynomial(k)[1]) for k in range(1, npt)])
    d = np.linalg.norm(P[1:npt], axis=1)
    print(f'   initial set: |grad L_k(x0)| min {gn.min():.3e} median {np.median(gn):.3e}; points with |grad|<1e-8: '
          f'{int((gn < 1e-8).sum())}; distances to x0 {d.min():.3f}-{d.max():.3f}; antipodal pairs: '
          f'{sum(np.allclose(P[i], -P[j]) for i in range(1, npt) for j in range(i + 1, npt))}')
