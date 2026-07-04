import subprocess
import time
import sys

print("Starting fetch loop supervisor...")

while True:
    print("Running fetch_ninja_yearly.py...")
    # Run the fetch script
    result = subprocess.run([r"..\venv\Scripts\python.exe", "fetch_ninja_yearly.py"])
    
    if result.returncode == 0:
        print("Fetch completed successfully! Exiting supervisor.")
        break
    else:
        print("Rate limit hit or error occurred. Sleeping for 1 hour (3600 seconds)...")
        time.sleep(3600)
