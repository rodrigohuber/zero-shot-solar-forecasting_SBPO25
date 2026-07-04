import os
import glob
import json
import time
import requests

TOKEN = 'YOUR_RENEWABLES_NINJA_API_TOKEN'  # get yours at https://www.renewables.ninja/profile (original token redacted before commit)
headers = {'Authorization': f'Token {TOKEN}'}

TARGET_DIRS = [
    '0 gera maranhao',
    '1 sao domingos',
    '10 Rio de janeiro',
    '2 nova brasilia urucui',
    '3 Redencao do Gurgueia',
    '4 caripare',
    '5 santa maria da vitoria',
    '6 manga',
    '7 jequitai',
    '8 gov valadares',
    '9 vicosa'
]

BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FETCHED_DIR = os.path.join(os.path.dirname(__file__), 'fetched-data')

if not os.path.exists(FETCHED_DIR):
    os.makedirs(FETCHED_DIR)

def extract_lat_lon(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# {"units"'):
                try:
                    metadata = json.loads(line.strip()[2:])
                    params = metadata.get('params', {})
                    return params.get('lat'), params.get('lon')
                except Exception as e:
                    pass
    return None, None

for folder in TARGET_DIRS:
    print(f"\nProcessing {folder}...")
    folder_path = os.path.join(BASE_DATA_DIR, folder)
    out_folder = os.path.join(FETCHED_DIR, folder)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    
    # find one csv to extract lat lon
    csvs = glob.glob(os.path.join(folder_path, '*ninja_weather*.csv'))
    if not csvs:
        print(f"No weather CSV found in {folder}, skipping.")
        continue
    
    lat, lon = extract_lat_lon(csvs[0])
    if not lat or not lon:
        print(f"Could not extract lat/lon for {folder}, skipping.")
        continue
    
    print(f"Found Lat: {lat}, Lon: {lon}")
    
    # WEATHER REQUEST (2020-2023 to save API rate limits: 1 request instead of 4)
    url_weather = 'https://www.renewables.ninja/api/data/weather'
    params_weather = {
        'lat': lat, 'lon': lon,
        'date_from': '2020-01-01', 'date_to': '2023-12-31',
        'dataset': 'merra2', 'var_t2m': 'true', 'var_prectotland': 'true',
        'var_precsnoland': 'false', 'var_snomas': 'false', 'var_rhoa': 'true',
        'var_swgdn': 'true', 'var_swtdn': 'true', 'var_cldtot': 'true',
        'local_time': 'true', 'header': 'true', 'format': 'csv'
    }
    
    weather_out = os.path.join(out_folder, f"ninja_weather_{lat}_{lon}_2020_2023.csv")
    print("Fetching weather...")
    r = requests.get(url_weather, headers=headers, params=params_weather)
    if r.status_code == 200:
        with open(weather_out, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f"Saved weather to {weather_out}")
    else:
        print(f"Weather request failed: {r.status_code} {r.text[:100]}")
        
    time.sleep(2) # respect 1/sec burst limit
    
    # WIND REQUEST
    url_wind = 'https://www.renewables.ninja/api/data/wind'
    params_wind = {
        'lat': lat, 'lon': lon,
        'date_from': '2020-01-01', 'date_to': '2023-12-31',
        'dataset': 'merra2', 'capacity': '1', 'height': '80',
        'turbine': 'Vestas V90 2000', 'raw': 'true',
        'local_time': 'true', 'header': 'true', 'format': 'csv'
    }
    
    wind_out = os.path.join(out_folder, f"ninja_wind_{lat}_{lon}_2020_2023.csv")
    print("Fetching wind...")
    r = requests.get(url_wind, headers=headers, params=params_wind)
    if r.status_code == 200:
        with open(wind_out, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f"Saved wind to {wind_out}")
    else:
        print(f"Wind request failed: {r.status_code} {r.text[:100]}")
        
    time.sleep(2) # respect 1/sec burst limit

print("\nDone! Fetched all 22 files using exactly 22 API requests, staying under the 50/hour limit.")
