# Main entry point for encroachment detection
# main.py

import os
from datetime import datetime
from nvidia_api.visual_changenet import run_visual_changenet
from processing.postprocess import load_change_map, analyze_encroachment
from data.sentinel2_downloader import get_sentinel2_images
from config.settings import (
    EARTHDATA_USERNAME, EARTHDATA_PASSWORD, EARTHDATA_TOKEN, GEOJSON_PATH,
    IMAGE_SIZE, CLOUD_COVER_THRESHOLD
)

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Directories - use absolute paths
BEFORE_IMAGE = os.path.join(SCRIPT_DIR, "data", "input", "before.jpg")
AFTER_IMAGE = os.path.join(SCRIPT_DIR, "data", "input", "after.jpg")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "data", "output")

os.makedirs(os.path.join(SCRIPT_DIR, "data", "input"), exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("ENCROACHMENT DETECTION SYSTEM")
print("=" * 60)

# Step 1: Download Sentinel-2 images
print("\n[Step 1] Downloading Sentinel-2 images...")
print(f"Using credentials: {EARTHDATA_USERNAME}")
print(f"Cloud cover threshold: {CLOUD_COVER_THRESHOLD}%")
print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE}x3")

try:
    before_img, after_img = get_sentinel2_images(
        EARTHDATA_USERNAME,
        EARTHDATA_PASSWORD,
        GEOJSON_PATH,
        os.path.join(SCRIPT_DIR, "data", "input"),
        token=EARTHDATA_TOKEN
    )
    print(f"[+] Before image: {before_img}")
    print(f"[+] After image: {after_img}")
except Exception as e:
    print(f"[!] Warning: Could not download Sentinel-2 images: {e}")
    print("Proceeding with demo images...")

# Step 2: Run Visual ChangeNet
print("\n[Step 2] Running Visual ChangeNet...")
run_visual_changenet(BEFORE_IMAGE, AFTER_IMAGE, OUTPUT_DIR)

# Step 3: Analyze results
print("\n[Step 3] Analyzing output...")
change_map = load_change_map(OUTPUT_DIR)

encroachment, pixels, ratio = analyze_encroachment(change_map)

print("\n" + "=" * 60)
print("ANALYSIS RESULTS")
print("=" * 60)
print(f"Changed pixels : {pixels}")
print(f"Change ratio   : {ratio:.4f}")
print(f"Date           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if encroachment:
    print("\n[ALERT] ENCROACHMENT DETECTED")
else:
    print("\n[OK] NO ENCROACHMENT DETECTED")

print("=" * 60)
