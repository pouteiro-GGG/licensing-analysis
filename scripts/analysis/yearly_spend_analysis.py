#!/usr/bin/env python3
"""
Yearly Spend Analysis Tool
Provides detailed monthly spending trends, percentage increases, and granular reporting
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class YearlySpendAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/yearly_analysis_20250725"
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
    
    def create_yearly_analysis(self, data):
        """Create comprehensive yearly analysis with monthly trends."""
        benchmarks = data.get('benchmarks', [])
        
        # Create DataFrame
        df = pd.DataFrame(benchmarks)
        df['benchmark_value'] = df['benchmark'].apply(self.extract_benchmark_value)
        df['variance_amount'] = df['actual_spend'] - df['benchmark_value']
        df['variance_percentage'] = ((df['actual_spend'] - df['benchmark_value']) / df['benchmark_value']) * 100
        df['savings_potential'] = np.where(df['variance_percentage'] > 0, df['variance_amount'], 0)
        df['overpayment_flag'] = df['variance_percentage'] > 20
        
        # Add month and year columns for time-based analysis
        df['date'] = pd.to_datetime(df.get('date', '2025-01-01'))
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        df['quarter'] = df['date'].dt.quarter
        
        return df
    
    def calculate_monthly_trends(self, df):
        """Calculate monthly spending trends and percentage changes."""
        monthly_data = df.groupby(['year', 'month', 'month_name']).agg({
            'actual_spend': 'sum',
            'benchmark_value': 'sum',
            'variance_amount': 'sum',
            'savings_potential': 'sum'
        }).reset_index()
        
        # Calculate month-over-month percentage changes
        monthly_data['spend_change_pct'] = monthly_data['actual_spend'].pct_change() * 100
        monthly_data['benchmark_change_pct'] = monthly_data['benchmark_value'].pct_change() * 100
        monthly_data['variance_change_pct'] = monthly_data['variance_amount'].pct_change() * 100
        
        # Calculate year-over-year changes
        monthly_data['yoy_spend_change'] = monthly_data.groupby('month')['actual_spend'].pct_change(periods=12) * 100
        
        return monthly_data
    
    def calculate_vendor_trends(self, df):
        """Calculate spending trends by vendor."""
        vendor_trends = df.groupby(['vendor', 'year', 'month']).agg({
            'actual_spend': 'sum',
            'benchmark_value': 'sum',
            'variance_amount': 'sum',
            'savings_potential': 'sum'
        }).reset_index()
        
        # Calculate vendor-specific trends
        vendor_trends['vendor_spend_change'] = vendor_trends.groupby('vendor')['actual_spend'].pct_change() * 100
        vendor_trends['vendor_variance_pct'] = (vendor_trends['variance_amount'] / vendor_trends['benchmark_value']) * 100
        
        return vendor_trends
    
    def calculate_service_category_trends(self, df):
        """Calculate spending trends by service category."""
        # Extract service category from AI categorization
        df['service_category'] = df['ai_categorization'].apply(
            lambda x: x.get('primary_category', 'Unknown') if isinstance(x, dict) else 'Unknown'
        )
        
        category_trends = df.groupby(['service_category', 'year', 'month']).agg({
            'actual_spend': 'sum',
            'benchmark_value': 'sum',
            'variance_amount': 'sum',
            'savings_potential': 'sum'
        }).reset_index()
        
        category_trends['category_spend_change'] = category_trends.groupby('service_category')['actual_spend'].pct_change() * 100
        category_trends['category_variance_pct'] = (category_trends['variance_amount'] / category_trends['benchmark_value']) * 100
        
        return category_trends
    
    def create_yearly_summary(self, df, monthly_trends, vendor_trends, category_trends):
        """Create comprehensive yearly summary."""
        
        # Yearly totals
        yearly_total = df['actual_spend'].sum()
        yearly_benchmark = df['benchmark_value'].sum()
        yearly_variance = df['variance_amount'].sum()
        yearly_savings = df['savings_potential'].sum()
        
        # Monthly averages
        monthly_avg_spend = monthly_trends['actual_spend'].mean()
        monthly_avg_variance = monthly_trends['variance_amount'].mean()
        
        # Growth rates
        total_growth_rate = ((yearly_total - yearly_benchmark) / yearly_benchmark) * 100 if yearly_benchmark > 0 else 0
        
        # Top vendors by spend
        top_vendors = df.groupby('vendor')['actual_spend'].sum().sort_values(ascending=False).head(10)
        
        # Top categories by spend
        df['service_category'] = df['ai_categorization'].apply(
            lambda x: x.get('primary_category', 'Unknown') if isinstance(x, dict) else 'Unknown'
        )
        top_categories = df.groupby('service_category')['actual_spend'].sum().sort_values(ascending=False).head(10)
        
        # Overpayment analysis
        overpayment_vendors = df[df['overpayment_flag']].groupby('vendor')['variance_amount'].sum().sort_values(ascending=False)
        
        summary = {
            'yearly_total': yearly_total,
            'yearly_benchmark': yearly_benchmark,
            'yearly_variance': yearly_variance,
            'yearly_savings': yearly_savings,
            'monthly_avg_spend': monthly_avg_spend,
            'monthly_avg_variance': monthly_avg_variance,
            'total_growth_rate': total_growth_rate,
            'top_vendors': top_vendors,
            'top_categories': top_categories,
            'overpayment_vendors': overpayment_vendors,
            'monthly_trends': monthly_trends,
            'vendor_trends': vendor_trends,
            'category_trends': category_trends
        }
        
        return summary
    
    def create_visualizations(self, summary):
        """Create comprehensive visualizations."""
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Yearly Spend Analysis - Monthly Trends and Vendor Performance', fontsize=16, fontweight='bold')
        
        # 1. Monthly spending trends
        monthly_data = summary['monthly_trends']
        axes[0, 0].plot(monthly_data.index, monthly_data['actual_spend'], marker='o', linewidth=2, label='Actual Spend')
        axes[0, 0].plot(monthly_data.index, monthly_data['benchmark_value'], marker='s', linewidth=2, label='Benchmark')
        axes[0, 0].set_title('Monthly Spending Trends')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel('Spend ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Month-over-month percentage changes
        axes[0, 1].bar(monthly_data.index, monthly_data['spend_change_pct'], alpha=0.7, color='skyblue')
        axes[0, 1].set_title('Month-over-Month Spend Changes (%)')
        axes[0, 1].set_xlabel('Month')
        axes[0, 1].set_ylabel('Percentage Change')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Top vendors by spend
        top_vendors = summary['top_vendors'].head(8)
        axes[0, 2].barh(range(len(top_vendors)), top_vendors.values, color='lightcoral')
        axes[0, 2].set_yticks(range(len(top_vendors)))
        axes[0, 2].set_yticklabels(top_vendors.index, fontsize=8)
        axes[0, 2].set_title('Top Vendors by Spend')
        axes[0, 2].set_xlabel('Spend ($)')
        
        # 4. Variance analysis
        variance_data = monthly_data[['actual_spend', 'benchmark_value', 'variance_amount']]
        variance_data.plot(kind='bar', ax=axes[1, 0], width=0.8)
        axes[1, 0].set_title('Monthly Variance Analysis')
        axes[1, 0].set_xlabel('Month')
        axes[1, 0].set_ylabel('Amount ($)')
        axes[1, 0].legend(['Actual', 'Benchmark', 'Variance'])
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Overpayment analysis
        overpayment_data = summary['overpayment_vendors'].head(8)
        axes[1, 1].barh(range(len(overpayment_data)), overpayment_data.values, color='red', alpha=0.7)
        axes[1, 1].set_yticks(range(len(overpayment_data)))
        axes[1, 1].set_yticklabels(overpayment_data.index, fontsize=8)
        axes[1, 1].set_title('Vendors with Highest Overpayments')
        axes[1, 1].set_xlabel('Overpayment Amount ($)')
        
        # 6. Service category breakdown
        category_data = summary['top_categories'].head(8)
        axes[1, 2].pie(category_data.values, labels=category_data.index, autopct='%1.1f%%', startangle=90)
        axes[1, 2].set_title('Spend by Service Category')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/yearly_analysis_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    def create_detailed_csv_reports(self, df, summary):
        """Create detailed CSV reports for granular analysis."""
        
        # 1. Monthly detailed report
        monthly_detailed = df.groupby(['year', 'month', 'month_name', 'vendor', 'service_category']).agg({
            'actual_spend': 'sum',
            'benchmark_value': 'sum',
            'variance_amount': 'sum',
            'variance_percentage': 'mean',
            'savings_potential': 'sum'
        }).reset_index()
        
        monthly_detailed.to_csv(f'{self.output_dir}/monthly_detailed_analysis.csv', index=False)
        
        # 2. Vendor performance report
        vendor_performance = df.groupby('vendor').agg({
            'actual_spend': 'sum',
            'benchmark_value': 'sum',
            'variance_amount': 'sum',
            'variance_percentage': 'mean',
            'savings_potential': 'sum',
            'overpayment_flag': 'sum'
        }).reset_index()
        
        vendor_performance['total_items'] = df.groupby('vendor').size().reset_index()[0]
        vendor_performance['overpayment_rate'] = (vendor_performance['overpayment_flag'] / vendor_performance['total_items']) * 100
        vendor_performance = vendor_performance.sort_values('actual_spend', ascending=False)
        
        vendor_performance.to_csv(f'{self.output_dir}/vendor_performance_analysis.csv', index=False)
        
        # 3. Service category analysis
        df['service_category'] = df['ai_categorization'].apply(
            lambda x: x.get('primary_category', 'Unknown') if isinstance(x, dict) else 'Unknown'
        )
        
        category_analysis = df.groupby('service_category').agg({
            'actual_spend': 'sum',
            'benchmark_value': 'sum',
            'variance_amount': 'sum',
            'variance_percentage': 'mean',
            'savings_potential': 'sum'
        }).reset_index()
        
        category_analysis['spend_percentage'] = (category_analysis['actual_spend'] / category_analysis['actual_spend'].sum()) * 100
        category_analysis = category_analysis.sort_values('actual_spend', ascending=False)
        
        category_analysis.to_csv(f'{self.output_dir}/service_category_analysis.csv', index=False)
        
        # 4. Quarterly summary
        quarterly_summary = df.groupby(['year', 'quarter']).agg({
            'actual_spend': 'sum',
            'benchmark_value': 'sum',
            'variance_amount': 'sum',
            'savings_potential': 'sum'
        }).reset_index()
        
        quarterly_summary['quarterly_growth'] = quarterly_summary['actual_spend'].pct_change() * 100
        quarterly_summary['quarterly_variance_pct'] = (quarterly_summary['variance_amount'] / quarterly_summary['benchmark_value']) * 100
        
        quarterly_summary.to_csv(f'{self.output_dir}/quarterly_summary.csv', index=False)
        
        return {
            'monthly_detailed': monthly_detailed,
            'vendor_performance': vendor_performance,
            'category_analysis': category_analysis,
            'quarterly_summary': quarterly_summary
        }
    
    def create_markdown_report(self, summary, csv_reports):
        """Create comprehensive markdown report."""
        
        report = f"""# Yearly Spend Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period:** Yearly with Monthly Granularity

