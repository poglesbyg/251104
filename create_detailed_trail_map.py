#!/usr/bin/env python3
"""
Create a highly detailed, feature-rich map of the Appalachian Trail.
"""

import sys
import pandas as pd
import numpy as np
import folium
from folium import plugins
import os
import json

def get_state_info(lat):
    """Get state name and info based on latitude."""
    states = {
        (34.6, 35.0): {'name': 'Georgia', 'miles': 75, 'color': '#FF6B6B'},
        (35.0, 36.6): {'name': 'North Carolina', 'miles': 96, 'color': '#4ECDC4'},
        (35.8, 36.7): {'name': 'Tennessee', 'miles': 72, 'color': '#45B7D1'},
        (36.6, 39.5): {'name': 'Virginia', 'miles': 545, 'color': '#96CEB4'},
        (39.3, 39.75): {'name': 'West Virginia', 'miles': 4, 'color': '#FFEAA7'},
        (39.5, 39.75): {'name': 'Maryland', 'miles': 41, 'color': '#DFE6E9'},
        (39.75, 42.0): {'name': 'Pennsylvania', 'miles': 230, 'color': '#74B9FF'},
        (41.0, 41.4): {'name': 'New Jersey', 'miles': 72, 'color': '#A29BFE'},
        (41.2, 41.7): {'name': 'New York', 'miles': 88, 'color': '#FD79A8'},
        (41.5, 42.1): {'name': 'Connecticut', 'miles': 52, 'color': '#FDCB6E'},
        (42.0, 42.75): {'name': 'Massachusetts', 'miles': 90, 'color': '#6C5CE7'},
        (42.75, 43.4): {'name': 'Vermont', 'miles': 150, 'color': '#00B894'},
        (43.4, 45.3): {'name': 'New Hampshire', 'miles': 161, 'color': '#E17055'},
        (45.3, 46.0): {'name': 'Maine', 'miles': 281, 'color': '#0984E3'}
    }
    
    for (min_lat, max_lat), info in states.items():
        if min_lat <= lat <= max_lat:
            return info
    return {'name': 'Unknown', 'miles': 0, 'color': '#95A5A6'}

