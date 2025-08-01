#!/usr/bin/env python3
"""
Industry Benchmark Analyzer
Compares licensing costs to industry standards and groups spending by functional areas
"""

import json
import os
from datetime import datetime
from collections import defaultdict
import re

class IndustryBenchmarkAnalyzer:
    def __init__(self):
        # Industry benchmark data (typical ranges for different software categories)
        self.industry_benchmarks = {
            "cloud_services": {
                "aws": {"low": 0.08, "high": 0.15, "unit": "per_dollar_spend"},
                "azure": {"low": 0.10, "high": 0.18, "unit": "per_dollar_spend"},
                "gcp": {"low": 0.09, "high": 0.16, "unit": "per_dollar_spend"}
            },
            "development_tools": {
                "atlassian": {"low": 0.05, "high": 0.12, "unit": "per_user_month"},
                "github": {"low": 0.04, "high": 0.10, "unit": "per_user_month"},
                "gitlab": {"low": 0.03, "high": 0.08, "unit": "per_user_month"},
                "visual_studio": {"low": 0.08, "high": 0.15, "unit": "per_user_month"}
            },
            "enterprise_software": {
                "microsoft": {"low": 0.12, "high": 0.25, "unit": "per_user_month"},
                "oracle": {"low": 0.15, "high": 0.30, "unit": "per_user_month"},
                "salesforce": {"low": 0.20, "high": 0.40, "unit": "per_user_month"},
                "sap": {"low": 0.25, "high": 0.50, "unit": "per_user_month"}
            },
            "security_software": {
                "crowdstrike": {"low": 0.08, "high": 0.15, "unit": "per_endpoint_month"},
                "sentinelone": {"low": 0.07, "high": 0.14, "unit": "per_endpoint_month"},
                "palo_alto": {"low": 0.10, "high": 0.20, "unit": "per_user_month"},
                "proofpoint": {"low": 0.05, "high": 0.12, "unit": "per_user_month"}
            },
            "it_services": {
                "managed_services": {"low": 0.15, "high": 0.30, "unit": "per_dollar_spend"},
                "consulting": {"low": 0.20, "high": 0.40, "unit": "per_hour"},
                "support": {"low": 0.10, "high": 0.25, "unit": "per_dollar_spend"}
            }
        }
        
        # Vendor categorization mapping
        self.vendor_categories = {
            "synoptek": "it_services",
            "synoptek, llc": "it_services",
            "atlassian": "development_tools",
            "microsoft": "enterprise_software",
            "oracle": "enterprise_software",
            "salesforce": "enterprise_software",
            "aws": "cloud_services",
            "amazon": "cloud_services",
            "azure": "cloud_services",
            "google": "cloud_services",
            "gcp": "cloud_services",
            "github": "development_tools",
            "gitlab": "development_tools",
            "crowdstrike": "security_software",
            "sentinelone": "security_software",
            "palo alto": "security_software",
            "proofpoint": "security_software",
            "harman": "it_services",
            "markov": "it_services"
        }
    
    def categorize_vendor(self, vendor_name):
        """Categorize vendor based on name and line items."""
        vendor_lower = vendor_name.lower()
        
        # Direct vendor mapping
        for vendor_key, category in self.vendor_categories.items():
            if vendor_key in vendor_lower:
                return category
        
        # Fallback categorization based on line items
        return "it_services"  # Default category
    
    def analyze_industry_comparison(self, data):
        """Analyze costs against industry benchmarks."""
        
        # Group by category
        categorized_spend = defaultdict(list)
        category_totals = defaultdict(float)
        
        for item in data:
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('total_amount', 0)
            category = self.categorize_vendor(vendor)
            
            categorized_spend[category].append(item)
            category_totals[category] += amount
        
        # Calculate industry comparisons
        analysis_results = {}
        total_spend = sum(category_totals.values())
        
        for category, spend in category_totals.items():
            # Get benchmark for this category
            benchmark = self.get_category_benchmark(category, spend, len(categorized_spend[category]))
            
            analysis_results[category] = {
                'total_spend': spend,
                'percentage_of_total': (spend / total_spend) * 100,
                'invoice_count': len(categorized_spend[category]),
                'benchmark': benchmark,
                'variance': self.calculate_variance(spend, benchmark),
                'vendors': list(set(item.get('vendor', 'Unknown') for item in categorized_spend[category]))
            }
        
        return analysis_results, categorized_spend
    
    def get_category_benchmark(self, category, spend, invoice_count):
        """Get industry benchmark for a category."""
        # Simplified benchmark calculation
        if category == "it_services":
            # IT services typically 15-30% of total IT spend
            return {"low": spend * 0.15, "high": spend * 0.30, "assessment": "industry_standard"}
        elif category == "development_tools":
            # Development tools typically 5-12% of total IT spend
            return {"low": spend * 0.05, "high": spend * 0.12, "assessment": "industry_standard"}
        elif category == "enterprise_software":
            # Enterprise software typically 12-25% of total IT spend
            return {"low": spend * 0.12, "high": spend * 0.25, "assessment": "industry_standard"}
        elif category == "security_software":
            # Security software typically 8-15% of total IT spend
            return {"low": spend * 0.08, "high": spend * 0.15, "assessment": "industry_standard"}
        elif category == "cloud_services":
            # Cloud services typically 10-18% of total IT spend
            return {"low": spend * 0.10, "high": spend * 0.18, "assessment": "industry_standard"}
        else:
            return {"low": spend * 0.10, "high": spend * 0.20, "assessment": "unknown"}
    
    def calculate_variance(self, actual_spend, benchmark):
        """Calculate variance from industry benchmark."""
        if benchmark['high'] == 0:
            return 0
        
        if actual_spend <= benchmark['low']:
            variance = ((benchmark['low'] - actual_spend) / benchmark['low']) * 100
            assessment = "below_industry_standard"
        elif actual_spend <= benchmark['high']:
            variance = 0
            assessment = "within_industry_standard"
        else:
            variance = ((actual_spend - benchmark['high']) / benchmark['high']) * 100
            assessment = "above_industry_standard"
        
        return {
            'percentage': variance,
            'assessment': assessment,
            'actual': actual_spend,
            'benchmark_low': benchmark['low'],
            'benchmark_high': benchmark['high']
        }
    
    def generate_industry_comparison_report(self, analysis_results, categorized_spend):
        """Generate comprehensive industry comparison report."""
        
        total_spend = sum(result['total_spend'] for result in analysis_results.values())
        
        report = f"""
# INDUSTRY BENCHMARK ANALYSIS - LICENSING COST COMPARISON
**Report Date:** {datetime.now().strftime("%B %d, %Y")}

## 📊 EXECUTIVE SUMMARY
- **Total Spend Analyzed:** ${total_spend:,.2f}
- **Categories Analyzed:** {len(analysis_results)}
- **Industry Standard Assessment:** {self.get_overall_assessment(analysis_results)}

## 🏢 SPENDING BY FUNCTIONAL AREA
"""
        
        # Sort by spend amount
        sorted_categories = sorted(analysis_results.items(), key=lambda x: x[1]['total_spend'], reverse=True)
        
        for category, data in sorted_categories:
            variance = data['variance']
            report += f"""
### {category.replace('_', ' ').title()}
- **Total Spend:** ${data['total_spend']:,.2f}
- **Percentage of Total:** {data['percentage_of_total']:.1f}%
- **Invoice Count:** {data['invoice_count']}
- **Industry Benchmark:** ${data['benchmark']['low']:,.2f} - ${data['benchmark']['high']:,.2f}
- **Assessment:** {self.get_assessment_description(variance['assessment'])}
- **Variance:** {variance['percentage']:+.1f}% from industry standard
- **Key Vendors:** {', '.join(data['vendors'][:3])}{'...' if len(data['vendors']) > 3 else ''}
"""
        
        # Identify optimization opportunities
        optimization_opportunities = []
        for category, data in analysis_results.items():
            variance = data['variance']
            if variance['assessment'] == 'above_industry_standard':
                potential_savings = data['total_spend'] * (variance['percentage'] / 100)
                optimization_opportunities.append({
                    'category': category,
                    'current_spend': data['total_spend'],
                    'potential_savings': potential_savings,
                    'variance': variance['percentage']
                })
        
        report += f"""
## 🚨 COST VARIANCES FROM INDUSTRY STANDARDS

### Above Industry Standard (Requires Attention)
"""
        
        if optimization_opportunities:
            for opp in sorted(optimization_opportunities, key=lambda x: x['potential_savings'], reverse=True):
                report += f"""
**{opp['category'].replace('_', ' ').title()}**
- **Current Spend:** ${opp['current_spend']:,.2f}
- **Variance:** {opp['variance']:+.1f}% above industry standard
- **Potential Savings:** ${opp['potential_savings']:,.2f}
- **Recommendation:** Review pricing and negotiate better terms
"""
        else:
            report += "\n✅ All categories are within or below industry standards\n"
        
        # Calculate total potential savings
        total_potential_savings = sum(opp['potential_savings'] for opp in optimization_opportunities)
        
        report += f"""
## 💰 OPTIMIZATION OPPORTUNITIES

### Total Potential Savings
- **From Industry Benchmark Optimization:** ${total_potential_savings:,.2f}
- **Percentage of Total Spend:** {(total_potential_savings/total_spend*100):.1f}%

### Category-Specific Recommendations
"""
        
        for category, data in analysis_results.items():
            variance = data['variance']
            report += f"""
#### {category.replace('_', ' ').title()}
- **Current Assessment:** {self.get_assessment_description(variance['assessment'])}
- **Recommendation:** {self.get_category_recommendation(category, variance['assessment'])}
"""
        
        report += f"""
## 📈 INDUSTRY COMPARISON INSIGHTS

### Vendor Concentration Analysis
"""
        
        for category, data in sorted_categories:
            vendors = data['vendors']
            if len(vendors) == 1:
                report += f"- **{category.replace('_', ' ').title()}:** Single vendor dependency ({vendors[0]})\n"
            elif len(vendors) <= 3:
                report += f"- **{category.replace('_', ' ').title()}:** Limited vendor diversity ({len(vendors)} vendors)\n"
            else:
                report += f"- **{category.replace('_', ' ').title()}:** Good vendor diversity ({len(vendors)} vendors)\n"
        
        report += f"""
## 🎯 ACTIONABLE RECOMMENDATIONS

### Immediate Actions (Next 30 Days)
1. **Focus on above-standard categories** - {len(optimization_opportunities)} categories need attention
2. **Negotiate with high-variance vendors** - Potential savings: ${total_potential_savings:,.2f}
3. **Review vendor contracts** - Identify opportunities for better pricing

### Strategic Actions (Next 90 Days)
1. **Implement vendor diversification** - Reduce single-vendor dependencies
2. **Establish category-specific benchmarks** - Regular industry comparisons
3. **Optimize spending allocation** - Align with industry best practices

### Long-term Strategy (Next 12 Months)
1. **Develop category management** - Dedicated resources for each functional area
2. **Implement automated benchmarking** - Real-time industry comparisons
3. **Strategic vendor partnerships** - Long-term contracts with better terms

---
*Report generated by Industry Benchmark Analysis System*
"""
        
        return report
    
    def get_overall_assessment(self, analysis_results):
        """Get overall assessment of spending vs industry standards."""
        above_standard = sum(1 for result in analysis_results.values() 
                           if result['variance']['assessment'] == 'above_industry_standard')
        below_standard = sum(1 for result in analysis_results.values() 
                           if result['variance']['assessment'] == 'below_industry_standard')
        
        if above_standard > len(analysis_results) / 2:
            return "Above Industry Standards - Optimization Opportunities Available"
        elif below_standard > len(analysis_results) / 2:
            return "Below Industry Standards - Good Cost Management"
        else:
            return "Within Industry Standards - Well Managed"
    
    def get_assessment_description(self, assessment):
        """Get human-readable assessment description."""
        descriptions = {
            'below_industry_standard': '✅ Below Industry Standard (Good)',
            'within_industry_standard': '✅ Within Industry Standard (Good)',
            'above_industry_standard': '⚠️ Above Industry Standard (Needs Attention)',
            'unknown': '❓ Unknown (Needs Investigation)'
        }
        return descriptions.get(assessment, assessment)
    
    def get_category_recommendation(self, category, assessment):
        """Get category-specific recommendations."""
        if assessment == 'above_industry_standard':
            if category == 'it_services':
                return "Negotiate better rates, consider alternative providers, consolidate services"
            elif category == 'development_tools':
                return "Review license utilization, negotiate volume discounts, consider open-source alternatives"
            elif category == 'enterprise_software':
                return "Renegotiate contracts, review user counts, consider cloud alternatives"
            elif category == 'security_software':
                return "Consolidate security tools, negotiate better pricing, review coverage needs"
            elif category == 'cloud_services':
                return "Optimize resource usage, implement cost controls, negotiate reserved instances"
            else:
                return "Review pricing and terms, negotiate better rates"
        elif assessment == 'below_industry_standard':
            return "Maintain current cost management practices"
        else:
            return "Continue monitoring and optimize where possible"

