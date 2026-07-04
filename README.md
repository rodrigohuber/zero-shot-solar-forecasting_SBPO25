# SBPO Solar-Irradiance Transfer-Learning Pipeline — V3-V6 (Pruned, Standalone)

This folder is a pruned, standalone copy of versions V3, V4, V5 and V6 of the zero-shot
transfer-learning pipeline evaluated in the SBPO paper. It contains only what is needed to
independently re-run each version's experiment and reproduce its published results — all the
exploratory/fix/fetch scripts, logs, notebooks and per-version READMEs from the original
working folders have been left behind. See `COMPARISON.md` for what changed between versions
and why the results differ, and each `vN/VERSION.md` for the version-specific code delta.

📄 **Paper:** *Exploring Transfer Learning Techniques for Solar Irradiation Forecast across
Geographically Diverse Locations in Brazil Using Reanalysis Data* (Mendes, Baião & Souza,
SBPO 2025) — [official publication](https://proceedings.science/sbpo/sbpo-2025/trabalhos/exploring-transfer-learning-techniques-for-solar-irradiation-forecast-across-geo?lang=pt-br)
· [full text (Markdown)](paper/SBPO2025_transfer-learning-solar-forecasting.md) · [citation](paper/README.md)

> ### ⚠️ Renewables.ninja API token — register your own before fetching data
>
> The raw-data fetch/prep scripts (`data_acquisition/` and `v4/data_prep/`) call the
> [Renewables.ninja](https://www.renewables.ninja/) API, which requires a personal API token.
> The token shipped in these scripts is a **shared free-tier token obtained publicly** — it is
> provided only so the fetch code is runnable out of the box, is rate-limited, and may be
> revoked or throttled at any time. **Before running any data-acquisition or data-prep script,
> create your own account and use your own token:**
>
> 1. Register (free) at <https://www.renewables.ninja/register>.
> 2. Copy your personal API token from your profile page
>    (<https://www.renewables.ninja/profile>).
> 3. Replace the `TOKEN = '...'` line at the top of the relevant script with your own token.
>
> **You do not need a token to reproduce the published results** — the fetched data is already
> bundled under `data/`. The token is only needed if you want to re-run the fetch from scratch.

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

## Results showcase (no install required)

Want to see the results without running anything? Two options:

- **Rendered HTML** — open [`docs/index.html`](docs/index.html), which links a static,
  zero-install render of each version's analysis (`docs/v3.html` … `docs/v6.html`).
- **Executed notebooks** — each `vN/analysis/Transfer_Analysis_executed.ipynb` is committed
  with its plots, tables and maps already rendered, viewable directly on GitHub.

To regenerate them yourself, follow the run steps below and re-execute
`vN/analysis/Transfer_Analysis.ipynb`.

## Structure

```
v3-6/
├── README.md              # this file
├── COMPARISON.md          # per-version results tables + why they differ
├── data_acquisition/      # shared raw-data fetch scripts (identical across V3-V6)
│   ├── fetch_ninja.py
│   ├── fetch_ninja_yearly.py    # main Renewables.ninja API puller, used by run_fetch_loop.py
│   ├── run_fetch_loop.py        # retry/backoff supervisor around fetch_ninja_yearly.py
│   ├── validate_data.py
│   └── data_fetch_validation_log.md
├── data/
│   ├── v3/                # V3's own data snapshot (20 stations, 160 files, ~77 MB)
│   └── v4-6/               # shared by V4, V5, V6 — verified byte-identical across the three
│                            # (20 stations, 274 files, ~132 MB)
├── v3/
│   ├── VERSION.md
│   ├── run_experiment.py
│   ├── run_similarity.py
│   ├── model/              # generate_source_model.py, compare_pkls.py, source.pkl,
│   │                        # galeao_merra.pkl, source_data/ (V3's own Galeão source series)
│   ├── results_reference/  # frozen reference outputs (sbpo_v3_results.csv + _with_similarities.csv)
│   ├── analysis/            # Transfer_Analysis.ipynb (plotting/analysis notebook)
│   └── docs_archive/        # historical write-ups first produced at V3 (see dedup note below)
├── v4/  (same shape, model/source_data/ is V4's cleaned/extended Galeão series, plus
│        data_prep/ — the V3→V4 data-cleanup scripts — and its own docs_archive/)
├── v5/  (same shape, model/source_data/ identical to V4's; no data_prep/ — see v5/VERSION.md)
└── v6/  (same shape, model/source_data/ identical to V4's/V5's; no data_prep/ — see v6/VERSION.md)
```

Each version's `data/` (station folders) lives centrally under `v3-6/data/` because V4, V5
and V6 share an identical data snapshot (`diff -rq` confirmed zero differences) — no need to
store it three times. V3 has its own, smaller/older snapshot. Each version's `model/` folder
(including `model/source_data/`, the Galeão-only series used to build the frozen source model)
is kept per-version because it differs between V3 and V4-V6.

`analysis/Transfer_Analysis.ipynb` is byte-identical across all four versions but is still
copied into each `vN/analysis/` (rather than centralized) because it reads a *relative* path,
`../results/sbpo_v3_results_with_similarities.csv` — it must sit next to that version's own
`results/` folder to pick up that version's own numbers.

`docs_archive/` files are deduplicated: each historical log/write-up is archived once, in the
earliest version whose folder had it (`rio_vs_galeao_analysis.md` and
`temporal_divergence_analysis.md` first appear at V3; `experiment_log.txt`,
`similarity_log.txt`, `time-series-data-science-conformity-report.md`,
`v4_experiment_results.md` and `v4_status_tag.md` first appear at V4 and were carried forward
byte-identical through V6). The one exception is `vN_experiment_log.txt`, which is genuinely
version-specific and always stays with its own version (`v5/docs_archive/v5_experiment_log.txt`,
`v6/docs_archive/v6_experiment_log.txt`).

## Setup

This is a self-contained bundle — create a fresh virtualenv and install the pinned
dependencies from `requirements.txt` (Python 3.12 recommended):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` pins the exact versions verified to reproduce `results_reference/`
bit-exactly (see **Verification** below). The core pipeline (`run_experiment.py`,
`run_similarity.py`) needs only the first block; the analysis notebook
(`vN/analysis/Transfer_Analysis.ipynb`) additionally needs the notebook extras listed at the
bottom of `requirements.txt` (`jupyter`, `nbconvert`, `ipykernel`, `seaborn`, `folium`).

> **Note on regenerated outputs.** Each `vN/results/` folder, the `vN/*_verify.log` /
> `vN/sim_verify.log` files, and `vN/analysis/Transfer_Analysis_executed.ipynb` are *generated*
> by running the pipeline and are git-ignored — a fresh clone starts without them and the steps
> below recreate them. The **frozen expected values** you compare against live in
> `vN/results_reference/` (committed, never regenerated).

## Reproducing from scratch

The sections below ("How to run each version end-to-end") assume `data/` and `model/` already
contain the prepared CSVs/pickles that ship in this folder. To reproduce those inputs
themselves — i.e. go all the way from a bare Renewables.ninja API pull to a finished
`Transfer_Analysis.ipynb` plot — run the following in order. Every command assumes the venv
from **Setup** above and a working directory as shown.

1. **Data acquisition** (shared, produces the raw per-station `fetched-data/` used to build
   both `data/v3` and `data/v4-6`):

   ```powershell
   cd v3-6\data_acquisition
   ..\..\venv\Scripts\python.exe run_fetch_loop.py   # supervises fetch_ninja_yearly.py, retries hourly on HTTP 429
   ..\..\venv\Scripts\python.exe validate_data.py     # sanity-checks the fetched CSVs
   ```

   `fetch_ninja_yearly.py` hits the Renewables.ninja `weather` and `wind` endpoints
   (`https://www.renewables.ninja/api/data/{weather,wind}`, MERRA-2 dataset) for each of the 20
   target stations plus the Galeão `model/source_data/` series, and writes results under a
   local `fetched-data/<station>/` tree. It carries a **hardcoded API token** in the script
   (`TOKEN = '...'`) — this is a shared free-tier token (see the disclaimer at the top of this
   README); register at Renewables.ninja and swap in your own token before running. Output naming follows
   `ninja_{weather,wind}_<lat>_<lon>_uncorrected <YY>.csv`. V3's `data/v3` snapshot is the
   *earlier* state of this fetch (fewer years per station, e.g. "0 gera maranhao" missing
   2021-2023); `data/v4-6` is what you get after re-running the fetch loop later and merging
   the new years in (step 2 below) — the two `data/` folders in this repo are just two
   snapshots in time of the same acquisition process, not two different sources.

2. **v3 → v4 data preparation** (v4/v5/v6 only — V3 skips this):

   ```powershell
   cd v3-6\v4\data_prep
   # each script's paths are relative to a working copy of the v4-era `data/` and
   # `model/source_data/` — read DATA_PREP.md before running any of them standalone.
   ..\..\..\venv\Scripts\python.exe fix_galeao.py         # 1. backfill 2017-2019 Galeão source data
   ..\..\..\venv\Scripts\python.exe clean_galeao.py        # 2. normalize timestamps/columns
   ..\..\..\venv\Scripts\python.exe fix_galeao_wind.py     # 3. re-fetch+clean raw wind for 2017-2019
   ..\..\..\venv\Scripts\python.exe fix_maracana.py        # 4. backfill Maracanã target station
   ..\..\..\venv\Scripts\python.exe fix_clean.py           # 5. final timestamp-format pass
   ..\..\..\venv\Scripts\python.exe merge_data.py           # 6. merge fetched-data/ into data/
   ```

   See `v3-6\v4\data_prep\DATA_PREP.md` for what each script transforms and why. V5 and V6
   inherit this prepared data unchanged (verified with `diff -rq`), so they never re-run this
   step — they just point back at `v4/data_prep/`.

3. **Generate the frozen source model** — see "Rebuilding the frozen source model" below
   (`model/generate_source_model.py`, per version).

4. **Run the experiment and similarity pipeline** — see "How to run each version end-to-end"
   and "Running `run_similarity.py`" below (`run_experiment.py` then `run_similarity.py`, per
   version).

5. **Analysis notebook** — open `vN/analysis/Transfer_Analysis.ipynb` (Jupyter/JupyterLab,
   using the same venv as a kernel) and run all cells. It reads
   `../results/sbpo_v3_results_with_similarities.csv` via a relative path, so it must be opened
   with its own `vN/analysis/` as the working directory (the default when Jupyter opens a
   notebook in place) — do not move it elsewhere without also moving/symlinking `results/`
   alongside it. Step 4 must have completed for that version first.

### Completeness note

This bundle intentionally omits a few things from the original `ROOT/vN` working folders,
because they're either secrets, redundant, or working-directory clutter rather than pipeline
inputs/outputs:

- **`tokens.log`** (per version) — a local LLM API token-usage ledger from the original
  authoring sessions; not part of the reproducible pipeline.
- **Each `ROOT/vN/README.md`** — superseded by this bundle's own `README.md` +
  `COMPARISON.md` + per-version `VERSION.md`; the originals described the *working* folder
  layout (which included many one-off/exploratory scripts not carried into `v3-6/`), not this
  pruned one.
- **`fetched-data/`** (per version, in `ROOT/vN`) — the raw, unmerged fetch output before
  `merge_data.py` folds it into `data/`; not needed once `data/` itself is present, and
  regenerated by re-running `data_acquisition/run_fetch_loop.py` if you want it back.

Nothing else was left out: every script that participates in data acquisition, data
preparation, model generation, experiment execution, similarity computation, or analysis is
present somewhere in this bundle (either per-version or centralized where identical).

## How to run each version end-to-end

All commands below assume your working directory is the version folder itself
(e.g. `v3-6\v4\`) and that you use the existing venv's python
(`..\..\venv\Scripts\python.exe`, or activate the venv first and just call `python`).

### V3

```powershell
cd v3-6\v3
..\..\..\venv\Scripts\python.exe run_experiment.py --data_dir ..\data\v3 --model_path .\model\source.pkl --out_dir .\results
```

Fresh output lands in `v3-6\v3\results\sbpo_v3_results.csv` — diff it against
`v3-6\v3\results_reference\sbpo_v3_results.csv` to verify reproduction.

### V4, V5, V6 (identical invocation shape — only the folder changes)

```powershell
cd v3-6\v4      # or v5, or v6
..\..\..\venv\Scripts\python.exe run_experiment.py --data_dir ..\data\v4-6 --model_path .\model\source.pkl --out_dir .\results
```

Compare the fresh `.\results\sbpo_v3_results.csv` against `.\results_reference\sbpo_v3_results.csv`.

`run_experiment.py` CLI flags (all optional, shown with their defaults):
- `--data_dir` (default `./data`) — directory containing the target station subfolders.
- `--model_path` (default `./model/source.pkl`) — frozen source model to evaluate zero-shot.
- `--out_dir` (default `./results`) — where to write `sbpo_v3_results.csv`.

### Rebuilding the frozen source model (optional, per version)

`model/generate_source_model.py` has no CLI flags: it always reads
`<script_dir>/source_data/` and always writes `<script_dir>/source.pkl`. Since each version's
`model/source_data/` was copied in place, this works unmodified:

```powershell
cd v3-6\v4\model      # or v3, v5, v6
..\..\..\..\venv\Scripts\python.exe generate_source_model.py
```

Then optionally audit against the frozen `galeao_merra.pkl` with `python compare_pkls.py`
(from inside the same `model/` folder — read that script for its own expected invocation if
you use it, it wasn't modified as part of this pruning).

### Running `run_similarity.py`

`run_similarity.py` has **no CLI flags** — it hardcodes three relative paths from its own
current working directory: `./data`, `./model/source_data`, and
`./results/sbpo_v3_results.csv` (it reads the last one and writes
`./results/sbpo_v3_results_with_similarities.csv`). Because this folder centralizes `data/`
under `v3-6/data/` instead of duplicating it inside each version folder, you need a `data`
directory (or junction) next to the script before running it. Two options:

**Option A — junction (recommended, no duplicate copy):**

```powershell
cd v3-6\v4                                   # or v3, v5, v6
New-Item -ItemType Junction -Path .\data -Target ..\data\v4-6    # use ..\data\v3 for the v3 folder
..\..\..\venv\Scripts\python.exe run_similarity.py
Remove-Item .\data                            # clean up the junction when done, optional
```

**Option B — run `run_experiment.py` first** so `./results/sbpo_v3_results.csv` exists (see
above), then run Option A's junction + `run_similarity.py` step to produce
`./results/sbpo_v3_results_with_similarities.csv`.

Note `run_similarity.py` requires `pycatch22` and `dtaidistance` in addition to the base
dependencies listed above.

## Dependencies

All dependencies with exact, reproduction-verified version pins are in **`requirements.txt`**
(`pip install -r requirements.txt`). Core pipeline: `pandas`, `numpy`, `scipy`,
`scikit-learn`, `scikit-optimize`, `joblib`, `pycatch22`, `dtaidistance`. Analysis-notebook
extras (only needed for `Transfer_Analysis.ipynb`): `matplotlib`, `seaborn`, `folium`,
`jupyter`, `nbconvert`, `ipykernel`.

## Verifying file counts against source

The data copies were verified against the original working folders at build time:

| Copy | Files | Source |
|---|---|---|
| `v3-6/data/v3` | 160 | `ROOT/v3/data` (160) |
| `v3-6/data/v4-6` | 274 | `ROOT/v4/data` (274) |
| `v3-6/v3/model` | 12 | `ROOT/v3/model` (12) |
| `v3-6/v4/model` | 18 | `ROOT/v4/model` (18) |
| `v3-6/v5/model` | 18 | `ROOT/v5/model` (18) |
| `v3-6/v6/model` | 18 | `ROOT/v6/model` (18) |

## Verification

**Date:** 2026-07-01. All four versions were re-run end-to-end from this folder and compared
against `results_reference/`. Full logs are kept per version as `vN/run_verify.log`
(experiment) and `vN/sim_verify.log` (similarity).

**Environment.** A fresh Python 3.12.9 venv was created with packages pinned to the original
venv's versions: `scikit-learn==1.3.2`, `numpy==1.26.4`,
`pandas==3.0.3`, `scikit-optimize==0.10.2`, `joblib==1.5.3`, `dtaidistance==2.4.0`,
`pycatch22==0.4.5` (scipy 1.17.1). Note: `v3/model/source.pkl` was pickled under
scikit-learn 1.9.0 (unpickling under 1.3.2 emits `InconsistentVersionWarning`), while
v4/v5/v6's `source.pkl` were pickled under 1.3.2; despite the warning, v3's Transfer numbers
reproduced exactly.

**Commands run (per version, from inside `vN\`):**

```powershell
python run_experiment.py --data_dir ..\data\v3 --model_path .\model\source.pkl --out_dir .\results   # v3
python run_experiment.py --data_dir ..\data\v4-6 --model_path .\model\source.pkl --out_dir .\results  # v4/v5/v6
python run_similarity.py   # via a scaffold dir with junctions (see caveat below)
```

**Results vs `results_reference/` (20/20 stations each):**

| Version | Experiment runtime | Transfer_MAPE_% max abs diff | Local_MAPE_% max abs diff | Similarity runtime | Similarity cols (Geo/Catch22/DTW/Lat/Lon) max abs diff |
|---|---|---|---|---|---|
| v3 | 116 s | **0.0 (exact)** | 1.360 | 11 s | **0.0 (exact)** |
| v4 | 185 s | **0.0 (exact)** | 1.392 | 14 s | **0.0 (exact)** |
| v5 | 182 s | **0.0 (exact)** | 1.039 | 13 s | **0.0 (exact)** |
| v6 | 242 s | **0.0 (exact)** | 0.263 | 13 s | **0.0 (exact)** |

**Verdict: PASS for all four versions** on everything that is deterministic — Transfer MAPE
(frozen source model) and all similarity columns reproduce bit-exactly.

**Local MAPE is inherently non-deterministic**, not an environment issue: `BayesSearchCV` in
`run_experiment.py` is constructed without a `random_state` (only the inner
`RandomForestRegressor(random_state=42)` is seeded), so the Bayesian hyperparameter search
samples differently on every run. Two identical back-to-back v3 runs in the same environment
differed by up to 1.525 in Local_MAPE_% — the ≤1.392 deviations from the reference are within
this run-to-run noise band.

**Known reference inconsistency (v5, v6).** The frozen
`results_reference/sbpo_v3_results_with_similarities.csv` for v5 and v6 embeds MAPE columns
from an *older* experiment run than the frozen `results_reference/sbpo_v3_results.csv` in the
same folder (the two reference files disagree with each other on Transfer_MAPE_% by up to
0.643 for v5 and 0.805 for v6; v3 and v4 references are internally consistent). Comparison of
the `_with_similarities.csv` for v5/v6 is therefore meaningful only on the similarity columns
— which match exactly.

**Fixes / workarounds applied (no pipeline logic was changed):**

1. `run_experiment.py` does not create `--out_dir`; the `results\` folder must exist or the
   final `to_csv` fails with `OSError: Cannot save file into a non-existent directory`.
   Fix: `mkdir results` inside each version folder before running (folders now exist).
2. The junction workaround documented above (`New-Item -ItemType Junction -Path .\data ...`)
   **fails on this Google Drive-backed filesystem** (`New-Item : Incorrect function`).
   Workaround used for `run_similarity.py`: build a small scaffold directory on a local NTFS
   drive containing an unmodified copy of `run_similarity.py`, junctions `data` →
   `v3-6\data\<v3|v4-6>` and `model\source_data` → `v3-6\vN\model\source_data` (junctions
   created *on local NTFS* pointing *into* Google Drive work fine), plus `results\` seeded
   with the fresh `sbpo_v3_results.csv`; run from the scaffold, then copy
   `sbpo_v3_results_with_similarities.csv` back into `vN\results\`. If this folder is ever
   moved to a local NTFS drive, the original junction recipe works as documented.

### Transfer_Analysis.ipynb execution test (2026-07-02)

Ran `jupyter nbconvert --to notebook --execute` on the byte-identical
`vN\analysis\Transfer_Analysis.ipynb` for all four versions, directly on this Google Drive
path (no locking issues encountered, no local-scratch fallback needed). Reused the session's
scratch Python 3.12.9 venv, adding `matplotlib`, `seaborn`, `folium`, `jupyter`, `nbconvert`,
`ipykernel` on top of the packages already installed for the pipeline verification above.

**Notebook inventory:** reads exactly one input, `../results/sbpo_v3_results_with_similarities.csv`
(relative to `analysis\`), via `os.path.join('..', 'results', ...)` — matches this bundle's
layout with no path changes needed. Imports: `folium`, `matplotlib`, `numpy`, `pandas`,
`seaborn`, `scipy.stats.t`, `scipy.stats.pearsonr`, `os`. No files are written by the notebook
itself (all output is inline: `plt.show()` figures and an inline `folium` map); the only
artifact produced by this test is the executed notebook copy.

Executed copies were written alongside the originals as `Transfer_Analysis_executed.ipynb`
(not committed changes to `Transfer_Analysis.ipynb` itself).

| Version | Result | Cells | Error outputs |
|---|---|---|---|
| v3 | PASS | 18 | 0 |
| v4 | PASS | 18 | 0 |
| v5 | PASS | 18 | 0 |
| v6 | PASS | 18 | 0 |

No path/scheme mismatches and no code bugs surfaced — the notebook runs end-to-end unmodified
for all four versions.
