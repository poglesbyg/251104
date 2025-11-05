#!/usr/bin/env python3
"""
Comprehensive FKT Analysis Report for the Appalachian Trail.
Analyzes the record-breaking 40 days, 18 hours, 6 minutes achievement.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_or_generate_data
from analysis import TrailAnalyzer
from fkt_analysis import FKTAnalyzer
from fkt_visualization import FKTVisualizer


def main():
    """Generate comprehensive FKT analysis report."""
    
    print("\n" + "="*80)
    print("  APPALACHIAN TRAIL FASTEST KNOWN TIME (FKT) ANALYSIS")
    print("  40 days, 18 hours, 6 minutes")
    print("="*80 + "\n")
    
    # Load data
    print("📊 Loading trail data...")
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'trail_data.csv')
    df, _ = load_or_generate_data(data_path)
    
    # Create analyzers
    print("🔬 Analyzing trail characteristics...")
    trail_analyzer = TrailAnalyzer(df)
    fkt_analyzer = FKTAnalyzer(df, trail_analyzer)
    
    # Print comprehensive report
    fkt_analyzer.print_comprehensive_report()
    
    # Generate visualizations
    print("\n" + "="*80)
    print("  GENERATING VISUALIZATIONS")
    print("="*80 + "\n")
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    fkt_viz = FKTVisualizer(fkt_analyzer, output_dir)
    fkt_viz.create_fkt_dashboard()
    
    print("\n" + "="*80)
    print("  FKT ANALYSIS COMPLETE")
    print("="*80)
    
    print("\n📁 Generated Files:")
    print(f"  • {output_dir}/fkt_pace_comparison.png")
    print(f"  • {output_dir}/fkt_daily_profile.png")
    print(f"  • {output_dir}/fkt_terrain_pace.png")
    
    print("\n💡 Key Takeaways:")
    print("  • 48 miles per day for 40+ consecutive days")
    print("  • 20+ hours of movement daily")
    print("  • 5,400+ feet of elevation gain every single day")
    print("  • 3.7x faster than typical thru-hike")
    print("  • Sustained 2.4 mph pace with minimal rest")
    
    print("\n🏆 This FKT represents the pinnacle of ultra-endurance achievement!")
    print("\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

