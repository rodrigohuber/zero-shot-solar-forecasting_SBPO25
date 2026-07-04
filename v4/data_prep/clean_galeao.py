import pandas as pd
import os
import glob

source_dir = os.path.join('model', 'source_data')

for year in ['2017', '2018', '2019']:
    for prefix in ['ninja_weather', 'ninja_wind']:
        file_path = os.path.join(source_dir, f"{prefix}_{year}.csv")
        
        # Read the file skipping the 3 metadata lines
        df = pd.read_csv(file_path, skiprows=3)
        
        # Convert time to datetime and create local_time by subtracting 3 hours
        df['time'] = pd.to_datetime(df['time'])
        df.insert(1, 'local_time', df['time'] - pd.Timedelta(hours=3))
        
        # Format times back to string for consistency with 2020-2023
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%00')
        df['local_time'] = df['local_time'].dt.strftime('%Y-%m-%d %H:%00')
        
        # Overwrite the file exactly matching the 2020 format
        df.to_csv(file_path, index=False)
        print(f"Cleaned {file_path}")

print("Done cleaning 2017-2019 Galeao data!")
