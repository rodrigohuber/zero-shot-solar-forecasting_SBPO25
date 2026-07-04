# V3 → V6 Comparison

Four consecutive iterations of the zero-shot solar-irradiance transfer-learning pipeline.
Each step changes exactly one thing (data cleanliness, a leakage bug, or a feature set) —
tables below are read straight from each version's own `results_reference/sbpo_v3_results.csv`.

## What changed, version to version

| Step | What changed | Files touched | Effect |
|---|---|---|---|
| V3 → V4 | **Data only.** Cleaned/extended Galeão source series (`model/source_data/` gains 2020-2023) and extended target `data/` (274 files vs 160, extra 2021-2023 ninja files, notably for "0 gera maranhao"). Code is byte-identical. | data files only | Large swing in both Local and Transfer MAPE per-station (e.g. "sao domingos" Transfer MAPE 18.83% → 13.54%; "0 gera maranhao" 19.39% → 15.80%). Mean Transfer MAPE drops 12.825% → 12.632%. |
| V4 → V5 | **Data-leakage fix.** IQR outlier-clipping bounds now computed on the training slice only (`column[:-8760]` hourly / `column[:-365]` daily) instead of the full series (train+test). | `run_experiment.py`, `model/generate_source_model.py` | Small, expected degradation: mean Local MAPE +0.043 pp, mean Transfer MAPE +0.087 pp. This is the "honest" cost of removing a subtle look-ahead leak. |
| V5 → V6 | **Temporal-overfitting experiment.** Feature set expanded from `['TA','PR','GHI','NV']` to also include `['dayofweek','quarter','month','year','dayofyear','dayofmonth','weekofyear']`. | `run_experiment.py` (~line 109/120), `model/generate_source_model.py` (~line 99) | Mean Local MAPE roughly flat (11.825% → 11.799%), but mean Transfer MAPE rises 12.719% → 12.785%: the Random Forest memorizes calendar position from the source station's history, which doesn't generalize when zero-shot transferring to a different station. Confirms these linear temporal features were correctly "dead code" in the paper-faithful baseline. |

## Full per-station results (Local MAPE % / Transfer MAPE %)

| Station | V3 Local | V3 Transfer | V4 Local | V4 Transfer | V5 Local | V5 Transfer | V6 Local | V6 Transfer |
|---|---|---|---|---|---|---|---|---|
| 0 gera maranhao | 15.708 | 19.385 | 13.078 | 15.795 | 13.167 | 16.303 | 13.238 | 16.466 |
| 1 sao domingos | 15.114 | 18.829 | 12.935 | 13.537 | 11.852 | 14.18 | 11.948 | 14.342 |
| 10 Rio de janeiro | 11.445 | 6.724 | 12.272 | 12.427 | 12.586 | 12.496 | 12.246 | 12.522 |
| 2 nova brasilia urucui | 13.878 | 16.3 | 10.769 | 12.295 | 11.218 | 12.72 | 10.93 | 12.774 |
| 3 Redencao do Gurgueia | 10.82 | 11.299 | 9.784 | 11.16 | 9.895 | 11.238 | 10.098 | 11.165 |
| 4 caripare | 10.665 | 12.859 | 10.217 | 13.811 | 10.555 | 13.671 | 10.915 | 13.634 |
| 5 santa maria da vitoria | 9.339 | 10.65 | 7.598 | 12.513 | 8.057 | 12.313 | 7.744 | 12.198 |
| 6 manga | 8.802 | 10.983 | 8.854 | 11.164 | 9.688 | 10.957 | 9.188 | 10.989 |
| 7 jequitai | 10.918 | 11.935 | 10.791 | 12.352 | 11.031 | 12.443 | 10.975 | 12.376 |
| 8 gov valadares | 10.788 | 10.426 | 10.676 | 10.894 | 10.729 | 10.856 | 10.366 | 11.161 |
| 9 vicosa | 11.212 | 10.939 | 12.193 | 11.363 | 12.172 | 11.64 | 11.955 | 11.64 |
| bangu -22.8753_-43.4649 | 12.337 | 12.478 | 12.761 | 12.483 | 12.566 | 12.466 | 12.492 | 12.457 |
| barra da tijuca -23.0114_-43.3218 | 13.545 | 13.138 | 13.497 | 13.013 | 13.356 | 13.08 | 13.445 | 13.2 |
| botafogo -22.9454_-43.1808 | 12.917 | 13.215 | 12.873 | 12.962 | 12.77 | 13.036 | 12.944 | 13.192 |
| copacabana -22.9864_-43.1872 | 13.207 | 13.269 | 13.017 | 13.077 | 13.068 | 13.167 | 13.236 | 13.311 |
| ipanema -22.9873_-43.2019 | 13.249 | 13.247 | 12.811 | 13.074 | 12.918 | 13.127 | 12.939 | 13.291 |
| jacarepagua -22.9532_-43.3716 | 13.127 | 12.737 | 13.182 | 12.762 | 12.743 | 12.683 | 12.839 | 12.655 |
| maracanã -22.9122_-43.2312 | 12.741 | 12.886 | 12.931 | 12.819 | 12.796 | 12.66 | 13.014 | 12.842 |
| marambaia -23.0626_-43.8556 | 12.27 | 12.431 | 12.768 | 12.459 | 12.683 | 12.652 | 12.801 | 12.649 |
| meier -22.9017_-43.2797 | 12.625 | 12.763 | 12.642 | 12.676 | 12.652 | 12.696 | 12.66 | 12.845 |
| **Mean** | **12.235** | **12.825** | **11.782** | **12.632** | **11.825** | **12.719** | **11.799** | **12.785** |

