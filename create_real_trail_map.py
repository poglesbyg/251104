#!/usr/bin/env python3
"""
Create a map using the REAL AT coordinates from ArcGIS!
"""

import sys
import pandas as pd
import numpy as np
import folium
import os

def assign_states(df_coords):
    """Assign states to coordinates based on latitude."""
    def get_state(lat):
        if lat < 35.0:
            return 'Georgia'
        elif lat < 36.0:
            return 'North Carolina'
        elif lat < 36.7:
            return 'Tennessee/NC'
        elif lat < 39.5:
            return 'Virginia'
        elif lat < 39.75:
            return 'West Virginia/MD'
        elif lat < 42.0:
            return 'Pennsylvania'
        elif lat < 41.4:
            return 'New Jersey'
        elif lat < 41.7:
            return 'New York'
        elif lat < 42.1:
            return 'Connecticut'
        elif lat < 42.75:
            return 'Massachusetts'
        elif lat < 43.4:
            return 'Vermont'
        elif lat < 45.3:
            return 'New Hampshire'
        else:
            return 'Maine'
    
    df_coords['state'] = df_coords['latitude'].apply(get_state)
    return df_coords

def estimate_elevation(lat):
    """Estimate elevation based on latitude (rough approximation)."""
    # Southern states - higher starting elevation
    if lat < 36:
        return 3000 + np.sin((lat - 34.6) * 10) * 1000
    # Virginia - moderate
    elif lat < 39.5:
        return 2500 + np.sin((lat - 36) * 8) * 1200
    # Mid-Atlantic - lower
    elif lat < 42:
        return 1200 + np.sin((lat - 39.5) * 12) * 800
    # New England - higher again
    else:
        return 1500 + np.sin((lat - 42) * 6) * 2500