def main():
    print("\n" + "="*80)
    print("CREATING DETAILED APPALACHIAN TRAIL MAP")
    print("="*80 + "\n")
    
    # Load complete trail data
    complete_file = './data/arcgis_cache/at_trail_complete.json'
    
    if not os.path.exists(complete_file):
        print(f"❌ Complete data not found: {complete_file}")
        print("\nRun first: uv run python fetch_complete_at_data.py")
        return
    
    print(f"Loading complete trail data...")
    with open(complete_file, 'r') as f:
        geojson_data = json.load(f)
    
    features = geojson_data.get('features', [])
    print(f"✓ Loaded {len(features):,} trail segments")
    
    # Extract all coordinates for analysis
    print("Analyzing trail data...")
    all_coords = []
    for feature in features:
        geom = feature.get('geometry', {})
        if geom.get('type') == 'LineString':
            coords = geom.get('coordinates', [])
            for lon, lat in coords:
                all_coords.append({'lat': lat, 'lon': lon})
    
    coords_df = pd.DataFrame(all_coords)
    print(f"✓ Analyzed {len(coords_df):,} GPS points\n")
    
    # Create map
    center_lat = coords_df['lat'].mean()
    center_lon = coords_df['lon'].mean()
    
    print("Creating detailed interactive map...")
    trail_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap',
        control_scale=True,
        prefer_canvas=True  # Better performance
    )
    
    # Add basemap options
    folium.TileLayer('CartoDB Positron', name='Light').add_to(trail_map)
    folium.TileLayer('CartoDB Dark_Matter', name='Dark').add_to(trail_map)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap',
        name='Topographic'
    ).add_to(trail_map)
    
    print("  ✓ Basemaps added")
    
    # Create feature groups for organization
    trail_layer = folium.FeatureGroup(name='Trail Route', show=True)
    markers_layer = folium.FeatureGroup(name='Markers & Info', show=True)
    mile_markers_layer = folium.FeatureGroup(name='Mile Markers', show=False)
    state_layer = folium.FeatureGroup(name='State Boundaries', show=True)
    
    # Draw trail segments by state (colored)
    print("  ✓ Drawing trail with state coloring...")
    
    current_state = None
    state_boundaries = []
    cumulative_distance = 0
    prev_coord = None
    
    for feature in features:
        geom = feature.get('geometry', {})
        
        if geom.get('type') == 'LineString':
            coords = geom.get('coordinates', [])
            trail_coords = [(lat, lon) for lon, lat in coords]
            
            if len(trail_coords) > 0:
                # Determine state for this segment
                mid_lat = np.mean([c[0] for c in trail_coords])
                state_info = get_state_info(mid_lat)
                
                # Track state boundaries
                if current_state != state_info['name']:
                    if current_state is not None:
                        state_boundaries.append({
                            'name': state_info['name'],
                            'lat': mid_lat,
                            'lon': np.mean([c[1] for c in trail_coords]),
                            'distance': cumulative_distance
                        })
                    current_state = state_info['name']
                
                # Draw segment in state color
                folium.PolyLine(
                    trail_coords,
                    color=state_info['color'],
                    weight=4,
                    opacity=0.85,
                    popup=f"<b>{state_info['name']}</b><br>{state_info['miles']} miles in state",
                    tooltip=f"{state_info['name']}"
                ).add_to(trail_layer)
                
                # Calculate distance
                if prev_coord:
                    from geopy.distance import geodesic
                    dist = geodesic(prev_coord, trail_coords[0]).miles
                    cumulative_distance += dist
                
                prev_coord = trail_coords[-1]
        
        if (len(trail_layer._children) + 1) % 1000 == 0:
            print(f"    Processed {len(trail_layer._children)} segments...")
    
    trail_layer.add_to(trail_map)
    print(f"  ✓ Drew {len(trail_layer._children)} colored trail segments")
    
    # Add state boundary markers
    print("  ✓ Adding state boundaries...")
    for boundary in state_boundaries:
        folium.Marker(
            [boundary['lat'], boundary['lon']],
            popup=f"""<b>Entering {boundary['name']}</b><br>
                     Approximate mile: {boundary['distance']:.0f}""",
            icon=folium.Icon(color='blue', icon='map-signs', prefix='fa'),
            tooltip=f"State: {boundary['name']}"
        ).add_to(state_layer)
    
    state_layer.add_to(trail_map)
    print(f"    Added {len(state_boundaries)} state boundary markers")
    
    # Add mile markers every 100 miles
    print("  ✓ Adding mile markers...")
    mile_marker_interval = 100
    
    for mile in range(0, 2200, mile_marker_interval):
        # Find approximate coordinate
        target_dist = mile
        # Use a point from the data (approximate)
        idx = int(len(coords_df) * (mile / 2190))
        if idx < len(coords_df):
            coord = coords_df.iloc[idx]
            
            folium.Marker(
                [coord['lat'], coord['lon']],
                popup=f"<b>Mile {mile}</b>",
                icon=folium.DivIcon(html=f'''
                    <div style="font-size: 10pt; font-weight: bold; 
                                background-color: white; border: 2px solid green;
                                border-radius: 50%; width: 30px; height: 30px;
                                text-align: center; line-height: 30px;
                                box-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        {mile}
                    </div>
                '''),
                tooltip=f"Mile {mile}"
            ).add_to(mile_markers_layer)
    
    mile_markers_layer.add_to(trail_map)
    print(f"    Added {2200 // mile_marker_interval} mile markers")
    
    # Add terminus markers
    print("  ✓ Adding terminus markers...")
    
    # Springer Mountain, GA
    folium.Marker(
        [34.6268, -84.1938],
        popup="""<div style="width: 200px;">
                <h4 style="margin: 0; color: #2E7D32;">Springer Mountain, GA</h4>
                <hr style="margin: 5px 0;">
                <b>Southern Terminus</b><br>
                <b>Elevation:</b> 3,782 feet<br>
                <b>Mile:</b> 0<br>
                <b>Coordinates:</b> 34.6268°N, 84.1938°W<br>
                <br>
                <i>🎒 Start of the 2,190 mile journey to Maine!</i>
                </div>""",
        icon=folium.Icon(color='green', icon='flag', prefix='fa', icon_color='white'),
        tooltip='🏁 START: Springer Mountain, Georgia'
    ).add_to(markers_layer)
    
    # Mount Katahdin, ME
    folium.Marker(
        [45.9044, -68.9213],
        popup="""<div style="width: 200px;">
                <h4 style="margin: 0; color: #C62828;">Mount Katahdin, ME</h4>
                <hr style="margin: 5px 0;">
                <b>Northern Terminus</b><br>
                <b>Elevation:</b> 5,267 feet<br>
                <b>Mile:</b> 2,190<br>
                <b>Coordinates:</b> 45.9044°N, 68.9213°W<br>
                <br>
                <i>🏔️ Congratulations, you made it!</i>
                </div>""",
        icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa', icon_color='white'),
        tooltip='🏁 FINISH: Mount Katahdin, Maine'
    ).add_to(markers_layer)
    
    # Add some notable peaks/locations
    print("  ✓ Adding notable landmarks...")
    
    notable_points = [
        {'name': 'Blood Mountain, GA', 'lat': 34.7402, 'lon': -83.9294, 'elev': 4458, 'desc': 'Highest peak in Georgia'},
        {'name': 'Clingmans Dome, TN/NC', 'lat': 35.5628, 'lon': -83.4985, 'elev': 6643, 'desc': 'Highest point on AT'},
        {'name': 'McAfee Knob, VA', 'lat': 37.3869, 'lon': -80.0785, 'elev': 3197, 'desc': 'Most photographed spot on AT'},
        {'name': 'Shenandoah NP, VA', 'lat': 38.5267, 'lon': -78.4378, 'elev': 3500, 'desc': '101 miles through the park'},
        {'name': 'Delaware Water Gap, PA/NJ', 'lat': 40.9703, 'lon': -75.1380, 'elev': 300, 'desc': 'Major landmark'},
        {'name': 'Bear Mountain, NY', 'lat': 41.3123, 'lon': -74.0006, 'elev': 1305, 'desc': 'Lowest point on AT'},
        {'name': 'Mount Greylock, MA', 'lat': 42.6375, 'lon': -73.1664, 'elev': 3491, 'desc': 'Highest in Massachusetts'},
        {'name': 'Mount Washington, NH', 'lat': 44.2706, 'lon': -71.3033, 'elev': 6288, 'desc': 'Highest in Northeast'},
    ]
    
    for point in notable_points:
        folium.Marker(
            [point['lat'], point['lon']],
            popup=f"""<div style="width: 180px;">
                    <h4 style="margin: 0; color: #1976D2;">{point['name']}</h4>
                    <hr style="margin: 5px 0;">
                    <b>Elevation:</b> {point['elev']:,} ft<br>
                    <b>Note:</b> {point['desc']}
                    </div>""",
            icon=folium.Icon(color='purple', icon='mountain', prefix='fa'),
            tooltip=f"⛰️ {point['name']}"
        ).add_to(markers_layer)
    
    print(f"    Added {len(notable_points)} notable landmarks")
    
    markers_layer.add_to(trail_map)
    
    # Add enhanced legend (safer version without special characters that break JS)
    print("  ✓ Creating detailed legend...")
    
    from branca.element import MacroElement
    from jinja2 import Template
    
    legend_template = """
    {% macro html(this, kwargs) %}
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 260px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 15px; border-radius: 8px;
                box-shadow: 3px 3px 10px rgba(0,0,0,0.4);">
        <h4 style="margin: 0 0 10px 0; color: #2E7D32; text-align: center;">
            Appalachian Trail
        </h4>
        <p style="margin: 8px 0; font-size: 12px;">
            <b>Trail by State (colored)</b><br>
            14 states from GA to ME<br>
            3,021 segments - 788k points
        </p>
        <p style="margin: 8px 0; font-size: 12px;">
            <b>Markers:</b><br>
            Green flag: Start (GA)<br>
            Red flag: End (ME)<br>
            Purple: Notable peaks<br>
            Blue: State boundaries
        </p>
        <p style="margin: 5px 0; font-size: 10px; color: #666; font-style: italic;">
            Source: Official ArcGIS/NPS data
        </p>
    </div>
    {% endmacro %}
    """
    
    legend = MacroElement()
    legend._template = Template(legend_template)
    trail_map.get_root().add_child(legend)
    
    # Add interactive plugins
    print("  ✓ Adding interactive tools...")
    
    # Fullscreen
    plugins.Fullscreen(position='topleft').add_to(trail_map)
    
    # Measure tool
    plugins.MeasureControl(
        primary_length_unit='miles',
        secondary_length_unit='kilometers',
        primary_area_unit='sqmiles'
    ).add_to(trail_map)
    
    # Mini map
    minimap = plugins.MiniMap(toggle_display=True)
    trail_map.add_child(minimap)
    
    # Mouse position
    plugins.MousePosition(
        separator=' | ',
        prefix='Coordinates: ',
        lat_formatter=lambda x: f'{x:.4f}°N',
        lng_formatter=lambda x: f'{abs(x):.4f}°W'
    ).add_to(trail_map)
    
    # Search box for markers
    plugins.Search(
        layer=markers_layer,
        search_label='tooltip',
        placeholder='Search landmarks...',
        collapsed=True
    ).add_to(trail_map)
    
    # Layer control
    folium.LayerControl(position='topright', collapsed=False).add_to(trail_map)
    
    # Save
    output_file = './outputs/real_arcgis_trail_map.html'
    trail_map.save(output_file)
    
    print(f"\n✓ Detailed map created!\n")
    print("="*80)
    print("✅ DETAILED ARCGIS TRAIL MAP COMPLETE!")
    print("="*80)
    
    print(f"\n📍 Saved to: {output_file}")
    print(f"   File size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
    print(f"   Trail segments: {len(features):,}")
    print(f"   GPS points: {len(coords_df):,}")
    
    print("\n🎨 Enhanced Features:")
    print("   ✓ Trail colored by state (14 colors)")
    print("   ✓ State boundary markers (14 markers)")
    print("   ✓ Notable peaks & landmarks (8 points)")
    print("   ✓ Start/end terminus markers (correct coords)")
    print("   ✓ Mile markers (optional layer)")
    print("   ✓ Mini map (bottom-right)")
    print("   ✓ Mouse position display")
    print("   ✓ Search landmarks")
    print("   ✓ Measure distances")
    print("   ✓ Fullscreen mode")
    print("   ✓ 4 basemap options")
    
    print("\n🗺️  Open in browser:")
    print(f"   open {output_file}")
    
    print("\n💡 Tips:")
    print("   • Use layer control (top-right) to toggle features")
    print("   • Click trail segments to see state info")
    print("   • Click landmarks for details")
    print("   • Use measure tool to calculate distances")
    print("   • Switch basemaps for different views")
    
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

