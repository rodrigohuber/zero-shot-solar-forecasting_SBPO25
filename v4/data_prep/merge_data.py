import os
import shutil

FETCHED_DIR = 'fetched-data'
DATA_DIR = 'data'

def merge_data():
    if not os.path.exists(FETCHED_DIR):
        print(f"Directory {FETCHED_DIR} not found.")
        return

    stations = [d for d in os.listdir(FETCHED_DIR) if os.path.isdir(os.path.join(FETCHED_DIR, d))]
    
    files_moved = 0
    for station in stations:
        fetched_station_dir = os.path.join(FETCHED_DIR, station)
        data_station_dir = os.path.join(DATA_DIR, station)
        
        # Ensure target directory exists
        os.makedirs(data_station_dir, exist_ok=True)
        
        files = [f for f in os.listdir(fetched_station_dir) if f.endswith('.csv')]
        
        for file in files:
            src = os.path.join(fetched_station_dir, file)
            dst = os.path.join(data_station_dir, file)
            
            # Move file (overwrite if exists, though it shouldn't)
            shutil.copy2(src, dst)
            files_moved += 1
            print(f"Moved {file} to {data_station_dir}")
            
    print(f"\nSUCCESS: Copied {files_moved} files from {FETCHED_DIR} to {DATA_DIR}!")

if __name__ == '__main__':
    merge_data()