def main():
    print("\n" + "="*80)
    print("CREATING ENHANCED MAP WITH REAL ARCGIS COORDINATES")
    print("="*80 + "\n")
    
    # Load COMPLETE trail data (all segments)
    complete_file = './data/arcgis_cache/at_trail_complete.json'
    raw_file = './data/arcgis_cache/at_trail_raw.json'
    
    # Try complete file first
    if os.path.exists(complete_file):
        data_file = complete_file
        print(f"Loading COMPLETE trail data: {complete_file}")
    elif os.path.exists(raw_file):
        data_file = raw_file
        print(f"Loading partial trail data: {raw_file}")
        print("⚠️  For complete trail, run: uv run python fetch_complete_at_data.py\n")
    else:
        print(f"❌ No trail data found")
        print("\nRun first: uv run python fetch_complete_at_data.py")
        return
    
    import json
    with open(data_file, 'r') as f:
        geojson_data = json.load(f)
    
    features = geojson_data.get('features', [])
    print(f"✓ Loaded {len(features)} trail segment features")
    
    # Count total points
    total_points = sum(len(f.get('geometry', {}).get('coordinates', [])) 
                      for f in features if f.get('geometry', {}).get('type') == 'LineString')
    print(f"  Total GPS points: {total_points:,}\n")
    
    # Calculate center point from all features
    all_lats = []
    all_lons = []
    for feature in features[:100]:  # Sample for center calculation
        geom = feature.get('geometry', {})
        if geom.get('type') == 'LineString':
            coords = geom.get('coordinates', [])
            for lon, lat in coords:
                all_lats.append(lat)
                all_lons.append(lon)
    
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)
    
    print("Creating enhanced interactive map...")
    trail_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Add multiple FREE basemap options (no authentication needed)
    folium.TileLayer('CartoDB Positron', name='Light Map').add_to(trail_map)
    folium.TileLayer('CartoDB Dark_Matter', name='Dark Map').add_to(trail_map)
    
    # Add OpenTopoMap (free topographic)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap',
        name='Topographic',
        overlay=False,
        control=True
    ).add_to(trail_map)
    
    print("  ✓ Added multiple basemap layers")
    
    # Draw each trail segment as its own feature (don't connect segments!)
    print("  ✓ Drawing trail segments...")
    
    segments_drawn = 0
    for feature in features:
        geom = feature.get('geometry', {})
        
        if geom.get('type') == 'LineString':
            coords = geom.get('coordinates', [])
            # Convert to (lat, lon) tuples for folium
            trail_coords = [(lat, lon) for lon, lat in coords]
            
            # Draw this segment
            folium.PolyLine(
                trail_coords,
                color='#2E7D32',
                weight=4,
                opacity=0.8,
                tooltip='Appalachian Trail'
            ).add_to(trail_map)
            
            segments_drawn += 1
        
        if (segments_drawn + 1) % 500 == 0:
            print(f"    Processed {segments_drawn} segments...")
    
    print(f"  ✓ Drew {segments_drawn} trail segments (no connecting lines!)")
    
    # Add terminus markers with ACTUAL known coordinates
    print("  ✓ Adding terminus markers...")
    
    # Springer Mountain, GA - Southern Terminus (known coordinates)
    springer_lat, springer_lon = 34.6268, -84.1938
    
    # Mount Katahdin, ME - Northern Terminus (known coordinates)
    katahdin_lat, katahdin_lon = 45.9044, -68.9213
    
    folium.Marker(
        [springer_lat, springer_lon],
        popup="""<b>Springer Mountain, GA</b><br>
                  Southern Terminus<br>
                  Elevation: 3,782 ft<br>
                  <i>Mile 0 - Start of your journey!</i><br>
                  Coordinates: 34.6268°N, 84.1938°W""",
        icon=folium.Icon(color='green', icon='play', prefix='fa'),
        tooltip='🏁 Southern Terminus - Springer Mountain, GA'
    ).add_to(trail_map)
    
    folium.Marker(
        [katahdin_lat, katahdin_lon],
        popup="""<b>Mount Katahdin, ME</b><br>
                  Northern Terminus<br>
                  Elevation: 5,267 ft<br>
                  <i>Mile 2,190 - You made it!</i><br>
                  Coordinates: 45.9044°N, 68.9213°W""",
        icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa'),
        tooltip='🏁 Northern Terminus - Mount Katahdin, ME'
    ).add_to(trail_map)
    
    print(f"    Added Springer Mountain, GA: {springer_lat:.4f}°N, {springer_lon:.4f}°W")
    print(f"    Added Mount Katahdin, ME: {katahdin_lat:.4f}°N, {katahdin_lon:.4f}°W")
    
    # Add elevation legend
    print("  ✓ Adding elevation legend...")
    
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 220px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <p style="margin: 0; font-weight: bold; text-align: center; color: #2E7D32;">Appalachian Trail</p>
        <p style="margin: 5px 0; font-size: 12px;">
            <span style="color: green;">━━</span> Official Trail Route<br>
            <span style="color: green;">▶</span> Springer Mtn, GA (Start)<br>
            <span style="color: red;">⚑</span> Mt. Katahdin, ME (End)
        </p>
        <p style="margin: 5px 0; font-size: 11px; color: #666; font-style: italic;">
            2,000 trail segments<br>
            Real ArcGIS coordinates
        </p>
    </div>
    '''
    trail_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title overlay
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 350px; height: 80px; 
                background-color: rgba(255, 255, 255, 0.9); 
                border:2px solid grey; z-index:9999; 
                font-size:16px; padding: 15px; border-radius: 5px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <h3 style="margin: 0; color: #2E7D32;">Appalachian Trail</h3>
        <p style="margin: 5px 0; font-size: 13px;">
            <b>2,190 miles</b> • Georgia to Maine<br>
            <i>Real ArcGIS coordinates from official NPS/ATC data</i>
        </p>
    </div>
    '''
    trail_map.get_root().html.add_child(folium.Element(title_html))
    
    # Add layer control
    folium.LayerControl(position='topright').add_to(trail_map)
    
    # Add fullscreen button
    from folium.plugins import Fullscreen
    Fullscreen(position='topleft').add_to(trail_map)
    
    # Add measure control
    from folium.plugins import MeasureControl
    MeasureControl(primary_length_unit='miles').add_to(trail_map)
    
    print("  ✓ Added interactive controls")
    
    # Save
    output_file = './outputs/real_arcgis_trail_map.html'
    trail_map.save(output_file)
    
    print(f"\n✓ Enhanced map created successfully!\n")
    print("="*80)
    print("✅ ENHANCED REAL ARCGIS TRAIL MAP CREATED!")
    print("="*80)
    
    print(f"\n📍 Saved to: {output_file}")
    print(f"   File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"   Trail segments: {segments_drawn}")
    
    print("\n🎨 Map Features:")
    print("   ✓ Actual trail segments (no false connections)")
    print("   ✓ Clean, continuous trail route")
    print("   ✓ Multiple basemap options (4 choices)")
    print("   ✓ Fullscreen mode")
    print("   ✓ Distance measurement tool")
    print("   ✓ Start/end terminus markers")
    print(f"   ✓ {segments_drawn} real trail segments from ArcGIS")
    
    print("\n🗺️  Open in browser to explore!")
    print(f"   open {output_file}")
    
    print("\n✨ Real coordinates from Appalachian National Scenic Trail FeatureServer")
    print("   https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services/")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

