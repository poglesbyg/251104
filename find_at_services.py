#!/usr/bin/env python3
"""
Actively search for working Appalachian Trail ArcGIS service endpoints.
"""

import requests
import json
import time

def test_service_url(url, description="Service"):
    """Test if a service URL is accessible."""
    try:
        response = requests.get(f"{url}?f=json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                return True, data
            else:
                return False, data.get('error', {}).get('message', 'Unknown error')
        else:
            return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)

def search_for_at_services():
    """Search for Appalachian Trail services."""
    
    print("\n" + "="*80)
    print("SEARCHING FOR APPALACHIAN TRAIL ARCGIS SERVICES")
    print("="*80 + "\n")
    
    # Known organization IDs to try
    org_ids = [
        "fBc8EJBxQRMcHlei",  # Common in AT data
        "P20K5JdGTFZJBmJR",  # NPS
        "nzS0F0zdNLvs7nc8",  # USDA Forest Service
    ]
    
    # Common service name patterns
    service_patterns = [
        "AT_Centerline",
        "Appalachian_Trail",
        "AT_Trail",
        "Trail_Centerline",
        "AppalachianTrail_Centerline",
        "AT_NRCA_Trail",
        "APPA_Trail",
        "AT_Route",
        "Trail_Line",
    ]
    
    working_services = []
    
    for org_id in org_ids:
        print(f"\n🔍 Checking organization: {org_id}")
        
        # Try to list all services for this org
        base_url = f"https://services.arcgis.com/{org_id}/arcgis/rest/services"
        print(f"   Testing: {base_url}")
        
        success, result = test_service_url(base_url)
        if success:
            print(f"   ✓ Organization accessible!")
            
            # List available services
            services = result.get('services', [])
            folders = result.get('folders', [])
            
            if services:
                print(f"   Found {len(services)} services:")
                for service in services:
                    name = service.get('name', '')
                    stype = service.get('type', '')
                    print(f"      • {name} ({stype})")
                    
                    # Check if it's AT-related
                    if any(term in name.lower() for term in ['appalachian', 'trail', 'at_', 'appa']):
                        service_url = f"{base_url}/{name}/{stype}"
                        print(f"        🎯 AT-related! Testing: {service_url}")
                        
                        s_success, s_result = test_service_url(service_url)
                        if s_success:
                            print(f"        ✅ WORKING!")
                            working_services.append({
                                'url': service_url,
                                'name': name,
                                'type': stype,
                                'org': org_id
                            })
            
            if folders:
                print(f"   Found {len(folders)} folders: {folders}")
        else:
            print(f"   ✗ Not accessible: {result}")
        
        time.sleep(0.5)  # Be nice to the API
    
    # Try alternative service URLs
    print(f"\n\n🔍 Trying common AT service patterns...")
    
    for org_id in org_ids:
        for pattern in service_patterns:
            for service_type in ['FeatureServer', 'MapServer']:
                url = f"https://services.arcgis.com/{org_id}/arcgis/rest/services/{pattern}/{service_type}/0"
                
                success, result = test_service_url(url, f"{pattern}/{service_type}")
                if success:
                    print(f"\n✅ FOUND: {url}")
                    working_services.append({
                        'url': url,
                        'name': pattern,
                        'type': service_type,
                        'org': org_id
                    })
                
                time.sleep(0.3)
    
    # Print results
    print("\n" + "="*80)
    print("SEARCH RESULTS")
    print("="*80 + "\n")
    
    if working_services:
        print(f"✅ Found {len(working_services)} working service(s):\n")
        for i, service in enumerate(working_services, 1):
            print(f"{i}. {service['name']} ({service['type']})")
            print(f"   URL: {service['url']}")
            print(f"   Org: {service['org']}")
            print()
        
        print("\n📝 To use in your analysis:")
        print("\n1. Edit src/arcgis_integration.py")
        print("2. Update line ~24:")
        print(f"   ATC_SERVICE_URL = \"{working_services[0]['url'].rsplit('/', 2)[0]}\"")
        print("\n3. Re-run your notebook!")
        
    else:
        print("⚠ No working services found automatically.")
        print("\nManual steps:")
        print("1. Visit: https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset")
        print("2. Click on any dataset")
        print("3. Look for 'API' or 'View Full Details'")
        print("4. Copy the REST endpoint URL")
        print("5. Update src/arcgis_integration.py with that URL")
    
    print("\n" + "="*80)
    
    return working_services

if __name__ == '__main__':
    try:
        services = search_for_at_services()
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

