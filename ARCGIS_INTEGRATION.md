# ArcGIS Integration Guide

## Overview

The Appalachian Trail Analysis project now supports integration with **ArcGIS data sources** to enhance accuracy with real geographic data instead of synthetic data.

## 🗺️ What You Can Get from ArcGIS

### Official Trail Data
- **Exact trail coordinates** - Real GPS paths, not interpolated
- **Elevation profiles** - From USGS Digital Elevation Models (DEM)
- **Trail relocations** - Historical and current route changes

### Points of Interest
- **Shelters** - Locations, capacity, amenities
- **Water sources** - Locations and reliability ratings
- **Towns** - Nearby towns with services (groceries, lodging, etc.)
- **Road crossings** - Trailheads and parking areas
- **Viewpoints** - Notable scenic locations

### Contextual Data
- **Land ownership** - National Park Service, US Forest Service, State Parks, Private
- **Terrain types** - Vegetation, land cover, soil types
- **Protected areas** - Wilderness areas, wildlife management
- **Climate data** - Temperature, precipitation patterns
- **Trail conditions** - Current status, closures, warnings

## 📦 Installation

### Basic (Using REST APIs only)
The project already includes `requests` - no additional packages needed for basic ArcGIS REST API access.

### Advanced (Full ArcGIS Python API)
For advanced features, install the ArcGIS Python API:

```bash
uv add arcgis
```

For complete GIS capabilities:

```bash
uv add arcgis geopandas shapely rasterio
```

## 🚀 Quick Start

### 1. Basic Integration

```python
from src.arcgis_integration import ArcGISDataFetcher

# Initialize
fetcher = ArcGISDataFetcher()

# See available resources
resources = fetcher.get_arcgis_resources()
print(resources)
```

### 2. Fetch Trail Centerline

```python
# Get official trail geometry
trail_data = fetcher.fetch_trail_centerline()

if trail_data:
    features = trail_data['features']
    print(f"Fetched {len(features)} trail segments")
```

### 3. Get Elevation Data

```python
# Sample coordinates (lon, lat)
coords = [
    (-84.1938, 34.6268),  # Springer Mountain, GA
    (-84.1234, 35.4567),  # Somewhere in NC
    # ... more coordinates
]

# Fetch elevations from USGS
elevations = fetcher.fetch_elevation_profile(coords, sample_rate=10)
print(elevations)
```

### 4. Integrate with Existing Analysis

```python
from src.arcgis_integration import ArcGISDataFetcher
from src.analysis import TrailAnalyzer
from src.fkt_analysis import FKTAnalyzer

# Fetch real data
fetcher = ArcGISDataFetcher()
trail_data = fetcher.create_enhanced_dataset()

# Use with existing analyzers
analyzer = TrailAnalyzer(trail_data)
summary = analyzer.get_summary_statistics()

fkt = FKTAnalyzer(trail_data, analyzer)
fkt.print_comprehensive_report()
```

## 🔗 Data Sources

### 1. Appalachian Trail Natural Resource Condition Assessment (Official)

**Official NPS/ATC Hub**: [https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com)

This is the primary official source for AT data, maintained by the National Park Service and Appalachian Trail Conservancy.

**Alternative ATC Hub**: https://hub.arcgis.com (search "Appalachian Trail Conservancy")

Available datasets:
- Trail centerline geometry
- Shelter locations and info
- Water source locations
- Trail signs and markers
- Mile markers
- Parking areas

**Note**: Service endpoints change periodically. Check ATC's ArcGIS Hub for current URLs.

### 2. USGS National Map

**Elevation service**: https://nationalmap.gov/epqs/

Features:
- Point elevation queries
- Digital Elevation Models (DEM)
- 10-meter and 30-meter resolution
- Covers entire USA

**API Example**:
```bash
curl "https://nationalmap.gov/epqs/pqs.php?x=-84.1938&y=34.6268&units=Feet&output=json"
```

### 3. Esri Living Atlas

**URL**: https://livingatlas.arcgis.com

