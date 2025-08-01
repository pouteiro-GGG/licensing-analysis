#!/usr/bin/env python3
"""
Corrected Synoptek Analysis Tool
Focuses on actual overpayment issues and potential double-paying scenarios
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

class CorrectedSynoptekAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/corrected_synoptek_analysis_20250725"
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
    
    def create_corrected_analysis(self, data):
        """Create corrected analysis focusing on actual overpayment issues."""
        benchmarks = data.get('benchmarks', [])
        
        # Filter for Synoptek records
        synoptek_records = [b for b in benchmarks if b.get('vendor', '').lower() == 'synoptek']
        
        # Create DataFrame
        df = pd.DataFrame(synoptek_records)
        
        if df.empty:
            print("No Synoptek records found in the dataset.")
            return None
        
        # Focus on actual costs and identify potential issues
        df['actual_cost'] = df['actual_spend']
        df['subcategory'] = df['subcategory'].fillna('Unknown')
        df['category'] = df['category'].fillna('Unknown')
        
        # Extract service information
        df['service_type'] = df['ai_categorization'].apply(
            lambda x: x.get('service_type', 'Unknown') if isinstance(x, dict) else 'Unknown'
        )
        
        df['primary_category'] = df['ai_categorization'].apply(
            lambda x: x.get('primary_category', 'Unknown') if isinstance(x, dict) else 'Unknown'
        )
        
        # Identify potential duplicate services
        df['service_key'] = df['subcategory'] + '_' + df['service_type']
        df['duplicate_flag'] = df.duplicated(subset=['service_key'], keep=False)
        
        # Calculate cost per service type
        df['cost_per_service'] = df['actual_cost']
        
        # Identify high-cost outliers
        cost_mean = df['actual_cost'].mean()
        cost_std = df['actual_cost'].std()
        df['high_cost_outlier'] = df['actual_cost'] > (cost_mean + 2 * cost_std)
        
        # Identify potential overpayments based on service type patterns
        service_avg_costs = df.groupby('service_type')['actual_cost'].mean()
        df['service_avg_cost'] = df['service_type'].map(service_avg_costs)
        df['cost_variance_from_avg'] = df['actual_cost'] - df['service_avg_cost']
        df['cost_variance_pct'] = (df['cost_variance_from_avg'] / df['service_avg_cost']) * 100
        
        # Flag potential overpayments (more than 50% above average for same service type)
        df['potential_overpayment'] = df['cost_variance_pct'] > 50
        
        return df
    
    def analyze_double_paying_scenarios(self, df):
        """Analyze potential double-paying scenarios."""
        
        # Group by service type and subcategory to find duplicates
        duplicate_analysis = df[df['duplicate_flag']].groupby(['service_key', 'service_type', 'subcategory']).agg({
            'actual_cost': ['sum', 'count', 'mean'],
            'vendor': 'first',
            'company': 'first'
        }).reset_index()
        
        duplicate_analysis.columns = ['Service_Key', 'Service_Type', 'Subcategory', 'Total_Cost', 'Duplicate_Count', 'Avg_Cost', 'Vendor', 'Company']
        
        # Calculate potential savings from eliminating duplicates
        duplicate_analysis['Potential_Savings'] = duplicate_analysis['Total_Cost'] - duplicate_analysis['Avg_Cost']
        duplicate_analysis['Savings_Percentage'] = (duplicate_analysis['Potential_Savings'] / duplicate_analysis['Total_Cost']) * 100
        
        return duplicate_analysis
    
    def analyze_high_cost_services(self, df):
        """Analyze high-cost services that may be overpriced."""
        
        # Identify services with unusually high costs
        high_cost_services = df[df['high_cost_outlier']].copy()
        high_cost_services = high_cost_services.sort_values('actual_cost', ascending=False)
        
        # Calculate industry averages for comparison
        service_cost_analysis = df.groupby('service_type').agg({
            'actual_cost': ['mean', 'median', 'std', 'count'],
            'potential_overpayment': 'sum'
        }).round(2)
        
        service_cost_analysis.columns = ['Avg_Cost', 'Median_Cost', 'Std_Cost', 'Service_Count', 'Overpayment_Count']
        service_cost_analysis['Overpayment_Rate'] = (service_cost_analysis['Overpayment_Count'] / service_cost_analysis['Service_Count']) * 100
        
        return high_cost_services, service_cost_analysis
    
    def create_corrected_summary(self, df, duplicate_analysis, high_cost_services, service_cost_analysis):
        """Create corrected summary focusing on actual issues."""
        
        # Overall statistics
        total_cost = df['actual_cost'].sum()
        total_services = len(df)
        duplicate_services = len(df[df['duplicate_flag']])
        potential_overpayments = len(df[df['potential_overpayment']])
        high_cost_outliers = len(df[df['high_cost_outlier']])
        
        # Duplicate analysis
        total_duplicate_cost = duplicate_analysis['Total_Cost'].sum()
        potential_duplicate_savings = duplicate_analysis['Potential_Savings'].sum()
        
        # High cost analysis
        total_high_cost = high_cost_services['actual_cost'].sum() if len(high_cost_services) > 0 else 0
        
        # Service type analysis
        top_service_types = df.groupby('service_type')['actual_cost'].sum().sort_values(ascending=False).head(10)
        
        summary = {
            'total_cost': total_cost,
            'total_services': total_services,
            'duplicate_services': duplicate_services,
            'potential_overpayments': potential_overpayments,
            'high_cost_outliers': high_cost_outliers,
            'total_duplicate_cost': total_duplicate_cost,
            'potential_duplicate_savings': potential_duplicate_savings,
            'total_high_cost': total_high_cost,
            'top_service_types': top_service_types,
            'duplicate_analysis': duplicate_analysis,
            'high_cost_services': high_cost_services,
            'service_cost_analysis': service_cost_analysis
        }
        
        return summary
    
    def create_corrected_visualizations(self, df, summary):
        """Create visualizations focusing on actual issues."""
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Corrected Synoptek Analysis - Actual Overpayment and Double-Paying Issues', fontsize=16, fontweight='bold')
        
        # 1. Service cost distribution
        axes[0, 0].hist(df['actual_cost'], bins=30, alpha=0.7, color='red', edgecolor='black')
        axes[0, 0].set_title('Distribution of Service Costs')
        axes[0, 0].set_xlabel('Service Cost ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Duplicate services analysis
        if len(summary['duplicate_analysis']) > 0:
            duplicate_costs = summary['duplicate_analysis']['Total_Cost'].head(8)
            axes[0, 1].barh(range(len(duplicate_costs)), duplicate_costs.values, color='orange', alpha=0.7)
            axes[0, 1].set_yticks(range(len(duplicate_costs)))
            axes[0, 1].set_yticklabels(duplicate_costs.index, fontsize=6)
            axes[0, 1].set_title('Duplicate Services by Total Cost')
            axes[0, 1].set_xlabel('Total Cost ($)')
        
        # 3. High cost outliers
        if len(summary['high_cost_services']) > 0:
            high_cost_data = summary['high_cost_services']['actual_cost'].head(8)
            axes[0, 2].barh(range(len(high_cost_data)), high_cost_data.values, color='red', alpha=0.7)
            axes[0, 2].set_yticks(range(len(high_cost_data)))
            axes[0, 2].set_yticklabels(summary['high_cost_services']['subcategory'].head(8), fontsize=6)
            axes[0, 2].set_title('High Cost Outliers')
            axes[0, 2].set_xlabel('Cost ($)')
        
        # 4. Service type cost analysis
        top_service_types = summary['top_service_types'].head(8)
        axes[1, 0].barh(range(len(top_service_types)), top_service_types.values, color='lightblue')
        axes[1, 0].set_yticks(range(len(top_service_types)))
        axes[1, 0].set_yticklabels(top_service_types.index, fontsize=8)
        axes[1, 0].set_title('Top Service Types by Cost')
        axes[1, 0].set_xlabel('Total Cost ($)')
        
        # 5. Issue breakdown
        issues = ['Duplicate Services', 'Potential Overpayments', 'High Cost Outliers']
        issue_counts = [summary['duplicate_services'], summary['potential_overpayments'], summary['high_cost_outliers']]
        colors = ['orange', 'red', 'darkred']
        
        axes[1, 1].pie(issue_counts, labels=issues, colors=colors, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Service Issues Breakdown')
        
        # 6. Cost variance analysis
        if len(df) > 0:
            cost_variance = df['cost_variance_pct'].dropna()
            axes[1, 2].hist(cost_variance, bins=20, alpha=0.7, color='purple', edgecolor='black')
            axes[1, 2].axvline(x=50, color='red', linestyle='--', alpha=0.7, label='50% Overpayment Threshold')
            axes[1, 2].set_title('Cost Variance from Service Average (%)')
            axes[1, 2].set_xlabel('Variance Percentage (%)')
            axes[1, 2].set_ylabel('Frequency')
            axes[1, 2].legend()
            axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/corrected_synoptek_analysis_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    def create_corrected_csv_reports(self, df, summary):
        """Create corrected CSV reports focusing on actual issues."""
        
        # 1. All services with issues flagged
        services_with_issues = df.copy()
        services_with_issues['issue_flags'] = services_with_issues.apply(
            lambda row: ';'.join([
                'DUPLICATE' if row['duplicate_flag'] else '',
                'OVERPAYMENT' if row['potential_overpayment'] else '',
                'HIGH_COST' if row['high_cost_outlier'] else ''
            ]).strip(';'), axis=1
        )
        
        services_with_issues = services_with_issues.sort_values('actual_cost', ascending=False)
        services_with_issues.to_csv(f'{self.output_dir}/synoptek_services_with_issues.csv', index=False)
        
        # 2. Duplicate services analysis
        summary['duplicate_analysis'].to_csv(f'{self.output_dir}/synoptek_duplicate_services.csv', index=False)
        
        # 3. High cost services
        if len(summary['high_cost_services']) > 0:
            summary['high_cost_services'].to_csv(f'{self.output_dir}/synoptek_high_cost_services.csv', index=False)
        
        # 4. Service type cost analysis
        summary['service_cost_analysis'].to_csv(f'{self.output_dir}/synoptek_service_cost_analysis.csv', index=False)
        
        # 5. Potential overpayments
        potential_overpayments = df[df['potential_overpayment']].copy()
        potential_overpayments = potential_overpayments.sort_values('cost_variance_pct', ascending=False)
        potential_overpayments.to_csv(f'{self.output_dir}/synoptek_potential_overpayments.csv', index=False)
        
        return {
            'services_with_issues': services_with_issues,
            'duplicate_analysis': summary['duplicate_analysis'],
            'high_cost_services': summary['high_cost_services'],
            'service_cost_analysis': summary['service_cost_analysis'],
            'potential_overpayments': potential_overpayments
        }
    
    def create_corrected_markdown_report(self, df, summary, csv_reports):
        """Create corrected markdown report focusing on actual issues."""
        
        report = f"""# Corrected Synoptek Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Focus:** Actual Overpayment Issues and Double-Paying Scenarios

