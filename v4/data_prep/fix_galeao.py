import requests
import sys
import os
import time

# Shared free-tier Renewables.ninja token. Register your own (free) at
# https://www.renewables.ninja/register and replace it below before running.
TOKEN = 'fd5a9a0f960a588e9abce483ede6d2c3103e8d1b'
headers = {'Authorization': f'Token {TOKEN}'}

out_dir = os.path.join('model', 'source_data')
lat, lon = -22.813, -43.245

def fetch_year(year, dataset='merra2'):
    weather_out = os.path.join(out_dir, f"ninja_weather_{year}.csv")
    wind_out = os.path.join(out_dir, f"ninja_wind_{year}.csv")
    
    # Weather
    if not os.path.exists(weather_out):
        print(f"  Fetching weather for {year}...")
        url = 'https://www.renewables.ninja/api/data/weather'
        params = {
            'lat': lat, 'lon': lon, 'date_from': f'{year}-01-01', 'date_to': f'{year}-12-31',
            'dataset': dataset, 'var_t2m': 'true', 'var_prectotland': 'true',
            'var_rhoa': 'true', 'var_swgdn': 'true', 'var_swtdn': 'true',
            'var_cldtot': 'true', 'format': 'csv'
        }
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            with open(weather_out, 'w', encoding='utf-8') as f:
                f.write(r.text)
        else:
            print(f"Error {r.status_code} fetching weather")
        time.sleep(1.5)
        
    # Wind
    if not os.path.exists(wind_out):
        print(f"  Fetching wind for {year}...")
        url = 'https://www.renewables.ninja/api/data/wind'
        params = {
            'lat': lat, 'lon': lon, 'date_from': f'{year}-01-01', 'date_to': f'{year}-12-31',
            'dataset': dataset, 'capacity': 1.0, 'height': 100, 'turbine': 'Vestas V80 2000',
            'format': 'csv'
        }
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            with open(wind_out, 'w', encoding='utf-8') as f:
                f.write(r.text)
        else:
            print(f"Error {r.status_code} fetching wind")
        time.sleep(1.5)

print(f"Fixing Galeao source data...")
for year in ['2017', '2018', '2019']:
    fetch_year(year)
print("Done fixing Galeao!")
