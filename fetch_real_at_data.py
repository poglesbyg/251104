#!/usr/bin/env python3
"""
Fetch REAL Appalachian Trail data from ArcGIS.
Uses the discovered working service.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from arcgis_integration import ArcGISDataFetcher
import pandas as pd
import json

def main():
    print("\n" + "="*80)
    print("FETCHING REAL APPALACHIAN TRAIL DATA FROM ARCGIS")
    print("="*80 + "\n")
    
    print("Service: Appalachian National Scenic Trail")
    print("URL: https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services/Appalachian_National_Scenic_Trail/FeatureServer")
    print()
    
    # Initialize fetcher
    fetcher = ArcGISDataFetcher()
    
    # Fetch trail data
    print("Fetching trail centerline data...\n")
    trail_data = fetcher.fetch_trail_centerline()
    
    if trail_data and 'features' in trail_data:
        features = trail_data['features']
        print(f"✅ SUCCESS! Fetched {len(features)} trail features\n")
        
        # Analyze what we got
        print("="*80)
        print("DATA PREVIEW")
        print("="*80 + "\n")
        
        if len(features) > 0:
            # Show first feature
            first_feature = features[0]
            attrs = first_feature.get('attributes', {})
            geom = first_feature.get('geometry', {})
            
            print("Sample Feature Attributes:")
            for key, value in attrs.items():
                print(f"  {key}: {value}")
            
            print(f"\nGeometry Type: {geom.get('type', 'N/A')}")
            
            if 'paths' in geom:
                print(f"Paths: {len(geom['paths'])}")
                if len(geom['paths']) > 0:
                    print(f"Points in first path: {len(geom['paths'][0])}")
            
            # Save raw data
            cache_file = os.path.join(fetcher.cache_dir, 'at_trail_raw.json')
            with open(cache_file, 'w') as f:
                json.dump(trail_data, f, indent=2)
            print(f"\n💾 Raw data saved to: {cache_file}")
            
            # Try to convert to usable format
            print("\n" + "="*80)
            print("CONVERTING TO DATAFRAME")
            print("="*80 + "\n")
            
            import numpy as np
            from geopy.distance import geodesic
            
            trail_points = []
            cumulative_distance = 0
            prev_point = None
            
            for idx, feature in enumerate(features):
                geom = feature.get('geometry', {})
                attrs = feature.get('attributes', {})
                
                # GeoJSON format: coordinates are [lon, lat] pairs
                if geom.get('type') == 'LineString' and 'coordinates' in geom:
                    coords = geom['coordinates']
                    
                    for point in coords:
                        lon, lat = point[0], point[1]
                        
                        # Calculate distance from previous point
                        if prev_point is not None:
                            dist_km = geodesic(
                                (prev_point[1], prev_point[0]),  # (lat, lon)
                                (lat, lon)
                            ).kilometers
                            cumulative_distance += dist_km * 0.621371  # km to miles
                        
                        trail_points.append({
                            'longitude': lon,
                            'latitude': lat,
                            'distance_miles': cumulative_distance,
                            'feature_name': attrs.get('Name', 'Unknown'),
                            'status': attrs.get('Status', 'Unknown'),
                            'feature_id': idx
                        })
                        
                        prev_point = (lon, lat)
                
                if (idx + 1) % 500 == 0:
                    print(f"  Processed {idx + 1}/{len(features)} features...")
            
            if len(trail_points) == 0:
                print("⚠️ No coordinates extracted. Geometry format may be different.")
                print("First feature geometry structure:")
                print(json.dumps(features[0].get('geometry', {}), indent=2)[:500])
            else:
                trail_df = pd.DataFrame(trail_points)
                
                print(f"✅ Converted to DataFrame: {len(trail_df)} points")
                print(f"   Latitude range: {trail_df['latitude'].min():.4f} to {trail_df['latitude'].max():.4f}")
                print(f"   Longitude range: {trail_df['longitude'].min():.4f} to {trail_df['longitude'].max():.4f}")
            
            # Save DataFrame
            csv_file = os.path.join(fetcher.cache_dir, 'at_trail_real.csv')
            trail_df.to_csv(csv_file, index=False)
            print(f"\n💾 DataFrame saved to: {csv_file}")
            
            print("\n" + "="*80)
            print("✅ REAL AT DATA READY TO USE!")
            print("="*80)
            
            print("\nNext steps:")
            print("1. The data is now cached locally")
            print("2. Re-run your notebook - it will use this real data!")
            print("3. Or load directly:")
            print(f"   df = pd.read_csv('{csv_file}')")
            
    else:
        print("❌ Failed to fetch data")
        print("\nCheck your internet connection and try again")
    
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