Provides:
- World Terrain basemaps
- Satellite imagery
- Topographic maps
- Climate layers
- Land cover data
- Hydrography

### 4. National Park Service

**GIS Data**: https://www.nps.gov/subjects/gis/

Includes:
- Park boundaries
- Facilities
- Trails (for NPS sections of AT)
- Visitor centers
- Campgrounds

## 📊 Data Integration Workflow

### Step 1: Find Current Endpoints

**Official AT Hub** (Primary Source):
```
https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com
```

Or visit ArcGIS Hub and search for "Appalachian Trail":
```
https://hub.arcgis.com/search?q=appalachian%20trail
```

Look for:
- Appalachian Trail Conservancy organization
- Official trail datasets
- REST service URLs

### Step 2: Update Service URLs

Edit `src/arcgis_integration.py`:

```python
# Update these URLs with current endpoints
ATC_SERVICE_URL = "https://services1.arcgis.com/YOUR_ORG_ID/arcgis/rest/services"
```

### Step 3: Fetch Data

```python
fetcher = ArcGISDataFetcher()

# Fetch and cache
enhanced_data = fetcher.create_enhanced_dataset(use_cache=False)

# Data is automatically cached to data/arcgis_cache/
```

### Step 4: Use with Analysis

```python
# The DataFrame format is compatible with existing analysis
from src.analysis import TrailAnalyzer
from src.visualization import TrailVisualizer

analyzer = TrailAnalyzer(enhanced_data)
visualizer = TrailVisualizer(enhanced_data)

# All existing analysis and visualizations work!
```

## 🎯 Use Cases

### 1. Accurate Elevation Profiles

```python
# Get real elevation data instead of synthetic
fetcher = ArcGISDataFetcher()

# Fetch trail coordinates from ATC
trail_geom = fetcher.fetch_trail_centerline()
coords = extract_coordinates(trail_geom)

# Get USGS elevations
elevations = fetcher.fetch_elevation_profile(coords)

# Now you have REAL elevation data!
```

### 2. Shelter Planning

```python
# Get all shelter locations
shelters = fetcher.fetch_trail_features('shelters')

# Calculate distances between shelters
shelter_distances = calculate_distances(shelters)

# Plan daily mileage based on shelter spacing
```

### 3. Water Source Analysis

```python
# Fetch water sources
water = fetcher.fetch_trail_features('water')

# Analyze water availability by section
water_gaps = analyze_water_gaps(water)

# Warn about sections with limited water
```

### 4. Enhanced Daylight Analysis

```python
# Use real coordinates for accurate daylight calculations
from src.daylight_analysis import DaylightAnalyzer

daylight = DaylightAnalyzer(enhanced_data)
# Now calculations use actual latitude changes along real trail
```

## 🔧 Configuration

### Authentication (if needed)

For private/organizational data:

```python
from arcgis.gis import GIS

# Login with credentials
gis = GIS("https://www.arcgis.com", "username", "password")

# Or use API key
gis = GIS("https://www.arcgis.com", api_key="YOUR_API_KEY")
```

### Caching

Data is automatically cached to avoid repeated API calls:

```python
fetcher = ArcGISDataFetcher(cache_dir='./my_cache')

# Use cached data
data = fetcher.create_enhanced_dataset(use_cache=True)

# Force refresh
data = fetcher.create_enhanced_dataset(use_cache=False)
```

## 💡 Best Practices

### 1. Respect API Limits
- Use sample_rate to reduce elevation API calls
- Cache downloaded data locally
- Add delays between requests if needed

### 2. Validate Data
- Check for NULL elevations
- Verify coordinate bounds
- Compare with known values

### 3. Handle Errors Gracefully
- API endpoints may change
- Services may be temporarily unavailable
- Fall back to synthetic data if needed

### 4. Attribute Data Sources
```python
# Always note data source in outputs
metadata = {
    'data_source': 'ArcGIS/ATC',
    'fetch_date': '2024-11-05',
    'elevation_source': 'USGS National Map'
}
```

