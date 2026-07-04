import requests
import os
import pandas as pd

# Shared free-tier Renewables.ninja token. Register your own (free) at
# https://www.renewables.ninja/register and replace it below before running.
TOKEN = 'fd5a9a0f960a588e9abce483ede6d2c3103e8d1b'
headers = {'Authorization': f'Token {TOKEN}'}

out_dir = os.path.join('model', 'source_data')
lat, lon = -22.813, -43.245

for year in ['2017', '2018', '2019']:
    wind_out = os.path.join(out_dir, f"ninja_wind_{year}.csv")
    print(f"Refetching wind for {year}...")
    url = 'https://www.renewables.ninja/api/data/wind'
    params = {
        'lat': lat, 'lon': lon, 'date_from': f'{year}-01-01', 'date_to': f'{year}-12-31',
        'dataset': 'merra2', 'capacity': 1.0, 'height': 100, 'turbine': 'Vestas V80 2000',
        'raw': 'true', 'format': 'csv'
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        with open(wind_out, 'w', encoding='utf-8') as f:
            f.write(r.text)
        
        # Clean immediately
        df = pd.read_csv(wind_out, skiprows=3)
        df['time'] = pd.to_datetime(df['time'].str.replace(':%00', ':00'))
        df.insert(1, 'local_time', df['time'] - pd.Timedelta(hours=3))
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M')
        df['local_time'] = df['local_time'].dt.strftime('%Y-%m-%d %H:%M')
        df.to_csv(wind_out, index=False)
        print(f"Cleaned {wind_out}")
    else:
        print(f"Error {r.status_code}")
