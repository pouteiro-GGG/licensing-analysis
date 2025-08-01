#!/usr/bin/env python3
"""
Synoptek Licensing Analysis Tool
Detailed analysis of Synoptek licensing costs to determine overpayment/underpayment per license
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

class SynoptekLicensingAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/synoptek_licensing_analysis_20250725"
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
    
    def create_synoptek_licensing_analysis(self, data):
        """Create detailed Synoptek licensing analysis."""
        benchmarks = data.get('benchmarks', [])
        
        # Filter for Synoptek records
        synoptek_records = [b for b in benchmarks if b.get('vendor', '').lower() == 'synoptek']
        
        # Create DataFrame
        df = pd.DataFrame(synoptek_records)
        
        if df.empty:
            print("No Synoptek records found in the dataset.")
            return None
        
        df['benchmark_value'] = df['benchmark'].apply(self.extract_benchmark_value)
        df['variance_amount'] = df['actual_spend'] - df['benchmark_value']
        df['variance_percentage'] = ((df['actual_spend'] - df['benchmark_value']) / df['benchmark_value']) * 100
        df['savings_potential'] = np.where(df['variance_percentage'] > 0, df['variance_amount'], 0)
        df['overpayment_flag'] = df['variance_percentage'] > 20
        
        # Extract licensing information from AI categorization
        df['licensing_type'] = df['ai_categorization'].apply(
            lambda x: x.get('service_type', 'Unknown') if isinstance(x, dict) else 'Unknown'
        )
        
        df['license_category'] = df['ai_categorization'].apply(
            lambda x: x.get('primary_category', 'Unknown') if isinstance(x, dict) else 'Unknown'
        )
        
        # Extract subcategory for more granular analysis
        df['subcategory'] = df['subcategory'].fillna('Unknown')
        
        # Create license-specific analysis
        df['per_license_cost'] = df['actual_spend']  # Assuming each record represents a license
        df['per_license_benchmark'] = df['benchmark_value']
        df['per_license_variance'] = df['variance_amount']
        df['per_license_variance_pct'] = df['variance_percentage']
        
        return df
    
    def calculate_licensing_metrics(self, df):
        """Calculate detailed licensing metrics."""
        
        # Overall licensing metrics
        total_licenses = len(df)
        total_license_cost = df['actual_spend'].sum()
        total_license_benchmark = df['benchmark_value'].sum()
        total_license_variance = df['variance_amount'].sum()
        total_savings_potential = df['savings_potential'].sum()
        
        # Per-license averages
        avg_license_cost = df['actual_spend'].mean()
        avg_license_benchmark = df['benchmark_value'].mean()
        avg_license_variance = df['variance_amount'].mean()
        
        # Licensing categories analysis
        category_analysis = df.groupby('license_category').agg({
            'actual_spend': ['sum', 'mean', 'count'],
            'benchmark_value': ['sum', 'mean'],
            'variance_amount': ['sum', 'mean'],
            'variance_percentage': 'mean',
            'savings_potential': 'sum'
        }).round(2)
        
        # Subcategory analysis
        subcategory_analysis = df.groupby('subcategory').agg({
            'actual_spend': ['sum', 'mean', 'count'],
            'benchmark_value': ['sum', 'mean'],
            'variance_amount': ['sum', 'mean'],
            'variance_percentage': 'mean',
            'savings_potential': 'sum'
        }).round(2)
        
        # Overpayment analysis
        overpayment_records = df[df['overpayment_flag']]
        underpayment_records = df[~df['overpayment_flag']]
        
        overpayment_analysis = {
            'total_overpayment_records': len(overpayment_records),
            'total_underpayment_records': len(underpayment_records),
            'overpayment_amount': overpayment_records['variance_amount'].sum(),
            'underpayment_amount': underpayment_records['variance_amount'].sum(),
            'avg_overpayment_per_license': overpayment_records['variance_amount'].mean() if len(overpayment_records) > 0 else 0,
            'avg_underpayment_per_license': underpayment_records['variance_amount'].mean() if len(underpayment_records) > 0 else 0
        }
        
        # Top overpayment licenses
        top_overpayments = df[df['overpayment_flag']].nlargest(10, 'variance_amount')
        
        # Top underpayment licenses
        top_underpayments = df[~df['overpayment_flag']].nsmallest(10, 'variance_amount')
        
        metrics = {
            'total_licenses': total_licenses,
            'total_license_cost': total_license_cost,
            'total_license_benchmark': total_license_benchmark,
            'total_license_variance': total_license_variance,
            'total_savings_potential': total_savings_potential,
            'avg_license_cost': avg_license_cost,
            'avg_license_benchmark': avg_license_benchmark,
            'avg_license_variance': avg_license_variance,
            'category_analysis': category_analysis,
            'subcategory_analysis': subcategory_analysis,
            'overpayment_analysis': overpayment_analysis,
            'top_overpayments': top_overpayments,
            'top_underpayments': top_underpayments
        }
        
        return metrics
    
    def create_licensing_visualizations(self, df, metrics):
        """Create licensing-specific visualizations."""
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Synoptek Licensing Analysis - Per License Cost Analysis', fontsize=16, fontweight='bold')
        
        # 1. License cost distribution
        axes[0, 0].hist(df['actual_spend'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Distribution of License Costs')
        axes[0, 0].set_xlabel('License Cost ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Actual vs Benchmark comparison
        axes[0, 1].scatter(df['benchmark_value'], df['actual_spend'], alpha=0.6, color='red')
        axes[0, 1].plot([0, df['benchmark_value'].max()], [0, df['benchmark_value'].max()], 'k--', alpha=0.5)
        axes[0, 0].set_title('Actual vs Benchmark License Costs')
        axes[0, 1].set_xlabel('Benchmark Cost ($)')
        axes[0, 1].set_ylabel('Actual Cost ($)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Variance percentage distribution
        axes[0, 2].hist(df['variance_percentage'], bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
        axes[0, 2].axvline(x=0, color='red', linestyle='--', alpha=0.7)
        axes[0, 2].set_title('Distribution of License Cost Variance (%)')
        axes[0, 2].set_xlabel('Variance Percentage (%)')
        axes[0, 2].set_ylabel('Frequency')
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Top license categories by cost
        category_costs = df.groupby('license_category')['actual_spend'].sum().sort_values(ascending=False).head(8)
        axes[1, 0].barh(range(len(category_costs)), category_costs.values, color='lightgreen')
        axes[1, 0].set_yticks(range(len(category_costs)))
        axes[1, 0].set_yticklabels(category_costs.index, fontsize=8)
        axes[1, 0].set_title('Top License Categories by Cost')
        axes[1, 0].set_xlabel('Total Cost ($)')
        
        # 5. Overpayment vs Underpayment analysis
        overpayment_count = metrics['overpayment_analysis']['total_overpayment_records']
        underpayment_count = metrics['overpayment_analysis']['total_underpayment_records']
        
        labels = ['Overpaying', 'Underpaying']
        sizes = [overpayment_count, underpayment_count]
        colors = ['red', 'green']
        
        axes[1, 1].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('License Payment Status')
        
        # 6. Top overpayment licenses
        top_overpayments = metrics['top_overpayments'].head(8)
        axes[1, 2].barh(range(len(top_overpayments)), top_overpayments['variance_amount'], color='red', alpha=0.7)
        axes[1, 2].set_yticks(range(len(top_overpayments)))
        axes[1, 2].set_yticklabels(top_overpayments['subcategory'], fontsize=6)
        axes[1, 2].set_title('Top Overpayment Licenses')
        axes[1, 2].set_xlabel('Overpayment Amount ($)')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/synoptek_licensing_analysis_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    def create_detailed_licensing_csv_reports(self, df, metrics):
        """Create detailed CSV reports for licensing analysis."""
        
        # 1. Detailed license analysis
        license_detailed = df[['subcategory', 'license_category', 'actual_spend', 'benchmark_value', 
                              'variance_amount', 'variance_percentage', 'savings_potential', 'overpayment_flag']].copy()
        license_detailed['license_id'] = range(1, len(license_detailed) + 1)
        license_detailed = license_detailed.sort_values('variance_amount', ascending=False)
        
        license_detailed.to_csv(f'{self.output_dir}/synoptek_license_detailed_analysis.csv', index=False)
        
        # 2. Category summary
        category_summary = metrics['category_analysis'].reset_index()
        category_summary.columns = ['License_Category', 'Total_Cost', 'Avg_Cost', 'License_Count', 
                                  'Total_Benchmark', 'Avg_Benchmark', 'Total_Variance', 'Avg_Variance', 
                                  'Avg_Variance_Pct', 'Total_Savings_Potential']
        category_summary.to_csv(f'{self.output_dir}/synoptek_license_category_summary.csv', index=False)
        
        # 3. Subcategory summary
        subcategory_summary = metrics['subcategory_analysis'].reset_index()
        subcategory_summary.columns = ['Subcategory', 'Total_Cost', 'Avg_Cost', 'License_Count', 
                                     'Total_Benchmark', 'Avg_Benchmark', 'Total_Variance', 'Avg_Variance', 
                                     'Avg_Variance_Pct', 'Total_Savings_Potential']
        subcategory_summary.to_csv(f'{self.output_dir}/synoptek_license_subcategory_summary.csv', index=False)
        
        # 4. Overpayment analysis
        overpayment_details = df[df['overpayment_flag']].copy()
        overpayment_details['overpayment_rank'] = overpayment_details['variance_amount'].rank(ascending=False)
        overpayment_details = overpayment_details.sort_values('variance_amount', ascending=False)
        
        overpayment_details.to_csv(f'{self.output_dir}/synoptek_license_overpayments.csv', index=False)
        
        # 5. Underpayment analysis
        underpayment_details = df[~df['overpayment_flag']].copy()
        underpayment_details['underpayment_rank'] = underpayment_details['variance_amount'].rank(ascending=True)
        underpayment_details = underpayment_details.sort_values('variance_amount', ascending=True)
        
        underpayment_details.to_csv(f'{self.output_dir}/synoptek_license_underpayments.csv', index=False)
        
        return {
            'license_detailed': license_detailed,
            'category_summary': category_summary,
            'subcategory_summary': subcategory_summary,
            'overpayment_details': overpayment_details,
            'underpayment_details': underpayment_details
        }
    
    def create_licensing_markdown_report(self, df, metrics, csv_reports):
        """Create comprehensive licensing markdown report."""
        
        report = f"""# Synoptek Licensing Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Focus:** Per-License Cost Analysis and Overpayment/Underpayment Detection