## 📈 Comparison: Synthetic vs Real Data

### Synthetic Data (Current Default)
✅ Always available (no internet needed)
✅ Fast generation
✅ Good for demonstration/testing
✅ Consistent results
❌ Approximate elevations
❌ Interpolated coordinates
❌ No real trail features

### Real ArcGIS Data
✅ Actual trail geometry
✅ Real elevation from USGS DEM
✅ Authentic trail features
✅ Current trail conditions
❌ Requires internet connection
❌ API endpoints may change
❌ Rate limits on API calls

## 🚧 Troubleshooting

### Problem: 400/404 errors from API

**Solution**: Service URLs have changed. Check ArcGIS Hub for current endpoints.

### Problem: Elevation API returns 301/302

**Solution**: USGS may have moved the service. Check https://nationalmap.gov for current API docs.

### Problem: No features returned

**Solution**: 
- Verify the service is public (may require authentication)
- Check the `where` clause in query
- Verify layer index (0, 1, 2, etc.)

### Problem: Slow elevation fetches

**Solution**:
- Increase `sample_rate` to query fewer points
- Cache results locally
- Use batch elevation services if available

## 📚 Additional Resources

### Documentation
- **ArcGIS REST API**: https://developers.arcgis.com/rest/
- **ArcGIS Python API**: https://developers.arcgis.com/python/
- **USGS Services**: https://nationalmap.gov/epqs/
- **GeoJSON Spec**: https://geojson.org/

### Tutorials
- ArcGIS Python API Guide: https://developers.arcgis.com/python/guide/
- REST API Query Guide: https://developers.arcgis.com/rest/services-reference/
- Elevation Services: https://www.usgs.gov/ngp-standards-and-specifications

### Community
- Esri GeoNet: https://community.esri.com/
- ArcGIS Hub: https://hub.arcgis.com/
- r/gis on Reddit: https://reddit.com/r/gis

## 🎯 Next Steps

1. **Explore ArcGIS Hub** for AT datasets
2. **Test USGS elevation API** with sample coordinates  
3. **Update service URLs** in `arcgis_integration.py`
4. **Fetch small dataset** to test integration
5. **Run analysis** with real data
6. **Compare results** with synthetic data
7. **Share findings** with the community!

## 💻 Example: Complete Integration

```python
#!/usr/bin/env python3
"""Complete ArcGIS integration example."""

from src.arcgis_integration import ArcGISDataFetcher
from src.analysis import TrailAnalyzer
from src.fkt_analysis import FKTAnalyzer
from src.daylight_analysis import DaylightAnalyzer
from src.visualization import TrailVisualizer

def main():
    # Step 1: Fetch real data
    print("Fetching ArcGIS data...")
    fetcher = ArcGISDataFetcher()
    trail_data = fetcher.create_enhanced_dataset()
    
    if trail_data is None:
        print("Falling back to synthetic data")
        from src.data_loader import load_or_generate_data
        trail_data, _ = load_or_generate_data('./data/trail_data.csv')
    
    # Step 2: Run all analyses with real data
    print("Running analyses...")
    analyzer = TrailAnalyzer(trail_data)
    fkt = FKTAnalyzer(trail_data, analyzer)
    daylight = DaylightAnalyzer(trail_data)
    
    # Step 3: Generate visualizations
    print("Creating visualizations...")
    viz = TrailVisualizer(trail_data, './outputs')
    viz.create_dashboard(analyzer)
    
    # Step 4: Print reports
    print("="*70)
    print("ANALYSIS WITH REAL ARCGIS DATA")
    print("="*70)
    
    summary = analyzer.get_summary_statistics()
    print(summary)
    
    fkt.print_comprehensive_report(
        include_daylight=True,
        daylight_analyzer=daylight
    )
    
    print("\n✅ Complete analysis with real ArcGIS data!")

if __name__ == '__main__':
    main()
```

---

**Ready to enhance your analysis with real data? Run:**

```bash
python arcgis_example.py
```

This will guide you through the integration process step by step!

