"""EXPLORATORY (not a gate attempt): does Py-BOBYQA 1.5.0 with npt=(n+1)(n+2)/2 hit EXIT_LINALG_ERROR on a smooth
quadratic? Gradient/Hessian = the 'Approximate gradient/Hessian' Py-BOBYQA printed at the step3A fit2 s1 crash
(logs/step3A_fit2_ecf_mnufixed_s1.log), in cobaya's scaled units. Optional additive noise (seeded) of given size.
No likelihood evaluations."""
import re, sys, numpy as np, pybobyqa, warnings
warnings.simplefilter('ignore')
txt = open('logs/step3A_fit2_ecf_mnufixed_s1.log').read()
g = np.array([float(v) for v in re.search(r'Approximate gradient = \[([^\]]*)\]', txt).group(1).split()])
H = np.array([float(v) for v in re.search(r'Approximate Hessian = \[\[(.*?)\]\]', txt, re.S).group(1).replace('[', ' ').replace(']', ' ').split()]).reshape(8, 8)
H = 0.5 * (H + H.T); w = np.linalg.eigvalsh(H)
print('Hessian eigenvalues:', np.round(w, 4))
if w.min() <= 0: H = H + (1e-3 - w.min()) * np.eye(8)
n = 8; lb = -50 * np.ones(n); ub = 50 * np.ones(n)
for noise in (0.0, 3e-5):
    for npt, up, lab in [((n + 1) * (n + 2) // 2, None, 'npt=45 (full)'), ((n + 1) * (n + 2) // 2 - 1, None, 'npt=44'),
                         (2 * n + 1, None, 'npt=17 (default)'),
                         ((n + 1) * (n + 2) // 2, {'restarts.use_restarts': True, 'restarts.use_soft_restarts': True,
                          'restarts.max_unsuccessful_restarts': 1, 'restarts.auto_detect': False}, 'npt=45 + soft restarts (max_unsucc 1)')]:
        rng = np.random.default_rng(1)
        f = lambda x: 981.88 + g @ x + 0.5 * x @ H @ x + (noise * rng.standard_normal() if noise else 0.0)
        r = pybobyqa.solve(f, np.zeros(n), bounds=(lb, ub), rhobeg=1.0, rhoend=0.005, npt=npt, maxfun=8000,
                           user_params=up, do_logging=False)
        xs = -np.linalg.solve(H, g); fs = 981.88 + 0.5 * g @ xs
        print(f'noise={noise:g} {lab:40s} flag={r.flag} nf={r.nf} nruns={r.nruns} f-f*={r.f - fs:.2e} msg={r.msg[:60]}')
