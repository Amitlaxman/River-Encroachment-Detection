# Main entry point for encroachment detection
# main.py

import os
import shutil
from datetime import datetime
import cv2
import numpy as np

from nvidia_api.visual_changenet import run_visual_changenet
from processing.postprocess import load_change_map, analyze_encroachment
from config.settings import (
    IMAGE_SIZE,
    EARTHDATA_USERNAME,
    EARTHDATA_PASSWORD,
    GEOJSON_PATH,
    CLOUD_COVER_THRESHOLD,
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

# Step 1: Check for input images
print("\n[Step 1] Preparing input images...")
print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE}x3")

# Prefer local images if available; otherwise download using Earthdata
before_path = BEFORE_IMAGE
after_path = AFTER_IMAGE

if os.path.exists(before_path) and os.path.exists(after_path):
    print("[+] Found local before/after images. Skipping download.")
else:
    print("[!] Local images not found. Downloading Sentinel-2 imagery...")
    if not EARTHDATA_USERNAME or not EARTHDATA_PASSWORD:
        print("[!] Earthdata credentials missing. Set EARTHDATA_USERNAME and EARTHDATA_PASSWORD.")
        exit(1)

    try:
        from data.sentinel2_downloader import get_sentinel2_images
        before_path, after_path = get_sentinel2_images(
            username=EARTHDATA_USERNAME,
            password=EARTHDATA_PASSWORD,
            geojson_path=GEOJSON_PATH,
            output_dir=os.path.join(SCRIPT_DIR, "data", "input"),
        )
    except Exception as e:
        print(f"[!] Download failed: {e}")
        exit(1)

if not (before_path and after_path and os.path.exists(before_path) and os.path.exists(after_path)):
    print("[!] Unable to obtain valid before/after images. Aborting.")
    exit(1)

print(f"[+] Before image: {before_path}")
print(f"[+] After image: {after_path}")


# Step 2: Run Visual ChangeNet
print("\n[Step 2] Running Visual ChangeNet...")
run_visual_changenet(before_path, after_path, OUTPUT_DIR)

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

# Create overlay of change_map onto the after image and save
try:
    after_img = cv2.imread(after_path)
    if after_img is None:
        raise RuntimeError("Could not read after image for overlay")

    # Ensure same size
    h, w = after_img.shape[:2]
    if change_map.shape != (h, w):
        change_resized = cv2.resize(change_map, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        change_resized = change_map

    # Normalize and threshold for mask
    change_norm = (change_resized.astype(np.float32) / 255.0)
    mask = (change_norm > 0.6).astype(np.uint8)

    # Create red overlay where mask is True
    overlay = after_img.copy()
    overlay[mask == 1] = (0, 0, 255)

    blended = cv2.addWeighted(after_img, 0.7, overlay, 0.3, 0)

    overlay_path = os.path.join(OUTPUT_DIR, "overlay_on_after.jpg")
    cv2.imwrite(overlay_path, blended)
    print(f"[+] Saved overlay image: {overlay_path}")
except Exception as e:
    print(f"[!] Could not create overlay: {e}")
