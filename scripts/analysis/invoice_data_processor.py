"""
Invoice Data Processor
Processes data from the existing invoice project cache for licensing analysis
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from config import create_directories

logger = logging.getLogger(__name__)

class InvoiceDataProcessor:
    """
    Processes invoice data from the existing invoice project cache
    and prepares it for licensing analysis.
    """
    
    def __init__(self, invoice_cache_path: str = None):
        """Initialize the invoice data processor."""
        self.invoice_cache_path = invoice_cache_path
        create_directories()
        logger.info(f"Invoice Data Processor initialized with cache path: {invoice_cache_path}")
    
    def load_invoice_cache(self) -> Dict[str, Any]:
        """Load the invoice cache from the existing project."""
        if not self.invoice_cache_path:
            logger.warning("No invoice cache path provided. Please specify a path to the invoice cache file.")
            return {}
        
        if not os.path.exists(self.invoice_cache_path):
            logger.warning(f"Invoice cache file not found: {self.invoice_cache_path}")
            return {}
        
        try:
            with open(self.invoice_cache_path, 'r') as f:
                cache_data = json.load(f)
            logger.info(f"Loaded {len(cache_data)} entries from invoice cache")
            return cache_data
        except Exception as e:
            logger.error(f"Error loading invoice cache: {e}")
            return {}
    
    def extract_licensing_data(self, cache_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract licensing-relevant data from invoice cache."""
        licensing_data = []
        
        for cache_key, invoice_data in cache_data.items():
            if not isinstance(invoice_data, dict) or "line_items" not in invoice_data:
                continue
            
            # Extract basic invoice information
            invoice_info = {
                "cache_key": cache_key,
                "vendor": invoice_data.get("vendor", ""),
                "bill_to": invoice_data.get("bill_to", ""),
                "invoice_date": invoice_data.get("invoice_date", ""),
                "line_items": invoice_data.get("line_items", []),
                "total_amount": sum(item.get("total_amount", 0) for item in invoice_data.get("line_items", [])),
                "extracted_at": datetime.now().isoformat()
            }
            
            # Filter for licensing-relevant invoices
            if self._is_licensing_relevant(invoice_info):
                licensing_data.append(invoice_info)
        
        logger.info(f"Extracted {len(licensing_data)} licensing-relevant invoices")
        return licensing_data
    
    def _is_licensing_relevant(self, invoice_info: Dict[str, Any]) -> bool:
        """Determine if an invoice is relevant for licensing analysis."""
        vendor = invoice_info.get("vendor", "").lower()
        line_items = invoice_info.get("line_items", [])
        
        # Check vendor relevance
        licensing_vendors = [
            "microsoft", "adobe", "vmware", "oracle", "sap", "salesforce", 
            "servicenow", "atlassian", "aws", "google", "azure", "synoptek"
        ]
        
        if any(vendor_name in vendor for vendor_name in licensing_vendors):
            return True
        
        # Check line items for licensing keywords
        licensing_keywords = [
            "license", "licensing", "subscription", "software", "saas", 
            "cloud", "azure", "aws", "office", "365", "adobe", "vmware",
            "oracle", "sap", "salesforce", "servicenow", "atlassian"
        ]
        
        for item in line_items:
            description = item.get("description", "").lower()
            if any(keyword in description for keyword in licensing_keywords):
                return True
        
        return False
    
    def categorize_invoices(self, licensing_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize invoices by vendor and type."""
        categories = {
            "microsoft": [],
            "adobe": [],
            "vmware": [],
            "oracle": [],
            "sap": [],
            "salesforce": [],
            "servicenow": [],
            "atlassian": [],
            "cloud_services": [],
            "professional_services": [],
            "other": []
        }
        
        for invoice in licensing_data:
            vendor = invoice.get("vendor", "").lower()
            
            if "microsoft" in vendor or any("microsoft" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["microsoft"].append(invoice)
            elif "adobe" in vendor or any("adobe" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["adobe"].append(invoice)
            elif "vmware" in vendor or any("vmware" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["vmware"].append(invoice)
            elif "oracle" in vendor or any("oracle" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["oracle"].append(invoice)
            elif "sap" in vendor or any("sap" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["sap"].append(invoice)
            elif "salesforce" in vendor or any("salesforce" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["salesforce"].append(invoice)
            elif "servicenow" in vendor or any("servicenow" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["servicenow"].append(invoice)
            elif "atlassian" in vendor or any("atlassian" in item.get("description", "").lower() for item in invoice.get("line_items", [])):
                categories["atlassian"].append(invoice)
            elif any(keyword in vendor for keyword in ["azure", "aws", "google", "cloud"]):
                categories["cloud_services"].append(invoice)
            elif any(keyword in vendor for keyword in ["synoptek", "consulting", "professional"]):
                categories["professional_services"].append(invoice)
            else:
                categories["other"].append(invoice)
        
        # Log categorization results
        for category, invoices in categories.items():
            if invoices:
                total_cost = sum(invoice.get("total_amount", 0) for invoice in invoices)
                logger.info(f"{category}: {len(invoices)} invoices, ${total_cost:,.2f} total")
        
        return categories
    
    def analyze_cost_trends(self, licensing_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cost trends over time."""
        if not licensing_data:
            return {}
        
        # Convert to DataFrame for analysis
        df_data = []
        for invoice in licensing_data:
            try:
                date_str = invoice.get("invoice_date", "")
                if date_str:
                    # Try to parse various date formats
                    date = self._parse_date(date_str)
                    if date:
                        df_data.append({
                            "date": date,
                            "vendor": invoice.get("vendor", ""),
                            "total_amount": invoice.get("total_amount", 0),
                            "bill_to": invoice.get("bill_to", "")
                        })
            except Exception as e:
                logger.warning(f"Error processing date for invoice: {e}")
        
        if not df_data:
            return {}
        
        df = pd.DataFrame(df_data)
        df = df.sort_values("date")
        
        # Monthly trends
        monthly_trends = df.groupby(df["date"].dt.to_period("M")).agg({
            "total_amount": ["sum", "mean", "count"]
        }).round(2)
        
        # Vendor trends
        vendor_trends = df.groupby("vendor").agg({
            "total_amount": ["sum", "mean", "count"]
        }).round(2)
        
        # Recent vs historical comparison
        recent_date = df["date"].max()
        three_months_ago = recent_date - timedelta(days=90)
        
        recent_data = df[df["date"] >= three_months_ago]
        historical_data = df[df["date"] < three_months_ago]
        
        recent_total = recent_data["total_amount"].sum()
        historical_avg = historical_data["total_amount"].mean() if len(historical_data) > 0 else 0
        
        trend_analysis = {
            "monthly_trends": monthly_trends.to_dict(),
            "vendor_trends": vendor_trends.to_dict(),
            "recent_vs_historical": {
                "recent_total": recent_total,
                "historical_average": historical_avg,
                "trend_percentage": ((recent_total - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
            },
            "total_invoices": len(df),
            "date_range": {
                "start": df["date"].min().isoformat(),
                "end": df["date"].max().isoformat()
            }
        }
        
        return trend_analysis
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats."""
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d/%m/%Y",
            "%Y/%m/%d"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def generate_summary_report(self, licensing_data: List[Dict[str, Any]], categories: Dict[str, List[Dict[str, Any]]], trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary report of the licensing data."""
        total_cost = sum(invoice.get("total_amount", 0) for invoice in licensing_data)
        total_invoices = len(licensing_data)
        
        # Top vendors by cost
        vendor_costs = {}
        for invoice in licensing_data:
            vendor = invoice.get("vendor", "Unknown")
            if vendor not in vendor_costs:
                vendor_costs[vendor] = 0
            vendor_costs[vendor] += invoice.get("total_amount", 0)
        
        top_vendors = sorted(vendor_costs.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Category breakdown
        category_breakdown = {}
        for category, invoices in categories.items():
            if invoices:
                category_cost = sum(invoice.get("total_amount", 0) for invoice in invoices)
                category_breakdown[category] = {
                    "invoice_count": len(invoices),
                    "total_cost": category_cost,
                    "percentage": (category_cost / total_cost * 100) if total_cost > 0 else 0
                }
        
        summary_report = {
            "summary": {
                "total_invoices": total_invoices,
                "total_cost": total_cost,
                "date_generated": datetime.now().isoformat()
            },
            "top_vendors": top_vendors,
            "category_breakdown": category_breakdown,
            "trend_analysis": trends,
            "data_quality": {
                "invoices_with_dates": len([i for i in licensing_data if i.get("invoice_date")]),
                "invoices_with_vendors": len([i for i in licensing_data if i.get("vendor")]),
                "invoices_with_line_items": len([i for i in licensing_data if i.get("line_items")])
            }
        }
        
        return summary_report
    
    def save_processed_data(self, licensing_data: List[Dict[str, Any]], output_file: str = "processed_licensing_data.json"):
        """Save processed licensing data to file."""
        output_path = os.path.join("reports", output_file)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(licensing_data, f, indent=2)
            logger.info(f"Processed data saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            return None
    
    def process_all_data(self) -> Dict[str, Any]:
        """Process all invoice data and return comprehensive results."""
        logger.info("Starting comprehensive invoice data processing")
        
        # Load cache data
        cache_data = self.load_invoice_cache()
        if not cache_data:
            return {"error": "No cache data available"}
        
        # Extract licensing data
        licensing_data = self.extract_licensing_data(cache_data)
        if not licensing_data:
            return {"error": "No licensing-relevant data found"}
        
        # Categorize invoices
        categories = self.categorize_invoices(licensing_data)
        
        # Analyze trends
        trends = self.analyze_cost_trends(licensing_data)
        
        # Generate summary report
        summary_report = self.generate_summary_report(licensing_data, categories, trends)
        
        # Save processed data
        self.save_processed_data(licensing_data)
        
        results = {
            "licensing_data": licensing_data,
            "categories": categories,
            "trends": trends,
            "summary_report": summary_report,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info("Invoice data processing completed")
        return results

def main():
    """Main function for testing the invoice data processor."""
    try:
        # Initialize processor
        processor = InvoiceDataProcessor()
        
        # Process all data
        results = processor.process_all_data()
        
        if "error" in results:
            print(f"Error: {results['error']}")
        else:
            print("Invoice data processing completed successfully!")
            print(f"Processed {len(results['licensing_data'])} licensing-relevant invoices")
            print(f"Total cost: ${results['summary_report']['summary']['total_cost']:,.2f}")
            
            # Print top vendors
            print("\nTop vendors by cost:")
            for vendor, cost in results['summary_report']['top_vendors'][:5]:
                print(f"  {vendor}: ${cost:,.2f}")
            
            # Print category breakdown
            print("\nCategory breakdown:")
            for category, data in results['summary_report']['category_breakdown'].items():
                if data['invoice_count'] > 0:
                    print(f"  {category}: {data['invoice_count']} invoices, ${data['total_cost']:,.2f} ({data['percentage']:.1f}%)")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 