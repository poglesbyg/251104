#!/usr/bin/env python3
"""
Quick test script for ArcGIS service URLs.
Use this to verify a service URL works before updating the integration.
"""

import sys
import requests
import json

def test_service(url):
    """Test if a service URL is valid and accessible."""
    print(f"\n🔍 Testing: {url}\n")
    
    # Test 1: Service root
    print("Test 1: Service root...")
    try:
        response = requests.get(f"{url}?f=json", timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                print(f"  ❌ Error: {data['error'].get('message', 'Unknown')}")
                return False
            
            print(f"  ✅ Service accessible!")
            
            # Show service info
            if 'layers' in data:
                print(f"  Layers: {len(data['layers'])}")
                for layer in data['layers'][:5]:  # Show first 5
                    print(f"    - {layer.get('id')}: {layer.get('name')}")
            
            if 'tables' in data:
                print(f"  Tables: {len(data['tables'])}")
            
        else:
            print(f"  ❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test 2: Query layer 0
    print("\nTest 2: Query layer 0...")
    try:
        query_url = f"{url}/0/query"
        params = {
            'where': '1=1',
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        response = requests.get(query_url, params=params, timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'count' in data:
                print(f"  ✅ Found {data['count']} features")
                
                # Try to get one feature as example
                params2 = {
                    'where': '1=1',
                    'outFields': '*',
                    'resultRecordCount': 1,
                    'f': 'json'
                }
                response2 = requests.get(query_url, params=params2, timeout=10)
                if response2.status_code == 200:
                    data2 = response2.json()
                    if 'features' in data2 and len(data2['features']) > 0:
                        feature = data2['features'][0]
                        print(f"\n  Sample feature attributes:")
                        for key, value in list(feature.get('attributes', {}).items())[:5]:
                            print(f"    {key}: {value}")
                
                return True
            elif 'error' in data:
                print(f"  ❌ Error: {data['error'].get('message', 'Unknown')}")
        else:
            print(f"  ❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return False

if __name__ == '__main__':
    print("="*80)
    print("ARCGIS SERVICE URL TESTER")
    print("="*80)
    
    if len(sys.argv) > 1:
        # URL provided as argument
        url = sys.argv[1]
    else:
        # Prompt for URL
        print("\nEnter the service URL to test:")
        print("(e.g., https://services.arcgis.com/[ORG]/arcgis/rest/services/[NAME]/FeatureServer)")
        print()
        url = input("URL: ").strip()
    
    if not url:
        print("\n❌ No URL provided")
        sys.exit(1)
    
    # Clean up URL
    url = url.rstrip('/')
    if url.endswith('/0') or url.endswith('/1') or url.endswith('/2'):
        url = url.rsplit('/', 1)[0]
        print(f"\nℹ️  Removed layer number from URL: {url}")
    
    success = test_service(url)
    
    print("\n" + "="*80)
    if success:
        print("✅ SERVICE IS WORKING!")
        print("\nTo use in your analysis:")
        print("1. Edit src/arcgis_integration.py")
        print("2. Update ATC_SERVICE_URL or add new constant:")
        print(f"   SERVICE_URL = \"{url}\"")
        print("3. Re-run your notebook")
    else:
        print("❌ SERVICE TEST FAILED")
        print("\nTroubleshooting:")
        print("- Verify the URL is correct")
        print("- Check if the service is public (may need authentication)")
        print("- Try opening the URL in a browser with ?f=json at the end")
        print("- Look for the service in ArcGIS Hub datasets page")
    print("="*80 + "\n")

