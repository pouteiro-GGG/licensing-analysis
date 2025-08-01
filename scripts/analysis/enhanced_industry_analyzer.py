#!/usr/bin/env python3
"""
Enhanced Industry Benchmark Analyzer
Performs analytical comparison against industry standards with intelligent vendor consolidation
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

class EnhancedIndustryAnalyzer:
    def __init__(self):
        self.data_file = "reports/executive/cleaned_licensing_data_20250725.json"
        self.output_file = "reports/executive/enhanced_industry_analysis_20250725.md"
        self.json_output = "reports/executive/enhanced_industry_analysis_20250725.json"
        
        # Industry benchmark data (realistic percentages of total IT budget)
        self.industry_benchmarks = {
            "it_services": {"low": 0.15, "high": 0.30, "typical": 0.22},
            "development_tools": {"low": 0.05, "high": 0.12, "typical": 0.08},
            "enterprise_software": {"low": 0.12, "high": 0.25, "typical": 0.18},
            "security_software": {"low": 0.08, "high": 0.15, "typical": 0.12},
            "cloud_services": {"low": 0.10, "high": 0.18, "typical": 0.14},
            "corporate_software": {"low": 0.05, "high": 0.10, "typical": 0.07}
        }
        
        # Vendor categories
        self.vendor_categories = {
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
        
        for vendor_key, category in self.vendor_categories.items():
            if vendor_key in vendor_lower:
                return category
        
        return "it_services"
    
    def get_realistic_benchmark(self, category, total_spend):
        """Get realistic benchmark for a category."""
        if category in self.industry_benchmarks:
            benchmark = self.industry_benchmarks[category]
            return {
                "low": total_spend * benchmark["low"],
                "high": total_spend * benchmark["high"],
                "typical": total_spend * benchmark["typical"]
            }
        else:
            # Default benchmark for unknown categories
            return {
                "low": total_spend * 0.10,
                "high": total_spend * 0.20,
                "typical": total_spend * 0.15
            }
    
    def calculate_realistic_variance(self, actual_spend, benchmark):
        """Calculate variance from benchmark."""
        if benchmark["typical"] == 0:
            return 0
        
        variance = ((actual_spend - benchmark["typical"]) / benchmark["typical"]) * 100
        
        if actual_spend < benchmark["low"]:
            status = "Below Benchmark"
        elif actual_spend > benchmark["high"]:
            status = "Above Benchmark"
        else:
            status = "Within Benchmark"
        
        return variance, status
    
    def analyze_with_historical_data(self):
        """Analyze data with historical context and intelligent consolidation."""
        if not os.path.exists(self.data_file):
            print(f"Error: Data file {self.data_file} not found!")
            return None
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        print(f"Analyzing {len(data)} records with intelligent vendor consolidation...")
        
        # Initialize analysis structures
        analysis = {
            "summary": {},
            "by_year": defaultdict(lambda: {"total": 0, "categories": defaultdict(float), "vendors": defaultdict(float), "companies": defaultdict(float)}),
            "by_category": defaultdict(lambda: {"total": 0, "vendors": defaultdict(float), "companies": defaultdict(float), "yearly": defaultdict(float)}),
            "by_vendor": defaultdict(lambda: {"total": 0, "categories": defaultdict(float), "companies": defaultdict(float), "yearly": defaultdict(float)}),
            "by_company": defaultdict(lambda: {"total": 0, "categories": defaultdict(float), "vendors": defaultdict(float), "yearly": defaultdict(float)}),
            "benchmarks": {},
            "recommendations": []
        }
        
        total_spend = 0
        
        # Process each record
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
            analysis["by_category"][category]["yearly"][year] += amount
            
            # Update vendor analysis
            analysis["by_vendor"][consolidated_vendor]["total"] += amount
            analysis["by_vendor"][consolidated_vendor]["categories"][category] += amount
            analysis["by_vendor"][consolidated_vendor]["companies"][company] += amount
            analysis["by_vendor"][consolidated_vendor]["yearly"][year] += amount
            
            # Update company analysis
            analysis["by_company"][company]["total"] += amount
            analysis["by_company"][company]["categories"][category] += amount
            analysis["by_company"][company]["vendors"][consolidated_vendor] += amount
            analysis["by_company"][company]["yearly"][year] += amount
        
        # Calculate benchmarks and variances
        analysis["summary"]["total_spend"] = total_spend
        analysis["summary"]["total_invoices"] = len(data)
        analysis["summary"]["years_analyzed"] = sorted(analysis["by_year"].keys())
        analysis["summary"]["vendor_count"] = len(analysis["by_vendor"])
        analysis["summary"]["company_count"] = len(analysis["by_company"])
        analysis["summary"]["category_count"] = len(analysis["by_category"])
        
        # Calculate benchmarks for each category
        for category, data in analysis["by_category"].items():
            benchmark = self.get_realistic_benchmark(category, total_spend)
            variance, status = self.calculate_realistic_variance(data["total"], benchmark)
            
            analysis["benchmarks"][category] = {
                "actual_spend": data["total"],
                "benchmark": benchmark,
                "variance_percentage": variance,
                "status": status,
                "percentage_of_total": (data["total"] / total_spend) * 100 if total_spend > 0 else 0
            }
        
        # Generate recommendations
        analysis["recommendations"] = self.generate_recommendations(analysis)
        
        return analysis
    
    def generate_recommendations(self, analysis):
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Check for categories above benchmark
        for category, benchmark_data in analysis["benchmarks"].items():
            if benchmark_data["status"] == "Above Benchmark":
                recommendations.append({
                    "type": "cost_reduction",
                    "category": category,
                    "priority": "high" if benchmark_data["variance_percentage"] > 50 else "medium",
                    "message": f"Consider reducing {category.replace('_', ' ').title()} spending. Currently {benchmark_data['variance_percentage']:.1f}% above industry benchmark.",
                    "potential_savings": benchmark_data["actual_spend"] - benchmark_data["benchmark"]["typical"]
                })
        
        # Check for vendor consolidation opportunities
        top_vendors = sorted(analysis["by_vendor"].items(), key=lambda x: x[1]["total"], reverse=True)[:5]
        for vendor, data in top_vendors:
            if data["total"] > analysis["summary"]["total_spend"] * 0.15:  # More than 15% of total
                recommendations.append({
                    "type": "vendor_consolidation",
                    "vendor": vendor,
                    "priority": "medium",
                    "message": f"Consider consolidating {vendor} services or negotiating better rates. Represents {data['total']/analysis['summary']['total_spend']*100:.1f}% of total spend.",
                    "potential_savings": data["total"] * 0.10  # Assume 10% savings potential
                })
        
        # Check for company-specific insights
        for company, data in analysis["by_company"].items():
            if data["total"] > analysis["summary"]["total_spend"] * 0.20:  # More than 20% of total
                recommendations.append({
                    "type": "company_optimization",
                    "company": company,
                    "priority": "medium",
                    "message": f"Review {company} licensing needs. Represents {data['total']/analysis['summary']['total_spend']*100:.1f}% of total spend.",
                    "potential_savings": data["total"] * 0.05  # Assume 5% savings potential
                })
        
        return recommendations
    
    def generate_enhanced_report(self, analysis):
        """Generate comprehensive markdown report."""
        if not analysis:
            return "No analysis data available."
        
        report = []
        report.append("# Enhanced Industry Benchmark Analysis")
        report.append(f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total Spend**: ${analysis['summary']['total_spend']:,.2f}")
        report.append(f"- **Total Invoices**: {analysis['summary']['total_invoices']:,}")
        report.append(f"- **Years Analyzed**: {', '.join(map(str, analysis['summary']['years_analyzed']))}")
        report.append(f"- **Vendors (Consolidated)**: {analysis['summary']['vendor_count']}")
        report.append(f"- **Companies**: {analysis['summary']['company_count']}")
        report.append(f"- **Categories**: {analysis['summary']['category_count']}")
        report.append("")
        
        # Benchmark Analysis
        report.append("## Industry Benchmark Analysis")
        report.append("")
        report.append("| Category | Actual Spend | Industry Benchmark | Variance | Status |")
        report.append("|----------|--------------|-------------------|----------|--------|")
        
        for category, benchmark_data in analysis["benchmarks"].items():
            category_name = category.replace('_', ' ').title()
            actual = f"${benchmark_data['actual_spend']:,.2f}"
            benchmark = f"${benchmark_data['benchmark']['typical']:,.2f}"
            variance = f"{benchmark_data['variance_percentage']:+.1f}%"
            status = benchmark_data['status']
            
            report.append(f"| {category_name} | {actual} | {benchmark} | {variance} | {status} |")
        
        report.append("")
        
        # Top Vendors (Consolidated)
        report.append("## Top Vendors (Consolidated)")
        report.append("")
        report.append("| Vendor | Total Spend | % of Total | Top Categories |")
        report.append("|--------|-------------|------------|----------------|")
        
        top_vendors = sorted(analysis["by_vendor"].items(), key=lambda x: x[1]["total"], reverse=True)[:10]
        for vendor, data in top_vendors:
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            top_categories = sorted(data["categories"].items(), key=lambda x: x[1], reverse=True)[:2]
            categories_str = ", ".join([f"{cat.replace('_', ' ').title()}" for cat, _ in top_categories])
            
            report.append(f"| {vendor} | ${data['total']:,.2f} | {percentage:.1f}% | {categories_str} |")
        
        report.append("")
        
        # Company Breakdown
        report.append("## Company Breakdown")
        report.append("")
        report.append("| Company | Total Spend | % of Total | Top Vendors |")
        report.append("|---------|-------------|------------|-------------|")
        
        top_companies = sorted(analysis["by_company"].items(), key=lambda x: x[1]["total"], reverse=True)[:10]
        for company, data in top_companies:
            percentage = (data["total"] / analysis["summary"]["total_spend"]) * 100
            top_vendors = sorted(data["vendors"].items(), key=lambda x: x[1], reverse=True)[:2]
            vendors_str = ", ".join([vendor for vendor, _ in top_vendors])
            
            report.append(f"| {company} | ${data['total']:,.2f} | {percentage:.1f}% | {vendors_str} |")
        
        report.append("")
        
        # Yearly Trends
        report.append("## Yearly Spending Trends")
        report.append("")
        for year in sorted(analysis["by_year"].keys()):
            year_data = analysis["by_year"][year]
            report.append(f"### {year}")
            report.append(f"- **Total**: ${year_data['total']:,.2f}")
            
            # Top categories for the year
            top_categories = sorted(year_data["categories"].items(), key=lambda x: x[1], reverse=True)[:3]
            categories_str = ", ".join([f"{cat.replace('_', ' ').title()}" for cat, _ in top_categories])
            report.append(f"- **Top Categories**: {categories_str}")
            
            # Top vendors for the year
            top_vendors = sorted(year_data["vendors"].items(), key=lambda x: x[1], reverse=True)[:3]
            vendors_str = ", ".join([vendor for vendor, _ in top_vendors])
            report.append(f"- **Top Vendors**: {vendors_str}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        if analysis["recommendations"]:
            for i, rec in enumerate(analysis["recommendations"], 1):
                priority_icon = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
                report.append(f"### {i}. {priority_icon} {rec['type'].replace('_', ' ').title()}")
                report.append(f"**{rec['message']}**")
                if "potential_savings" in rec:
                    report.append(f"*Potential Savings: ${rec['potential_savings']:,.2f}*")
                report.append("")
        else:
            report.append("No specific recommendations at this time.")
        
        # Key Insights
        report.append("## Key Insights")
        report.append("")
        
        # Find categories above benchmark
        above_benchmark = [cat for cat, data in analysis["benchmarks"].items() if data["status"] == "Above Benchmark"]
        if above_benchmark:
            report.append(f"- **Categories Above Benchmark**: {', '.join([cat.replace('_', ' ').title() for cat in above_benchmark])}")
        
        # Find largest vendor
        largest_vendor = max(analysis["by_vendor"].items(), key=lambda x: x[1]["total"])
        report.append(f"- **Largest Vendor**: {largest_vendor[0]} (${largest_vendor[1]['total']:,.2f})")
        
        # Find largest company
        largest_company = max(analysis["by_company"].items(), key=lambda x: x[1]["total"])
        report.append(f"- **Largest Company**: {largest_company[0]} (${largest_company[1]['total']:,.2f})")
        
        # Calculate total potential savings
        total_potential_savings = sum(rec.get("potential_savings", 0) for rec in analysis["recommendations"])
        if total_potential_savings > 0:
            report.append(f"- **Total Potential Savings**: ${total_potential_savings:,.2f}")
        
        return "\n".join(report)
    
    def run_analysis(self):
        """Run the complete analysis and generate reports."""
        print("Starting Enhanced Industry Benchmark Analysis...")
        print("Using intelligent vendor consolidation and company extraction...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Run analysis
        analysis = self.analyze_with_historical_data()
        
        if not analysis:
            print("Analysis failed!")
            return
        
        # Generate markdown report
        report = self.generate_enhanced_report(analysis)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON data for other tools
        with open(self.json_output, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"Enhanced industry analysis completed!")
        print(f"Report saved to: {self.output_file}")
        print(f"JSON data saved to: {self.json_output}")
        print(f"Total spend analyzed: ${analysis['summary']['total_spend']:,.2f}")
        print(f"Vendors consolidated: {analysis['summary']['vendor_count']}")
        print(f"Companies identified: {analysis['summary']['company_count']}")

def main():
    """Main execution function."""
    analyzer = EnhancedIndustryAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 