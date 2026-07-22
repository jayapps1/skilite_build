import os
import subprocess
import time
import urllib.request
from html2image import Html2Image

BASE_DIR = r"d:\skilite-build"
OUTPUT_DIR = os.path.join(BASE_DIR, "project_review", "responsive_screenshots")

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of screenshots to take
SCREENSHOTS_MATRIX = [
    # 1. Desktop mode (1280px viewport width)
    {
        "filename": "restaurant-home-desktop-1280.png",
        "category": "restaurant-food",
        "page": "home",
        "device": "desktop",
        "width": 1280,
        "height": 1000,
        "selector": "#live-business-preview"
    },
    {
        "filename": "restaurant-menu-desktop-1280.png",
        "category": "restaurant-food",
        "page": "features",
        "device": "desktop",
        "width": 1280,
        "height": 1000,
        "selector": "#live-business-preview"
    },
    {
        "filename": "technology-home-desktop-1280.png",
        "category": "technology",
        "page": "home",
        "device": "desktop",
        "width": 1280,
        "height": 1000,
        "selector": "#live-business-preview"
    },
    {
        "filename": "realestate-home-desktop-1280.png",
        "category": "real-estate",
        "page": "home",
        "device": "desktop",
        "width": 1280,
        "height": 1000,
        "selector": "#live-business-preview"
    },
    {
        "filename": "community-preview-desktop-1280.png",
        "category": "construction",
        "page": "home",
        "device": "desktop",
        "width": 1400,
        "height": 900,
        "selector": None  # capture entire viewport to see the full page layout
    },

    # 2. Tablet mode (768px viewport width)
    {
        "filename": "restaurant-home-tablet-768.png",
        "category": "restaurant-food",
        "page": "home",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": "#live-business-preview"
    },
    {
        "filename": "restaurant-menu-tablet-768.png",
        "category": "restaurant-food",
        "page": "features",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": "#live-business-preview"
    },
    {
        "filename": "technology-home-tablet-768.png",
        "category": "technology",
        "page": "home",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": "#live-business-preview"
    },
    {
        "filename": "healthcare-home-tablet-768.png",
        "category": "healthcare",
        "page": "home",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": "#live-business-preview"
    },
    {
        "filename": "realestate-properties-tablet-768.png",
        "category": "real-estate",
        "page": "features",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": "#live-business-preview"
    },
    {
        "filename": "contact-page-tablet-768.png",
        "category": "technology",
        "page": "contact",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": "#live-business-preview"
    },
    {
        "filename": "profile-page-tablet-768.png",
        "category": "technology",
        "page": "profile",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": "#live-business-preview"
    },
    {
        "filename": "community-preview-tablet-768.png",
        "category": "construction",
        "page": "home",
        "device": "tablet",
        "width": 1024,
        "height": 1100,
        "selector": None
    },

    # 3. Mobile mode (390px viewport width)
    {
        "filename": "restaurant-home-mobile-390.png",
        "category": "restaurant-food",
        "page": "home",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "restaurant-menu-mobile-390.png",
        "category": "restaurant-food",
        "page": "features",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "restaurant-contact-mobile-390.png",
        "category": "restaurant-food",
        "page": "contact",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "restaurant-profile-mobile-390.png",
        "category": "restaurant-food",
        "page": "profile",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "technology-home-mobile-390.png",
        "category": "technology",
        "page": "home",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "technology-products-mobile-390.png",
        "category": "technology",
        "page": "features",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "healthcare-home-mobile-390.png",
        "category": "healthcare",
        "page": "home",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "education-courses-mobile-390.png",
        "category": "education",
        "page": "features",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "fashion-products-mobile-390.png",
        "category": "fashion",
        "page": "features",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "realestate-properties-mobile-390.png",
        "category": "real-estate",
        "page": "features",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "tourism-packages-mobile-390.png",
        "category": "hospitality-tourism",
        "page": "features",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": "#live-business-preview"
    },
    {
        "filename": "community-preview-mobile-390.png",
        "category": "construction",
        "page": "home",
        "device": "mobile",
        "width": 600,
        "height": 1200,
        "selector": None
    },

    # 4. Small Mobile mode (360px viewport width)
    {
        "filename": "restaurant-home-small-mobile-360.png",
        "category": "restaurant-food",
        "page": "home",
        "device": "mobile",
        "width": 360,
        "height": 900,
        "selector": "#live-business-preview"
    },
    {
        "filename": "technology-home-small-mobile-360.png",
        "category": "technology",
        "page": "home",
        "device": "mobile",
        "width": 360,
        "height": 900,
        "selector": "#live-business-preview"
    },
    {
        "filename": "contact-form-small-mobile-360.png",
        "category": "technology",
        "page": "contact",
        "device": "mobile",
        "width": 360,
        "height": 800,
        "selector": "#live-business-preview"
    },
    {
        "filename": "footer-small-mobile-360.png",
        "category": "technology",
        "page": "home",
        "device": "mobile",
        "width": 360,
        "height": 800,
        "selector": "#preview-footer-element"
    },

    # 5. Large Mobile mode (430px viewport width)
    {
        "filename": "restaurant-menu-large-mobile-430.png",
        "category": "restaurant-food",
        "page": "features",
        "device": "mobile",
        "width": 430,
        "height": 1000,
        "selector": "#live-business-preview"
    },
    {
        "filename": "realestate-properties-large-mobile-430.png",
        "category": "real-estate",
        "page": "features",
        "device": "mobile",
        "width": 430,
        "height": 1000,
        "selector": "#live-business-preview"
    },
    {
        "filename": "profile-page-large-mobile-430.png",
        "category": "technology",
        "page": "profile",
        "device": "mobile",
        "width": 430,
        "height": 1000,
        "selector": "#live-business-preview"
    }
]