## 📊 Executive Summary

### **Overall Licensing Analysis**
- **Total Licenses Analyzed:** {metrics['total_licenses']}
- **Total License Cost:** ${metrics['total_license_cost']:,.2f}
- **Total Benchmark Cost:** ${metrics['total_license_benchmark']:,.2f}
- **Total Variance:** ${metrics['total_license_variance']:,.2f}
- **Total Savings Potential:** ${metrics['total_savings_potential']:,.2f}

### **Per-License Averages**
- **Average License Cost:** ${metrics['avg_license_cost']:,.2f}
- **Average Benchmark Cost:** ${metrics['avg_license_benchmark']:,.2f}
- **Average Variance per License:** ${metrics['avg_license_variance']:,.2f}

## 💰 Overpayment vs Underpayment Analysis

### **Payment Status Breakdown**
- **Overpaying Licenses:** {metrics['overpayment_analysis']['total_overpayment_records']} licenses
- **Underpaying Licenses:** {metrics['overpayment_analysis']['total_underpayment_records']} licenses
- **Total Overpayment Amount:** ${metrics['overpayment_analysis']['overpayment_amount']:,.2f}
- **Total Underpayment Amount:** ${metrics['overpayment_analysis']['underpayment_amount']:,.2f}
- **Average Overpayment per License:** ${metrics['overpayment_analysis']['avg_overpayment_per_license']:,.2f}
- **Average Underpayment per License:** ${metrics['overpayment_analysis']['avg_underpayment_per_license']:,.2f}