## 📊 Executive Summary

### **Total Spend Analysis**
- **Total Actual Spend:** ${summary['yearly_total']:,.2f}
- **Total Benchmark Spend:** ${summary['yearly_benchmark']:,.2f}
- **Total Variance:** ${summary['yearly_variance']:,.2f}
- **Total Savings Potential:** ${summary['yearly_savings']:,.2f}
- **Overall Growth Rate:** {summary['total_growth_rate']:.2f}%

### **Monthly Averages**
- **Average Monthly Spend:** ${summary['monthly_avg_spend']:,.2f}
- **Average Monthly Variance:** ${summary['monthly_avg_variance']:,.2f}

## 📈 Monthly Trends Analysis

### **Spending Patterns**
The analysis reveals the following monthly spending patterns:

"""
        
        # Add monthly trends analysis
        monthly_data = summary['monthly_trends']
        for idx, row in monthly_data.iterrows():
            report += f"""
**{row['month_name']} {row['year']}:**
- **Actual Spend:** ${row['actual_spend']:,.2f}
- **Benchmark:** ${row['benchmark_value']:,.2f}
- **Variance:** ${row['variance_amount']:,.2f}
- **Month-over-Month Change:** {row['spend_change_pct']:.2f}%
"""
        
        report += f"""

## 🏢 Top Vendors Analysis

