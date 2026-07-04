# Reproduction guide

Full detail for independently reproducing every result in this repository. For a quick start
see [README.md](README.md); for what changed between versions see [COMPARISON.md](COMPARISON.md)
and each `vN/VERSION.md`.

## What the pipeline does

A Random Forest "source" model is trained once on Galeão station (RJ) MERRA-2-derived
features (`TA`, `PR`, `GHI`, `NV` — air temperature, pressure, GHI, wind — resampled to daily
resolution). `run_experiment.py` then evaluates, for each of 20 target stations across Brazil:

- **Transfer**: the frozen Galeão source model applied zero-shot to the target station's own
  held-out test year.
- **Local**: a model trained directly (Bayesian-optimized) on that target station's own
  training data, evaluated on the same held-out test year.

`run_similarity.py` additionally computes geographic (Haversine), DTW and Catch22 time-series
similarity between each target station and the Galeão source, and merges them with the
`run_experiment.py` results.

## Structure

```
.
├── README.md              # slim landing page
├── REPRODUCTION.md        # this file
├── COMPARISON.md          # per-version results tables + why they differ
├── data_acquisition/      # shared raw-data fetch scripts (identical across V3-V6)
│   ├── fetch_ninja.py
│   ├── fetch_ninja_yearly.py    # main Renewables.ninja API puller, used by run_fetch_loop.py
│   ├── run_fetch_loop.py        # retry/backoff supervisor around fetch_ninja_yearly.py
│   ├── validate_data.py
│   └── data_fetch_validation_log.md
├── data/
│   ├── v3/                # V3's own data snapshot (20 stations, 160 files, ~77 MB)
│   └── v4-6/              # shared by V4, V5, V6 — verified byte-identical (20 stations, 274 files, ~132 MB)
├── paper/                 # paper full text (Markdown) + citation
├── docs/                  # zero-install HTML results showcase
├── v3/
│   ├── VERSION.md
│   ├── run_experiment.py
│   ├── run_similarity.py
│   ├── model/             # generate_source_model.py, compare_pkls.py, source.pkl,
│   │                        galeao_merra.pkl, source_data/ (V3's own Galeão source series)
│   ├── results_reference/ # frozen reference outputs (sbpo_v3_results.csv + _with_similarities.csv)
│   ├── analysis/          # Transfer_Analysis.ipynb (plotting/analysis notebook)
│   └── docs_archive/      # historical write-ups first produced at V3
├── v4/  (same shape, plus data_prep/ — the V3→V4 data-cleanup scripts)
├── v5/  (same shape, model/source_data/ identical to V4's; no data_prep/)
└── v6/  (same shape, model/source_data/ identical to V4's/V5's; no data_prep/)
```

`data/` is centralized because V4, V5 and V6 share an identical snapshot (`diff -rq` confirmed
zero differences); V3 has its own, smaller/older snapshot. Each version's `model/` is kept
per-version because it differs between V3 and V4-V6. `analysis/Transfer_Analysis.ipynb` is
byte-identical across versions but copied into each `vN/analysis/` because it reads the
relative path `../results/sbpo_v3_results_with_similarities.csv`.

## Setup

