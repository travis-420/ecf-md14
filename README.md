If this is useful, cite: https://doi.org/10.5281/zenodo.21252690 (v1.0), https://doi.org/10.5281/zenodo.21269478 (full-Planck update), or the concept DOI https://doi.org/10.5281/zenodo.21252689 (always latest version).
# ECF-MD14: dark energy as a delayed response to cosmic structure formation

One-parameter phenomenological model (leaky integrator of the Madau-Dickinson
star-formation history) tested against DESI DR2 BAO + Pantheon+ SNe + Planck
2018 compressed distance priors. See NOTE.md for the full research note,
results, robustness diagnostics, and dated kill conditions.
VERIFICATION.md is an independent blind replication record: a separate
session, given the code but not the results, fetched the data and
reproduced every reported statistic exactly.

Headline: dchi2 = -11.64 vs LCDM with one parameter under the full Planck likelihood (plik-lite TTTEEE + tau prior + DESI DR2 BAO + Pantheon+); certified tau_ecf = 2.405 +0.87/-0.51 (68%, 6-chain MPI, R-1 = 0.019); beats the 2-parameter w0waCDM (dchi2 = -8.85) in every data block with one fewer parameter; first on AIC; BIC now favors the model over LCDM. ~3.4 sigma. Not a detection. Kill condition 2 executed: did not fire. Falsifiable by DESI final / Euclid. Full details in RESULTS_FULLPLANCK.md.

## Reproduce
Requirements: python 3.12+, numpy, scipy, pandas. Fetch data first:

  mkdir data && cd data
  curl -sL "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt" -o desi_dr2_mean.txt
  curl -sL "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt" -o desi_dr2_cov.txt
  curl -sL "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES.dat" -o pp.dat
  curl -sL "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES_STAT%2BSYS.cov" -o pp.cov

Then edit the /home/claude/gateb paths in the scripts to your data directory
and run in order 01 -> 05. Scripts 06-08 are the model-development stages
(one-parameter projection test, source scan incl. the FAILED linear-growth
variant, growth/fsigma8 degeneracy checks) kept for completeness.

IMPORTANT — one setup step: scripts 03, 04, and 09-12 bootstrap by executing
a file named gateb2.py, the pre-publication working name of
02_gateB2_cmb_anchor.py. Before running them, create the alias in your data
directory (or wherever you point the exec() paths):

  cp 02_gateB2_cmb_anchor.py <your-data-dir>/gateb2.py

Filename note: the scripts were renamed for publication after the blind
replication. VERIFICATION.md therefore refers to them by their original
working names — likelihood.py = 01_gateB_bao_sn.py, gateb2.py =
02_gateB2_cmb_anchor.py, prof2.py = 03_tau_profile.py, diag.py =
04_diagnostics.py. The code is identical; only the filenames changed.

Scripts 09-14 are the CCBH-identification chain documented in the NOTE.md
Addendum: 09 verifies the kernel/CCBH identity and measures k; 10 brackets
the required source decline; 11 tests the Shen et al. (2020) quasar
luminosity density source; 12 is the pre-registered X-ray-census source
test; 13 computes the coupled Soltan closure prediction (kill condition 5);
14 is the fsigma8 growth consistency check. Scripts 09-12 require the
gateb2.py alias above; 13 and 14 are standalone.

Runtime: minutes on one CPU. No data are redistributed here; everything is
fetched from the official public releases.

## License / citation
Timestamped research note, July 7, 2026. 
If this is useful, cite: https://doi.org/10.5281/zenodo.21252690 (v1.0), https://doi.org/10.5281/zenodo.21269478 (full-Planck update), or the concept DOI https://doi.org/10.5281/zenodo.21252689 (always latest version).
