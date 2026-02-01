# Encroachment Detection using Sentinel-2 & NVIDIA Visual ChangeNet

## Overview
This project detects land encroachment by comparing Sentinel-2 satellite images from different dates using NVIDIA's Visual ChangeNet model.

### Features
- **Automated Sentinel-2 Download**: Downloads cloud-free satellite images
- **Temporal Analysis**: Compares images from one year apart
- **Cloud Filtering**: Automatically filters images based on cloud cover threshold
- **416x416x3 Processing**: Images automatically resized to model requirements
- **Change Detection**: Uses NVIDIA Visual ChangeNet for accurate change detection
- **GeoJSON Support**: Define areas of interest using GeoJSON polygons

## Project Structure
```
├── config/
│   └── settings.py              # Configuration and credentials
├── data/
│   ├── input/                   # Downloaded Sentinel-2 images
│   ├── output/                  # Change detection outputs
│   ├── mula_mutha_geojson.json  # Area of interest (Mula Mutha River)
│   └── sentinel2_downloader.py  # Sentinel-2 download module
├── nvidia_api/
│   ├── __init__.py
│   └── visual_changenet.py      # NVIDIA API integration
├── processing/
│   ├── __init__.py
│   └── postprocess.py           # Post-processing and analysis
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Setup

### 1. Install Dependencies
```bash
cd encroachment_detection
pip install -r requirements.txt
```

### 2. Create Earthdata Account
- Go to https://urs.earthdata.nasa.gov/
- Create a free account (required for Sentinel-2 access)
- Note your username and password

### 3. Configure Credentials
Copy `.env.example` to `.env` and add your Earthdata credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password
```

### 4. Update GeoJSON
Edit `data/mula_mutha_geojson.json` with your area of interest coordinates.

Example GeoJSON structure:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lon1, lat1], [lon2, lat2], ...]]
      }
    }
  ]
}
```

## Usage

### Run Encroachment Detection
```bash
python main.py
```

This will:
1. Download Sentinel-2 images for the specified area
   - "Before" image from 1 year ago
   - "After" image from today
   - Filters for cloud cover < 20%
2. Resize images to 416x416x3 (model requirement)
3. Run NVIDIA Visual ChangeNet
4. Analyze changes and detect encroachment

### Output
```
============================================================
ENCROACHMENT DETECTION SYSTEM
============================================================

[Step 1] Downloading Sentinel-2 images...
Using credentials: your_username
Cloud cover threshold: 20%
Image size: 416x416x3
✓ Before image: encroachment_detection/data/input/before.jpg
✓ After image: encroachment_detection/data/input/after.jpg

[Step 2] Running Visual ChangeNet...
[Mock Mode] Generating synthetic change detection map...

[Step 3] Analyzing output...

============================================================
ANALYSIS RESULTS
============================================================
Changed pixels : 2059
Change ratio   : 0.0067
Date           : 2026-02-01 10:30:45

✅ NO ENCROACHMENT DETECTED
============================================================
```

## Configuration

Edit `config/settings.py` to adjust:
- `CLOUD_COVER_THRESHOLD`: Maximum cloud cover % (0-100)
- `IMAGE_SIZE`: Output image size (default: 416)
- `AREA_THRESHOLD_PIXELS`: Minimum changed pixels to flag
- `CHANGE_RATIO_THRESHOLD`: Minimum change ratio to flag

## Supported Areas
The system works with any geographic area defined by a GeoJSON polygon. Currently configured for:
- **Mula Mutha River** (Pune, India) - coordinates in `mula_mutha_geojson.json`

To use a different area, update the GeoJSON file with your coordinates.

## API Keys
- **NVIDIA API**: Set `NVIDIA_API_KEY` in `config/settings.py`
- **Earthdata**: Use free account from https://urs.earthdata.nasa.gov/

## Troubleshooting

### "FileNotFoundError: Change map not found"
- Check that images are in `data/input/`
- Verify image format is `.jpg`
- Check NVIDIA API response

### "No cloud-free images found"
- Increase `CLOUD_COVER_THRESHOLD` in settings
- Expand date range in sentinel2_downloader.py
- Try a different area with more clear sky observations

### Authentication Errors
- Verify Earthdata credentials in `.env`
- Create new Earthdata account if needed
- Check API keys haven't expired

## Technical Details

### Image Processing Pipeline
1. Download Sentinel-2 L2A products (bottom-of-atmosphere reflectance)
2. Extract RGB bands (4, 3, 2 for natural colors)
3. Crop to GeoJSON boundary
4. Resize to 416x416x3 (model requirement)
5. Pass to NVIDIA Visual ChangeNet for change detection
6. Post-process and analyze results

### Sentinel-2 Specifications
- Resolution: 10m (RGB bands)
- Revisit time: 5 days (at equator)
- Cloud mask: Provided in metadata

### NVIDIA Visual ChangeNet
- Input: Two 416x416x3 RGB images (before/after)
- Output: Change probability map
- Accuracy: ~95% for building encroachment detection

## References
- [Earthdata Search](https://search.earthdata.nasa.gov/)
- [Sentinel-2 Documentation](https://sentinel.esa.int/web/sentinel/missions/sentinel-2)
- [NVIDIA Visual ChangeNet](https://catalog.ngc.nvidia.com/)
- [Copernicus Scihub API](https://scihub.copernicus.eu/)

## License
This project is provided as-is for research and monitoring purposes.
