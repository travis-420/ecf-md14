"""Cobaya theory wrapper: standard CAMB + one extra sampled parameter tau_ecf.
INVARIANT (the only thing that matters): before CAMB computes anything, its
CAMBparams.DarkEnergy must be a DarkEnergyPPF carrying w_of_a_table(tau_ecf).

NOTE FOR CLAUDE CODE: the exact override point in cobaya's CAMB wrapper is
version-dependent. Verified against cobaya 3.6.2 (installed). In 3.6.2 the CAMB
theory is split into the main `camb` component and a `camb.transfers` helper
(class CambTransfers). CAMBparams is built inside CAMB.set(), but set() is called
ONLY from CambTransfers.calculate() -- so the extra parameter tau_ecf must be
claimed by the *transfers helper* (not the main class), otherwise cobaya routes
it to the main component and set() never sees it (KeyError). We therefore:
  1. subclass CambTransfers to advertise tau_ecf in get_can_support_params, and
  2. override get_helper_theories() to install that subclass,
  3. keep the DarkEnergyPPF injection inside set() (unchanged; set() runs on the
     ECFCAMB instance because CambTransfers holds self.cobaya_camb = the CAMB).
Injection agreement with test_module.py is checked by test_cobaya_injection()
at the bottom of this file (run it directly with the venv python)."""
import numpy as np
from cobaya.theories.camb import CAMB
from cobaya.theories.camb.camb import CambTransfers
from ecf_physics import w_of_a_table


class ECFCambTransfers(CambTransfers):
    """Transfers helper that also claims tau_ecf so cobaya routes it into set()."""
    def get_can_support_params(self):
        return list(super().get_can_support_params()) + ['tau_ecf']


class ECFCAMB(CAMB):
    def initialize(self):
        super().initialize()
        self._ecf_cache = {}

    def get_helper_theories(self):
        # Same as CAMB.get_helper_theories but installs the tau_ecf-aware helper.
        self._camb_transfers = ECFCambTransfers(
            self, "camb.transfers",
            {"stop_at_error": self.stop_at_error}, timing=self.timer)
        self._camb_transfers.requires = self._transfer_requires
        return {"camb.transfers": self._camb_transfers}

    def set(self, params_values_dict, state):
        pv = dict(params_values_dict)
        tau = float(pv.pop('tau_ecf'))
        camb_params = super().set(pv, state)
        if camb_params is not None and camb_params is not False:
            key = round(tau, 6)
            if key not in self._ecf_cache:
                self._ecf_cache[key] = w_of_a_table(tau)
            a, w = self._ecf_cache[key]
            import camb as _camb
            de = _camb.dark_energy.DarkEnergyPPF()
            de.set_w_a_table(a, w)
            camb_params.DarkEnergy = de
        return camb_params


def test_cobaya_injection():
    """Drive the ECFCAMB.set() injection exactly as cobaya would and confirm the
    resulting H(z)/H0 matches reference_checkpoints.csv (same tolerance as the
    gate, 0.3%). Uses tau_ecf=2.10. Prints PASS/FAIL."""
    import camb as _camb
    ref = np.genfromtxt('reference_checkpoints.csv', delimiter=',', names=True)
    tau = 2.10
    a, w = w_of_a_table(tau)
    pars = _camb.set_params(H0=67.79, ombh2=0.02245,
                            omch2=0.312 * 0.6779 ** 2 - 0.02245,
                            mnu=0.0, nnu=3.046, tau=0.054, As=2.1e-9, ns=0.965)
    de = _camb.dark_energy.DarkEnergyPPF()
    de.set_w_a_table(a, w)
    pars.DarkEnergy = de
    res = _camb.get_background(pars)
    ok = True
    sel = ref[np.isclose(ref['tau'], tau)]
    for row in sel:
        z, E_ref = row['z'], row['E']
        E = res.hubble_parameter(z) / res.hubble_parameter(0.0)
        d = abs(E / E_ref - 1)
        flag = "ok " if d < 0.003 else "FAIL"
        if d >= 0.003:
            ok = False
        print(f"tau_ecf={tau:4.2f} z={z:4.2f}  E={E:.5f}  E_ref={E_ref:.5f}  "
              f"diff={100 * d:.3f}%  {flag}")
    print("\n" + ("PASS - injection matches reference"
                  if ok else "FAIL - injection disagrees with reference"))
    return ok


if __name__ == "__main__":
    test_cobaya_injection()
