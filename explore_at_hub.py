#!/usr/bin/env python3
"""
Explore the official AT Natural Resource Condition Assessment Hub.
URL: https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com
"""

import sys
import os
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def explore_hub_services():
    """Explore available services on the AT NRCA Hub."""
    
    print("\n" + "="*80)
    print("  APPALACHIAN TRAIL NATURAL RESOURCE CONDITION ASSESSMENT")
    print("  Official ArcGIS Hub Exploration")
    print("="*80 + "\n")
    
    hub_url = "https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com"
    
    print(f"🗺️  Hub URL: {hub_url}")
    print()
    
    # Common REST API endpoints to try
    base_services = [
        "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services",
        "https://services.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services",
    ]
    
    print("🔍 Searching for AT services...\n")
    
    for base_url in base_services:
        print(f"Checking: {base_url}")
        try:
            response = requests.get(f"{base_url}?f=json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                services = data.get('services', [])
                folders = data.get('folders', [])
                
                print(f"  ✓ Found {len(services)} services")
                print(f"  ✓ Found {len(folders)} folders")
                
                # List AT-related services
                at_services = [s for s in services if 'appalachian' in s.get('name', '').lower() 
                              or 'trail' in s.get('name', '').lower()
                              or 'at_' in s.get('name', '').lower()]
                
                if at_services:
                    print(f"\n  📍 AT-related services:")
                    for service in at_services:
                        print(f"    • {service['name']} ({service['type']})")
                
                # List folders that might contain AT data
                at_folders = [f for f in folders if 'appalachian' in f.lower() 
                             or 'trail' in f.lower() or 'at' in f.lower()]
                
                if at_folders:
                    print(f"\n  📁 AT-related folders:")
                    for folder in at_folders:
                        print(f"    • {folder}")
                
                print()
                
        except Exception as e:
            print(f"  ⚠ Error: {e}")
        
        print()
    
    # Try to find specific AT centerline service
    print("\n" + "="*80)
    print("  COMMON AT SERVICE ENDPOINTS TO TRY")
    print("="*80 + "\n")
    
    potential_endpoints = [
        "AT_Centerline/FeatureServer/0",
        "Appalachian_Trail_Centerline/FeatureServer/0",
        "AT_Trail/FeatureServer/0",
        "Trail_Centerline/FeatureServer/0",
        "AT_NRCA_Trail/FeatureServer/0",
        "AppalachianTrail/FeatureServer/0",
    ]
    
    print("Testing potential endpoints:")
    for endpoint in potential_endpoints:
        test_url = f"https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/{endpoint}/query"
        print(f"\n  Testing: {endpoint}")
        
        try:
            params = {
                'where': '1=1',
                'returnCountOnly': 'true',
                'f': 'json'
            }
            response = requests.get(test_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'count' in data:
                    print(f"    ✓ FOUND! Count: {data['count']} features")
                    print(f"    URL: {test_url}")
                elif 'error' in data:
                    error_msg = data['error'].get('message', 'Unknown error')
                    print(f"    ✗ Error: {error_msg}")
            else:
                print(f"    ✗ Status: {response.status_code}")
                
        except Exception as e:
            print(f"    ✗ {str(e)[:60]}")
    
    # Provide manual exploration instructions
    print("\n" + "="*80)
    print("  MANUAL EXPLORATION")
    print("="*80 + "\n")
    
    print("To find available datasets:")
    print()
    print("1. Visit the hub in browser:")
    print(f"   {hub_url}")
    print()
    print("2. Look for 'Data' or 'Datasets' section")
    print()
    print("3. Click on any dataset to see its details")
    print()
    print("4. Look for 'View API' or 'REST Endpoint' link")
    print()
    print("5. Copy the service URL and update src/arcgis_integration.py")
    print()
    print("📚 Common data types on NPS/ATC hubs:")
    print("   • Trail centerline (line geometry)")
    print("   • Shelters (point features)")
    print("   • Water sources (point features)")
    print("   • Trail segments with conditions")
    print("   • Viewsheds and protected areas")
    print()
    
    print("="*80)
    print("  NEXT STEPS")
    print("="*80 + "\n")
    
    print("If you found a working endpoint:")
    print()
    print("1. Update src/arcgis_integration.py:")
    print("   ATC_SERVICE_URL = 'YOUR_WORKING_URL'")
    print()
    print("2. Test fetching data:")
    print("   from src.arcgis_integration import ArcGISDataFetcher")
    print("   fetcher = ArcGISDataFetcher()")
    print("   data = fetcher.fetch_trail_centerline()")
    print()
    print("3. Use with analysis:")
    print("   from src.analysis import TrailAnalyzer")
    print("   analyzer = TrailAnalyzer(data)")
    print()


if __name__ == '__main__':
    try:
        explore_hub_services()
    except KeyboardInterrupt:
        print("\n\nExploration cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

