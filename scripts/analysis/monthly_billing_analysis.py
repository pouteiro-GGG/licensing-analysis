#!/usr/bin/env python3
"""
Monthly Billing Analysis Tool
Proper analysis accounting for monthly billing cycles and actual overpayment issues
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

class MonthlyBillingAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/monthly_billing_analysis_20250725"
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
    
    def create_monthly_billing_analysis(self, data):
        """Create analysis accounting for monthly billing cycles."""
        benchmarks = data.get('benchmarks', [])
        
        # Filter for Synoptek records
        synoptek_records = [b for b in benchmarks if b.get('vendor', '').lower() == 'synoptek']
        
        # Create DataFrame
        df = pd.DataFrame(synoptek_records)
        
        if df.empty:
            print("No Synoptek records found in the dataset.")
            return None
        
        # Focus on actual costs and service analysis
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
        
        # Create unique service identifiers (not treating monthly billing as duplicates)
        df['service_identifier'] = df['subcategory'] + '_' + df['service_type'] + '_' + df['primary_category']
        
        # Analyze monthly costs by service type
        service_monthly_analysis = df.groupby('service_identifier').agg({
            'actual_cost': ['sum', 'mean', 'count', 'std'],
            'subcategory': 'first',
            'service_type': 'first',
            'primary_category': 'first'
        }).round(2)
        
        service_monthly_analysis.columns = ['Total_Cost', 'Avg_Monthly_Cost', 'Billing_Months', 'Cost_Std_Dev', 
                                         'Subcategory', 'Service_Type', 'Primary_Category']
        
        # Calculate cost variance and identify potential overpayments
        service_monthly_analysis['Cost_Variance'] = service_monthly_analysis['Cost_Std_Dev'] / service_monthly_analysis['Avg_Monthly_Cost']
        service_monthly_analysis['Potential_Overpayment'] = service_monthly_analysis['Cost_Variance'] > 0.5  # 50% variance threshold
        
        # Identify high-cost services
        cost_threshold = service_monthly_analysis['Avg_Monthly_Cost'].quantile(0.9)  # Top 10%
        service_monthly_analysis['High_Cost_Service'] = service_monthly_analysis['Avg_Monthly_Cost'] > cost_threshold
        
        # Calculate annual costs
        service_monthly_analysis['Annual_Cost'] = service_monthly_analysis['Avg_Monthly_Cost'] * 12
        
        return df, service_monthly_analysis
    
    def analyze_billing_patterns(self, df):
        """Analyze billing patterns and identify irregularities."""
        
        # Group by service identifier to analyze billing patterns
        billing_patterns = df.groupby('service_identifier').agg({
            'actual_cost': ['min', 'max', 'mean', 'std', 'count'],
            'subcategory': 'first',
            'service_type': 'first'
        }).round(2)
        
        billing_patterns.columns = ['Min_Cost', 'Max_Cost', 'Avg_Cost', 'Std_Cost', 'Billing_Count', 
                                  'Subcategory', 'Service_Type']
        
        # Calculate billing irregularities
        billing_patterns['Cost_Range'] = billing_patterns['Max_Cost'] - billing_patterns['Min_Cost']
        billing_patterns['Cost_Variance_Pct'] = (billing_patterns['Cost_Range'] / billing_patterns['Avg_Cost']) * 100
        
        # Flag irregular billing (high variance)
        billing_patterns['Irregular_Billing'] = billing_patterns['Cost_Variance_Pct'] > 50
        
        # Identify potential billing errors
        billing_patterns['Potential_Billing_Error'] = (
            (billing_patterns['Cost_Variance_Pct'] > 100) | 
            (billing_patterns['Std_Cost'] > billing_patterns['Avg_Cost'])
        )
        
        return billing_patterns
    
    def analyze_service_cost_efficiency(self, df, service_monthly_analysis):
        """Analyze service cost efficiency and identify optimization opportunities."""
        
        # Calculate cost per service type
        service_efficiency = service_monthly_analysis.groupby('Service_Type').agg({
            'Total_Cost': 'sum',
            'Avg_Monthly_Cost': 'mean',
            'Billing_Months': 'sum',
            'Potential_Overpayment': 'sum',
            'High_Cost_Service': 'sum'
        }).round(2)
        
        service_efficiency['Service_Count'] = service_monthly_analysis.groupby('Service_Type').size()
        service_efficiency['Overpayment_Rate'] = (service_efficiency['Potential_Overpayment'] / service_efficiency['Service_Count']) * 100
        service_efficiency['High_Cost_Rate'] = (service_efficiency['High_Cost_Service'] / service_efficiency['Service_Count']) * 100
        
        # Calculate annual costs by service type
        service_efficiency['Annual_Cost'] = service_efficiency['Avg_Monthly_Cost'] * 12
        
        return service_efficiency
    
    def create_monthly_summary(self, df, service_monthly_analysis, billing_patterns, service_efficiency):
        """Create summary focusing on monthly billing analysis."""
        
        # Overall statistics
        total_cost = df['actual_cost'].sum()
        total_services = len(service_monthly_analysis)
        total_billing_months = service_monthly_analysis['Billing_Months'].sum()
        avg_monthly_cost = service_monthly_analysis['Avg_Monthly_Cost'].mean()
        
        # Overpayment analysis
        potential_overpayments = len(service_monthly_analysis[service_monthly_analysis['Potential_Overpayment']])
        high_cost_services = len(service_monthly_analysis[service_monthly_analysis['High_Cost_Service']])
        
        # Billing irregularities
        irregular_billing = len(billing_patterns[billing_patterns['Irregular_Billing']])
        potential_billing_errors = len(billing_patterns[billing_patterns['Potential_Billing_Error']])
        
        # Top cost services
        top_cost_services = service_monthly_analysis.nlargest(10, 'Annual_Cost')
        
        # Top irregular billing
        top_irregular_billing = billing_patterns[billing_patterns['Irregular_Billing']].nlargest(10, 'Cost_Variance_Pct')
        
        summary = {
            'total_cost': total_cost,
            'total_services': total_services,
            'total_billing_months': total_billing_months,
            'avg_monthly_cost': avg_monthly_cost,
            'potential_overpayments': potential_overpayments,
            'high_cost_services': high_cost_services,
            'irregular_billing': irregular_billing,
            'potential_billing_errors': potential_billing_errors,
            'top_cost_services': top_cost_services,
            'top_irregular_billing': top_irregular_billing,
            'service_efficiency': service_efficiency,
            'service_monthly_analysis': service_monthly_analysis,
            'billing_patterns': billing_patterns
        }
        
        return summary
    
    def create_monthly_visualizations(self, df, summary):
        """Create visualizations for monthly billing analysis."""
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Monthly Billing Analysis - Synoptek Service Cost Analysis', fontsize=16, fontweight='bold')
        
        # 1. Monthly cost distribution
        monthly_costs = summary['service_monthly_analysis']['Avg_Monthly_Cost']
        axes[0, 0].hist(monthly_costs, bins=30, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].set_title('Distribution of Monthly Service Costs')
        axes[0, 0].set_xlabel('Monthly Cost ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Top annual costs by service
        top_annual_costs = summary['top_cost_services']['Annual_Cost'].head(8)
        axes[0, 1].barh(range(len(top_annual_costs)), top_annual_costs.values, color='red', alpha=0.7)
        axes[0, 1].set_yticks(range(len(top_annual_costs)))
        axes[0, 1].set_yticklabels(top_annual_costs.index, fontsize=6)
        axes[0, 1].set_title('Top Services by Annual Cost')
        axes[0, 1].set_xlabel('Annual Cost ($)')
        
        # 3. Service type cost analysis
        service_costs = summary['service_efficiency']['Annual_Cost'].head(8)
        axes[0, 2].barh(range(len(service_costs)), service_costs.values, color='green', alpha=0.7)
        axes[0, 2].set_yticks(range(len(service_costs)))
        axes[0, 2].set_yticklabels(service_costs.index, fontsize=8)
        axes[0, 2].set_title('Service Types by Annual Cost')
        axes[0, 2].set_xlabel('Annual Cost ($)')
        
        # 4. Billing variance analysis
        if len(summary['top_irregular_billing']) > 0:
            irregular_costs = summary['top_irregular_billing']['Cost_Variance_Pct'].head(8)
            axes[1, 0].barh(range(len(irregular_costs)), irregular_costs.values, color='orange', alpha=0.7)
            axes[1, 0].set_yticks(range(len(irregular_costs)))
            axes[1, 0].set_yticklabels(irregular_costs.index, fontsize=6)
            axes[1, 0].set_title('Services with Irregular Billing')
            axes[1, 0].set_xlabel('Cost Variance (%)')
        
        # 5. Issue breakdown
        issues = ['Potential Overpayments', 'High Cost Services', 'Irregular Billing', 'Billing Errors']
        issue_counts = [
            summary['potential_overpayments'],
            summary['high_cost_services'],
            summary['irregular_billing'],
            summary['potential_billing_errors']
        ]
        colors = ['red', 'orange', 'yellow', 'purple']
        
        axes[1, 1].pie(issue_counts, labels=issues, colors=colors, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Billing Issues Breakdown')
        
        # 6. Monthly cost vs billing months
        monthly_data = summary['service_monthly_analysis']
        axes[1, 2].scatter(monthly_data['Billing_Months'], monthly_data['Avg_Monthly_Cost'], alpha=0.6, color='purple')
        axes[1, 2].set_title('Monthly Cost vs Billing Duration')
        axes[1, 2].set_xlabel('Billing Months')
        axes[1, 2].set_ylabel('Average Monthly Cost ($)')
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/monthly_billing_analysis_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    def create_monthly_csv_reports(self, df, summary):
        """Create CSV reports for monthly billing analysis."""
        
        # 1. Monthly service analysis
        monthly_analysis = summary['service_monthly_analysis'].reset_index()
        monthly_analysis.to_csv(f'{self.output_dir}/synoptek_monthly_service_analysis.csv', index=False)
        
        # 2. Billing patterns analysis
        billing_patterns = summary['billing_patterns'].reset_index()
        billing_patterns.to_csv(f'{self.output_dir}/synoptek_billing_patterns.csv', index=False)
        
        # 3. Service efficiency analysis
        service_efficiency = summary['service_efficiency'].reset_index()
        service_efficiency.to_csv(f'{self.output_dir}/synoptek_service_efficiency.csv', index=False)
        
        # 4. Top cost services
        top_cost_services = summary['top_cost_services'].reset_index()
        top_cost_services.to_csv(f'{self.output_dir}/synoptek_top_cost_services.csv', index=False)
        
        # 5. Irregular billing services
        irregular_billing = summary['top_irregular_billing'].reset_index()
        irregular_billing.to_csv(f'{self.output_dir}/synoptek_irregular_billing.csv', index=False)
        
        # 6. Potential overpayments
        potential_overpayments = summary['service_monthly_analysis'][summary['service_monthly_analysis']['Potential_Overpayment']].reset_index()
        potential_overpayments.to_csv(f'{self.output_dir}/synoptek_potential_overpayments.csv', index=False)
        
        return {
            'monthly_analysis': monthly_analysis,
            'billing_patterns': billing_patterns,
            'service_efficiency': service_efficiency,
            'top_cost_services': top_cost_services,
            'irregular_billing': irregular_billing,
            'potential_overpayments': potential_overpayments
        }
    
    def create_monthly_markdown_report(self, df, summary, csv_reports):
        """Create markdown report for monthly billing analysis."""
        
        report = f"""# Monthly Billing Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Focus:** Monthly Billing Analysis and Actual Overpayment Issues

