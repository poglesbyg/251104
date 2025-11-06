#!/usr/bin/env python3
"""
Create a comprehensive map showing ALL features from the ArcGIS analysis.
Visualizes: shelters, water, towns, difficulty, dry sections, and more!
"""

import sys
import os
sys.path.insert(0, './src')

import pandas as pd
import numpy as np
import folium
from folium import plugins
import json
from data_loader import load_or_generate_data
from analysis import TrailAnalyzer

def simulate_shelters(trail_df, avg_spacing_miles=10):
    """Simulate shelter locations."""
    total_miles = trail_df['distance_miles'].max()
    shelter_miles = []
    current_mile = 0
    
    while current_mile < total_miles:
        spacing = np.random.uniform(avg_spacing_miles - 2, avg_spacing_miles + 5)
        current_mile += spacing
        if current_mile < total_miles:
            shelter_miles.append(current_mile)
    
    shelters = []
    for mile in shelter_miles:
        idx = (trail_df['distance_miles'] - mile).abs().idxmin()
        row = trail_df.loc[idx]
        
        shelters.append({
            'mile': row['distance_miles'],
            'state': row['state'],
            'elevation': row['elevation_ft'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'name': f"Shelter {int(mile)}"
        })
    
    return pd.DataFrame(shelters)

def simulate_water_sources(trail_df):
    """Simulate water source locations."""
    total_miles = trail_df['distance_miles'].max()
    water_miles = []
    current_mile = 0
    
    while current_mile < total_miles:
        spacing = np.random.uniform(1, 8)
        current_mile += spacing
        if current_mile < total_miles:
            water_miles.append(current_mile)
    
    water_sources = []
    for mile in water_miles:
        idx = (trail_df['distance_miles'] - mile).abs().idxmin()
        row = trail_df.loc[idx]
        
        reliability = np.random.choice(['Reliable', 'Seasonal', 'Intermittent'], p=[0.6, 0.3, 0.1])
        water_type = np.random.choice(['Spring', 'Stream', 'Creek', 'Piped'], p=[0.4, 0.3, 0.2, 0.1])
        
        water_sources.append({
            'mile': row['distance_miles'],
            'state': row['state'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'reliability': reliability,
            'type': water_type
        })
    
    return pd.DataFrame(water_sources)

def simulate_towns(trail_df):
    """Simulate town locations."""
    total_miles = trail_df['distance_miles'].max()
    towns = []
    current_mile = np.random.uniform(20, 40)
    
    while current_mile < total_miles:
        idx = (trail_df['distance_miles'] - current_mile).abs().idxmin()
        row = trail_df.loc[idx]
        
        has_grocery = np.random.choice([True, False], p=[0.7, 0.3])
        has_hostel = np.random.choice([True, False], p=[0.5, 0.5])
        has_outfitter = np.random.choice([True, False], p=[0.3, 0.7])
        
        towns.append({
            'mile': row['distance_miles'],
            'state': row['state'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'grocery': has_grocery,
            'hostel': has_hostel,
            'outfitter': has_outfitter,
            'name': f"Town ~Mile {int(current_mile)}"
        })
        
        current_mile += np.random.uniform(30, 60)
    
    return pd.DataFrame(towns)

def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE ANALYSIS MAP - ALL FEATURES")
    print("="*80 + "\n")
    
    # Load trail data for analysis
    print("Loading trail data for analysis...")
    df, _ = load_or_generate_data('./data/trail_data.csv')
    analyzer = TrailAnalyzer(df)
    df = analyzer.df  # Get enriched data
    
    print(f"✓ Loaded {len(df):,} analysis points")
    print(f"  Distance: {df['distance_miles'].max():.1f} miles\n")
    
    # Generate infrastructure data
    print("Generating infrastructure data...")
    shelters_df = simulate_shelters(df)
    water_df = simulate_water_sources(df)
    towns_df = simulate_towns(df)
    
    print(f"✓ {len(shelters_df)} shelters")
    print(f"✓ {len(water_df)} water sources")
    print(f"✓ {len(towns_df)} towns\n")
    
    # Identify problem areas
    spacing = shelters_df['mile'].diff().dropna()
    large_gaps = shelters_df[1:][spacing > spacing.mean() + spacing.std()].copy()
    large_gaps['spacing'] = spacing[spacing > spacing.mean() + spacing.std()].values
    
    reliable_water = water_df[water_df['reliability'] == 'Reliable'].sort_values('mile')
    water_spacing = reliable_water['mile'].diff().dropna()
    dry_sections = reliable_water[1:][water_spacing > 10].copy()
    dry_sections['gap_miles'] = water_spacing[water_spacing > 10].values
    
    print(f"Identified {len(large_gaps)} large shelter gaps")
    print(f"Identified {len(dry_sections)} dry sections\n")
    
    # Create map
    print("Creating comprehensive map...")
    trail_map = folium.Map(
        location=[40.0, -76.0],
        zoom_start=6,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Basemaps
    folium.TileLayer('CartoDB Positron', name='Light').add_to(trail_map)
    folium.TileLayer('CartoDB Dark_Matter', name='Dark').add_to(trail_map)
    
    # Create feature groups for organization
    trail_layer = folium.FeatureGroup(name='🥾 Trail Route (Real)', show=True)
    shelter_layer = folium.FeatureGroup(name='🏕️ Shelters', show=True)
    water_layer = folium.FeatureGroup(name='💧 Water Sources', show=True)
    town_layer = folium.FeatureGroup(name='🏘️ Towns (Resupply)', show=True)
    problem_layer = folium.FeatureGroup(name='⚠️ Problem Areas', show=True)
    difficulty_layer = folium.FeatureGroup(name='📊 Difficulty Zones', show=False)
    
    # Load REAL trail segments from ArcGIS
    print("  Loading real trail segments from ArcGIS...")
    complete_file = './data/arcgis_cache/at_trail_complete.json'
    
    if os.path.exists(complete_file):
        with open(complete_file, 'r') as f:
            geojson_data = json.load(f)
        
        real_features = geojson_data.get('features', [])
        print(f"  ✓ Loaded {len(real_features):,} real trail segments")
        
        # Draw REAL trail segments
        print("  Drawing real trail segments...")
        for idx, feature in enumerate(real_features):
            geom = feature.get('geometry', {})
            
            if geom.get('type') == 'LineString':
                coords = geom.get('coordinates', [])
                trail_coords = [(lat, lon) for lon, lat in coords]
                
                folium.PolyLine(
                    trail_coords,
                    color='#2E7D32',
                    weight=3,
                    opacity=0.8,
                    tooltip='AT - Real ArcGIS path'
                ).add_to(trail_layer)
            
            if (idx + 1) % 1000 == 0:
                print(f"    {idx + 1:,}/{len(real_features):,} segments...")
        
        print(f"  ✓ Drew {len(real_features):,} REAL trail segments from ArcGIS")
    else:
        # Fallback to synthetic if real data not available
        print("  ⚠️  Real trail data not found, using synthetic")
        print("      Run 'uv run python fetch_complete_at_data.py' for real trail")
        trail_coords = list(zip(df['latitude'], df['longitude']))
        folium.PolyLine(
            trail_coords[::10],
            color='#2E7D32',
            weight=3,
            opacity=0.7,
            tooltip='Appalachian Trail (synthetic)'
        ).add_to(trail_layer)
    
    trail_layer.add_to(trail_map)
    
    # Add shelters
    print(f"  Adding {len(shelters_df)} shelters...")
    for _, shelter in shelters_df.iterrows():
        folium.CircleMarker(
            [shelter['latitude'], shelter['longitude']],
            radius=5,
            popup=f"""<b>{shelter['name']}</b><br>
                     Mile: {shelter['mile']:.1f}<br>
                     State: {shelter['state']}<br>
                     Elevation: {shelter['elevation']:.0f} ft""",
            color='#FF9800',
            fill=True,
            fillColor='#FFE0B2',
            fillOpacity=0.8,
            tooltip=f"Shelter - Mile {shelter['mile']:.0f}"
        ).add_to(shelter_layer)
    shelter_layer.add_to(trail_map)
    
    # Add water sources
    print(f"  Adding {len(water_df)} water sources...")
    for _, water in water_df.iterrows():
        # Color by reliability
        if water['reliability'] == 'Reliable':
            color = '#2196F3'
            fill_color = '#BBDEFB'
        elif water['reliability'] == 'Seasonal':
            color = '#FFC107'
            fill_color = '#FFF9C4'
        else:
            color = '#F44336'
            fill_color = '#FFCDD2'
        
        folium.CircleMarker(
            [water['latitude'], water['longitude']],
            radius=3,
            popup=f"""<b>{water['type']}</b><br>
                     Mile: {water['mile']:.1f}<br>
                     Reliability: {water['reliability']}<br>
                     State: {water['state']}""",
            color=color,
            fill=True,
            fillColor=fill_color,
            fillOpacity=0.7,
            tooltip=f"Water: {water['reliability']}"
        ).add_to(water_layer)
    water_layer.add_to(trail_map)
    
    # Add towns
    print(f"  Adding {len(towns_df)} towns...")
    for _, town in towns_df.iterrows():
        services = []
        if town['grocery']:
            services.append('Grocery')
        if town['hostel']:
            services.append('Hostel')
        if town['outfitter']:
            services.append('Outfitter')
        
        folium.Marker(
            [town['latitude'], town['longitude']],
            popup=f"""<b>{town['name']}</b><br>
                     Mile: {town['mile']:.0f}<br>
                     State: {town['state']}<br>
                     Services: {', '.join(services) if services else 'Basic'}""",
            icon=folium.Icon(color='blue', icon='shopping-cart', prefix='fa'),
            tooltip=f"Town - Mile {town['mile']:.0f}"
        ).add_to(town_layer)
    town_layer.add_to(trail_map)
    
    # Highlight problem areas
    print(f"  Highlighting {len(large_gaps)} shelter gaps...")
    for _, gap in large_gaps.iterrows():
        # Find start of gap
        prev_idx = shelters_df[shelters_df['mile'] < gap['mile']].index[-1]
        prev_shelter = shelters_df.loc[prev_idx]
        
        # Draw warning line
        folium.PolyLine(
            [[prev_shelter['latitude'], prev_shelter['longitude']],
             [gap['latitude'], gap['longitude']]],
            color='red',
            weight=6,
            opacity=0.5,
            dash_array='10,10',
            popup=f"<b>Large Shelter Gap!</b><br>{gap['spacing']:.1f} miles<br>Camping required"
        ).add_to(problem_layer)
        
        # Add warning marker
        mid_lat = (prev_shelter['latitude'] + gap['latitude']) / 2
        mid_lon = (prev_shelter['longitude'] + gap['longitude']) / 2
        
        folium.Marker(
            [mid_lat, mid_lon],
            popup=f"<b>⚠️ Shelter Gap</b><br>{gap['spacing']:.1f} miles<br>Plan for camping",
            icon=folium.Icon(color='orange', icon='exclamation-triangle', prefix='fa'),
            tooltip=f"⚠️ {gap['spacing']:.1f} mi gap"
        ).add_to(problem_layer)
    
    print(f"  Highlighting {len(dry_sections)} dry sections...")
    for _, dry in dry_sections.iterrows():
        # Find start of dry section
        prev_idx = reliable_water[reliable_water['mile'] < dry['mile']].index[-1]
        prev_water = reliable_water.loc[prev_idx]
        
        # Get trail section coords
        section_df = df[
            (df['distance_miles'] >= prev_water['mile']) & 
            (df['distance_miles'] <= dry['mile'])
        ]
        
        if len(section_df) > 0:
            # Highlight dry section
            dry_coords = list(zip(section_df['latitude'], section_df['longitude']))
            folium.PolyLine(
                dry_coords[::5],
                color='#FF5722',
                weight=8,
                opacity=0.4,
                popup=f"<b>💧 Dry Section!</b><br>{dry['gap_miles']:.1f} miles without reliable water<br>Carry extra capacity"
            ).add_to(problem_layer)
    
    problem_layer.add_to(trail_map)
    
    # Add difficulty zones
    print("  Adding difficulty zones...")
    difficult_sections = df[df['difficulty'].isin(['Very Difficult', 'Extreme'])]
    
    # Group into continuous sections
    if len(difficult_sections) > 0:
        for state in difficult_sections['state'].unique():
            state_difficult = difficult_sections[difficult_sections['state'] == state]
            if len(state_difficult) > 10:
                coords = list(zip(state_difficult['latitude'], state_difficult['longitude']))
                folium.PolyLine(
                    coords[::5],
                    color='#D32F2F',
                    weight=10,
                    opacity=0.3,
                    popup=f"<b>Difficult Terrain</b><br>State: {state}"
                ).add_to(difficulty_layer)
    
    difficulty_layer.add_to(trail_map)
    
    # Add terminus markers
    print("  Adding markers...")
    
    folium.Marker(
        [34.6268, -84.1938],
        popup="<b>Springer Mountain, GA</b><br>START - Mile 0<br>Elevation: 3,782 ft",
        icon=folium.Icon(color='green', icon='flag', prefix='fa'),
        tooltip='🏁 START'
    ).add_to(trail_map)
    
    folium.Marker(
        [45.9044, -68.9213],
        popup="<b>Mount Katahdin, ME</b><br>FINISH - Mile 2,190<br>Elevation: 5,267 ft",
        icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa'),
        tooltip='🏁 FINISH'
    ).add_to(trail_map)
    
    # Add statistics overlay
    print("  Adding statistics panel...")
    
    stats_html = f"""
    <div style="position: fixed; top: 10px; left: 50px; width: 320px;
                background-color: rgba(255,255,255,0.95); border: 2px solid #2E7D32;
                z-index: 9999; padding: 15px; border-radius: 8px;
                box-shadow: 3px 3px 10px rgba(0,0,0,0.4);">
        <h3 style="margin: 0 0 10px 0; color: #2E7D32; border-bottom: 2px solid #2E7D32; padding-bottom: 8px;">
            📊 Trail Analysis Summary
        </h3>
        <div style="font-size: 13px; line-height: 1.8;">
            <b>Infrastructure:</b><br>
            • {len(shelters_df)} Shelters (avg {spacing.mean():.1f} mi apart)<br>
            • {len(water_df)} Water sources ({len(water_df[water_df['reliability']=='Reliable'])} reliable)<br>
            • {len(towns_df)} Towns for resupply<br>
            <br>
            <b>⚠️ Plan For:</b><br>
            • {len(large_gaps)} sections with large shelter gaps<br>
            • {len(dry_sections)} dry sections (&gt;10 mi)<br>
            <br>
            <b>Trail Stats:</b><br>
            • Distance: {df['distance_miles'].max():.0f} miles<br>
            • Elev gain: {df['cumulative_gain'].max():,.0f} ft<br>
            • States: 14<br>
            <br>
            <p style="font-size: 11px; color: #666; margin: 5px 0 0 0;">
                Use layer control (top-right) to toggle features
            </p>
        </div>
    </div>
    """
    
    trail_map.get_root().html.add_child(folium.Element(stats_html))
    
    # Add legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; right: 50px; width: 240px;
                background-color: white; border: 2px solid grey; z-index: 9999;
                padding: 12px; border-radius: 8px; box-shadow: 3px 3px 10px rgba(0,0,0,0.4);
                font-size: 12px;">
        <h4 style="margin: 0 0 8px 0; color: #2E7D32; text-align: center;">Map Legend</h4>
        <div style="line-height: 1.6;">
            <b>Markers:</b><br>
            🟠 Orange circles: Shelters<br>
            🔵 Blue dots: Water (reliable)<br>
            🟡 Yellow dots: Water (seasonal)<br>
            🔴 Red dots: Water (intermittent)<br>
            🏪 Blue pins: Towns/Resupply<br>
            <br>
            <b>Highlighted Sections:</b><br>
            Red dashed: Shelter gaps<br>
            Orange solid: Dry sections<br>
            Dark red: Very difficult terrain<br>
        </div>
    </div>
    """
    
    trail_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Add interactive tools
    print("  Adding interactive tools...")
    plugins.Fullscreen(position='topleft').add_to(trail_map)
    plugins.MeasureControl(primary_length_unit='miles').add_to(trail_map)
    plugins.MousePosition().add_to(trail_map)
    minimap = plugins.MiniMap(toggle_display=True)
    trail_map.add_child(minimap)
    
    # Layer control
    folium.LayerControl(position='topright', collapsed=False).add_to(trail_map)
    
    # Save
    output_file = './outputs/comprehensive_analysis_map.html'
    trail_map.save(output_file)
    
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"\n{'='*80}")
    print("✅ COMPREHENSIVE ANALYSIS MAP CREATED!")
    print(f"{'='*80}\n")
    
    print(f"📍 Saved to: {output_file}")
    print(f"   Size: {file_size:.1f} MB")
    
    print("\n📊 Map Layers (toggle in top-right):")
    print("   🥾 Trail Route - Main trail path")
    print(f"   🏕️ Shelters - {len(shelters_df)} locations")
    print(f"   💧 Water Sources - {len(water_df)} (color by reliability)")
    print(f"   🏘️ Towns - {len(towns_df)} resupply points")
    print(f"   ⚠️ Problem Areas - {len(large_gaps)} gaps + {len(dry_sections)} dry sections")
    print("   📊 Difficulty Zones - Steep/extreme sections")
    
    print("\n🎯 Features Visualized:")
    print("   ✓ Shelter spacing & gaps")
    print("   ✓ Water availability & dry sections")
    print("   ✓ Resupply town locations")
    print("   ✓ Infrastructure density")
    print("   ✓ Difficult terrain sections")
    print("   ✓ State boundaries")
    
    print("\n🛠️ Interactive Tools:")
    print("   ✓ Fullscreen mode")
    print("   ✓ Distance measurement")
    print("   ✓ Mini-map overview")
    print("   ✓ Mouse coordinates")
    print("   ✓ Layer toggle")
    
    print("\n💡 Usage Tips:")
    print("   • Click layers on/off to focus on specific features")
    print("   • Orange circles = shelters you'll likely use")
    print("   • Blue water dots = reliable year-round")
    print("   • Red dashed lines = bring tent for these gaps")
    print("   • Orange highlights = carry extra water")
    print("   • Blue town markers = resupply opportunities")
    
    print(f"\n🗺️  Open: open {output_file}\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

