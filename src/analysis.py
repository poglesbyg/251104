"""
Analysis module for Appalachian Trail data.
Provides statistical analysis and insights.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import signal


class TrailAnalyzer:
    """Analyze trail data for insights and statistics."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with trail data.
        
        Args:
            df: DataFrame with trail data
        """
        self.df = df.copy()
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """Calculate derived metrics like grade and cumulative gain."""
        # Calculate elevation change between points
        self.df['elev_change'] = self.df['elevation_ft'].diff()
        
        # Calculate distance between points
        self.df['segment_distance'] = self.df['distance_miles'].diff()
        
        # Calculate grade (elevation change per mile)
        self.df['grade_percent'] = (
            (self.df['elev_change'] / (self.df['segment_distance'] * 5280)) * 100
        ).fillna(0)
        
        # Categorize grade difficulty
        self.df['difficulty'] = pd.cut(
            self.df['grade_percent'].abs(),
            bins=[-np.inf, 5, 10, 15, 20, np.inf],
            labels=['Easy', 'Moderate', 'Difficult', 'Very Difficult', 'Extreme']
        )
        
        # Cumulative elevation gain
        self.df['cumulative_gain'] = (
            self.df['elev_change'].clip(lower=0).cumsum()
        )
        
        # Cumulative elevation loss
        self.df['cumulative_loss'] = (
            self.df['elev_change'].clip(upper=0).abs().cumsum()
        )
    
    def find_peaks_and_valleys(self, prominence: int = 500) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find significant peaks and valleys in elevation profile.
        
        Args:
            prominence: Minimum prominence in feet for a peak/valley
            
        Returns:
            Tuple of (peak_indices, valley_indices)
        """
        elevations = self.df['elevation_ft'].values
        
        # Find peaks
        peaks, _ = signal.find_peaks(elevations, prominence=prominence)
        
        # Find valleys (peaks in negative elevation)
        valleys, _ = signal.find_peaks(-elevations, prominence=prominence)
        
        return peaks, valleys
    
    def analyze_difficulty_distribution(self) -> pd.DataFrame:
        """
        Analyze trail difficulty distribution.
        
        Returns:
            DataFrame with difficulty statistics by category
        """
        difficulty_stats = self.df.groupby('difficulty', observed=True).agg({
            'segment_distance': 'sum',
            'grade_percent': ['mean', 'max'],
            'elev_change': 'sum'
        }).round(2)
        
        difficulty_stats.columns = ['Miles', 'Avg Grade %', 'Max Grade %', 'Total Elev Change']
        
        # Calculate percentage of trail
        total_miles = difficulty_stats['Miles'].sum()
        difficulty_stats['% of Trail'] = (
            (difficulty_stats['Miles'] / total_miles * 100).round(1)
        )
        
        return difficulty_stats
    
    def get_toughest_sections(self, n: int = 10, window_miles: float = 5.0) -> pd.DataFrame:
        """
        Find the toughest sections of trail based on elevation gain per mile.
        
        Args:
            n: Number of tough sections to return
            window_miles: Window size in miles to analyze
            
        Returns:
            DataFrame with toughest sections
        """
        # Calculate rolling elevation gain
        window_points = int(window_miles / self.df['segment_distance'].mean())
        
        rolling_gain = (
            self.df['elev_change']
            .clip(lower=0)
            .rolling(window=window_points, min_periods=1)
            .sum()
        )
        
        # Find peak sections
        top_indices = rolling_gain.nlargest(n).index
        
        sections = []
        for idx in top_indices:
            start_idx = max(0, idx - window_points // 2)
            end_idx = min(len(self.df), idx + window_points // 2)
            
            section_data = self.df.iloc[start_idx:end_idx]
            
            sections.append({
                'Start Mile': section_data['distance_miles'].iloc[0],
                'End Mile': section_data['distance_miles'].iloc[-1],
                'State': section_data['state'].iloc[len(section_data) // 2],
                'Elevation Gain': section_data['elev_change'].clip(lower=0).sum(),
                'Max Elevation': section_data['elevation_ft'].max(),
                'Avg Grade %': section_data['grade_percent'].mean()
            })
        
        return pd.DataFrame(sections).round(2)
    
    def analyze_by_state(self) -> pd.DataFrame:
        """
        Comprehensive state-by-state analysis.
        
        Returns:
            DataFrame with statistics for each state
        """
        state_stats = []
        
        for state in self.df['state'].unique():
            state_data = self.df[self.df['state'] == state]
            elev_changes = state_data['elev_change']
            
            stats = {
                'State': state,
                'Miles': state_data['distance_miles'].max() - state_data['distance_miles'].min(),
                'Min Elevation': state_data['elevation_ft'].min(),
                'Max Elevation': state_data['elevation_ft'].max(),
                'Elev Range': state_data['elevation_ft'].max() - state_data['elevation_ft'].min(),
                'Total Gain': elev_changes[elev_changes > 0].sum(),
                'Total Loss': abs(elev_changes[elev_changes < 0].sum()),
                'Avg Elevation': state_data['elevation_ft'].mean(),
                'Avg Grade %': abs(state_data['grade_percent']).mean(),
                'Max Grade %': abs(state_data['grade_percent']).max()
            }
            
            state_stats.append(stats)
        
        return pd.DataFrame(state_stats).round(2)
    
    def calculate_hiking_time_estimates(self, 
                                       flat_speed_mph: float = 3.0,
                                       ascent_time_ft_per_hour: float = 1000.0,
                                       descent_time_ft_per_hour: float = 2000.0) -> Dict:
        """
        Estimate hiking times using Naismith's rule variants.
        
        Args:
            flat_speed_mph: Average speed on flat terrain
            ascent_time_ft_per_hour: Feet of elevation gain per hour
            descent_time_ft_per_hour: Feet of elevation loss per hour
            
        Returns:
            Dictionary with time estimates
        """
        total_distance = self.df['distance_miles'].max()
        total_gain = self.df['cumulative_gain'].max()
        total_loss = self.df['cumulative_loss'].max()
        
        # Calculate time components
        flat_time_hours = total_distance / flat_speed_mph
        ascent_time_hours = total_gain / ascent_time_ft_per_hour
        descent_penalty_hours = total_loss / descent_time_ft_per_hour
        
        total_time_hours = flat_time_hours + ascent_time_hours + descent_penalty_hours
        
        # Convert to days assuming 8 hours hiking per day
        hiking_days = total_time_hours / 8
        
        return {
            'total_hours': round(total_time_hours, 1),
            'hiking_days_8hr': round(hiking_days, 1),
            'hiking_days_10hr': round(total_time_hours / 10, 1),
            'typical_thru_hike_months': round(hiking_days / 30, 1),
            'components': {
                'flat_time_hours': round(flat_time_hours, 1),
                'ascent_time_hours': round(ascent_time_hours, 1),
                'descent_time_hours': round(descent_penalty_hours, 1)
            }
        }
    
    def get_summary_statistics(self) -> Dict:
        """
        Get comprehensive summary statistics.
        
        Returns:
            Dictionary with summary statistics
        """
        peaks, valleys = self.find_peaks_and_valleys()
        
        return {
            'total_distance_miles': round(self.df['distance_miles'].max(), 1),
            'total_elevation_gain_ft': round(self.df['cumulative_gain'].max(), 0),
            'total_elevation_loss_ft': round(self.df['cumulative_loss'].max(), 0),
            'min_elevation_ft': round(self.df['elevation_ft'].min(), 0),
            'max_elevation_ft': round(self.df['elevation_ft'].max(), 0),
            'avg_elevation_ft': round(self.df['elevation_ft'].mean(), 0),
            'elevation_range_ft': round(
                self.df['elevation_ft'].max() - self.df['elevation_ft'].min(), 0
            ),
            'num_significant_peaks': len(peaks),
            'num_significant_valleys': len(valleys),
            'avg_grade_percent': round(abs(self.df['grade_percent']).mean(), 2),
            'max_grade_percent': round(abs(self.df['grade_percent']).max(), 2),
            'num_states': self.df['state'].nunique(),
            'hiking_time_estimates': self.calculate_hiking_time_estimates()
        }


if __name__ == '__main__':
    from data_loader import load_or_generate_data
    
    # Load data
    df, _ = load_or_generate_data('../data/trail_data.csv')
    
    # Analyze
    analyzer = TrailAnalyzer(df)
    
    print("=== APPALACHIAN TRAIL ANALYSIS ===\n")
    
    summary = analyzer.get_summary_statistics()
    print("Summary Statistics:")
    for key, value in summary.items():
        if key != 'hiking_time_estimates':
            print(f"  {key}: {value}")
    
    print("\n=== State-by-State Analysis ===")
    print(analyzer.analyze_by_state())
    
    print("\n=== Difficulty Distribution ===")
    print(analyzer.analyze_difficulty_distribution())
    
    print("\n=== Toughest Sections ===")
    print(analyzer.get_toughest_sections())
    
    print("\n=== Hiking Time Estimates ===")
    time_est = summary['hiking_time_estimates']
    print(f"Total hiking time: {time_est['total_hours']} hours")
    print(f"Estimated thru-hike: {time_est['hiking_days_8hr']} days (8hr/day)")
    print(f"Typical thru-hike: {time_est['typical_thru_hike_months']} months")

