"""
Data loader module for Appalachian Trail data.
Creates a realistic dataset based on actual AT characteristics.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
import json


class AppalachianTrailData:
    """Generate and manage Appalachian Trail data."""
    
    # Actual AT state information
    STATES = [
        {'name': 'Georgia', 'miles': 75.0, 'start_elev': 3782, 'max_elev': 4461},
        {'name': 'North Carolina', 'miles': 95.7, 'start_elev': 3500, 'max_elev': 6643},
        {'name': 'Tennessee', 'miles': 71.6, 'start_elev': 3500, 'max_elev': 6643},
        {'name': 'Virginia', 'miles': 544.6, 'start_elev': 2500, 'max_elev': 5729},
        {'name': 'West Virginia', 'miles': 4.0, 'start_elev': 1200, 'max_elev': 1500},
        {'name': 'Maryland', 'miles': 40.9, 'start_elev': 1000, 'max_elev': 1880},
        {'name': 'Pennsylvania', 'miles': 229.6, 'start_elev': 800, 'max_elev': 2080},
        {'name': 'New Jersey', 'miles': 72.2, 'start_elev': 400, 'max_elev': 1653},
        {'name': 'New York', 'miles': 88.4, 'start_elev': 400, 'max_elev': 1433},
        {'name': 'Connecticut', 'miles': 51.6, 'start_elev': 500, 'max_elev': 2316},
        {'name': 'Massachusetts', 'miles': 90.0, 'start_elev': 800, 'max_elev': 3491},
        {'name': 'Vermont', 'miles': 150.0, 'start_elev': 1000, 'max_elev': 4393},
        {'name': 'New Hampshire', 'miles': 161.0, 'start_elev': 1500, 'max_elev': 6288},
        {'name': 'Maine', 'miles': 281.4, 'start_elev': 1000, 'max_elev': 5267}
    ]
    
    def __init__(self, points_per_mile: int = 10):
        """
        Initialize the data generator.
        
        Args:
            points_per_mile: Number of data points to generate per mile
        """
        self.points_per_mile = points_per_mile
        self.total_miles = sum(state['miles'] for state in self.STATES)
        
    def generate_trail_data(self) -> pd.DataFrame:
        """
        Generate a realistic trail dataset with coordinates and elevation.
        
        Returns:
            DataFrame with trail data
        """
        # Calculate total points needed
        total_points = int(self.total_miles * self.points_per_mile)
        
        # Starting point: Springer Mountain, GA
        start_lat, start_lon = 34.6268, -84.1938
        # Ending point: Mount Katahdin, ME
        end_lat, end_lon = 45.9044, -68.9213
        
        data = []
        cumulative_miles = 0
        point_idx = 0
        
        for state in self.STATES:
            state_points = int(state['miles'] * self.points_per_mile)
            
            for i in range(state_points):
                # Calculate position along trail
                progress = (cumulative_miles + (i / self.points_per_mile)) / self.total_miles
                
                # Interpolate coordinates (simplified linear interpolation)
                lat = start_lat + (end_lat - start_lat) * progress
                lon = start_lon + (end_lon - start_lon) * progress
                
                # Add some realistic wiggle to the path
                lat += np.random.normal(0, 0.01)
                lon += np.random.normal(0, 0.01)
                
                # Generate realistic elevation profile
                state_progress = i / state_points
                
                # Create varied terrain with peaks and valleys
                base_elev = state['start_elev']
                max_elev = state['max_elev']
                
                # Multiple sine waves for realistic terrain
                elev_variation = (
                    np.sin(state_progress * np.pi * 3) * (max_elev - base_elev) * 0.3 +
                    np.sin(state_progress * np.pi * 7) * (max_elev - base_elev) * 0.2 +
                    np.sin(state_progress * np.pi * 13) * (max_elev - base_elev) * 0.1
                )
                
                elevation = base_elev + elev_variation + np.random.normal(0, 20)
                elevation = max(0, min(elevation, max_elev * 1.1))
                
                data.append({
                    'point_id': point_idx,
                    'latitude': lat,
                    'longitude': lon,
                    'elevation_ft': elevation,
                    'distance_miles': cumulative_miles + (i / self.points_per_mile),
                    'state': state['name']
                })
                
                point_idx += 1
            
            cumulative_miles += state['miles']
        
        df = pd.DataFrame(data)
        return df
    
    def calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate trail statistics from the data.
        
        Args:
            df: Trail dataframe
            
        Returns:
            Dictionary of statistics
        """
        # Calculate elevation gain/loss
        elevation_changes = df['elevation_ft'].diff()
        total_gain = elevation_changes[elevation_changes > 0].sum()
        total_loss = abs(elevation_changes[elevation_changes < 0].sum())
        
        # State-by-state statistics
        state_stats = []
        for state in self.STATES:
            state_data = df[df['state'] == state['name']]
            if len(state_data) > 0:
                state_stats.append({
                    'state': state['name'],
                    'miles': state['miles'],
                    'min_elevation': state_data['elevation_ft'].min(),
                    'max_elevation': state_data['elevation_ft'].max(),
                    'avg_elevation': state_data['elevation_ft'].mean(),
                    'elev_gain': elevation_changes[state_data.index][
                        elevation_changes[state_data.index] > 0
                    ].sum() if len(state_data) > 1 else 0
                })
        
        return {
            'total_distance_miles': self.total_miles,
            'total_elevation_gain_ft': total_gain,
            'total_elevation_loss_ft': total_loss,
            'min_elevation_ft': df['elevation_ft'].min(),
            'max_elevation_ft': df['elevation_ft'].max(),
            'avg_elevation_ft': df['elevation_ft'].mean(),
            'num_states': len(self.STATES),
            'state_statistics': state_stats
        }
    
    def save_data(self, df: pd.DataFrame, filepath: str):
        """Save trail data to CSV."""
        df.to_csv(filepath, index=False)
        
    def save_statistics(self, stats: Dict, filepath: str):
        """Save statistics to JSON."""
        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: convert_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            return obj
        
        stats = convert_types(stats)
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)


