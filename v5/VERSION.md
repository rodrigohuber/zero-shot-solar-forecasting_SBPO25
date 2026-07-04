# V5 — Data-Leakage Fix (IQR Outlier Bounds on Training Slice Only)

## What this version is
Same data as V4 (`data/` and `model/source_data/` are identical to V4, verified with
`diff -rq`). The only change is a fix to how IQR outlier-clipping bounds are computed:
V4 computed bounds using the entire series (including the held-out test window), which
leaks test-set statistics into preprocessing. V5 computes the bounds using only the
training slice.

## Code delta vs V4
`run_experiment.py` (both the hourly outlier pass and the daily outlier pass):
```python
# V4:
quartiles = column.quantile([0.25, 0.75])

# V5:
train_col = column[:-8760] if len(column) > 8760 else column   # hourly: hold out last 8760 hrs (1yr)
quartiles = train_col.quantile([0.25, 0.75])
...
train_col = column[:-365] if len(column) > 365 else column     # daily: hold out last 365 days
quartiles = train_col.quantile([0.25, 0.75])
```
Identical fix applied in `model/generate_source_model.py` (used to build the frozen source
model itself, so the source model's own preprocessing is also leakage-free).

## Code delta vs V6 (its immediate neighbor going forward)
V6 expands the feature set used for training/prediction from the 4 physical features to
include 7 additional linear temporal features, to demonstrate that they cause overfitting
in zero-shot transfer:

`run_experiment.py` (~line 109 and ~line 120):
```python
# V5:
data = df[['TA', 'PR', 'GHI', 'NV']]
...
source_predictions = source_model.predict(test_data[['TA', 'PR', 'GHI', 'NV']])

# V6:
data = df[['TA', 'PR', 'GHI', 'NV', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear', 'dayofmonth', 'weekofyear']]
...
source_predictions = source_model.predict(test_data[['TA', 'PR', 'GHI', 'NV', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear', 'dayofmonth', 'weekofyear']])
```
Same change in `model/generate_source_model.py` (~line 99).

## Results summary (from `results_reference/sbpo_v3_results.csv`, n=20 stations)
- Mean Local MAPE: **11.825%** (+0.043 pp vs V4 — expected/honest: the model loses its
  "future knowledge" cheat code, so local error rises slightly but is now realistic)
- Mean Transfer MAPE: **12.719%** (+0.087 pp vs V4)
- Mean Transfer Loss: **+0.894 pp**

See `../COMPARISON.md` for the full per-station table across V3–V6.

## Reproducibility extras
- `analysis/Transfer_Analysis.ipynb` — the plotting/analysis notebook for this version (reads
  `../results/sbpo_v3_results_with_similarities.csv`, so run `run_experiment.py` +
  `run_similarity.py` first). Byte-identical to the V3/V4/V6 copies.
- Data preparation (V3→V4 raw-data cleanup) lives in `../v4/data_prep/` — V5 shares V4's
  `data/` and `model/source_data/` unchanged (verified with `diff -rq`), so no separate
  `data_prep/` copy exists here.
- `docs_archive/` — only `v5_experiment_log.txt` is archived here (version-specific log, kept
  with its own version by rule); the other historical write-ups (rio/galeao analysis, temporal
  divergence, experiment/similarity logs, conformity report, v4 status docs) are unchanged from
  V3/V4 and archived there instead — see `../v3/docs_archive/` and `../v4/docs_archive/`.
- Data acquisition scripts live centrally in `../data_acquisition/` (identical across V3-V6).
