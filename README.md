If this is useful, cite: https://doi.org/10.5281/zenodo.21252690 (v1.0) or the concept DOI https://doi.org/10.5281/zenodo.21252689 (always latest version).
# ECF-MD14: dark energy as a delayed response to cosmic structure formation

One-parameter phenomenological model (leaky integrator of the Madau-Dickinson
star-formation history) tested against DESI DR2 BAO + Pantheon+ SNe + Planck
2018 compressed distance priors. See NOTE.md for the full research note,
results, robustness diagnostics, and dated kill conditions.
VERIFICATION.md is an independent blind replication record: a separate
session, given the code but not the results, fetched the data and
reproduced every reported statistic exactly.

Headline: dchi2 = -7.6 vs LCDM with one parameter (tau = 2.1 +0.6/-0.4 e-folds);
beats the 2-parameter w0waCDM in absolute fit; first on AIC; ties LCDM on BIC.
~2.8 sigma. Not a detection. Falsifiable by DESI final / Euclid.

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

Runtime: minutes on one CPU. No data are redistributed here; everything is
fetched from the official public releases.

## License / citation
Timestamped research note, July 7, 2026. 
If this is useful, cite: https://doi.org/10.5281/zenodo.21252690 (v1.0) or the concept DOI https://doi.org/10.5281/zenodo.21252689 (always latest version).
