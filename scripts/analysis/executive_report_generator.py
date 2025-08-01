#!/usr/bin/env python3
"""
Executive Report Generator
Creates clean, actionable reports for executives from licensing analysis data
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

class ExecutiveReportGenerator:
    def __init__(self):
        self.report_date = datetime.now().strftime("%B %d, %Y")
        
    def generate_executive_summary(self, analysis_data: List[Dict[str, Any]], output_file: str = None) -> str:
        """Generate a high-level executive summary report."""
        
        # Calculate key metrics
        total_spend = sum(item.get('total_amount', 0) for item in analysis_data)
        total_invoices = len(analysis_data)
        vendors = list(set(item.get('vendor', 'Unknown') for item in analysis_data))
        
        # Analyze cost variances
        cost_variances = []
        high_risk_items = []
        optimization_opportunities = []
        
        for item in analysis_data:
            if 'analysis' in item:
                analysis = item['analysis']
                summary = analysis.get('summary', {})
                
                # Cost variance
                variance = summary.get('cost_variance_percentage', 0)
                if variance > 0:
                    cost_variances.append({
                        'vendor': item.get('vendor', 'Unknown'),
                        'amount': item.get('total_amount', 0),
                        'variance': variance,
                        'assessment': summary.get('overall_assessment', 'Unknown')
                    })
                
                # High risk items
                risk_assessment = analysis.get('risk_assessment', {})
                high_risk = risk_assessment.get('high_risk_items', [])
                if high_risk:
                    high_risk_items.append({
                        'vendor': item.get('vendor', 'Unknown'),
                        'amount': item.get('total_amount', 0),
                        'risks': high_risk
                    })
                
                # Optimization opportunities
                opportunities = summary.get('cost_optimization_opportunities', [])
                if opportunities:
                    optimization_opportunities.append({
                        'vendor': item.get('vendor', 'Unknown'),
                        'amount': item.get('total_amount', 0),
                        'opportunities': opportunities
                    })
        
        # Generate report
        report = f"""
# EXECUTIVE SUMMARY - LICENSING COST ANALYSIS
**Report Date: {self.report_date}**

## 📊 KEY METRICS
- **Total Spend Analyzed:** ${total_spend:,.2f}
- **Total Invoices:** {total_invoices}
- **Vendors Analyzed:** {len(vendors)}
- **Top Vendors:** {', '.join(vendors[:5])}{'...' if len(vendors) > 5 else ''}

## 🚨 CRITICAL FINDINGS

### High-Cost Variance Items (>15% above standard)
"""
        
        high_variance_items = [item for item in cost_variances if item['variance'] > 15]
        if high_variance_items:
            for item in high_variance_items[:5]:  # Top 5
                report += f"""
**{item['vendor']}** - ${item['amount']:,.2f}
- **Variance:** {item['variance']:.1f}% above standard
- **Assessment:** {item['assessment']}
"""
        else:
            report += "\n✅ No critical cost variances identified\n"
        
        report += f"""
### High-Risk Items Requiring Immediate Attention
"""
        
        if high_risk_items:
            for item in high_risk_items[:3]:  # Top 3
                report += f"""
**{item['vendor']}** - ${item['amount']:,.2f}
- **Risks:** {', '.join(item['risks'][:2])}{'...' if len(item['risks']) > 2 else ''}
"""
        else:
            report += "\n✅ No high-risk items identified\n"
        
        # Calculate potential savings
        total_potential_savings = sum(item['amount'] * (item['variance'] / 100) for item in high_variance_items)
        
        report += f"""
## 💰 COST SAVINGS OPPORTUNITIES

### Immediate Savings Potential
- **Total Potential Savings:** ${total_potential_savings:,.2f}
- **Percentage of Total Spend:** {(total_potential_savings/total_spend*100):.1f}%

### Top Optimization Opportunities
"""
        
        if optimization_opportunities:
            for opp in optimization_opportunities[:3]:  # Top 3
                report += f"""
**{opp['vendor']}** - ${opp['amount']:,.2f}
- {opp['opportunities'][0] if opp['opportunities'] else 'Review pricing and terms'}
"""
        
        report += f"""
## 🎯 RECOMMENDED ACTIONS

### Immediate (Next 30 Days)
1. **Negotiate with high-variance vendors** - Potential savings: ${total_potential_savings:,.2f}
2. **Review and terminate unused licenses** - Estimated 10-15% savings
3. **Implement license management tools** - Prevent future over-licensing

### Short-term (Next 90 Days)
1. **Consolidate vendor contracts** - Leverage volume discounts
2. **Implement automated monitoring** - Real-time cost tracking
3. **Establish vendor management program** - Regular price reviews

### Long-term (Next 12 Months)
1. **Develop strategic vendor partnerships** - Long-term contracts with better terms
2. **Implement FinOps practices** - Cloud cost optimization
3. **Regular licensing audits** - Quarterly reviews

