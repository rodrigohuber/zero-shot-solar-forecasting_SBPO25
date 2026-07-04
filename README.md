# Zero-Shot Transfer Learning for Solar-Irradiance Forecasting (SBPO 2025)

Reproducible code and data for the SBPO 2025 paper. A Random Forest is trained **once** on
Galeão station (Rio de Janeiro) MERRA-2 reanalysis data and applied **zero-shot** to 20 solar
stations across Brazil. Forecast accuracy is strong near the source and degrades as the target
diverges geographically and climatically — quantifying when transfer learning is reliable.

📄 **Paper:** *Exploring Transfer Learning Techniques for Solar Irradiation Forecast across
Geographically Diverse Locations in Brazil Using Reanalysis Data* — Mendes, Baião & Souza,
SBPO 2025.
[Official publication](https://proceedings.science/sbpo/sbpo-2025/trabalhos/exploring-transfer-learning-techniques-for-solar-irradiation-forecast-across-geo?lang=pt-br)
· [full text](paper/SBPO2025_transfer-learning-solar-forecasting.md)
· [cite](paper/README.md)

## Results

Zero-shot **Transfer** (frozen Galeão model) vs. a locally-trained **Local** model — mean MAPE
across all 20 stations, for each successive version of the pipeline:

| Version | Change | Transfer MAPE % | Local MAPE % |
|---|---|:--:|:--:|
| v3 | base reproduction | 12.83 | 12.24 |
| v4 | data cleanup (+2021–23) | 12.63 | 11.78 |
| v5 | IQR outlier-leakage fix | 12.72 | 11.83 |
| v6 | + temporal features | 12.79 | 11.80 |

Browse the rendered per-version analysis (plots, maps, per-station tables) with **no install**
in [`docs/index.html`](docs/index.html), or see [`COMPARISON.md`](COMPARISON.md) for why the
versions differ.

## Quickstart

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd v3      # or v4 / v5 / v6
python run_experiment.py --data_dir ..\data\v3 --model_path .\model\source.pkl --out_dir .\results
python run_similarity.py
```

Fresh output lands in `results/`; compare it against the frozen `results_reference/`.
Transfer MAPE and all similarity columns reproduce **bit-exactly**; Local MAPE varies
run-to-run (the Bayesian hyperparameter search is unseeded). Full end-to-end reproduction
(raw data fetch → preparation → analysis notebooks, with verified version pins) is in
**[REPRODUCTION.md](REPRODUCTION.md)**.

## What's here

| Path | Contents |
|---|---|
| `v3/`–`v6/` | Four pipeline versions: `run_experiment.py`, `run_similarity.py`, `model/`, frozen `results_reference/`, analysis notebook |
| `data/` | Bundled MERRA-2 / Renewables.ninja inputs for all 20 stations |
| `data_acquisition/`, `v4/data_prep/` | Raw-data fetch & preparation scripts (full provenance) |
| `docs/` | Zero-install HTML results showcase |
| `paper/` | Paper full text + citation |

> **Data note:** reproducing the published results needs **no API token** — the data is bundled
> under `data/`. Re-fetching raw data uses the [Renewables.ninja](https://www.renewables.ninja/)
> API; the token in the fetch scripts is a shared public free-tier one, so
> [register your own](https://www.renewables.ninja/register) before re-fetching.

## License

MIT — see [LICENSE](LICENSE).
