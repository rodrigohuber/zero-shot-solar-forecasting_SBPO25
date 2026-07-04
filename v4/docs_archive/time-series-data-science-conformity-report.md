# Time-Series & Data Science Conformity Report

This document evaluates the `v4` Transfer Learning pipeline for conformity to best practices in data science and time-series forecasting. While the pipeline is structurally sound and avoids catastrophic failures, several methodological flaws and inefficiencies were identified.

## ✅ Major Conformity Successes

The pipeline strictly adheres to the most critical rules of time-series forecasting:

1. **No Time-Travel Leakage in Testing:** The use of `train_test_split(shuffle=False, test_size=365)` correctly segregates the past (2017-2022) for training and the strict chronological future (2023) for testing.
2. **Proper Validation Splitting:** During the Bayesian Optimization phase, the pipeline uses `TimeSeriesSplit(n_splits=3)`. This ensures that cross-validation folds respect chronological order and do not peek into future data during hyperparameter tuning.

## ⚠️ Methodological Flaws & Errors

### 1. Minor Data Leakage via Outlier Clipping
**Severity: Minor**

In both `run_experiment.py` and `generate_source_model.py`, the outlier handling is applied across the **entire dataset before** the train/test split occurs:
```python
for col in df.columns:
    df[col] = replace_outliers_hourly(df[col]) # Calculates quantiles on entire dataset
```
* **The Flaw:** The Interquartile Range thresholds (Q1 and Q3) are calculated using the full 2017-2023 dataset. This allows information about the 2023 test data's distribution to subtly influence the clipping boundaries applied to the 2017-2022 training data (and vice versa).
* **The Fix:** The dataset should be split into train and test sets *first*. Q1 and Q3 must be calculated exclusively on the training set, and those exact thresholds should be applied to clip both sets independently.
* **Impact:** Because it is an IQR calculation over 7 years of data, extreme days in 2023 will barely shift the 25th and 75th percentiles. It does not invalidate the results, but it constitutes a classic (albeit minor) data leak that a strict peer-reviewer would penalize.

### 2. Redundant Feature Engineering (Code Inefficiency)
**Severity: Minor**

The pipeline includes a `create_features(df)` function that extracts temporal data (e.g., `dayofweek`, `quarter`, `month`, `year`).
* **The Flaw:** Immediately after these features are generated, the pipeline discards them when constructing the final training set:
```python
data = df[['TA', 'PR', 'GHI', 'NV']] # Time features are completely dropped!
```
* **The Fix:** Either remove the `create_features` function to save compute time, or include these temporal markers in the `data` array. 
* **Impact:** Wasted computation. Furthermore, Random Forest models perform exceptionally well when given temporal markers to model seasonal solar variance. By dropping them, the model is forced to infer seasonality entirely from raw weather variables.

### 3. Missing Feature Scaling in Transfer Learning
**Severity: Negligible / Best-Practice Violation**

The pipeline feeds raw, unscaled variables (like GHI which scales to 1000+, alongside PR which is a tiny decimal) directly into the Random Forest models.
* **The Flaw:** The models omit standard scaling (e.g., `StandardScaler`).
* **Impact:** Tree-based algorithms like Random Forest are invariant to monotonic transformations, so they do not strictly *require* feature scaling to determine node splits. However, in the specific context of **Transfer Learning** and Domain Adaptation, normalizing distributions is usually considered a best practice so that source and target domains overlap more cleanly. 

## Conclusion
The core experimental design is valid. The chronological splits are perfectly respected. To achieve publication-grade perfection, the outlier clipping logic must be moved to occur *after* the train/test split.
