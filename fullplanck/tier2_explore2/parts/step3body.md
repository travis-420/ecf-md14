**Result.**

{{FILE:logs/tables_step3_summary.log}}

- **Failures:** none. All 16 base runs converged (`Run 1/1 converged`, Py-BOBYQA `EXIT_SUCCESS`), and no polish round
  failed (`EXIT_SUCCESS` in every round).
- **Fit 1:**
  - all 8 starts in the window;
  - **S = 0.0250** (total χ² 2005.4233–2005.4483);
  - −log-post spread 0.00012;
  - 1–2 polish rounds per start.
- **Fit 2:**
  - all 8 starts in the window;
  - **S = 0.1618** (total χ² 1994.0816–1994.2434);
  - −log-post spread 0.00241;
  - 1–5 polish rounds per start.
  - **Above the 0.1 target.** The same pattern as step 2: every start ended on the 0.001 rule (s6 only in its 5th
    round), with final −log post up to 0.0024 above the best start (s2, 981.86703) (`logs/stop_analysis.log`).
- **What the polish added over the base run alone** (`logs/tables_step3_base.log`):
  - fit 1: base S = 0.4371, polished 0.0250;
  - fit 2: base S in window = 0.9975 with 7/8 in the window (s2 was 0.3162 above the best), polished 0.1618 with 8/8.
- **Reproducibility check:** the base s0 runs start from the certified point with the same settings as session 2's
  s0, and reproduced session 2's s0 endpoints exactly: fit 1 986.0182 / 2005.5291, fit 2 981.8865 / 1993.9537.
- **Cost** (`logs/cost_step3.log`), base + polish:
  - **fit 1:** 1667 + 981 = 2648 evaluations, 257–426 per start;
  - **fit 2:** 3147 + 2370 = 5517 evaluations, 457–918 per start.
  - Wall times are in the tables; they are load-dependent.

**Base runs** (`scripts/tables2.py base`, `logs/tables_step3_base.log`):

{{FILE:logs/tables_step3_base.log}}

**Polish rounds** (`logs/tables_step3_polish.log`). Round 0 = the base endpoint.

{{FILE:logs/tables_step3_polish.log}}
