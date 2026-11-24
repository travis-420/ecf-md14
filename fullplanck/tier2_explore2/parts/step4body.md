**Result (CPL, Σmν fixed; not fit 5).**

{{FILE:logs/tables_step4_summary.log}}

- **Failures:** none.
  - All 8 base runs converged.
  - All 31 polish rounds ended "Success: rho has reached rhoend". Full npt here is 55 interpolation points.
  - So (ii) did not crash in 9 dimensions.
- **Agreement: poor.**
  - −log-post spread 0.0356; **S = 0.2812** (total χ² 1996.4597–1996.7409); 8/8 in the window.
  - Polishing improved on the base runs (base: spread 0.0750, S = 0.7107), but the starts did not converge together:
    - s5, s6 and s7 hit the 5-round cap while still gaining 0.0012–0.0079 per round;
    - s4 stopped on the 0.001 rule 0.0286 above the best start (s2, 982.78839).
  - In 9 dimensions, then, both the 0.001 per-round rule and the 5-round cap bind well before agreement.
- **Cost** (`logs/cost_step4.log`): base 2573 + polish 4419 = 6992 evaluations, 428–1182 per start. Polish: 2–5 rounds
  and 320–794 evaluations per start.

**Base runs** (`logs/tables_step4_base.log`):

{{FILE:logs/tables_step4_base.log}}

**Polish rounds** (`logs/tables_step4_polish.log`). Round 0 = the base endpoint.

{{FILE:logs/tables_step4_polish.log}}