### **Top 10 Vendors by Spend**
"""
        
        for vendor, spend in summary['top_vendors'].head(10).items():
            report += f"- **{vendor}:** ${spend:,.2f}\n"
        
        report += f"""

### **Vendors with Highest Overpayments**
"""
        
        for vendor, overpayment in summary['overpayment_vendors'].head(10).items():
            report += f"- **{vendor}:** ${overpayment:,.2f} overpayment\n"
        
        report += f"""

## 📋 Service Category Breakdown

### **Top Service Categories by Spend**
"""
        
        for category, spend in summary['top_categories'].head(10).items():
            report += f"- **{category}:** ${spend:,.2f}\n"
        
        report += f"""

## 💰 Savings Opportunities

### **Immediate Savings Potential**
Based on the analysis, the following opportunities exist for immediate cost optimization:

1. **Vendor Negotiations:** Focus on vendors with highest overpayments
2. **Service Optimization:** Review high-spend service categories
3. **Benchmark Alignment:** Align spending with industry benchmarks

### **Long-term Optimization Strategies**
1. **Monthly Monitoring:** Track spending trends monthly
2. **Vendor Performance:** Regular vendor performance reviews
3. **Category Analysis:** Deep dive into high-spend categories

## 📊 Detailed Reports Available

The following detailed CSV reports have been generated for granular analysis:

