#!/usr/bin/env python3
"""
Presentation-Style Analysis Report Generator
Creates professional presentation-style reports focusing on charge assessment
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

class PresentationStyleAnalysis:
    def __init__(self):
        self.ai_data_file = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        self.output_dir = "reports/current/presentation_style_analysis_20250725"
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
    
    def create_presentation_analysis(self, data):
        """Create presentation-style analysis focusing on charge assessment."""
        benchmarks = data.get('benchmarks', [])
        
        # Filter for Synoptek records
        synoptek_records = [b for b in benchmarks if b.get('vendor', '').lower() == 'synoptek']
        
        # Create DataFrame
        df = pd.DataFrame(synoptek_records)
        
        if df.empty:
            print("No Synoptek records found in the dataset.")
            return None
        
        # Focus on charge assessment
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
        
        # Calculate charge assessment metrics
        df['service_identifier'] = df['subcategory'] + '_' + df['service_type']
        
        # Analyze charges by service type
        service_analysis = df.groupby('service_identifier').agg({
            'actual_cost': ['sum', 'mean', 'count', 'std'],
            'subcategory': 'first',
            'service_type': 'first',
            'primary_category': 'first'
        }).round(2)
        
        service_analysis.columns = ['Total_Cost', 'Avg_Monthly_Cost', 'Billing_Months', 'Cost_Std_Dev', 
                                 'Subcategory', 'Service_Type', 'Primary_Category']
        
        # Calculate charge assessment indicators
        service_analysis['Cost_Per_Service'] = service_analysis['Avg_Monthly_Cost']
        service_analysis['Cost_Variance'] = service_analysis['Cost_Std_Dev'] / service_analysis['Avg_Monthly_Cost']
        
        # Identify potential overcharges
        cost_threshold = service_analysis['Avg_Monthly_Cost'].quantile(0.9)  # Top 10%
        service_analysis['High_Cost_Flag'] = service_analysis['Avg_Monthly_Cost'] > cost_threshold
        
        # Calculate industry comparison metrics
        service_analysis['Industry_Comparison'] = service_analysis['Avg_Monthly_Cost'].apply(
            lambda x: 'Above Average' if x > cost_threshold else 'Normal' if x > service_analysis['Avg_Monthly_Cost'].median() else 'Below Average'
        )
        
        return df, service_analysis
    
    def assess_charge_fairness(self, df, service_analysis):
        """Assess whether charges are fair or overpriced."""
        
        # Calculate overall metrics
        total_cost = df['actual_cost'].sum()
        avg_cost_per_service = service_analysis['Avg_Monthly_Cost'].mean()
        median_cost = service_analysis['Avg_Monthly_Cost'].median()
        
        # Identify overpriced services
        overpriced_services = service_analysis[service_analysis['High_Cost_Flag']].copy()
        overpriced_cost = overpriced_services['Total_Cost'].sum()
        overpriced_percentage = (overpriced_cost / total_cost) * 100
        
        # Calculate fairness metrics
        cost_distribution = {
            'Normal': len(service_analysis[service_analysis['Industry_Comparison'] == 'Normal']),
            'Above_Average': len(service_analysis[service_analysis['Industry_Comparison'] == 'Above Average']),
            'Below_Average': len(service_analysis[service_analysis['Industry_Comparison'] == 'Below Average'])
        }
        
        # Assess overall fairness
        if overpriced_percentage > 30:
            overall_assessment = "POTENTIALLY OVERCHARGED"
            assessment_color = "red"
        elif overpriced_percentage > 15:
            overall_assessment = "MIXED - SOME CONCERNS"
            assessment_color = "orange"
        else:
            overall_assessment = "CHARGES APPEAR NORMAL"
            assessment_color = "green"
        
        assessment = {
            'total_cost': total_cost,
            'avg_cost_per_service': avg_cost_per_service,
            'median_cost': median_cost,
            'overpriced_services_count': len(overpriced_services),
            'overpriced_cost': overpriced_cost,
            'overpriced_percentage': overpriced_percentage,
            'cost_distribution': cost_distribution,
            'overall_assessment': overall_assessment,
            'assessment_color': assessment_color,
            'overpriced_services': overpriced_services,
            'service_analysis': service_analysis
        }
        
        return assessment
    
    def create_presentation_visualizations(self, df, assessment):
        """Create presentation-style visualizations."""
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Synoptek Charge Assessment - Are We Being Overcharged?', fontsize=16, fontweight='bold')
        
        # 1. Overall assessment pie chart
        assessment_labels = ['Normal Charges', 'Potentially Overcharged']
        assessment_sizes = [
            assessment['total_cost'] - assessment['overpriced_cost'],
            assessment['overpriced_cost']
        ]
        assessment_colors = ['green', 'red']
        
        axes[0, 0].pie(assessment_sizes, labels=assessment_labels, colors=assessment_colors, 
                       autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Charge Assessment Breakdown')
        
        # 2. Cost distribution by service type
        service_costs = assessment['service_analysis'].groupby('Service_Type')['Total_Cost'].sum().head(8)
        axes[0, 1].barh(range(len(service_costs)), service_costs.values, color='blue', alpha=0.7)
        axes[0, 1].set_yticks(range(len(service_costs)))
        axes[0, 1].set_yticklabels(service_costs.index, fontsize=8)
        axes[0, 1].set_title('Total Cost by Service Type')
        axes[0, 1].set_xlabel('Total Cost ($)')
        
        # 3. Industry comparison
        comparison_data = assessment['cost_distribution']
        comparison_labels = list(comparison_data.keys())
        comparison_values = list(comparison_data.values())
        comparison_colors = ['green', 'orange', 'blue']
        
        axes[0, 2].bar(comparison_labels, comparison_values, color=comparison_colors, alpha=0.7)
        axes[0, 2].set_title('Service Cost vs Industry Average')
        axes[0, 2].set_ylabel('Number of Services')
        
        # 4. Top overpriced services
        top_overpriced = assessment['overpriced_services'].nlargest(8, 'Avg_Monthly_Cost')
        axes[1, 0].barh(range(len(top_overpriced)), top_overpriced['Avg_Monthly_Cost'], color='red', alpha=0.7)
        axes[1, 0].set_yticks(range(len(top_overpriced)))
        axes[1, 0].set_yticklabels(top_overpriced['Subcategory'], fontsize=6)
        axes[1, 0].set_title('Top Potentially Overpriced Services')
        axes[1, 0].set_xlabel('Monthly Cost ($)')
        
        # 5. Cost variance analysis
        variance_data = assessment['service_analysis']['Cost_Variance'].dropna()
        axes[1, 1].hist(variance_data, bins=20, alpha=0.7, color='purple', edgecolor='black')
        axes[1, 1].set_title('Cost Variance Distribution')
        axes[1, 1].set_xlabel('Cost Variance')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Assessment summary
        assessment_text = f"""
