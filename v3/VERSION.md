# V3 — Baseline Reproduction

## What this version is
The first standalone reproduction of the SBPO paper's zero-shot transfer-learning pipeline:
a Random Forest source model trained on Galeão (RJ) MERRA-2-derived features (`TA`, `PR`,
`GHI`, `NV`) is evaluated zero-shot against 20 target stations, and compared to a locally
trained (Bayesian-optimized) model per station.

V3 uses its own snapshot of source data (`model/source_data/`, MERRA years 2017-2019 for the
wind/weather pair used to build `source.pkl`) and its own `data/` snapshot (same 20 target
station folders as V4-V6, but with fewer years of ninja files per station — notably the
"0 gera maranhao" station is missing its 2021-2023 files).

## Code delta vs V4 (its immediate neighbor)
None. `run_experiment.py` and `model/generate_source_model.py` are byte-for-byte identical
between V3 and V4 (verified with `diff`). V3 and V4 differ **only in data**:

- V4's `model/source_data/` adds three extra years not present in V3's:
  `ninja_weather_2020.csv`, `ninja_weather_2021.csv`, `ninja_weather_2022.csv`,
  `ninja_weather_2023.csv`, `ninja_wind_2020.csv`, `ninja_wind_2021.csv`,
  `ninja_wind_2022.csv`, `ninja_wind_2023.csv` (cleaned Galeão source data).
- V4's `data/` adds extra 2021-2023 `ninja_weather`/`ninja_wind` files, most notably 6 files
  under the "0 gera maranhao" station folder (160 files in V3's `data/` vs 274 in V4's; the
  20 station folders themselves are the same in both versions).

That data-only change is what moved results between V3 and V4 — e.g. "sao domingos"
Transfer MAPE dropped from 18.83% (V3) to 13.54% (V4).

## Results summary (from `results_reference/sbpo_v3_results.csv`, n=20 stations)
- Mean Local MAPE: **12.235%**
- Mean Transfer MAPE: **12.825%**
- Mean Transfer Loss: **+0.590 pp** (transfer worse than local, on average)

See `../COMPARISON.md` for the full per-station table across V3–V6.

## Reproducibility extras
- `analysis/Transfer_Analysis.ipynb` — the plotting/analysis notebook for this version (reads
  `../results/sbpo_v3_results_with_similarities.csv`, so run `run_experiment.py` +
  `run_similarity.py` first). Byte-identical to the V4/V5/V6 copies.
- `docs_archive/` — historical write-ups first produced at V3 and carried forward unchanged
  through V6: `rio_vs_galeao_analysis.md`, `temporal_divergence_analysis.md`.
- Data acquisition scripts (`fetch_ninja.py`, `fetch_ninja_yearly.py`, `run_fetch_loop.py`,
  `validate_data.py`) live centrally in `../data_acquisition/` (identical across V3-V6).