## 📊 Monthly Billing Overview

### **Overall Service Analysis**
- **Total Services:** {summary['total_services']}
- **Total Cost:** ${summary['total_cost']:,.2f}
- **Total Billing Months:** {summary['total_billing_months']}
- **Average Monthly Cost per Service:** ${summary['avg_monthly_cost']:,.2f}

## 🔍 Billing Issues Identified

### **Service Analysis**
- **Potential Overpayments:** {summary['potential_overpayments']} services
- **High Cost Services:** {summary['high_cost_services']} services
- **Irregular Billing:** {summary['irregular_billing']} services
- **Potential Billing Errors:** {summary['potential_billing_errors']} services

## 💰 Top Cost Services (Annual)

"""
        
        # Add top cost services analysis
        for idx, row in summary['top_cost_services'].head(10).iterrows():
            report += f"""
**{row['Subcategory']} ({row['Service_Type']}):**
- **Annual Cost:** ${row['Annual_Cost']:,.2f}
- **Monthly Average:** ${row['Avg_Monthly_Cost']:,.2f}
- **Billing Months:** {row['Billing_Months']}
- **Cost Variance:** {row['Cost_Variance']:.2f}
"""
        
        report += f"""

## ⚠️ Irregular Billing Patterns

### **Services with High Cost Variance**
"""
        
        # Add irregular billing analysis
        for idx, row in summary['top_irregular_billing'].head(10).iterrows():
            report += f"""
