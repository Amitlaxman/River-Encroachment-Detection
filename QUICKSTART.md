# Quick Start Guide - Sentinel-2 Encroachment Detection

## 5-Minute Setup

### 1. Get Earthdata Credentials (2 min)
```
1. Visit: https://urs.earthdata.nasa.gov/
2. Click "Register" 
3. Fill in details and create account
4. Verify email
5. Note your username and password
```

### 2. Create .env File (1 min)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password
```

### 3. Update GeoJSON (1 min)
Edit `data/mula_mutha_geojson.json` with your area:

**Option A: Use default Mula Mutha River** (ready to use)

**Option B: Use GeoJSON.io to create polygon**
1. Go to https://geojson.io
2. Draw polygon around your area
3. Copy GeoJSON
4. Replace coordinates in `mula_mutha_geojson.json`

### 4. Run System (1 min)
```bash
python main.py
```

## What Happens

```
✓ Step 1: Downloads satellite images for your area
  - "Before" image from 1 year ago
  - "After" image from today
  - Filters for cloud-free images

✓ Step 2: Runs change detection AI
  - NVIDIA Visual ChangeNet
  - Compares before/after images

✓ Step 3: Reports encroachment
  - Shows changed pixels
  - Shows change percentage
  - Flags if encroachment detected
```

## Output Example

```
============================================================
ENCROACHMENT DETECTION SYSTEM
============================================================

[Step 1] Downloading Sentinel-2 images...
✓ Before image: encroachment_detection/data/input/before.jpg
✓ After image: encroachment_detection/data/input/after.jpg

[Step 2] Running Visual ChangeNet...

[Step 3] Analyzing output...

============================================================
ANALYSIS RESULTS
============================================================
Changed pixels : 2059
Change ratio   : 0.0067
Date           : 2026-02-01 17:34:37

✅ NO ENCROACHMENT DETECTED
============================================================
```

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| `Connection timed out` | Network issue, try again later |
| `Invalid credentials` | Check `.env` file spelling |
| `Invalid GeoJSON` | Use https://geojson.io to validate |
| `No module named...` | Run `pip install -r requirements.txt` |

## File Structure

```
encroachment_detection/
├── .env                      ← Add credentials here
├── config/settings.py
├── data/
│   ├── input/               ← Downloaded images go here
│   ├── output/              ← Detection results here
│   ├── mula_mutha_geojson.json  ← Edit this for your area
│   └── sentinel2_downloader.py
├── main.py                  ← Run this
└── README.md                ← Full documentation
```

## Customize Detection

Edit `config/settings.py` to adjust:
```python
CLOUD_COVER_THRESHOLD = 20      # Cloud tolerance (0-100%)
AREA_THRESHOLD_PIXELS = 500     # Minimum change size
CHANGE_RATIO_THRESHOLD = 0.02   # Minimum change %
IMAGE_SIZE = 416                # Model requires 416x416
```

## Next Steps

1. **Get Real Credentials**: Create Earthdata account
2. **Define Your Area**: Update GeoJSON coordinates
3. **Run Detection**: Execute `python main.py`
4. **Review Results**: Check detection outputs
5. **Adjust Thresholds**: Fine-tune sensitivity

## Support Resources

- **GeoJSON Creation**: https://geojson.io
- **Coordinate Finder**: https://maps.google.com
- **Earthdata Portal**: https://earthdata.nasa.gov
- **Full Documentation**: See `README.md`
- **Setup Guide**: See `SETUP_SENTINEL2.md`

## Architecture

```
Sentinel-2 Satellite
        ↓
Download (Earthdata API)
        ↓
416x416x3 Image Processing
        ↓
NVIDIA Visual ChangeNet
        ↓
Change Detection Analysis
        ↓
Encroachment Report
```

## Key Features

- ✅ Automated satellite image download
- ✅ Cloud filtering
- ✅ 1-year temporal analysis
- ✅ Custom area support (GeoJSON)
- ✅ 416x416x3 format (model requirement)
- ✅ Change detection AI
- ✅ Automated reporting

## Security Note

**Never commit `.env` file to version control!**
- Keep credentials private
- Use `.gitignore` (already configured)
- Each user should have own `.env`

---

Ready? Start with Step 1 above! 🚀
