#!/usr/bin/env python3
"""
Extract service URLs from ArcGIS Web AppBuilder apps.
"""

import requests
import json
import re
from urllib.parse import urlparse, parse_qs

def extract_from_webapp(app_url):
    """
    Extract service URLs from ArcGIS Web AppBuilder app.
    
    Args:
        app_url: URL of the web app viewer
    """
    print("\n" + "="*80)
    print("EXTRACTING SERVICE URLS FROM ARCGIS WEB APP")
    print("="*80 + "\n")
    
    print(f"App URL: {app_url}\n")
    
    # Parse the URL to get the app ID
    parsed = urlparse(app_url)
    params = parse_qs(parsed.query)
    app_id = params.get('id', [None])[0]
    
    if not app_id:
        print("❌ Could not extract app ID from URL")
        return []
    
    print(f"App ID: {app_id}\n")
    
    # Web AppBuilder apps have a config endpoint
    config_urls = [
        f"https://www.arcgis.com/sharing/rest/content/items/{app_id}/data?f=json",
        f"https://www.arcgis.com/sharing/rest/content/items/{app_id}?f=json",
    ]
    
    service_urls = []
    
    for config_url in config_urls:
        print(f"🔍 Trying config endpoint: {config_url}\n")
        
        try:
            response = requests.get(config_url, timeout=15)
            
            if response.status_code == 200:
                try:
                    config = response.json()
                    print(f"✓ Retrieved app configuration")
                    
                    # Extract service URLs from the config
                    service_urls = extract_service_urls_from_config(config)
                    
                    if service_urls:
                        print(f"\n✅ Found {len(service_urls)} service URL(s)!\n")
                        return service_urls
                    
                except json.JSONDecodeError:
                    # Might be HTML or other format
                    text = response.text
                    # Try to find service URLs in the text
                    urls = re.findall(r'https://services\d*\.arcgis\.com/[^"\']+/FeatureServer', text)
                    if urls:
                        print(f"✓ Found URLs in response")
                        return list(set(urls))
                    
        except Exception as e:
            print(f"⚠ Error: {e}\n")
    
    return service_urls

def extract_service_urls_from_config(config, urls=None):
    """Recursively extract service URLs from config JSON."""
    if urls is None:
        urls = []
    
    if isinstance(config, dict):
        # Check for 'url' key
        if 'url' in config:
            url = config['url']
            if 'arcgis.com' in url and ('FeatureServer' in url or 'MapServer' in url):
                # Clean the URL - remove layer numbers and query params
                base_url = url.split('/query')[0].split('?')[0]
                if base_url not in urls:
                    urls.append(base_url)
                    
                    # Extract service name
                    service_name = 'Unknown'
                    if 'rest/services/' in base_url:
                        parts = base_url.split('rest/services/')[-1].split('/')
                        if len(parts) > 0:
                            service_name = parts[0]
                    
                    print(f"  📍 Found: {service_name}")
                    print(f"     {base_url}")
        
        # Check for common config keys
        for key in ['map', 'operationalLayers', 'layers', 'tables', 'itemData', 'webmap']:
            if key in config:
                extract_service_urls_from_config(config[key], urls)
    
    elif isinstance(config, list):
        for item in config:
            extract_service_urls_from_config(item, urls)
    
    return urls

def main():
    """Main function."""
    
    # Default: the app you found
    default_app = "https://www.arcgis.com/apps/webappviewer/index.html?id=6298c848ba2a490588b7f6d25453e4e0"
    
    import sys
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
    else:
        app_url = default_app
        print(f"Using default app URL (you can pass a different one as argument)")
    
    service_urls = extract_from_webapp(app_url)
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")
    
    if service_urls:
        print(f"✅ Found {len(service_urls)} service URL(s):\n")
        
        for i, url in enumerate(service_urls, 1):
            print(f"{i}. {url}")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80 + "\n")
        
        print("1. Test the URL(s):")
        print(f"   uv run python test_service_url.py \"{service_urls[0]}\"")
        
        print("\n2. If working, update src/arcgis_integration.py:")
        # Remove layer number if present
        base_url = service_urls[0]
        if base_url.endswith('/0') or base_url.endswith('/1'):
            base_url = base_url.rsplit('/', 1)[0]
        
        print(f"   ATC_SERVICE_URL = \"{base_url}\"")
        
        print("\n3. Re-run your notebook - it will use real data!")
        
    else:
        print("⚠ Could not automatically extract service URLs")
        print("\n📝 Manual method:")
        print("1. Open the app in your browser")
        print("2. Press F12 → Network tab")
        print("3. Reload the page")
        print("4. Filter for 'FeatureServer' or 'query'")
        print("5. Copy any service URL you see")
        print("6. Test it with: uv run python test_service_url.py YOUR_URL")
    
    print("\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

