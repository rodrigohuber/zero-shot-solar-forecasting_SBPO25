import pandas as pd
import numpy as np
import os
import glob
import json
import math
from pycatch22 import catch22_all
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist
from dtaidistance import dtw

# ==========================================
# 1. HAVERSINE GEOGRAPHIC DISTANCE
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in kilometers between two points on the earth."""
    R = 6371.0 # Earth radius in kilometers
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
        
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def extract_lat_lon(csv_path):
    """Extract lat/lon from the JSON header of Renewables.ninja files."""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = [next(f) for _ in range(3)]
        
        # The 3rd line contains the JSON metadata prefixed by "# "
        json_str = lines[2].strip()
        if json_str.startswith('# '):
            json_str = json_str[2:]
        metadata = json.loads(json_str)
        
        lat = float(metadata['params']['lat'])
        lon = float(metadata['params']['lon'])
        return lat, lon
    except Exception as e:
        # Fallback to parsing from filename if header is missing
        basename = os.path.basename(csv_path)
        parts = basename.split('_')
        for i, part in enumerate(parts):
            if '.' in part and part.replace('.', '').replace('-', '').isdigit():
                try:
                    return float(parts[i]), float(parts[i+1])
                except:
                    pass
        return None, None

# ==========================================
# 2. TIME-SERIES SIMILARITY
# ==========================================
def create_windows(series, window_size=100, step=10):
    series = series.dropna().values
    if len(series) < window_size:
        return [series]
    return [series[i:i + window_size] for i in range(0, len(series) - window_size + 1, step)]

def extract_catch22_features(windows):
    features = []
    for w in windows:
        w_float = w.astype(float)
        f = catch22_all(w_float)
        mean_val = np.mean(w_float)
        std_val = np.std(w_float)
        features.append(np.concatenate([f['values'], [mean_val, std_val]]))
    return np.array(features)

def compute_catch22_similarity(source_series, target_series):
    w_source = create_windows(source_series)
    w_target = create_windows(target_series)
    
    f_source = extract_catch22_features(w_source)
    f_target = extract_catch22_features(w_target)
    
    # Scale based on target 
    scaler = StandardScaler().fit(f_target)
    s_source = scaler.transform(f_source)
    s_target = scaler.transform(f_target)
    
    distance_matrix = cdist(s_source, s_target, metric='euclidean')
    return np.median(distance_matrix)

def compute_dtw_distance(source_series, target_series):
    # Subsample to avoid massive memory usage on long series
    s1 = source_series.dropna().values[::5]
    s2 = target_series.dropna().values[::5]
    return dtw.distance(s1, s2)

# ==========================================
# 3. PIPELINE PREPROCESSING
# ==========================================
def load_and_preprocess_series(directory_path, is_galeao=False):
    weather_files = sorted(glob.glob(os.path.join(directory_path, '*ninja_weather*.csv')))
    wind_files = sorted(glob.glob(os.path.join(directory_path, '*ninja_wind*.csv')))
        
    if not weather_files or not wind_files:
        return None, None, None
        
    dfs_w = [pd.read_csv(f, sep=',', decimal='.', comment='#') for f in weather_files]
    concat1 = pd.concat(dfs_w).reset_index(drop=True)
    
    # For Galeao, lat/lon is fixed
    lat, lon = -22.813, -43.245
    if not is_galeao:
        lat, lon = extract_lat_lon(weather_files[0])
    
    concat1.rename(columns={'swgdn': 'RG'}, inplace=True)
    
    df = concat1.copy()
    df['datetime'] = pd.to_datetime(df['local_time'])
    df.set_index('datetime', inplace=True)
    
    df = df[['RG']].copy()
    df.replace(0, np.nan, inplace=True)
    df = df.resample('D').mean()
    df.replace(0, np.nan, inplace=True)
    
    return df['RG'], lat, lon

# ==========================================
# 4. MAIN ORCHESTRATION
# ==========================================
if __name__ == '__main__':
    print("======================================================")
    print(" Calculating Geographic & Time-Series Similarities ")
    print("======================================================")
    
    source_dir = os.path.join("model", "source_data")
    data_dir = "data"
    
    print("Loading Source Station (Galeão)...")
    source_rg, source_lat, source_lon = load_and_preprocess_series(source_dir, is_galeao=True)
    
    stations = sorted([f.path for f in os.scandir(data_dir) if f.is_dir()])
    
    results = []
    
    for i, station_dir in enumerate(stations):
        station_name = os.path.basename(station_dir)
        print(f"[{i+1}/{len(stations)}] Processing {station_name}...")
        
        target_rg, target_lat, target_lon = load_and_preprocess_series(station_dir)
        
        if target_rg is None or target_lat is None:
            print(f"    -> Skipping {station_name}: Missing data or lat/lon.")
            continue
            
        geo_dist = haversine(source_lat, source_lon, target_lat, target_lon)
        
        # Calculate Catch22 and DTW on the raw target distributions
        catch22_dist = compute_catch22_similarity(source_rg, target_rg)
        dtw_dist = compute_dtw_distance(source_rg, target_rg)
        
        results.append({
            'Station': station_name,
            'Geo_Distance_km': geo_dist,
            'Catch22_Distance': catch22_dist,
            'DTW_Distance': dtw_dist,
            'Target_Lat': target_lat,
            'Target_Lon': target_lon
        })
        print(f"    -> Geo Dist: {geo_dist:.2f} km | Catch22: {catch22_dist:.2f} | DTW: {dtw_dist:.2f}")

    print("\nCalculation complete. Merging with existing ML results...")
    
    res_df = pd.DataFrame(results)
    res_df.sort_values(by="Geo_Distance_km", inplace=True)

    os.makedirs("results", exist_ok=True)

    ml_results_path = os.path.join("results", "sbpo_v3_results.csv")
    if os.path.exists(ml_results_path):
        ml_df = pd.read_csv(ml_results_path)
        final_df = pd.merge(ml_df, res_df, on="Station", how="left")
        final_df.sort_values(by="Geo_Distance_km", inplace=True)
        final_path = os.path.join("results", "sbpo_v3_results_with_similarities.csv")
        final_df.to_csv(final_path, index=False)
        
        print(f"Successfully saved enriched dataset to {final_path}")
    else:
        out_path = os.path.join("results", "station_similarities.csv")
        res_df.to_csv(out_path, index=False)
        print(f"No ML results found. Saved similarities standalone to {out_path}")
