# Appalachian Trail Official ArcGIS Hub Guide

## 🎯 Official Data Source Found!

**URL**: [https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com)

This is the **official Appalachian Trail Natural Resource Condition Assessment Hub**, maintained by:
- National Park Service (NPS)
- Appalachian Trail Conservancy (ATC)
- Cooperative Ecosystem Studies Units (CESU)

## 📊 What's Available

This hub provides comprehensive natural resource data for the Appalachian Trail, including:

### Trail Data
- **Trail Centerline** - Official AT route with GPS coordinates
- **Trail Segments** - Broken down by management zones
- **Mile Markers** - Exact mileage points
- **Trail Conditions** - Current status and closures

### Natural Resources
- **Vegetation Coverage** - Forest types and conditions
- **Wildlife Habitats** - Protected species areas
- **Water Resources** - Streams, springs, watersheds
- **Air Quality** - Monitoring station data
- **Soil Types** - Geological information

### Infrastructure
- **Shelters** - Locations, capacity, amenities
- **Campsites** - Designated camping areas
- **Parking Areas** - Trailhead access points
- **Road Crossings** - Highway intersections

### Management Data
- **Land Ownership** - NPS, USFS, State, Private
- **Protected Areas** - Wilderness zones, conservation lands
- **Management Zones** - Administrative boundaries
- **Cultural Resources** - Historic sites

## 🔍 How to Explore the Hub

### Option 1: Web Browser (Easiest)

1. **Go directly to the datasets page**: 
   [AT NRCA Datasets](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset)
   
   Or visit the main hub: [AT NRCA Hub](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com)

2. **Browse available datasets**:
   - The datasets page shows all available layers
   - Look for trail-related data (centerline, shelters, etc.)
   - Click on any dataset for details

3. **Find REST Endpoints**:
   - Each dataset has an "API" or "View Full Details" link
   - Look for "ArcGIS REST Services Directory" link
   - Copy the service URL

4. **Example**: If you find a service like:
   ```
   https://services.arcgis.com/[ORG]/arcgis/rest/services/AT_Trail/FeatureServer
   ```

### Option 2: Automated Exploration (Using Python)

Run the hub exploration script:

```bash
uv run python explore_at_hub.py
```

This will:
- Attempt to discover available services
- Test common endpoint patterns
- Provide guidance for manual exploration

### Option 3: Direct REST API

If you know the organization ID:

```bash
# List all services
curl "https://services.arcgis.com/[ORG_ID]/arcgis/rest/services?f=json"

# Query a specific layer
curl "https://services.arcgis.com/[ORG_ID]/arcgis/rest/services/SERVICE_NAME/FeatureServer/0/query?where=1=1&f=json"
```

## 🚀 Using the Data

### Once You Find a Working Endpoint

1. **Update the integration module**:

Edit `src/arcgis_integration.py`:

```python
# Replace with your discovered endpoint
ATC_SERVICE_URL = "https://services.arcgis.com/YOUR_ORG_ID/arcgis/rest/services"
```

2. **Test the connection**:

```python
from src.arcgis_integration import ArcGISDataFetcher

fetcher = ArcGISDataFetcher()
trail_data = fetcher.fetch_trail_centerline()

if trail_data:
    print(f"Success! Found {len(trail_data['features'])} features")
```

3. **Use with existing analysis**:

```python
from src.analysis import TrailAnalyzer
from src.fkt_analysis import FKTAnalyzer

# Convert GeoJSON to DataFrame format
trail_df = convert_geojson_to_dataframe(trail_data)

# Run all analyses
analyzer = TrailAnalyzer(trail_df)
fkt = FKTAnalyzer(trail_df, analyzer)
```

## 📋 Common Service Patterns

ArcGIS services typically follow these URL patterns:

### Feature Services (Vector Data)
```
https://services.arcgis.com/[ORG]/arcgis/rest/services/[NAME]/FeatureServer/[LAYER]
```

### Map Services (Imagery/Raster)
```
https://services.arcgis.com/[ORG]/arcgis/rest/services/[NAME]/MapServer/[LAYER]
```

### Query Parameters
```
?where=1=1              # Get all features
&outFields=*            # All attributes
&returnGeometry=true    # Include geometry
&f=json                 # JSON format
```

## 💡 Tips for Finding Data

### Look for These Service Names:
- `AT_Centerline`
- `Appalachian_Trail`
- `AT_Trail_Line`
- `Trail_Segments`
- `AT_NRCA_Trail`

### Common Layer Names:
- Layer 0: Usually the main trail line
- Layer 1: Might be points (shelters, etc.)
- Layer 2: Could be polygons (zones, etc.)

### Check Metadata:
- Each service has a REST endpoint
- Look for "Service Description" link
- Check available layers and fields

## 🔧 Troubleshooting

### "Service Not Found" (404)
- The service URL may have changed
- Try browsing the hub directly
- Look for updated organization ID

### "Invalid Token" (498)
- Service may require authentication
- Check if data is public
- May need to sign up for ArcGIS account

### Empty Response
- Check the `where` clause in your query
- Verify the layer index (0, 1, 2, etc.)
- Use `returnCountOnly=true` to test

### Network Errors
- Check your internet connection
- Some services may have rate limits
- Try again later if service is down

## 📚 Additional Resources

### Documentation
- **ArcGIS REST API**: https://developers.arcgis.com/rest/
- **NPS GIS Data**: https://www.nps.gov/subjects/gis/
- **ATC Resources**: https://appalachiantrail.org

### Related Hubs
- **NPS Data Store**: https://irma.nps.gov/DataStore/
- **USGS National Map**: https://www.usgs.gov/programs/national-geospatial-program
- **Protected Areas Database**: https://www.usgs.gov/programs/gap-analysis-project

### Community
- **GeoNet (Esri Community)**: https://community.esri.com/
- **r/gis**: https://reddit.com/r/gis
- **AT Community Forums**: https://www.whiteblaze.net/

## ✅ Next Steps

1. **Browse the datasets directly**
   - Visit: [AT NRCA Datasets](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset)
   - Explore available datasets
   - Download sample data manually
   - Identify the data you need

2. **Find REST endpoints**
   - Look for "API" links on each dataset
   - Test endpoints with curl or Python
   - Document working URLs

3. **Update integration**
   - Add discovered URLs to `arcgis_integration.py`
   - Test data fetching
   - Run analysis with real data

4. **Share findings**
   - Document successful endpoints
   - Share with the community
   - Update project documentation

---

**Official Hub**: [Appalachian Trail NRCA](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com)

This is a valuable resource for any serious AT analysis! 🏔️

