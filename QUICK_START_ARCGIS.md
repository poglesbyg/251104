# Quick Start: Using Real ArcGIS Data

## 🎯 Official AT Data Source

**Direct Link to Datasets**: [Browse AT Datasets](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset)

This page shows all available Appalachian Trail datasets from the official NPS/ATC hub.

## 🚀 3-Step Process to Get Real Data

### Step 1: Find a Dataset (5 minutes)

1. Visit: [AT NRCA Datasets](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset)

2. Look for datasets like:
   - "Trail Centerline"
   - "AT Trail Line" 
   - "Shelters"
   - "Water Sources"
   - "Parking Areas"

3. Click on a dataset you want

4. On the dataset page, look for:
   - "View API" button
   - "Service URL" link
   - "ArcGIS REST Services Directory" link

5. Copy the service URL (will look like):
   ```
   https://services.arcgis.com/[ID]/arcgis/rest/services/[NAME]/FeatureServer
   ```

### Step 2: Update Integration (2 minutes)

1. Open `src/arcgis_integration.py`

2. Find this line (around line 24):
   ```python
   ATC_SERVICE_URL = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services"
   ```

3. Replace with your discovered URL:
   ```python
   ATC_SERVICE_URL = "YOUR_DISCOVERED_URL_HERE"
   ```

4. Save the file

### Step 3: Fetch and Use Data (1 minute)

```python
from src.arcgis_integration import ArcGISDataFetcher
from src.analysis import TrailAnalyzer

# Fetch real data
fetcher = ArcGISDataFetcher()
trail_data = fetcher.fetch_trail_centerline()

if trail_data:
    print("✓ Successfully fetched real AT data!")
    
    # Use with existing analysis
    analyzer = TrailAnalyzer(trail_data)
    summary = analyzer.get_summary_statistics()
    print(summary)
else:
    print("⚠ Couldn't fetch - check the service URL")
```

## 📋 What to Look For

### Trail Geometry
Search for: "centerline", "trail line", "AT route"
- This gives you the exact GPS path of the trail
- Use for: Distance calculations, elevation profiles, mapping

### Points of Interest
Search for: "shelter", "water", "parking", "trailhead"
- Locations of facilities and features
- Use for: Planning analysis, resource availability

### Elevation Data
Search for: "DEM", "elevation", "contour"
- Real elevation measurements
- Use for: Accurate elevation profiles, difficulty analysis

## 🔍 How to Identify the Right Service URL

When you click on a dataset, you'll see:

1. **Overview Tab**: Description of the data
2. **API Tab**: Service URL and examples
3. **Data Tab**: Preview of actual data

The service URL format:
```
https://services.arcgis.com/[ORG_ID]/arcgis/rest/services/[SERVICE_NAME]/[TYPE]/[LAYER]
```

Where:
- `[ORG_ID]`: Organization identifier (long alphanumeric string)
- `[SERVICE_NAME]`: Name of the dataset
- `[TYPE]`: Usually `FeatureServer` (vector) or `MapServer` (raster)
- `[LAYER]`: Layer number (0, 1, 2, etc.)

## ✅ Testing Your Connection

Quick test in Python:

```python
import requests

# Your discovered URL
service_url = "YOUR_SERVICE_URL_HERE"

# Test query - just count features
params = {
    'where': '1=1',
    'returnCountOnly': 'true',
    'f': 'json'
}

response = requests.get(f"{service_url}/query", params=params)
data = response.json()

if 'count' in data:
    print(f"✓ Success! Found {data['count']} features")
else:
    print(f"⚠ Error: {data.get('error', 'Unknown error')}")
```

## 🎨 Example: Complete Workflow

```python
#!/usr/bin/env python3
"""Fetch and analyze real AT data."""

from src.arcgis_integration import ArcGISDataFetcher
from src.analysis import TrailAnalyzer
from src.fkt_analysis import FKTAnalyzer
from src.daylight_analysis import DaylightAnalyzer
from src.visualization import TrailVisualizer

# Step 1: Fetch real data
print("Fetching real AT data...")
fetcher = ArcGISDataFetcher()
trail_data = fetcher.create_enhanced_dataset(use_cache=False)

if trail_data is None:
    print("Couldn't fetch real data, using synthetic")
    from src.data_loader import load_or_generate_data
    trail_data, _ = load_or_generate_data('./data/trail_data.csv')

# Step 2: Run analyses
print("Analyzing trail data...")
analyzer = TrailAnalyzer(trail_data)
fkt = FKTAnalyzer(trail_data, analyzer)
daylight = DaylightAnalyzer(trail_data)

# Step 3: Generate visualizations
print("Creating visualizations...")
viz = TrailVisualizer(trail_data, './outputs')
viz.create_dashboard(analyzer)

# Step 4: Print reports
summary = analyzer.get_summary_statistics()
print(f"\n✓ Analyzed {summary['total_distance_miles']:.1f} miles")
print(f"✓ Total elevation gain: {summary['total_elevation_gain_ft']:,.0f} feet")

fkt.print_comprehensive_report(
    include_daylight=True,
    daylight_analyzer=daylight
)

print("\n🎉 Complete analysis with real data!")
```

## 💡 Pro Tips

### 1. Start Small
- Test with one dataset first
- Try a point layer (shelters) before lines (trail)
- Verify data quality before full integration

### 2. Cache Everything
- Real data takes time to fetch
- Always cache locally after first fetch
- Set `use_cache=True` in subsequent runs

### 3. Check Data Format
- Ensure coordinates are in correct format (lat/lon)
- Verify elevation units (feet vs meters)
- Check for NULL values

### 4. Respect API Limits
- Add delays between requests
- Don't fetch unnecessarily
- Use sample_rate for elevation queries

## 🔧 Troubleshooting

### "Service not found"
- The dataset may be private or removed
- Try a different dataset from the hub
- Check if you need to sign in

### "No features returned"
- Layer index might be wrong (try 0, 1, 2)
- Service URL might be incomplete
- Add `/0` at the end for first layer

### "Invalid parameters"
- Check query syntax in REST docs
- Use `f=json` for JSON format
- Ensure `where=1=1` to get all features

### Network errors (like you experienced)
- This is normal without internet
- All analysis works fine with synthetic data
- Try ArcGIS integration when online

## 📊 What You Get

With real ArcGIS data:

| Feature | Synthetic | Real ArcGIS |
|---------|-----------|-------------|
| Trail Path | Interpolated | ✓ Exact GPS |
| Elevation | Modeled | ✓ USGS DEM |
| Shelters | None | ✓ Real locations |
| Water | None | ✓ Source locations |
| Accuracy | ~Good | ✓ Official |

## 🎯 Recommended Datasets to Find

Priority order:

1. **Trail Centerline** - Most important
   - Exact route with coordinates
   - Essential for accurate analysis

2. **Elevation Profile** - Second priority
   - Real USGS measurements
   - Better than synthetic elevation

3. **Shelters** - Nice to have
   - Planning and analysis
   - Spacing between facilities

4. **Water Sources** - Nice to have
   - Resource availability
   - Dry section identification

## 📚 Resources

- **Datasets**: [Browse AT Data](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset)
- **Main Hub**: [AT NRCA](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com)
- **API Docs**: [ArcGIS REST](https://developers.arcgis.com/rest/)

---

**Ready to fetch real data?** Visit the [datasets page](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset) and start exploring! 🗺️

