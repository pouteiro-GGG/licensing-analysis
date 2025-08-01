#!/usr/bin/env python3
"""
Demo: Human-Readable Reports
Shows how the system generates beautiful, easy-to-read reports from analysis data
"""

import os
import json
from datetime import datetime
from licensing_analyzer import LicensingAnalyzer
from report_formatter import format_report_from_file

def demo_human_readable_reports():
    """Demonstrate human-readable report generation."""
    try:
        print("📄 Human-Readable Report Demo")
        print("=" * 60)
        
        # Check if we have existing analysis data
        latest_report = None
        reports_dir = "reports"
        
        if os.path.exists(reports_dir):
            json_files = [f for f in os.listdir(reports_dir) if f.endswith('.json') and 'licensing_analysis_report' in f]
            if json_files:
                # Get the latest report
                latest_report = max(json_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
                latest_report_path = os.path.join(reports_dir, latest_report)
                print(f"📊 Found existing analysis report: {latest_report}")
            else:
                print("📊 No existing analysis reports found. Creating sample data...")
                latest_report_path = create_sample_analysis_data()
        else:
            print("📊 No reports directory found. Creating sample data...")
            latest_report_path = create_sample_analysis_data()
        
        # Generate human-readable report
        print(f"\n🔄 Generating human-readable report from: {latest_report_path}")
        
        # Generate comprehensive report
        comprehensive_report = format_report_from_file(
            latest_report_path, 
            "reports/human_readable_comprehensive_report.txt"
        )
        
        print("✅ Comprehensive human-readable report generated!")
        
        # Show a preview of the report
        print("\n📋 REPORT PREVIEW:")
        print("-" * 60)
        
        # Show first 50 lines of the report
        lines = comprehensive_report.split('\n')
        for i, line in enumerate(lines[:50]):
            print(line)
            if i >= 49:
                print("...")
                break
        
        # Generate cost control report
        print(f"\n💰 Generating cost control report...")
        analyzer = LicensingAnalyzer()
        cost_report = analyzer.generate_cost_control_report("reports/human_readable_cost_report.txt")
        
        print("✅ Cost control report generated!")
        
        # Show cost report preview
        print("\n💰 COST CONTROL REPORT PREVIEW:")
        print("-" * 60)
        cost_lines = cost_report.split('\n')
        for i, line in enumerate(cost_lines[:20]):
            print(line)
            if i >= 19:
                print("...")
                break
        
        # Generate vendor-specific report (if we have vendor data)
        print(f"\n🏢 Generating vendor-specific report...")
        try:
            with open(latest_report_path, 'r') as f:
                analysis_data = json.load(f)
            
            # Get top vendor
            top_vendors = analysis_data.get("comprehensive_summary", {}).get("top_vendors_by_cost", [])
            if top_vendors:
                top_vendor_name = top_vendors[0][0]
                vendor_report = analyzer.generate_vendor_report(
                    analysis_data, 
                    top_vendor_name, 
                    f"reports/human_readable_vendor_report_{top_vendor_name.replace(' ', '_')}.txt"
                )
                print(f"✅ Vendor report generated for: {top_vendor_name}")
                
                # Show vendor report preview
                print(f"\n🏢 VENDOR REPORT PREVIEW ({top_vendor_name}):")
                print("-" * 60)
                vendor_lines = vendor_report.split('\n')
                for i, line in enumerate(vendor_lines[:25]):
                    print(line)
                    if i >= 24:
                        print("...")
                        break
        except Exception as e:
            print(f"⚠️  Could not generate vendor report: {e}")
        
        # Summary
        print(f"\n📋 GENERATED REPORTS:")
        print("-" * 60)
        print("✅ Comprehensive Analysis Report: reports/human_readable_comprehensive_report.txt")
        print("✅ Cost Control Report: reports/human_readable_cost_report.txt")
        if top_vendors:
            print(f"✅ Vendor Report: reports/human_readable_vendor_report_{top_vendor_name.replace(' ', '_')}.txt")
        
        print(f"\n🎯 REPORT FEATURES:")
        print("-" * 60)
        print("• 📊 Executive Summary with color-coded assessments")
        print("• 🔍 Key Findings organized by priority")
        print("• 🏢 Vendor Analysis with cost breakdowns")
        print("• 📊 Category Breakdown with insights")
        print("• ⚠️  Risk Assessment by severity level")
        print("• 🎯 Actionable Recommendations with timelines")
        print("• 💰 Estimated Savings projections")
        print("• 📞 Clear Next Steps for implementation")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_analysis_data():
    """Create sample analysis data for demo purposes."""
    sample_data = {
        "comprehensive_summary": {
            "total_invoices_analyzed": 150,
            "total_cost": 2500000.00,
            "average_cost_variance_percentage": 25.5,
            "overall_assessment": "Above Standard",
            "top_vendors_by_cost": [
                ["Microsoft", 1200000.00],
                ["Adobe", 450000.00],
                ["Atlassian", 300000.00],
                ["VMware", 250000.00],
                ["Oracle", 200000.00]
            ]
        },
        "aggregated_findings": {
            "key_findings": [
                "Microsoft 365 licensing costs are 15% above industry standards",
                "Adobe Creative Suite pricing is competitive but lacks volume discounts",
                "Atlassian suite shows good value for money",
                "VMware licensing could benefit from enterprise agreements",
                "Oracle database licensing appears over-provisioned",
                "Professional services rates are 20% above market average",
                "Hardware procurement costs are within acceptable ranges",
                "Cloud services show potential for optimization",
                "Support costs represent 8% of total spend",
                "Multiple overlapping tools identified in collaboration category"
            ],
            "category_breakdown": {
                "Microsoft 365": {
                    "cost": 1200000.00,
                    "recommendations": ["Negotiate enterprise agreement", "Review license utilization"]
                },
                "Adobe": {
                    "cost": 450000.00,
                    "recommendations": ["Implement volume licensing", "Consider Creative Cloud alternatives"]
                },
                "Atlassian": {
                    "cost": 300000.00,
                    "recommendations": ["Current pricing is competitive", "Monitor for future increases"]
                }
            },
            "risk_assessment": {
                "high": [
                    "Microsoft licensing over-provisioned by 25%",
                    "Oracle database licensing not optimized",
                    "Professional services costs excessive"
                ],
                "medium": [
                    "Adobe lacks volume discounts",
                    "Cloud services could be optimized",
                    "Support costs slightly above average"
                ],
                "low": [
                    "Atlassian pricing is reasonable",
                    "Hardware costs are competitive",
                    "Basic infrastructure costs are standard"
                ]
            }
        },
        "recommendations": {
            "immediate_actions": [
                "Review Microsoft 365 license utilization and right-size",
                "Negotiate enterprise agreement with Microsoft",
                "Audit Oracle database licensing requirements",
                "Review professional services contracts and rates"
            ],
            "short_term_optimizations": [
                "Implement volume licensing for Adobe products",
                "Optimize cloud services usage and costs",
                "Consolidate overlapping collaboration tools",
                "Negotiate better support contract terms"
            ],
            "long_term_strategies": [
                "Develop comprehensive software asset management strategy",
                "Implement automated license monitoring and optimization",
                "Establish vendor management program",
                "Create cost optimization governance framework"
            ],
            "estimated_savings": {
                "immediate": 150000.00,
                "short_term": 300000.00,
                "long_term": 500000.00
            }
        }
    }
    
    # Save sample data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sample_file = f"reports/sample_analysis_data_{timestamp}.json"
    
    os.makedirs("reports", exist_ok=True)
    with open(sample_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"📊 Sample analysis data created: {sample_file}")
    return sample_file

def show_report_comparison():
    """Show comparison between JSON and human-readable formats."""
    print("\n📊 FORMAT COMPARISON")
    print("=" * 60)
    
    print("🔴 JSON FORMAT (Machine-readable):")
    print("-" * 40)
    print('''{
  "comprehensive_summary": {
    "total_invoices_analyzed": 1293,
    "total_cost": 14157950.02,
    "overall_assessment": "Critical"
  }
}''')
    
    print("\n🟢 HUMAN-READABLE FORMAT:")
    print("-" * 40)
    print('''================================================================================
                    LICENSING ANALYSIS REPORT
                    Cost Optimization & Risk Assessment
================================================================================
Generated: July 25, 2025 at 09:30 AM

📊 EXECUTIVE SUMMARY
--------------------------------------------------------------------------------

Overall Assessment:     🔴 CRITICAL - Immediate Action Required
Total Invoices Analyzed: 1,293
Total Cost Analyzed:     $14,157,950.02
Average Cost Variance:   72.2%

🏢 TOP VENDORS BY COST:

  1. Synoptek, LLC: $8,541,066.25
  2. Synoptek: $4,946,352.87
  3. Markov Processes International, Inc.: $149,737.50
  4. Atlassian Pty Ltd: $131,595.57
  5. Harman Connected Services Inc: $110,584.16

🔍 KEY FINDINGS
--------------------------------------------------------------------------------

🚨 CRITICAL ISSUES:

  1. Azure managed services premium at $9,235.42/month is significantly above 
     typical managed service costs
  2. Total monthly spend of $54,037.50 for migration services is excessive 
     for a single month
  3. IT Advisory services at $2250/month appears high for 31-user organization

💡 OPTIMIZATION OPPORTUNITIES:

  1. Consider annual licensing for better rates
  2. Negotiate volume discounts for multiple units
  3. Implement auto-scaling and scheduled shutdowns

🎯 RECOMMENDATIONS
--------------------------------------------------------------------------------

⚡ IMMEDIATE ACTIONS (Next 30 Days):

  1. Review Microsoft 365 pricing
  2. Audit Oracle database licensing requirements
  3. Review professional services contracts and rates

💰 ESTIMATED SAVINGS:

  Immediate (30 days):     $150,000.00
  Short-term (90 days):    $300,000.00
  Long-term (12 months):   $500,000.00

📞 NEXT STEPS

1. Review critical findings and immediate actions
2. Schedule vendor negotiations for high-value contracts
3. Implement cost optimization recommendations
4. Set up regular cost monitoring and review cycles
5. Consider implementing automated cost alerts

For questions or additional analysis, contact your IT cost management team.

================================================================================''')

if __name__ == "__main__":
    print("🚀 Human-Readable Report Demo")
    print("=" * 60)
    
    # Run the demo
    success = demo_human_readable_reports()
    
    # Show format comparison
    show_report_comparison()
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("\n📋 Key Benefits of Human-Readable Reports:")
        print("• ✅ Easy to read and understand")
        print("• ✅ Color-coded priority levels")
        print("• ✅ Organized sections with clear headers")
        print("• ✅ Actionable insights and recommendations")
        print("• ✅ Professional presentation for stakeholders")
        print("• ✅ Immediate value for decision-making")
    else:
        print("\n❌ Demo failed. Please check the errors above.") 