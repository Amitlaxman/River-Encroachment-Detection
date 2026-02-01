"""
Sentinel-2 image downloader from Earth Data (NASA/USGS)
Downloads cloud-free images for before and after dates
"""

import os
import json
import requests
import numpy as np
import cv2
from datetime import datetime, timedelta
from pathlib import Path


class Sentinel2Downloader:
    """Download and process Sentinel-2 images from Earth Data"""
    
    # Copernicus Data Space Ecosystem (CDSE) API endpoint for Sentinel-2
    CDSE_SEARCH_URL = "https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json"
    
    def __init__(self, username=None, password=None, geojson_path=None, token=None):
        """
        Initialize downloader with Earthdata credentials
        
        Args:
            username: Earthdata/Sentinel username
            password: Earthdata/Sentinel password
            geojson_path: Path to GeoJSON file with area of interest (absolute or relative)
            token: Optional Bearer token for Earthdata (preferred over username/password)
        """
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()
        # Prefer token-based auth if provided
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        elif username and password:
            self.session.auth = (username, password)
        
        # Convert to absolute path if relative
        if not os.path.isabs(geojson_path):
            # Get the encroachment_detection directory
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            geojson_path = os.path.join(script_dir, geojson_path)
        
        # Load GeoJSON
        with open(geojson_path, 'r') as f:
            self.geojson = json.load(f)
        
        # Extract bounds from GeoJSON
        self.bounds = self._extract_bounds()
    
    def _extract_bounds(self):
        """Extract bounding box from GeoJSON"""
        feature = self.geojson['features'][0]
        geometry = feature['geometry']
        
        # Handle different coordinate structures
        if geometry['type'] == 'Polygon':
            coords = geometry['coordinates'][0]  # Outer ring of polygon
        elif geometry['type'] == 'MultiPolygon':
            coords = geometry['coordinates'][0][0]  # First polygon, outer ring
        else:
            coords = geometry['coordinates']
        
        # Extract longitude and latitude
        lons = [float(c[0]) for c in coords]
        lats = [float(c[1]) for c in coords]
        
        return {
            'min_lon': min(lons),
            'max_lon': max(lons),
            'min_lat': min(lats),
            'max_lat': max(lats)
        }
    
    def download_images(self, output_dir, current_date=None, cloud_threshold=20):
        """
        Download before and after Sentinel-2 images
        
        Args:
            output_dir: Directory to save images
            current_date: Current date (datetime object), defaults to today
            cloud_threshold: Maximum cloud cover percentage (0-100)
        
        Returns:
            Tuple of (before_image_path, after_image_path)
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Calculate dates
        after_date = current_date
        before_date = current_date - timedelta(days=365)
        
        print(f"Downloading Sentinel-2 images...")
        print(f"Before date: {before_date.strftime('%Y-%m-%d')}")
        print(f"After date: {after_date.strftime('%Y-%m-%d')}")
        print(f"Area: {self.bounds}")
        print(f"Max cloud cover: {cloud_threshold}%")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Download images
        before_path = self._search_and_download(
            before_date, output_dir, "before.jpg", cloud_threshold
        )
        after_path = self._search_and_download(
            after_date, output_dir, "after.jpg", cloud_threshold
        )
        
        return before_path, after_path
    
    def _search_and_download(self, target_date, output_dir, filename, cloud_threshold):
        """
        Search for and download a Sentinel-2 image
        
        Args:
            target_date: Target date for image
            output_dir: Output directory
            filename: Output filename
            cloud_threshold: Maximum cloud cover percentage
        
        Returns:
            Path to downloaded and processed image
        """
        # Build search parameters for Copernicus Data Space Ecosystem (CDSE)
        start_date = (target_date - timedelta(days=15)).strftime('%Y-%m-%dT00:00:00Z')
        end_date = (target_date + timedelta(days=15)).strftime('%Y-%m-%dT23:59:59Z')

        params = {
            'startDate': start_date,
            'completionDate': end_date,
            # cloudCover expects a range in brackets: [min,max]
            'cloudCover': f"[0,{int(cloud_threshold)}]",
            'maxRecords': 10
        }

        print(f"\nSearching for image near {target_date.strftime('%Y-%m-%d')} using CDSE...")

        try:
            # Use CDSE search URL; session headers should include Authorization if token provided
            response = self.session.get(self.CDSE_SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            features = data.get('features', [])

            if not features:
                print(f"No cloud-free images found near {target_date.strftime('%Y-%m-%d')}")
                print("Creating synthetic image for demo...")
                return self._create_synthetic_image(output_dir, filename)

            # Choose best feature (lowest cloud cover) if available
            best_feat = None
            best_cloud = None
            for feat in features:
                props = feat.get('properties', {})
                cloud = props.get('cloudCover') or props.get('cloud_cover') or props.get('eo:cloud_cover')
                try:
                    cloud_val = float(cloud) if cloud is not None else None
                except Exception:
                    cloud_val = None

                if cloud_val is not None:
                    if best_cloud is None or cloud_val < best_cloud:
                        best_cloud = cloud_val
                        best_feat = feat

            if best_feat is None:
                # fallback to first feature
                best_feat = features[0]

            # Extract identifier for downloading
            product_id = best_feat.get('id') or best_feat.get('properties', {}).get('productIdentifier') or best_feat.get('properties', {}).get('title')
            title = best_feat.get('properties', {}).get('title', product_id)

            print(f"Found image: {title} (product id: {product_id})")

            # Download using the entire feature (may contain browse/quicklook links)
            return self._download_and_process(best_feat, output_dir, filename)

        except Exception as e:
            print(f"Error downloading from CDSE: {e}")
            print("Creating synthetic image for demo...")
            return self._create_synthetic_image(output_dir, filename)
    
    def _download_and_process(self, feature_or_id, output_dir, filename):
        """
        Download Sentinel-2 product and extract RGB bands
        
        Args:
            product_id: Copernicus product ID
            output_dir: Output directory
            filename: Output filename
        
        Returns:
            Path to processed image
        """
        # Try to download a browse/quicklook image from the feature
        print(f"Downloading product {feature_or_id}...")

        # If a feature dict was passed, attempt to find a usable URL
        url = None
        if isinstance(feature_or_id, dict):
            feat = feature_or_id
            # Common locations for links
            candidates = []
            if 'links' in feat and isinstance(feat['links'], list):
                candidates.extend([l.get('href') or l.get('url') for l in feat['links']])
            props = feat.get('properties', {})
            # props may contain common keys
            for key in ('browseURL', 'browseurl', 'quicklook', 'quicklook_url', 'link', 'thumbnail', 'thumbnail_url', 'browse'):
                if key in props:
                    candidates.append(props.get(key))
            # assets or additional properties
            assets = feat.get('assets') or props.get('assets') or {}
            if isinstance(assets, dict):
                for a in assets.values():
                    if isinstance(a, dict):
                        candidates.append(a.get('href') or a.get('url'))

            # Also scan property values for any image URL
            for v in props.values():
                if isinstance(v, str) and v.lower().startswith('http') and any(ext in v.lower() for ext in ('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
                    candidates.append(v)

            # Flatten and pick first URL with an image or tiff extension
            for c in candidates:
                if not c:
                    continue
                if any(ext in c.lower() for ext in ('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
                    url = c
                    break

        # If feature_or_id is a plain id/string, we don't have links; fall back
        if not url:
            print("No browse/quicklook URL found for product; falling back to synthetic image")
            return self._create_synthetic_image(output_dir, filename)

        # Download the image
        try:
            resp = self.session.get(url, stream=True, timeout=120)
            resp.raise_for_status()
            tmp_path = os.path.join(output_dir, f"_download_tmp")
            with open(tmp_path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)

            # If image, read and resize to 416x416
            lower = url.lower()
            output_path = os.path.join(output_dir, filename)
            if any(lower.endswith(ext) for ext in ('.jpg', '.jpeg', '.png')):
                img = cv2.imread(tmp_path)
                if img is None:
                    raise ValueError("Downloaded preview is not a valid image")
                resized = cv2.resize(img, (416, 416))
                cv2.imwrite(output_path, resized)
                os.remove(tmp_path)
                print(f"Saved preview as: {output_path}")
                return output_path

            # If GeoTIFF, try to read bands using rasterio
            if any(lower.endswith(ext) for ext in ('.tif', '.tiff')):
                try:
                    import rasterio
                    with rasterio.open(tmp_path) as ds:
                        # Sentinel-2 RGB bands are usually 4(R),3(G),2(B) at 10m
                        # Attempt to read these bands (band indexes may vary)
                        # We'll try common bands: 4,3,2
                        bands = []
                        for b in (4, 3, 2):
                            try:
                                arr = ds.read(b)
                                bands.append(arr)
                            except Exception:
                                bands = []
                                break
                        if len(bands) == 3:
                            # Stack and normalize to uint8
                            rgb = np.dstack(bands)
                            # Simple rescale to 0-255
                            rgb_min, rgb_max = rgb.min(), rgb.max()
                            if rgb_max > rgb_min:
                                rgb = (rgb - rgb_min) / (rgb_max - rgb_min) * 255.0
                            rgb = rgb.astype('uint8')
                            resized = cv2.resize(rgb, (416, 416))
                            cv2.imwrite(output_path, resized)
                            os.remove(tmp_path)
                            print(f"Saved extracted RGB to: {output_path}")
                            return output_path
                except Exception as e:
                    print(f"Rasterio read failed: {e}")

            # If we get here, couldn't process downloaded file
            print("Downloaded file couldn't be processed; using synthetic image")
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return self._create_synthetic_image(output_dir, filename)

        except Exception as e:
            print(f"Error downloading preview: {e}")
            return self._create_synthetic_image(output_dir, filename)
    
    def _create_synthetic_image(self, output_dir, filename):
        """
        Create a synthetic Sentinel-2 image for demo/testing
        
        Args:
            output_dir: Output directory
            filename: Output filename
        
        Returns:
            Path to created image
        """
        # Create realistic RGB image (Sentinel-2 bands 4, 3, 2)
        # Simulate satellite imagery with terrain variations
        image = np.zeros((416, 416, 3), dtype=np.uint8)
        
        # Add terrain-like patterns
        x, y = np.meshgrid(np.linspace(0, 4, 416), np.linspace(0, 4, 416))
        
        # Red channel - vegetation indices
        image[:, :, 0] = np.uint8(100 + 50 * np.sin(x) * np.cos(y))
        
        # Green channel - vegetation
        image[:, :, 1] = np.uint8(120 + 60 * np.sin(x + 0.5) * np.cos(y + 0.5))
        
        # Blue channel - water/shadows
        image[:, :, 2] = np.uint8(80 + 40 * np.sin(x + 1) * np.cos(y + 1))
        
        # Add some realistic noise
        noise = np.random.normal(0, 5, image.shape)
        image = np.uint8(np.clip(image + noise, 0, 255))
        
        # Save image
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, image)
        print(f"Created image: {output_path}")
        
        return output_path
    
    def crop_to_geojson(self, image_path, output_path):
        """
        Crop image to GeoJSON area
        
        Args:
            image_path: Input image path
            output_path: Output image path
        
        Returns:
            Path to cropped image
        """
        image = cv2.imread(image_path)
        # For now, resize to 416x416
        # In production, would use geo-referencing to crop correctly
        resized = cv2.resize(image, (416, 416))
        cv2.imwrite(output_path, resized)
        return output_path


def get_sentinel2_images(username=None, password=None, geojson_path=None, output_dir=None, token=None):
    """
    Convenience function to download Sentinel-2 images
    
    Args:
        username: Earthdata username
        password: Earthdata password
        geojson_path: Path to GeoJSON file
        output_dir: Output directory
    
    Returns:
        Tuple of (before_image_path, after_image_path)
    """
    # Accept token passed in via username if caller uses positional args.
    # For explicit token support, caller should pass token via keyword.
    downloader = Sentinel2Downloader(username, password, geojson_path, token=token)
    before_path, after_path = downloader.download_images(output_dir)
    return before_path, after_path
