import numpy as np
from scipy.integrate import solve_ivp, cumulative_trapezoid
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

Om0, Orad0, H0, sig8 = 0.315, 9.24e-5, 67.4, 0.81
c_km = 299792.458
OmDE = 1 - Om0 - Orad0

N = 4000
lna = np.linspace(np.log(1e-6), 0.0, N)
a = np.exp(lna); dx = lna[1]-lna[0]

def exp_conv(S, tau):
    # exact O(N) recursion for exponential memory kernel
    out = np.zeros(N); dec = np.exp(-dx/tau)
    for i in range(1, N):
        out[i] = dec*out[i-1] + 0.5*dx*(S[i] + S[i-1]*dec)
    return out

def w_of(shape):
    return -1 - np.gradient(np.log(np.maximum(shape,1e-300)), lna)/3

def E2_of(shape):
    return Om0*a**-3 + Orad0*a**-4 + OmDE*shape

def growth(E2_arr):
    dlnH = 0.5*np.gradient(np.log(E2_arr), lna)
    E2i = interp1d(lna, E2_arr, kind='cubic')
    dHi = interp1d(lna, dlnH, kind='cubic')
    x0 = np.log(1e-3)
    def rhs(x,y):
        D,Dp = y
        Omv = Om0*np.exp(-3*x)/E2i(x)
        return [Dp, -(2+dHi(x))*Dp + 1.5*Omv*D]
    xs_eval = lna[lna>=x0]
    sol = solve_ivp(rhs,[x0,0],[1e-3,1e-3],t_eval=xs_eval,rtol=1e-8,atol=1e-12)
    return sol.t, sol.y[0], sol.y[1]/sol.y[0]   # lna, D, f

def selfconsistent(tau, iters=4):
    E2 = E2_of(np.ones(N))
    Omar = Om0*a**-3/E2
    S = Omar**0.55 * Omar; S/=np.trapezoid(S,lna)
    shape = exp_conv(S,tau); shape/=shape[-1]
    w_first = w_of(shape).copy()
    for it in range(iters):
        E2 = E2_of(shape)
        xs,D,f = growth(E2)
        fg = np.empty(N); m = lna>=xs[0]-1e-12
        fg[m]=np.interp(lna[m],xs,f)
        Omar = Om0*a**-3/E2
        fg[~m]=Omar[~m]**0.55
        S = fg*Omar; S/=np.trapezoid(S,lna)
        new = exp_conv(S,tau); new/=new[-1]
        dw = np.max(np.abs(w_of(new)-w_of(shape))[a>0.1])
        shape = new
        if dw<1e-4: break
    return shape, w_first

def mu_of(shape):
    E = np.sqrt(E2_of(shape)); z = 1/a-1
    o = np.argsort(z); zs=z[o]
    Dc = cumulative_trapezoid(c_km/(H0*E[o]), zs, initial=0)
    dL = (1+zs)*Dc
    return zs, 5*np.log10(np.maximum(dL,1e-10))+25

def shape_CPL(w0,wa):
    return a**(-3*(1+w0+wa))*np.exp(-3*wa*(1-a))

def fit_cpl_to(shape):
    zt, mt = mu_of(shape)
    sel = (zt>=0.01)&(zt<=2.3)
    def model(z,w0,wa):
        zz,mm = mu_of(shape_CPL(w0,wa))
        return np.interp(z,zz,mm)
    p,_ = curve_fit(model, zt[sel], mt[sel], p0=[-0.8,-0.3])
    return p

def fs8(E2_arr, zpts):
    xs,D,f = growth(E2_arr)
    zz = 1/np.exp(xs)-1
    Dn = D/D[-1]
    fs = sig8*f*Dn
    return np.interp(zpts, zz[::-1], fs[::-1])

# ============ RUN ============
print("PART 1: Self-consistent ECF (tau=1) -- does the feedback loop matter?")
shape1, wfirst = selfconsistent(1.0)
w1 = w_of(shape1)
wi = interp1d(a, w1); wfi = interp1d(a, wfirst)
print(f"  w(z=0): first-pass {wfi(1.0):+.4f}  ->  self-consistent {wi(1.0):+.4f}")
print(f"  w(z=0.5): first-pass {wfi(1/1.5):+.4f}  ->  self-consistent {wi(1/1.5):+.4f}")

print("\nPART 2: Growth observable fs8(z): ECF vs its CPL mimic vs LCDM")
p_cpl = fit_cpl_to(shape1)
print(f"  CPL mimic of ECF(tau=1): w0={p_cpl[0]:+.3f}, wa={p_cpl[1]:+.3f}")
zpts = np.array([0.15,0.38,0.51,0.70,1.00,1.48])
fs_ecf  = fs8(E2_of(shape1), zpts)
fs_cpl  = fs8(E2_of(shape_CPL(*p_cpl)), zpts)
fs_lcdm = fs8(E2_of(np.ones(N)), zpts)
print(f"\n  {'z':>5} | {'ECF':>7} | {'CPL-mimic':>9} | {'LCDM':>7} | ECF-CPL % | ECF-LCDM %")
for i,z in enumerate(zpts):
    d1 = 100*(fs_ecf[i]-fs_cpl[i])/fs_cpl[i]
    d2 = 100*(fs_ecf[i]-fs_lcdm[i])/fs_lcdm[i]
    print(f"  {z:5.2f} | {fs_ecf[i]:7.4f} | {fs_cpl[i]:9.4f} | {fs_lcdm[i]:7.4f} | {d1:+8.3f}% | {d2:+8.2f}%")
print("\n  Current fs8 errors: ~3-8% per point. DESI-full/Euclid era: ~1-2% per bin.")

print("\nPART 3: The ECF locus in the (w0, wa) plane -- one parameter, one curve")
print(f"  {'tau':>5} | {'w0':>8} | {'wa':>8}")
locus=[]
for tau in [0.3,0.5,0.75,1.0,1.5,2.0,3.0,5.0]:
    sh,_ = selfconsistent(tau, iters=3)
    p = fit_cpl_to(sh)
    locus.append((tau,p[0],p[1]))
    print(f"  {tau:5.2f} | {p[0]:+8.3f} | {p[1]:+8.3f}")
print("\n  As tau -> infinity the locus terminates at LCDM (-1, 0).")
np.save('/home/claude/locus.npy', np.array(locus))
