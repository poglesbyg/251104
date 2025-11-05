#!/usr/bin/env python3
"""
Example script demonstrating ArcGIS integration with AT analysis.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from arcgis_integration import ArcGISDataFetcher, create_arcgis_integration_guide


def main():
    """Demonstrate ArcGIS integration capabilities."""
    
    print("\n" + "="*80)
    print("  APPALACHIAN TRAIL ANALYSIS - ARCGIS INTEGRATION DEMO")
    print("="*80 + "\n")
    
    # Show integration guide
    create_arcgis_integration_guide()
    
    # Initialize fetcher
    print("\n" + "="*80)
    print("  STEP 1: INITIALIZE ARCGIS DATA FETCHER")
    print("="*80 + "\n")
    
    fetcher = ArcGISDataFetcher()
    print("✓ ArcGIS fetcher initialized")
    print(f"✓ Cache directory: {fetcher.cache_dir}")
    
    # Show available resources
    print("\n" + "="*80)
    print("  STEP 2: AVAILABLE DATA SOURCES")
    print("="*80 + "\n")
    
    resources = fetcher.get_arcgis_resources()
    
    print("📍 Official Sources:")
    for source, info in resources['official_sources'].items():
        if isinstance(info, dict):
            print(f"  • {source}: {info.get('description', 'N/A')}")
            if 'url' in info or 'ATC_Hub' in info:
                url = info.get('url') or info.get('ATC_Hub', '')
                if url:
                    print(f"    URL: {url}")
        else:
            print(f"  • {source}: {info}")
    
    print("\n🗺️  Available Data Types:")
    for i, data_type in enumerate(resources['data_types'], 1):
        print(f"  {i:2d}. {data_type}")
    
    # Example: Try fetching trail centerline
    print("\n" + "="*80)
    print("  STEP 3: FETCHING SAMPLE DATA")
    print("="*80 + "\n")
    
    print("Attempting to fetch AT centerline...")
    print("(Note: This may require internet connection and valid endpoints)")
    
    trail_data = fetcher.fetch_trail_centerline()
    
    if trail_data:
        print("✓ Successfully fetched trail data!")
        print(f"  Features: {len(trail_data.get('features', []))}")
    else:
        print("⚠ Could not fetch trail data - endpoint may need updating")
        print("  This is normal for demo purposes")
    
    # Example elevation query
    print("\n" + "="*80)
    print("  STEP 4: USGS ELEVATION API EXAMPLE")
    print("="*80 + "\n")
    
    print("Testing USGS elevation API with sample coordinates...")
    
    # Springer Mountain, GA (AT southern terminus)
    sample_coords = [(-84.1938, 34.6268)]
    
    print(f"  Querying: Springer Mountain, GA")
    print(f"  Coordinates: {sample_coords[0]}")
    
    try:
        import requests
        params = {
            'x': sample_coords[0][0],
            'y': sample_coords[0][1],
            'units': 'Feet',
            'output': 'json'
        }
        response = requests.get(fetcher.USGS_ELEVATION_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            elevation = data.get('USGS_Elevation_Point_Query_Service', {}).get('Elevation_Query', {}).get('Elevation')
            if elevation:
                print(f"  ✓ Elevation: {elevation} feet")
                print(f"  (Expected: ~3,782 feet)")
        else:
            print(f"  ⚠ API returned status {response.status_code}")
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    
    # Integration with existing analysis
    print("\n" + "="*80)
    print("  STEP 5: INTEGRATION WITH EXISTING ANALYSIS")
    print("="*80 + "\n")
    
    print("How to integrate ArcGIS data with existing analysis:")
    print()
    print("  1. Fetch real trail data:")
    print("     fetcher = ArcGISDataFetcher()")
    print("     trail_data = fetcher.create_enhanced_dataset()")
    print()
    print("  2. Use with Trail Analyzer:")
    print("     from src.analysis import TrailAnalyzer")
    print("     analyzer = TrailAnalyzer(trail_data)")
    print("     summary = analyzer.get_summary_statistics()")
    print()
    print("  3. Use with FKT Analysis:")
    print("     from src.fkt_analysis import FKTAnalyzer")
    print("     fkt = FKTAnalyzer(trail_data, analyzer)")
    print("     fkt.print_comprehensive_report()")
    print()
    print("  4. Use with Daylight Analysis:")
    print("     from src.daylight_analysis import DaylightAnalyzer")
    print("     daylight = DaylightAnalyzer(trail_data)")
    print("     comparison = daylight.compare_hiking_windows()")
    
    # Next steps
    print("\n" + "="*80)
    print("  NEXT STEPS")
    print("="*80 + "\n")
    
    print("🔧 To use real ArcGIS data:")
    print()
    print("  1. Optional: Install ArcGIS Python API")
    print("     uv add arcgis")
    print()
    print("  2. Visit ArcGIS Hub to find current endpoints:")
    print("     https://hub.arcgis.com")
    print("     Search for 'Appalachian Trail Conservancy'")
    print()
    print("  3. Update service URLs in src/arcgis_integration.py")
    print()
    print("  4. Run data fetch:")
    print("     from src.arcgis_integration import ArcGISDataFetcher")
    print("     fetcher = ArcGISDataFetcher()")
    print("     data = fetcher.create_enhanced_dataset()")
    print()
    print("  5. Use the data with existing analysis modules")
    print()
    print("📚 Resources:")
    print("  • ATC Hub: https://hub.arcgis.com/search?q=appalachian%20trail")
    print("  • USGS Elevation: https://nationalmap.gov/epqs/")
    print("  • ArcGIS REST API Docs: https://developers.arcgis.com/rest/")
    
    print("\n" + "="*80)
    print("  DEMO COMPLETE")
    print("="*80)
    print()
    print("✨ The analysis can now use either:")
    print("   • Synthetic data (current method - for demonstration)")
    print("   • Real ArcGIS data (enhanced accuracy)")
    print()
    print("Both work with all existing analysis modules!")
    print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