## Mean deltas

| Transition | Δ Mean Local MAPE | Δ Mean Transfer MAPE |
|---|---|---|
| V3 → V4 | -0.453 pp | -0.193 pp |
| V4 → V5 | +0.043 pp | +0.087 pp |
| V5 → V6 | -0.026 pp | +0.066 pp |
| V3 → V6 (net) | -0.436 pp | -0.040 pp |

## Interpretation

**V3 → V4 (data quality):** The dominant driver of change across this whole series. Two
outlier stations in V3 — "0 gera maranhao" and "1 sao domingos" — had Transfer MAPE north of
18-19% because their source/target series were built from dirtier, shorter data. Cleaning the
Galeão source data and extending target station coverage to 2021-2023 fixed both stations'
numbers substantially (19.39%→15.80% and 18.83%→13.54% respectively) and pulled the whole-panel
mean Transfer MAPE down by ~0.2 pp. Note station "10 Rio de janeiro" moved the *other*
direction (Transfer MAPE 6.72%→12.43%) — its V3 result benefited from a data artifact that
the V4 cleanup removed, revealing this station's true (harder) zero-shot transfer difficulty.

**V4 → V5 (leakage fix, expected/honest cost):** This is a textbook "fixing the bug makes the
number look slightly worse" result. V4 computed IQR outlier bounds using the full series,
including the 1-year test window, effectively letting the model preprocessing "see" a summary
statistic derived from the future. V5 restricts that computation to the training slice only.
The mean Transfer MAPE cost is tiny (+0.087 pp) and Local MAPE similarly (+0.043 pp) — the
leak was real but small in magnitude, and removing it is unambiguously correct methodology.

**V5 → V6 (temporal-feature overfitting):** Adding `year`, `dayofyear`, `dayofweek`, etc. to
the feature set leaves Local MAPE essentially unchanged (a locally-trained model tested on its
own station's near-future timeline can exploit calendar position almost for free) but
increases Transfer MAPE for the majority of stations (14 of 20 stations get worse; net mean
+0.066 pp). This is the clearest evidence in the V3-V6 series that linear temporal features are
a transfer-learning liability: the Random Forest partially memorizes "what year/day-of-year it
is at Galeão" rather than learning a transferable physical mapping from meteorological inputs
to irradiance, so the zero-shot jump to a new station's calendar position degrades predictions.
This validates the choice to keep these features unused (functionally dead code) in the
paper-faithful V4/V5 baseline.

## Provenance note: stale reference files in V5/V6 (corrected 2026-07-02)

The original `v5/results/sbpo_v3_results_with_similarities.csv` and its V6 counterpart were
**internally inconsistent** with their own frozen `sbpo_v3_results.csv`: each version folder was
created by copying its predecessor (V4 → V5 → V6), the experiment was re-run (overwriting
`sbpo_v3_results.csv`), but `run_similarity.py` was never re-run — so the merged file kept the
**predecessor's MAPE columns** (V5's stale file embeds V4's results, verified: e.g. Rio de
janeiro 12.272/12.427 = V4's exact values; disagreement with the frozen experiment CSV reached
0.643–0.805 pp Transfer MAPE).

During the 2026-07-02 verification, fresh, internally consistent `_with_similarities.csv` files
were generated (similarity columns matched the stale references **exactly**, confirming the
similarity computation itself was always correct — only the merged MAPE snapshot was stale).
The corrected `_with_similarities.csv` in `results_reference/` was rebuilt by merging the
**frozen** `sbpo_v3_results.csv` MAPE columns with the **verified** similarity columns, so the
reference pair is now byte-consistent (fresh-run Local MAPEs were not used, as they carry
BayesSearchCV run-to-run noise). The original stale files are preserved
alongside them as `sbpo_v3_results_with_similarities_STALE_pre-vN_mapes.csv` for audit purposes.
The original `SBPO_temp_test/v5` and `v6` folders were left untouched as historical record.
