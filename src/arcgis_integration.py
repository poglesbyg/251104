"""
ArcGIS integration for Appalachian Trail analysis.
Fetches real geographic data from ArcGIS services.
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime


class ArcGISDataFetcher:
    """
    Fetch Appalachian Trail data from ArcGIS services.
    """
    
    # ArcGIS REST API endpoints
    ARCGIS_BASE_URL = "https://services.arcgis.com"
    
    # Appalachian Trail Natural Resource Condition Assessment (Official)
    AT_NRCA_HUB = "https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com"
    AT_NRCA_DATASETS = "https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset"
    AT_NRCA_APP = "https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/apps/61c37a4a9a004ee994bde60d6792041b/explore"
    
    # REAL WORKING SERVICE! Appalachian National Scenic Trail
    # Source: https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services
    AT_TRAIL_SERVICE = "https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services/Appalachian_National_Scenic_Trail/FeatureServer"
    ATC_SERVICE_URL = "https://services6.arcgis.com/9tSn0MQDcjQ12ht2/arcgis/rest/services"
    
    # USGS Elevation service
    USGS_ELEVATION_URL = "https://nationalmap.gov/epqs/pqs.php"
    
    # NPS (National Park Service) Trail data
    NPS_BASE_URL = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services"
    
    def __init__(self, cache_dir: str = '../data/arcgis_cache'):
        """
        Initialize ArcGIS data fetcher.
        
        Args:
            cache_dir: Directory to cache downloaded data
        """
        self.cache_dir = cache_dir
        import os
        os.makedirs(cache_dir, exist_ok=True)
        
    def fetch_trail_centerline(self, output_format: str = 'geojson') -> Optional[Dict]:
        """
        Fetch the official AT centerline from ArcGIS.
        
        Args:
            output_format: Output format ('geojson', 'json', etc.)
            
        Returns:
            GeoJSON or dict with trail data
        """
        # Use the real working AT service!
        url = f"{self.AT_TRAIL_SERVICE}/0/query"
        
        params = {
            'where': '1=1',  # Get all features
            'outFields': '*',
            'f': output_format,
            'returnGeometry': 'true'
        }
        
        try:
            print(f"Fetching AT centerline from ArcGIS...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Successfully fetched {len(data.get('features', []))} features")
                return data
            else:
                print(f"⚠ API returned status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠ Could not fetch from ArcGIS: {e}")
            print("  Tip: Check if the service URL is current at ArcGIS Hub")
            return None
    
    def fetch_elevation_profile(self, coordinates: List[Tuple[float, float]], 
                               sample_rate: int = 100) -> pd.DataFrame:
        """
        Fetch elevation data for trail coordinates using USGS Elevation API.
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            sample_rate: Sample every Nth coordinate to reduce API calls
            
        Returns:
            DataFrame with coordinates and elevations
        """
        elevations = []
        sampled_coords = coordinates[::sample_rate] if len(coordinates) > sample_rate else coordinates
        
        print(f"Fetching elevation data for {len(sampled_coords)} points...")
        
        for i, (lon, lat) in enumerate(sampled_coords):
            try:
                params = {
                    'x': lon,
                    'y': lat,
                    'units': 'Feet',
                    'output': 'json'
                }
                
                response = requests.get(self.USGS_ELEVATION_URL, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    elevation = data.get('USGS_Elevation_Point_Query_Service', {}).get('Elevation_Query', {}).get('Elevation')
                    
                    if elevation:
                        elevations.append({
                            'longitude': lon,
                            'latitude': lat,
                            'elevation_ft': float(elevation)
                        })
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i + 1}/{len(sampled_coords)}")
                    
            except Exception as e:
                print(f"  ⚠ Error at point {i}: {e}")
                continue
        
        print(f"✓ Successfully fetched {len(elevations)} elevation points")
        return pd.DataFrame(elevations)
    
    def fetch_trail_features(self, feature_type: str = 'shelters') -> Optional[pd.DataFrame]:
        """
        Fetch trail features (shelters, water sources, towns, etc.).
        
        Args:
            feature_type: Type of feature ('shelters', 'water', 'towns', etc.)
            
        Returns:
            DataFrame with feature locations and attributes
        """
        # This would query specific feature layers
        # Example structure - actual endpoints vary
        feature_urls = {
            'shelters': 'AT_Shelters/FeatureServer/0',
            'water': 'AT_Water_Sources/FeatureServer/0',
            'parking': 'AT_Parking/FeatureServer/0',
            'towns': 'AT_Towns/FeatureServer/0'
        }
        
        if feature_type not in feature_urls:
            print(f"⚠ Unknown feature type: {feature_type}")
            return None
        
        url = f"{self.ATC_SERVICE_URL}/{feature_urls[feature_type]}/query"
        
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'json',
            'returnGeometry': 'true'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                # Convert to DataFrame
                records = []
                for feature in features:
                    attrs = feature.get('attributes', {})
                    geom = feature.get('geometry', {})
                    
                    record = attrs.copy()
                    record['longitude'] = geom.get('x')
                    record['latitude'] = geom.get('y')
                    records.append(record)
                
                return pd.DataFrame(records)
            else:
                print(f"⚠ API returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠ Error fetching {feature_type}: {e}")
            return None
    
    def query_esri_living_atlas(self, query_type: str = 'terrain') -> Optional[Dict]:
        """
        Query Esri Living Atlas for contextual data.
        
        Args:
            query_type: Type of data ('terrain', 'landcover', 'climate', etc.)
            
        Returns:
            Dictionary with query results
        """
        # Living Atlas provides various basemaps and data layers
        living_atlas_services = {
            'terrain': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer',
            'imagery': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer',
            'landcover': 'https://landscape.blm.gov/geoportal/rest/find/document',
        }
        
        print(f"Living Atlas services available for: {', '.join(living_atlas_services.keys())}")
        return living_atlas_services
    
    def create_enhanced_dataset(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Create an enhanced dataset combining real ArcGIS data with analysis needs.
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            DataFrame with enhanced trail data
        """
        import os
        cache_file = os.path.join(self.cache_dir, 'arcgis_enhanced_trail.csv')
        
        if use_cache and os.path.exists(cache_file):
            print(f"Loading cached ArcGIS data from {cache_file}")
            return pd.read_csv(cache_file)
        
        print("\n" + "="*70)
        print("CREATING ENHANCED DATASET WITH ARCGIS DATA")
        print("="*70 + "\n")
        
        # Step 1: Try to fetch trail centerline
        print("Step 1: Fetching trail centerline...")
        centerline = self.fetch_trail_centerline()
        
        if centerline and 'features' in centerline:
            # Extract coordinates from GeoJSON
            coordinates = self._extract_coordinates_from_geojson(centerline)
            print(f"  ✓ Extracted {len(coordinates)} coordinate points")
            
            # Step 2: Fetch elevations
            print("\nStep 2: Fetching elevation data...")
            elevation_df = self.fetch_elevation_profile(coordinates, sample_rate=50)
            
            if len(elevation_df) > 0:
                # Save to cache
                elevation_df.to_csv(cache_file, index=False)
                print(f"\n✓ Enhanced dataset saved to {cache_file}")
                return elevation_df
        
        print("\n⚠ Could not fetch real ArcGIS data.")
        print("  Falling back to synthetic data generation.")
        print("  To use real data, check ArcGIS Hub for current service endpoints:")
        print("  - https://hub.arcgis.com")
        print("  - Search for 'Appalachian Trail Conservancy'")
        
        return None
    
    def _extract_coordinates_from_geojson(self, geojson: Dict) -> List[Tuple[float, float]]:
        """Extract coordinate pairs from GeoJSON features."""
        coordinates = []
        
        for feature in geojson.get('features', []):
            geometry = feature.get('geometry', {})
            geom_type = geometry.get('type', '')
            coords = geometry.get('coordinates', [])
            
            if geom_type == 'LineString':
                coordinates.extend([(c[0], c[1]) for c in coords])
            elif geom_type == 'MultiLineString':
                for line in coords:
                    coordinates.extend([(c[0], c[1]) for c in line])
        
        return coordinates
    
    def get_arcgis_resources(self) -> Dict:
        """
        Get information about available ArcGIS resources for the AT.
        
        Returns:
            Dictionary of available resources and endpoints
        """
        resources = {
            'official_sources': {
                'AT_NRCA_Hub': {
                    'url': 'https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com',
                    'description': 'Appalachian Trail Natural Resource Condition Assessment - Official NPS/ATC Hub'
                },
                'AT_NRCA_Datasets': {
                    'url': 'https://appalachian-trail-natural-resource-condition-assessment-clus.hub.arcgis.com/search?collection=dataset',
                    'description': 'Direct link to browse all available AT datasets'
                },
                'ATC_Hub': {
                    'url': 'https://hub.arcgis.com/search?collection=Organization&orgid=fBc8EJBxQRMcHlei',
                    'description': 'Appalachian Trail Conservancy official data'
                }
            },
            'usgs_services': {
                'elevation': self.USGS_ELEVATION_URL,
                'description': 'USGS National Map elevation service'
            },
            'esri_living_atlas': {
                'url': 'https://livingatlas.arcgis.com',
                'description': 'Contextual data layers (terrain, imagery, climate)'
            },
            'nps_services': {
                'url': 'https://www.nps.gov/subjects/gis/services.htm',
                'description': 'National Park Service GIS data'
            },
            'data_types': [
                'Trail centerline geometry',
                'Elevation profiles (DEM)',
                'Shelter locations',
                'Water sources',
                'Road crossings',
                'Town locations',
                'Trail conditions',
                'Land ownership',
                'Vegetation/terrain types',
                'Viewshed analysis'
            ]
        }
        
        return resources


