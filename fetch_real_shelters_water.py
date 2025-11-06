#!/usr/bin/env python3
"""
Fetch REAL shelter and water source data from ArcGIS.
"""

import requests
import json
import pandas as pd
import time

def search_for_at_features(base_org_url):
    """Search for AT shelter and water source services."""
    
    print(f"\n🔍 Searching for AT features in organization...")
    
    # Try to list all services
    try:
        response = requests.get(f"{base_org_url}?f=json", timeout=15)
        if response.status_code == 200:
            data = response.json()
            services = data.get('services', [])
            
            at_related = []
            for service in services:
                name = service.get('name', '').lower()
                if any(keyword in name for keyword in ['shelter', 'water', 'facility', 'amenity', 'campsite']):
                    at_related.append(service)
            
            if at_related:
                print(f"✓ Found {len(at_related)} potentially relevant services:")
                for svc in at_related:
                    print(f"  • {svc['name']} ({svc['type']})")
            
            return at_related
    except Exception as e:
        print(f"⚠ Error: {e}")
    
    return []

def try_common_endpoints(base_org_url):
    """Try common endpoint names for shelters and water."""
    
    print(f"\n🔍 Trying common endpoint patterns...")
    
    common_names = [
        ('AT_Shelters', 'Shelters'),
        ('Appalachian_Trail_Shelters', 'Shelters'),
        ('Shelters', 'Shelters'),
        ('Trail_Shelters', 'Shelters'),
        ('AT_Water_Sources', 'Water'),
        ('Water_Sources', 'Water'),
        ('Trail_Water', 'Water'),
        ('AT_Facilities', 'Facilities'),
        ('Trail_Amenities', 'Amenities'),
    ]
    
    found_services = []
    
    for service_name, feature_type in common_names:
        for svc_type in ['FeatureServer', 'MapServer']:
            url = f"{base_org_url}/{service_name}/{svc_type}/0/query"
            
            try:
                params = {
                    'where': '1=1',
                    'returnCountOnly': 'true',
                    'f': 'json'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'count' in data and data['count'] > 0:
                        print(f"  ✅ FOUND: {service_name}/{svc_type} ({data['count']} features)")
                        found_services.append({
                            'name': service_name,
                            'type': svc_type,
                            'feature_type': feature_type,
                            'count': data['count'],
                            'url': f"{base_org_url}/{service_name}/{svc_type}"
                        })
                
            except:
                pass
            
            time.sleep(0.2)
    
    return found_services

def main():
    print("\n" + "="*80)
    print("SEARCHING FOR REAL AT SHELTER & WATER DATA")
    print("="*80)
    
    # Known working organization
    base_org_url = "https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services"
    
    print(f"\nBase URL: {base_org_url}")
    
    # Search methods
    services = search_for_at_features(base_org_url)
    common = try_common_endpoints(base_org_url)
    
    print("\n" + "="*80)
    print("SEARCH RESULTS")
    print("="*80 + "\n")
    
    if common:
        print(f"✅ Found {len(common)} working endpoints:\n")
        for svc in common:
            print(f"  {svc['feature_type']}: {svc['name']}")
            print(f"    Count: {svc['count']}")
            print(f"    URL: {svc['url']}")
            print()
    else:
        print("⚠️  No shelter/water services found automatically")
        print("\n📝 Manual Options:")
        print("\n1. Search ArcGIS Hub for shelter/water datasets:")
        print("   https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset")
        print("   Look for: 'shelter', 'water', 'facility', 'campsite'")
        print("\n2. Check if there are separate apps/services for these features")
        print("\n3. The trail centerline might be the only available data")
        print("   In that case, simulated data is the best option for analysis")
        
        print("\n💡 Current Status:")
        print("   ✓ Trail path: REAL (3,021 segments from ArcGIS)")
        print("   ⚠ Shelters: Simulated (realistic spacing)")
        print("   ⚠ Water: Simulated (realistic distribution)")
        print("   ⚠ Towns: Simulated (typical access points)")
        
        print("\n   Simulated data uses:")
        print("   • Realistic spacing patterns")
        print("   • Typical infrastructure density")
        print("   • Placed on REAL trail coordinates")
        print("   • Good for planning estimates")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