OVERALL ASSESSMENT: {assessment['overall_assessment']}

Total Cost: ${assessment['total_cost']:,.2f}
Overpriced Services: {assessment['overpriced_services_count']}
Overpriced Amount: ${assessment['overpriced_cost']:,.2f}
Overpriced Percentage: {assessment['overpriced_percentage']:.1f}%

Key Findings:
• {assessment['overpriced_services_count']} services flagged as potentially overpriced
• ${assessment['overpriced_cost']:,.2f} in potentially overcharged costs
• {assessment['overpriced_percentage']:.1f}% of total spend may be overpriced
        """
        
        axes[1, 2].text(0.1, 0.5, assessment_text, transform=axes[1, 2].transAxes, 
                        fontsize=10, verticalalignment='center', 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor=assessment['assessment_color'], alpha=0.3))
        axes[1, 2].set_title('Assessment Summary')
        axes[1, 2].axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/charge_assessment_presentation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    def create_presentation_csv_reports(self, df, assessment):
        """Create presentation-style CSV reports."""
        
        # 1. Overall charge assessment
        assessment_summary = pd.DataFrame([{
            'Assessment_Date': datetime.now().strftime('%Y-%m-%d'),
            'Total_Cost': assessment['total_cost'],
            'Overpriced_Services_Count': assessment['overpriced_services_count'],
            'Overpriced_Cost': assessment['overpriced_cost'],
            'Overpriced_Percentage': assessment['overpriced_percentage'],
            'Overall_Assessment': assessment['overall_assessment'],
            'Average_Cost_Per_Service': assessment['avg_cost_per_service'],
            'Median_Cost_Per_Service': assessment['median_cost']
        }])
        
        try:
            assessment_summary.to_csv(f'{self.output_dir}/charge_assessment_summary.csv', index=False)
        except PermissionError:
            print("⚠️ Warning: Could not overwrite charge_assessment_summary.csv (file may be open)")
        
        # 2. Overpriced services details
        overpriced_details = assessment['overpriced_services'].reset_index()
        try:
            overpriced_details.to_csv(f'{self.output_dir}/overpriced_services_details.csv', index=False)
        except PermissionError:
            print("⚠️ Warning: Could not overwrite overpriced_services_details.csv (file may be open)")
        
        # 3. Service cost analysis
        service_cost_analysis = assessment['service_analysis'].reset_index()
        try:
            service_cost_analysis.to_csv(f'{self.output_dir}/service_cost_analysis.csv', index=False)
        except PermissionError:
            print("⚠️ Warning: Could not overwrite service_cost_analysis.csv (file may be open)")
        
        # 4. Industry comparison
        industry_comparison = pd.DataFrame([
            {'Category': 'Normal', 'Count': assessment['cost_distribution']['Normal']},
            {'Category': 'Above Average', 'Count': assessment['cost_distribution']['Above_Average']},
            {'Category': 'Below Average', 'Count': assessment['cost_distribution']['Below_Average']}
        ])
        
        try:
            industry_comparison.to_csv(f'{self.output_dir}/industry_comparison.csv', index=False)
        except PermissionError:
            print("⚠️ Warning: Could not overwrite industry_comparison.csv (file may be open)")
        
        return {
            'assessment_summary': assessment_summary,
            'overpriced_details': overpriced_details,
            'service_cost_analysis': service_cost_analysis,
            'industry_comparison': industry_comparison
        }
    
    def create_presentation_markdown_report(self, df, assessment, csv_reports):
        """Create presentation-style markdown report."""
        
        report = f"""# Synoptek Charge Assessment Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Purpose:** Determine if Synoptek charges are normal or overpriced