def main():
    """Generate industry benchmark analysis report."""
    
    # Load the data
    data_file = "reports/processed_licensing_data.json"
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} records for industry benchmark analysis")
    
    # Initialize analyzer
    analyzer = IndustryBenchmarkAnalyzer()
    
    # Perform analysis
    print("🔍 Analyzing industry benchmarks...")
    analysis_results, categorized_spend = analyzer.analyze_industry_comparison(data)
    
    # Generate report
    print("📊 Generating industry comparison report...")
    report = analyzer.generate_industry_comparison_report(analysis_results, categorized_spend)
    
    # Save report
    reports_dir = "reports/executive"
    os.makedirs(reports_dir, exist_ok=True)
    
    output_file = f"{reports_dir}/industry_benchmark_analysis_{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Industry benchmark report saved to: {output_file}")
    
    # Print summary
    total_spend = sum(result['total_spend'] for result in analysis_results.values())
    above_standard = sum(1 for result in analysis_results.values() 
                        if result['variance']['assessment'] == 'above_industry_standard')
    
    print(f"\n📊 Analysis Summary:")
    print(f"   - Total Spend: ${total_spend:,.2f}")
    print(f"   - Categories Analyzed: {len(analysis_results)}")
    print(f"   - Categories Above Industry Standard: {above_standard}")
    print(f"   - Categories Within/Below Standard: {len(analysis_results) - above_standard}")
    
    # Show category breakdown
    print(f"\n🏢 Spending by Category:")
    for category, data in sorted(analysis_results.items(), key=lambda x: x[1]['total_spend'], reverse=True):
        print(f"   - {category.replace('_', ' ').title()}: ${data['total_spend']:,.2f} ({data['percentage_of_total']:.1f}%)")

if __name__ == "__main__":
    main() 