## ⚠️ Critical Issues Identified

### **Overall Service Analysis**
- **Total Services:** {summary['total_services']}
- **Total Cost:** ${summary['total_cost']:,.2f}
- **Duplicate Services:** {summary['duplicate_services']}
- **Potential Overpayments:** {summary['potential_overpayments']}
- **High Cost Outliers:** {summary['high_cost_outliers']}

## 🔴 Double-Paying Scenarios

### **Duplicate Services Analysis**
- **Total Duplicate Cost:** ${summary['total_duplicate_cost']:,.2f}
- **Potential Savings from Eliminating Duplicates:** ${summary['potential_duplicate_savings']:,.2f}
- **Duplicate Services Found:** {summary['duplicate_services']}

### **Top Duplicate Service Groups**
"""
        
        # Add duplicate service analysis
        duplicate_data = summary['duplicate_analysis']
        for idx, row in duplicate_data.head(10).iterrows():
            report += f"""
**{row['Service_Type']} - {row['Subcategory']}:**
- **Total Cost:** ${row['Total_Cost']:,.2f}
- **Duplicate Count:** {row['Duplicate_Count']}
- **Average Cost:** ${row['Avg_Cost']:,.2f}
- **Potential Savings:** ${row['Potential_Savings']:,.2f}
- **Savings Percentage:** {row['Savings_Percentage']:.1f}%
"""
        
        report += f"""

