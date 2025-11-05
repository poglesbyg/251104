#!/usr/bin/env python3
"""
Process real AT data from ArcGIS into analysis-ready format.
Handles the multi-segment geometry properly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json

def process_real_at_data(sample_rate=10):
    """
    Process real AT data into analysis-ready format.
    
    Args:
        sample_rate: Sample every Nth point to reduce dataset size
    """
    print("\n" + "="*80)
    print("PROCESSING REAL APPALACHIAN TRAIL DATA")
    print("="*80 + "\n")
    
    # Load raw GeoJSON
    raw_file = './data/arcgis_cache/at_trail_raw.json'
    
    if not os.path.exists(raw_file):
        print(f"❌ Raw data not found: {raw_file}")
        print("\nRun first: uv run python fetch_real_at_data.py")
        return None
    
    print(f"Loading raw GeoJSON: {raw_file}")
    with open(raw_file, 'r') as f:
        data = json.load(f)
    
    features = data.get('features', [])
    print(f"✓ Loaded {len(features)} trail segments\n")
    
    # Extract all coordinates from all features
    print("Extracting coordinates from LineStrings...")
    all_coords = []
    
    for idx, feature in enumerate(features):
        geom = feature.get('geometry', {})
        attrs = feature.get('attributes', {})
        
        if geom.get('type') == 'LineString' and 'coordinates' in geom:
            coords = geom['coordinates']
            for lon, lat in coords:
                all_coords.append({
                    'longitude': lon,
                    'latitude': lat,
                    'feature_id': idx,
                    'feature_name': attrs.get('Name', 'AT'),
                    'status': attrs.get('Status', 'Official')
                })
    
    print(f"✓ Extracted {len(all_coords):,} coordinate points\n")
    
    # Sample to reduce size
    if sample_rate > 1:
        print(f"Sampling every {sample_rate}th point for manageability...")
        all_coords = all_coords[::sample_rate]
        print(f"✓ Sampled to {len(all_coords):,} points\n")
    
    # Sort by latitude (south to north - approximate trail order)
    print("Sorting coordinates (south to north)...")
    all_coords = sorted(all_coords, key=lambda x: x['latitude'])
    
    # Calculate cumulative distance
    print("Calculating accurate distances...")
    cumulative_distance = 0
    prev_coord = None
    
    processed_points = []
    
    for i, coord in enumerate(all_coords):
        lat, lon = coord['latitude'], coord['longitude']
        
        # Calculate distance from previous point
        if prev_coord:
            dist_km = geodesic(
                (prev_coord['latitude'], prev_coord['longitude']),
                (lat, lon)
            ).kilometers
            cumulative_distance += dist_km * 0.621371  # km to miles
        
        # Add state assignment
        state = assign_state(lat, lon)
        
        processed_points.append({
            'point_id': i,
            'latitude': lat,
            'longitude': lon,
            'distance_miles': cumulative_distance,
            'state': state,
            'feature_name': coord['feature_name'],
            'status': coord['status']
        })
        
        prev_coord = coord
        
        if (i + 1) % 10000 == 0:
            print(f"  Processed {i + 1:,}/{len(all_coords):,} points...")
    
    df = pd.DataFrame(processed_points)
    
    print(f"\n✓ Processed {len(df):,} points")
    print(f"  Total distance: {df['distance_miles'].max():.1f} miles")
    print(f"  States: {df['state'].nunique()}")
    
    # Save processed data
    output_file = './data/arcgis_cache/at_real_processed.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    
    return df

def assign_state(lat, lon):
    """Assign state based on lat/lon (approximate but better than lat-only)."""
    
    # More accurate state assignments based on lat/lon ranges
    if 34.6 <= lat < 35.0:
        return 'Georgia'
    elif 35.0 <= lat < 35.8:
        if lon > -83.5:
            return 'North Carolina'
        else:
            return 'Tennessee'
    elif 35.8 <= lat < 36.6:
        if lon > -82.5:
            return 'North Carolina'
        else:
            return 'Tennessee'
    elif 36.6 <= lat < 39.5:
        return 'Virginia'
    elif 39.5 <= lat < 39.75:
        if lon > -78.3:
            return 'Maryland'
        else:
            return 'West Virginia'
    elif 39.75 <= lat < 42.0:
        return 'Pennsylvania'
    elif 42.0 <= lat < 41.4:
        return 'New Jersey'
    elif 41.35 <= lat < 41.6:
        return 'New York'
    elif 41.6 <= lat < 42.1:
        return 'Connecticut'
    elif 42.1 <= lat < 42.75:
        return 'Massachusetts'
    elif 42.75 <= lat < 43.4:
        return 'Vermont'
    elif 43.4 <= lat < 45.3:
        return 'New Hampshire'
    elif lat >= 45.3:
        return 'Maine'
    else:
        # Default fallback
        return 'Virginia'

def main():
    # Process the data
    df = process_real_at_data(sample_rate=10)
    
    if df is None:
        return
    
    print("\n" + "="*80)
    print("QUICK ANALYSIS OF REAL DATA")
    print("="*80 + "\n")
    
    print(f"📊 Overview:")
    print(f"  Total points: {len(df):,}")
    print(f"  Total distance: {df['distance_miles'].max():.1f} miles")
    print(f"  Lat range: {df['latitude'].min():.4f}° to {df['latitude'].max():.4f}°")
    print(f"  Lon range: {df['longitude'].min():.4f}° to {df['longitude'].max():.4f}°")
    
    print(f"\n📍 Miles by State:")
    state_miles = df.groupby('state').agg({
        'distance_miles': lambda x: x.max() - x.min()
    }).round(1)
    print(state_miles.sort_values('distance_miles', ascending=False))
    
    print("\n" + "="*80)
    print("✅ REAL DATA READY FOR ANALYSIS!")
    print("="*80)
    
    print("\nNext steps:")
    print("1. Use in your notebooks:")
    print("   df = pd.read_csv('./data/arcgis_cache/at_real_processed.csv')")
    print()
    print("2. Run full analysis:")
    print("   from src.analysis import TrailAnalyzer")
    print("   analyzer = TrailAnalyzer(df)")
    print()
    print("3. Note: Elevation data is not included yet")
    print("   Add with: fetch USGS elevation or use synthetic")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

