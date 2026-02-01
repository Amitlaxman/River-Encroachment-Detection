# Sentinel-2 Integration Setup Guide

## Overview
This guide explains how to set up the Sentinel-2 image downloader for the encroachment detection system.

## Prerequisites
- Python 3.7+
- Internet connection
- Earthdata account (free)
- GeoJSON file with your area of interest

## Step 1: Create an Earthdata Account

### Register for Earthdata
1. Visit https://urs.earthdata.nasa.gov/
2. Click "Register" or "Create an account"
3. Fill in the required information:
   - First Name
   - Last Name
   - Email address
   - Confirm email
4. Create a password
5. Accept the terms and click "Register"
6. Verify your email by clicking the link sent to your inbox

### Enable Sentinel-2 Access
1. Log in to your Earthdata account
2. Go to Profile → App Passwords
3. Create a new application password or note your current credentials
4. These credentials work with multiple NASA/ESA services including Sentinel-2

## Step 2: Configure Your GeoJSON

### Prepare Your Area of Interest
1. Open `encroachment_detection/data/mula_mutha_geojson.json`
2. Update coordinates with your area of interest

### GeoJSON Format
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Your Area Name"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [longitude1, latitude1],
            [longitude2, latitude2],
            [longitude3, latitude3],
            [longitude4, latitude4],
            [longitude1, latitude1]  // Close the polygon
          ]
        ]
      }
    }
  ]
}
```

### Finding Coordinates
- Use Google Maps: Right-click location → copy coordinates
- Use https://geojson.io for interactive polygon creation
- Format: [Longitude, Latitude] (not Latitude, Longitude!)
- Longitude range: -180 to +180
- Latitude range: -90 to +90

### Example: Mula Mutha River (Pune, India)
```json
{
  "coordinates": [
    [
      [73.8, 18.5],      // Southwest
      [73.95, 18.5],     // Southeast
      [73.95, 18.65],    // Northeast
      [73.8, 18.65],     // Northwest
      [73.8, 18.5]       // Close polygon
    ]
  ]
}
```

## Step 3: Set Up Environment Variables

### Create .env File
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Earthdata credentials:
   ```
   EARTHDATA_USERNAME=your_earthdata_username
   EARTHDATA_PASSWORD=your_earthdata_password
   ```

### Keep Credentials Secure
- Never commit `.env` to version control
- Use `.gitignore` to prevent accidental uploads
- Each user should have their own `.env` file
- For production, consider using AWS Secrets Manager or similar

## Step 4: Configure Detection Parameters

Edit `config/settings.py` to customize:

```python
# Maximum cloud cover percentage (0-100)
CLOUD_COVER_THRESHOLD = 20

# Image output size (model requires 416x416)
IMAGE_SIZE = 416

# Encroachment thresholds
AREA_THRESHOLD_PIXELS = 500      # Minimum changed pixels
CHANGE_RATIO_THRESHOLD = 0.02    # Minimum change ratio
```

### Parameter Guide
- **CLOUD_COVER_THRESHOLD**: 
  - Lower (0-10): Fewer available images, mostly cloud-free
  - Medium (15-25): Good balance
  - Higher (30+): More images available, some cloud cover
  
- **AREA_THRESHOLD_PIXELS**:
  - Lower: Detects smaller changes
  - Higher: Only detects significant encroachment
  
- **CHANGE_RATIO_THRESHOLD**:
  - Percentage of image showing change
  - 0.02 = 2% of image area changed

## Step 5: Install Dependencies

```bash
cd encroachment_detection
pip install -r requirements.txt
```

Required packages:
- `requests`: HTTP requests
- `numpy`: Numerical computing
- `opencv-python`: Image processing
- `rasterio`: Geospatial data I/O
- `scipy`: Scientific computing
- `matplotlib`: Visualization
- `python-dotenv`: Environment variable management
- `sentinelsat`: Sentinel-2 API access
- `geojson`: GeoJSON handling
- `pyproj`: Coordinate transformations

## Step 6: Run the System

```bash
python main.py
```

### Expected Output
```
============================================================
ENCROACHMENT DETECTION SYSTEM
============================================================

