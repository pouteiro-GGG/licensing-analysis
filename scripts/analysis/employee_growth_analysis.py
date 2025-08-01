#!/usr/bin/env python3
"""
Employee Growth Analysis Tool
Analysis accounting for employee growth from 120 to 160 employees and its impact on Synoptek costs
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

class EmployeeGrowthAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/employee_growth_analysis_20250725"
        self.ensure_output_dir()
        
        # Employee growth data
        self.employee_growth = {
            'jan_2025': 120,
            'current': 160,
            'growth_rate': (160 - 120) / 120 * 100,  # 33.33%
            'additional_employees': 160 - 120  # 40 employees
        }
        
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
    
    def create_employee_growth_analysis(self, data):
        """Create analysis accounting for employee growth."""
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
        
        # Create unique service identifiers
        df['service_identifier'] = df['subcategory'] + '_' + df['service_type'] + '_' + df['primary_category']
        
        # Analyze costs by service type
        service_analysis = df.groupby('service_identifier').agg({
            'actual_cost': ['sum', 'mean', 'count', 'std'],
            'subcategory': 'first',
            'service_type': 'first',
            'primary_category': 'first'
        }).round(2)
        
        service_analysis.columns = ['Total_Cost', 'Avg_Monthly_Cost', 'Billing_Months', 'Cost_Std_Dev', 
                                 'Subcategory', 'Service_Type', 'Primary_Category']
        
        # Calculate per-employee costs
        service_analysis['Cost_Per_Employee_Current'] = service_analysis['Avg_Monthly_Cost'] / self.employee_growth['current']
        service_analysis['Cost_Per_Employee_Jan2025'] = service_analysis['Avg_Monthly_Cost'] / self.employee_growth['jan_2025']
        
        # Calculate expected costs based on employee growth
        service_analysis['Expected_Cost_With_Growth'] = service_analysis['Avg_Monthly_Cost'] * (self.employee_growth['current'] / self.employee_growth['jan_2025'])
        service_analysis['Cost_Variance_From_Expected'] = service_analysis['Avg_Monthly_Cost'] - service_analysis['Expected_Cost_With_Growth']
        service_analysis['Cost_Variance_Pct'] = (service_analysis['Cost_Variance_From_Expected'] / service_analysis['Expected_Cost_With_Growth']) * 100
        
        # Identify services that scale with employees
        employee_scaling_services = [
            'software_licensing', 'license/subscription', 'software_subscription',
            'microsoft_365_licensing', 'enterprise_software_licensing',
            'endpoint_protection', 'security_licensing', 'productivity_software'
        ]
        
        service_analysis['Scales_With_Employees'] = service_analysis['Service_Type'].isin(employee_scaling_services)
        
        # Calculate expected growth impact
        service_analysis['Expected_Growth_Impact'] = np.where(
            service_analysis['Scales_With_Employees'],
            service_analysis['Avg_Monthly_Cost'] * (self.employee_growth['growth_rate'] / 100),
            0
        )
        
        # Identify overpayments beyond employee growth
        service_analysis['Overpayment_Beyond_Growth'] = service_analysis['Cost_Variance_From_Expected'] > 0
        service_analysis['Overpayment_Amount'] = np.where(
            service_analysis['Overpayment_Beyond_Growth'],
            service_analysis['Cost_Variance_From_Expected'],
            0
        )
        
        return df, service_analysis
    
    def analyze_employee_scaling_services(self, service_analysis):
        """Analyze services that should scale with employee growth."""
        
        # Filter for services that should scale with employees
        scaling_services = service_analysis[service_analysis['Scales_With_Employees']].copy()
        
        # Calculate expected vs actual costs
        scaling_services['Expected_Cost_With_40_More_Employees'] = scaling_services['Avg_Monthly_Cost'] * (160/120)
        scaling_services['Actual_vs_Expected_Ratio'] = scaling_services['Avg_Monthly_Cost'] / scaling_services['Expected_Cost_With_40_More_Employees']
        
        # Identify services that grew more than expected
        scaling_services['Grew_More_Than_Expected'] = scaling_services['Actual_vs_Expected_Ratio'] > 1.1  # 10% tolerance
        
        # Calculate total impact
        total_expected_growth = scaling_services['Expected_Growth_Impact'].sum()
        total_actual_growth = scaling_services['Avg_Monthly_Cost'].sum() - (scaling_services['Avg_Monthly_Cost'].sum() * (120/160))
        
        return scaling_services, total_expected_growth, total_actual_growth
    
    def analyze_non_scaling_services(self, service_analysis):
        """Analyze services that shouldn't scale with employee growth."""
        
        # Filter for services that shouldn't scale with employees
        non_scaling_services = service_analysis[~service_analysis['Scales_With_Employees']].copy()
        
        # These services shouldn't have grown significantly
        non_scaling_services['Should_Not_Grow'] = non_scaling_services['Cost_Variance_Pct'] > 20
        
        # Calculate unexpected growth
        unexpected_growth_services = non_scaling_services[non_scaling_services['Should_Not_Grow']]
        
        return non_scaling_services, unexpected_growth_services
    
    def create_employee_growth_summary(self, df, service_analysis, scaling_services, non_scaling_services, total_expected_growth, total_actual_growth):
        """Create summary accounting for employee growth."""
        
        # Overall statistics
        total_cost = df['actual_cost'].sum()
        total_services = len(service_analysis)
        
        # Employee scaling analysis
        scaling_services_count = len(scaling_services)
        non_scaling_services_count = len(non_scaling_services)
        
        # Overpayment analysis
        overpayment_services = service_analysis[service_analysis['Overpayment_Beyond_Growth']]
        total_overpayment_amount = overpayment_services['Overpayment_Amount'].sum()
        
        # Top cost services adjusted for employee growth
        top_cost_services = service_analysis.nlargest(10, 'Avg_Monthly_Cost')
        
        # Services that grew more than expected
        grew_more_than_expected = scaling_services[scaling_services['Grew_More_Than_Expected']]
        
        # Unexpected growth in non-scaling services
        unexpected_growth = non_scaling_services[non_scaling_services['Should_Not_Grow']]
        
        summary = {
            'employee_growth': self.employee_growth,
            'total_cost': total_cost,
            'total_services': total_services,
            'scaling_services_count': scaling_services_count,
            'non_scaling_services_count': non_scaling_services_count,
            'total_expected_growth': total_expected_growth,
            'total_actual_growth': total_actual_growth,
            'overpayment_services_count': len(overpayment_services),
            'total_overpayment_amount': total_overpayment_amount,
            'top_cost_services': top_cost_services,
            'grew_more_than_expected': grew_more_than_expected,
            'unexpected_growth': unexpected_growth,
            'service_analysis': service_analysis,
            'scaling_services': scaling_services,
            'non_scaling_services': non_scaling_services
        }
        
        return summary
    
    def create_employee_growth_visualizations(self, df, summary):
        """Create visualizations accounting for employee growth."""
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Employee Growth Analysis - Synoptek Costs Adjusted for 120→160 Employees', fontsize=16, fontweight='bold')
        
        # 1. Employee growth impact
        employee_data = summary['employee_growth']
        axes[0, 0].bar(['Jan 2025', 'Current'], [employee_data['jan_2025'], employee_data['current']], 
                       color=['blue', 'green'], alpha=0.7)
        axes[0, 0].set_title('Employee Growth: 120 → 160 (33.3% increase)')
        axes[0, 0].set_ylabel('Number of Employees')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Expected vs actual growth impact
        expected_growth = summary['total_expected_growth']
        actual_growth = summary['total_actual_growth']
        axes[0, 1].bar(['Expected Growth', 'Actual Growth'], [expected_growth, actual_growth], 
                       color=['orange', 'red'], alpha=0.7)
        axes[0, 1].set_title('Monthly Cost Growth Impact')
        axes[0, 1].set_ylabel('Monthly Cost ($)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Service scaling analysis
        scaling_counts = [summary['scaling_services_count'], summary['non_scaling_services_count']]
        scaling_labels = ['Scales with Employees', 'Doesn\'t Scale']
        axes[0, 2].pie(scaling_counts, labels=scaling_labels, autopct='%1.1f%%', startangle=90)
        axes[0, 2].set_title('Service Scaling Analysis')
        
        # 4. Top cost services per employee
        top_services = summary['top_cost_services'].head(8)
        cost_per_employee = top_services['Cost_Per_Employee_Current']
        axes[1, 0].barh(range(len(cost_per_employee)), cost_per_employee.values, color='purple', alpha=0.7)
        axes[1, 0].set_yticks(range(len(cost_per_employee)))
        axes[1, 0].set_yticklabels(cost_per_employee.index, fontsize=6)
        axes[1, 0].set_title('Top Services by Cost per Employee')
        axes[1, 0].set_xlabel('Cost per Employee ($)')
        
        # 5. Overpayment beyond growth
        overpayment_data = summary['service_analysis'][summary['service_analysis']['Overpayment_Beyond_Growth']]
        if len(overpayment_data) > 0:
            overpayment_amounts = overpayment_data['Overpayment_Amount'].head(8)
            axes[1, 1].barh(range(len(overpayment_amounts)), overpayment_amounts.values, color='red', alpha=0.7)
            axes[1, 1].set_yticks(range(len(overpayment_amounts)))
            axes[1, 1].set_yticklabels(overpayment_amounts.index, fontsize=6)
            axes[1, 1].set_title('Overpayments Beyond Employee Growth')
            axes[1, 1].set_xlabel('Overpayment Amount ($)')
        
        # 6. Cost variance from expected
        variance_data = summary['service_analysis']['Cost_Variance_Pct'].dropna()
        if len(variance_data) > 0:
            # Use a simple bar chart instead of histogram
            variance_ranges = ['< -50%', '-50% to 0%', '0% to 50%', '> 50%']
            variance_counts = [
                len(variance_data[variance_data < -50]),
                len(variance_data[(variance_data >= -50) & (variance_data < 0)]),
                len(variance_data[(variance_data >= 0) & (variance_data < 50)]),
                len(variance_data[variance_data >= 50])
            ]
            axes[1, 2].bar(variance_ranges, variance_counts, alpha=0.7, color='orange')
            axes[1, 2].set_title('Cost Variance Distribution')
            axes[1, 2].set_xlabel('Variance Range')
            axes[1, 2].set_ylabel('Number of Services')
            axes[1, 2].tick_params(axis='x', rotation=45)
            axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/employee_growth_analysis_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    def create_employee_growth_csv_reports(self, df, summary):
        """Create CSV reports accounting for employee growth."""
        
        # 1. Employee growth adjusted service analysis
        growth_analysis = summary['service_analysis'].reset_index()
        growth_analysis.to_csv(f'{self.output_dir}/synoptek_employee_growth_analysis.csv', index=False)
        
        # 2. Scaling services analysis
        scaling_services = summary['scaling_services'].reset_index()
        scaling_services.to_csv(f'{self.output_dir}/synoptek_scaling_services.csv', index=False)
        
        # 3. Non-scaling services analysis
        non_scaling_services = summary['non_scaling_services'].reset_index()
        non_scaling_services.to_csv(f'{self.output_dir}/synoptek_non_scaling_services.csv', index=False)
        
        # 4. Overpayments beyond growth
        overpayments = summary['service_analysis'][summary['service_analysis']['Overpayment_Beyond_Growth']].reset_index()
        overpayments.to_csv(f'{self.output_dir}/synoptek_overpayments_beyond_growth.csv', index=False)
        
        # 5. Services that grew more than expected
        grew_more = summary['grew_more_than_expected'].reset_index()
        grew_more.to_csv(f'{self.output_dir}/synoptek_grew_more_than_expected.csv', index=False)
        
        # 6. Unexpected growth in non-scaling services
        unexpected_growth = summary['unexpected_growth'].reset_index()
        unexpected_growth.to_csv(f'{self.output_dir}/synoptek_unexpected_growth.csv', index=False)
        
        return {
            'growth_analysis': growth_analysis,
            'scaling_services': scaling_services,
            'non_scaling_services': non_scaling_services,
            'overpayments': overpayments,
            'grew_more': grew_more,
            'unexpected_growth': unexpected_growth
        }
    
    def create_employee_growth_markdown_report(self, df, summary, csv_reports):
        """Create markdown report accounting for employee growth."""
        
        report = f"""# Employee Growth Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Focus:** Synoptek Costs Adjusted for Employee Growth (120 → 160 employees)

## 👥 Employee Growth Context

### **Growth Statistics**
- **January 2025 Employees:** {summary['employee_growth']['jan_2025']}
- **Current Employees:** {summary['employee_growth']['current']}
- **Employee Growth:** +{summary['employee_growth']['additional_employees']} employees
- **Growth Rate:** {summary['employee_growth']['growth_rate']:.1f}%

## 📊 Cost Analysis Adjusted for Employee Growth

### **Overall Service Analysis**
- **Total Services:** {summary['total_services']}
- **Total Cost:** ${summary['total_cost']:,.2f}
- **Scaling Services:** {summary['scaling_services_count']} (should grow with employees)
- **Non-Scaling Services:** {summary['non_scaling_services_count']} (shouldn't grow significantly)

### **Expected vs Actual Growth Impact**
- **Expected Monthly Growth:** ${summary['total_expected_growth']:,.2f}
- **Actual Monthly Growth:** ${summary['total_actual_growth']:,.2f}
- **Growth Variance:** ${summary['total_actual_growth'] - summary['total_expected_growth']:,.2f}

## 💰 Top Cost Services (Per Employee Adjusted)

"""
        
        # Add top cost services analysis
        for idx, row in summary['top_cost_services'].head(10).iterrows():
            report += f"""
**{row['Subcategory']} ({row['Service_Type']}):**
- **Monthly Cost:** ${row['Avg_Monthly_Cost']:,.2f}
- **Cost per Employee:** ${row['Cost_Per_Employee_Current']:,.2f}
- **Expected with Growth:** ${row['Expected_Cost_With_Growth']:,.2f}
- **Variance from Expected:** {row['Cost_Variance_Pct']:.1f}%
"""
        
        report += f"""

## 🔍 Services That Should Scale with Employees

### **Scaling Services Analysis**
"""
        
        # Add scaling services analysis
        scaling_data = summary['scaling_services']
        for idx, row in scaling_data.head(10).iterrows():
            report += f"""
**{row['Subcategory']} ({row['Service_Type']}):**
- **Monthly Cost:** ${row['Avg_Monthly_Cost']:,.2f}
- **Expected with 40 More Employees:** ${row['Expected_Cost_With_40_More_Employees']:,.2f}
- **Actual vs Expected Ratio:** {row['Actual_vs_Expected_Ratio']:.2f}
- **Grew More Than Expected:** {'Yes' if row['Grew_More_Than_Expected'] else 'No'}
"""
        
        report += f"""

## ⚠️ Services That Shouldn't Scale with Employees

### **Non-Scaling Services with Unexpected Growth**
"""
        
        # Add non-scaling services analysis
        unexpected_data = summary['unexpected_growth']
        for idx, row in unexpected_data.head(10).iterrows():
            report += f"""
**{row['Subcategory']} ({row['Service_Type']}):**
- **Monthly Cost:** ${row['Avg_Monthly_Cost']:,.2f}
- **Cost Variance:** {row['Cost_Variance_Pct']:.1f}%
- **Expected Cost:** ${row['Expected_Cost_With_Growth']:,.2f}
- **Overpayment Amount:** ${row['Overpayment_Amount']:,.2f}
"""
        
        report += f"""

## 🎯 Key Findings and Recommendations

### **Employee Growth Impact**
1. **Expected Growth:** 33.3% employee increase should result in proportional cost increases for scaling services
2. **Actual Growth:** ${summary['total_actual_growth']:,.2f} vs expected ${summary['total_expected_growth']:,.2f}
3. **Variance:** ${summary['total_actual_growth'] - summary['total_expected_growth']:,.2f} difference

### **Scaling Services Analysis**
- **Services that should scale:** {summary['scaling_services_count']} services
- **Services that grew more than expected:** {len(summary['grew_more_than_expected'])} services
- **Recommendation:** Review services that grew more than 33.3% with employee growth

### **Non-Scaling Services Analysis**
- **Services that shouldn't scale:** {summary['non_scaling_services_count']} services
- **Services with unexpected growth:** {len(summary['unexpected_growth'])} services
- **Recommendation:** Investigate why non-scaling services increased with employee growth

### **Overpayment Analysis**
- **Services overpaying beyond growth:** {summary['overpayment_services_count']} services
- **Total overpayment amount:** ${summary['total_overpayment_amount']:,.2f}
- **Recommendation:** Focus on services that grew beyond employee growth expectations

## 📋 Detailed Reports Available

The following detailed CSV reports have been generated:

1. **Employee Growth Analysis:** All services adjusted for employee growth
2. **Scaling Services:** Services that should scale with employee growth
3. **Non-Scaling Services:** Services that shouldn't scale with employee growth
4. **Overpayments Beyond Growth:** Services overpaying beyond employee growth
5. **Grew More Than Expected:** Services that grew more than 33.3%
6. **Unexpected Growth:** Non-scaling services with unexpected growth

---
*Generated by Employee Growth Analysis Tool*
"""
        
        return report
    
    def generate_employee_growth_analysis(self):
        """Generate the complete employee growth analysis."""
        print("=" * 70)
        print("    EMPLOYEE GROWTH ANALYSIS GENERATOR")
        print("=" * 70)
        print()
        
        # Load data
        data = self.load_ai_data()
        if not data:
            return False
        
        print("📊 Creating employee growth analysis...")
        
        # Create analysis
        df, service_analysis = self.create_employee_growth_analysis(data)
        if df is None:
            print("❌ No Synoptek records found for analysis!")
            return False
        
        print(f"📋 Found {len(df)} Synoptek billing records for analysis")
        print(f"👥 Accounting for employee growth: {self.employee_growth['jan_2025']} → {self.employee_growth['current']} employees")
        
        # Analyze scaling and non-scaling services
        scaling_services, total_expected_growth, total_actual_growth = self.analyze_employee_scaling_services(service_analysis)
        non_scaling_services, unexpected_growth_services = self.analyze_non_scaling_services(service_analysis)
        
        # Create summary
        summary = self.create_employee_growth_summary(df, service_analysis, scaling_services, non_scaling_services, total_expected_growth, total_actual_growth)
        
        # Create visualizations
        print("📈 Generating employee growth visualizations...")
        self.create_employee_growth_visualizations(df, summary)
        
        # Create CSV reports
        print("📋 Creating employee growth CSV reports...")
        csv_reports = self.create_employee_growth_csv_reports(df, summary)
        
        # Create markdown report
        print("📝 Creating employee growth report...")
        report = self.create_employee_growth_markdown_report(df, summary, csv_reports)
        
        with open(f'{self.output_dir}/employee_growth_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Employee growth analysis generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - employee_growth_analysis_report.md")
        print(f"   - employee_growth_analysis_charts.png")
        print(f"   - synoptek_employee_growth_analysis.csv")
        print(f"   - synoptek_scaling_services.csv")
        print(f"   - synoptek_non_scaling_services.csv")
        print(f"   - synoptek_overpayments_beyond_growth.csv")
        print(f"   - synoptek_grew_more_than_expected.csv")
        print(f"   - synoptek_unexpected_growth.csv")
        
        return True

def main():
    """Main function to generate employee growth analysis."""
    analyzer = EmployeeGrowthAnalysis()
    success = analyzer.generate_employee_growth_analysis()
    
    if success:
        print()
        print("🎉 Employee growth analysis completed successfully!")
        print("📋 Ready for employee growth-adjusted cost analysis")
        print("💼 Use CSV reports for detailed growth impact analysis")
    else:
        print("❌ Analysis generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 