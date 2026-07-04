# V6 — "Dead-Code Overfitting" Experiment (Linear Temporal Features)

## What this version is
Same data as V4/V5 (`data/` and `model/source_data/` identical, verified with `diff -rq`).
The only change vs V5 is adding 7 linear temporal features (`dayofweek`, `quarter`, `month`,
`year`, `dayofyear`, `dayofmonth`, `weekofyear`) alongside the 4 physical features
(`TA`, `PR`, `GHI`, `NV`) used to train the Random Forest and to generate predictions from
the frozen source model. This deliberately reproduces feature code that existed but was
unused ("dead code") in earlier versions, to test its effect empirically.

## Code delta vs V5
`run_experiment.py` (~line 109, ~line 120):
```python
# V5:
data = df[['TA', 'PR', 'GHI', 'NV']]
source_predictions = source_model.predict(test_data[['TA', 'PR', 'GHI', 'NV']])

# V6:
data = df[['TA', 'PR', 'GHI', 'NV', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear', 'dayofmonth', 'weekofyear']]
source_predictions = source_model.predict(test_data[['TA', 'PR', 'GHI', 'NV', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear', 'dayofmonth', 'weekofyear']])
```
`model/generate_source_model.py` (~line 99) has the identical feature-set expansion, so the
frozen source model itself is trained with the year/day/etc. columns included.

## Interpretation
Injecting `year`, `dayofyear`, and friends lets the Random Forest memorize position-in-time
rather than learn the underlying physical relationship. In a **zero-shot transfer** setting
(source model applied to an unseen station/period) this hurts generalization because the
temporal coordinates the model memorized don't transfer — hence Transfer MAPE degrades
relative to V5 for nearly every station. Local models are trained and evaluated on the same
station's own timeline, so the effect on Local MAPE is smaller/mixed.

## Results summary (from `results_reference/sbpo_v3_results.csv`, n=20 stations)
- Mean Local MAPE: **11.799%** (essentially flat vs V5's 11.825%)
- Mean Transfer MAPE: **12.785%** (+0.066 pp vs V5 — transfer degrades as predicted)
- Mean Transfer Loss: **+0.986 pp** (the largest gap between local and transfer of V3–V6)

See `../COMPARISON.md` for the full per-station table across V3–V6.

## Reproducibility extras
- `analysis/Transfer_Analysis.ipynb` — the plotting/analysis notebook for this version (reads
  `../results/sbpo_v3_results_with_similarities.csv`, so run `run_experiment.py` +
  `run_similarity.py` first). Byte-identical to the V3/V4/V5 copies.
- Data preparation (V3→V4 raw-data cleanup) lives in `../v4/data_prep/` — V6 shares V4's
  `data/` and `model/source_data/` unchanged (verified with `diff -rq`), so no separate
  `data_prep/` copy exists here.
- `docs_archive/` — only `v6_experiment_log.txt` is archived here (version-specific log, kept
  with its own version by rule); the other historical write-ups are unchanged from earlier
  versions and archived there instead — see `../v3/docs_archive/`, `../v4/docs_archive/` and
  `../v5/docs_archive/` (which holds `v5_experiment_log.txt`).
- Data acquisition scripts live centrally in `../data_acquisition/` (identical across V3-V6).
