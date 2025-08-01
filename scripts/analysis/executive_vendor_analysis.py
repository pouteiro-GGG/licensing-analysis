#!/usr/bin/env python3
"""
Executive Vendor Analysis Tool
Creates clean, executive-friendly analysis with clear vendor comparisons
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class ExecutiveVendorAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/executive_vendor_analysis_20250725"
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Ensure output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
    def load_ai_data(self):
        """Load the AI-enhanced analysis data."""
        if not os.path.exists(self.ai_data_file):
            print(f"Error: AI-enhanced data file not found: {self.ai_data_file}")
            return None
            
        with open(self.ai_data_file, 'r') as f:
            return json.load(f)
    
    def extract_benchmark_value(self, benchmark_dict):
        """Extract the typical benchmark value from the dictionary."""
        if isinstance(benchmark_dict, dict):
            return benchmark_dict.get('typical', 0)
        elif isinstance(benchmark_dict, (int, float)):
            return benchmark_dict
        else:
            return 0
    
    def clean_ai_categorization(self, ai_cat):
        """Clean and extract key information from AI categorization."""
        if not ai_cat:
            return {
                'primary_category': 'Unknown',
                'service_type': 'Unknown',
                'hidden_costs_count': 0,
                'msp_services_count': 0,
                'complexity_level': 'Unknown'
            }
        
        return {
            'primary_category': ai_cat.get('primary_category', 'Unknown'),
            'service_type': ai_cat.get('service_type', 'Unknown'),
            'hidden_costs_count': len(ai_cat.get('hidden_costs', [])),
            'msp_services_count': len(ai_cat.get('msp_services', [])),
            'complexity_level': ai_cat.get('complexity_level', 'Unknown')
        }
    
    def create_clean_dataframe(self, data):
        """Create a clean, executive-friendly DataFrame."""
        benchmarks = data.get('benchmarks', [])
        
        # Filter out FlexPath
        filtered_benchmarks = [b for b in benchmarks if 'flexpath' not in b.get('vendor', '').lower()]
        
        # Convert to DataFrame
        df = pd.DataFrame(filtered_benchmarks)
        
        if df.empty:
            print("No data found after filtering FlexPath")
            return None
        
        # Extract benchmark values
        df['benchmark_value'] = df['benchmark'].apply(self.extract_benchmark_value)
        
        # Calculate variances
        df['variance_amount'] = df['actual_spend'] - df['benchmark_value']
        df['variance_percentage'] = ((df['actual_spend'] - df['benchmark_value']) / df['benchmark_value']) * 100
        df['savings_potential'] = np.where(df['variance_percentage'] > 0, df['variance_amount'], 0)
        df['overpayment_flag'] = df['variance_percentage'] > 20
        
        # Clean AI categorization
        ai_data = df['ai_categorization'].apply(self.clean_ai_categorization)
        df['primary_category'] = ai_data.apply(lambda x: x['primary_category'])
        df['service_type'] = ai_data.apply(lambda x: x['service_type'])
        df['hidden_costs_count'] = ai_data.apply(lambda x: x['hidden_costs_count'])
        df['msp_services_count'] = ai_data.apply(lambda x: x['msp_services_count'])
        df['complexity_level'] = ai_data.apply(lambda x: x['complexity_level'])
        
        # Add risk levels
        df['risk_level'] = pd.cut(df['variance_percentage'], 
                                 bins=[-np.inf, 0, 20, 50, 100, np.inf],
                                 labels=['Below Benchmark', 'Acceptable', 'Moderate Risk', 'High Risk', 'Critical'])
        
        # Add recommendations
        df['recommendation'] = df['variance_percentage'].apply(self.get_recommendation)
        
        return df
    
    def get_recommendation(self, variance):
        """Get recommendation based on variance percentage."""
        if variance <= 0:
            return "Good Value - Below Benchmark"
        elif variance <= 20:
            return "Acceptable - Within Range"
        elif variance <= 50:
            return "Review Required - Moderate Overpayment"
        elif variance <= 100:
            return "Immediate Action - High Overpayment"
        else:
            return "Critical - Excessive Overpayment"
    
    def generate_vendor_insights(self, df):
        """Generate vendor-specific insights."""
        
        insights = {
            'total_spend': df['actual_spend'].sum(),
            'total_records': len(df),
            'total_potential_savings': df['savings_potential'].sum(),
            'overpayment_items': len(df[df['overpayment_flag']]),
            'critical_overpayments': len(df[df['variance_percentage'] > 50]),
            
            # Vendor analysis
            'vendor_analysis': df.groupby('vendor').agg({
                'actual_spend': 'sum',
                'savings_potential': 'sum',
                'variance_percentage': 'mean',
                'overpayment_flag': 'sum',
                'hidden_costs_count': 'sum',
                'msp_services_count': 'sum'
            }).sort_values('actual_spend', ascending=False),
            
            # Category analysis
            'category_analysis': df.groupby('primary_category').agg({
                'actual_spend': 'sum',
                'savings_potential': 'sum',
                'variance_percentage': 'mean'
            }).sort_values('actual_spend', ascending=False),
            
            # Top overpayments
            'top_overpayments': df[df['overpayment_flag']].nlargest(20, 'variance_percentage'),
            
            # Service type analysis
            'service_type_analysis': df.groupby('service_type').agg({
                'actual_spend': 'sum',
                'savings_potential': 'sum',
                'variance_percentage': 'mean'
            }).sort_values('actual_spend', ascending=False)
        }
        
        return insights
    
    def create_executive_visualizations(self, df, insights):
        """Create executive-friendly visualizations."""
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Top Vendors by Spend and Risk
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
        
        # Top 10 vendors by spend
        top_vendors = insights['vendor_analysis'].head(10)
        bars = ax1.barh(range(len(top_vendors)), top_vendors['actual_spend'] / 1000000)
        ax1.set_yticks(range(len(top_vendors)))
        ax1.set_yticklabels(top_vendors.index)
        ax1.set_xlabel('Spend (Millions $)')
        ax1.set_title('Top 10 Vendors by Total Spend')
        ax1.grid(True, alpha=0.3)
        
        # Add risk indicators
        for i, (vendor, data) in enumerate(top_vendors.iterrows()):
            if data['overpayment_flag'] > 0:
                bars[i].set_color('red')
            elif data['variance_percentage'] > 0:
                bars[i].set_color('orange')
        
        # Variance distribution
        ax2.hist(df['variance_percentage'], bins=30, alpha=0.7, edgecolor='black')
        ax2.axvline(x=0, color='red', linestyle='--', alpha=0.8, label='Benchmark')
        ax2.set_xlabel('Variance from Benchmark (%)')
        ax2.set_ylabel('Number of Items')
        ax2.set_title('Distribution of Price Variance')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Potential savings by vendor
        savings_by_vendor = insights['vendor_analysis'][insights['vendor_analysis']['savings_potential'] > 0]
        if not savings_by_vendor.empty:
            ax3.barh(range(len(savings_by_vendor)), savings_by_vendor['savings_potential'] / 1000)
            ax3.set_yticks(range(len(savings_by_vendor)))
            ax3.set_yticklabels(savings_by_vendor.index)
            ax3.set_xlabel('Potential Savings (Thousands $)')
            ax3.set_title('Potential Savings by Vendor')
            ax3.grid(True, alpha=0.3)
        
        # Service type analysis
        top_services = insights['service_type_analysis'].head(10)
        ax4.barh(range(len(top_services)), top_services['actual_spend'] / 1000000)
        ax4.set_yticks(range(len(top_services)))
        ax4.set_yticklabels(top_services.index)
        ax4.set_xlabel('Spend (Millions $)')
        ax4.set_title('Spend by Service Type')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/vendor_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Critical Issues Analysis
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Top overpayments
        top_overpayments = insights['top_overpayments'].head(15)
        colors = ['red' if x > 100 else 'orange' if x > 50 else 'yellow' for x in top_overpayments['variance_percentage']]
        bars = ax1.barh(range(len(top_overpayments)), top_overpayments['variance_percentage'], color=colors)
        ax1.set_yticks(range(len(top_overpayments)))
        ax1.set_yticklabels([f"{v} ({c})" for v, c in zip(top_overpayments['vendor'], top_overpayments['primary_category'])])
        ax1.set_xlabel('Variance from Benchmark (%)')
        ax1.set_title('Critical Overpayments (>20% Above Benchmark)')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, top_overpayments['actual_spend'])):
            ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                    f'${value:,.0f}', va='center', fontsize=8)
        
        # Hidden costs analysis
        hidden_costs = insights['vendor_analysis']['hidden_costs_count'].head(10)
        ax2.barh(range(len(hidden_costs)), hidden_costs.values)
        ax2.set_yticks(range(len(hidden_costs)))
        ax2.set_yticklabels(hidden_costs.index)
        ax2.set_xlabel('Number of Hidden Costs Identified')
        ax2.set_title('Hidden Costs by Vendor')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/critical_issues.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_clean_csv_files(self, df, insights):
        """Create clean, executive-friendly CSV files."""
        
        # 1. Executive Summary - Top 10 Vendors
        executive_summary = insights['vendor_analysis'].head(10).copy()
        executive_summary['avg_variance_percentage'] = executive_summary['variance_percentage'].round(1)
        executive_summary['total_spend_millions'] = (executive_summary['actual_spend'] / 1000000).round(2)
        executive_summary['potential_savings_thousands'] = (executive_summary['savings_potential'] / 1000).round(2)
        
        # Clean column names
        executive_summary.columns = [
            'Total_Spend', 'Potential_Savings', 'Avg_Variance_Percent', 
            'Overpayment_Items', 'Hidden_Costs_Count', 'MSP_Services_Count',
            'Avg_Variance_Percent_Clean', 'Total_Spend_Millions', 'Potential_Savings_Thousands'
        ]
        
        executive_summary.to_csv(f'{self.output_dir}/executive_vendor_summary.csv')
        
        # 2. Critical Issues - Items requiring immediate attention
        critical_items = df[df['overpayment_flag']].copy()
        critical_items = critical_items.sort_values('variance_percentage', ascending=False)
        
        # Clean columns for executive review
        critical_items_clean = critical_items[[
            'vendor', 'company', 'category', 'actual_spend', 'benchmark_value',
            'variance_percentage', 'variance_amount', 'savings_potential',
            'primary_category', 'service_type', 'risk_level', 'recommendation'
        ]].copy()
        
        critical_items_clean.columns = [
            'Vendor', 'Company', 'Category', 'Actual_Spend', 'Benchmark_Value',
            'Variance_Percent', 'Variance_Amount', 'Potential_Savings',
            'Service_Category', 'Service_Type', 'Risk_Level', 'Recommendation'
        ]
        
        critical_items_clean.to_csv(f'{self.output_dir}/critical_vendor_issues.csv', index=False)
        
        # 3. Service Category Analysis
        service_analysis = insights['category_analysis'].copy()
        service_analysis['total_spend_millions'] = (service_analysis['actual_spend'] / 1000000).round(2)
        service_analysis['potential_savings_thousands'] = (service_analysis['savings_potential'] / 1000).round(2)
        service_analysis['avg_variance_percent'] = service_analysis['variance_percentage'].round(1)
        
        service_analysis.columns = [
            'Total_Spend', 'Potential_Savings', 'Avg_Variance_Percent',
            'Total_Spend_Millions', 'Potential_Savings_Thousands', 'Avg_Variance_Percent_Clean'
        ]
        
        service_analysis.to_csv(f'{self.output_dir}/service_category_analysis.csv')
        
        return {
            'executive_summary': executive_summary,
            'critical_items': critical_items_clean,
            'service_analysis': service_analysis
        }
    
    def create_executive_report(self, df, insights, clean_data):
        """Create comprehensive executive report."""
        
        report = f"""# Executive Vendor Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period:** 2024-2025