**{row['Subcategory']} ({row['Service_Type']}):**
- **Cost Variance:** {row['Cost_Variance_Pct']:.1f}%
- **Min Cost:** ${row['Min_Cost']:,.2f}
- **Max Cost:** ${row['Max_Cost']:,.2f}
- **Average Cost:** ${row['Avg_Cost']:,.2f}
- **Billing Count:** {row['Billing_Count']}
"""
        
        report += f"""

## 📈 Service Type Analysis

### **Top Service Types by Annual Cost**
"""
        
        # Add service type analysis
        for service_type, data in summary['service_efficiency'].head(10).iterrows():
            report += f"""
**{service_type}:**
- **Annual Cost:** ${data['Annual_Cost']:,.2f}
- **Average Monthly Cost:** ${data['Avg_Monthly_Cost']:,.2f}
- **Service Count:** {data['Service_Count']}
- **Overpayment Rate:** {data['Overpayment_Rate']:.1f}%
- **High Cost Rate:** {data['High_Cost_Rate']:.1f}%
"""
        
        report += f"""

## 🎯 Key Findings and Recommendations

### **Monthly Billing Insights**
1. **Service Cost Analysis:** Average monthly cost per service is ${summary['avg_monthly_cost']:,.2f}
2. **Billing Consistency:** {summary['irregular_billing']} services show irregular billing patterns
3. **Cost Optimization:** {summary['potential_overpayments']} services may be overpaying
4. **High-Cost Services:** {summary['high_cost_services']} services are in the top 10% cost bracket

