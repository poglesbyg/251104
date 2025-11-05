"""
Visualization module for Appalachian Trail data.
Create beautiful and informative visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Tuple
import os


# Set style for matplotlib
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10


class TrailVisualizer:
    """Create visualizations for trail data."""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = '../outputs'):
        """
        Initialize visualizer with trail data.
        
        Args:
            df: DataFrame with trail data
            output_dir: Directory to save visualizations
        """
        self.df = df.copy()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_elevation_profile(self, 
                              highlight_states: bool = True,
                              save: bool = True,
                              filename: str = 'elevation_profile.png') -> Optional[str]:
        """
        Create elevation profile of the entire trail.
        
        Args:
            highlight_states: Whether to highlight state boundaries
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        fig, ax = plt.subplots(figsize=(16, 6))
        
        # Plot elevation
        ax.plot(self.df['distance_miles'], self.df['elevation_ft'], 
                linewidth=1.5, color='#2E7D32', alpha=0.8)
        
        # Fill under the curve
        ax.fill_between(self.df['distance_miles'], 0, self.df['elevation_ft'],
                        alpha=0.3, color='#4CAF50')
        
        # Highlight state boundaries if requested
        if highlight_states:
            states = self.df['state'].unique()
            colors = plt.cm.Set3(np.linspace(0, 1, len(states)))
            
            for i, state in enumerate(states):
                state_data = self.df[self.df['state'] == state]
                start_mile = state_data['distance_miles'].min()
                end_mile = state_data['distance_miles'].max()
                mid_mile = (start_mile + end_mile) / 2
                
                # Add vertical line at state boundary
                if i > 0:
                    ax.axvline(start_mile, color='gray', linestyle='--', 
                             alpha=0.5, linewidth=0.8)
                
                # Add state label
                ax.text(mid_mile, ax.get_ylim()[1] * 0.95, state,
                       ha='center', va='top', fontsize=8, 
                       bbox=dict(boxstyle='round', facecolor=colors[i], alpha=0.7))
        
        ax.set_xlabel('Distance (miles)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Elevation (feet)', fontsize=12, fontweight='bold')
        ax.set_title('Appalachian Trail Elevation Profile\nSpringer Mountain, GA to Mount Katahdin, ME',
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.df['distance_miles'].max())
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def plot_elevation_heatmap(self,
                              save: bool = True,
                              filename: str = 'elevation_heatmap.png') -> Optional[str]:
        """
        Create a heatmap showing elevation changes by state.
        
        Args:
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        # Prepare data
        state_elevations = []
        states = self.df['state'].unique()
        
        for state in states:
            state_data = self.df[self.df['state'] == state]
            state_elevations.append(state_data['elevation_ft'].values)
        
        # Find max length and pad
        max_len = max(len(x) for x in state_elevations)
        padded = np.array([
            np.pad(arr, (0, max_len - len(arr)), constant_values=np.nan)
            for arr in state_elevations
        ])
        
        fig, ax = plt.subplots(figsize=(16, 8))
        
        im = ax.imshow(padded, aspect='auto', cmap='terrain', 
                      interpolation='bilinear')
        
        ax.set_yticks(range(len(states)))
        ax.set_yticklabels(states)
        ax.set_xlabel('Trail Progress', fontsize=12, fontweight='bold')
        ax.set_title('Elevation Heatmap by State', fontsize=14, fontweight='bold', pad=20)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, label='Elevation (feet)')
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def plot_state_statistics(self,
                             state_stats: pd.DataFrame,
                             save: bool = True,
                             filename: str = 'state_statistics.png') -> Optional[str]:
        """
        Create visualization of state-by-state statistics.
        
        Args:
            state_stats: DataFrame with state statistics
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Miles by state
        ax1 = axes[0, 0]
        ax1.barh(state_stats['State'], state_stats['Miles'], color='#1976D2')
        ax1.set_xlabel('Miles', fontweight='bold')
        ax1.set_title('Trail Miles by State', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. Elevation range by state
        ax2 = axes[0, 1]
        ax2.barh(state_stats['State'], state_stats['Max Elevation'], 
                color='#4CAF50', alpha=0.7, label='Max Elevation')
        ax2.barh(state_stats['State'], state_stats['Min Elevation'], 
                color='#FFC107', alpha=0.7, label='Min Elevation')
        ax2.set_xlabel('Elevation (feet)', fontweight='bold')
        ax2.set_title('Elevation Range by State', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Total elevation gain by state
        ax3 = axes[1, 0]
        ax3.barh(state_stats['State'], state_stats['Total Gain'], color='#D32F2F')
        ax3.set_xlabel('Elevation Gain (feet)', fontweight='bold')
        ax3.set_title('Total Elevation Gain by State', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # 4. Average grade by state
        ax4 = axes[1, 1]
        colors = plt.cm.RdYlGn_r(state_stats['Avg Grade %'] / state_stats['Avg Grade %'].max())
        ax4.barh(state_stats['State'], state_stats['Avg Grade %'], color=colors)
        ax4.set_xlabel('Average Grade (%)', fontweight='bold')
        ax4.set_title('Average Trail Grade by State', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Appalachian Trail: State-by-State Analysis', 
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
    
    def create_interactive_elevation_profile(self,
                                            save: bool = True,
                                            filename: str = 'interactive_elevation.html') -> Optional[str]:
        """
        Create interactive elevation profile using Plotly.
        
        Args:
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        fig = go.Figure()
        
        # Add elevation trace
        fig.add_trace(go.Scatter(
            x=self.df['distance_miles'],
            y=self.df['elevation_ft'],
            mode='lines',
            name='Elevation',
            line=dict(color='#2E7D32', width=2),
            fill='tozeroy',
            fillcolor='rgba(76, 175, 80, 0.3)',
            hovertemplate='<b>Mile %{x:.1f}</b><br>' +
                         'Elevation: %{y:.0f} ft<br>' +
                         '<extra></extra>'
        ))
        
        # Add state markers
        for state in self.df['state'].unique():
            state_data = self.df[self.df['state'] == state]
            mid_idx = len(state_data) // 2
            mid_point = state_data.iloc[mid_idx]
            
            fig.add_annotation(
                x=mid_point['distance_miles'],
                y=mid_point['elevation_ft'] + 500,
                text=state,
                showarrow=False,
                font=dict(size=10),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='gray',
                borderwidth=1
            )
        
        fig.update_layout(
            title='Appalachian Trail Elevation Profile (Interactive)',
            xaxis_title='Distance (miles)',
            yaxis_title='Elevation (feet)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            font=dict(size=12)
        )
        
        if save:
            path = os.path.join(self.output_dir, filename)
            fig.write_html(path)
            return path
        else:
            fig.show()
            return None
    
    def create_interactive_map(self,
                              save: bool = True,
                              filename: str = 'trail_map.html') -> Optional[str]:
        """
        Create interactive map of the trail using Folium.
        
        Args:
            save: Whether to save the map
            filename: Filename for saved map
            
        Returns:
            Path to saved map if save=True
        """
        # Sample data for better performance (every 50th point)
        sampled_df = self.df.iloc[::50].copy()
        
        # Calculate center of trail
        center_lat = sampled_df['latitude'].mean()
        center_lon = sampled_df['longitude'].mean()
        
        # Create map
        trail_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer(
            tiles='https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.jpg',
            attr='Stadia Maps',
            name='Terrain'
        ).add_to(trail_map)
        folium.TileLayer('CartoDB Positron', name='Light').add_to(trail_map)
        
        # Color by elevation
        colors = plt.cm.RdYlGn(
            (sampled_df['elevation_ft'] - sampled_df['elevation_ft'].min()) /
            (sampled_df['elevation_ft'].max() - sampled_df['elevation_ft'].min())
        )
        
        # Create coordinates list
        coordinates = list(zip(sampled_df['latitude'], sampled_df['longitude']))
        
        # Add trail line
        folium.PolyLine(
            coordinates,
            color='green',
            weight=3,
            opacity=0.7,
            popup='Appalachian Trail'
        ).add_to(trail_map)
        
        # Add start and end markers
        start = sampled_df.iloc[0]
        end = sampled_df.iloc[-1]
        
        folium.Marker(
            [start['latitude'], start['longitude']],
            popup=f"<b>Start: Springer Mountain, GA</b><br>Elevation: {start['elevation_ft']:.0f} ft",
            icon=folium.Icon(color='green', icon='play'),
            tooltip='Trail Start'
        ).add_to(trail_map)
        
        folium.Marker(
            [end['latitude'], end['longitude']],
            popup=f"<b>End: Mount Katahdin, ME</b><br>Elevation: {end['elevation_ft']:.0f} ft",
            icon=folium.Icon(color='red', icon='stop'),
            tooltip='Trail End'
        ).add_to(trail_map)
        
        # Add state boundaries as markers
        for state in sampled_df['state'].unique():
            state_data = sampled_df[sampled_df['state'] == state]
            mid_idx = len(state_data) // 2
            if mid_idx < len(state_data):
                mid_point = state_data.iloc[mid_idx]
                
                folium.CircleMarker(
                    [mid_point['latitude'], mid_point['longitude']],
                    radius=5,
                    popup=f"<b>{state}</b>",
                    color='blue',
                    fill=True,
                    fillColor='lightblue',
                    fillOpacity=0.6
                ).add_to(trail_map)
        
        # Add layer control
        folium.LayerControl().add_to(trail_map)
        
        if save:
            path = os.path.join(self.output_dir, filename)
            trail_map.save(path)
            return path
        else:
            return trail_map
    
    def plot_difficulty_distribution(self,
                                    difficulty_stats: pd.DataFrame,
                                    save: bool = True,
                                    filename: str = 'difficulty_distribution.png') -> Optional[str]:
        """
        Visualize trail difficulty distribution.
        
        Args:
            difficulty_stats: DataFrame with difficulty statistics
            save: Whether to save the figure
            filename: Filename for saved figure
            
        Returns:
            Path to saved figure if save=True
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart of difficulty distribution
        ax1 = axes[0]
        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']
        ax1.pie(difficulty_stats['Miles'], 
               labels=difficulty_stats.index,
               autopct='%1.1f%%',
               colors=colors,
               startangle=90)
        ax1.set_title('Trail Difficulty Distribution\n(by Miles)', 
                     fontweight='bold', fontsize=12)
        
        # Bar chart with multiple metrics
        ax2 = axes[1]
        x = np.arange(len(difficulty_stats))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, difficulty_stats['Miles'], width, 
                       label='Miles', color='#1976D2', alpha=0.8)
        
        ax2_twin = ax2.twinx()
        bars2 = ax2_twin.bar(x + width/2, difficulty_stats['Avg Grade %'], width,
                            label='Avg Grade %', color='#D32F2F', alpha=0.8)
        
        ax2.set_xlabel('Difficulty Level', fontweight='bold')
        ax2.set_ylabel('Miles', fontweight='bold', color='#1976D2')
        ax2_twin.set_ylabel('Average Grade %', fontweight='bold', color='#D32F2F')
        ax2.set_title('Trail Metrics by Difficulty', fontweight='bold', fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(difficulty_stats.index, rotation=45, ha='right')
        ax2.tick_params(axis='y', labelcolor='#1976D2')
        ax2_twin.tick_params(axis='y', labelcolor='#D32F2F')
        
        # Add legends
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path, dpi=300, bbox_inches='tight')
            plt.close()
            return path
        else:
            plt.show()
            return None
    
    def create_dashboard(self, analyzer) -> str:
        """
        Create a comprehensive dashboard with all visualizations.
        
        Args:
            analyzer: TrailAnalyzer instance
            
        Returns:
            Path to main output directory
        """
        print("Generating visualizations...")
        
        # Get analysis data
        state_stats = analyzer.analyze_by_state()
        difficulty_stats = analyzer.analyze_difficulty_distribution()
        
        # Create all visualizations
        print("  - Elevation profile...")
        self.plot_elevation_profile()
        
        print("  - Interactive elevation profile...")
        self.create_interactive_elevation_profile()
        
        print("  - State statistics...")
        self.plot_state_statistics(state_stats)
        
        print("  - Difficulty distribution...")
        self.plot_difficulty_distribution(difficulty_stats)
        
        print("  - Elevation heatmap...")
        self.plot_elevation_heatmap()
        
        print("  - Interactive map...")
        self.create_interactive_map()
        
        print(f"\nAll visualizations saved to: {self.output_dir}")
        return self.output_dir


if __name__ == '__main__':
    from data_loader import load_or_generate_data
    from analysis import TrailAnalyzer
    
    # Load data
    df, _ = load_or_generate_data('../data/trail_data.csv')
    
    # Create analyzer and visualizer
    analyzer = TrailAnalyzer(df)
    visualizer = TrailVisualizer(df)
    
    # Create dashboard
    visualizer.create_dashboard(analyzer)