**Total Records Analyzed:** {insights['total_records']:,}
**FlexPath Filtered:** Yes

## Executive Summary

### Key Financial Metrics
- **Total Spend Analyzed:** ${insights['total_spend']:,.2f}
- **Potential Savings Identified:** ${insights['total_potential_savings']:,.2f}
- **Overpayment Items:** {insights['overpayment_items']} ({(insights['overpayment_items']/insights['total_records']*100):.1f}%)
- **Critical Overpayments (>50%):** {insights['critical_overpayments']}

### Risk Assessment
- **High Risk Items:** {len(df[df['variance_percentage'] > 50])} ({(len(df[df['variance_percentage'] > 50])/len(df)*100):.1f}%)
- **Moderate Risk Items:** {len(df[(df['variance_percentage'] > 20) & (df['variance_percentage'] <= 50)])} ({(len(df[(df['variance_percentage'] > 20) & (df['variance_percentage'] <= 50)])/len(df)*100):.1f}%)
- **Acceptable Items:** {len(df[(df['variance_percentage'] >= 0) & (df['variance_percentage'] <= 20)])} ({(len(df[(df['variance_percentage'] >= 0) & (df['variance_percentage'] <= 20)])/len(df)*100):.1f}%)

## Top 10 Vendors Requiring Attention