def load_or_generate_data(data_path: str = '../data/trail_data.csv') -> Tuple[pd.DataFrame, Dict]:
    """
    Load existing trail data or generate new data.
    
    Args:
        data_path: Path to the trail data CSV
        
    Returns:
        Tuple of (DataFrame, statistics dict)
    """
    import os
    
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        stats_path = data_path.replace('trail_data.csv', 'trail_stats.json')
        if os.path.exists(stats_path):
            with open(stats_path, 'r') as f:
                stats = json.load(f)
        else:
            at_data = AppalachianTrailData()
            stats = at_data.calculate_statistics(df)
    else:
        at_data = AppalachianTrailData(points_per_mile=10)
        df = at_data.generate_trail_data()
        stats = at_data.calculate_statistics(df)
        
        # Save the generated data
        at_data.save_data(df, data_path)
        stats_path = data_path.replace('trail_data.csv', 'trail_stats.json')
        at_data.save_statistics(stats, stats_path)
    
    return df, stats


if __name__ == '__main__':
    # Generate the data
    at_data = AppalachianTrailData(points_per_mile=10)
    df = at_data.generate_trail_data()
    stats = at_data.calculate_statistics(df)
    
    # Save data
    at_data.save_data(df, '../data/trail_data.csv')
    at_data.save_statistics(stats, '../data/trail_stats.json')
    
    print(f"Generated {len(df)} data points for {stats['total_distance_miles']:.1f} miles of trail")
    print(f"Elevation range: {stats['min_elevation_ft']:.0f} - {stats['max_elevation_ft']:.0f} feet")
    print(f"Total elevation gain: {stats['total_elevation_gain_ft']:.0f} feet")


