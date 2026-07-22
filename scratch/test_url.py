import subprocess
import urllib.request
import time
import os

BASE_DIR = r"d:\skilite-build"

def main():
    print("Starting server...")
    proc = subprocess.Popen(
        [os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe"), "manage.py", "runserver", "127.0.0.1:8002"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)
    
    url = "http://127.0.0.1:8002/community/palettes/system-preset-construction-light/?preview_category=restaurant-food&preview_page=home&preview_device=desktop&hide_chrome=1"
    print(f"Requesting {url}...")
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            print("Status code:", resp.status)
            html = resp.read()
            print("Content length:", len(html))
            print("HTML snippet:")
            print(html[:400].decode('utf-8', errors='ignore'))
    except Exception as e:
        print("Request failed:", e)
        
    print("Terminating server...")
    proc.terminate()
    proc.wait()

if __name__ == "__main__":
    main()
