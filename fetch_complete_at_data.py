#!/usr/bin/env python3
"""
Fetch ALL Appalachian Trail features using pagination.
Gets all 3,021+ segments instead of just 2,000.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json
import time

def fetch_all_trail_features():
    """Fetch all AT trail features with pagination."""
    
    print("\n" + "="*80)
    print("FETCHING COMPLETE APPALACHIAN TRAIL DATA (ALL SEGMENTS)")
    print("="*80 + "\n")
    
    service_url = "https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services/Appalachian_National_Scenic_Trail/FeatureServer/0/query"
    
    all_features = []
    offset = 0
    batch_size = 2000
    
    print("Fetching trail segments with pagination...\n")
    
    while True:
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'geojson',
            'returnGeometry': 'true',
            'resultOffset': offset,
            'resultRecordCount': batch_size
        }
        
        print(f"  Fetching offset {offset}...")
        
        try:
            response = requests.get(service_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                if len(features) == 0:
                    print(f"  ✓ No more features (completed)")
                    break
                
                all_features.extend(features)
                print(f"    Got {len(features)} features (total: {len(all_features)})")
                
                # If we got fewer than batch_size, we're done
                if len(features) < batch_size:
                    print(f"  ✓ Reached end of data")
                    break
                
                offset += batch_size
                time.sleep(0.5)  # Be nice to the API
                
            else:
                print(f"  ✗ HTTP {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            break
    
    print(f"\n✅ Total features fetched: {len(all_features)}")
    
    # Save complete data
    cache_dir = './data/arcgis_cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    complete_file = os.path.join(cache_dir, 'at_trail_complete.json')
    
    geojson = {
        'type': 'FeatureCollection',
        'features': all_features
    }
    
    with open(complete_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    file_size = os.path.getsize(complete_file) / (1024 * 1024)
    print(f"\n💾 Saved complete dataset: {complete_file}")
    print(f"   File size: {file_size:.1f} MB")
    print(f"   Features: {len(all_features)}")
    
    # Count total points
    total_points = 0
    for feature in all_features:
        geom = feature.get('geometry', {})
        if geom.get('type') == 'LineString':
            coords = geom.get('coordinates', [])
            total_points += len(coords)
    
    print(f"   Total GPS points: {total_points:,}")
    
    print("\n" + "="*80)
    print("✅ COMPLETE TRAIL DATA READY!")
    print("="*80)
    
    print("\nNext step:")
    print("  Run: uv run python create_real_trail_map.py")
    print("  (It will now use the complete dataset)")
    print()
    
    return all_features

if __name__ == '__main__':
    try:
        fetch_all_trail_features()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

