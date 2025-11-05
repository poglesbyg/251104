"""
Fastest Known Time (FKT) Analysis for the Appalachian Trail.
Analyzes the incredible 40 days, 18 hours, 6 minutes record.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple
from datetime import timedelta


class FKTAnalyzer:
    """Analyze Appalachian Trail FKT performance."""
    
    # FKT Record: 40 days, 18 hours, 6 minutes
    FKT_DAYS = 40
    FKT_HOURS = 18
    FKT_MINUTES = 6
    FKT_TOTAL_HOURS = FKT_DAYS * 24 + FKT_HOURS + FKT_MINUTES / 60
    
    # Typical thru-hike times
    TYPICAL_THRU_HIKE_DAYS = 150  # 5 months average
    FAST_THRU_HIKE_DAYS = 90      # 3 months for fast hikers
    
    def __init__(self, trail_data: pd.DataFrame, trail_analyzer=None):
        """
        Initialize FKT analyzer.
        
        Args:
            trail_data: DataFrame with trail data
            trail_analyzer: Optional TrailAnalyzer instance (recommended for full metrics)
        """
        self.df = trail_data.copy()
        self.analyzer = trail_analyzer
        self.total_distance = self.df['distance_miles'].max()
        
        # Get elevation gain from analyzer if available, otherwise calculate
        if trail_analyzer and hasattr(trail_analyzer, 'df') and 'cumulative_gain' in trail_analyzer.df.columns:
            self.total_elevation_gain = trail_analyzer.df['cumulative_gain'].max()
            self.df = trail_analyzer.df.copy()  # Use the enriched dataframe
        elif 'elev_change' in self.df.columns:
            self.total_elevation_gain = self.df['elev_change'].clip(lower=0).sum()
        else:
            self.total_elevation_gain = 0
    
    def get_fkt_metrics(self) -> Dict:
        """
        Calculate comprehensive FKT metrics.
        
        Returns:
            Dictionary with FKT performance metrics
        """
        fkt_total_minutes = self.FKT_DAYS * 24 * 60 + self.FKT_HOURS * 60 + self.FKT_MINUTES
        
        # Calculate paces
        avg_mph = self.total_distance / self.FKT_TOTAL_HOURS
        minutes_per_mile = self.FKT_TOTAL_HOURS * 60 / self.total_distance
        miles_per_day = self.total_distance / (self.FKT_DAYS + self.FKT_HOURS / 24)
        
        # Sleep and rest assumptions
        # FKT attempts typically involve 4-6 hours sleep per day
        assumed_sleep_hours_per_day = 4
        total_sleep_hours = assumed_sleep_hours_per_day * self.FKT_DAYS
        hiking_hours = self.FKT_TOTAL_HOURS - total_sleep_hours
        
        # Calculate moving pace
        moving_mph = self.total_distance / hiking_hours if hiking_hours > 0 else 0
        hiking_hours_per_day = hiking_hours / self.FKT_DAYS
        
        # Elevation rate
        elevation_gain_per_hour = self.total_elevation_gain / self.FKT_TOTAL_HOURS
        elevation_gain_per_day = self.total_elevation_gain / self.FKT_DAYS
        
        return {
            'fkt_record': {
                'days': self.FKT_DAYS,
                'hours': self.FKT_HOURS,
                'minutes': self.FKT_MINUTES,
                'total_hours': round(self.FKT_TOTAL_HOURS, 2),
                'total_minutes': fkt_total_minutes,
                'formatted': f"{self.FKT_DAYS}d {self.FKT_HOURS}h {self.FKT_MINUTES}m"
            },
            'pace_metrics': {
                'avg_mph_overall': round(avg_mph, 2),
                'avg_mph_moving': round(moving_mph, 2),
                'minutes_per_mile': round(minutes_per_mile, 2),
                'miles_per_day': round(miles_per_day, 2),
                'hiking_hours_per_day': round(hiking_hours_per_day, 2),
                'total_hiking_hours': round(hiking_hours, 1)
            },
            'elevation_metrics': {
                'total_gain_ft': round(self.total_elevation_gain, 0),
                'gain_per_hour_ft': round(elevation_gain_per_hour, 0),
                'gain_per_day_ft': round(elevation_gain_per_day, 0)
            },
            'comparison': {
                'vs_typical_thru_hike': round(self.TYPICAL_THRU_HIKE_DAYS / (self.FKT_DAYS + self.FKT_HOURS / 24), 2),
                'vs_fast_thru_hike': round(self.FAST_THRU_HIKE_DAYS / (self.FKT_DAYS + self.FKT_HOURS / 24), 2)
            }
        }
    
    def calculate_daily_segments(self) -> pd.DataFrame:
        """
        Calculate what each day of the FKT attempt would look like.
        
        Returns:
            DataFrame with daily segment breakdown
        """
        miles_per_day = self.total_distance / (self.FKT_DAYS + self.FKT_HOURS / 24)
        
        daily_segments = []
        current_mile = 0
        
        for day in range(1, self.FKT_DAYS + 2):  # +2 to capture partial last day
            start_mile = current_mile
            end_mile = min(current_mile + miles_per_day, self.total_distance)
            
            if start_mile >= self.total_distance:
                break
            
            # Get data for this segment
            segment_data = self.df[
                (self.df['distance_miles'] >= start_mile) & 
                (self.df['distance_miles'] < end_mile)
            ]
            
            if len(segment_data) > 0:
                # Calculate metrics for this day
                elev_changes = segment_data['elev_change'] if 'elev_change' in segment_data.columns else 0
                gain = elev_changes[elev_changes > 0].sum() if hasattr(elev_changes, 'sum') else 0
                loss = abs(elev_changes[elev_changes < 0].sum()) if hasattr(elev_changes, 'sum') else 0
                
                daily_segments.append({
                    'Day': day,
                    'Start Mile': round(start_mile, 1),
                    'End Mile': round(end_mile, 1),
                    'Miles': round(end_mile - start_mile, 1),
                    'Starting State': segment_data.iloc[0]['state'] if len(segment_data) > 0 else '',
                    'Ending State': segment_data.iloc[-1]['state'] if len(segment_data) > 0 else '',
                    'Min Elevation': round(segment_data['elevation_ft'].min(), 0),
                    'Max Elevation': round(segment_data['elevation_ft'].max(), 0),
                    'Elevation Gain': round(gain, 0),
                    'Elevation Loss': round(loss, 0),
                    'Avg Elevation': round(segment_data['elevation_ft'].mean(), 0)
                })
            
            current_mile = end_mile
        
        return pd.DataFrame(daily_segments)
    
    def identify_toughest_days(self, daily_segments: pd.DataFrame, n: int = 5) -> pd.DataFrame:
        """
        Identify the toughest days based on elevation gain.
        
        Args:
            daily_segments: DataFrame from calculate_daily_segments()
            n: Number of toughest days to return
            
        Returns:
            DataFrame with toughest days
        """
        return daily_segments.nlargest(n, 'Elevation Gain')[
            ['Day', 'Start Mile', 'End Mile', 'Starting State', 'Ending State', 
             'Miles', 'Elevation Gain', 'Max Elevation']
        ]
    
    def compare_pacing_strategies(self) -> pd.DataFrame:
        """
        Compare different pacing strategies including FKT.
        
        Returns:
            DataFrame comparing different hiking strategies
        """
        strategies = []
        
        # FKT
        fkt_metrics = self.get_fkt_metrics()
        strategies.append({
            'Strategy': 'FKT Record',
            'Total Days': self.FKT_DAYS + self.FKT_HOURS / 24,
            'Miles/Day': fkt_metrics['pace_metrics']['miles_per_day'],
            'Hours/Day': fkt_metrics['pace_metrics']['hiking_hours_per_day'] + 4,  # Include sleep
            'Moving MPH': fkt_metrics['pace_metrics']['avg_mph_moving'],
            'Difficulty': 'Extreme Elite'
        })
        
        # Ultra-fast thru-hike (60 days)
        ultra_days = 60
        strategies.append({
            'Strategy': 'Ultra-Fast Thru-hike',
            'Total Days': ultra_days,
            'Miles/Day': round(self.total_distance / ultra_days, 2),
            'Hours/Day': 16,
            'Moving MPH': round(self.total_distance / ultra_days / 14, 2),  # 14 hours moving
            'Difficulty': 'Very Hard'
        })
        
        # Fast thru-hike (90 days)
        strategies.append({
            'Strategy': 'Fast Thru-hike',
            'Total Days': self.FAST_THRU_HIKE_DAYS,
            'Miles/Day': round(self.total_distance / self.FAST_THRU_HIKE_DAYS, 2),
            'Hours/Day': 12,
            'Moving MPH': round(self.total_distance / self.FAST_THRU_HIKE_DAYS / 10, 2),
            'Difficulty': 'Hard'
        })
        
        # Typical thru-hike (150 days)
        strategies.append({
            'Strategy': 'Typical Thru-hike',
            'Total Days': self.TYPICAL_THRU_HIKE_DAYS,
            'Miles/Day': round(self.total_distance / self.TYPICAL_THRU_HIKE_DAYS, 2),
            'Hours/Day': 10,
            'Moving MPH': round(self.total_distance / self.TYPICAL_THRU_HIKE_DAYS / 8, 2),
            'Difficulty': 'Moderate'
        })
        
        # Leisurely thru-hike (180 days / 6 months)
        leisurely_days = 180
        strategies.append({
            'Strategy': 'Leisurely Thru-hike',
            'Total Days': leisurely_days,
            'Miles/Day': round(self.total_distance / leisurely_days, 2),
            'Hours/Day': 8,
            'Moving MPH': round(self.total_distance / leisurely_days / 6, 2),
            'Difficulty': 'Easy'
        })
        
        return pd.DataFrame(strategies)
    
    def calculate_required_pace_by_terrain(self) -> pd.DataFrame:
        """
        Calculate what pace is needed for FKT on different terrain types.
        
        Returns:
            DataFrame with pace requirements by terrain
        """
        if 'difficulty' not in self.df.columns or self.analyzer is None:
            return pd.DataFrame()
        
        fkt_metrics = self.get_fkt_metrics()
        target_mph = fkt_metrics['pace_metrics']['avg_mph_moving']
        
        terrain_pace = []
        
        for difficulty in ['Easy', 'Moderate', 'Difficult', 'Very Difficult', 'Extreme']:
            terrain_data = self.df[self.df['difficulty'] == difficulty]
            
            if len(terrain_data) > 0:
                miles = terrain_data['segment_distance'].sum()
                avg_grade = abs(terrain_data['grade_percent']).mean()
                
                # Estimate pace adjustment based on grade
                # Typically, each 1% grade reduces speed by ~5%
                pace_multiplier = 1.0 - (avg_grade * 0.05)
                required_flat_pace = target_mph / max(pace_multiplier, 0.3)
                
                time_hours = miles / target_mph
                
                terrain_pace.append({
                    'Terrain': difficulty,
                    'Miles': round(miles, 1),
                    '% of Trail': round(miles / self.total_distance * 100, 1),
                    'Avg Grade %': round(avg_grade, 2),
                    'Required Pace MPH': round(target_mph, 2),
                    'Equivalent Flat MPH': round(required_flat_pace, 2),
                    'Time Hours': round(time_hours, 1)
                })
        
        return pd.DataFrame(terrain_pace)
    
    def analyze_daylight_constrained_fkt(self, daylight_analyzer=None) -> Dict:
        """
        Analyze FKT with daylight-only hiking constraints.
        
        Args:
            daylight_analyzer: DaylightAnalyzer instance
            
        Returns:
            Dictionary with daylight-constrained analysis
        """
        if daylight_analyzer is None:
            # Import here to avoid circular dependency
            from daylight_analysis import DaylightAnalyzer
            daylight_analyzer = DaylightAnalyzer(self.df)
        
        # Get daylight-constrained FKT analysis
        daylight_fkt = daylight_analyzer.calculate_fkt_with_daylight(
            self.FKT_DAYS + self.FKT_HOURS / 24
        )
        
        # Calculate what duration is needed for daylight-only at reasonable pace
        from datetime import datetime
        spring_start = datetime(2024, 3, 15)
        
        # Try different paces
        pace_scenarios = []
        for pace in [2.5, 3.0, 3.5, 4.0]:
            duration = daylight_analyzer.calculate_daylight_based_duration(
                pace, spring_start
            )
            pace_scenarios.append(duration)
        
        return {
            'fkt_daylight_analysis': daylight_fkt,
            'daylight_duration_scenarios': pace_scenarios
        }
    
    def print_comprehensive_report(self, include_daylight: bool = False, daylight_analyzer=None):
        """
        Print a comprehensive FKT analysis report.
        
        Args:
            include_daylight: Whether to include daylight analysis
            daylight_analyzer: DaylightAnalyzer instance (required if include_daylight=True)
        """
        print("=" * 80)
        print("APPALACHIAN TRAIL FASTEST KNOWN TIME (FKT) ANALYSIS")
        print("=" * 80)
        
        fkt_metrics = self.get_fkt_metrics()
        
        print(f"\n🏆 RECORD: {fkt_metrics['fkt_record']['formatted']}")
        print(f"    ({fkt_metrics['fkt_record']['total_hours']:.1f} total hours)")
        
        print(f"\n📊 PACE METRICS:")
        pace = fkt_metrics['pace_metrics']
        print(f"    • Miles per day: {pace['miles_per_day']:.1f}")
        print(f"    • Overall average pace: {pace['avg_mph_overall']:.2f} mph")
        print(f"    • Moving pace (est): {pace['avg_mph_moving']:.2f} mph")
        print(f"    • Minutes per mile: {pace['minutes_per_mile']:.1f}")
        print(f"    • Hiking hours per day: {pace['hiking_hours_per_day']:.1f} hours")
        print(f"    • Total hiking hours: {pace['total_hiking_hours']:.1f} hours")
        
        print(f"\n⛰️  ELEVATION CHALLENGE:")
        elev = fkt_metrics['elevation_metrics']
        print(f"    • Total elevation gain: {elev['total_gain_ft']:,.0f} feet")
        print(f"    • Elevation gain per hour: {elev['gain_per_hour_ft']:,.0f} feet")
        print(f"    • Elevation gain per day: {elev['gain_per_day_ft']:,.0f} feet")
        
        print(f"\n🔥 COMPARISON TO TYPICAL THRU-HIKES:")
        comp = fkt_metrics['comparison']
        print(f"    • {comp['vs_typical_thru_hike']:.1f}x faster than typical thru-hike (150 days)")
        print(f"    • {comp['vs_fast_thru_hike']:.1f}x faster than fast thru-hike (90 days)")
        
        print(f"\n📅 DAILY BREAKDOWN:")
        daily_segments = self.calculate_daily_segments()
        toughest_days = self.identify_toughest_days(daily_segments, n=5)
        
        print(f"\n    Top 5 Toughest Days:")
        for _, day in toughest_days.iterrows():
            print(f"      Day {int(day['Day'])}: {day['Starting State']} → {day['Ending State']}")
            print(f"        Miles {day['Start Mile']:.1f}-{day['End Mile']:.1f} | "
                  f"{day['Miles']:.1f} mi | +{day['Elevation Gain']:.0f} ft gain")
        
        print(f"\n🎯 PACING STRATEGY COMPARISON:")
        strategies = self.compare_pacing_strategies()
        print("\n", strategies.to_string(index=False))
        
        print(f"\n⚡ REQUIRED PACE BY TERRAIN:")
        terrain_pace = self.calculate_required_pace_by_terrain()
        if len(terrain_pace) > 0:
            print("\n", terrain_pace.to_string(index=False))
        
        print("\n" + "=" * 80)
        print("This FKT represents one of the most impressive athletic achievements")
        print("in ultra-endurance sports, requiring exceptional fitness, mental")
        print("toughness, and strategic planning.")
        print("=" * 80)
        
        # Add daylight analysis if requested
        if include_daylight and daylight_analyzer:
            print("\n" + "=" * 80)
            print("DAYLIGHT-ONLY HIKING ANALYSIS")
            print("=" * 80)
            
            daylight_analysis = self.analyze_daylight_constrained_fkt(daylight_analyzer)
            
            print("\n🌞 FKT PACE WITH DAYLIGHT CONSTRAINTS:")
            print("\n  The current FKT record was set with near 24/7 hiking.")
            print("  Here's what the same pace would require with daylight-only:")
            
            for scenario in daylight_analysis['fkt_daylight_analysis']['scenarios']:
                print(f"\n    {scenario['scenario']}:")
                print(f"      Average daylight: {scenario['avg_daylight']} hours/day")
                print(f"      Required pace (using all daylight): {scenario['required_pace_mph']} mph")
                print(f"      Realistic pace (75% hiking): {scenario['realistic_pace_mph']} mph")
                print(f"      Feasibility: {scenario['feasible']}")
            
            print("\n  💡 For comparison, ultramarathon runners sustain 6-8 mph.")
            print("     The FKT with daylight-only would require running pace!")
            
            print("\n📊 REALISTIC DAYLIGHT-ONLY DURATIONS:")
            print("\n  Starting mid-March (optimal for NOBO):")
            
            for scenario in daylight_analysis['daylight_duration_scenarios']:
                pace = scenario['target_pace_mph']
                days = scenario['total_days']
                months = scenario['total_months']
                mpd = scenario['miles_per_day']
                
                # Add difficulty label
                if days < 60:
                    difficulty = "Very Fast"
                elif days < 90:
                    difficulty = "Fast"
                elif days < 150:
                    difficulty = "Moderate"
                else:
                    difficulty = "Leisurely"
                
                print(f"\n    {pace} mph pace ({difficulty}):")
                print(f"      {mpd:.1f} miles/day over {days:.0f} days ({months:.1f} months)")
                print(f"      Finish: {scenario['end_date']}")
            
            print("\n  ✨ Most thru-hikers maintain 2.0-3.0 mph with daylight-only hiking.")
            print("=" * 80)


if __name__ == '__main__':
    import sys
    import os
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    from data_loader import load_or_generate_data
    from analysis import TrailAnalyzer
    
    # Load data
    data_path = os.path.join(project_root, 'data', 'trail_data.csv')
    df, _ = load_or_generate_data(data_path)
    
    # Create analyzers
    trail_analyzer = TrailAnalyzer(df)
    fkt_analyzer = FKTAnalyzer(df, trail_analyzer)
    
    # Print comprehensive report
    fkt_analyzer.print_comprehensive_report()

