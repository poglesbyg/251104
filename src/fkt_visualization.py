"""
Visualization module for FKT analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Optional
import os


class FKTVisualizer:
    """Create visualizations for FKT analysis."""
    
    def __init__(self, fkt_analyzer, output_dir: str = '../outputs'):
        """
        Initialize FKT visualizer.
        
        Args:
            fkt_analyzer: FKTAnalyzer instance
            output_dir: Directory to save visualizations
        """
        self.fkt = fkt_analyzer
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_pace_comparison(self, save: bool = True, filename: str = 'fkt_pace_comparison.png') -> Optional[str]:
        """
        Compare FKT pace with other pacing strategies.
        
        Args:
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        strategies = self.fkt.compare_pacing_strategies()
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Miles per day comparison
        ax1 = axes[0, 0]
        colors = ['#D32F2F', '#FF9800', '#FFC107', '#4CAF50', '#2196F3']
        bars = ax1.barh(strategies['Strategy'], strategies['Miles/Day'], color=colors)
        ax1.set_xlabel('Miles per Day', fontweight='bold')
        ax1.set_title('Daily Mileage Comparison', fontweight='bold', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, strategies['Miles/Day'])):
            ax1.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val:.1f}', 
                    va='center', fontweight='bold')
        
        # 2. Total days comparison
        ax2 = axes[0, 1]
        bars = ax2.barh(strategies['Strategy'], strategies['Total Days'], color=colors)
        ax2.set_xlabel('Total Days', fontweight='bold')
        ax2.set_title('Time to Completion', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='x')
        ax2.invert_xaxis()  # Faster times on the right
        
        for i, (bar, val) in enumerate(zip(bars, strategies['Total Days'])):
            ax2.text(val - 3, bar.get_y() + bar.get_height()/2, f'{val:.1f}', 
                    va='center', ha='right', fontweight='bold')
        
        # 3. Moving speed comparison
        ax3 = axes[1, 0]
        bars = ax3.barh(strategies['Strategy'], strategies['Moving MPH'], color=colors)
        ax3.set_xlabel('Moving Speed (MPH)', fontweight='bold')
        ax3.set_title('Average Moving Pace', fontweight='bold', fontsize=12)
        ax3.grid(True, alpha=0.3, axis='x')
        
        for i, (bar, val) in enumerate(zip(bars, strategies['Moving MPH'])):
            ax3.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}', 
                    va='center', fontweight='bold')
        
        # 4. Hours per day comparison
        ax4 = axes[1, 1]
        bars = ax4.barh(strategies['Strategy'], strategies['Hours/Day'], color=colors)
        ax4.set_xlabel('Hours per Day', fontweight='bold')
        ax4.set_title('Daily Time Investment', fontweight='bold', fontsize=12)
        ax4.grid(True, alpha=0.3, axis='x')
        
        for i, (bar, val) in enumerate(zip(bars, strategies['Hours/Day'])):
            ax4.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}', 
                    va='center', fontweight='bold')
        
        plt.suptitle('FKT vs Traditional Thru-Hiking Strategies', 
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
    
    def plot_daily_elevation_profile(self, save: bool = True, filename: str = 'fkt_daily_profile.png') -> Optional[str]:
        """
        Show daily elevation challenge for FKT attempt.
        
        Args:
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        daily_segments = self.fkt.calculate_daily_segments()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
        
        # Top plot: Elevation gain per day
        colors = plt.cm.RdYlGn_r(daily_segments['Elevation Gain'] / daily_segments['Elevation Gain'].max())
        bars1 = ax1.bar(daily_segments['Day'], daily_segments['Elevation Gain'], color=colors, edgecolor='black', linewidth=0.5)
        ax1.set_xlabel('Day', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Elevation Gain (feet)', fontweight='bold', fontsize=12)
        ax1.set_title('Daily Elevation Gain Challenge', fontweight='bold', fontsize=14)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.axhline(daily_segments['Elevation Gain'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Average: {daily_segments["Elevation Gain"].mean():.0f} ft')
        ax1.legend()
        
        # Highlight toughest days
        toughest = daily_segments.nlargest(5, 'Elevation Gain')
        for _, day in toughest.iterrows():
            ax1.annotate(f'Day {int(day["Day"])}\n+{day["Elevation Gain"]:.0f} ft', 
                        xy=(day['Day'], day['Elevation Gain']),
                        xytext=(0, 10), textcoords='offset points',
                        ha='center', fontsize=8, 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Bottom plot: Elevation range per day
        ax2.fill_between(daily_segments['Day'], 
                        daily_segments['Min Elevation'], 
                        daily_segments['Max Elevation'],
                        alpha=0.6, color='#4CAF50', edgecolor='black', linewidth=0.5)
        ax2.plot(daily_segments['Day'], daily_segments['Avg Elevation'], 
                color='#1976D2', linewidth=2, label='Average Elevation', marker='o', markersize=3)
        ax2.set_xlabel('Day', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Elevation (feet)', fontweight='bold', fontsize=12)
        ax2.set_title('Daily Elevation Range', fontweight='bold', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def plot_required_pace_by_terrain(self, save: bool = True, filename: str = 'fkt_terrain_pace.png') -> Optional[str]:
        """
        Visualize required pace by terrain difficulty.
        
        Args:
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        terrain_pace = self.fkt.calculate_required_pace_by_terrain()
        
        if len(terrain_pace) == 0:
            print("Cannot generate terrain pace visualization - difficulty data not available")
            return None
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # 1. Miles by terrain
        ax1 = axes[0]
        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']
        ax1.pie(terrain_pace['Miles'], labels=terrain_pace['Terrain'], autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax1.set_title('Trail Distribution\nby Terrain Difficulty', fontweight='bold', fontsize=12)
        
        # 2. Required pace
        ax2 = axes[1]
        bars = ax2.bar(range(len(terrain_pace)), terrain_pace['Equivalent Flat MPH'], 
                      color=colors, edgecolor='black', linewidth=1)
        ax2.set_xticks(range(len(terrain_pace)))
        ax2.set_xticklabels(terrain_pace['Terrain'], rotation=45, ha='right')
        ax2.set_ylabel('Equivalent Flat Pace (MPH)', fontweight='bold')
        ax2.set_title('Required Flat-Equivalent Pace\nby Terrain Type', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, val in zip(bars, terrain_pace['Equivalent Flat MPH']):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{val:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 3. Time spent on each terrain
        ax3 = axes[2]
        bars = ax3.barh(terrain_pace['Terrain'], terrain_pace['Time Hours'], color=colors, edgecolor='black')
        ax3.set_xlabel('Hours', fontweight='bold')
        ax3.set_title('Time Spent on Each\nTerrain Type', fontweight='bold', fontsize=12)
        ax3.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for bar, val in zip(bars, terrain_pace['Time Hours']):
            ax3.text(val + 5, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}h', va='center', fontweight='bold', fontsize=9)
        
        plt.suptitle('FKT Pace Requirements by Terrain', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def create_fkt_dashboard(self):
        """Create all FKT visualizations."""
        print("Generating FKT visualizations...")
        
        print("  - Pace comparison...")
        self.plot_pace_comparison()
        
        print("  - Daily elevation profile...")
        self.plot_daily_elevation_profile()
        
        print("  - Terrain pace requirements...")
        self.plot_required_pace_by_terrain()
        
        print(f"\nFKT visualizations saved to: {self.output_dir}")


if __name__ == '__main__':
    import sys
    import os
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    from data_loader import load_or_generate_data
    from analysis import TrailAnalyzer
    from fkt_analysis import FKTAnalyzer
    
    # Load data
    data_path = os.path.join(project_root, 'data', 'trail_data.csv')
    df, _ = load_or_generate_data(data_path)
    
    # Create analyzers
    trail_analyzer = TrailAnalyzer(df)
    fkt_analyzer = FKTAnalyzer(df, trail_analyzer)
    
    # Create visualizations
    output_dir = os.path.join(project_root, 'outputs')
    fkt_viz = FKTVisualizer(fkt_analyzer, output_dir)
    fkt_viz.create_fkt_dashboard()

