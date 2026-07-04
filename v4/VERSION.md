# V4 — Cleaned/Extended Data (Paper-Faithful Baseline)

## What this version is
Same code as V3 (`run_experiment.py`, `model/generate_source_model.py` are byte-identical),
but run against cleaned/extended data: a corrected Galeão source series
(`model/source_data/`, now spanning 2017-2023) and an extended `data/` directory with
additional 2021-2023 ninja files (most notably 6 files for the "0 gera maranhao" station;
same 20 station folders as V3, 274 files vs V3's 160). This is treated as the paper-faithful
baseline for the rest of the V4→V6 iteration series (V4, V5 and V6 all share the exact same
`data/` and `model/source_data/` — verified with `diff -rq`, zero differences).

## Code delta vs V3
None (see `../v3/VERSION.md`). All differences vs V3 are data-only.

## Code delta vs V5 (its immediate neighbor going forward)
V5 fixes a data-leakage bug in the IQR-based outlier clipping: V4 computes the IQR bounds
on the **full** column (train + test), so outlier bounds are informed by data the model
will later be "tested" on. V5 computes them on the **training slice only**.

`run_experiment.py` (hourly pass, ~line 19, and daily pass, ~line 31):
```python
# V4:
quartiles = column.quantile([0.25, 0.75])

# V5:
train_col = column[:-8760] if len(column) > 8760 else column   # hourly pass
quartiles = train_col.quantile([0.25, 0.75])
...
train_col = column[:-365] if len(column) > 365 else column     # daily pass
quartiles = train_col.quantile([0.25, 0.75])
```
The identical change is applied in `model/generate_source_model.py`.

## Results summary (from `results_reference/sbpo_v3_results.csv`, n=20 stations)
- Mean Local MAPE: **11.782%**
- Mean Transfer MAPE: **12.632%**
- Mean Transfer Loss: **+0.850 pp**

See `../COMPARISON.md` for the full per-station table across V3–V6.

## Reproducibility extras
- `analysis/Transfer_Analysis.ipynb` — the plotting/analysis notebook for this version (reads
  `../results/sbpo_v3_results_with_similarities.csv`, so run `run_experiment.py` +
  `run_similarity.py` first). Byte-identical to the V3/V5/V6 copies.
- `data_prep/` — the six scripts that turned V3's raw data into V4's cleaned/extended `data/`
  and `model/source_data/` (verified byte-identical to the copies in `ROOT/v5` and `ROOT/v6`,
  so not duplicated there — V5 and V6 point back here since they share V4's data unchanged).
  See `data_prep/DATA_PREP.md` for what each script does and the order they were applied in.
- `docs_archive/` — historical write-ups first produced at V4 (new relative to V3) and carried
  forward unchanged through V6: `experiment_log.txt`, `similarity_log.txt`,
  `time-series-data-science-conformity-report.md`, `v4_experiment_results.md`,
  `v4_status_tag.md`.
- Data acquisition scripts live centrally in `../data_acquisition/` (identical across V3-V6).
