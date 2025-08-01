#!/usr/bin/env python3
"""
Comprehensive Executive Analysis Tool
Generates visually stunning, data-driven reports for executive decision-making
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

class ComprehensiveExecutiveAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/comprehensive_analysis_20250725"
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
    
    def create_dataframe_analysis(self, data):
        """Create comprehensive DataFrame analysis."""
        benchmarks = data.get('benchmarks', [])
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(benchmarks)
        
        # Extract benchmark values from dictionary
        df['benchmark_value'] = df['benchmark'].apply(self.extract_benchmark_value)
        
        # Add calculated columns
        df['variance_amount'] = df['actual_spend'] - df['benchmark_value']
        df['variance_percentage'] = ((df['actual_spend'] - df['benchmark_value']) / df['benchmark_value']) * 100
        df['savings_potential'] = np.where(df['variance_percentage'] > 0, df['variance_amount'], 0)
        df['overpayment_flag'] = df['variance_percentage'] > 20  # Flag items 20%+ above benchmark
        
        # Extract AI categorization data
        df['primary_category'] = df['ai_categorization'].apply(
            lambda x: x.get('primary_category', 'Unknown') if x else 'Unknown'
        )
        df['hidden_costs_count'] = df['ai_categorization'].apply(
            lambda x: len(x.get('hidden_costs', [])) if x else 0
        )
        df['msp_services_count'] = df['ai_categorization'].apply(
            lambda x: len(x.get('msp_services', [])) if x else 0
        )
        
        return df
    
    def generate_executive_insights(self, df):
        """Generate comprehensive executive insights."""
        
        insights = {
            'total_spend': df['actual_spend'].sum(),
            'total_records': len(df),
            'total_potential_savings': df['savings_potential'].sum(),
            'overpayment_items': len(df[df['overpayment_flag']]),
            'critical_overpayments': len(df[df['variance_percentage'] > 50]),
            'vendor_analysis': df.groupby('vendor').agg({
                'actual_spend': 'sum',
                'savings_potential': 'sum',
                'variance_percentage': 'mean',
                'overpayment_flag': 'sum'
            }).sort_values('actual_spend', ascending=False),
            'category_analysis': df.groupby('primary_category').agg({
                'actual_spend': 'sum',
                'savings_potential': 'sum',
                'variance_percentage': 'mean'
            }).sort_values('actual_spend', ascending=False),
            'top_overpayments': df[df['overpayment_flag']].nlargest(20, 'variance_percentage'),
            'hidden_costs_summary': df.groupby('vendor')['hidden_costs_count'].sum().sort_values(ascending=False),
            'msp_services_summary': df.groupby('vendor')['msp_services_count'].sum().sort_values(ascending=False)
        }
        
        return insights
    
    def create_visualizations(self, df, insights):
        """Create comprehensive visualizations."""
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Spend Distribution by Vendor
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
        
        # Top 10 vendors by spend
        top_vendors = insights['vendor_analysis'].head(10)
        ax1.barh(range(len(top_vendors)), top_vendors['actual_spend'] / 1000000)
        ax1.set_yticks(range(len(top_vendors)))
        ax1.set_yticklabels(top_vendors.index)
        ax1.set_xlabel('Spend (Millions $)')
        ax1.set_title('Top 10 Vendors by Total Spend')
        ax1.grid(True, alpha=0.3)
        
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
        
        # Category analysis
        top_categories = insights['category_analysis'].head(10)
        ax4.barh(range(len(top_categories)), top_categories['actual_spend'] / 1000000)
        ax4.set_yticks(range(len(top_categories)))
        ax4.set_yticklabels(top_categories.index)
        ax4.set_xlabel('Spend (Millions $)')
        ax4.set_title('Spend by Service Category')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/spend_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Critical Overpayments Analysis
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
        hidden_costs = insights['hidden_costs_summary'].head(10)
        ax2.barh(range(len(hidden_costs)), hidden_costs.values)
        ax2.set_yticks(range(len(hidden_costs)))
        ax2.set_yticklabels(hidden_costs.index)
        ax2.set_xlabel('Number of Hidden Costs Identified')
        ax2.set_title('Hidden Costs by Vendor')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/critical_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Detailed Line-by-Line Analysis
        self.create_detailed_analysis_table(df, insights)
    
    def create_detailed_analysis_table(self, df, insights):
        """Create detailed line-by-line analysis table."""
        
        # Create detailed analysis DataFrame
        detailed_df = df.copy()
        detailed_df['risk_level'] = pd.cut(detailed_df['variance_percentage'], 
                                         bins=[-np.inf, 0, 20, 50, 100, np.inf],
                                         labels=['Below Benchmark', 'Acceptable', 'Moderate Risk', 'High Risk', 'Critical'])
        
        # Add recommendations
        detailed_df['recommendation'] = detailed_df['variance_percentage'].apply(self.get_recommendation)
        
        # Save detailed analysis
        detailed_df.to_csv(f'{self.output_dir}/detailed_line_analysis.csv', index=False)
        
        # Create summary table for executive review
        executive_summary = detailed_df[detailed_df['overpayment_flag']].copy()
        executive_summary = executive_summary.sort_values('variance_percentage', ascending=False)
        executive_summary.to_csv(f'{self.output_dir}/executive_priority_items.csv', index=False)
        
        return detailed_df
    
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
    
    def create_executive_report(self, df, insights):
        """Create comprehensive executive report."""
        
        report = f"""# Comprehensive Executive Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period:** 2024-2025
