# 16_kc5_ledger_update.py -- companion to KC5_LEDGER_UPDATE.md (Track A ledger).
# Locates Liepold & Ma 2024 (ApJL 971, L29) against the pre-registered
# coupled-Soltan KC5 window. The (1-eta)/eta prefactor is common to every
# accretion epoch, so the window rescales exactly. Standalone.
import numpy as np

f = lambda eta: (1 - eta) / eta
scale = lambda eta: f(eta) / f(0.1)
lo, hi, cen = 4.2e6, 5.2e6, 4.7e6            # pre-registered window at eta=0.1
LM, LMp, LMm = 1.8e6, 0.8e6, 0.5e6           # Liepold & Ma 2024

print("required window vs eta:")
for eta in [0.057, 0.1, 0.167, 0.2]:
    print(f"  eta={eta:5}: ({lo*scale(eta):.2e} - {hi*scale(eta):.2e})")

print("\ntension (sigma to reach window lower edge / center, upper error):")
for eta in [0.1, 0.2]:
    print(f"  eta={eta}: {(lo*scale(eta)-LM)/LMp:+.2f} / {(cen*scale(eta)-LM)/LMp:+.2f}")

def eta_for(rho, anchor):
    return 1 / (1 + rho / anchor * f(0.1))

print("\neta required for consistency:")
print(f"  L&M central vs window center: eta = {eta_for(LM, cen):.3f}")
print(f"  L&M 68% band vs window center: eta in "
      f"[{eta_for(LM+LMp, cen):.3f}, {eta_for(LM-LMm, cen):.3f}]")
print(f"  L&M 68% band vs window lower edge: eta in "
      f"[{eta_for(LM+LMp, lo):.3f}, {eta_for(LM-LMm, lo):.3f}]")
print("\npre-registered eta range [0.057, 0.2] -> overlap sliver eta ~ 0.15-0.20")
print("VERDICT: KC5 NOT FIRED; 3-sigma tension at fiducial eta=0.1;")
print("consistency lives at the top of the pre-registered efficiency range.")
