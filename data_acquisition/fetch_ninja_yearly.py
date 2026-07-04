import os
import glob
import json
import time
import requests
import sys

TOKEN = 'YOUR_RENEWABLES_NINJA_API_TOKEN'  # get yours at https://www.renewables.ninja/profile (original token redacted before commit)
headers = {'Authorization': f'Token {TOKEN}'}

TARGET_DIRS_B = [
    '0 gera maranhao', '1 sao domingos', '10 Rio de janeiro', 
    '2 nova brasilia urucui', '3 Redencao do Gurgueia', '4 caripare', 
    '5 santa maria da vitoria', '6 manga', '7 jequitai', 
    '8 gov valadares', '9 vicosa'
]
YEARS_B = ['2021', '2022', '2023']

TARGET_DIRS_A = [
    'bangu -22.8753_-43.4649', 'barra da tijuca -23.0114_-43.3218', 
    'botafogo -22.9454_-43.1808', 'copacabana -22.9864_-43.1872', 
    'ipanema -22.9873_-43.2019', 'jacarepagua -22.9532_-43.3716', 
    'maracan -22.9122_-43.2312', 'marambaia -23.0626_-43.8556', 
    'meier -22.9017_-43.2797'
] # Note: source_data already has 2020-2023, maybe we need 2017-2019 for it too? Let's add it.
TARGET_DIRS_A.append('../model/source_data')
YEARS_A = ['2017', '2018', '2019']

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

def fetch_year(lat, lon, year, url, base_params, out_path, kind):
    print(f"  Fetching {kind} for {year}...", end=" ")
    params = base_params.copy()
    params['date_from'] = f"{year}-01-01"
    params['date_to'] = f"{year}-12-31"
    
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print("OK")
        return True
    elif r.status_code == 429:
        print(f"RATE LIMIT EXCEEDED (429)! Stopping script.")
        return False
    else:
        print(f"FAILED ({r.status_code}: {r.text[:50]})")
        return True

def process_group(folders, years_to_fetch):
    for folder in folders:
        print(f"\nProcessing {folder}...")
        if folder == '../model/source_data':
            folder_path = os.path.join(os.path.dirname(__file__), 'model', 'source_data')
            out_folder = os.path.join(FETCHED_DIR, 'source_data')
        else:
            folder_path = os.path.join(BASE_DATA_DIR, folder)
            out_folder = os.path.join(FETCHED_DIR, folder)
            
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        
        csvs = glob.glob(os.path.join(folder_path, '*ninja_weather*.csv'))
        if not csvs:
            print(f"No weather CSV found, skipping.")
            continue
        
        lat, lon = extract_lat_lon(csvs[0])
        if not lat or not lon:
            print(f"Could not extract lat/lon, skipping.")
            continue
        
        url_weather = 'https://www.renewables.ninja/api/data/weather'
        params_weather = {
            'lat': lat, 'lon': lon, 'dataset': 'merra2', 'var_t2m': 'true', 
            'var_prectotland': 'true', 'var_precsnoland': 'false', 
            'var_snomas': 'false', 'var_rhoa': 'true', 'var_swgdn': 'true', 
            'var_swtdn': 'true', 'var_cldtot': 'true', 'local_time': 'true', 
            'header': 'true', 'format': 'csv'
        }
        
        url_wind = 'https://www.renewables.ninja/api/data/wind'
        params_wind = {
            'lat': lat, 'lon': lon, 'dataset': 'merra2', 'capacity': '1', 
            'height': '80', 'turbine': 'Vestas V90 2000', 'raw': 'true',
            'local_time': 'true', 'header': 'true', 'format': 'csv'
        }
        
        for year in years_to_fetch:
            weather_out = os.path.join(out_folder, f"ninja_weather_{lat}_{lon}_uncorrected {year[-2:]}.csv")
            wind_out = os.path.join(out_folder, f"ninja_wind_{lat}_{lon}_uncorrected {year[-2:]}.csv")
            
            if not os.path.exists(weather_out):
                time.sleep(1.5)
                if not fetch_year(lat, lon, year, url_weather, params_weather, weather_out, "weather"):
                    sys.exit(1)
            
            if not os.path.exists(wind_out):
                time.sleep(1.5)
                if not fetch_year(lat, lon, year, url_wind, params_wind, wind_out, "wind"):
                    sys.exit(1)

print("Starting fetch job...")
process_group(TARGET_DIRS_B, YEARS_B)
process_group(TARGET_DIRS_A, YEARS_A)
print("\nDone!")
