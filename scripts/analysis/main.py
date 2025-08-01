"""
Main entry point for Licensing Analysis
Orchestrates the entire process of analyzing licensing costs using Claude Opus 4
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List
import argparse

from config import create_directories, get_config
from invoice_data_processor import InvoiceDataProcessor
from licensing_analyzer import LicensingAnalyzer
from cache_manager import migrate_invoice_cache

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LicensingAnalysisOrchestrator:
    """
    Main orchestrator for the licensing analysis process.
    Coordinates data processing, analysis, and reporting.
    """
    
    def __init__(self, api_key: str = None, invoice_cache_path: str = None):
        """Initialize the orchestrator."""
        self.config = get_config()
        create_directories()
        
        # Initialize components
        self.data_processor = InvoiceDataProcessor(invoice_cache_path)
        self.analyzer = LicensingAnalyzer(api_key)
        self.invoice_cache_path = invoice_cache_path
        
        logger.info("Licensing Analysis Orchestrator initialized")
    
    def run_complete_analysis(self, migrate_cache: bool = True) -> Dict[str, Any]:
        """
        Run the complete licensing analysis process.
        
        Args:
            migrate_cache: Whether to migrate data from the existing invoice cache
            
        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Starting complete licensing analysis")
        
        # Step 1: Migrate cache if requested
        if migrate_cache:
            logger.info("Migrating invoice cache data")
            try:
                migrate_invoice_cache(self.invoice_cache_path)
                logger.info("Cache migration completed")
            except Exception as e:
                logger.warning(f"Cache migration failed: {e}")
        
        # Step 2: Process invoice data
        logger.info("Processing invoice data")
        processing_results = self.data_processor.process_all_data()
        
        if "error" in processing_results:
            logger.error(f"Data processing failed: {processing_results['error']}")
            return {"error": processing_results["error"]}
        
        licensing_data = processing_results["licensing_data"]
        logger.info(f"Processed {len(licensing_data)} licensing-relevant invoices")
        
        # Step 3: Analyze licensing data with Claude Opus 4 using batch processing
        logger.info("Starting Claude Opus 4 batch analysis")
        
        # Prepare all data for batch analysis
        analysis_data_list = []
        for invoice_data in licensing_data:
            analysis_data = {
                "vendor": invoice_data.get("vendor", ""),
                "bill_to": invoice_data.get("bill_to", ""),
                "invoice_date": invoice_data.get("invoice_date", ""),
                "line_items": invoice_data.get("line_items", []),
                "total_amount": invoice_data.get("total_amount", 0)
            }
            analysis_data_list.append(analysis_data)
        
        # Use batch analysis to minimize API calls
        batch_size = self.config["api"]["batch_size"]
        logger.info(f"Using batch analysis with batch size: {batch_size}")
        logger.info(f"Total API calls needed: {(len(analysis_data_list) + batch_size - 1) // batch_size}")
        
        # Perform batch analysis
        analysis_results = self.analyzer.analyze_multiple_invoices_batch(analysis_data_list, batch_size)
        
        # Step 4: Create comprehensive analysis
        logger.info("Creating comprehensive analysis")
        comprehensive_analysis = self._create_comprehensive_analysis(analysis_results, processing_results)
        
        # Step 5: Generate reports
        logger.info("Generating reports")
        reports = self._generate_reports(comprehensive_analysis, processing_results)
        
        # Step 6: Create final results
        final_results = {
            "processing_results": processing_results,
            "analysis_results": analysis_results,
            "comprehensive_analysis": comprehensive_analysis,
            "reports": reports,
            "cache_stats": self.analyzer.get_cache_stats(),
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info("Complete licensing analysis finished")
        return final_results
    
    def _create_comprehensive_analysis(self, analysis_results: List[Dict[str, Any]], processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive analysis from all results."""
        if not analysis_results:
            return {"error": "No analysis results available"}
        
        # Extract analysis data
        analyses = [result["analysis"] for result in analysis_results]
        
        # Create comprehensive analysis using the analyzer
        comprehensive_analysis = self.analyzer._create_comprehensive_analysis(
            analyses,
            processing_results["summary_report"]["summary"]["total_cost"],
            dict(processing_results["summary_report"]["top_vendors"])
        )
        
        # Add additional insights
        comprehensive_analysis["processing_insights"] = {
            "total_invoices_processed": len(processing_results["licensing_data"]),
            "category_breakdown": processing_results["summary_report"]["category_breakdown"],
            "trend_analysis": processing_results["trends"],
            "data_quality": processing_results["summary_report"]["data_quality"]
        }
        
        return comprehensive_analysis
    
    def _generate_reports(self, comprehensive_analysis: Dict[str, Any], processing_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate various reports."""
        reports = {}
        
        try:
            # Generate JSON report
            json_report = self.analyzer.generate_report(comprehensive_analysis, "json")
            reports["json_report"] = json_report
            
            # Generate Excel report
            excel_report = self.analyzer.generate_report(comprehensive_analysis, "excel")
            reports["excel_report"] = excel_report
            
            # Generate processing summary
            processing_summary = {
                "summary": processing_results["summary_report"],
                "categories": processing_results["categories"],
                "trends": processing_results["trends"]
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processing_report_path = f"reports/processing_summary_{timestamp}.json"
            with open(processing_report_path, 'w') as f:
                json.dump(processing_summary, f, indent=2)
            reports["processing_summary"] = processing_report_path
            
            logger.info(f"Generated reports: {list(reports.keys())}")
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            reports["error"] = str(e)
        
        return reports
    
    def analyze_specific_vendor(self, vendor_name: str) -> Dict[str, Any]:
        """Analyze licensing data for a specific vendor."""
        logger.info(f"Analyzing vendor: {vendor_name}")
        
        # Process data
        processing_results = self.data_processor.process_all_data()
        if "error" in processing_results:
            return {"error": processing_results["error"]}
        
        # Filter for specific vendor
        vendor_data = []
        for invoice in processing_results["licensing_data"]:
            if vendor_name.lower() in invoice.get("vendor", "").lower():
                vendor_data.append(invoice)
        
        if not vendor_data:
            return {"error": f"No data found for vendor: {vendor_name}"}
        
        logger.info(f"Found {len(vendor_data)} invoices for {vendor_name}")
        
        # Analyze vendor data
        analysis_results = []
        for invoice_data in vendor_data:
            analysis_data = {
                "vendor": invoice_data.get("vendor", ""),
                "bill_to": invoice_data.get("bill_to", ""),
                "invoice_date": invoice_data.get("invoice_date", ""),
                "line_items": invoice_data.get("line_items", []),
                "total_amount": invoice_data.get("total_amount", 0)
            }
            
            result = self.analyzer.analyze_licensing_data(analysis_data)
            if result:
                analysis_results.append({
                    "invoice_data": invoice_data,
                    "analysis": result
                })
        
        # Create vendor-specific analysis
        vendor_analysis = self._create_vendor_analysis(vendor_name, analysis_results, vendor_data)
        
        return {
            "vendor_name": vendor_name,
            "vendor_data": vendor_data,
            "analysis_results": analysis_results,
            "vendor_analysis": vendor_analysis,
            "completed_at": datetime.now().isoformat()
        }
    
    def _create_vendor_analysis(self, vendor_name: str, analysis_results: List[Dict[str, Any]], vendor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create vendor-specific analysis."""
        if not analysis_results:
            return {"error": "No analysis results available"}
        
        total_cost = sum(invoice.get("total_amount", 0) for invoice in vendor_data)
        analyses = [result["analysis"] for result in analysis_results]
        
        # Calculate vendor-specific metrics
        avg_variance = sum(analysis.get("summary", {}).get("cost_variance_percentage", 0) for analysis in analyses) / len(analyses)
        
        # Determine vendor assessment
        if avg_variance > self.config["thresholds"]["cost_variance_critical"]:
            vendor_assessment = "Critical - Immediate attention required"
        elif avg_variance > self.config["thresholds"]["cost_variance_warning"]:
            vendor_assessment = "Above Standard - Optimization opportunities available"
        else:
            vendor_assessment = "At Standard - Costs are reasonable"
        
        vendor_analysis = {
            "vendor_name": vendor_name,
            "total_invoices": len(vendor_data),
            "total_cost": total_cost,
            "average_cost_variance": avg_variance,
            "vendor_assessment": vendor_assessment,
            "key_findings": [],
            "recommendations": [],
            "risk_items": []
        }
        
        # Aggregate findings from all analyses
        for analysis in analyses:
            summary = analysis.get("summary", {})
            vendor_analysis["key_findings"].extend(summary.get("key_findings", []))
            vendor_analysis["recommendations"].extend(analysis.get("recommendations", {}).get("immediate_actions", []))
            vendor_analysis["risk_items"].extend(analysis.get("risk_assessment", {}).get("high_risk_items", []))
        
        # Remove duplicates
        vendor_analysis["key_findings"] = list(set(vendor_analysis["key_findings"]))
        vendor_analysis["recommendations"] = list(set(vendor_analysis["recommendations"]))
        vendor_analysis["risk_items"] = list(set(vendor_analysis["risk_items"]))
        
        return vendor_analysis

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description="Licensing Analysis using Claude Opus 4")
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    parser.add_argument("--cache-path", help="Path to the invoice cache file (e.g., ../InvoicesAI/Invoices/Invoices/cache.json)")
    parser.add_argument("--vendor", help="Analyze specific vendor only")
    parser.add_argument("--no-migrate", action="store_true", help="Skip cache migration")
    parser.add_argument("--output", choices=["json", "excel", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator
        orchestrator = LicensingAnalysisOrchestrator(args.api_key, args.cache_path)
        
        if args.vendor:
            # Analyze specific vendor
            results = orchestrator.analyze_specific_vendor(args.vendor)
            if "error" in results:
                print(f"Error: {results['error']}")
                return
            
            print(f"\n=== Vendor Analysis: {args.vendor} ===")
            print(f"Total invoices: {results['vendor_analysis']['total_invoices']}")
            print(f"Total cost: ${results['vendor_analysis']['total_cost']:,.2f}")
            print(f"Assessment: {results['vendor_analysis']['vendor_assessment']}")
            
            if results['vendor_analysis']['key_findings']:
                print("\nKey Findings:")
                for finding in results['vendor_analysis']['key_findings'][:5]:
                    print(f"  - {finding}")
            
            if results['vendor_analysis']['recommendations']:
                print("\nRecommendations:")
                for rec in results['vendor_analysis']['recommendations'][:5]:
                    print(f"  - {rec}")
        
        else:
            # Run complete analysis
            results = orchestrator.run_complete_analysis(migrate_cache=not args.no_migrate)
            
            if "error" in results:
                print(f"Error: {results['error']}")
                return
            
            print("\n=== Licensing Analysis Complete ===")
            print(f"Processed {len(results['processing_results']['licensing_data'])} invoices")
            print(f"Analyzed {len(results['analysis_results'])} invoices with Claude Opus 4")
            print(f"Total cost analyzed: ${results['comprehensive_analysis']['comprehensive_summary']['total_cost']:,.2f}")
            print(f"Overall assessment: {results['comprehensive_analysis']['comprehensive_summary']['overall_assessment']}")
            
            # Print top findings
            if results['comprehensive_analysis']['aggregated_findings']['key_findings']:
                print("\nTop Findings:")
                for finding in results['comprehensive_analysis']['aggregated_findings']['key_findings'][:5]:
                    print(f"  - {finding}")
            
            # Print top recommendations
            if results['comprehensive_analysis']['recommendations']['immediate_actions']:
                print("\nImmediate Actions:")
                for action in results['comprehensive_analysis']['recommendations']['immediate_actions'][:5]:
                    print(f"  - {action}")
            
            # Print reports generated
            if results['reports']:
                print(f"\nReports generated:")
                for report_type, report_path in results['reports'].items():
                    print(f"  - {report_type}: {report_path}")
        
        # Print cache stats
        cache_stats = orchestrator.analyzer.get_cache_stats()
        print(f"\nCache Statistics:")
        print(f"  Hit rate: {cache_stats['hit_rate']:.2%}")
        print(f"  Total entries: {cache_stats['total_entries']}")
        print(f"  Cache size: {cache_stats['total_size_mb']:.1f} MB")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 