**Assessment Focus:** Charge fairness and potential overcharging

---

## 🎯 EXECUTIVE SUMMARY

### **OVERALL ASSESSMENT: {assessment['overall_assessment']}**

**Key Metrics:**
- **Total Cost:** ${assessment['total_cost']:,.2f}
- **Overpriced Services:** {assessment['overpriced_services_count']} services flagged
- **Overpriced Amount:** ${assessment['overpriced_cost']:,.2f}
- **Overpriced Percentage:** {assessment['overpriced_percentage']:.1f}% of total spend

---

## 📊 CHARGE ASSESSMENT BREAKDOWN

### **Cost Distribution Analysis**
- **Normal Charges:** {assessment['cost_distribution']['Normal']} services
- **Above Average:** {assessment['cost_distribution']['Above_Average']} services  
- **Below Average:** {assessment['cost_distribution']['Below_Average']} services

### **Industry Comparison**
- **Average Cost per Service:** ${assessment['avg_cost_per_service']:,.2f}
- **Median Cost per Service:** ${assessment['median_cost']:,.2f}
- **Cost Variance:** {assessment['service_analysis']['Cost_Variance'].mean():.2f}

---

## 🔴 POTENTIALLY OVERPRICED SERVICES

### **Top Overpriced Services by Monthly Cost**
"""
        
        # Add top overpriced services
        top_overpriced = assessment['overpriced_services'].nlargest(10, 'Avg_Monthly_Cost')
        for idx, row in top_overpriced.iterrows():
            report += f"""
