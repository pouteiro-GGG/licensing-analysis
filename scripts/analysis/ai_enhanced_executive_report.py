#!/usr/bin/env python3
"""
AI-Enhanced Executive Report Generator
Creates a human-readable executive report from the AI-enhanced analysis data
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class AIEnhancedExecutiveReport:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_file = "reports/current/ai_enhanced_executive_summary_20250725.md"
        
    def load_ai_data(self):
        """Load the AI-enhanced analysis data."""
        if not os.path.exists(self.ai_data_file):
            print(f"Error: AI-enhanced data file not found: {self.ai_data_file}")
            return None
            
        with open(self.ai_data_file, 'r') as f:
            return json.load(f)
    
    def generate_executive_summary(self, data):
        """Generate a comprehensive executive summary."""
        
        summary = data.get('summary', {})
        benchmarks = data.get('benchmarks', [])
        recommendations = data.get('recommendations', [])
        
        # Extract key metrics
        total_spend = summary.get('total_spend', 0)
        total_records = summary.get('total_records', 0)
        
        # Analyze benchmarks
        above_benchmark = [b for b in benchmarks if b.get('status') == 'Above Benchmark']
        below_benchmark = [b for b in benchmarks if b.get('status') == 'Below Benchmark']
        at_benchmark = [b for b in benchmarks if b.get('status') == 'At Benchmark']
        
        # Calculate potential savings
        potential_savings = sum(b.get('potential_savings', 0) for b in above_benchmark)
        
        # Group by vendor
        vendor_analysis = defaultdict(lambda: {'total_spend': 0, 'items': [], 'above_benchmark': 0})
        for benchmark in benchmarks:
            vendor = benchmark.get('vendor', 'Unknown')
            amount = benchmark.get('actual_spend', 0)
            vendor_analysis[vendor]['total_spend'] += amount
            vendor_analysis[vendor]['items'].append(benchmark)
            if benchmark.get('status') == 'Above Benchmark':
                vendor_analysis[vendor]['above_benchmark'] += 1
        
        # Top vendors by spend
        top_vendors = sorted(vendor_analysis.items(), key=lambda x: x[1]['total_spend'], reverse=True)[:10]
        
        # AI categorizations analysis
        ai_categories = defaultdict(lambda: {'count': 0, 'total_spend': 0})
        for benchmark in benchmarks:
            ai_cat = benchmark.get('ai_categorization', {})
            if ai_cat:
                category = ai_cat.get('primary_category', 'Unknown')
                ai_categories[category]['count'] += 1
                ai_categories[category]['total_spend'] += benchmark.get('actual_spend', 0)
        
        # Hidden costs analysis
        hidden_costs = defaultdict(int)
        for benchmark in benchmarks:
            ai_cat = benchmark.get('ai_categorization', {})
            if ai_cat:
                costs = ai_cat.get('hidden_costs', [])
                for cost in costs:
                    hidden_costs[cost] += 1
        
        # MSP services analysis
        msp_services = defaultdict(int)
        for benchmark in benchmarks:
            ai_cat = benchmark.get('ai_categorization', {})
            if ai_cat:
                services = ai_cat.get('msp_services', [])
                for service in services:
                    msp_services[service] += 1
        
        return {
            'summary': summary,
            'total_spend': total_spend,
            'total_records': total_records,
            'above_benchmark': above_benchmark,
            'below_benchmark': below_benchmark,
            'at_benchmark': at_benchmark,
            'potential_savings': potential_savings,
            'vendor_analysis': vendor_analysis,
            'top_vendors': top_vendors,
            'ai_categories': ai_categories,
            'hidden_costs': hidden_costs,
            'msp_services': msp_services,
            'recommendations': recommendations
        }
    
    def create_markdown_report(self, analysis):
        """Create a human-readable markdown report."""
        
        report = f"""# AI-Enhanced Executive Summary Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period:** 2024-2025
**AI-Enhanced Analysis:** Yes

## Executive Summary

### Key Metrics
- **Total Spend Analyzed:** ${analysis['total_spend']:,.2f}
- **Total Records:** {analysis['total_records']:,}
- **Potential Savings Identified:** ${analysis['potential_savings']:,.2f}
- **Above Benchmark Items:** {len(analysis['above_benchmark'])}
- **Below Benchmark Items:** {len(analysis['below_benchmark'])}

### Benchmark Performance
- **Above Benchmark:** {len(analysis['above_benchmark'])} items ({(len(analysis['above_benchmark'])/analysis['total_records']*100):.1f}%)
- **At Benchmark:** {len(analysis['at_benchmark'])} items ({(len(analysis['at_benchmark'])/analysis['total_records']*100):.1f}%)
- **Below Benchmark:** {len(analysis['below_benchmark'])} items ({(len(analysis['below_benchmark'])/analysis['total_records']*100):.1f}%)

## Top Vendors by Spend

"""
        
        for vendor, data in analysis['top_vendors']:
            report += f"- **{vendor}**: ${data['total_spend']:,.2f} ({data['above_benchmark']} items above benchmark)\n"
        
        report += f"""
## Critical Findings

