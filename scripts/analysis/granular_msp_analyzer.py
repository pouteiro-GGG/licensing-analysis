#!/usr/bin/env python3
"""
Granular MSP Service Analyzer
Provides detailed breakdown of services resold by MSPs with intelligent vendor consolidation
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

class GranularMSPAnalyzer:
    def __init__(self):
        self.data_file = "reports/executive/cleaned_licensing_data_20250725.json"
        self.output_file = "reports/executive/granular_msp_analysis_20250725.md"
        self.json_output = "reports/executive/granular_msp_analysis_20250725.json"
        
        # MSP vendors that resell services
        self.msp_vendors = {
            "synoptek": "Synoptek",
            "synoptek, llc": "Synoptek",
            "synoptek llc": "Synoptek"
        }
        
        # Service patterns to identify underlying services
        self.service_patterns = {
            "azure": ["azure", "microsoft azure", "cloud platform", "virtual machine", "vm", "storage", "database"],
            "office365": ["office 365", "o365", "microsoft 365", "exchange", "sharepoint", "teams", "outlook"],
            "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "rds"],
            "google_cloud": ["google cloud", "gcp", "compute engine", "cloud storage", "bigquery"],
            "security": ["security", "antivirus", "firewall", "endpoint protection", "threat detection"],
            "backup": ["backup", "disaster recovery", "data protection", "replication"],
            "monitoring": ["monitoring", "alerting", "logging", "observability", "performance"],
            "support": ["support", "maintenance", "technical support", "help desk"],
            "licensing": ["license", "licensing", "subscription", "per user", "per seat"],
            "consulting": ["consulting", "professional services", "implementation", "migration"]
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
    
    def identify_service_from_line_items(self, line_items):
        """Identify underlying services from line item descriptions."""
        if not line_items:
            return []
        
        # Handle both string and list formats
        if isinstance(line_items, list):
            # Join list items into a single string
            line_items_text = " ".join(str(item) for item in line_items)
        else:
            line_items_text = str(line_items)
        
        identified_services = []
        line_items_lower = line_items_text.lower()
        
        for service_type, patterns in self.service_patterns.items():
            for pattern in patterns:
                if pattern in line_items_lower:
                    identified_services.append(service_type)
                    break
        
        return list(set(identified_services))  # Remove duplicates
    
    def analyze_msp_services(self):
        """Analyze MSP services with granular breakdown."""
        if not os.path.exists(self.data_file):
            print(f"Error: Data file {self.data_file} not found!")
            return None
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        print(f"Analyzing {len(data)} records for granular MSP service breakdown...")
        
        # Initialize analysis structures
        analysis = {
            "summary": {},
            "msp_services": defaultdict(lambda: {
                "total_spend": 0,
                "invoice_count": 0,
                "companies": defaultdict(float),
                "services": defaultdict(lambda: {"spend": 0, "invoices": 0}),
                "line_items": []
            }),
            "service_breakdown": defaultdict(lambda: {
                "total_spend": 0,
                "msp_vendors": defaultdict(float),
                "companies": defaultdict(float)
            }),
            "company_msp_usage": defaultdict(lambda: {
                "total_spend": 0,
                "msp_vendors": defaultdict(float),
                "services": defaultdict(float)
            })
        }
        
        total_msp_spend = 0
        msp_invoice_count = 0
        
        # Process each record
        for item in data:
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('total_amount', 0)
            line_items = item.get('line_items', '')
            bill_to = item.get('bill_to', '')
            
            # Apply intelligent consolidation
            consolidated_vendor = self.consolidate_vendor_name(vendor)
            company = self.extract_company_from_bill_to(bill_to)
            
            # Check if this is an MSP vendor
            if consolidated_vendor.lower() in [msp.lower() for msp in self.msp_vendors.values()]:
                total_msp_spend += amount
                msp_invoice_count += 1
                
                # Identify underlying services
                identified_services = self.identify_service_from_line_items(line_items)
                
                # Update MSP services analysis
                analysis["msp_services"][consolidated_vendor]["total_spend"] += amount
                analysis["msp_services"][consolidated_vendor]["invoice_count"] += 1
                analysis["msp_services"][consolidated_vendor]["companies"][company] += amount
                
                # Add line items for detailed analysis
                if line_items:
                    analysis["msp_services"][consolidated_vendor]["line_items"].append({
                        "amount": amount,
                        "company": company,
                        "description": line_items,
                        "services": identified_services
                    })
                
                # Update service breakdown
                for service in identified_services:
                    analysis["msp_services"][consolidated_vendor]["services"][service]["spend"] += amount
                    analysis["msp_services"][consolidated_vendor]["services"][service]["invoices"] += 1
                    
                    analysis["service_breakdown"][service]["total_spend"] += amount
                    analysis["service_breakdown"][service]["msp_vendors"][consolidated_vendor] += amount
                    analysis["service_breakdown"][service]["companies"][company] += amount
                
                # Update company MSP usage
                analysis["company_msp_usage"][company]["total_spend"] += amount
                analysis["company_msp_usage"][company]["msp_vendors"][consolidated_vendor] += amount
                for service in identified_services:
                    analysis["company_msp_usage"][company]["services"][service] += amount
        
        # Calculate summary metrics
        analysis["summary"]["total_msp_spend"] = total_msp_spend
        analysis["summary"]["msp_invoice_count"] = msp_invoice_count
        analysis["summary"]["msp_vendors_count"] = len(analysis["msp_services"])
        analysis["summary"]["companies_using_msp"] = len(analysis["company_msp_usage"])
        analysis["summary"]["services_identified"] = len(analysis["service_breakdown"])
        
        return analysis
    
    def generate_granular_report(self, analysis):
        """Generate comprehensive granular MSP report."""
        if not analysis:
            return "No analysis data available."
        
        report = []
        report.append("# Granular MSP Service Analysis")
        report.append(f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total MSP Spend**: ${analysis['summary']['total_msp_spend']:,.2f}")
        report.append(f"- **MSP Invoices**: {analysis['summary']['msp_invoice_count']:,}")
        report.append(f"- **MSP Vendors**: {analysis['summary']['msp_vendors_count']}")
        report.append(f"- **Companies Using MSPs**: {analysis['summary']['companies_using_msp']}")
        report.append(f"- **Services Identified**: {analysis['summary']['services_identified']}")
        report.append("")
        
        # MSP Vendor Breakdown
        report.append("## MSP Vendor Breakdown")
        report.append("")
        
        for msp_vendor, data in sorted(analysis["msp_services"].items(), key=lambda x: x[1]["total_spend"], reverse=True):
            report.append(f"### {msp_vendor}")
            report.append(f"- **Total Spend**: ${data['total_spend']:,.2f}")
            report.append(f"- **Invoice Count**: {data['invoice_count']}")
            report.append("")
            
            # Services breakdown
            if data["services"]:
                report.append("#### Services Breakdown:")
                for service, service_data in sorted(data["services"].items(), key=lambda x: x[1]["spend"], reverse=True):
                    percentage = (service_data["spend"] / data["total_spend"]) * 100
                    report.append(f"- **{service.replace('_', ' ').title()}**: ${service_data['spend']:,.2f} ({percentage:.1f}%)")
                report.append("")
            
            # Companies served
            if data["companies"]:
                report.append("#### Companies Served:")
                for company, spend in sorted(data["companies"].items(), key=lambda x: x[1], reverse=True):
                    percentage = (spend / data["total_spend"]) * 100
                    report.append(f"- **{company}**: ${spend:,.2f} ({percentage:.1f}%)")
                report.append("")
            
            # Sample line items
            if data["line_items"]:
                report.append("#### Sample Line Items:")
                for item in data["line_items"][:5]:  # Show first 5
                    services_str = ", ".join([s.replace('_', ' ').title() for s in item["services"]]) if item["services"] else "Uncategorized"
                    report.append(f"- ${item['amount']:,.2f} - {item['description'][:100]}... (Services: {services_str})")
                report.append("")
        
        # Service Type Analysis
        report.append("## Service Type Analysis")
        report.append("")
        
        for service, data in sorted(analysis["service_breakdown"].items(), key=lambda x: x[1]["total_spend"], reverse=True):
            report.append(f"### {service.replace('_', ' ').title()}")
            report.append(f"- **Total Spend**: ${data['total_spend']:,.2f}")
            report.append("")
            
            # MSP vendors providing this service
            if data["msp_vendors"]:
                report.append("#### MSP Vendors:")
                for vendor, spend in sorted(data["msp_vendors"].items(), key=lambda x: x[1], reverse=True):
                    percentage = (spend / data["total_spend"]) * 100
                    report.append(f"- **{vendor}**: ${spend:,.2f} ({percentage:.1f}%)")
                report.append("")
            
            # Companies using this service
            if data["companies"]:
                report.append("#### Companies Using This Service:")
                for company, spend in sorted(data["companies"].items(), key=lambda x: x[1], reverse=True):
                    percentage = (spend / data["total_spend"]) * 100
                    report.append(f"- **{company}**: ${spend:,.2f} ({percentage:.1f}%)")
                report.append("")
        
        # Company MSP Usage
        report.append("## Company MSP Usage")
        report.append("")
        
        for company, data in sorted(analysis["company_msp_usage"].items(), key=lambda x: x[1]["total_spend"], reverse=True):
            report.append(f"### {company}")
            report.append(f"- **Total MSP Spend**: ${data['total_spend']:,.2f}")
            report.append("")
            
            # MSP vendors used
            if data["msp_vendors"]:
                report.append("#### MSP Vendors Used:")
                for vendor, spend in sorted(data["msp_vendors"].items(), key=lambda x: x[1], reverse=True):
                    percentage = (spend / data["total_spend"]) * 100
                    report.append(f"- **{vendor}**: ${spend:,.2f} ({percentage:.1f}%)")
                report.append("")
            
            # Services used
            if data["services"]:
                report.append("#### Services Used:")
                for service, spend in sorted(data["services"].items(), key=lambda x: x[1], reverse=True):
                    percentage = (spend / data["total_spend"]) * 100
                    report.append(f"- **{service.replace('_', ' ').title()}**: ${spend:,.2f} ({percentage:.1f}%)")
                report.append("")
        
        # Key Insights
        report.append("## Key Insights")
        report.append("")
        
        # Largest MSP vendor
        if analysis["msp_services"]:
            largest_msp = max(analysis["msp_services"].items(), key=lambda x: x[1]["total_spend"])
            report.append(f"- **Largest MSP Vendor**: {largest_msp[0]} (${largest_msp[1]['total_spend']:,.2f})")
        
        # Most used service
        if analysis["service_breakdown"]:
            most_used_service = max(analysis["service_breakdown"].items(), key=lambda x: x[1]["total_spend"])
            report.append(f"- **Most Used Service**: {most_used_service[0].replace('_', ' ').title()} (${most_used_service[1]['total_spend']:,.2f})")
        
        # Company with highest MSP spend
        if analysis["company_msp_usage"]:
            highest_msp_company = max(analysis["company_msp_usage"].items(), key=lambda x: x[1]["total_spend"])
            report.append(f"- **Company with Highest MSP Spend**: {highest_msp_company[0]} (${highest_msp_company[1]['total_spend']:,.2f})")
        
        # Service distribution
        if analysis["service_breakdown"]:
            total_service_spend = sum(data["total_spend"] for data in analysis["service_breakdown"].values())
            report.append(f"- **Total Service Spend**: ${total_service_spend:,.2f}")
            report.append("- **Service Distribution**:")
            for service, data in sorted(analysis["service_breakdown"].items(), key=lambda x: x[1]["total_spend"], reverse=True):
                percentage = (data["total_spend"] / total_service_spend) * 100
                report.append(f"  - {service.replace('_', ' ').title()}: {percentage:.1f}%")
        
        return "\n".join(report)
    
    def run_analysis(self):
        """Run the complete granular MSP analysis."""
        print("Starting Granular MSP Service Analysis...")
        print("Using intelligent vendor consolidation and company extraction...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Run analysis
        analysis = self.analyze_msp_services()
        
        if not analysis:
            print("Analysis failed!")
            return
        
        # Generate report
        report = self.generate_granular_report(analysis)
        
        # Save markdown report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON data
        with open(self.json_output, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"Granular MSP analysis completed!")
        print(f"Report saved to: {self.output_file}")
        print(f"JSON data saved to: {self.json_output}")
        print(f"Total MSP spend analyzed: ${analysis['summary']['total_msp_spend']:,.2f}")
        print(f"MSP vendors identified: {analysis['summary']['msp_vendors_count']}")
        print(f"Services identified: {analysis['summary']['services_identified']}")

def main():
    """Main execution function."""
    analyzer = GranularMSPAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 