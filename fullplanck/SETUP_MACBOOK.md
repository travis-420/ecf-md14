# Full-likelihood run (kill condition 2) -- MacBook protocol

Open Claude Code in this folder and say: "Read SETUP_MACBOOK.md and execute it
step by step. Never proceed past a failed gate. Never fabricate output."

## Step 0 -- environment (~20 min, mostly downloads)
python3 -m venv venv && source venv/bin/activate
pip install cobaya camb numpy scipy
cobaya-install planck_2018_highl_plik.TTTEEE_lite_native bao.desi_dr2 sn.pantheonplus -p ./packages
(If bao.desi_dr2 is not a valid name in the installed cobaya, list options with
`cobaya-doc bao` and use the DESI DR2 entry. Plik-lite-native is the clik-free
Planck high-l likelihood; the tau prior in the yaml replaces low-l EE. Optional
upgrade later: full clik low-l likelihoods.)

## Step 1 -- GATE: physics validation (5 min). MUST PRINT PASS.
python test_module.py
This checks CAMB reproduces the original pipeline's expansion history for
tau = 1.5, 2.1, 3.0 to 0.3%. Differences to know about: reference uses
massless neutrinos (test does too); production chains use mnu=0.06 eV --
that is an intended upgrade, not a bug.

## Step 2 -- GATE: LCDM sanity chain (run first, overnight #1)
cobaya-run lcdm.yaml
Converged (R-1 < 0.02) means: compare marginalized means against published
Planck+DESI+SN LCDM: Om ~ 0.30-0.31, H0 ~ 67.5-68.5, ombh2 ~ 0.0224.
If these are off, STOP and debug the likelihood stack.

## Step 3 -- the contest (overnights #2, #3; can run in parallel on cores)
Build cpl_full.yaml and ecf_full.yaml per the merge notes, then:
cobaya-run cpl_full.yaml
cobaya-run ecf_full.yaml
Also run direct minimizations for clean delta-chi2 vs the compressed-prior run:
cobaya-run lcdm.yaml --minimize   (repeat for cpl, ecf)

## Step 4 -- what to bring back
- best-fit -logpost / chi2 for all three (minimize outputs)
- marginalized tau_ecf (mean, 68%) and w0/wa
- R-1 values proving convergence
Expected outcomes, pre-registered: if the compressed-prior result was faithful,
ECF's preference should hold or sharpen (published full-likelihood evolving-DE
preferences run ~3-4 sigma where compressed gave ~2.8). If the full likelihood
ERASES the preference, kill condition 2 fires and the note gets its honest update.
