#!/usr/bin/env python3
"""
Main analysis script for Appalachian Trail project.
Generates data, performs analysis, and creates visualizations.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_or_generate_data, AppalachianTrailData
from analysis import TrailAnalyzer
from visualization import TrailVisualizer
import json


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main():
    """Run the complete analysis pipeline."""
    
    print_section("APPALACHIAN TRAIL ANALYSIS & VISUALIZATION")
    
    # Step 1: Load or generate data
    print("📊 Loading trail data...")
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'trail_data.csv')
    
    if not os.path.exists(data_path):
        print("  Generating new trail data...")
        at_data = AppalachianTrailData(points_per_mile=10)
        df = at_data.generate_trail_data()
        stats = at_data.calculate_statistics(df)
        
        # Save data
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        at_data.save_data(df, data_path)
        stats_path = data_path.replace('trail_data.csv', 'trail_stats.json')
        at_data.save_statistics(stats, stats_path)
        print(f"  ✓ Generated {len(df):,} data points")
    else:
        print("  Loading existing data...")
        df, stats = load_or_generate_data(data_path)
        print(f"  ✓ Loaded {len(df):,} data points")
    
    # Step 2: Analyze the trail
    print_section("STATISTICAL ANALYSIS")
    
    analyzer = TrailAnalyzer(df)
    summary = analyzer.get_summary_statistics()
    
    print("📈 Summary Statistics:")
    print(f"  • Total Distance: {summary['total_distance_miles']:.1f} miles")
    print(f"  • Total Elevation Gain: {summary['total_elevation_gain_ft']:,.0f} feet")
    print(f"  • Total Elevation Loss: {summary['total_elevation_loss_ft']:,.0f} feet")
    print(f"  • Elevation Range: {summary['min_elevation_ft']:.0f} - {summary['max_elevation_ft']:.0f} feet")
    print(f"  • Average Elevation: {summary['avg_elevation_ft']:.0f} feet")
    print(f"  • Number of States: {summary['num_states']}")
    print(f"  • Significant Peaks: {summary['num_significant_peaks']}")
    print(f"  • Significant Valleys: {summary['num_significant_valleys']}")
    print(f"  • Average Grade: {summary['avg_grade_percent']:.2f}%")
    print(f"  • Maximum Grade: {summary['max_grade_percent']:.2f}%")
    
    # Hiking time estimates
    time_est = summary['hiking_time_estimates']
    print(f"\n⏱️  Hiking Time Estimates (Naismith's Rule):")
    print(f"  • Total hiking time: {time_est['total_hours']:,.0f} hours")
    print(f"  • Days at 8 hours/day: {time_est['hiking_days_8hr']:.0f} days")
    print(f"  • Days at 10 hours/day: {time_est['hiking_days_10hr']:.0f} days")
    print(f"  • Typical thru-hike duration: {time_est['typical_thru_hike_months']:.1f} months")
    
    # State analysis
    print_section("STATE-BY-STATE BREAKDOWN")
    state_stats = analyzer.analyze_by_state()
    print(state_stats.to_string(index=False))
    
    # Difficulty analysis
    print_section("DIFFICULTY DISTRIBUTION")
    difficulty_stats = analyzer.analyze_difficulty_distribution()
    print(difficulty_stats.to_string())
    
    # Toughest sections
    print_section("TOP 10 TOUGHEST SECTIONS (5-mile windows)")
    tough_sections = analyzer.get_toughest_sections(n=10, window_miles=5.0)
    print(tough_sections.to_string(index=False))
    
    # Step 3: Create visualizations
    print_section("GENERATING VISUALIZATIONS")
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    visualizer = TrailVisualizer(df, output_dir)
    
    # Generate all visualizations
    visualizer.create_dashboard(analyzer)
    
    # Save comprehensive analysis report
    print_section("SAVING ANALYSIS REPORT")
    
    report = {
        'summary_statistics': summary,
        'state_analysis': state_stats.to_dict('records'),
        'difficulty_distribution': difficulty_stats.reset_index().to_dict('records'),
        'toughest_sections': tough_sections.to_dict('records')
    }
    
    report_path = os.path.join(output_dir, 'analysis_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"  ✓ Analysis report saved to: {report_path}")
    
    # Final summary
    print_section("ANALYSIS COMPLETE!")
    
    print("📁 Output Files:")
    print(f"  • Data: {data_path}")
    print(f"  • Visualizations: {output_dir}/")
    print(f"  • Analysis Report: {report_path}")
    
    print("\n🗺️  Interactive Files (open in browser):")
    print(f"  • Interactive Map: {output_dir}/trail_map.html")
    print(f"  • Interactive Elevation: {output_dir}/interactive_elevation.html")
    
    print("\n📊 Static Visualizations:")
    print(f"  • Elevation Profile: {output_dir}/elevation_profile.png")
    print(f"  • State Statistics: {output_dir}/state_statistics.png")
    print(f"  • Difficulty Distribution: {output_dir}/difficulty_distribution.png")
    print(f"  • Elevation Heatmap: {output_dir}/elevation_heatmap.png")
    
    print("\n✨ Analysis complete! Open the HTML files in your browser to explore interactively.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