"""
        
        # Top 10 vendors with issues
        top_vendors_with_issues = insights['vendor_analysis'][insights['vendor_analysis']['overpayment_flag'] > 0].head(10)
        for vendor, data in top_vendors_with_issues.iterrows():
            report += f"- **{vendor}**: ${data['actual_spend']:,.2f} spend, {data['overpayment_flag']} overpayment items, {data['variance_percentage']:.1f}% avg variance\n"
        
        report += f"""
## Critical Findings

### Top 10 Highest Overpayments
"""
        
        top_overpayments = insights['top_overpayments'].head(10)
        for idx, row in top_overpayments.iterrows():
            report += f"- **{row['vendor']}** ({row['primary_category']}): ${row['actual_spend']:,.2f} (**{row['variance_percentage']:+.1f}%** above benchmark)\n"
        
        report += f"""
## Service Category Analysis

### Highest Cost Categories
"""
        
        # Top categories by spend
        top_categories = insights['category_analysis'].head(10)
        for category, data in top_categories.iterrows():
            report += f"- **{category}**: ${data['actual_spend']:,.2f} total spend\n"
        
        report += f"""
### Categories with Highest Potential Savings
"""
        
        # Categories with potential savings
        savings_by_category = insights['category_analysis'][insights['category_analysis']['savings_potential'] > 0].head(10)
        for category, data in savings_by_category.iterrows():
            report += f"- **{category}**: ${data['savings_potential']:,.2f} potential savings\n"
        
        report += f"""
