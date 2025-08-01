#!/usr/bin/env python3
"""
Detailed Category Analyzer
Differentiates between corporate tools/licenses and development tools
Checks for data duplication and provides detailed breakdown
"""

import json
import os
from datetime import datetime
from collections import defaultdict
import re

class DetailedCategoryAnalyzer:
    def __init__(self):
        # Detailed vendor categorization with subcategories
        self.vendor_categories = {
            # IT Services & Consulting
            "synoptek": {"category": "it_services", "subcategory": "managed_services", "type": "service"},
            "synoptek, llc": {"category": "it_services", "subcategory": "managed_services", "type": "service"},
            "harman": {"category": "it_services", "subcategory": "consulting", "type": "service"},
            "markov": {"category": "it_services", "subcategory": "consulting", "type": "service"},
            
            # Development Tools & Platforms
            "atlassian": {"category": "development_tools", "subcategory": "project_management", "type": "license"},
            "github": {"category": "development_tools", "subcategory": "version_control", "type": "license"},
            "gitlab": {"category": "development_tools", "subcategory": "version_control", "type": "license"},
            "visual studio": {"category": "development_tools", "subcategory": "ide", "type": "license"},
            "jetbrains": {"category": "development_tools", "subcategory": "ide", "type": "license"},
            "intellij": {"category": "development_tools", "subcategory": "ide", "type": "license"},
            "pycharm": {"category": "development_tools", "subcategory": "ide", "type": "license"},
            "webstorm": {"category": "development_tools", "subcategory": "ide", "type": "license"},
            
            # Corporate Software & Licenses
            "microsoft": {"category": "corporate_software", "subcategory": "productivity", "type": "license"},
            "office 365": {"category": "corporate_software", "subcategory": "productivity", "type": "license"},
            "microsoft 365": {"category": "corporate_software", "subcategory": "productivity", "type": "license"},
            "oracle": {"category": "corporate_software", "subcategory": "database", "type": "license"},
            "salesforce": {"category": "corporate_software", "subcategory": "crm", "type": "license"},
            "sap": {"category": "corporate_software", "subcategory": "erp", "type": "license"},
            "adobe": {"category": "corporate_software", "subcategory": "creative", "type": "license"},
            "adobe creative": {"category": "corporate_software", "subcategory": "creative", "type": "license"},
            
            # Cloud Services & Infrastructure
            "aws": {"category": "cloud_services", "subcategory": "infrastructure", "type": "service"},
            "amazon": {"category": "cloud_services", "subcategory": "infrastructure", "type": "service"},
            "azure": {"category": "cloud_services", "subcategory": "infrastructure", "type": "service"},
            "google": {"category": "cloud_services", "subcategory": "infrastructure", "type": "service"},
            "gcp": {"category": "cloud_services", "subcategory": "infrastructure", "type": "service"},
            "google cloud": {"category": "cloud_services", "subcategory": "infrastructure", "type": "service"},
            
            # Security Software
            "crowdstrike": {"category": "security_software", "subcategory": "endpoint_protection", "type": "license"},
            "sentinelone": {"category": "security_software", "subcategory": "endpoint_protection", "type": "license"},
            "palo alto": {"category": "security_software", "subcategory": "network_security", "type": "license"},
            "proofpoint": {"category": "security_software", "subcategory": "email_security", "type": "license"},
            "symantec": {"category": "security_software", "subcategory": "endpoint_protection", "type": "license"},
            "mcafee": {"category": "security_software", "subcategory": "endpoint_protection", "type": "license"},
            
            # Communication & Collaboration
            "slack": {"category": "communication", "subcategory": "team_collaboration", "type": "license"},
            "teams": {"category": "communication", "subcategory": "team_collaboration", "type": "license"},
            "zoom": {"category": "communication", "subcategory": "video_conferencing", "type": "license"},
            "webex": {"category": "communication", "subcategory": "video_conferencing", "type": "license"},
            "ringcentral": {"category": "communication", "subcategory": "unified_communications", "type": "license"},
            
            # Data & Analytics
            "tableau": {"category": "data_analytics", "subcategory": "business_intelligence", "type": "license"},
            "power bi": {"category": "data_analytics", "subcategory": "business_intelligence", "type": "license"},
            "snowflake": {"category": "data_analytics", "subcategory": "data_warehouse", "type": "license"},
            "databricks": {"category": "data_analytics", "subcategory": "data_engineering", "type": "license"}
        }
    
    def parse_date(self, date_str):
        """Parse various date formats and extract year."""
        if not date_str or date_str == "Not found":
            return None
        
        # Try to extract year from various formats
        year_patterns = [
            r'(\d{4})',  # 2024, 2025
            r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, date_str)
            if match:
                if len(match.groups()) == 1:
                    return int(match.group(1))
                elif len(match.groups()) == 3:
                    return int(match.group(3))  # Assume last group is year
        
        # Check for month names with years
        if '2024' in date_str:
            return 2024
        elif '2025' in date_str:
            return 2025
        
        return None
    
    def categorize_vendor_detailed(self, vendor_name, line_items=None):
        """Categorize vendor with detailed subcategories."""
        vendor_lower = vendor_name.lower()
        
        # Direct vendor mapping
        for vendor_key, category_info in self.vendor_categories.items():
            if vendor_key in vendor_lower:
                return category_info
        
        # Analyze line items for better categorization
        if line_items:
            line_items_text = " ".join([str(item) for item in line_items]).lower()
            
            # Check for development-related terms
            dev_terms = ["jira", "confluence", "bitbucket", "github", "gitlab", "ide", "development", "coding", "programming"]
            if any(term in line_items_text for term in dev_terms):
                return {"category": "development_tools", "subcategory": "project_management", "type": "license"}
            
            # Check for corporate software terms
            corp_terms = ["office", "365", "microsoft", "adobe", "creative", "productivity", "word", "excel", "powerpoint"]
            if any(term in line_items_text for term in corp_terms):
                return {"category": "corporate_software", "subcategory": "productivity", "type": "license"}
            
            # Check for cloud terms
            cloud_terms = ["aws", "azure", "cloud", "compute", "storage", "database"]
            if any(term in line_items_text for term in cloud_terms):
                return {"category": "cloud_services", "subcategory": "infrastructure", "type": "service"}
        
        # Default to IT services if no specific match
        return {"category": "it_services", "subcategory": "managed_services", "type": "service"}
    
    def check_for_duplicates(self, data):
        """Check for potential duplicate entries."""
        duplicates = []
        seen_entries = {}
        
        for i, item in enumerate(data):
            # Create a unique key based on vendor, amount, and date
            vendor = item.get('vendor', '').lower()
            amount = item.get('total_amount', 0)
            date = item.get('invoice_date', '')
            
            # Create a key that's more flexible for duplicate detection
            key = f"{vendor}_{amount}_{date[:10]}"  # Use first 10 chars of date
            
            if key in seen_entries:
                duplicates.append({
                    'index': i,
                    'original_index': seen_entries[key],
                    'vendor': vendor,
                    'amount': amount,
                    'date': date,
                    'duplicate_key': key
                })
            else:
                seen_entries[key] = i
        
        return duplicates
    
    def analyze_detailed_categories(self, data):
        """Perform detailed category analysis with subcategories."""
        
        # Check for duplicates first
        duplicates = self.check_for_duplicates(data)
        
        # Initialize detailed tracking
        category_breakdown = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        vendor_analysis = defaultdict(lambda: defaultdict(float))
        yearly_analysis = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        # Process each item
        for i, item in enumerate(data):
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('total_amount', 0)
            line_items = item.get('line_items', [])
            year = self.parse_date(item.get('invoice_date', ''))
            
            # Get detailed categorization
            category_info = self.categorize_vendor_detailed(vendor, line_items)
            category = category_info['category']
            subcategory = category_info['subcategory']
            item_type = category_info['type']
            
            # Track by category and subcategory
            category_breakdown[category][subcategory][item_type].append({
                'index': i,
                'vendor': vendor,
                'amount': amount,
                'date': item.get('invoice_date', ''),
                'line_items': line_items,
                'is_duplicate': any(d['index'] == i for d in duplicates)
            })
            
            # Track vendor totals
            vendor_analysis[vendor][category] += amount
            
            # Track yearly analysis
            if year:
                yearly_analysis[year][category][subcategory] += amount
        
        return {
            'category_breakdown': category_breakdown,
            'vendor_analysis': vendor_analysis,
            'yearly_analysis': yearly_analysis,
            'duplicates': duplicates,
            'total_records': len(data),
            'duplicate_count': len(duplicates)
        }
    
    def generate_detailed_report(self, analysis_results):
        """Generate comprehensive detailed analysis report."""
        
        category_breakdown = analysis_results['category_breakdown']
        vendor_analysis = analysis_results['vendor_analysis']
        yearly_analysis = analysis_results['yearly_analysis']
        duplicates = analysis_results['duplicates']
        
        report = f"""
# DETAILED CATEGORY ANALYSIS - LICENSING DATA
**Report Date:** {datetime.now().strftime("%B %d, %Y")}

## 📊 EXECUTIVE SUMMARY
- **Total Records Analyzed:** {analysis_results['total_records']}
- **Potential Duplicates Found:** {analysis_results['duplicate_count']}
- **Categories Identified:** {len(category_breakdown)}
- **Vendors Analyzed:** {len(vendor_analysis)}

## 🔍 DUPLICATE ANALYSIS

### Potential Duplicate Entries
"""
        
        if duplicates:
            report += f"""
**Found {len(duplicates)} potential duplicate entries:**
"""
            for dup in duplicates[:10]:  # Show first 10
                report += f"""
- **Record {dup['index']}** duplicates **Record {dup['original_index']}**
  - Vendor: {dup['vendor']}
  - Amount: ${dup['amount']:,.2f}
  - Date: {dup['date']}
"""
            if len(duplicates) > 10:
                report += f"\n... and {len(duplicates) - 10} more duplicates\n"
        else:
            report += "\n✅ No duplicate entries detected\n"
        
        report += f"""
## 🏢 DETAILED CATEGORY BREAKDOWN

### Category Summary
"""
        
        # Calculate totals by category
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        for category, subcategories in category_breakdown.items():
            for subcategory, types in subcategories.items():
                for item_type, items in types.items():
                    category_total = sum(item['amount'] for item in items)
                    category_totals[category] += category_total
                    category_counts[category] += len(items)
        
        # Sort categories by total spend
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        total_spend = sum(category_totals.values())
        
        for category, total_spend_cat in sorted_categories:
            percentage = (total_spend_cat / total_spend) * 100 if total_spend > 0 else 0
            report += f"""
#### {category.replace('_', ' ').title()}
- **Total Spend:** ${total_spend_cat:,.2f}
- **Percentage of Total:** {percentage:.1f}%
- **Record Count:** {category_counts[category]}
"""
            
            # Show subcategories
            if category in category_breakdown:
                subcategory_totals = defaultdict(float)
                for subcategory, types in category_breakdown[category].items():
                    for item_type, items in types.items():
                        subcategory_totals[subcategory] += sum(item['amount'] for item in items)
                
                for subcategory, sub_total in sorted(subcategory_totals.items(), key=lambda x: x[1], reverse=True):
                    sub_percentage = (sub_total / total_spend_cat) * 100 if total_spend_cat > 0 else 0
                    report += f"""
  - **{subcategory.replace('_', ' ').title()}:** ${sub_total:,.2f} ({sub_percentage:.1f}% of category)
"""
        
        report += f"""
## 📅 YEARLY ANALYSIS
"""
        
        for year in sorted(yearly_analysis.keys()):
            year_total = sum(sum(subcategories.values()) for subcategories in yearly_analysis[year].values())
            report += f"""
### {year}
- **Total Spend:** ${year_total:,.2f}
- **Categories:** {len(yearly_analysis[year])}
"""
            
            for category, subcategories in yearly_analysis[year].items():
                category_total = sum(subcategories.values())
                report += f"""
  - **{category.replace('_', ' ').title()}:** ${category_total:,.2f}
"""
        
        report += f"""
## 🏢 VENDOR ANALYSIS

### Top Vendors by Category
"""
        
        # Group vendors by category
        vendors_by_category = defaultdict(list)
        for vendor, categories in vendor_analysis.items():
            for category, amount in categories.items():
                vendors_by_category[category].append((vendor, amount))
        
        for category in sorted_categories:
            category_name = category[0]
            if category_name in vendors_by_category:
                vendors = sorted(vendors_by_category[category_name], key=lambda x: x[1], reverse=True)
                report += f"""
#### {category_name.replace('_', ' ').title()} Vendors
"""
                for vendor, amount in vendors[:5]:  # Top 5 vendors per category
                    report += f"""
- **{vendor}:** ${amount:,.2f}
"""
        
        report += f"""
## 🎯 DEVELOPMENT TOOLS vs CORPORATE SOFTWARE ANALYSIS

### Development Tools Breakdown
"""
        
        if 'development_tools' in category_breakdown:
            dev_tools = category_breakdown['development_tools']
            dev_total = sum(sum(sum(item['amount'] for item in items) for items in types.values()) for types in dev_tools.values())
            
            report += f"""
- **Total Development Tools Spend:** ${dev_total:,.2f}
- **Percentage of Total:** {(dev_total/total_spend*100):.1f}%
"""
            
            for subcategory, types in dev_tools.items():
                subcategory_total = sum(sum(item['amount'] for item in items) for items in types.values())
                report += f"""
- **{subcategory.replace('_', ' ').title()}:** ${subcategory_total:,.2f}
"""
        else:
            report += "\n- No development tools identified\n"
        
        report += f"""
### Corporate Software Breakdown
"""
        
        if 'corporate_software' in category_breakdown:
            corp_software = category_breakdown['corporate_software']
            corp_total = sum(sum(sum(item['amount'] for item in items) for items in types.values()) for types in corp_software.values())
            
            report += f"""
- **Total Corporate Software Spend:** ${corp_total:,.2f}
- **Percentage of Total:** {(corp_total/total_spend*100):.1f}%
"""
            
            for subcategory, types in corp_software.items():
                subcategory_total = sum(sum(item['amount'] for item in items) for items in types.values())
                report += f"""
- **{subcategory.replace('_', ' ').title()}:** ${subcategory_total:,.2f}
"""
        else:
            report += "\n- No corporate software identified\n"
        
        report += f"""
## 📋 RECOMMENDATIONS

### Data Quality Improvements
1. **Review Duplicate Entries** - {len(duplicates)} potential duplicates found
2. **Standardize Vendor Names** - Ensure consistent vendor naming
3. **Validate Line Items** - Check for missing or incorrect line item data

### Category Optimization
1. **Development Tools** - Review if all tools are actively used
2. **Corporate Software** - Consolidate licenses and negotiate volume discounts
3. **IT Services** - Analyze service scope and negotiate better rates

### Vendor Management
1. **Consolidate Vendors** - Reduce vendor count where possible
2. **Negotiate Volume Discounts** - Leverage total spend for better rates
3. **Review Contract Terms** - Ensure optimal pricing and terms

---
*Detailed Category Analysis Report - {datetime.now().strftime("%B %d, %Y")}*
"""
        
        return report

