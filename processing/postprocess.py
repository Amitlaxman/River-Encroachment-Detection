# Post-processing module for encroachment detection results
# processing/postprocess.py

import numpy as np
import cv2
from scipy.ndimage import gaussian_filter
import os

from config.settings import AREA_THRESHOLD_PIXELS, CHANGE_RATIO_THRESHOLD


def load_change_map(output_dir):
    """Load the change detection map from output directory.
    
    NVIDIA Visual ChangeNet output files:
    - out_*.jpg: Output change detection maps
    - *.response: Metadata
    
    Returns the first valid change map found.
    """
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory not found: {output_dir}")
    
    files = os.listdir(output_dir)
    
    # Look for output images (NVIDIA format: out_*.jpg)
    for file in sorted(files):
        if file.startswith("out_") and file.endswith(".jpg"):
            filepath = os.path.join(output_dir, file)
            change_map = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if change_map is not None:
                print(f"Loaded change map: {file}")
                return change_map
    
    # Fallback: look for any PNG/JPG files
    for file in sorted(files):
        if file.endswith((".png", ".jpg", ".jpeg")) and not file.startswith("changenet"):
            filepath = os.path.join(output_dir, file)
            change_map = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if change_map is not None:
                print(f"Loaded change map: {file}")
                return change_map
    
    available_files = ", ".join([f for f in files if not f.endswith(".response") and not f.endswith(".zip")])
    if not available_files:
        available_files = "(empty directory or only metadata)"
    raise FileNotFoundError(f"Change map not found in {output_dir}. Available files: {available_files}")


def analyze_encroachment(change_map):
    change_map = change_map.astype(np.float32) / 255.0

    change_map = gaussian_filter(change_map, sigma=2)

    binary = (change_map > 0.6).astype(np.uint8)

    changed_pixels = binary.sum()
    total_pixels = binary.size
    ratio = changed_pixels / total_pixels

    encroachment = (
        changed_pixels > AREA_THRESHOLD_PIXELS and
        ratio > CHANGE_RATIO_THRESHOLD
    )

    return encroachment, changed_pixels, ratio
