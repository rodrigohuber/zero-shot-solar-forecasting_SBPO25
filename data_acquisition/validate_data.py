import os
import pandas as pd
import json

FETCHED_DIR = 'fetched-data'
OLD_DIR = 'data'

def validate_files():
    errors = []
    warnings = []
    
    if not os.path.exists(FETCHED_DIR):
        print("Fetched data directory not found.")
        return
        
    stations = [d for d in os.listdir(FETCHED_DIR) if os.path.isdir(os.path.join(FETCHED_DIR, d))]
    
    for station in stations:
        fetched_station_dir = os.path.join(FETCHED_DIR, station)
        old_station_dir = os.path.join(OLD_DIR, station)
        
        csv_files = [f for f in os.listdir(fetched_station_dir) if f.endswith('.csv')]
        
        if not csv_files:
            continue
            
        # Get one old weather and one old wind file to compare schemas
        old_weather_cols = None
        old_wind_cols = None
        
        if os.path.exists(old_station_dir):
            old_files = [f for f in os.listdir(old_station_dir) if f.endswith('.csv')]
            for f in old_files:
                path = os.path.join(old_station_dir, f)
                try:
                    df = pd.read_csv(path, header=3)
                    if 'weather' in f:
                        old_weather_cols = list(df.columns)
                    elif 'wind' in f:
                        old_wind_cols = list(df.columns)
                except Exception:
                    pass
                    
        for csv_file in csv_files:
            file_path = os.path.join(fetched_station_dir, csv_file)
            
            # Check 1: Is it actually an error JSON saved as CSV?
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('{'):
                        errors.append(f"{csv_file} in {station} contains JSON/Error instead of CSV data!")
                        continue
            except Exception as e:
                errors.append(f"Could not read {csv_file}: {e}")
                continue
                
            # Check 2: Schema comparison
            try:
                # Ninja files have metadata in first 3 rows, header is row 3 (0-indexed)
                df_new = pd.read_csv(file_path, header=3)
                new_cols = list(df_new.columns)
                
                if 'weather' in csv_file and old_weather_cols:
                    if new_cols != old_weather_cols:
                        warnings.append(f"Column mismatch in {csv_file}. Old: {old_weather_cols}, New: {new_cols}")
                elif 'wind' in csv_file and old_wind_cols:
                    if new_cols != old_wind_cols:
                        warnings.append(f"Column mismatch in {csv_file}. Old: {old_wind_cols}, New: {new_cols}")
                        
                # Check 3: Ensure time column exists
                if 'time' not in new_cols:
                    errors.append(f"Missing 'time' column in {csv_file}")
                    
                # Check 4: Ensure it has 8760 or 8784 rows (1 year of hourly data)
                if len(df_new) not in [8760, 8784]:
                    warnings.append(f"{csv_file} has {len(df_new)} rows instead of 8760/8784.")
                    
            except Exception as e:
                errors.append(f"Pandas could not parse {csv_file}: {e}")

    print(f"=== VALIDATION REPORT ===")
    print(f"Total Stations Checked: {len(stations)}")
    
    if not errors and not warnings:
        print("\nSUCCESS! All new files are clean CSVs, match the old schemas perfectly, and have full 1-year hourly rows.")
    else:
        if errors:
            print("\nCRITICAL ERRORS FOUND:")
            for e in errors:
                print(f" - {e}")
                
        if warnings:
            print("\nWARNINGS:")
            for w in warnings:
                print(f" - {w}")

if __name__ == '__main__':
    validate_files()