**Total Records Analyzed:** {insights['total_records']:,}

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

## Critical Findings

### Top 10 Highest Overpayments
"""
        
        top_overpayments = insights['top_overpayments'].head(10)
        for idx, row in top_overpayments.iterrows():
            report += f"- **{row['vendor']}** ({row['primary_category']}): ${row['actual_spend']:,.2f} (**{row['variance_percentage']:+.1f}%** above benchmark)\n"
        
        report += f"""
### Vendor Risk Analysis
"""
        
        # Vendors with highest risk
        high_risk_vendors = insights['vendor_analysis'][insights['vendor_analysis']['overpayment_flag'] > 0].head(10)
        for vendor, data in high_risk_vendors.iterrows():
            report += f"- **{vendor}**: ${data['actual_spend']:,.2f} spend, {data['overpayment_flag']} overpayment items, {data['variance_percentage']:.1f}% avg variance\n"
        
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

The following files have been generated for detailed review:

1. **`detailed_line_analysis.csv`**: Complete line-by-line analysis
2. **`executive_priority_items.csv`**: Items requiring immediate attention
3. **`spend_analysis.png`**: Visual spend distribution analysis
4. **`critical_analysis.png`**: Critical overpayments visualization

## Financial Impact

### Potential Savings by Category
"""
        
        # Top categories by potential savings
        savings_by_category = insights['category_analysis'][insights['category_analysis']['savings_potential'] > 0].head(10)
        for category, data in savings_by_category.iterrows():
            report += f"- **{category}**: ${data['savings_potential']:,.2f} potential savings\n"
        
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
*Generated by Comprehensive Executive Analysis Tool*
"""
        
        return report
    
    def generate_comprehensive_report(self):
        """Generate the complete comprehensive analysis."""
        print("=" * 70)
        print("    COMPREHENSIVE EXECUTIVE ANALYSIS TOOL")
        print("=" * 70)
        print()
        
        print("Loading AI-enhanced analysis data...")
        data = self.load_ai_data()
        
        if not data:
            print("Failed to load AI data")
            return False
        
        print("Creating comprehensive DataFrame analysis...")
        df = self.create_dataframe_analysis(data)
        
        print("Generating executive insights...")
        insights = self.generate_executive_insights(df)
        
        print("Creating visualizations...")
        self.create_visualizations(df, insights)
        
        print("Generating executive report...")
        report = self.create_executive_report(df, insights)
        
        # Save the report
        with open(f'{self.output_dir}/comprehensive_executive_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Comprehensive Executive Analysis completed!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"💰 Potential savings identified: ${insights['total_potential_savings']:,.2f}")
        print(f"🚨 Critical overpayments: {insights['critical_overpayments']}")
        print(f"📊 Files generated:")
        print(f"   - comprehensive_executive_report.md")
        print(f"   - detailed_line_analysis.csv")
        print(f"   - executive_priority_items.csv")
        print(f"   - spend_analysis.png")
        print(f"   - critical_analysis.png")
        
        return True

def main():
    """Main function to generate comprehensive executive analysis."""
    analyzer = ComprehensiveExecutiveAnalysis()
    success = analyzer.generate_comprehensive_report()
    
    if success:
        print()
        print("🎉 Analysis completed successfully!")
        print("📋 Ready for executive presentation")
        print("💼 Use insights for vendor negotiations")
    else:
        print("❌ Analysis failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 