"""
Daylight hours analysis for Appalachian Trail hiking.
Calculates available daylight based on location and time of year.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple
import math


class DaylightAnalyzer:
    """Calculate daylight hours for trail locations and dates."""
    
    # Typical thru-hike start dates
    NOBO_START_DATE = datetime(2024, 3, 15)  # Northbound: mid-March
    SOBO_START_DATE = datetime(2024, 6, 15)  # Southbound: mid-June
    
    def __init__(self, trail_data: pd.DataFrame):
        """
        Initialize daylight analyzer.
        
        Args:
            trail_data: DataFrame with trail data including latitude
        """
        self.df = trail_data.copy()
        self.total_distance = self.df['distance_miles'].max()
    
    @staticmethod
    def calculate_daylight_hours(latitude: float, date: datetime) -> float:
        """
        Calculate daylight hours for a given latitude and date.
        Uses simplified sunrise equation.
        
        Args:
            latitude: Latitude in degrees
            date: Date to calculate for
            
        Returns:
            Hours of daylight
        """
        # Day of year
        day_of_year = date.timetuple().tm_yday
        
        # Solar declination angle (degrees)
        declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))
        
        # Hour angle (radians)
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        
        # Handle polar day/night
        cos_hour_angle = -math.tan(lat_rad) * math.tan(dec_rad)
        
        if cos_hour_angle > 1:
            # Polar night
            return 0.0
        elif cos_hour_angle < -1:
            # Polar day
            return 24.0
        
        # Hour angle in degrees
        hour_angle = math.degrees(math.acos(cos_hour_angle))
        
        # Daylight hours
        daylight = (2 * hour_angle) / 15
        
        # Add civil twilight (about 30 minutes morning and evening)
        # Most hikers can use twilight hours
        daylight += 1.0
        
        return max(0, min(24, daylight))
    
    def calculate_daylight_by_mile(self, start_date: datetime, 
                                   miles_per_day: float) -> pd.DataFrame:
        """
        Calculate daylight hours for each point along the trail.
        
        Args:
            start_date: Start date of hike
            miles_per_day: Average miles per day
            
        Returns:
            DataFrame with daylight information
        """
        daylight_data = []
        
        for _, row in self.df.iterrows():
            # Calculate days from start
            days_elapsed = row['distance_miles'] / miles_per_day
            current_date = start_date + timedelta(days=days_elapsed)
            
            # Calculate daylight hours
            daylight = self.calculate_daylight_hours(row['latitude'], current_date)
            
            daylight_data.append({
                'distance_miles': row['distance_miles'],
                'latitude': row['latitude'],
                'state': row['state'],
                'date': current_date,
                'day_of_year': current_date.timetuple().tm_yday,
                'daylight_hours': daylight
            })
        
        return pd.DataFrame(daylight_data)
    
    def analyze_daylight_constrained_pace(self, 
                                         start_date: datetime,
                                         direction: str = 'NOBO',
                                         desired_days: int = None) -> Dict:
        """
        Analyze what pace is achievable hiking only during daylight.
        
        Args:
            start_date: Start date
            direction: 'NOBO' (northbound) or 'SOBO' (southbound)
            desired_days: Target completion days (if None, calculates optimal)
            
        Returns:
            Dictionary with daylight-constrained analysis
        """
        if desired_days is None:
            # Estimate based on typical thru-hike
            desired_days = 150
        
        miles_per_day = self.total_distance / desired_days
        
        # Calculate daylight availability
        daylight_df = self.calculate_daylight_by_mile(start_date, miles_per_day)
        
        # Average daylight hours available
        avg_daylight = daylight_df['daylight_hours'].mean()
        min_daylight = daylight_df['daylight_hours'].min()
        max_daylight = daylight_df['daylight_hours'].max()
        
        # Calculate required hiking hours per day
        # Assuming you use all daylight hours for hiking (unrealistic but upper bound)
        max_miles_per_day = miles_per_day
        required_pace_mph = max_miles_per_day / avg_daylight
        
        # More realistic: account for breaks, setup/takedown camp
        actual_hiking_hours = avg_daylight * 0.75  # 75% of daylight for actual hiking
        realistic_pace_mph = max_miles_per_day / actual_hiking_hours
        
        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'direction': direction,
            'total_days': desired_days,
            'miles_per_day': round(miles_per_day, 2),
            'avg_daylight_hours': round(avg_daylight, 2),
            'min_daylight_hours': round(min_daylight, 2),
            'max_daylight_hours': round(max_daylight, 2),
            'required_pace_mph': round(required_pace_mph, 2),
            'actual_hiking_hours': round(actual_hiking_hours, 2),
            'realistic_pace_mph': round(realistic_pace_mph, 2),
            'end_date': (start_date + timedelta(days=desired_days)).strftime('%Y-%m-%d')
        }
    
    def calculate_fkt_with_daylight(self, fkt_days: float = 40.75) -> Dict:
        """
        Calculate what FKT pace would require with daylight-only hiking.
        
        Args:
            fkt_days: FKT duration in days
            
        Returns:
            Dictionary with daylight-constrained FKT analysis
        """
        miles_per_day = self.total_distance / fkt_days
        
        # Try different start dates
        scenarios = []
        
        # Spring start (optimal for NOBO)
        spring_start = datetime(2024, 4, 1)
        spring_daylight = self.calculate_daylight_by_mile(spring_start, miles_per_day)
        
        # Summer start (longest days)
        summer_start = datetime(2024, 6, 15)
        summer_daylight = self.calculate_daylight_by_mile(summer_start, miles_per_day)
        
        for name, start_date, daylight_df in [
            ('Spring Start (Apr 1)', spring_start, spring_daylight),
            ('Summer Start (Jun 15)', summer_start, summer_daylight)
        ]:
            avg_daylight = daylight_df['daylight_hours'].mean()
            min_daylight = daylight_df['daylight_hours'].min()
            
            # Calculate required pace
            required_pace = miles_per_day / avg_daylight
            
            # Calculate with realistic hiking time (75% of daylight)
            realistic_hiking_hours = avg_daylight * 0.75
            realistic_pace = miles_per_day / realistic_hiking_hours
            
            scenarios.append({
                'scenario': name,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'avg_daylight': round(avg_daylight, 2),
                'min_daylight': round(min_daylight, 2),
                'miles_per_day': round(miles_per_day, 2),
                'required_pace_mph': round(required_pace, 2),
                'realistic_hiking_hours': round(realistic_hiking_hours, 2),
                'realistic_pace_mph': round(realistic_pace, 2),
                'feasible': 'Yes' if realistic_pace < 3.5 else 'Very Challenging'
            })
        
        return {
            'fkt_days': fkt_days,
            'scenarios': scenarios
        }
    
    def compare_hiking_windows(self) -> pd.DataFrame:
        """
        Compare different start dates and their daylight availability.
        
        Returns:
            DataFrame comparing different start months
        """
        comparisons = []
        
        months = [
            ('March', datetime(2024, 3, 15)),
            ('April', datetime(2024, 4, 15)),
            ('May', datetime(2024, 5, 15)),
            ('June', datetime(2024, 6, 15)),
            ('July', datetime(2024, 7, 15)),
            ('August', datetime(2024, 8, 15))
        ]
        
        for month_name, start_date in months:
            # Calculate for typical thru-hike (150 days)
            analysis = self.analyze_daylight_constrained_pace(
                start_date, 
                'NOBO', 
                desired_days=150
            )
            
            comparisons.append({
                'Start Month': month_name,
                'Start Date': start_date.strftime('%b %d'),
                'End Date': datetime.strptime(analysis['end_date'], '%Y-%m-%d').strftime('%b %d'),
                'Avg Daylight': analysis['avg_daylight_hours'],
                'Min Daylight': analysis['min_daylight_hours'],
                'Max Daylight': analysis['max_daylight_hours'],
                'Hiking Hours/Day': analysis['actual_hiking_hours'],
                'Required Pace': analysis['realistic_pace_mph']
            })
        
        return pd.DataFrame(comparisons)
    
    def calculate_daylight_based_duration(self, 
                                         target_pace_mph: float,
                                         start_date: datetime,
                                         hiking_hours_per_day: float = None) -> Dict:
        """
        Calculate how long it takes at a given pace with daylight constraints.
        
        Args:
            target_pace_mph: Desired hiking pace in mph
            start_date: Start date
            hiking_hours_per_day: Override daylight calculation with fixed hours
            
        Returns:
            Dictionary with duration estimate
        """
        if hiking_hours_per_day is None:
            # Calculate based on daylight
            # Use iterative approach
            estimated_days = 150
            for _ in range(10):  # Iterate to converge
                miles_per_day = self.total_distance / estimated_days
                daylight_df = self.calculate_daylight_by_mile(start_date, miles_per_day)
                avg_daylight = daylight_df['daylight_hours'].mean()
                hiking_hours = avg_daylight * 0.75
                miles_per_day = target_pace_mph * hiking_hours
                estimated_days = self.total_distance / miles_per_day
        else:
            hiking_hours = hiking_hours_per_day
            miles_per_day = target_pace_mph * hiking_hours
            estimated_days = self.total_distance / miles_per_day
        
        return {
            'target_pace_mph': target_pace_mph,
            'hiking_hours_per_day': round(hiking_hours, 2),
            'miles_per_day': round(miles_per_day, 2),
            'total_days': round(estimated_days, 1),
            'total_months': round(estimated_days / 30, 1),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': (start_date + timedelta(days=estimated_days)).strftime('%Y-%m-%d')
        }


if __name__ == '__main__':
    import sys
    import os
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    from data_loader import load_or_generate_data
    
    # Load data
    data_path = os.path.join(project_root, 'data', 'trail_data.csv')
    df, _ = load_or_generate_data(data_path)
    
    # Create analyzer
    daylight_analyzer = DaylightAnalyzer(df)
    
    print("=" * 80)
    print("APPALACHIAN TRAIL DAYLIGHT HOURS ANALYSIS")
    print("=" * 80)
    
    # Compare start months
    print("\n📅 START MONTH COMPARISON (150-day thru-hike)\n")
    comparison = daylight_analyzer.compare_hiking_windows()
    print(comparison.to_string(index=False))
    
    # FKT with daylight
    print("\n\n🏆 FKT PACE WITH DAYLIGHT-ONLY HIKING\n")
    fkt_daylight = daylight_analyzer.calculate_fkt_with_daylight(40.75)
    print(f"FKT Record: {fkt_daylight['fkt_days']:.1f} days")
    print("\nScenarios:")
    for scenario in fkt_daylight['scenarios']:
        print(f"\n  {scenario['scenario']}:")
        print(f"    Average daylight: {scenario['avg_daylight']} hours")
        print(f"    Miles per day: {scenario['miles_per_day']}")
        print(f"    Required pace: {scenario['required_pace_mph']} mph")
        print(f"    With breaks (75% hiking): {scenario['realistic_pace_mph']} mph")
        print(f"    Feasible: {scenario['feasible']}")
    
    # Calculate realistic daylight-only durations
    print("\n\n⏱️  DAYLIGHT-ONLY HIKING DURATIONS\n")
    
    paces = [2.0, 2.5, 3.0, 3.5]
    spring_start = datetime(2024, 3, 15)
    
    for pace in paces:
        result = daylight_analyzer.calculate_daylight_based_duration(pace, spring_start)
        print(f"  {pace} mph pace:")
        print(f"    {result['miles_per_day']:.1f} miles/day")
        print(f"    {result['total_days']:.0f} days ({result['total_months']:.1f} months)")
        print(f"    {result['start_date']} → {result['end_date']}")
        print()
