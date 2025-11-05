#!/usr/bin/env python3
"""
Daylight-Constrained Hiking Analysis Report.
Analyzes realistic hiking scenarios considering only daylight hours.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_or_generate_data
from analysis import TrailAnalyzer
from daylight_analysis import DaylightHikingAnalyzer
from daylight_visualization import DaylightVisualizer


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    """Generate comprehensive daylight-constrained analysis report."""
    
    print_section("DAYLIGHT-CONSTRAINED HIKING ANALYSIS")
    print("Analysis for hiking ONLY during daylight hours\n")
    
    # Load data
    print("📊 Loading trail data...")
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'trail_data.csv')
    df, _ = load_or_generate_data(data_path)
    
    # Create analyzers
    print("🔬 Analyzing with daylight constraints...")
    trail_analyzer = TrailAnalyzer(df)
    daylight_analyzer = DaylightHikingAnalyzer(df, trail_analyzer)
    
    print_section("FKT PACE WITH DAYLIGHT CONSTRAINTS")
    
    # Analyze FKT pace
    fkt_analysis = daylight_analyzer.calculate_daylight_constrained_pace(
        48, start_month=5, northbound=True
    )
    
    print("🏆 FKT Record Pace: 48 miles/day")
    print(f"\nTotal Days: {fkt_analysis['total_days']:.1f} days")
    print(f"\n🌅 Daylight Availability:")
    print(f"  • Average daylight: {fkt_analysis['avg_daylight_hours']:.1f} hours/day")
    print(f"  • Minimum daylight: {fkt_analysis['min_daylight_hours']:.1f} hours/day")
    print(f"  • Maximum daylight: {fkt_analysis['max_daylight_hours']:.1f} hours/day")
    print(f"  • Hiking hours available: {fkt_analysis['avg_hiking_hours_available']:.1f} hours/day (after breaks)")
    
    print(f"\n🏃 Required Pace:")
    print(f"  • Average: {fkt_analysis['avg_required_pace_mph']:.2f} mph")
    print(f"  • Maximum: {fkt_analysis['max_required_pace_mph']:.2f} mph")
    
    print(f"\n⚡ Feasibility: {fkt_analysis['feasibility']}")
    
    if fkt_analysis['max_required_pace_mph'] > 6.0:
        print("\n⚠️  REALITY CHECK:")
        print("   The FKT record pace is NOT achievable with daylight-only hiking!")
        print(f"   Required pace of {fkt_analysis['max_required_pace_mph']:.1f} mph is beyond")
        print("   sustainable human capabilities on mountainous terrain.")
        print("   The actual FKT must involve significant night hiking.")
    
    print_section("REALISTIC DAYLIGHT-ONLY SCENARIOS")
    
    # Test different paces
    scenarios = [
        ("Aggressive Thru-Hike", 30),
        ("Fast Thru-Hike", 25),
        ("Moderate Thru-Hike", 20),
        ("Comfortable Thru-Hike", 15)
    ]
    
    print("Starting in April (Northbound):\n")
    
    for scenario_name, miles_per_day in scenarios:
        analysis = daylight_analyzer.calculate_daylight_constrained_pace(
            miles_per_day, start_month=4, northbound=True
        )
        
        print(f"\n{scenario_name}: {miles_per_day} miles/day")
        print(f"  • Total days: {analysis['total_days']:.0f} days ({analysis['total_days']/30:.1f} months)")
        print(f"  • Avg pace required: {analysis['avg_required_pace_mph']:.2f} mph")
        print(f"  • Max pace required: {analysis['max_required_pace_mph']:.2f} mph")
        print(f"  • Hiking hours/day: {analysis['avg_hiking_hours_available']:.1f} hours")
        print(f"  • Feasibility: {analysis['feasibility']}")
    
    print_section("SEASONAL START COMPARISON")
    
    print("Comparing different start months for 25 miles/day (Northbound):\n")
    
    seasonal = daylight_analyzer.compare_seasonal_starts(25, northbound=True)
    print(seasonal.to_string(index=False))
    
    print("\n💡 Insights:")
    print("  • May-June starts provide the most daylight hours")
    print("  • April starts offer good balance of daylight and trail conditions")
    print("  • March starts have less daylight but beat the crowds")
    print("  • August starts face decreasing daylight as you progress north")
    
    print_section("OPTIMAL PACE RECOMMENDATION")
    
    # Find optimal pace for comfortable hiking
    print("Finding optimal daily mileage for 3.0 mph comfortable pace...\n")
    
    optimal = daylight_analyzer.calculate_optimal_pace_for_daylight(
        start_month=4, target_pace_mph=3.0
    )
    
    print(f"✅ Recommended Daily Mileage: {optimal['target_miles_per_day']:.0f} miles/day")
    print(f"\nThis allows:")
    print(f"  • Comfortable {optimal['avg_required_pace_mph']:.2f} mph average pace")
    print(f"  • {optimal['avg_hiking_hours_available']:.1f} hours of actual hiking")
    print(f"  • Time for breaks, meals, and camp setup")
    print(f"  • Total journey: {optimal['total_days']:.0f} days ({optimal['total_days']/30:.1f} months)")
    print(f"  • Assessment: {optimal['feasibility']}")
    
    # Test faster comfortable pace
    print("\n\nFor experienced hikers (3.5 mph comfortable pace):")
    optimal_fast = daylight_analyzer.calculate_optimal_pace_for_daylight(
        start_month=4, target_pace_mph=3.5
    )
    print(f"  • Recommended: {optimal_fast['target_miles_per_day']:.0f} miles/day")
    print(f"  • Total journey: {optimal_fast['total_days']:.0f} days ({optimal_fast['total_days']/30:.1f} months)")
    
    print_section("GENERATING VISUALIZATIONS")
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    daylight_viz = DaylightVisualizer(daylight_analyzer, output_dir)
    daylight_viz.create_daylight_dashboard()
    
    print_section("ANALYSIS COMPLETE")
    
    print("📁 Generated Files:")
    print(f"  • {output_dir}/daylight_throughout_hike.png")
    print(f"  • {output_dir}/seasonal_comparison.png")
    print(f"  • {output_dir}/pace_vs_daylight.png")
    
    print("\n📊 Key Takeaways:")
    print("  ✓ 20-25 miles/day is realistic for experienced daylight-only hikers")
    print("  ✓ April-May starts provide optimal daylight conditions")
    print("  ✓ Expect 3-4 months for a strong daylight-only thru-hike")
    print("  ✓ The FKT record REQUIRES significant night hiking")
    print("  ✓ Plan for 12-14 hours of available hiking time in peak season")
    
    print("\n🌙 Night Hiking Consideration:")
    print("  The FKT record of 40.75 days at 48 mi/day is only possible with")
    print("  extensive night hiking using headlamps. This analysis shows that")
    print("  daylight-only hiking is best suited for 15-30 miles per day,")
    print("  depending on fitness level and desired comfort.")
    
    print("\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