def main():
    """Generate detailed category analysis report."""
    
    # Load the data
    data_file = "reports/processed_licensing_data.json"
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} records for detailed category analysis")
    
    # Initialize analyzer
    analyzer = DetailedCategoryAnalyzer()
    
    # Perform analysis
    print("🔍 Performing detailed category analysis...")
    analysis_results = analyzer.analyze_detailed_categories(data)
    
    # Generate report
    print("📊 Generating detailed category analysis report...")
    report = analyzer.generate_detailed_report(analysis_results)
    
    # Save report
    reports_dir = "reports/executive"
    os.makedirs(reports_dir, exist_ok=True)
    
    output_file = f"{reports_dir}/detailed_category_analysis_{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Detailed category analysis report saved to: {output_file}")
    
    # Print summary
    category_breakdown = analysis_results['category_breakdown']
    duplicates = analysis_results['duplicates']
    
    print(f"\n📊 Detailed Analysis Summary:")
    print(f"   - Total Records: {analysis_results['total_records']}")
    print(f"   - Potential Duplicates: {len(duplicates)}")
    print(f"   - Categories Identified: {len(category_breakdown)}")
    
    # Show category breakdown
    category_totals = defaultdict(float)
    for category, subcategories in category_breakdown.items():
        for subcategory, types in subcategories.items():
            for item_type, items in types.items():
                category_totals[category] += sum(item['amount'] for item in items)
    
    total_spend = sum(category_totals.values())
    print(f"\n🏢 Category Breakdown:")
    for category, total_spend_cat in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (total_spend_cat / total_spend) * 100 if total_spend > 0 else 0
        print(f"   - {category.replace('_', ' ').title()}: ${total_spend_cat:,.2f} ({percentage:.1f}%)")
    
    if duplicates:
        print(f"\n⚠️ Duplicate Analysis:")
        print(f"   - Found {len(duplicates)} potential duplicate entries")
        print(f"   - Review recommended for data quality")

if __name__ == "__main__":
    main() 