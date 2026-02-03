# Sentinel-2 Integration Setup Guide

## Overview
This guide explains how to set up Sentinel-2 image downloads using the **Copernicus Data Space Ecosystem (CDSE)** for the encroachment detection system.

## Prerequisites
- Python 3.7+
- Internet connection
- **CDSE account (free)** - NEW! We now use CDSE instead of Earthdata
- GeoJSON file with your area of interest

## Step 1: Create a CDSE Account

The system now uses **Copernicus Data Space Ecosystem (CDSE)** instead of Earthdata for better Sentinel-2 access.

### Register for CDSE
1. Visit https://dataspace.copernicus.eu/
2. Click "Register" or "Create an account"
3. Fill in the required information:
   - Email address
   - Password
   - Accept terms and conditions
4. Verify your email by clicking the link sent to your inbox
5. Your account is ready to use!

### Benefits of CDSE
- Free access to Sentinel-2 Level 2A processed data
- Better API reliability
- OAuth2 token-based authentication
- Direct access to Copernicus data

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

2. Edit `.env` with your CDSE credentials:
   ```
   # CDSE Credentials (from https://dataspace.copernicus.eu/)
   CDSE_USERNAME=your_cdse_username
   CDSE_PASSWORD=your_cdse_password
   
   # Optional: Pre-generated OAuth2 token (if available)
   # CDSE_TOKEN=your_token_here
   ```

### How It Works
- Your username and password are used to obtain an OAuth2 token from CDSE
- The token is then used for all API requests
- Tokens are automatically refreshed as needed

### Keep Credentials Secure
- Never commit `.env` to version control
- Use `.gitignore` to prevent accidental uploads
- Each user should have their own `.env` file
- For production, consider using cloud secret management services

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
  - Medium (15-25): Good balance (recommended)
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
- `requests`: HTTP requests and OAuth2
- `numpy`: Numerical computing
- `opencv-python`: Image processing
- `rasterio`: Geospatial data I/O
- `scipy`: Scientific computing
- `matplotlib`: Visualization
- `python-dotenv`: Environment variable management
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
Using CDSE credentials: your_username
Cloud cover threshold: 20%
Image size: 416x416x3

Searching for image near 2025-02-02 using CDSE...
  Bounds: {'min_lon': 73.8, 'max_lon': 73.95, ...}
  Token available: Yes

Found image: S2A_MSIL2A_20250202T... 
[+] Before image: /path/to/before.jpg
[+] After image: /path/to/after.jpg

[Step 2] Running Visual ChangeNet...

[Step 3] Analyzing output...

============================================================
ANALYSIS RESULTS
============================================================
Changed pixels : 2059
Change ratio   : 0.0067

[OK] NO ENCROACHMENT DETECTED
============================================================
```

## Troubleshooting

### "403 Client Error: Forbidden"
- **Cause**: Invalid CDSE credentials or authentication failure
- **Solution**: 
  - Verify your CDSE username and password in `.env`
  - Reset password at https://dataspace.copernicus.eu/
  - Create a new CDSE account
  - Check that your account is activated
  - Wait a few minutes for account to fully activate

### "Error downloading from CDSE"
- **Cause**: Network issue or service temporarily unavailable
- **Solution**: 
  - Check internet connection
  - Try again (CDSE may be down for maintenance)
  - System will fall back to synthetic test images

### "No cloud-free images found"
- **Cause**: Area has heavy cloud cover during the search period
- **Solution**:
  - Increase `CLOUD_COVER_THRESHOLD` in settings
  - Try a different time period (dry season often better)
  - Choose an area with less persistent clouds

### "No authorization token available"
- **Cause**: CDSE authentication disabled
- **Solution**:
  - Verify `.env` file exists with CDSE credentials
  - Check username and password are correct
  - Ensure the `.env` file is in the `encroachment_detection` directory

### "Invalid GeoJSON"
- **Cause**: Malformed GeoJSON file
- **Solution**:
  - Validate GeoJSON at https://geojson.io
  - Ensure coordinates are [longitude, latitude]
  - Close the polygon (first and last coordinates must match)
  - Check for JSON syntax errors (missing commas, brackets)

### "Connection timeout"
- **Cause**: CDSE service is slow or unreachable
- **Solution**: 
  - Check internet connection
  - Verify firewall/proxy settings
  - Try again later

## Advanced Configuration

### Using a Pre-Generated Token
If you have a pre-generated CDSE OAuth2 token, you can use it directly:

```bash
# In .env
CDSE_USERNAME=
CDSE_PASSWORD=
CDSE_TOKEN=your_long_oauth2_token_here
```

The system will use the token instead of obtaining a new one.

### Batch Processing Multiple Areas
```python
from data.sentinel2_downloader import get_sentinel2_images

areas = [
    "area1_geojson.json",
    "area2_geojson.json",
    "area3_geojson.json"
]

for area_file in areas:
    before, after = get_sentinel2_images(
        username="your_cdse_username",
        password="your_cdse_password",
        geojson_path=area_file,
        output_dir="output"
    )
```

### Historical Analysis
Modify analysis to compare multiple years:

```python
from datetime import datetime, timedelta

for year in [2020, 2021, 2022, 2023, 2024, 2025]:
    target_date = datetime(year, 2, 1)
    # ... download and analyze for each year
```

## Useful Resources

### CDSE & Sentinel-2 Data
- [CDSE Home](https://dataspace.copernicus.eu/)
- [CDSE Account Management](https://dataspace.copernicus.eu/account)
- [Sentinel-2 Documentation](https://sentinel.esa.int/web/sentinel/missions/sentinel-2)
- [Sentinel-2 L2A Product Guide](https://sentinels.copernicus.eu/documents/247904/685211/Sentinel-2_L1C_Data_Quality_Report)
- [Band Information](https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-2-msi/msi-instrument)

### Coordinate/Map Tools
- [Google Maps](https://maps.google.com)
- [GeoJSON.io](https://geojson.io) - Interactive polygon creation
- [CDSE Visualization](https://browser.dataspace.copernicus.eu/)

### References
- [OAuth2 in CDSE](https://documentation.dataspace.copernicus.eu/APIs/OData.html)
- [CDSE OData API Guide](https://documentation.dataspace.copernicus.eu/APIs/OData.html)

## Migration from Earthdata

If you were previously using Earthdata credentials, here's how to migrate:

1. Create a new CDSE account at https://dataspace.copernicus.eu/
2. Update your `.env` file with CDSE credentials
3. The code will automatically use CDSE for authentication
4. Earthdata credentials in `.env` are no longer needed (can be removed)

The system is now fully compatible with CDSE and will no longer use Earthdata endpoints.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the console
3. Verify CDSE credentials in `.env`
4. Test credentials at https://dataspace.copernicus.eu/
5. Validate GeoJSON format at https://geojson.io

## Security Notes

### Never Share
- `.env` files with actual credentials
- CDSE credentials in code repositories
- Passwords in commit messages
- API tokens in public repositories

### Best Practices
- Use environment variables for sensitive data
- Rotate credentials periodically for high-security deployments
- Monitor API usage for suspicious activity
- Keep Python dependencies updated for security patches


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