## 📈 SUCCESS METRICS
- **Target Cost Reduction:** 15-20% of current spend
- **Timeline:** 6-12 months
- **ROI:** 300-500% return on optimization efforts

---
*Report generated by Licensing Analysis System*
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Executive summary saved to: {output_file}")
        
        return report
    
    def generate_vendor_report(self, analysis_data: List[Dict[str, Any]], vendor_name: str, output_file: str = None) -> str:
        """Generate a focused report for a specific vendor."""
        
        vendor_data = [item for item in analysis_data if item.get('vendor', '').lower() == vendor_name.lower()]
        
        if not vendor_data:
            return f"No data found for vendor: {vendor_name}"
        
        total_spend = sum(item.get('total_amount', 0) for item in vendor_data)
        avg_variance = 0
        total_variance = 0
        count = 0
        
        for item in vendor_data:
            if 'analysis' in item:
                variance = item['analysis'].get('summary', {}).get('cost_variance_percentage', 0)
                total_variance += variance
                count += 1
        
        if count > 0:
            avg_variance = total_variance / count
        
        report = f"""
# VENDOR ANALYSIS REPORT
**Vendor:** {vendor_name}
**Report Date:** {self.report_date}

## 📊 VENDOR OVERVIEW
- **Total Spend:** ${total_spend:,.2f}
- **Number of Invoices:** {len(vendor_data)}
- **Average Cost Variance:** {avg_variance:+.1f}%
- **Overall Assessment:** {'Above Standard' if avg_variance > 10 else 'At Standard' if avg_variance > -10 else 'Below Standard'}

## 🔍 DETAILED ANALYSIS
"""
        
        for i, item in enumerate(vendor_data[:5], 1):  # Top 5 invoices
            analysis = item.get('analysis', {})
            summary = analysis.get('summary', {})
            
            report += f"""
### Invoice {i}
- **Amount:** ${item.get('total_amount', 0):,.2f}
- **Date:** {item.get('invoice_date', 'Unknown')}
- **Cost Variance:** {summary.get('cost_variance_percentage', 0):+.1f}%
- **Assessment:** {summary.get('overall_assessment', 'Unknown')}
- **Key Finding:** {summary.get('key_findings', ['None'])[0] if summary.get('key_findings') else 'No findings'}
"""
        
        # Recommendations
        all_recommendations = []
        for item in vendor_data:
            if 'analysis' in item:
                analysis = item.get('analysis', {})
                recommendations = analysis.get('recommendations', {})
                all_recommendations.extend(recommendations.get('immediate_actions', []))
                all_recommendations.extend(recommendations.get('short_term_optimizations', []))
        
        unique_recommendations = list(set(all_recommendations))[:5]
        
        report += f"""
## 💡 RECOMMENDATIONS

### Immediate Actions
"""
        
        for rec in unique_recommendations:
            report += f"- {rec}\n"
        
        potential_savings = total_spend * (avg_variance / 100) if avg_variance > 0 else 0
        
        report += f"""
### Potential Impact
- **Potential Savings:** ${potential_savings:,.2f}
- **Savings Percentage:** {avg_variance:.1f}% of current spend
- **Timeline:** 30-90 days

---
*Report generated by Licensing Analysis System*
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Vendor report saved to: {output_file}")
        
        return report
    
    def generate_cost_savings_report(self, analysis_data: List[Dict[str, Any]], output_file: str = None) -> str:
        """Generate a focused cost savings report."""
        
        # Calculate savings opportunities
        savings_opportunities = []
        total_spend = 0
        
        for item in analysis_data:
            total_spend += item.get('total_amount', 0)
            
            if 'analysis' in item:
                analysis = item.get('analysis', {})
                summary = analysis.get('summary', {})
                variance = summary.get('cost_variance_percentage', 0)
                
                if variance > 0:
                    potential_savings = item.get('total_amount', 0) * (variance / 100)
                    savings_opportunities.append({
                        'vendor': item.get('vendor', 'Unknown'),
                        'amount': item.get('total_amount', 0),
                        'variance': variance,
                        'potential_savings': potential_savings,
                        'opportunities': summary.get('cost_optimization_opportunities', [])
                    })
        
        # Sort by potential savings
        savings_opportunities.sort(key=lambda x: x['potential_savings'], reverse=True)
        
        total_potential_savings = sum(item['potential_savings'] for item in savings_opportunities)
        
        report = f"""
# COST SAVINGS OPPORTUNITIES REPORT
**Report Date:** {self.report_date}

## 💰 EXECUTIVE SUMMARY
- **Total Spend Analyzed:** ${total_spend:,.2f}
- **Total Potential Savings:** ${total_potential_savings:,.2f}
- **Savings Percentage:** {(total_potential_savings/total_spend*100):.1f}% of total spend

## 🎯 TOP SAVINGS OPPORTUNITIES
"""
        
        for i, opp in enumerate(savings_opportunities[:10], 1):  # Top 10
            report += f"""
