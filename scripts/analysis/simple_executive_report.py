#!/usr/bin/env python3
"""
Simple Executive Report Generator
Generates high-level executive reports with intelligent vendor consolidation
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

class SimpleExecutiveReport:
    def __init__(self):
        self.data_file = "reports/executive/cleaned_licensing_data_20250725.json"
        self.output_file = "reports/executive/simple_executive_report_20250725.md"
        self.json_output = "reports/executive/simple_executive_report_20250725.json"
    
    def consolidate_vendor_name(self, vendor_name):
        """Consolidate vendor names to handle variations."""
        vendor_lower = vendor_name.lower().strip()
        
        # Vendor consolidation rules
        vendor_mappings = {
            'synoptek': 'Synoptek',
            'synoptek, llc': 'Synoptek',
            'synoptek llc': 'Synoptek',
            'atlassian': 'Atlassian',
            'microsoft': 'Microsoft',
            'oracle': 'Oracle',
            'salesforce': 'Salesforce',
            'aws': 'AWS',
            'amazon': 'AWS',
            'amazon web services': 'AWS',
            'azure': 'Microsoft Azure',
            'google': 'Google',
            'gcp': 'Google Cloud',
            'google cloud': 'Google Cloud',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'crowdstrike': 'CrowdStrike',
            'sentinelone': 'SentinelOne',
            'palo alto': 'Palo Alto Networks',
            'proofpoint': 'Proofpoint',
            'harman': 'Harman',
            'harman connected services': 'Harman',
            'markov': 'Markov Processes',
            'markov processes': 'Markov Processes',
            'markov processes international': 'Markov Processes'
        }
        
        # Check for exact matches first
        for key, value in vendor_mappings.items():
            if vendor_lower == key:
                return value
        
        # Check for partial matches
        for key, value in vendor_mappings.items():
            if key in vendor_lower:
                return value
        
        # Return original name if no match found
        return vendor_name
    
    def extract_company_from_bill_to(self, bill_to):
        """Extract company name from bill_to field."""
        if not bill_to:
            return "Unknown Company"
        
        # Common company patterns with better consolidation
        company_patterns = [
            (r'great\s+gray\s+(?:trust\s+)?company', 'Great Gray Trust Company'),
            (r'great\s+gray\s+market', 'Great Gray Market'),
            (r'great\s+gray', 'Great Gray'),
            (r'rpag', 'RPAG'),
            (r'retirement\s+plan\s+advisory\s+group', 'RPAG'),
            (r'flexpath\s+(?:advisors?|partners?)', 'Flexpath'),
            (r'flexpath', 'Flexpath')
        ]
        
        bill_to_lower = bill_to.lower()
        
        for pattern, company_name in company_patterns:
            match = re.search(pattern, bill_to_lower)
            if match:
                return company_name
        
        # If no pattern matches, try to extract first company-like name
        words = bill_to.split(',')[0].split()
        potential_company = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                potential_company.append(word)
        
        if potential_company:
            return ' '.join(potential_company[:3])  # Take first 3 words max
        
        return "Unknown Company"
    
    def parse_date(self, date_str):
        """Parse various date formats and extract year."""
        if not date_str:
            return None
        
        # Try to extract year
        year_match = re.search(r'20\d{2}', date_str)
        if year_match:
            return int(year_match.group())
        
        return None
    
    def categorize_vendor(self, vendor_name):
        """Categorize vendor based on name."""
        vendor_lower = vendor_name.lower()
        
        vendor_categories = {
            "synoptek": "it_services",
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
        
        for vendor_key, category in vendor_categories.items():
            if vendor_key in vendor_lower:
                return category
        
        return "it_services"
    
    def generate_executive_report(self):
        """Generate comprehensive executive report with intelligent consolidation."""
        if not os.path.exists(self.data_file):
            print(f"Error: Data file {self.data_file} not found!")
            return None
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        print(f"Generating executive report for {len(data)} records with intelligent vendor consolidation...")
        
        # Initialize analysis structures
        analysis = {
            "summary": {},
            "by_year": defaultdict(lambda: {"total": 0, "categories": defaultdict(float), "vendors": defaultdict(float), "companies": defaultdict(float)}),
            "by_category": defaultdict(lambda: {"total": 0, "vendors": defaultdict(float), "companies": defaultdict(float)}),
            "by_vendor": defaultdict(lambda: {"total": 0, "categories": defaultdict(float), "companies": defaultdict(float)}),
            "by_company": defaultdict(lambda: {"total": 0, "categories": defaultdict(float), "vendors": defaultdict(float)}),
            "monthly_data": defaultdict(float),
            "recommendations": []
        }
        
        total_spend = 0
        
        # Process each record with intelligent consolidation
        for item in data:
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('total_amount', 0)
            date_str = item.get('invoice_date', '')
            bill_to = item.get('bill_to', '')
            
            # Apply intelligent consolidation
            consolidated_vendor = self.consolidate_vendor_name(vendor)
            company = self.extract_company_from_bill_to(bill_to)
            category = self.categorize_vendor(consolidated_vendor)
            year = self.parse_date(date_str) or 2025
            
            total_spend += amount
            
            # Update year analysis
            analysis["by_year"][year]["total"] += amount
            analysis["by_year"][year]["categories"][category] += amount
            analysis["by_year"][year]["vendors"][consolidated_vendor] += amount
            analysis["by_year"][year]["companies"][company] += amount
            
            # Update category analysis
            analysis["by_category"][category]["total"] += amount
            analysis["by_category"][category]["vendors"][consolidated_vendor] += amount
            analysis["by_category"][category]["companies"][company] += amount
            
            # Update vendor analysis
            analysis["by_vendor"][consolidated_vendor]["total"] += amount
            analysis["by_vendor"][consolidated_vendor]["categories"][category] += amount
            analysis["by_vendor"][consolidated_vendor]["companies"][company] += amount
            
            # Update company analysis
            analysis["by_company"][company]["total"] += amount
            analysis["by_company"][company]["categories"][category] += amount
            analysis["by_company"][company]["vendors"][consolidated_vendor] += amount
        
        # Calculate summary metrics
        analysis["summary"]["total_spend"] = total_spend
        analysis["summary"]["total_invoices"] = len(data)
        analysis["summary"]["years_analyzed"] = sorted(analysis["by_year"].keys())
        analysis["summary"]["vendor_count"] = len(analysis["by_vendor"])
        analysis["summary"]["company_count"] = len(analysis["by_company"])
        analysis["summary"]["category_count"] = len(analysis["by_category"])
        analysis["summary"]["avg_invoice"] = total_spend / len(data) if data else 0
        
        # Generate recommendations
        analysis["recommendations"] = self.generate_recommendations(analysis)
        
        return analysis
    
    def generate_recommendations(self, analysis):
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check for high-spending vendors
        top_vendors = sorted(analysis["by_vendor"].items(), key=lambda x: x[1]["total"], reverse=True)[:3]
        for vendor, data in top_vendors:
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            if percentage > 20:
                recommendations.append({
                    "type": "vendor_optimization",
                    "priority": "high",
                    "message": f"Review {vendor} contracts and usage. Represents {percentage:.1f}% of total spend.",
                    "potential_savings": data["total"] * 0.15
                })
        
        # Check for category optimization
        for category, data in analysis["by_category"].items():
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            if percentage > 30:
                recommendations.append({
                    "type": "category_optimization",
                    "priority": "medium",
                    "message": f"Optimize {category.replace('_', ' ').title()} spending. Represents {percentage:.1f}% of total spend.",
                    "potential_savings": data["total"] * 0.10
                })
        
        # Check for company-specific insights
        for company, data in analysis["by_company"].items():
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            if percentage > 25:
                recommendations.append({
                    "type": "company_review",
                    "priority": "medium",
                    "message": f"Review {company} licensing needs. Represents {percentage:.1f}% of total spend.",
                    "potential_savings": data["total"] * 0.05
                })
        
        return recommendations
    
    def create_report(self, analysis):
        """Create the executive report content."""
        if not analysis:
            return "No analysis data available."
        
        report = []
        report.append("# Executive Licensing Analysis Report")
        report.append(f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total Annual Spend**: ${analysis['summary']['total_spend']:,.2f}")
        report.append(f"- **Total Invoices**: {analysis['summary']['total_invoices']:,}")
        report.append(f"- **Average Invoice**: ${analysis['summary']['avg_invoice']:,.2f}")
        report.append(f"- **Years Analyzed**: {', '.join(map(str, analysis['summary']['years_analyzed']))}")
        report.append(f"- **Vendors (Consolidated)**: {analysis['summary']['vendor_count']}")
        report.append(f"- **Companies**: {analysis['summary']['company_count']}")
        report.append("")
        
        # Key Metrics
        report.append("## Key Metrics")
        report.append("")
        
        # Top 3 vendors
        top_vendors = sorted(analysis["by_vendor"].items(), key=lambda x: x[1]["total"], reverse=True)[:3]
        report.append("### Top 3 Vendors (Consolidated)")
        for i, (vendor, data) in enumerate(top_vendors, 1):
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            report.append(f"{i}. **{vendor}**: ${data['total']:,.2f} ({percentage:.1f}%)")
        report.append("")
        
        # Top 3 companies
        top_companies = sorted(analysis["by_company"].items(), key=lambda x: x[1]["total"], reverse=True)[:3]
        report.append("### Top 3 Companies")
        for i, (company, data) in enumerate(top_companies, 1):
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            report.append(f"{i}. **{company}**: ${data['total']:,.2f} ({percentage:.1f}%)")
        report.append("")
        
        # Category breakdown
        report.append("### Spending by Category")
        for category, data in sorted(analysis["by_category"].items(), key=lambda x: x[1]["total"], reverse=True):
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            report.append(f"- **{category.replace('_', ' ').title()}**: ${data['total']:,.2f} ({percentage:.1f}%)")
        report.append("")
        
        # Historical Analysis
        report.append("## Historical Analysis")
        report.append("")
        for year in sorted(analysis["by_year"].keys()):
            year_data = analysis["by_year"][year]
            report.append(f"### {year}")
            report.append(f"- **Total Spend**: ${year_data['total']:,.2f}")
            
            # Top vendor for the year
            if year_data["vendors"]:
                top_vendor = max(year_data["vendors"].items(), key=lambda x: x[1])
                report.append(f"- **Top Vendor**: {top_vendor[0]} (${top_vendor[1]:,.2f})")
            
            # Top company for the year
            if year_data["companies"]:
                top_company = max(year_data["companies"].items(), key=lambda x: x[1])
                report.append(f"- **Top Company**: {top_company[0]} (${top_company[1]:,.2f})")
            report.append("")
        
        # Cost Optimization Opportunities
        report.append("## Cost Optimization Opportunities")
        report.append("")
        
        if analysis["recommendations"]:
            total_potential_savings = 0
            for i, rec in enumerate(analysis["recommendations"], 1):
                priority_icon = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
                report.append(f"### {i}. {priority_icon} {rec['type'].replace('_', ' ').title()}")
                report.append(f"**{rec['message']}**")
                if "potential_savings" in rec:
                    report.append(f"*Potential Annual Savings: ${rec['potential_savings']:,.2f}*")
                    total_potential_savings += rec["potential_savings"]
                report.append("")
            
            report.append(f"### Total Potential Annual Savings: ${total_potential_savings:,.2f}")
        else:
            report.append("No specific optimization opportunities identified at this time.")
        report.append("")
        
        # Primary Targets for Optimization
        report.append("## Primary Targets for Optimization")
        report.append("")
        
        # Find highest spending vendor
        if analysis["by_vendor"]:
            highest_vendor = max(analysis["by_vendor"].items(), key=lambda x: x[1]["total"])
            vendor_percentage = (highest_vendor[1]["total"] / analysis["summary"]["total_spend"]) * 100
            report.append(f"1. **{highest_vendor[0]}** - ${highest_vendor[1]['total']:,.2f} ({vendor_percentage:.1f}% of total)")
        
        # Find highest spending category
        if analysis["by_category"]:
            highest_category = max(analysis["by_category"].items(), key=lambda x: x[1]["total"])
            category_percentage = (highest_category[1]["total"] / analysis["summary"]["total_spend"]) * 100
            report.append(f"2. **{highest_category[0].replace('_', ' ').title()}** - ${highest_category[1]['total']:,.2f} ({category_percentage:.1f}% of total)")
        
        # Find highest spending company
        if analysis["by_company"]:
            highest_company = max(analysis["by_company"].items(), key=lambda x: x[1]["total"])
            company_percentage = (highest_company[1]["total"] / analysis["summary"]["total_spend"]) * 100
            report.append(f"3. **{highest_company[0]}** - ${highest_company[1]['total']:,.2f} ({company_percentage:.1f}% of total)")
        report.append("")
        
        # Recommended Actions
        report.append("## Recommended Actions")
        report.append("")
        report.append("1. **Immediate (Next 30 Days)**")
        report.append("   - Review contracts with top 3 vendors")
        report.append("   - Audit usage patterns for highest-spending categories")
        report.append("   - Identify unused or underutilized licenses")
        report.append("")
        report.append("2. **Short-term (Next 90 Days)**")
        report.append("   - Negotiate better rates with major vendors")
        report.append("   - Implement usage monitoring and alerts")
        report.append("   - Develop vendor consolidation strategy")
        report.append("")
        report.append("3. **Long-term (Next 6 Months)**")
        report.append("   - Establish centralized license management")
        report.append("   - Implement automated renewal tracking")
        report.append("   - Develop cost optimization policies")
        report.append("")
        
        # Success Metrics
        report.append("## Success Metrics")
        report.append("")
        report.append("- **Target**: 15-20% reduction in annual licensing costs")
        report.append("- **Timeline**: 12 months")
        report.append("- **Key Indicators**:")
        report.append("  - Reduced average invoice size")
        report.append("  - Fewer vendor relationships")
        report.append("  - Increased license utilization rates")
        report.append("  - Improved contract terms")
        
        return "\n".join(report)
    
    def run_report(self):
        """Run the complete report generation."""
        print("Generating Simple Executive Report...")
        print("Using intelligent vendor consolidation and company extraction...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Generate analysis
        analysis = self.generate_executive_report()
        
        if not analysis:
            print("Report generation failed!")
            return
        
        # Create report
        report = self.create_report(analysis)
        
        # Save markdown report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON data
        with open(self.json_output, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"Simple executive report completed!")
        print(f"Report saved to: {self.output_file}")
        print(f"JSON data saved to: {self.json_output}")
        print(f"Total spend analyzed: ${analysis['summary']['total_spend']:,.2f}")
        print(f"Vendors consolidated: {analysis['summary']['vendor_count']}")
        print(f"Companies identified: {analysis['summary']['company_count']}")

def main():
    """Main execution function."""
    reporter = SimpleExecutiveReport()
    reporter.run_report()

if __name__ == "__main__":
    main() 