## 💰 High Cost Services Analysis

### **High Cost Outliers**
- **Total High Cost Services:** {summary['high_cost_outliers']}
- **Total High Cost Amount:** ${summary['total_high_cost']:,.2f}

### **Top High Cost Services**
"""
        
        # Add high cost services analysis
        high_cost_data = summary['high_cost_services']
        for idx, row in high_cost_data.head(10).iterrows():
            report += f"""
**{row['subcategory']}:**
- **Actual Cost:** ${row['actual_cost']:,.2f}
- **Service Type:** {row['service_type']}
- **Cost Variance from Average:** {row['cost_variance_pct']:.1f}%
"""
        
        report += f"""

## 📊 Service Type Cost Analysis

### **Top Service Types by Total Cost**
"""
        
        # Add service type analysis
        for service_type, cost in summary['top_service_types'].head(10).items():
            service_stats = summary['service_cost_analysis'].loc[service_type]
            report += f"""
**{service_type}:**
- **Total Cost:** ${cost:,.2f}
- **Average Cost:** ${service_stats['Avg_Cost']:,.2f}
- **Service Count:** {service_stats['Service_Count']}
- **Overpayment Rate:** {service_stats['Overpayment_Rate']:.1f}%
"""
        
        report += f"""

## 🎯 Key Findings and Recommendations

