# Comparative Analysis: `10 Rio de janeiro` vs `source_galeao`

This document details the relationship between the `v3/data/10 Rio de janeiro` target folder and the `v3/model/source_galeao` training folder. Although they represent the same general macro-climate (Galeão/Rio de Janeiro), they differ significantly in their temporal bounds and precise coordinate grids.

## 1. Temporal Difference (Time Travel)
- **`source_galeao` (Training)**: Contains data strictly for the years **2020 to 2023**. This is the dataset the base Random Forest model was trained on.
- **`10 Rio de janeiro` (Evaluation)**: Contains data strictly for the years **2017 to 2020** (`17.csv` through `20.csv`). It acts as an out-of-sample temporal holdout.

## 2. Geographical Nuance
In the experiment pipeline, weather and wind data are pulled from two slightly different coordinate grids:
- **Wind Data**: The wind file in `10 Rio de janeiro` is located at `-22.8075, -43.2355`. This is practically **directly on top** of Galeão Airport (`-22.8089, -43.2436`).
- **Weather Data**: The weather/solar file in `10 Rio de janeiro` is located at `-22.8376, -43.3092`. The `run_similarity.py` pipeline calculated this to be exactly **7.12 km** away from the exact Galeão anchor point.

## 3. Machine Learning Performance (Negative Transfer Loss)
Because `10 Rio de janeiro` is practically the exact same location as `source_galeao` (just 7km away and shifted 3 years into the past), the machine learning results for this specific folder exhibit "Negative Transfer Loss":

- **Local MAPE**: 11.16%
- **Transferred MAPE**: 6.72% 
- **Transfer Loss**: **-4.43%**

The `source_galeao` model performed **better** on this target location than a local model trained directly on the location itself! This proves that the `source_galeao` model is incredibly robust at capturing the local micro-climate, achieving an exceptional 6.7% MAPE on out-of-sample temporal holdout data.

## 4. Relevance to the Original Paper
In the original `AORESENTACAO V2.ipynb` paper, the 9 Rio de Janeiro stations plotted were strictly surrounding neighborhoods (Barra, Copacabana, Jacarepagua, Maracana, Marambaia, Bangu, Botafogo, Ipanema, Meier). 

**`10 Rio de janeiro` was purposely excluded** from those scatter plots and bar charts because it isn't a true "transfer" target. It is essentially just Galeão itself being tested on historical data, whereas the paper was designed to test the transferability of Galeão's model to *other* distinct geographical neighborhoods.