## 🏷️ Top License Categories by Cost

"""
        
        # Add category analysis
        category_data = metrics['category_analysis']
        for category in category_data.index:
            total_cost = category_data.loc[category, ('actual_spend', 'sum')]
            avg_cost = category_data.loc[category, ('actual_spend', 'mean')]
            license_count = category_data.loc[category, ('actual_spend', 'count')]
            avg_variance_pct = category_data.loc[category, ('variance_percentage', 'mean')]
            
            report += f"""
**{category}:**
- **Total Cost:** ${total_cost:,.2f}
- **Average Cost per License:** ${avg_cost:,.2f}
- **Number of Licenses:** {license_count}
- **Average Variance:** {avg_variance_pct:.2f}%
"""
        
        report += f"""

## 🔴 Top Overpayment Licenses

"""
        
        for idx, row in metrics['top_overpayments'].head(10).iterrows():
            report += f"""
**{row['subcategory']}:**
- **Actual Cost:** ${row['actual_spend']:,.2f}
- **Benchmark Cost:** ${row['benchmark_value']:,.2f}
- **Overpayment:** ${row['variance_amount']:,.2f}
- **Variance Percentage:** {row['variance_percentage']:.2f}%
"""
        
        report += f"""

## 🟢 Top Underpayment Licenses

"""
        
        for idx, row in metrics['top_underpayments'].head(10).iterrows():
            report += f"""