### **Immediate Actions Required**
1. **Eliminate Duplicate Services:** Focus on {summary['duplicate_services']} duplicate services
2. **Review High Cost Services:** Investigate {summary['high_cost_outliers']} high-cost outliers
3. **Negotiate Overpayments:** Address {summary['potential_overpayments']} potential overpayments

### **Potential Savings Opportunities**
- **Duplicate Elimination:** ${summary['potential_duplicate_savings']:,.2f}
- **High Cost Optimization:** Review ${summary['total_high_cost']:,.2f} in high-cost services
- **Overpayment Reduction:** Address {summary['potential_overpayments']} overpayment scenarios

### **Strategic Recommendations**
1. **Audit All Services:** Conduct comprehensive service audit
2. **Consolidate Duplicates:** Merge or eliminate duplicate services
3. **Negotiate Pricing:** Use analysis to negotiate better rates
4. **Implement Monitoring:** Regular cost monitoring and alerting

## 📋 Detailed Reports Available

The following detailed CSV reports have been generated:

1. **Services with Issues:** All services flagged with problems
2. **Duplicate Services:** Detailed duplicate service analysis
3. **High Cost Services:** High-cost outlier analysis
4. **Service Cost Analysis:** Service type cost breakdown
5. **Potential Overpayments:** Services identified as overpaying

---
*Generated by Corrected Synoptek Analysis Tool*
"""
        
        return report
    
    def generate_corrected_analysis(self):
        """Generate the complete corrected analysis."""
        print("=" * 70)
        print("    CORRECTED SYNOPTEK ANALYSIS GENERATOR")
        print("=" * 70)
        print()
        
        # Load data
        data = self.load_ai_data()
        if not data:
            return False
        
        print("📊 Creating corrected Synoptek analysis...")
        
        # Create analysis
        df = self.create_corrected_analysis(data)
        if df is None:
            print("❌ No Synoptek records found for analysis!")
            return False
        
        print(f"📋 Found {len(df)} Synoptek service records for analysis")
        
        # Analyze specific issues
        duplicate_analysis = self.analyze_double_paying_scenarios(df)
        high_cost_services, service_cost_analysis = self.analyze_high_cost_services(df)
        
        # Create summary
        summary = self.create_corrected_summary(df, duplicate_analysis, high_cost_services, service_cost_analysis)
        
        # Create visualizations
        print("📈 Generating corrected visualizations...")
        self.create_corrected_visualizations(df, summary)
        
        # Create CSV reports
        print("📋 Creating corrected CSV reports...")
        csv_reports = self.create_corrected_csv_reports(df, summary)
        
        # Create markdown report
        print("📝 Creating corrected analysis report...")
        report = self.create_corrected_markdown_report(df, summary, csv_reports)
        
        with open(f'{self.output_dir}/corrected_synoptek_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Corrected Synoptek analysis generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - corrected_synoptek_analysis_report.md")
        print(f"   - corrected_synoptek_analysis_charts.png")
        print(f"   - synoptek_services_with_issues.csv")
        print(f"   - synoptek_duplicate_services.csv")
        print(f"   - synoptek_high_cost_services.csv")
        print(f"   - synoptek_service_cost_analysis.csv")
        print(f"   - synoptek_potential_overpayments.csv")
        
        return True

def main():
    """Main function to generate corrected Synoptek analysis."""
    analyzer = CorrectedSynoptekAnalysis()
    success = analyzer.generate_corrected_analysis()
    
    if success:
        print()
        print("🎉 Corrected Synoptek analysis completed successfully!")
        print("📋 Ready for actual overpayment and double-paying analysis")
        print("💼 Use CSV reports for detailed issue analysis")
    else:
        print("❌ Analysis generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 