### {i}. {opp['vendor']}
- **Current Spend:** ${opp['amount']:,.2f}
- **Cost Variance:** {opp['variance']:.1f}% above standard
- **Potential Savings:** ${opp['potential_savings']:,.2f}
- **Primary Opportunity:** {opp['opportunities'][0] if opp['opportunities'] else 'Negotiate better pricing'}

"""
        
        report += f"""
## 📊 SAVINGS BY CATEGORY

### High Impact (>$10,000 potential savings)
"""
        
        high_impact = [opp for opp in savings_opportunities if opp['potential_savings'] > 10000]
        for opp in high_impact:
            report += f"- **{opp['vendor']}:** ${opp['potential_savings']:,.2f}\n"
        
        report += f"""
### Medium Impact ($1,000-$10,000 potential savings)
"""
        
        medium_impact = [opp for opp in savings_opportunities if 1000 <= opp['potential_savings'] <= 10000]
        for opp in medium_impact:
            report += f"- **{opp['vendor']}:** ${opp['potential_savings']:,.2f}\n"
        
        report += f"""
## 🚀 IMPLEMENTATION ROADMAP

### Phase 1: Quick Wins (30 days)
- Focus on vendors with >20% cost variance
- Estimated savings: ${sum(opp['potential_savings'] for opp in savings_opportunities if opp['variance'] > 20):,.2f}

### Phase 2: Strategic Negotiations (90 days)
- Renegotiate contracts with major vendors
- Estimated savings: ${sum(opp['potential_savings'] for opp in savings_opportunities if opp['amount'] > 50000):,.2f}

### Phase 3: Process Optimization (6 months)
- Implement automated monitoring and management
- Estimated savings: 10-15% of remaining spend

## 📈 ROI PROJECTION
- **Investment Required:** $50,000-$100,000 (tools, consulting, time)
- **Annual Savings:** ${total_potential_savings:,.2f}
- **ROI:** {(total_potential_savings/75000*100):.0f}% (assuming $75k investment)
- **Payback Period:** 2-3 months

---
*Report generated by Licensing Analysis System*
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Cost savings report saved to: {output_file}")
        
        return report

def main():
    """Generate executive reports from analysis data."""
    
    # Check if analysis data exists
    data_file = "reports/processed_licensing_data.json"
    if not os.path.exists(data_file):
        print(f"❌ Analysis data file not found: {data_file}")
        print("Please run the licensing analysis first.")
        return
    
    print("🚀 Generating Executive Reports...")
    
    # Load analysis data
    try:
        with open(data_file, 'r') as f:
            analysis_data = json.load(f)
        print(f"✅ Loaded {len(analysis_data)} analysis records")
    except Exception as e:
        print(f"❌ Error loading analysis data: {e}")
        return
    
    # Initialize report generator
    generator = ExecutiveReportGenerator()
    
    # Generate reports
    reports_dir = "reports/executive"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Executive Summary
    print("\n📊 Generating Executive Summary...")
    summary = generator.generate_executive_summary(
        analysis_data, 
        f"{reports_dir}/executive_summary_{datetime.now().strftime('%Y%m%d')}.md"
    )
    
    # Cost Savings Report
    print("💰 Generating Cost Savings Report...")
    savings_report = generator.generate_cost_savings_report(
        analysis_data,
        f"{reports_dir}/cost_savings_report_{datetime.now().strftime('%Y%m%d')}.md"
    )
    
    # Vendor-specific reports (top 3 vendors by spend)
    vendor_spend = {}
    for item in analysis_data:
        vendor = item.get('vendor', 'Unknown')
        vendor_spend[vendor] = vendor_spend.get(vendor, 0) + item.get('total_amount', 0)
    
    top_vendors = sorted(vendor_spend.items(), key=lambda x: x[1], reverse=True)[:3]
    
    print("🏢 Generating Vendor Reports...")
    for vendor, spend in top_vendors:
        print(f"   - {vendor}: ${spend:,.2f}")
        generator.generate_vendor_report(
            analysis_data,
            vendor,
            f"{reports_dir}/vendor_report_{vendor.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        )
    
    print(f"\n🎉 Executive reports generated successfully!")
    print(f"📁 Reports saved to: {reports_dir}/")
    print(f"\n📋 Generated Reports:")
    print(f"   - Executive Summary")
    print(f"   - Cost Savings Opportunities")
    print(f"   - Vendor Reports ({len(top_vendors)} vendors)")
    
    # Show summary
    print(f"\n📊 Quick Summary:")
    total_spend = sum(item.get('total_amount', 0) for item in analysis_data)
    print(f"   - Total Spend Analyzed: ${total_spend:,.2f}")
    print(f"   - Total Invoices: {len(analysis_data)}")
    print(f"   - Vendors Analyzed: {len(vendor_spend)}")

if __name__ == "__main__":
    main() 