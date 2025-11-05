"""
Visualization module for daylight analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional
import os


class DaylightVisualizer:
    """Create visualizations for daylight analysis."""
    
    def __init__(self, daylight_analyzer, output_dir: str = '../outputs'):
        """
        Initialize daylight visualizer.
        
        Args:
            daylight_analyzer: DaylightAnalyzer instance
            output_dir: Directory to save visualizations
        """
        self.daylight = daylight_analyzer
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_daylight_by_season(self, save: bool = True, 
                               filename: str = 'daylight_seasonal_comparison.png') -> Optional[str]:
        """
        Compare daylight hours for different start dates.
        
        Args:
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Get comparison data
        comparison = self.daylight.compare_hiking_windows()
        
        # Plot 1: Daylight hours by start month
        x = range(len(comparison))
        width = 0.25
        
        ax1.bar([i - width for i in x], comparison['Avg Daylight'], width, 
               label='Average', color='#FFC107', edgecolor='black')
        ax1.bar(x, comparison['Min Daylight'], width,
               label='Minimum', color='#FF9800', edgecolor='black')
        ax1.bar([i + width for i in x], comparison['Max Daylight'], width,
               label='Maximum', color='#4CAF50', edgecolor='black')
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(comparison['Start Month'], rotation=45, ha='right')
        ax1.set_ylabel('Daylight Hours', fontweight='bold', fontsize=12)
        ax1.set_title('Daylight Availability by Start Month\n(150-day thru-hike)',
                     fontweight='bold', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on average bars
        for i, val in enumerate(comparison['Avg Daylight']):
            ax1.text(i - width, val + 0.2, f'{val:.1f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Plot 2: Required pace by start month
        ax2.plot(x, comparison['Required Pace'], marker='o', linewidth=2.5,
                markersize=10, color='#D32F2F', label='Required Pace')
        ax2.fill_between(x, comparison['Required Pace'], alpha=0.3, color='#D32F2F')
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(comparison['Start Month'], rotation=45, ha='right')
        ax2.set_ylabel('Required Pace (MPH)', fontweight='bold', fontsize=12)
        ax2.set_title('Required Hiking Pace by Start Month\n(to complete in 150 days)',
                     fontweight='bold', fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels
        for i, val in enumerate(comparison['Required Pace']):
            ax2.text(i, val + 0.02, f'{val:.2f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Highlight optimal window
        ax2.axhspan(0, 1.5, alpha=0.1, color='green', label='Easy Pace')
        ax2.axhspan(1.5, 2.0, alpha=0.1, color='yellow', label='Moderate Pace')
        ax2.axhspan(2.0, 3.0, alpha=0.1, color='red', label='Challenging Pace')
        
        plt.suptitle('Impact of Start Date on Daylight-Only Thru-Hiking',
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def plot_24_7_vs_daylight(self, save: bool = True,
                             filename: str = 'hiking_strategy_comparison.png') -> Optional[str]:
        """
        Compare 24/7 hiking vs daylight-only strategies.
        
        Args:
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Data for comparison
        strategies = [
            {'name': 'FKT (24/7)', 'days': 41, 'hours_per_day': 20.4, 'mph': 2.39, 'sleep': 4},
            {'name': 'Daylight Fast', 'days': 61, 'hours_per_day': 11.0, 'mph': 3.0, 'sleep': 8},
            {'name': 'Daylight Moderate', 'days': 89, 'hours_per_day': 11.0, 'mph': 2.0, 'sleep': 8},
            {'name': 'Typical Thru-hike', 'days': 150, 'hours_per_day': 8.0, 'mph': 1.63, 'sleep': 8}
        ]
        
        names = [s['name'] for s in strategies]
        days = [s['days'] for s in strategies]
        hours = [s['hours_per_day'] for s in strategies]
        paces = [s['mph'] for s in strategies]
        sleep = [s['sleep'] for s in strategies]
        
        colors = ['#D32F2F', '#FF9800', '#4CAF50', '#2196F3']
        
        # 1. Total days comparison
        ax1 = axes[0, 0]
        bars = ax1.barh(names, days, color=colors, edgecolor='black', linewidth=1.5)
        ax1.set_xlabel('Total Days', fontweight='bold')
        ax1.set_title('Duration to Complete Trail', fontweight='bold', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.invert_xaxis()
        
        for bar, val in zip(bars, days):
            ax1.text(val - 3, bar.get_y() + bar.get_height()/2, f'{val}d',
                    va='center', ha='right', fontweight='bold', fontsize=10)
        
        # 2. Hiking hours per day
        ax2 = axes[0, 1]
        bars = ax2.barh(names, hours, color=colors, edgecolor='black', linewidth=1.5)
        ax2.set_xlabel('Hiking Hours/Day', fontweight='bold')
        ax2.set_title('Daily Hiking Time', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, hours):
            ax2.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.1f}h',
                    va='center', fontweight='bold', fontsize=10)
        
        # 3. Required pace
        ax3 = axes[1, 0]
        bars = ax3.barh(names, paces, color=colors, edgecolor='black', linewidth=1.5)
        ax3.set_xlabel('Required Pace (MPH)', fontweight='bold')
        ax3.set_title('Average Hiking Pace Needed', fontweight='bold', fontsize=12)
        ax3.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, paces):
            ax3.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                    va='center', fontweight='bold', fontsize=10)
        
        # 4. Sleep hours
        ax4 = axes[1, 1]
        bars = ax4.barh(names, sleep, color=colors, edgecolor='black', linewidth=1.5)
        ax4.set_xlabel('Sleep Hours/Day', fontweight='bold')
        ax4.set_title('Daily Rest Time', fontweight='bold', fontsize=12)
        ax4.grid(True, alpha=0.3, axis='x')
        
        for bar, val in zip(bars, sleep):
            ax4.text(val + 0.15, bar.get_y() + bar.get_height()/2, f'{val}h',
                    va='center', fontweight='bold', fontsize=10)
        
        plt.suptitle('24/7 Hiking vs Daylight-Only Strategies',
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def plot_daylight_along_trail(self, start_date: datetime, miles_per_day: float,
                                  save: bool = True,
                                  filename: str = 'daylight_along_trail.png') -> Optional[str]:
        """
        Show daylight hours along the trail over time.
        
        Args:
            start_date: Start date of hike
            miles_per_day: Average miles per day
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        # Calculate daylight by mile
        daylight_df = self.daylight.calculate_daylight_by_mile(start_date, miles_per_day)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
        
        # Plot 1: Daylight hours vs distance
        ax1.fill_between(daylight_df['distance_miles'], daylight_df['daylight_hours'],
                        alpha=0.6, color='#FFC107', edgecolor='black', linewidth=1)
        ax1.plot(daylight_df['distance_miles'], daylight_df['daylight_hours'],
                color='#FF6F00', linewidth=2, label='Daylight Hours')
        
        # Add horizontal lines for reference
        ax1.axhline(12, color='gray', linestyle='--', alpha=0.5, label='12 hours')
        ax1.axhline(14, color='green', linestyle='--', alpha=0.5, label='14 hours')
        
        ax1.set_xlabel('Distance (miles)', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Daylight Hours', fontweight='bold', fontsize=12)
        ax1.set_title(f'Daylight Hours Along Trail\nStarting {start_date.strftime("%B %d, %Y")} at {miles_per_day:.1f} mi/day',
                     fontweight='bold', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Highlight state boundaries
        states = daylight_df['state'].unique()
        for state in states:
            state_data = daylight_df[daylight_df['state'] == state]
            start_mile = state_data['distance_miles'].min()
            if start_mile > 0:
                ax1.axvline(start_mile, color='gray', linestyle=':', alpha=0.3)
        
        # Plot 2: Date progression
        ax2.plot(daylight_df['distance_miles'], daylight_df['day_of_year'],
                linewidth=2.5, color='#2196F3', marker='o', markersize=1)
        
        ax2.set_xlabel('Distance (miles)', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Day of Year', fontweight='bold', fontsize=12)
        ax2.set_title('Calendar Progression Along Trail', fontweight='bold', fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        # Add month labels
        month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax2.set_yticks(month_days)
        ax2.set_yticklabels(month_names)
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def create_daylight_dashboard(self):
        """Create all daylight visualizations."""
        print("Generating daylight visualizations...")
        
        print("  - Seasonal comparison...")
        self.plot_daylight_by_season()
        
        print("  - 24/7 vs daylight comparison...")
        self.plot_24_7_vs_daylight()
        
        print("  - Daylight along trail...")
        spring_start = datetime(2024, 3, 15)
        self.plot_daylight_along_trail(spring_start, 13.0)  # Typical thru-hike pace
        
        print(f"\nDaylight visualizations saved to: {self.output_dir}")


if __name__ == '__main__':
    import sys
    import os
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    from data_loader import load_or_generate_data
    from daylight_analysis import DaylightAnalyzer
    
    # Load data
    data_path = os.path.join(project_root, 'data', 'trail_data.csv')
    df, _ = load_or_generate_data(data_path)
    
    # Create analyzer and visualizer
    daylight_analyzer = DaylightAnalyzer(df)
    output_dir = os.path.join(project_root, 'outputs')
    daylight_viz = DaylightVisualizer(daylight_analyzer, output_dir)
    
    # Create visualizations
    daylight_viz.create_daylight_dashboard()
