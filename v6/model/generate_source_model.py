import pandas as pd
import numpy as np
import os
import glob
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. OUTLIER HANDLING (EXACT PAPER MATCH)
# ==========================================

def replace_outliers_hourly(column):
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
    df = df.copy()
    df['dayofweek']  = df.index.dayofweek
    df['quarter']    = df.index.quarter
    df['month']      = df.index.month
    df['year']       = df.index.year
    df['dayofyear']  = df.index.dayofyear
    df['dayofmonth'] = df.index.day
    df['weekofyear'] = df.index.isocalendar().week.astype(int)
    return df

if __name__ == '__main__':
    print("======================================================")
    print(" Generating Source Model (Galeão) for Zero-Shot Transfer")
    print("======================================================")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory_path = os.path.join(script_dir, "source_data")
    
    wind_files = sorted(glob.glob(os.path.join(directory_path, 'ninja_wind*.csv')))
    weather_files = sorted(glob.glob(os.path.join(directory_path, 'ninja_weather*.csv')))
    
    if not weather_files or not wind_files:
        print(f"ERROR: Galeao data not found in {directory_path}")
        exit(1)
        
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
    
    df.replace(0, np.nan, inplace=True)
    
    for col in df.columns:
        df[col] = replace_outliers_hourly(df[col])
        
    df = df.resample('D').mean()
    df.replace(0, np.nan, inplace=True)
    df['RG'] = replace_outliers_daily_rg(df['RG'])
    df = create_features(df)
    df = df.dropna()
    
    data = df[['TA', 'PR', 'GHI', 'NV', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear', 'dayofmonth', 'weekofyear']]
    target = df['RG']
    
    train_data, test_data, train_target, test_target = train_test_split(
        data, target, test_size=365, shuffle=False, random_state=42
    )
    
    print(f"Data parsed successfully. Training samples: {len(train_data)}")
    print("Training the RandomForestRegressor with exact parameters...")
    
    # Using the exact best parameters discovered in the original model
    model = RandomForestRegressor(
        max_depth=20,
        min_samples_leaf=1,
        min_samples_split=2,
        n_estimators=100,
        bootstrap=True,
        random_state=42
    )
    
    model.fit(train_data, train_target)
    
    out_file = os.path.join(script_dir, "source.pkl")
    joblib.dump(model, out_file)
    print(f"Success! Model generated and saved to {out_file}")