**{row['Subcategory']} ({row['Service_Type']}):**
- **Monthly Cost:** ${row['Avg_Monthly_Cost']:,.2f}
- **Total Cost:** ${row['Total_Cost']:,.2f}
- **Billing Months:** {row['Billing_Months']}
- **Cost Variance:** {row['Cost_Variance']:.2f}
- **Assessment:** Potentially overpriced
"""
        
        report += f"""

---

## 📈 SERVICE TYPE ANALYSIS

### **Highest Cost Service Types**
"""
        
        # Add service type analysis
        service_costs = assessment['service_analysis'].groupby('Service_Type')['Total_Cost'].sum().sort_values(ascending=False).head(10)
        for service_type, cost in service_costs.items():
            service_count = len(assessment['service_analysis'][assessment['service_analysis']['Service_Type'] == service_type])
            avg_cost = assessment['service_analysis'][assessment['service_analysis']['Service_Type'] == service_type]['Avg_Monthly_Cost'].mean()
            
            report += f"""
**{service_type}:**
- **Total Cost:** ${cost:,.2f}
- **Service Count:** {service_count}
- **Average Monthly Cost:** ${avg_cost:,.2f}
"""
        
        report += f"""

---

## 🎯 KEY FINDINGS & RECOMMENDATIONS

### **Assessment Results**
"""
        
        if assessment['overpriced_percentage'] > 30:
            report += f"""
🚨 **CRITICAL FINDINGS:**
- {assessment['overpriced_percentage']:.1f}% of total spend appears overpriced
- ${assessment['overpriced_cost']:,.2f} in potentially overcharged costs
- {assessment['overpriced_services_count']} services require immediate review

**RECOMMENDATIONS:**
1. **Immediate Action:** Review all {assessment['overpriced_services_count']} flagged services
2. **Negotiation:** Use analysis to negotiate with Synoptek
3. **Alternative Quotes:** Obtain competitive quotes for overpriced services
4. **Contract Review:** Reassess current contract terms and pricing
"""
        elif assessment['overpriced_percentage'] > 15:
            report += f"""
⚠️ **MIXED FINDINGS:**
- {assessment['overpriced_percentage']:.1f}% of total spend shows concerns
- ${assessment['overpriced_cost']:,.2f} in potentially overcharged costs
- {assessment['overpriced_services_count']} services need review

**RECOMMENDATIONS:**
1. **Selective Review:** Focus on top {min(5, assessment['overpriced_services_count'])} overpriced services
2. **Market Research:** Compare pricing with industry standards
3. **Negotiation:** Address specific overpriced services with Synoptek
4. **Monitoring:** Implement regular cost monitoring
"""
        else:
            report += f"""
✅ **POSITIVE FINDINGS:**
- Only {assessment['overpriced_percentage']:.1f}% of total spend shows concerns
- ${assessment['overpriced_cost']:,.2f} in potentially overcharged costs
- {assessment['overpriced_services_count']} services flagged for review

**RECOMMENDATIONS:**
1. **Minor Review:** Review the {assessment['overpriced_services_count']} flagged services
2. **Optimization:** Focus on service optimization rather than pricing
3. **Monitoring:** Continue regular cost monitoring
4. **Relationship:** Maintain positive relationship with Synoptek
"""
        
        report += f"""

### **Strategic Recommendations**

#### **Immediate Actions (Next 30 Days):**
1. **Service Review:** Audit all {assessment['overpriced_services_count']} flagged services
2. **Market Comparison:** Compare pricing with industry benchmarks
3. **Vendor Discussion:** Schedule meeting with Synoptek to discuss findings
4. **Alternative Quotes:** Obtain competitive quotes for overpriced services

