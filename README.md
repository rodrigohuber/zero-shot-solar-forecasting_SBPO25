<h1 align="center">Zero-Shot Transfer Learning for Solar-Irradiance Forecasting</h1>

<p align="center">
  <em>One model, trained on a single Brazilian airport, forecasts day-ahead solar irradiance
  across a 2,145&nbsp;km span of the country — with no fine-tuning — and we show exactly
  <strong>when</strong> and <strong>why</strong> it works.</em>
</p>

<p align="center">
  <a href="https://proceedings.science/sbpo/sbpo-2025/trabalhos/exploring-transfer-learning-techniques-for-solar-irradiation-forecast-across-geo?lang=pt-br"><img src="https://img.shields.io/badge/Paper-SBPO%202025-1a5fb4" alt="Paper"></a>
  <img src="https://img.shields.io/badge/Python-3.12-3776ab" alt="Python 3.12">
  <img src="https://img.shields.io/badge/Results-bit--exact%20reproducible-2e7d32" alt="Reproducible">
  <img src="https://img.shields.io/badge/License-MIT-6a1b9a" alt="MIT License">
</p>

---

Day-ahead solar forecasting normally demands a bespoke model per site — expensive and
data-hungry at grid scale. This work asks a sharper question: **how far can a single
pre-trained model travel before it breaks?** A Random Forest is trained **once** on Galeão
Airport (Rio de Janeiro) from MERRA-2 reanalysis, then applied **zero-shot** — frozen, no
fine-tuning — to 20 stations spanning the Brazilian coast to the deep Northeast. The answer is
both a strong positive result and a principled map of its limits.

## Headline results

- **A single frozen model rivals 20 locally-optimized ones.** Averaged over all 20 sites,
  the zero-shot transfer model trails Bayesian-optimized *per-site* models by just
  **0.6 percentage points MAPE** (12.8% vs 12.2%).
- **Near the source, transfer wins outright.** Across the 10 metropolitan-Rio sites
  (≤ 68 km), zero-shot transfer is *on par with or better than* locally-trained models — and
  at the source-adjacent site it **halves** the error (**6.7%** transfer vs 11.4% local).
- **Degradation is lawful, not random.** Transfer error rises monotonically with
  source–target divergence, reaching **+3.7 pp** at the ~2,145 km northern extreme — a decline
  the study's **geographic, DTW, and Catch22 similarity metrics** quantify and anticipate,
  turning "will transfer work here?" into a measurable, pre-deployment decision.

### Accuracy vs. distance from the source (representative sites)

| Target site | Distance from source | Transfer MAPE | Local MAPE | Δ (Transfer − Local) |
|---|--:|--:|--:|--:|
| Rio de Janeiro (source-adjacent) | 7 km | **6.7%** | 11.4% | **−4.7** |
| Méier (Rio metro) | 10 km | 12.8% | 12.6% | +0.1 |
| Marambaia (Rio coast) | 68 km | 12.4% | 12.3% | +0.2 |
| Gov. Valadares | 459 km | 10.4% | 10.8% | −0.4 |
| Caripará | 1,276 km | 12.9% | 10.7% | +2.2 |
| Gera / Maranhão | 2,145 km | 19.4% | 15.7% | +3.7 |

*Full 20-station results, per-version, in [`COMPARISON.md`](COMPARISON.md) and the rendered
notebooks under [`docs/`](docs/index.html).*

## What makes this more than a benchmark

- **Similarity-driven transferability.** Beyond raw error, three complementary lenses —
  Haversine geographic distance, Dynamic Time Warping (DTW), and Catch22 time-series features
  — characterize *why* a target site is easy or hard to transfer to, giving a basis for
  deciding transfer feasibility **before** deploying anywhere new.
- **Reanalysis-grade inputs at continental scale.** MERRA-2 hourly air temperature, pressure,
  cloud cover, and top-of-atmosphere / ground-level irradiance for 20 sites, resampled to a
  daily day-ahead target.
- **Fair local baselines.** Each site's "local" competitor is not a toy model but a
  Bayesian-optimized Random Forest (`BayesSearchCV` over depth, estimators, split/leaf sizes),
  so the transfer result is measured against a genuinely tuned opponent.

## Reproducibility as a first-class result

The pipeline ships as **four transparent, versioned stages** (`v3` → `v6`) that document and
correct methodological subtleties rather than hiding them — including an **outlier-leakage
fix** (IQR bounds computed on the training slice only) and an explicit study of added temporal
features. Every version is verified end-to-end:

- **Transfer MAPE and all similarity columns reproduce bit-exactly** against the frozen
  `results_reference/` — in a clean venv, and even under substantial library-version drift.
- Local MAPE is *honestly* reported as run-to-run variable (the Bayesian search is unseeded);
  the noise band is documented rather than papered over.
- Full pinned environment, data provenance, and per-step commands in
  **[REPRODUCTION.md](REPRODUCTION.md)**.

## Paper

> **Exploring Transfer Learning Techniques for Solar Irradiation Forecast across
> Geographically Diverse Locations in Brazil Using Reanalysis Data**
> Rodrigo Huber Marques Moreira Mendes, Fernanda Araújo Baião, Reinaldo Castro Souza · PUC-Rio
> *Simpósio Brasileiro de Pesquisa Operacional (SBPO) 2025*

[Official publication](https://proceedings.science/sbpo/sbpo-2025/trabalhos/exploring-transfer-learning-techniques-for-solar-irradiation-forecast-across-geo?lang=pt-br)
· [full text](paper/SBPO2025_transfer-learning-solar-forecasting.md)
· [BibTeX](paper/README.md)

## Quickstart

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd v3      # or v4 / v5 / v6
python run_experiment.py --data_dir ..\data\v3 --model_path .\model\source.pkl --out_dir .\results
python run_similarity.py
```

Fresh output lands in `results/`; compare against the frozen `results_reference/`. Full
end-to-end reproduction (raw data fetch → preparation → analysis notebooks) is in
**[REPRODUCTION.md](REPRODUCTION.md)**.

## Repository map

| Path | Contents |
|---|---|
| `v3/`–`v6/` | Four pipeline versions: `run_experiment.py`, `run_similarity.py`, `model/`, frozen `results_reference/`, analysis notebook |
| `data/` | Bundled MERRA-2 / Renewables.ninja inputs for all 20 stations |
| `data_acquisition/`, `v4/data_prep/` | Raw-data fetch & preparation scripts (full provenance) |
| `docs/` | Zero-install HTML results showcase |
| `paper/` | Paper full text + citation |

> **Data note:** reproducing the published results needs **no API token** — the data is bundled.
> Re-fetching raw data uses the [Renewables.ninja](https://www.renewables.ninja/) API; the token
> in the fetch scripts is a shared public free-tier one, so
> [register your own](https://www.renewables.ninja/register) before re-fetching.

## License

MIT — see [LICENSE](LICENSE).
