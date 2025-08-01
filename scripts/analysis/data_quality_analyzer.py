#!/usr/bin/env python3
"""
Data Quality Analyzer
Cleans data by removing duplicates and standardizing vendor names with intelligent consolidation
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

class DataQualityAnalyzer:
    def __init__(self):
        self.data_file = "reports/executive/cleaned_licensing_data_20250725.json"
        self.output_file = "reports/executive/data_quality_analysis_20250725.md"
        self.cleaned_output = "reports/executive/cleaned_licensing_data_20250725.json"
        self.json_output = "reports/executive/data_quality_analysis_20250725.json"
    
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
    
    def clean_data(self):
        """Clean data by removing duplicates and standardizing names."""
        if not os.path.exists(self.data_file):
            print(f"Error: Data file {self.data_file} not found!")
            return None
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        print(f"Cleaning {len(data)} records with intelligent vendor consolidation...")
        
        # Initialize cleaning analysis
        cleaning_analysis = {
            "original_count": len(data),
            "duplicates_removed": 0,
            "vendors_consolidated": {},
            "companies_consolidated": {},
            "cleaned_data": [],
            "quality_metrics": {}
        }
        
        # Track unique records to avoid duplicates
        seen_records = set()
        vendor_mapping = {}
        company_mapping = {}
        
        for item in data:
            # Create a unique key for duplicate detection
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('total_amount', 0)
            date = item.get('invoice_date', '')
            bill_to = item.get('bill_to', '')
            
            # Create unique identifier
            record_key = f"{vendor}_{amount}_{date}_{bill_to}"
            
            if record_key in seen_records:
                cleaning_analysis["duplicates_removed"] += 1
                continue
            
            seen_records.add(record_key)
            
            # Apply intelligent consolidation
            original_vendor = vendor
            original_company = self.extract_company_from_bill_to(bill_to)
            
            consolidated_vendor = self.consolidate_vendor_name(vendor)
            consolidated_company = self.extract_company_from_bill_to(bill_to)
            
            # Track vendor consolidation
            if original_vendor != consolidated_vendor:
                if original_vendor not in vendor_mapping:
                    vendor_mapping[original_vendor] = consolidated_vendor
                    cleaning_analysis["vendors_consolidated"][original_vendor] = consolidated_vendor
            
            # Track company consolidation
            if original_company != consolidated_company:
                if original_company not in company_mapping:
                    company_mapping[original_company] = consolidated_company
                    cleaning_analysis["companies_consolidated"][original_company] = consolidated_company
            
            # Create cleaned record
            cleaned_item = item.copy()
            cleaned_item['vendor'] = consolidated_vendor
            cleaned_item['company'] = consolidated_company
            
            cleaning_analysis["cleaned_data"].append(cleaned_item)
        
        # Calculate quality metrics
        cleaning_analysis["quality_metrics"] = {
            "final_count": len(cleaning_analysis["cleaned_data"]),
            "duplicate_rate": (cleaning_analysis["duplicates_removed"] / cleaning_analysis["original_count"]) * 100,
            "vendor_consolidation_count": len(cleaning_analysis["vendors_consolidated"]),
            "company_consolidation_count": len(cleaning_analysis["companies_consolidated"]),
            "data_quality_score": ((len(cleaning_analysis["cleaned_data"]) - cleaning_analysis["duplicates_removed"]) / cleaning_analysis["original_count"]) * 100
        }
        
        return cleaning_analysis
    
    def analyze_clean_data(self, cleaning_analysis):
        """Analyze the cleaned data for insights."""
        if not cleaning_analysis or not cleaning_analysis["cleaned_data"]:
            return None
        
        data = cleaning_analysis["cleaned_data"]
        
        analysis = {
            "summary": {},
            "vendor_analysis": defaultdict(lambda: {"total": 0, "invoices": 0, "companies": set()}),
            "company_analysis": defaultdict(lambda: {"total": 0, "invoices": 0, "vendors": set()}),
            "quality_insights": []
        }
        
        total_spend = 0
        
        for item in data:
            vendor = item.get('vendor', 'Unknown')
            company = item.get('company', 'Unknown Company')
            amount = item.get('total_amount', 0)
            
            total_spend += amount
            
            # Update vendor analysis
            analysis["vendor_analysis"][vendor]["total"] += amount
            analysis["vendor_analysis"][vendor]["invoices"] += 1
            analysis["vendor_analysis"][vendor]["companies"].add(company)
            
            # Update company analysis
            analysis["company_analysis"][company]["total"] += amount
            analysis["company_analysis"][company]["invoices"] += 1
            analysis["company_analysis"][company]["vendors"].add(vendor)
        
        # Calculate summary metrics
        analysis["summary"]["total_spend"] = total_spend
        analysis["summary"]["total_invoices"] = len(data)
        analysis["summary"]["unique_vendors"] = len(analysis["vendor_analysis"])
        analysis["summary"]["unique_companies"] = len(analysis["company_analysis"])
        analysis["summary"]["avg_invoice"] = total_spend / len(data) if data else 0
        
        # Generate quality insights
        analysis["quality_insights"] = self.generate_quality_insights(cleaning_analysis, analysis)
        
        return analysis
    
    def generate_quality_insights(self, cleaning_analysis, analysis):
        """Generate insights about data quality improvements."""
        insights = []
        
        # Duplicate removal insights
        if cleaning_analysis["duplicates_removed"] > 0:
            insights.append({
                "type": "duplicate_removal",
                "message": f"Removed {cleaning_analysis['duplicates_removed']} duplicate records ({cleaning_analysis['quality_metrics']['duplicate_rate']:.1f}% of original data)",
                "impact": "Improved data accuracy and reduced inflated spend calculations"
            })
        
        # Vendor consolidation insights
        if cleaning_analysis["quality_metrics"]["vendor_consolidation_count"] > 0:
            insights.append({
                "type": "vendor_consolidation",
                "message": f"Consolidated {cleaning_analysis['quality_metrics']['vendor_consolidation_count']} vendor name variations",
                "impact": "Better vendor spend analysis and reduced fragmentation"
            })
        
        # Company consolidation insights
        if cleaning_analysis["quality_metrics"]["company_consolidation_count"] > 0:
            insights.append({
                "type": "company_consolidation",
                "message": f"Consolidated {cleaning_analysis['quality_metrics']['company_consolidation_count']} company name variations",
                "impact": "Improved company-level spend analysis"
            })
        
        # Data quality score insights
        quality_score = cleaning_analysis["quality_metrics"]["data_quality_score"]
        if quality_score >= 95:
            insights.append({
                "type": "quality_score",
                "message": f"Excellent data quality score: {quality_score:.1f}%",
                "impact": "High confidence in analysis results"
            })
        elif quality_score >= 85:
            insights.append({
                "type": "quality_score",
                "message": f"Good data quality score: {quality_score:.1f}%",
                "impact": "Reliable analysis results with minor caveats"
            })
        else:
            insights.append({
                "type": "quality_score",
                "message": f"Data quality score needs improvement: {quality_score:.1f}%",
                "impact": "Consider additional data cleaning steps"
            })
        
        return insights
    
    def generate_clean_report(self, cleaning_analysis, data_analysis):
        """Generate comprehensive data quality report."""
        if not cleaning_analysis:
            return "No cleaning analysis data available."
        
        report = []
        report.append("# Data Quality Analysis Report")
        report.append(f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Original Records**: {cleaning_analysis['original_count']:,}")
        report.append(f"- **Final Records**: {cleaning_analysis['quality_metrics']['final_count']:,}")
        report.append(f"- **Duplicates Removed**: {cleaning_analysis['duplicates_removed']:,}")
        report.append(f"- **Data Quality Score**: {cleaning_analysis['quality_metrics']['data_quality_score']:.1f}%")
        report.append(f"- **Vendors Consolidated**: {cleaning_analysis['quality_metrics']['vendor_consolidation_count']}")
        report.append(f"- **Companies Consolidated**: {cleaning_analysis['quality_metrics']['company_consolidation_count']}")
        report.append("")
        
        # Data Quality Metrics
        report.append("## Data Quality Metrics")
        report.append("")
        report.append("| Metric | Value | Impact |")
        report.append("|--------|-------|--------|")
        report.append(f"| Duplicate Rate | {cleaning_analysis['quality_metrics']['duplicate_rate']:.1f}% | Removed inflated counts |")
        report.append(f"| Vendor Consolidation | {cleaning_analysis['quality_metrics']['vendor_consolidation_count']} | Improved vendor analysis |")
        report.append(f"| Company Consolidation | {cleaning_analysis['quality_metrics']['company_consolidation_count']} | Better company insights |")
        report.append(f"| Data Quality Score | {cleaning_analysis['quality_metrics']['data_quality_score']:.1f}% | Overall confidence level |")
        report.append("")
        
        # Vendor Consolidation Details
        if cleaning_analysis["vendors_consolidated"]:
            report.append("## Vendor Consolidation Details")
            report.append("")
            report.append("| Original Name | Consolidated Name |")
            report.append("|---------------|-------------------|")
            for original, consolidated in cleaning_analysis["vendors_consolidated"].items():
                report.append(f"| {original} | {consolidated} |")
            report.append("")
        
        # Company Consolidation Details
        if cleaning_analysis["companies_consolidated"]:
            report.append("## Company Consolidation Details")
            report.append("")
            report.append("| Original Name | Consolidated Name |")
            report.append("|---------------|-------------------|")
            for original, consolidated in cleaning_analysis["companies_consolidated"].items():
                report.append(f"| {original} | {consolidated} |")
            report.append("")
        
        # Quality Insights
        if data_analysis and data_analysis["quality_insights"]:
            report.append("## Quality Insights")
            report.append("")
            for insight in data_analysis["quality_insights"]:
                report.append(f"### {insight['type'].replace('_', ' ').title()}")
                report.append(f"**{insight['message']}**")
                report.append(f"*Impact: {insight['impact']}*")
                report.append("")
        
        # Cleaned Data Summary
        if data_analysis:
            report.append("## Cleaned Data Summary")
            report.append("")
            report.append(f"- **Total Spend**: ${data_analysis['summary']['total_spend']:,.2f}")
            report.append(f"- **Total Invoices**: {data_analysis['summary']['total_invoices']:,}")
            report.append(f"- **Unique Vendors**: {data_analysis['summary']['unique_vendors']}")
            report.append(f"- **Unique Companies**: {data_analysis['summary']['unique_companies']}")
            report.append(f"- **Average Invoice**: ${data_analysis['summary']['avg_invoice']:,.2f}")
            report.append("")
            
            # Top vendors after cleaning
            report.append("### Top 5 Vendors (After Consolidation)")
            top_vendors = sorted(data_analysis["vendor_analysis"].items(), key=lambda x: x[1]["total"], reverse=True)[:5]
            for i, (vendor, data) in enumerate(top_vendors, 1):
                percentage = (data["total"] / data_analysis["summary"]["total_spend"]) * 100
                report.append(f"{i}. **{vendor}**: ${data['total']:,.2f} ({percentage:.1f}%) - {data['invoices']} invoices")
            report.append("")
            
            # Top companies after cleaning
            report.append("### Top 5 Companies (After Consolidation)")
            top_companies = sorted(data_analysis["company_analysis"].items(), key=lambda x: x[1]["total"], reverse=True)[:5]
            for i, (company, data) in enumerate(top_companies, 1):
                percentage = (data["total"] / data_analysis["summary"]["total_spend"]) * 100
                report.append(f"{i}. **{company}**: ${data['total']:,.2f} ({percentage:.1f}%) - {data['invoices']} invoices")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        report.append("1. **Data Collection**: Implement standardized vendor naming conventions")
        report.append("2. **Duplicate Prevention**: Add validation checks during data entry")
        report.append("3. **Regular Audits**: Schedule monthly data quality reviews")
        report.append("4. **Automated Cleaning**: Implement automated data cleaning processes")
        report.append("5. **Training**: Educate teams on proper data entry practices")
        
        return "\n".join(report)
    
    def run_analysis(self):
        """Run the complete data quality analysis."""
        print("Starting Data Quality Analysis...")
        print("Using intelligent vendor consolidation and company extraction...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Clean data
        cleaning_analysis = self.clean_data()
        
        if not cleaning_analysis:
            print("Data cleaning failed!")
            return
        
        # Analyze cleaned data
        data_analysis = self.analyze_clean_data(cleaning_analysis)
        
        # Generate report
        report = self.generate_clean_report(cleaning_analysis, data_analysis)
        
        # Save markdown report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save cleaned data
        with open(self.cleaned_output, 'w', encoding='utf-8') as f:
            json.dump(cleaning_analysis["cleaned_data"], f, indent=2, default=str)
        
        # Save analysis data
        analysis_data = {
            "cleaning_analysis": cleaning_analysis,
            "data_analysis": data_analysis
        }
        with open(self.json_output, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        print(f"Data quality analysis completed!")
        print(f"Report saved to: {self.output_file}")
        print(f"Cleaned data saved to: {self.cleaned_output}")
        print(f"Analysis data saved to: {self.json_output}")
        print(f"Original records: {cleaning_analysis['original_count']:,}")
        print(f"Final records: {cleaning_analysis['quality_metrics']['final_count']:,}")
        print(f"Duplicates removed: {cleaning_analysis['duplicates_removed']:,}")
        print(f"Data quality score: {cleaning_analysis['quality_metrics']['data_quality_score']:.1f}%")

def main():
    """Main execution function."""
    analyzer = DataQualityAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 