# Temporal Divergence Analysis: A Methodological Flaw in Data Sourcing

During the auditing of the `v3` zero-shot transfer learning pipeline, a significant temporal divergence was discovered in the underlying datasets used for model evaluation. The target stations are cleanly divided into two incompatible temporal groups.

## The Temporal Split

### Group A: Synchronous Data (2020 - 2023)
These stations perfectly match the exact years the base model (`source.pkl`) was trained on. The machine learning model evaluated them during the exact same macroeconomic and climatic time window:
- `source_data` (Galeão base model)
- `bangu`
- `barra da tijuca`
- `botafogo`
- `copacabana`
- `ipanema`
- `jacarepagua`
- `maracanã`
- `marambaia`
- `meier`

*Note: These are exclusively the Rio de Janeiro (RJ) localized neighborhoods.*

### Group B: Asynchronous Historical Data (2017 - 2020)
These folders contain strictly older historical data. This means the base model (trained on 2020-2023) was tested not only on a completely different geographical location, but it was forced to "time travel" backwards to predict historical weather.
- `0 gera maranhao`
- `1 sao domingos`
- `2 nova brasilia urucui`
- `3 Redencao do Gurgueia`
- `4 caripare`
- `5 santa maria da vitoria`
- `6 manga`
- `7 jequitai`
- `8 gov valadares`
- `9 vicosa`
- `10 Rio de janeiro`

*Note: These comprise all of the long-distance Brazil (BR) targets.*

---

## Data Science Implications

From a strict time-series data science and peer-review perspective, **this is a catastrophic methodological flaw**. 

If this research is evaluated strictly as a time-series forecasting experiment, it suffers from several critical invalidations:

1. **Confounding Variables (Temporal Drift vs. Geographic Shift)**: When the model predicts poorly in a distant station (e.g., Gov Valadares), it is mathematically impossible to isolate whether the error stems from the spatial distance (Spatial Transfer Loss) or because the climate in 2017 was fundamentally different from 2021 (Temporal Drift). Two independent variables have been completely mixed.
2. **Macrometeorological Events**: Solar irradiance and wind patterns are heavily influenced by macro events (e.g., *El Niño*, *La Niña*). The 2020-2023 window has a distinct global climate footprint compared to 2017-2020. The model learned the "rules" of the 2020-2023 atmosphere, and was unfairly penalized when tested against the 2017 atmosphere.
3. **Invalid Comparisons**: It is statistically invalid to plot the RJ stations and the BR stations on the same trend line or scatter plot. Comparing an RJ station's 2022 MAPE against a BR station's 2018 MAPE is comparing asynchronous entities. Consequently, the statistical correlations calculated (Pearson/Spearman) are technically compromised because the dataset is not controlled for time.

## Resolution Plan

Because the `v3` pipeline is fully dynamic and automated, fixing this flaw does not require writing any new code. To restore the mathematical integrity of the experiment:

1. Re-download the weather and wind data from Renewables.ninja for the 10 Brazil coordinates, ensuring the date range is strictly set to **2020 - 2023**.
2. Replace the old `17.csv` - `20.csv` files inside the `v3/data/` folders with the newly downloaded synchronous data.
3. Re-run `python run_experiment.py` and `python run_similarity.py`.
4. Re-run the `Transfer_Analysis.ipynb` notebook.

The pipeline will automatically recalculate the entire paper with perfectly synchronous, mathematically valid data.