**{row['subcategory']}:**
- **Actual Cost:** ${row['actual_spend']:,.2f}
- **Benchmark Cost:** ${row['benchmark_value']:,.2f}
- **Underpayment:** ${row['variance_amount']:,.2f}
- **Variance Percentage:** {row['variance_percentage']:.2f}%
"""
        
        report += f"""

## 📋 License Subcategory Analysis

### **Top Subcategories by Cost**
"""
        
        subcategory_data = metrics['subcategory_analysis']
        for subcategory in subcategory_data.index:
            total_cost = subcategory_data.loc[subcategory, ('actual_spend', 'sum')]
            avg_cost = subcategory_data.loc[subcategory, ('actual_spend', 'mean')]
            license_count = subcategory_data.loc[subcategory, ('actual_spend', 'count')]
            avg_variance_pct = subcategory_data.loc[subcategory, ('variance_percentage', 'mean')]
            
            report += f"""
**{subcategory}:**
- **Total Cost:** ${total_cost:,.2f}
- **Average Cost per License:** ${avg_cost:,.2f}
- **Number of Licenses:** {license_count}
- **Average Variance:** {avg_variance_pct:.2f}%
"""
        
        report += f"""

## 🎯 Key Insights and Recommendations

### **Overpayment Analysis**
1. **Focus Areas:** Target licenses with highest overpayment percentages
2. **Negotiation Opportunities:** Use benchmark data for vendor negotiations
3. **License Optimization:** Consider downgrading or consolidating overpriced licenses

### **Underpayment Analysis**
1. **Value Assessment:** Evaluate if underpayments represent good value
2. **Service Quality:** Ensure underpayments don't compromise service quality
3. **Future Planning:** Consider if underpayments are sustainable long-term

### **Strategic Recommendations**
1. **Immediate Actions:**
   - Review top 10 overpayment licenses for immediate cost reduction
   - Negotiate with Synoptek using benchmark data
   - Consider license consolidation opportunities

2. **Long-term Strategy:**
   - Implement regular license cost reviews
   - Establish license cost benchmarks
   - Monitor license utilization and optimization

## 📊 Detailed Reports Available

The following detailed CSV reports have been generated for granular licensing analysis:

1. **License Detailed Analysis:** Line-by-line license cost breakdown
2. **License Category Summary:** Category-level cost analysis
3. **License Subcategory Summary:** Subcategory-level cost analysis
4. **License Overpayments:** Detailed overpayment analysis
5. **License Underpayments:** Detailed underpayment analysis

---
*Generated by Synoptek Licensing Analysis Tool*
"""
        
        return report
    
    def generate_licensing_analysis(self):
        """Generate the complete Synoptek licensing analysis."""
        print("=" * 70)
        print("    SYNOPTEK LICENSING ANALYSIS GENERATOR")
        print("=" * 70)
        print()
        
        # Load data
        data = self.load_ai_data()
        if not data:
            return False
        
        print("📊 Creating Synoptek licensing analysis...")
        
        # Create analysis
        df = self.create_synoptek_licensing_analysis(data)
        if df is None:
            print("❌ No Synoptek records found for analysis!")
            return False
        
        print(f"📋 Found {len(df)} Synoptek license records for analysis")
        
        # Calculate metrics
        metrics = self.calculate_licensing_metrics(df)
        
        # Create visualizations
        print("📈 Generating licensing visualizations...")
        self.create_licensing_visualizations(df, metrics)
        
        # Create CSV reports
        print("📋 Creating detailed licensing CSV reports...")
        csv_reports = self.create_detailed_licensing_csv_reports(df, metrics)
        
        # Create markdown report
        print("📝 Creating comprehensive licensing report...")
        report = self.create_licensing_markdown_report(df, metrics, csv_reports)
        
        with open(f'{self.output_dir}/synoptek_licensing_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Synoptek licensing analysis generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - synoptek_licensing_analysis_report.md")
        print(f"   - synoptek_licensing_analysis_charts.png")
        print(f"   - synoptek_license_detailed_analysis.csv")
        print(f"   - synoptek_license_category_summary.csv")
        print(f"   - synoptek_license_subcategory_summary.csv")
        print(f"   - synoptek_license_overpayments.csv")
        print(f"   - synoptek_license_underpayments.csv")
        
        return True

def main():
    """Main function to generate Synoptek licensing analysis."""
    analyzer = SynoptekLicensingAnalysis()
    success = analyzer.generate_licensing_analysis()
    
    if success:
        print()
        print("🎉 Synoptek licensing analysis completed successfully!")
        print("📋 Ready for detailed licensing analysis")
        print("💼 Use CSV reports for granular license cost analysis")
    else:
        print("❌ Analysis generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 