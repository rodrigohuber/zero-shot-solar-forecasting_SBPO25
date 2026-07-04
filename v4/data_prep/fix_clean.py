import pandas as pd
import os

source_dir = os.path.join('model', 'source_data')

for year in ['2017', '2018', '2019']:
    for prefix in ['ninja_weather', 'ninja_wind']:
        file_path = os.path.join(source_dir, f"{prefix}_{year}.csv")
        
        df = pd.read_csv(file_path)
        
        df['time'] = pd.to_datetime(df['time'].str.replace(':%00', ':00'))
        df['local_time'] = pd.to_datetime(df['local_time'].str.replace(':%00', ':00'))
        
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M')
        df['local_time'] = df['local_time'].dt.strftime('%Y-%m-%d %H:%M')
        
        df.to_csv(file_path, index=False)
        print(f"Cleaned {file_path}")