1. **Monthly Detailed Analysis:** Line-by-line monthly spending breakdown
2. **Vendor Performance Analysis:** Comprehensive vendor performance metrics
3. **Service Category Analysis:** Detailed category spending analysis
4. **Quarterly Summary:** Quarterly trends and growth analysis

## 🎯 Key Insights

### **Growth Trends**
- Overall spending growth rate: {summary['total_growth_rate']:.2f}%
- Average monthly variance: ${summary['monthly_avg_variance']:,.2f}
- Total savings potential: ${summary['yearly_savings']:,.2f}

### **Optimization Opportunities**
- Focus on vendors with highest overpayments
- Review service categories with highest variance
- Implement monthly spending reviews
- Establish vendor performance metrics

---
*Generated by Yearly Spend Analysis Tool*
"""
        
        return report
    
    def generate_yearly_analysis(self):
        """Generate the complete yearly analysis."""
        print("=" * 70)
        print("    YEARLY SPEND ANALYSIS GENERATOR")
        print("=" * 70)
        print()
        
        # Load data
        data = self.load_ai_data()
        if not data:
            return False
        
        print("📊 Creating yearly analysis...")
        
        # Create analysis
        df = self.create_yearly_analysis(data)
        monthly_trends = self.calculate_monthly_trends(df)
        vendor_trends = self.calculate_vendor_trends(df)
        category_trends = self.calculate_service_category_trends(df)
        
        # Create summary
        summary = self.create_yearly_summary(df, monthly_trends, vendor_trends, category_trends)
        
        # Create visualizations
        print("📈 Generating visualizations...")
        self.create_visualizations(summary)
        
        # Create CSV reports
        print("📋 Creating detailed CSV reports...")
        csv_reports = self.create_detailed_csv_reports(df, summary)
        
        # Create markdown report
        print("📝 Creating comprehensive report...")
        report = self.create_markdown_report(summary, csv_reports)
        
        with open(f'{self.output_dir}/yearly_spend_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Yearly analysis generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - yearly_spend_analysis_report.md")
        print(f"   - yearly_analysis_charts.png")
        print(f"   - monthly_detailed_analysis.csv")
        print(f"   - vendor_performance_analysis.csv")
        print(f"   - service_category_analysis.csv")
        print(f"   - quarterly_summary.csv")
        
        return True

def main():
    """Main function to generate yearly spend analysis."""
    analyzer = YearlySpendAnalysis()
    success = analyzer.generate_yearly_analysis()
    
    if success:
        print()
        print("🎉 Yearly analysis completed successfully!")
        print("📋 Ready for detailed spend analysis")
        print("💼 Use CSV reports for granular analysis")
    else:
        print("❌ Analysis generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 