def wait_for_server(url, timeout=15):
    """Pings local server until it is fully loaded and accepting requests."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    print("Server is UP and ready!")
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def main():
    print("Starting local Django Server for responsive screenshots acquisition...")
    server_process = subprocess.Popen(
        [os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe"), "manage.py", "runserver", "127.0.0.1:8000"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        # Ping check
        base_test_url = "http://127.0.0.1:8000/community/palettes/system-preset-construction-light/"
        if not wait_for_server(base_test_url):
            print("Error: Django development server did not boot in time. Exiting.")
            return

        print("Initializing html2image browser system...")
        hti = Html2Image()
        
        # Capture screenshots
        for config in SCREENSHOTS_MATRIX:
            filename = config["filename"]
            category = config["category"]
            page = config["page"]
            device = config["device"]
            width = config["width"]
            height = config["height"]
            
            # Construct preview page URL with custom overrides
            if filename.startswith("community-preview"):
                # Render full page chrome (aside metadata + swatches + preview site)
                url = f"{base_test_url}?preview_category={category}&preview_page={page}&preview_device={device}"
            else:
                # Render only the preview website (hide editor/community chrome borders)
                url = f"{base_test_url}?preview_category={category}&preview_page={page}&preview_device={device}&hide_chrome=1"
            
            output_filepath = os.path.join(OUTPUT_DIR, filename)
            print(f" - Capturing: {filename} at browser resolution {width}x{height}...")
            
            try:
                # Configure custom viewport size on html2image
                # Take screenshot of the entire viewport (which only contains the preview site due to hide_chrome=1)
                hti.screenshot(url=url, save_as=filename, size=(width, height))
                
                # Move from local dir to targeted folder if html2image saves in current directory
                if os.path.exists(filename):
                    os.rename(filename, output_filepath)
                    print(f"   Saved screenshot: {output_filepath}")
                else:
                    print(f"   Saved check (html2image directly resolved): {output_filepath}")
            except Exception as e:
                print(f"   Failed to capture {filename}: {e}")
            
            time.sleep(0.3)
            
    finally:
        print("Terminating Django local server process...")
        server_process.terminate()
        server_process.wait()
        print("Django server terminated successfully.")

if __name__ == "__main__":
    main()