[Step 1] Downloading Sentinel-2 images...
Using credentials: your_username
Cloud cover threshold: 20%
Image size: 416x416x3

[Step 2] Running Visual ChangeNet...

[Step 3] Analyzing output...

============================================================
ANALYSIS RESULTS
============================================================
Changed pixels : 2059
Change ratio   : 0.0067

✅ NO ENCROACHMENT DETECTED
============================================================
```

## Troubleshooting

### "Connection to scihub.copernicus.eu timed out"
- **Cause**: Network connection issue or service unavailable
- **Solution**: 
  - Check internet connection
  - Try again later (service may be down for maintenance)
  - System falls back to creating synthetic test images

### "No cloud-free images found"
- **Cause**: Area has heavy cloud cover during date range
- **Solution**:
  - Increase `CLOUD_COVER_THRESHOLD` in settings
  - Try a different time period
  - Choose an area with less persistent clouds

### "Invalid credentials"
- **Cause**: Earthdata username/password incorrect
- **Solution**:
  - Verify credentials in `.env`
  - Reset password at https://urs.earthdata.nasa.gov/
  - Create new Earthdata account

### "Invalid GeoJSON"
- **Cause**: Malformed GeoJSON file
- **Solution**:
  - Validate GeoJSON at https://geojson.io
  - Ensure coordinates are [longitude, latitude]
  - Close the polygon (first and last coordinates must match)

### "Image size mismatch"
- **Cause**: Downloaded image not 416x416x3
- **Solution**: Handled automatically by image resizing in pipeline

## Advanced Configuration

### Using with Different Satellites
To integrate other satellite sources, create a new downloader:

```python
class Sentinel5Downloader:
    # For atmospheric composition
    SCIHUB_API = "https://scihub.copernicus.eu/apihub"
    
class LandsatDownloader:
    # 30m resolution, 16-day revisit
    USGS_API = "https://earthexplorer.usgs.gov"
```

### Batch Processing Multiple Areas
```python
areas = [
    "area1_geojson.json",
    "area2_geojson.json",
    "area3_geojson.json"
]

for area_file in areas:
    before, after = get_sentinel2_images(username, password, area_file, output_dir)
    results = run_encroachment_detection(before, after)
    save_results(area_file, results)
```

### Historical Analysis
Modify `main.py` to analyze multiple years:

```python
from datetime import datetime, timedelta

for year in range(2020, 2026):
    target_date = datetime(year, 2, 1)
    before_date = target_date - timedelta(days=365)
    # ... download and analyze
```

## Useful Resources

### Sentinel-2 Data
- [Sentinel-2 L2A Products](https://sentinel.esa.int/web/sentinel/missions/sentinel-2)
- [Band Descriptions](https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-2-msi/msi-instrument)
- [Product Handbook](https://sentinels.copernicus.eu/documents/247904/685211/Sentinel-2_L1C_Data_Quality_Report)

### Tools for Coordinate Discovery
- [Google Maps](https://maps.google.com)
- [GeoJSON.io](https://geojson.io) - Interactive polygon creation
- [Sentinel-2 Browse Imagery](https://scihub.copernicus.eu/dhus/#/home)
- [USGS EarthExplorer](https://earthexplorer.usgs.gov)

### NVIDIA API
- [NVIDIA NGC Catalog](https://catalog.ngc.nvidia.com/)
- [Visual ChangeNet Documentation](https://docs.nvidia.com/deeplearning/cv-sdk/using-cv-sdk.html)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the console
3. Verify configuration in `config/settings.py`
4. Check `.env` credentials
5. Validate GeoJSON format

## Security Notes

### Never Share
- `.env` files with actual credentials
- Earthdata credentials in code repositories
- API keys in public repositories

### Best Practices
- Use environment variables for sensitive data
- Rotate credentials periodically
- Monitor API usage for suspicious activity
- Keep dependencies updated for security patches
