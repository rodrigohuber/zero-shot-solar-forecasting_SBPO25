import joblib
import pandas as pd
import numpy as np
import os
import glob
from sklearn.metrics import mean_squared_error

def replace_outliers_hourly(column):
    quartiles = column.quantile([0.25, 0.75])
    Q1 = quartiles[0.25]
    Q3 = quartiles[0.75]
    IQR = Q3 - Q1
    lower_whisker = Q1 - 1.5 * IQR
    upper_whisker = Q3 + 1.5 * IQR
    column.loc[column < lower_whisker] = lower_whisker
    column.loc[column > upper_whisker] = upper_whisker
    return column

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

# Load models
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
m1_path = os.path.join(script_dir, 'galeao_merra.pkl')
m2_path = os.path.join(script_dir, 'test.pkl')
m1 = joblib.load(m1_path)
m2 = joblib.load(m2_path)

print("Loaded both models.")

# Test against a station (e.g., Sao Domingos)
d_path = os.path.join(script_dir, '..', 'data', '1 sao domingos')
weather_files = sorted(glob.glob(os.path.join(d_path, '*ninja_weather*.csv')))
wind_files = sorted(glob.glob(os.path.join(d_path, '*ninja_wind*.csv')))

dfs_w = [pd.read_csv(f, sep=',', decimal='.', comment='#') for f in weather_files]
dfs_wind = [pd.read_csv(f, sep=',', decimal='.', comment='#') for f in wind_files]
concat1 = pd.concat(dfs_w).reset_index(drop=True)
concat2 = pd.concat(dfs_wind).reset_index(drop=True)
concat1['VV'] = concat2['wind_speed']
concat1.rename(columns={'t2m': 'TA', 'prectotland': 'PR', 'rhoa': 'DA', 'swgdn': 'RG', 'swtdn': 'GHI', 'cldtot': 'NV'}, inplace=True)
df = concat1.copy()
df['datetime'] = pd.to_datetime(df['local_time'])
df.set_index('datetime', inplace=True)
df.drop(columns=['time', 'local_time'], inplace=True, errors='ignore')

df.replace(0, np.nan, inplace=True)
for col in df.columns:
    df[col] = replace_outliers_hourly(df[col])
df = df.resample('D').mean()
df.replace(0, np.nan, inplace=True)
df = create_features(df)
df = df.dropna()

data = df[['TA', 'PR', 'GHI', 'NV']].tail(365) # Take exactly 365 test rows

# Predict
p1 = m1.predict(data)
p2 = m2.predict(data)

mse_diff = mean_squared_error(p1, p2)
max_diff = np.max(np.abs(p1 - p2))

print(f"MSE between original pkl and test pkl: {mse_diff}")
print(f"Max absolute difference in predictions: {max_diff}")
print(f"p1 sample: {p1[:5]}")
print(f"p2 sample: {p2[:5]}")
