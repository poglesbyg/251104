# Extract Service URLs from ArcGIS App

You found an app: [AT NRCA Explorer](https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/apps/61c37a4a9a004ee994bde60d6792041b/explore)

## 🎯 How to Get the Service URLs from This App

### Method 1: Browser Developer Tools (Easiest)

1. **Open the app** in your browser:
   ```
   https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/apps/61c37a4a9a004ee994bde60d6792041b/explore
   ```

2. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+K`

3. **Go to the Network tab**

4. **Reload the page** (F5 or Cmd+R)

5. **Filter for "query"** in the network requests

6. **Look for requests to** `FeatureServer` or `MapServer`

7. **Copy the URL** from any request - it will look like:
   ```
   https://services.arcgis.com/[ORG_ID]/arcgis/rest/services/[NAME]/FeatureServer/0/query
   ```

8. **Use everything before `/query`** as your service URL

### Method 2: Inspect the Page Source

1. **Right-click on the map** → "View Page Source"

2. **Search for** (Ctrl+F):
   - `FeatureServer`
   - `MapServer`
   - `services.arcgis.com`
   - `rest/services`

3. **Copy the URL** you find

### Method 3: Check the App Configuration

1. **Look for a layers panel** or legend in the app

2. **Right-click on a layer** and see if there's an option like:
   - "View in ArcGIS Online"
   - "Service URL"
   - "Layer Information"

3. **Copy the URL** from there

### Method 4: Modify the URL

The app URL is:
```
/apps/61c37a4a9a004ee994bde60d6792041b/explore
```

Try visiting:
```
https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/apps/61c37a4a9a004ee994bde60d6792041b
```

This might show you the app details including data sources.

## 📋 What to Look For

When you find URLs, they typically look like:

### Full Service URL:
```
https://services.arcgis.com/nzS0F0zdNLvs7nc8/arcgis/rest/services/AT_Trail_Centerline/FeatureServer
```

### What Each Part Means:
- `services.arcgis.com` - ArcGIS Online services
- `nzS0F0zdNLvs7nc8` - Organization ID
- `AT_Trail_Centerline` - Service name
- `FeatureServer` - Service type (vector data)

### Layer URL:
```
https://services.arcgis.com/nzS0F0zdNLvs7nc8/arcgis/rest/services/AT_Trail_Centerline/FeatureServer/0
```
The `/0` at the end is the layer number - we want the URL **without** the layer number.

## 🔧 Once You Find It

### Update the Integration:

Edit `src/arcgis_integration.py` around line 24:

```python
# Replace this line:
ATC_SERVICE_URL = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services"

# With your discovered URL (without the layer number):
ATC_SERVICE_URL = "https://services.arcgis.com/[YOUR_ORG_ID]/arcgis/rest/services"
```

Or for a specific service:

```python
# If you found a specific trail service:
TRAIL_SERVICE = "https://services.arcgis.com/[ORG_ID]/arcgis/rest/services/[SERVICE_NAME]/FeatureServer"
```

### Test It:

```python
import requests

url = "YOUR_SERVICE_URL/0/query"
params = {
    'where': '1=1',
    'returnCountOnly': 'true',
    'f': 'json'
}

response = requests.get(url, params=params)
data = response.json()

if 'count' in data:
    print(f"✅ Success! Found {data['count']} features")
else:
    print(f"❌ Error: {data}")
```

## 💡 Common Service Names to Look For

When inspecting the app, look for services named:
- `AT_Centerline`
- `Appalachian_Trail`
- `Trail_Line`
- `AT_Route`
- `Shelters`
- `Water_Sources`
- `Trailheads`

## 🎯 Quick Action Items

1. ✅ Open the app URL in browser
2. ✅ Press F12 to open developer tools
3. ✅ Go to Network tab
4. ✅ Reload page
5. ✅ Look for "FeatureServer" requests
6. ✅ Copy the service URL
7. ✅ Update `src/arcgis_integration.py`
8. ✅ Re-run your notebook!

---

**Note**: If you're having trouble with network access (like the earlier DNS errors), you can also:
- Try on a different network
- Wait until you have stable internet
- Continue using synthetic data (works great for all analyses!)