#### **Short-term Actions (Next 90 Days):**
1. **Contract Negotiation:** Use analysis to negotiate better rates
2. **Service Optimization:** Consolidate or eliminate overpriced services
3. **Cost Monitoring:** Implement regular cost review process
4. **Performance Tracking:** Monitor service quality vs cost

#### **Long-term Strategy (Next 6-12 Months):**
1. **Vendor Assessment:** Evaluate Synoptek relationship based on pricing
2. **Market Analysis:** Regular comparison with alternative providers
3. **Cost Optimization:** Continuous improvement of service costs
4. **Contract Renewal:** Use analysis for contract renewal negotiations

---

## 📋 DETAILED REPORTS AVAILABLE

The following detailed CSV reports have been generated:

1. **Charge Assessment Summary:** Overall assessment metrics
2. **Overpriced Services Details:** Detailed analysis of flagged services
3. **Service Cost Analysis:** Complete service cost breakdown
4. **Industry Comparison:** Cost comparison with industry standards

---

## 🎯 CONCLUSION

**Assessment:** {assessment['overall_assessment']}

**Primary Finding:** {assessment['overpriced_percentage']:.1f}% of total spend ({assessment['overpriced_services_count']} services) appears potentially overpriced.

**Recommendation:** {'Immediate action required' if assessment['overpriced_percentage'] > 30 else 'Selective review recommended' if assessment['overpriced_percentage'] > 15 else 'Minor optimization opportunities exist'}.

---

*Generated by Presentation-Style Analysis Tool*
"""
        
        return report
    
    def generate_presentation_analysis(self):
        """Generate the complete presentation-style analysis."""
        print("=" * 70)
        print("    PRESENTATION-STYLE CHARGE ASSESSMENT GENERATOR")
        print("=" * 70)
        print()
        
        # Load data
        data = self.load_ai_data()
        if not data:
            return False
        
        print("📊 Creating presentation-style charge assessment...")
        
        # Create analysis
        df, service_analysis = self.create_presentation_analysis(data)
        if df is None:
            print("❌ No Synoptek records found for analysis!")
            return False
        
        print(f"📋 Found {len(df)} Synoptek service records for assessment")
        
        # Assess charge fairness
        assessment = self.assess_charge_fairness(df, service_analysis)
        
        # Create visualizations
        print("📈 Generating presentation visualizations...")
        self.create_presentation_visualizations(df, assessment)
        
        # Create CSV reports
        print("📋 Creating presentation CSV reports...")
        csv_reports = self.create_presentation_csv_reports(df, assessment)
        
        # Create markdown report
        print("📝 Creating presentation-style report...")
        report = self.create_presentation_markdown_report(df, assessment, csv_reports)
        
        with open(f'{self.output_dir}/charge_assessment_presentation_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Presentation-style analysis generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - charge_assessment_presentation_report.md")
        print(f"   - charge_assessment_presentation.png")
        print(f"   - charge_assessment_summary.csv")
        print(f"   - overpriced_services_details.csv")
        print(f"   - service_cost_analysis.csv")
        print(f"   - industry_comparison.csv")
        
        print()
        print(f"🎯 ASSESSMENT: {assessment['overall_assessment']}")
        print(f"💰 Overpriced Amount: ${assessment['overpriced_cost']:,.2f}")
        print(f"📊 Overpriced Percentage: {assessment['overpriced_percentage']:.1f}%")
        
        return True

def main():
    """Main function to generate presentation-style analysis."""
    analyzer = PresentationStyleAnalysis()
    success = analyzer.generate_presentation_analysis()
    
    if success:
        print()
        print("🎉 Presentation-style analysis completed successfully!")
        print("📋 Ready for executive presentation")
        print("💼 Use report for charge assessment and negotiations")
    else:
        print("❌ Analysis generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())