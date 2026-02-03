# Configuration settings for encroachment detection
# config/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")
load_dotenv(ENV_FILE)

# NVIDIA API Configuration
NVIDIA_API_URL = "https://ai.api.nvidia.com/v1/cv/nvidia/visual-changenet"
NVIDIA_API_KEY = "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"

# Sentinel-2 Configuration
# Earthdata credentials for accessing HSL (Harmonized Sentinel-2) data
EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME", None)
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASSWORD", None)

# Legacy CDSE configuration (deprecated - use Earthdata instead)
CDSE_USERNAME = os.getenv("CDSE_USERNAME", None)
CDSE_PASSWORD = os.getenv("CDSE_PASSWORD", None)
CDSE_TOKEN = os.getenv("CDSE_TOKEN", None)

# Get absolute path to GeoJSON file
GEOJSON_PATH = os.path.join(SCRIPT_DIR, "data", "mula_mutha_geojson.json")

# Image configuration
IMAGE_SIZE = 416  # Model requires 416x416x3 images
CLOUD_COVER_THRESHOLD = 20  # Maximum cloud cover percentage (0-100)

# Image enhancement (improves contrast/saturation for hazy scenes)
ENABLE_IMAGE_ENHANCEMENT = True
PERCENTILE_LOW = 2
PERCENTILE_HIGH = 98
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = 8
SATURATION_BOOST = 1.25
GAMMA = 1.0

# Encroachment decision thresholds
AREA_THRESHOLD_PIXELS = 500
CHANGE_RATIO_THRESHOLD = 0.02

# Change classes that indicate encroachment
ENCROACHMENT_CLASSES = {
    "farmland_to_building",
    "desert_to_building",
    "water_to_building"
}

