import pandas as pd
import numpy as np
import os
import glob
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit
from skopt import BayesSearchCV
import argparse

# ==========================================
# 1. OUTLIER HANDLING (EXACT PAPER MATCH)
# ==========================================

def replace_outliers_hourly(column):
    """Pass 1: Clip outliers using a 1.5 IQR multiplier on raw hourly data."""
    train_col = column[:-8760] if len(column) > 8760 else column
    quartiles = train_col.quantile([0.25, 0.75])
    Q1 = quartiles[0.25]
    Q3 = quartiles[0.75]
    IQR = Q3 - Q1
    lower_whisker = Q1 - 1.5 * IQR
    upper_whisker = Q3 + 1.5 * IQR
    column.loc[column < lower_whisker] = lower_whisker
    column.loc[column > upper_whisker] = upper_whisker
    return column

def replace_outliers_daily_rg(column):
    """Pass 2: Clip outliers using a tighter 0.9 IQR multiplier purely on the target (RG) after resampling."""
    train_col = column[:-365] if len(column) > 365 else column
    quartiles = train_col.quantile([0.25, 0.75])
    Q1 = quartiles[0.25]
    Q3 = quartiles[0.75]
    IQR = Q3 - Q1
    lower_whisker = Q1 - 0.9 * IQR
    upper_whisker = Q3 + 0.9 * IQR
    column.loc[column < lower_whisker] = lower_whisker
    column.loc[column > upper_whisker] = upper_whisker
    return column

# ==========================================
# 2. FEATURE ENGINEERING
# ==========================================

def create_features(df):
    """Extract temporal features required by the pipeline."""
    df = df.copy()
    df['dayofweek']  = df.index.dayofweek
    df['quarter']    = df.index.quarter
    df['month']      = df.index.month
    df['year']       = df.index.year
    df['dayofyear']  = df.index.dayofyear
    df['dayofmonth'] = df.index.day
    df['weekofyear'] = df.index.isocalendar().week.astype(int)
    return df

# ==========================================
# 3. CORE PROCESSING PIPELINE
# ==========================================

def process_station(directory_path, source_model):
    """
    Reads and processes the raw MERRA/NINJA CSVs for a single station, 
    matching the exact time-series data wrangling methodology from the paper.
    """
    weather_files = sorted(glob.glob(os.path.join(directory_path, '*ninja_weather*.csv')))
    wind_files = sorted(glob.glob(os.path.join(directory_path, '*ninja_wind*.csv')))
    
    if not weather_files or not wind_files:
        return None
        
    dfs_w = [pd.read_csv(f, sep=',', decimal='.', comment='#') for f in weather_files]
    dfs_wind = [pd.read_csv(f, sep=',', decimal='.', comment='#') for f in wind_files]
    
    concat1 = pd.concat(dfs_w).reset_index(drop=True)
    concat2 = pd.concat(dfs_wind).reset_index(drop=True)
    
    concat1['VV'] = concat2['wind_speed']
    concat1.rename(columns={
        't2m': 'TA', 
        'prectotland': 'PR', 
        'rhoa': 'DA', 
        'swgdn': 'RG', 
        'swtdn': 'GHI', 
        'cldtot': 'NV'
    }, inplace=True)
    
    df = concat1.copy()
    df['datetime'] = pd.to_datetime(df['local_time'])
    df.set_index('datetime', inplace=True)
    df.drop(columns=['time', 'local_time'], inplace=True, errors='ignore')
    
    # EXACT REPRODUCIBILITY LOGIC
    df.replace(0, np.nan, inplace=True)
    
    for col in df.columns:
        df[col] = replace_outliers_hourly(df[col])
        
    df = df.resample('D').mean()
    df.replace(0, np.nan, inplace=True)
    
    df['RG'] = replace_outliers_daily_rg(df['RG'])
    
    df = create_features(df)
    df = df.dropna()
    
    data = df[['TA', 'PR', 'GHI', 'NV']]
    target = df['RG']
    
    # Ensure exact matching test set
    train_data, test_data, train_target, test_target = train_test_split(
        data, target, test_size=365, shuffle=False, random_state=42
    )
    
    # ---------------------------------------------------------
    # ZERO-SHOT TRANSFER (SOURCE MODEL)
    # ---------------------------------------------------------
    source_predictions = source_model.predict(test_data[['TA', 'PR', 'GHI', 'NV']])
    transfer_mape = mean_absolute_percentage_error(test_target, source_predictions)
    
    # ---------------------------------------------------------
    # LOCAL MODEL TRAINING (Bayesian Optimization)
    # ---------------------------------------------------------
    # Workaround for skopt compatibility
    np.int = int
    
    opt = BayesSearchCV(
        RandomForestRegressor(random_state=42),
        {
            'n_estimators': [10, 50, 100, 200, 500],
            'max_depth': [None, 10, 20, 30, 50],
            'min_samples_split': [2, 5, 10, 30],
            'min_samples_leaf': [1, 2, 4, 10],
            'bootstrap': [True, False]
        },
        n_iter=5, # Reduced to 5 for speed; change to 50 for exhaustive search
        cv=TimeSeriesSplit(n_splits=3),
        n_jobs=-1,
        verbose=0
    )
    opt.fit(train_data, train_target)
    local_predictions = opt.predict(test_data)
    local_mape = mean_absolute_percentage_error(test_target, local_predictions)
    
    return {
        'Station': os.path.basename(directory_path),
        'Local_MAPE_%': local_mape * 100,
        'Transfer_MAPE_%': transfer_mape * 100,
        'Transfer_Loss_%': (transfer_mape - local_mape) * 100
    }

# ==========================================
# 4. MAIN ORCHESTRATION
# ==========================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run SBPO V3 Reproducibility Experiment')
    parser.add_argument('--data_dir', type=str, default='./data', help='Directory containing station subfolders')
    parser.add_argument('--model_path', type=str, default='./model/source.pkl', help='Path to source transfer model')
    parser.add_argument('--out_dir', type=str, default='./results', help='Output directory for results CSV')
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    print("======================================================")
    print(" Transfer Learning for Solar Irradiance - V3 Pipeline ")
    print("======================================================")
    
    # Load Source Model
    print(f"\nLoading source model from: {args.model_path}")
    source_model = joblib.load(args.model_path)
    
    # Find all station subfolders in the data directory
    stations = sorted([f.path for f in os.scandir(args.data_dir) if f.is_dir()])
    
    if not stations:
        print(f"ERROR: No station folders found in {args.data_dir}.")
        exit(1)
        
    print(f"Found {len(stations)} stations to process. Beginning experiment...\n")
    
    results = []
    
    for i, station_dir in enumerate(stations):
        station_name = os.path.basename(station_dir)
        print(f"[{i+1}/{len(stations)}] Evaluating {station_name}...")
        
        try:
            res = process_station(station_dir, source_model)
            if res:
                results.append(res)
            else:
                print(f"    -> Warning: No valid raw data found in {station_name}. Skipping.")
        except Exception as e:
            print(f"    -> ERROR processing {station_name}: {e}")
            
    print("\nExperiment finalized! Compiling results...")
    
    # Save Results
    if results:
        df_res = pd.DataFrame(results)
        # Round for clean reporting matching the paper
        df_res = df_res.round(3)
        out_file = os.path.join(args.out_dir, 'sbpo_v3_results.csv')
        df_res.to_csv(out_file, index=False)
        
        print(f"Results successfully saved to: {out_file}")
        print("\n=== TOP 5 SUMMARY ===")
        print(df_res.head().to_string(index=False))
    else:
        print("No results to save.")