Create a fresh virtualenv and install the pinned dependencies (Python 3.12 recommended):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` pins the exact versions verified to reproduce `results_reference/`
bit-exactly (see **Verification** below). The core pipeline needs only the first block; the
analysis notebook additionally needs the notebook extras (`jupyter`, `nbconvert`, `ipykernel`,
`seaborn`, `folium`).

> **Regenerated outputs.** Each `vN/results/` folder, the `vN/*_verify.log` /
> `vN/sim_verify.log` files, and `vN/analysis/Transfer_Analysis_executed.ipynb` are *generated*
> by running the pipeline and are git-ignored — a fresh clone starts without them and the steps
> below recreate them. The **frozen expected values** you compare against live in
> `vN/results_reference/` (committed, never regenerated).

## Renewables.ninja API token

The raw-data fetch/prep scripts (`data_acquisition/` and `v4/data_prep/`) call the
[Renewables.ninja](https://www.renewables.ninja/) API, which requires a personal token. The
token shipped in these scripts is a **shared free-tier token obtained publicly** — provided
only so the fetch code runs out of the box; it is rate-limited and may be revoked at any time.
Before running any fetch/prep script: register (free) at
<https://www.renewables.ninja/register>, copy your token from
<https://www.renewables.ninja/profile>, and replace the `TOKEN = '...'` line at the top of the
script. **You do not need a token to reproduce the published results** — the fetched data is
already bundled under `data/`.

## Reproducing from scratch

The core run assumes `data/` and `model/` already contain the prepared CSVs/pickles that ship
here. To reproduce those inputs themselves — from a bare Renewables.ninja API pull to a
finished `Transfer_Analysis.ipynb` plot — run the following in order (venv from **Setup**).

1. **Data acquisition** (shared, produces the raw per-station `fetched-data/`):

   ```powershell
   cd data_acquisition
   ..\venv\Scripts\python.exe run_fetch_loop.py   # supervises fetch_ninja_yearly.py, retries hourly on HTTP 429
   ..\venv\Scripts\python.exe validate_data.py     # sanity-checks the fetched CSVs
   ```

   `fetch_ninja_yearly.py` hits the Renewables.ninja `weather` and `wind` endpoints (MERRA-2
   dataset) for each of the 20 target stations plus the Galeão `model/source_data/` series.
   V3's `data/v3` snapshot is the *earlier* state of this fetch (fewer years per station);
   `data/v4-6` is the later state after re-running the loop and merging new years (step 2) —
   the two `data/` folders are two snapshots in time of the same acquisition process, not two
   different sources.

2. **v3 → v4 data preparation** (v4/v5/v6 only — V3 skips this):

   ```powershell
   cd v4\data_prep
   ..\..\venv\Scripts\python.exe fix_galeao.py         # 1. backfill 2017-2019 Galeão source data
   ..\..\venv\Scripts\python.exe clean_galeao.py       # 2. normalize timestamps/columns
   ..\..\venv\Scripts\python.exe fix_galeao_wind.py    # 3. re-fetch+clean raw wind for 2017-2019
   ..\..\venv\Scripts\python.exe fix_maracana.py       # 4. backfill Maracanã target station
   ..\..\venv\Scripts\python.exe fix_clean.py          # 5. final timestamp-format pass
   ..\..\venv\Scripts\python.exe merge_data.py         # 6. merge fetched-data/ into data/
   ```

   See `v4/data_prep/DATA_PREP.md` for what each script transforms. V5 and V6 inherit this
   prepared data unchanged (verified with `diff -rq`), so they never re-run this step.

3. **Generate the frozen source model** — see "Rebuilding the frozen source model" below.

4. **Run the experiment and similarity pipeline** — see "Running each version" below.

5. **Analysis notebook** — open `vN/analysis/Transfer_Analysis.ipynb` (Jupyter, same venv as
   kernel) and run all cells. It reads `../results/sbpo_v3_results_with_similarities.csv` via a
   relative path, so open it with its own `vN/analysis/` as the working directory. Step 4 must
   have completed for that version first.

## Running each version

Working directory is the version folder itself (activate the venv, or call its python
directly).

### V3

```powershell
cd v3
python run_experiment.py --data_dir ..\data\v3 --model_path .\model\source.pkl --out_dir .\results
```

### V4, V5, V6 (identical shape — only the folder changes)

```powershell
cd v4      # or v5, or v6
python run_experiment.py --data_dir ..\data\v4-6 --model_path .\model\source.pkl --out_dir .\results
```

Compare the fresh `.\results\sbpo_v3_results.csv` against `.\results_reference\sbpo_v3_results.csv`.

`run_experiment.py` CLI flags (all optional; defaults shown):
- `--data_dir` (`./data`) — directory containing the target station subfolders.
- `--model_path` (`./model/source.pkl`) — frozen source model to evaluate zero-shot.
- `--out_dir` (`./results`) — where to write `sbpo_v3_results.csv`.

### Rebuilding the frozen source model (optional, per version)

`model/generate_source_model.py` has no CLI flags: it reads `<script_dir>/source_data/` and
writes `<script_dir>/source.pkl`.

```powershell
cd v4\model      # or v3, v5, v6
python generate_source_model.py
```

Optionally audit against the frozen `galeao_merra.pkl` with `python compare_pkls.py` from
inside the same `model/` folder.

### Running run_similarity.py

`run_similarity.py` has **no CLI flags** — it hardcodes three relative paths from its current
working directory: `./data`, `./model/source_data`, and `./results/sbpo_v3_results.csv` (reads
the last, writes `./results/sbpo_v3_results_with_similarities.csv`). Because `data/` is
centralized under `data/` rather than duplicated per version, provide a `data` directory (or
junction) next to the script first:

**Option A — junction (recommended, no duplicate copy):**

```powershell
cd v4                                        # or v3, v5, v6
New-Item -ItemType Junction -Path .\data -Target ..\data\v4-6    # ..\data\v3 for the v3 folder
python run_similarity.py
Remove-Item .\data                           # clean up the junction, optional
```

**Option B** — run `run_experiment.py` first so `./results/sbpo_v3_results.csv` exists, then
run Option A's junction + `run_similarity.py` step.

`run_similarity.py` requires `pycatch22` and `dtaidistance`.

## Dependencies

All dependencies with exact, reproduction-verified pins are in **`requirements.txt`**
(`pip install -r requirements.txt`). Core pipeline: `pandas`, `numpy`, `scipy`,
`scikit-learn`, `scikit-optimize`, `joblib`, `pycatch22`, `dtaidistance`. Analysis-notebook
extras: `matplotlib`, `seaborn`, `folium`, `jupyter`, `nbconvert`, `ipykernel`.

## Verification

All four versions were re-run end-to-end from this folder and compared against
`results_reference/` (fresh Python 3.12.9 venv, pins as in `requirements.txt`). Note:
`v3/model/source.pkl` was pickled under scikit-learn 1.9.0 (unpickling under 1.3.2 emits
`InconsistentVersionWarning`); despite the warning, v3's Transfer numbers reproduce exactly.

**Results vs `results_reference/` (20/20 stations each):**

| Version | Transfer_MAPE_% max abs diff | Local_MAPE_% max abs diff | Similarity cols (Geo/Catch22/DTW/Lat/Lon) max abs diff |
|---|:--:|:--:|:--:|
| v3 | **0.0 (exact)** | 1.360 | **0.0 (exact)** |
| v4 | **0.0 (exact)** | 1.392 | **0.0 (exact)** |
| v5 | **0.0 (exact)** | 1.039 | **0.0 (exact)** |
| v6 | **0.0 (exact)** | 0.263 | **0.0 (exact)** |

**Verdict: PASS for all four versions** on everything deterministic — Transfer MAPE (frozen
source model) and all similarity columns reproduce bit-exactly.

**Local MAPE is inherently non-deterministic**, not an environment issue: `BayesSearchCV` in
`run_experiment.py` is constructed without a `random_state` (only the inner
`RandomForestRegressor(random_state=42)` is seeded), so the Bayesian search samples differently
each run. Two identical back-to-back v3 runs differed by up to 1.525 in Local_MAPE_% — the
reference deviations above are within this run-to-run noise band.

**Known reference inconsistency (v5, v6).** The frozen
`results_reference/sbpo_v3_results_with_similarities.csv` for v5 and v6 embeds MAPE columns
from an *older* run than the frozen `results_reference/sbpo_v3_results.csv` in the same folder
(the two disagree on Transfer_MAPE_% by up to 0.643 for v5 and 0.805 for v6; v3 and v4 are
internally consistent). Comparison of the `_with_similarities.csv` for v5/v6 is therefore
meaningful only on the similarity columns — which match exactly. The superseded copies are kept
as `*_STALE_pre-vN_mapes.csv` for transparency.

**Output-dir note.** `run_experiment.py` and `run_similarity.py` create their output directory
automatically; a fresh clone with no `results/` folder runs cleanly.

### Transfer_Analysis.ipynb execution test

`jupyter nbconvert --to notebook --execute` was run on the byte-identical
`vN/analysis/Transfer_Analysis.ipynb` for all four versions. Each reads exactly one input,
`../results/sbpo_v3_results_with_similarities.csv`. Imports: `folium`, `matplotlib`, `numpy`,
`pandas`, `seaborn`, `scipy.stats`. No files are written except the executed-notebook copy.

| Version | Result | Cells | Error outputs |
|---|---|:--:|:--:|
| v3 | PASS | 18 | 0 |
| v4 | PASS | 18 | 0 |
| v5 | PASS | 18 | 0 |
| v6 | PASS | 18 | 0 |
