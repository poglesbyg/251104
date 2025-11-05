#!/usr/bin/env python3
"""
Compare FKT with 24/7 hiking vs daylight-only hiking.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_or_generate_data
from analysis import TrailAnalyzer
from fkt_analysis import FKTAnalyzer
from daylight_analysis import DaylightAnalyzer


def main():
    """Generate daylight-aware FKT comparison."""
    
    print("\n" + "="*80)
    print("  FKT ANALYSIS: 24/7 HIKING vs DAYLIGHT-ONLY")
    print("="*80 + "\n")
    
    # Load data
    print("📊 Loading trail data...")
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'trail_data.csv')
    df, _ = load_or_generate_data(data_path)
    
    # Create analyzers
    print("🔬 Analyzing trail characteristics...\n")
    trail_analyzer = TrailAnalyzer(df)
    fkt_analyzer = FKTAnalyzer(df, trail_analyzer)
    daylight_analyzer = DaylightAnalyzer(df)
    
    # Print comprehensive report with daylight analysis
    fkt_analyzer.print_comprehensive_report(
        include_daylight=True,
        daylight_analyzer=daylight_analyzer
    )
    
    print("\n" + "="*80)
    print("  KEY INSIGHTS")
    print("="*80)
    
    print("\n🌙 24/7 HIKING (Current FKT):")
    print("  • Requires 20+ hours of movement daily")
    print("  • Hiking through the night with headlamps")
    print("  • Only 4 hours for sleep/rest per day")
    print("  • Extremely challenging but humanly possible")
    
    print("\n🌞 DAYLIGHT-ONLY HIKING:")
    print("  • Much more practical and safer")
    print("  • Allows proper sleep (7-8 hours)")
    print("  • Easier navigation and trail finding")
    print("  • Still challenging but more sustainable")
    
    print("\n📈 TIME DIFFERENCE:")
    fkt_days = 40.75
    daylight_fast = 61  # At 3.0 mph
    daylight_typical = 89  # At 2.0 mph
    
    print(f"  • 24/7 hiking: {fkt_days:.0f} days")
    print(f"  • Daylight-only (fast): ~{daylight_fast} days ({daylight_fast/fkt_days:.1f}x longer)")
    print(f"  • Daylight-only (typical): ~{daylight_typical} days ({daylight_typical/fkt_days:.1f}x longer)")
    
    print("\n💡 RECOMMENDATION:")
    print("  For most thru-hikers, daylight-only hiking is the way to go.")
    print("  Plan for 90-150 days depending on your fitness level.")
    print("  Starting in mid-March gives the best daylight hours!")
    
    print("\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