### Items Significantly Above Benchmark
"""
        
        # Show top 10 above benchmark items
        top_above = sorted(analysis['above_benchmark'], key=lambda x: x.get('variance_percentage', 0), reverse=True)[:10]
        
        for item in top_above:
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('actual_spend', 0)
            variance = item.get('variance_percentage', 0)
            category = item.get('category', 'Unknown')
            ai_cat = item.get('ai_categorization', {})
            primary_cat = ai_cat.get('primary_category', 'Unknown') if ai_cat else 'Unknown'
            
            report += f"- **{vendor}** ({primary_cat}): ${amount:,.2f} (**{variance:+.1f}%** above benchmark)\n"
        
        report += f"""
## AI-Enhanced Insights

### Service Categories Identified
"""
        
        # Top AI categories by spend
        top_categories = sorted(analysis['ai_categories'].items(), key=lambda x: x[1]['total_spend'], reverse=True)[:10]
        
        for category, data in top_categories:
            report += f"- **{category}**: ${data['total_spend']:,.2f} ({data['count']} items)\n"
        
        report += f"""
### Hidden Costs Identified
"""
        
        if analysis['hidden_costs']:
            for cost, count in sorted(analysis['hidden_costs'].items(), key=lambda x: x[1], reverse=True):
                report += f"- **{cost}**: Found in {count} invoices\n"
        else:
            report += "- No specific hidden costs identified\n"
        
        report += f"""
### MSP Services Breakdown
"""
        
        if analysis['msp_services']:
            for service, count in sorted(analysis['msp_services'].items(), key=lambda x: x[1], reverse=True):
                report += f"- **{service}**: {count} instances\n"
        else:
            report += "- No specific MSP services identified\n"
        
        report += f"""
## Strategic Recommendations

### Immediate Actions (High Priority)
"""
        
        high_priority = [r for r in analysis['recommendations'] if r.get('priority') == 'High']
        for rec in high_priority[:5]:
            vendor = rec.get('vendor', 'Unknown')
            message = rec.get('message', 'No message')
            savings = rec.get('potential_savings', 'Unknown')
            report += f"- **{vendor}**: {message} (Potential savings: {savings})\n"
        
        report += f"""
### Medium-Term Optimizations
"""
        
        medium_priority = [r for r in analysis['recommendations'] if r.get('priority') == 'Medium']
        for rec in medium_priority[:5]:
            vendor = rec.get('vendor', 'Unknown')
            message = rec.get('message', 'No message')
            savings = rec.get('potential_savings', 'Unknown')
            report += f"- **{vendor}**: {message} (Potential savings: {savings})\n"
        
        report += f"""
## Cost Optimization Opportunities

### By Vendor
"""
        
        # Vendors with highest potential savings
        vendors_with_savings = []
        for vendor, data in analysis['vendor_analysis'].items():
            vendor_savings = sum(item.get('potential_savings', 0) for item in data['items'] if item.get('status') == 'Above Benchmark')
            if vendor_savings > 0:
                vendors_with_savings.append((vendor, vendor_savings))
        
        vendors_with_savings.sort(key=lambda x: x[1], reverse=True)
        
        for vendor, savings in vendors_with_savings[:10]:
            report += f"- **{vendor}**: ${savings:,.2f} potential savings\n"
        
        report += f"""
## Next Steps

1. **Immediate Review**: Focus on items 50%+ above benchmark
2. **Vendor Negotiations**: Prioritize vendors with highest potential savings
3. **MSP Contract Review**: Analyze hidden costs and service markups
4. **Category Optimization**: Review spending in highest-cost categories
5. **Benchmark Monitoring**: Implement ongoing benchmark tracking

## Technical Notes

- **AI Models Used**: Claude 3.5 Haiku (categorization), Claude Opus 4 (analysis)
- **Data Quality**: {analysis['total_records']} records processed with AI enhancement
- **Benchmark Sources**: Industry-standard benchmarks for IT services and software
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d')}

---
*Report generated by AI-Enhanced Licensing Analysis System*
"""
        
        return report
    
    def generate_report(self):
        """Generate the complete executive report."""
        print("Loading AI-enhanced analysis data...")
        data = self.load_ai_data()
        
        if not data:
            print("Failed to load AI data")
            return False
        
        print("Analyzing data and generating insights...")
        analysis = self.generate_executive_summary(data)
        
        print("Creating human-readable report...")
        report = self.create_markdown_report(analysis)
        
        # Save the report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ AI-Enhanced Executive Report generated successfully!")
        print(f"📄 Report saved to: {self.output_file}")
        print(f"💰 Potential savings identified: ${analysis['potential_savings']:,.2f}")
        print(f"📊 Items above benchmark: {len(analysis['above_benchmark'])}")
        
        return True

def main():
    """Main function to generate the AI-enhanced executive report."""
    print("=" * 60)
    print("    AI-ENHANCED EXECUTIVE REPORT GENERATOR")
    print("=" * 60)
    print()
    
    generator = AIEnhancedExecutiveReport()
    success = generator.generate_report()
    
    if success:
        print()
        print("🎉 Report generation completed successfully!")
        print("📋 Next steps:")
        print("   1. Review the generated report")
        print("   2. Focus on high-priority recommendations")
        print("   3. Use insights for vendor negotiations")
    else:
        print("❌ Report generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 