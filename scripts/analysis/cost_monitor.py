#!/usr/bin/env python3
"""
Cost Monitor Dashboard
Real-time monitoring of API costs and optimization opportunities
"""

import os
import sys
import json
from datetime import datetime, timedelta
from licensing_analyzer import LicensingAnalyzer

def display_cost_dashboard():
    """Display comprehensive cost monitoring dashboard."""
    try:
        print("💰 Cost Control Dashboard")
        print("=" * 60)
        
        # Initialize analyzer
        analyzer = LicensingAnalyzer()
        
        # Get comprehensive cost data
        cost_stats = analyzer.get_cost_control_stats()
        cost_breakdown = analyzer.get_cost_breakdown()
        cost_trends = analyzer.get_cost_trends(days=30)
        recommendations = analyzer.get_optimization_recommendations()
        
        # Display summary metrics
        print("\n📊 COST SUMMARY")
        print("-" * 40)
        print(f"Total API Calls:     {cost_stats['total_api_calls']:>8}")
        print(f"Cache Hits:          {cost_stats['cache_hits']:>8}")
        print(f"Cache Misses:        {cost_stats['cache_misses']:>8}")
        print(f"Cache Hit Rate:      {cost_stats['cache_hit_rate']:>7.1%}")
        print(f"Total Cost:          ${cost_stats['total_cost_usd']:>7.4f}")
        print(f"Cost Savings:        ${cost_stats['cost_savings_usd']:>7.4f}")
        print(f"Net Cost:            ${cost_stats['net_cost_usd']:>7.4f}")
        print(f"Last Updated:        {cost_stats['last_updated'][:19]}")
        
        # Display vendor breakdown
        print("\n🏢 VENDOR COST BREAKDOWN")
        print("-" * 40)
        print(f"{'Vendor':<20} {'API Calls':<10} {'Cost':<10} {'Cache Rate':<12}")
        print("-" * 52)
        
        for vendor in cost_breakdown.get('vendors', []):
            vendor_name = vendor['vendor'][:19]  # Truncate long names
            api_calls = vendor['api_calls']
            cost = vendor['total_cost_usd']
            cache_rate = vendor['cache_hit_rate']
            
            print(f"{vendor_name:<20} {api_calls:<10} ${cost:<9.4f} {cache_rate:<11.1%}")
        
        # Display cost trends
        print("\n📈 COST TRENDS (Last 30 Days)")
        print("-" * 40)
        trends = cost_trends.get('trends', [])
        
        if trends:
            print(f"{'Date':<12} {'API Calls':<10} {'Cost':<10} {'Cache Rate':<12}")
            print("-" * 44)
            
            # Show last 7 days
            for trend in trends[-7:]:
                date = trend['date']
                api_calls = trend['api_calls']
                cost = trend['total_cost_usd']
                cache_rate = trend['cache_hit_rate']
                
                print(f"{date:<12} {api_calls:<10} ${cost:<9.4f} {cache_rate:<11.1%}")
        else:
            print("No trend data available")
        
        # Display optimization recommendations
        print("\n💡 OPTIMIZATION RECOMMENDATIONS")
        print("-" * 40)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("No optimization recommendations at this time")
        
        # Display cost alerts
        print("\n🚨 COST ALERTS")
        print("-" * 40)
        
        alerts = []
        
        # Check for high costs
        if cost_stats['total_cost_usd'] > 50:
            alerts.append("⚠️  High total cost detected (>$50)")
        
        # Check for low cache hit rate
        if cost_stats['cache_hit_rate'] < 0.3:
            alerts.append("⚠️  Low cache hit rate (<30%)")
        
        # Check for high API call volume
        if cost_stats['total_api_calls'] > 100:
            alerts.append("⚠️  High API call volume (>100 calls)")
        
        # Check for recent high costs
        recent_trends = trends[-3:] if trends else []
        if recent_trends:
            recent_cost = sum(t['total_cost_usd'] for t in recent_trends)
            if recent_cost > 10:
                alerts.append(f"⚠️  High recent costs (${recent_cost:.2f} in last 3 days)")
        
        if alerts:
            for alert in alerts:
                print(alert)
        else:
            print("✅ No cost alerts - system is operating efficiently")
        
        # Display efficiency metrics
        print("\n⚡ EFFICIENCY METRICS")
        print("-" * 40)
        
        if cost_stats['total_api_calls'] > 0:
            avg_cost_per_call = cost_stats['total_cost_usd'] / cost_stats['total_api_calls']
            efficiency_score = cost_stats['cache_hit_rate'] * 100
            
            print(f"Average Cost per Call: ${avg_cost_per_call:.4f}")
            print(f"Efficiency Score:      {efficiency_score:.1f}%")
            
            if efficiency_score >= 80:
                print("Efficiency Status:    🟢 Excellent")
            elif efficiency_score >= 60:
                print("Efficiency Status:    🟡 Good")
            elif efficiency_score >= 40:
                print("Efficiency Status:    🟠 Fair")
            else:
                print("Efficiency Status:    🔴 Poor")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return False

def export_cost_report(output_file: str = None):
    """Export comprehensive cost report."""
    try:
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"cost_report_{timestamp}.json"
        
        analyzer = LicensingAnalyzer()
        
        # Gather all cost data
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "cost_summary": analyzer.get_cost_control_stats(),
            "vendor_breakdown": analyzer.get_cost_breakdown(),
            "cost_trends": analyzer.get_cost_trends(days=30),
            "optimization_recommendations": analyzer.get_optimization_recommendations(),
            "analysis_export": analyzer.export_analysis_data()
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✅ Cost report exported to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Export error: {e}")
        return None

def cleanup_old_data(days_old: int = 365):
    """Clean up old analysis data."""
    try:
        analyzer = LicensingAnalyzer()
        
        # This would require adding a cleanup method to the cost control manager
        # For now, we'll just show the option
        print(f"🧹 Cleanup option: Remove analysis data older than {days_old} days")
        print("   (This feature can be implemented in the cost control manager)")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        return False

def main():
    """Main function for cost monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cost Control Monitoring Dashboard")
    parser.add_argument("--dashboard", action="store_true", help="Display cost dashboard")
    parser.add_argument("--export", help="Export cost report to file")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Clean up data older than DAYS")
    
    args = parser.parse_args()
    
    if args.dashboard:
        display_cost_dashboard()
    elif args.export:
        export_cost_report(args.export)
    elif args.cleanup:
        cleanup_old_data(args.cleanup)
    else:
        # Default: show dashboard
        display_cost_dashboard()

if __name__ == "__main__":
    main() 