### **Immediate Actions Required**
1. **Review Irregular Billing:** Investigate {summary['irregular_billing']} services with high cost variance
2. **Optimize High-Cost Services:** Review {summary['high_cost_services']} high-cost services
3. **Address Potential Overpayments:** Investigate {summary['potential_overpayments']} potential overpayments
4. **Fix Billing Errors:** Address {summary['potential_billing_errors']} potential billing errors

### **Strategic Recommendations**
1. **Monthly Cost Monitoring:** Implement regular monthly cost reviews
2. **Billing Pattern Analysis:** Monitor for irregular billing patterns
3. **Service Consolidation:** Consider consolidating similar services
4. **Vendor Negotiation:** Use analysis to negotiate better rates

## 📋 Detailed Reports Available

The following detailed CSV reports have been generated:

1. **Monthly Service Analysis:** Detailed monthly cost analysis by service
2. **Billing Patterns:** Analysis of billing consistency and patterns
3. **Service Efficiency:** Service type cost efficiency analysis
4. **Top Cost Services:** Highest annual cost services
5. **Irregular Billing:** Services with irregular billing patterns
6. **Potential Overpayments:** Services identified as potentially overpaying

---
*Generated by Monthly Billing Analysis Tool*
"""
        
        return report
    
    def generate_monthly_analysis(self):
        """Generate the complete monthly billing analysis."""
        print("=" * 70)
        print("    MONTHLY BILLING ANALYSIS GENERATOR")
        print("=" * 70)
        print()
        
        # Load data
        data = self.load_ai_data()
        if not data:
            return False
        
        print("📊 Creating monthly billing analysis...")
        
        # Create analysis
        df, service_monthly_analysis = self.create_monthly_billing_analysis(data)
        if df is None:
            print("❌ No Synoptek records found for analysis!")
            return False
        
        print(f"📋 Found {len(df)} Synoptek billing records for analysis")
        
        # Analyze billing patterns and efficiency
        billing_patterns = self.analyze_billing_patterns(df)
        service_efficiency = self.analyze_service_cost_efficiency(df, service_monthly_analysis)
        
        # Create summary
        summary = self.create_monthly_summary(df, service_monthly_analysis, billing_patterns, service_efficiency)
        
        # Create visualizations
        print("📈 Generating monthly billing visualizations...")
        self.create_monthly_visualizations(df, summary)
        
        # Create CSV reports
        print("📋 Creating monthly billing CSV reports...")
        csv_reports = self.create_monthly_csv_reports(df, summary)
        
        # Create markdown report
        print("📝 Creating monthly billing report...")
        report = self.create_monthly_markdown_report(df, summary, csv_reports)
        
        with open(f'{self.output_dir}/monthly_billing_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Monthly billing analysis generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - monthly_billing_analysis_report.md")
        print(f"   - monthly_billing_analysis_charts.png")
        print(f"   - synoptek_monthly_service_analysis.csv")
        print(f"   - synoptek_billing_patterns.csv")
        print(f"   - synoptek_service_efficiency.csv")
        print(f"   - synoptek_top_cost_services.csv")
        print(f"   - synoptek_irregular_billing.csv")
        print(f"   - synoptek_potential_overpayments.csv")
        
        return True

def main():
    """Main function to generate monthly billing analysis."""
    analyzer = MonthlyBillingAnalysis()
    success = analyzer.generate_monthly_analysis()
    
    if success:
        print()
        print("🎉 Monthly billing analysis completed successfully!")
        print("📋 Ready for proper monthly billing analysis")
        print("💼 Use CSV reports for detailed billing analysis")
    else:
        print("❌ Analysis generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 