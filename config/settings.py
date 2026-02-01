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
EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME", "your_username")
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASSWORD", "your_password")
# Optional Earthdata token (preferred). Set EARTHDATA_TOKEN in .env to use.
EARTHDATA_TOKEN = os.getenv("EARTHDATA_TOKEN", None)

# Get absolute path to GeoJSON file
GEOJSON_PATH = os.path.join(SCRIPT_DIR, "data", "mula_mutha_geojson.json")

# Image configuration
IMAGE_SIZE = 416  # Model requires 416x416x3 images
CLOUD_COVER_THRESHOLD = 20  # Maximum cloud cover percentage (0-100)

# Encroachment decision thresholds
AREA_THRESHOLD_PIXELS = 500
CHANGE_RATIO_THRESHOLD = 0.02

# Change classes that indicate encroachment
ENCROACHMENT_CLASSES = {
    "farmland_to_building",
    "desert_to_building",
    "water_to_building"
}
