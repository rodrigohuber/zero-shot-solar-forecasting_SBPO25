# V3 → V4-6 Data Preparation

These scripts were copied from `ROOT\v4` (verified byte-identical to the copies in `ROOT\v5`
and `ROOT\v6` — no version-specific variants exist, so they are archived once here rather than
duplicated into `v5/data_prep` and `v6/data_prep`). They record how V3's raw
Renewables.ninja/MERRA-2 pulls (via `../../data_acquisition/fetch_ninja_yearly.py`) were turned
into the cleaned/extended source data and station data used from V4 onward
(`v3-6/v4/model/source_data/` and `v3-6/data/v4-6/`).

They are **not wired into any run command** — they were one-off fixups applied manually, in
roughly the order below, against a working copy of the V3-era `data/` and `model/source_data/`
directories. Re-running them requires network access to the Renewables.ninja API (same hardcoded
token as `fetch_ninja_yearly.py`) and is only needed if you want to regenerate V4's data from
V3's raw pulls from scratch; the already-prepared result is what's checked into `v3-6/data/v4-6`
and `v3-6/v4/model/source_data`.

## Scripts, in application order

1. **`fix_galeao.py`** — Fetches the missing 2017-2019 Galeão (RJ, lat -22.813/lon -43.245)
   weather and wind data directly from the Renewables.ninja API into `model/source_data/`, one
   year at a time, skipping any file that already exists. This is the initial backfill that
   gives the Galeão source series its full 2017-2023 span (V3 only had a subset).

2. **`clean_galeao.py`** — Normalizes the freshly-fetched 2017-2019 Galeão files in
   `model/source_data/`: reads each `ninja_weather_<year>.csv` / `ninja_wind_<year>.csv`
   (skipping the 3-line Renewables.ninja metadata header), derives a `local_time` column by
   subtracting 3 hours from the UTC `time` column, and reformats both timestamp columns to
   `YYYY-MM-DD HH:00` strings so the 2017-2019 files match the column layout/format already
   used by the existing 2020-2023 files.

3. **`fix_galeao_wind.py`** — Re-fetches just the 2017-2019 Galeão **wind** files with
   `raw=true` added to the API request (the first pass in `fix_galeao.py` did not request raw
   wind output), then immediately cleans the result in-place (same UTC→local_time derivation
   and timestamp reformatting as `clean_galeao.py`, but handling a `:%00` artifact left by an
   intermediate format string). This corrects a data-quality issue specific to the wind series.

4. **`fix_maracana.py`** — Same backfill pattern as `fix_galeao.py` but applied to the
   Maracanã station folder under `data/` (lat -22.9122/lon -43.2312) instead of the model's
   source data: fetches its missing 2017-2019 weather/wind years from the API using the
   station's `_uncorrected <YY>.csv` naming convention, skipping files that already exist.

5. **`fix_clean.py`** — A second, more general timestamp-cleaning pass over
   `model/source_data/`'s 2017-2019 files: re-parses `time` and `local_time` (working around
   the same `:%00` formatting artifact `fix_galeao_wind.py` handles), and re-writes both as
   `YYYY-MM-DD HH:MM` strings. Effectively a consistency/idempotency fix run after the earlier
   scripts to make sure every file in `source_data/` uses the exact same timestamp string
   format before the source model is (re)trained.

6. **`merge_data.py`** — The final consolidation step: walks `fetched-data/` (the output
   directory used by `fetch_ninja_yearly.py` / `run_fetch_loop.py` in
   `../../data_acquisition/`, per-station subfolders of newly-fetched CSVs) and copies every
   `.csv` file into the matching station subfolder under `data/`, creating the target directory
   if needed. This is what turns a fresh `fetch_ninja_yearly.py` run's output into an
   in-place update of `data/` — the step that ultimately produced V4's 274-file `data/`
   snapshot (`v3-6/data/v4-6`) from V3's 160-file one (`v3-6/data/v3`).

## Net effect

Together these scripts (1) backfilled and cleaned 2017-2019 Galeão source data so
`model/generate_source_model.py` could train on a full 2017-2023 span, (2) applied the same
backfill to the Maracanã target station, and (3) merged newly-fetched 2021-2023 station files
(fetched via the shared `data_acquisition/` scripts, most notably for "0 gera maranhao") into
`data/`. The result is the V4 data snapshot that V5 and V6 both inherit unchanged.