class ArcGISEnhancedAnalysis:
    """Enhanced trail analysis using real ArcGIS data."""
    
    def __init__(self, arcgis_data: pd.DataFrame):
        """
        Initialize with ArcGIS-sourced data.
        
        Args:
            arcgis_data: DataFrame with real trail data from ArcGIS
        """
        self.data = arcgis_data
    
    def compare_with_synthetic(self, synthetic_data: pd.DataFrame) -> Dict:
        """
        Compare real ArcGIS data with synthetic data.
        
        Args:
            synthetic_data: Synthetic trail data
            
        Returns:
            Comparison metrics
        """
        comparison = {
            'data_points': {
                'arcgis': len(self.data),
                'synthetic': len(synthetic_data)
            },
            'elevation_range': {
                'arcgis': (self.data['elevation_ft'].min(), self.data['elevation_ft'].max()),
                'synthetic': (synthetic_data['elevation_ft'].min(), synthetic_data['elevation_ft'].max())
            }
        }
        
        return comparison


def create_arcgis_integration_guide():
    """Print a guide for integrating ArcGIS data."""
    
    guide = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║         ArcGIS Integration Guide for Appalachian Trail              ║
    ╚══════════════════════════════════════════════════════════════════════╝
    
    🗺️  AVAILABLE DATA SOURCES
    
    1. Appalachian Trail Conservancy (ATC) ArcGIS Hub
       - Official trail centerline
       - Shelter locations
       - Water sources
       - Trail markers
       URL: https://hub.arcgis.com (search "Appalachian Trail")
    
    2. USGS National Map
       - Elevation data (DEM)
       - Topographic maps
       - Hydrography
       URL: https://nationalmap.gov
    
    3. Esri Living Atlas
       - Basemaps (terrain, imagery, topo)
       - Climate data
       - Land cover
       URL: https://livingatlas.arcgis.com
    
    4. National Park Service
       - Park boundaries
       - Facilities
       - Trail conditions
       URL: https://www.nps.gov/subjects/gis
    
    📦 REQUIRED PACKAGES
    
    To use ArcGIS integration, install:
    
        uv add arcgis                    # ArcGIS Python API
        uv add requests                  # Already included
        uv add geopy                     # Already included
    
    Or for full GIS capabilities:
    
        uv add arcgis geopandas shapely
    
    🚀 USAGE EXAMPLES
    
    1. Basic Setup:
    
        from src.arcgis_integration import ArcGISDataFetcher
        
        fetcher = ArcGISDataFetcher()
        resources = fetcher.get_arcgis_resources()
        print(resources)
    
    2. Fetch Real Trail Data:
    
        # Get trail centerline
        trail_data = fetcher.fetch_trail_centerline()
        
        # Get elevation profile
        coords = [(lon, lat), ...]  # Your trail coordinates
        elevations = fetcher.fetch_elevation_profile(coords)
    
    3. Create Enhanced Dataset:
    
        enhanced_data = fetcher.create_enhanced_dataset()
        # This will fetch real data and cache it
    
    4. Use with Existing Analysis:
    
        from src.analysis import TrailAnalyzer
        
        analyzer = TrailAnalyzer(enhanced_data)
        summary = analyzer.get_summary_statistics()
    
    🔧 CONFIGURATION
    
    Set up authentication for private ArcGIS services:
    
        from arcgis.gis import GIS
        
        gis = GIS("https://www.arcgis.com", "username", "password")
        # Or use API key for public access
    
    💡 TIPS
    
    - Start with public data (no authentication needed)
    - Cache downloaded data to avoid repeated API calls
    - Respect API rate limits (add delays if needed)
    - Check ArcGIS Hub for latest service endpoints
    - Use sample_rate parameter to reduce API calls for elevation
    
    📊 DATA YOU CAN GET
    
    ✓ Exact trail coordinates (not interpolated)
    ✓ Real elevation profile from USGS DEM
    ✓ Shelter locations with amenities
    ✓ Water source locations and reliability
    ✓ Town distances and services
    ✓ Road crossings and parking areas
    ✓ Land ownership (NPS, USFS, private, etc.)
    ✓ Trail difficulty ratings (official)
    ✓ Historical trail relocations
    ✓ Real-time conditions (if available)
    
    🔗 NEXT STEPS
    
    1. Visit ArcGIS Hub and explore available AT datasets
    2. Install arcgis Python package if needed
    3. Run: python -c "from src.arcgis_integration import *; create_arcgis_integration_guide()"
    4. Try fetching a small dataset first
    5. Integrate with existing analysis modules
    
    ═══════════════════════════════════════════════════════════════════════
    """
    
    print(guide)


if __name__ == '__main__':
    # Print integration guide
    create_arcgis_integration_guide()
    
    # Demonstrate basic usage
    print("\n" + "="*70)
    print("TESTING ARCGIS INTEGRATION")
    print("="*70 + "\n")
    
    fetcher = ArcGISDataFetcher()
    
    # Show available resources
    print("Available ArcGIS Resources:")
    resources = fetcher.get_arcgis_resources()
    print(json.dumps(resources, indent=2))
    
    print("\n" + "="*70)
    print("To fetch real data, run:")
    print("  python src/arcgis_integration.py")
    print("\nNote: Some services may require updates to endpoints.")
    print("Check ArcGIS Hub for current URLs.")
    print("="*70)

