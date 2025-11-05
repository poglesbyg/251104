#!/usr/bin/env python3
"""
Analyze the REAL Appalachian Trail data fetched from ArcGIS!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from analysis import TrailAnalyzer
from fkt_analysis import FKTAnalyzer
from daylight_analysis import DaylightAnalyzer
from visualization import TrailVisualizer

def main():
    print("\n" + "="*80)
    print("ANALYZING REAL APPALACHIAN TRAIL DATA FROM ARCGIS")
    print("="*80 + "\n")
    
    # Load the real data
    real_data_path = './data/arcgis_cache/at_trail_real.csv'
    
    if not os.path.exists(real_data_path):
        print(f"❌ Real data not found at {real_data_path}")
        print("\nRun first: uv run python fetch_real_at_data.py")
        return
    
    print(f"Loading real AT data from: {real_data_path}")
    df = pd.read_csv(real_data_path)
    
    print(f"✓ Loaded {len(df):,} GPS points")
    print(f"  Distance: {df['distance_miles'].max():.1f} miles")
    print(f"  Latitude: {df['latitude'].min():.4f}° to {df['latitude'].max():.4f}°")
    print(f"  Longitude: {df['longitude'].min():.4f}° to {df['longitude'].max():.4f}°")
    
    # Note: We need to add state and elevation data
    print("\n📍 Adding state boundaries...")
    df = add_states_to_dataframe(df)
    
    print("\n⛰️  Note: Real elevation data requires USGS queries")
    print("  Using approximate elevations for now...")
    print("  (Run with elevation fetch for complete accuracy)")
    
    # Add placeholder elevations (you could fetch real ones from USGS)
    df['elevation_ft'] = 2000  # Placeholder
    
    # Create analyzer
    print("\n" + "="*80)
    print("RUNNING ANALYSIS ON REAL DATA")
    print("="*80 + "\n")
    
    analyzer = TrailAnalyzer(df)
    summary = analyzer.get_summary_statistics()
    
    print(f"📏 REAL TRAIL STATISTICS:")
    print(f"  Total Distance: {summary['total_distance_miles']:.1f} miles")
    print(f"  Number of States: {summary['num_states']}")
    print(f"  Data Points: {len(df):,}")
    print(f"  Average Point Spacing: {summary['total_distance_miles'] / len(df):.4f} miles")
    
    # FKT Analysis with real data
    print("\n🏆 FKT ANALYSIS WITH REAL TRAIL DATA:")
    fkt = FKTAnalyzer(df, analyzer)
    fkt_metrics = fkt.get_fkt_metrics()
    
    print(f"  Real distance: {summary['total_distance_miles']:.1f} miles")
    print(f"  FKT pace needed: {fkt_metrics['pace_metrics']['miles_per_day']:.1f} miles/day")
    print(f"  Moving speed: {fkt_metrics['pace_metrics']['avg_mph_moving']:.2f} mph")
    
    # State analysis
    print("\n📍 STATE-BY-STATE (Real Coordinates):")
    state_stats = analyzer.analyze_by_state()
    print(state_stats[['State', 'Miles']].to_string(index=False))
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE WITH REAL ARCGIS DATA!")
    print("="*80)
    
    print("\n💡 To get real elevations too:")
    print("  1. The script can query USGS for each coordinate")
    print("  2. This takes time (413k points!) but gives perfect accuracy")
    print("  3. Or sample every 10th point for speed")
    
    print("\n🎨 To visualize:")
    print("  viz = TrailVisualizer(df, './outputs')")
    print("  viz.plot_elevation_profile()")
    print("  viz.create_interactive_map()")
    
    print()

def add_states_to_dataframe(df):
    """Add state names based on latitude (approximate)."""
    # Approximate state boundaries by latitude
    state_boundaries = [
        (34.626, 34.99, 'Georgia'),
        (34.99, 36.58, 'North Carolina'),
        (35.0, 36.62, 'Tennessee'),
        (36.62, 39.47, 'Virginia'),
        (39.32, 39.72, 'West Virginia'),
        (39.47, 39.72, 'Maryland'),
        (39.72, 42.0, 'Pennsylvania'),
        (41.0, 41.35, 'New Jersey'),
        (41.2, 41.5, 'New York'),
        (41.5, 42.05, 'Connecticut'),
        (42.05, 42.73, 'Massachusetts'),
        (42.73, 43.0, 'Vermont'),
        (43.0, 45.3, 'New Hampshire'),
        (45.3, 45.95, 'Maine')
    ]
    
    def get_state(lat):
        for min_lat, max_lat, state in state_boundaries:
            if min_lat <= lat <= max_lat:
                return state
        # Default based on general location
        if lat < 36:
            return 'Georgia'
        elif lat > 45:
            return 'Maine'
        else:
            return 'Virginia'  # Most of the trail
    
    df['state'] = df['latitude'].apply(get_state)
    return df

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