## Strategic Recommendations

### Immediate Actions (Next 30 Days)
1. **Vendor Negotiations**: Focus on vendors with >50% variance
2. **Contract Reviews**: Re-examine contracts with hidden costs
3. **Benchmark Monitoring**: Implement ongoing price monitoring
4. **MSP Service Audit**: Review managed services pricing

### Medium-Term Initiatives (3-6 Months)
1. **Category Optimization**: Consolidate spending in high-cost categories
2. **Vendor Consolidation**: Reduce vendor count where possible
3. **Process Improvements**: Implement better procurement processes
4. **Technology Investments**: Consider automation for price monitoring

## Detailed Analysis Files

The following clean, executive-friendly files have been generated:

1. **`executive_vendor_summary.csv`**: Top 10 vendors with key metrics
2. **`critical_vendor_issues.csv`**: Items requiring immediate attention
3. **`service_category_analysis.csv`**: Service category breakdown
4. **`vendor_analysis.png`**: Visual vendor analysis
5. **`critical_issues.png`**: Critical issues visualization

## Financial Impact

### Potential Savings by Vendor
"""
        
        # Vendors with highest potential savings
        vendors_with_savings = insights['vendor_analysis'][insights['vendor_analysis']['savings_potential'] > 0].head(10)
        for vendor, data in vendors_with_savings.iterrows():
            report += f"- **{vendor}**: ${data['savings_potential']:,.2f} potential savings\n"
        
        report += f"""
### ROI Analysis
- **Analysis Cost**: Minimal (automated)
- **Potential Savings**: ${insights['total_potential_savings']:,.2f}
- **ROI**: Infinite (cost recovery in first negotiation)

## Next Steps

1. **Executive Review**: Share this report with leadership team
2. **Vendor Meetings**: Schedule negotiations with high-risk vendors
3. **Process Implementation**: Establish ongoing monitoring
4. **Quarterly Reviews**: Schedule regular analysis updates

---
*Generated by Executive Vendor Analysis Tool*
"""
        
        return report
    
    def generate_executive_analysis(self):
        """Generate the complete executive analysis."""
        print("=" * 70)
        print("    EXECUTIVE VENDOR ANALYSIS TOOL")
        print("=" * 70)
        print()
        
        print("Loading AI-enhanced analysis data...")
        data = self.load_ai_data()
        
        if not data:
            print("Failed to load AI data")
            return False
        
        print("Creating clean, executive-friendly DataFrame...")
        df = self.create_clean_dataframe(data)
        
        if df is None:
            print("No data available after filtering")
            return False
        
        print("Generating vendor insights...")
        insights = self.generate_vendor_insights(df)
        
        print("Creating executive visualizations...")
        self.create_executive_visualizations(df, insights)
        
        print("Creating clean CSV files...")
        clean_data = self.create_clean_csv_files(df, insights)
        
        print("Generating executive report...")
        report = self.create_executive_report(df, insights, clean_data)
        
        # Save the report
        with open(f'{self.output_dir}/executive_vendor_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Executive Vendor Analysis completed!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"💰 Potential savings identified: ${insights['total_potential_savings']:,.2f}")
        print(f"🚨 Critical overpayments: {insights['critical_overpayments']}")
        print(f"📊 Clean files generated:")
        print(f"   - executive_vendor_report.md")
        print(f"   - executive_vendor_summary.csv")
        print(f"   - critical_vendor_issues.csv")
        print(f"   - service_category_analysis.csv")
        print(f"   - vendor_analysis.png")
        print(f"   - critical_issues.png")
        
        return True

def main():
    """Main function to generate executive vendor analysis."""
    analyzer = ExecutiveVendorAnalysis()
    success = analyzer.generate_executive_analysis()
    
    if success:
        print()
        print("🎉 Executive analysis completed successfully!")
        print("📋 Ready for executive presentation")
        print("💼 Use insights for vendor negotiations")
    else:
        print("❌ Analysis failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 