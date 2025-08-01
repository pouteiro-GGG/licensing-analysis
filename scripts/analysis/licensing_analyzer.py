"""
Licensing Analyzer using Claude Opus 4
Analyzes licensing costs and determines if they're above industry standards
"""

import os
import json
import base64
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from anthropic import Anthropic, RateLimitError, APIError

from config import (
    CLAUDE_OPUS_4_CONFIG, 
    INDUSTRY_STANDARDS, 
    ANALYSIS_THRESHOLDS,
    get_api_key,
    create_directories
)
from cache_manager import get_cache_manager
from cost_control_manager import get_cost_control_manager
from report_formatter import ReportFormatter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('logs/licensing_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LicensingAnalyzer:
    """
    Main licensing analyzer using Claude Opus 4 to analyze licensing costs
    and determine if they're above industry standards.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the licensing analyzer."""
        self.api_key = api_key or get_api_key()
        self.client = Anthropic(api_key=self.api_key)
        self.cache_manager = get_cache_manager()
        self.cost_control_manager = get_cost_control_manager()
        self.config = CLAUDE_OPUS_4_CONFIG
        
        # Create necessary directories
        create_directories()
        
        logger.info("Licensing Analyzer initialized")
    
    def analyze_licensing_data(self, data: Dict[str, Any], max_retries: int = 5) -> Optional[Dict[str, Any]]:
        """
        Analyze licensing data using Claude Opus 4 to determine if costs are above standards.
        
        Args:
            data: Dictionary containing licensing data (vendor, line_items, etc.)
            max_retries: Maximum number of retry attempts for API calls
            
        Returns:
            Dictionary containing analysis results or None if analysis failed
        """
        # Check cost control cache first (persistent storage)
        cached_result = self.cost_control_manager.get_cached_analysis(data)
        if cached_result:
            logger.info("Using cost control cached analysis result")
            return cached_result
        
        # Check regular cache as fallback
        cache_key = f"analysis_{hash(json.dumps(data, sort_keys=True))}"
        cached_result = self.cache_manager.get(cache_key, data)
        if cached_result:
            logger.info("Using regular cached analysis result")
            return cached_result
        
        # Prepare data for analysis
        analysis_data = self._prepare_analysis_data(data)
        
        # Create prompt for Claude Opus 4
        prompt = self._create_analysis_prompt(analysis_data)
        
        # Call Claude Opus 4 API
        result = self._call_claude_opus_4(prompt, max_retries)
        
        if result:
            # Store in cost control manager (persistent)
            # Estimate tokens and cost (you can get actual values from API response)
            estimated_tokens = len(prompt.split()) * 1.3  # Rough estimate
            estimated_cost = (estimated_tokens / 1000) * 0.15  # Rough cost estimate
            self.cost_control_manager.store_analysis_result(data, result, int(estimated_tokens), estimated_cost)
            
            # Also cache in regular cache
            self.cache_manager.set(cache_key, result, data)
            return result
        
        return None
    
    def _prepare_analysis_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for analysis by extracting relevant information."""
        prepared_data = {
            "vendor": data.get("vendor", ""),
            "bill_to": data.get("bill_to", ""),
            "invoice_date": data.get("invoice_date", ""),
            "line_items": [],
            "total_amount": 0,
            "categories": {}
        }
        
        # Process line items
        for item in data.get("line_items", []):
            line_item = {
                "description": item.get("description", ""),
                "quantity": item.get("quantity", 0),
                "unit_price": item.get("unit_price", 0),
                "total_amount": item.get("total_amount", 0),
                "category": self._categorize_line_item(item.get("description", ""))
            }
            prepared_data["line_items"].append(line_item)
            prepared_data["total_amount"] += line_item["total_amount"]
            
            # Group by category
            category = line_item["category"]
            if category not in prepared_data["categories"]:
                prepared_data["categories"][category] = {
                    "items": [],
                    "total_amount": 0
                }
            prepared_data["categories"][category]["items"].append(line_item)
            prepared_data["categories"][category]["total_amount"] += line_item["total_amount"]
        
        return prepared_data
    
    def _categorize_line_item(self, description: str) -> str:
        """Categorize a line item based on its description."""
        description_lower = description.lower()
        
        # Software licenses
        if any(keyword in description_lower for keyword in ["microsoft", "office", "365", "e3", "e5"]):
            return "Microsoft 365"
        elif any(keyword in description_lower for keyword in ["adobe", "acrobat", "creative"]):
            return "Adobe"
        elif any(keyword in description_lower for keyword in ["vmware", "vsphere", "vcenter"]):
            return "VMware"
        elif any(keyword in description_lower for keyword in ["oracle", "database", "java"]):
            return "Oracle"
        elif any(keyword in description_lower for keyword in ["sap", "erp"]):
            return "SAP"
        elif any(keyword in description_lower for keyword in ["salesforce", "crm"]):
            return "Salesforce"
        elif any(keyword in description_lower for keyword in ["servicenow", "itom"]):
            return "ServiceNow"
        elif any(keyword in description_lower for keyword in ["atlassian", "jira", "confluence"]):
            return "Atlassian"
        
        # Cloud services
        elif any(keyword in description_lower for keyword in ["azure", "microsoft cloud"]):
            return "Azure"
        elif any(keyword in description_lower for keyword in ["aws", "amazon web services"]):
            return "AWS"
        elif any(keyword in description_lower for keyword in ["google cloud", "gcp"]):
            return "Google Cloud"
        elif any(keyword in description_lower for keyword in ["slack", "messaging"]):
            return "Slack"
        elif any(keyword in description_lower for keyword in ["zoom", "video conferencing"]):
            return "Zoom"
        
        # Infrastructure
        elif any(keyword in description_lower for keyword in ["hardware", "equipment", "device"]):
            return "Hardware"
        elif any(keyword in description_lower for keyword in ["network", "cisco", "meraki"]):
            return "Networking"
        elif any(keyword in description_lower for keyword in ["storage", "backup"]):
            return "Storage"
        elif any(keyword in description_lower for keyword in ["security", "firewall", "antivirus"]):
            return "Security"
        
        # Professional services
        elif any(keyword in description_lower for keyword in ["consulting", "consultant", "professional services"]):
            return "Professional Services"
        elif any(keyword in description_lower for keyword in ["implementation", "setup", "configuration"]):
            return "Implementation"
        elif any(keyword in description_lower for keyword in ["training", "education"]):
            return "Training"
        elif any(keyword in description_lower for keyword in ["support", "maintenance"]):
            return "Support"
        
        else:
            return "Other"
    
    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for Claude Opus 4 analysis."""
        prompt = f"""
{self.config['system_prompt']}

Please analyze the following licensing and IT infrastructure data to determine if costs are above industry standards:

VENDOR: {data['vendor']}
BILL TO: {data['bill_to']}
INVOICE DATE: {data['invoice_date']}
TOTAL AMOUNT: ${data['total_amount']:,.2f}

LINE ITEMS BY CATEGORY:
"""
        
        for category, category_data in data['categories'].items():
            prompt += f"\n{category.upper()} (${category_data['total_amount']:,.2f}):\n"
            for item in category_data['items']:
                prompt += f"  - {item['description']}: {item['quantity']} x ${item['unit_price']:.2f} = ${item['total_amount']:.2f}\n"
        
        prompt += f"""

INDUSTRY STANDARDS FOR REFERENCE:
{json.dumps(INDUSTRY_STANDARDS, indent=2)}

ANALYSIS THRESHOLDS:
- Warning: 15% above standard
- Critical: 30% above standard
- Usage efficiency warning: Below 70%
- License utilization warning: Below 80%

Please provide a detailed analysis in the following JSON format:

{{
    "summary": {{
        "total_cost": number,
        "cost_variance_percentage": number,
        "overall_assessment": "string (Below Standard/At Standard/Above Standard/Critical)",
        "key_findings": ["array of key findings"],
        "cost_optimization_opportunities": ["array of opportunities"]
    }},
    "category_analysis": {{
        "category_name": {{
            "cost": number,
            "industry_standard": number,
            "variance_percentage": number,
            "assessment": "string",
            "recommendations": ["array of recommendations"]
        }}
    }},
    "vendor_analysis": {{
        "vendor_name": "string",
        "pricing_assessment": "string",
        "negotiation_opportunities": ["array of opportunities"],
        "alternative_vendors": ["array of alternatives"]
    }},
    "recommendations": {{
        "immediate_actions": ["array of immediate actions"],
        "short_term_optimizations": ["array of short-term optimizations"],
        "long_term_strategies": ["array of long-term strategies"],
        "estimated_savings": {{
            "immediate": number,
            "short_term": number,
            "long_term": number
        }}
    }},
    "risk_assessment": {{
        "high_risk_items": ["array of high-risk items"],
        "medium_risk_items": ["array of medium-risk items"],
        "low_risk_items": ["array of low-risk items"]
    }}
}}

Provide only valid JSON. No explanatory text outside the JSON structure.
"""
        
        return prompt
    
    def _call_claude_opus_4(self, prompt: str, max_retries: int) -> Optional[Dict[str, Any]]:
        """Call Claude Opus 4 API with retry logic and improved rate limiting."""
        # Static system prompt that can be cached
        system_prompt = {
            "type": "text",
            "text": self.config.get("system_prompt", """You are an expert licensing analyst specializing in software licensing, 
            cloud services, and IT infrastructure costs. Your role is to analyze licensing data and 
            determine if costs are above industry standards. Provide detailed, accurate analysis with 
            specific recommendations for cost optimization."""),
            "cache_control": {"type": "ephemeral"}
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Claude Opus 4 API (attempt {attempt + 1}/{max_retries})")
                
                message = self.client.messages.create(
                    model=self.config["model"],
                    max_tokens=self.config["max_tokens"],
                    temperature=self.config["temperature"],
                    system=[system_prompt],
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                
                response_text = message.content[0].text
                result = self._extract_json_from_response(response_text)
                
                if result:
                    logger.info("Successfully received analysis from Claude Opus 4")
                    return result
                else:
                    logger.warning(f"Failed to extract JSON from response (attempt {attempt + 1})")
                    if attempt == max_retries - 1:
                        logger.error("All attempts to get valid JSON failed")
                        return None
                    time.sleep(5 * (attempt + 1))  # Progressive backoff: 5s, 10s, 15s
                    
            except RateLimitError:
                wait_time = min(60 * (2 ** attempt), 300)  # Max 5 minutes
                logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}")
                time.sleep(wait_time)
                
            except APIError as e:
                logger.error(f"API error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(10 * (attempt + 1))  # Progressive backoff for API errors
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5 * (attempt + 1))  # Progressive backoff
        
        return None
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from Claude Opus 4 response."""
        try:
            # Try to find JSON between ```json and ``` markers
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                return json.loads(json_str)
            
            # If no markdown markers, try to find JSON directly
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            logger.warning("No JSON found in response")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return None
    
    def analyze_multiple_invoices(self, invoices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze multiple invoices and provide comprehensive analysis."""
        logger.info(f"Analyzing {len(invoices_data)} invoices")
        
        results = []
        total_cost = 0
        vendor_costs = {}
        
        for i, invoice_data in enumerate(invoices_data):
            logger.info(f"Analyzing invoice {i + 1}/{len(invoices_data)}")
            
            analysis_result = self.analyze_licensing_data(invoice_data)
            if analysis_result:
                results.append(analysis_result)
                total_cost += invoice_data.get("total_amount", 0)
                
                vendor = invoice_data.get("vendor", "Unknown")
                if vendor not in vendor_costs:
                    vendor_costs[vendor] = 0
                vendor_costs[vendor] += invoice_data.get("total_amount", 0)
        
        # Create comprehensive analysis
        comprehensive_analysis = self._create_comprehensive_analysis(results, total_cost, vendor_costs)
        
        return comprehensive_analysis
    
    def analyze_multiple_invoices_batch(self, invoices_data: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Analyze multiple invoices using batch processing with caching."""
        logger.info(f"Starting batch analysis of {len(invoices_data)} invoices with batch size {batch_size}")
        
        all_results = []
        processed_count = 0
        
        # Process invoices in batches
        for i in range(0, len(invoices_data), batch_size):
            batch = invoices_data[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(invoices_data) + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} invoices)")
            
            # Check cache for each invoice in the batch
            cached_results = []
            uncached_invoices = []
            
            for j, invoice in enumerate(batch):
                # Check if this invoice is already cached
                cached_result = self.cost_control_manager.get_cached_analysis(invoice)
                if cached_result:
                    cached_results.append({
                        "invoice_data": invoice,
                        "analysis": cached_result,
                        "cache_hit": True
                    })
                    processed_count += 1
                    logger.info(f"Cache hit for invoice {i + j + 1}/{len(invoices_data)}")
                else:
                    uncached_invoices.append(invoice)
            
            # Add cached results to all_results
            all_results.extend(cached_results)
            
            # Process uncached invoices in batch
            if uncached_invoices:
                logger.info(f"Processing {len(uncached_invoices)} uncached invoices in batch {batch_num}")
                batch_results = self._analyze_batch(uncached_invoices)
                all_results.extend(batch_results)
                processed_count += len(uncached_invoices)
            else:
                logger.info(f"All invoices in batch {batch_num} were cached")
            
            # Progress update
            logger.info(f"Progress: {processed_count}/{len(invoices_data)} invoices analyzed ({processed_count/len(invoices_data)*100:.1f}%)")
            
            # Note: Removed unnecessary rate limiting delay - only retry on actual rate limit errors
        
        logger.info(f"Batch analysis completed. Successfully analyzed {len(all_results)} invoices")
        return all_results
    
    def _analyze_batch(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a batch of invoices in a single API call."""
        try:
            # Create a comprehensive prompt for the entire batch
            batch_prompt = self._create_batch_analysis_prompt(batch_data)
            
            # Call Claude Opus 4 with the batch
            logger.info(f"Calling Claude Opus 4 API for batch of {len(batch_data)} invoices")
            result = self._call_claude_opus_4(batch_prompt, max_retries=3)
            
            if result and "batch_analysis" in result:
                # Parse the batch results
                batch_results = self._parse_batch_results(result["batch_analysis"], batch_data)
                
                # Store each result in the cache
                for i, batch_result in enumerate(batch_results):
                    if i < len(batch_data):
                        invoice_data = batch_data[i]
                        analysis_data = batch_result.get("analysis", {})
                        
                        # Estimate tokens and cost for caching
                        estimated_tokens = len(batch_prompt.split()) * 1.3  # Rough estimate
                        estimated_cost = (estimated_tokens / 1000) * 0.15  # Rough cost estimate
                        
                        # Store in cost control manager
                        self.cost_control_manager.store_analysis_result(
                            invoice_data, 
                            analysis_data, 
                            int(estimated_tokens / len(batch_data)),  # Divide by batch size
                            estimated_cost / len(batch_data)  # Divide by batch size
                        )
                
                return batch_results
            else:
                logger.warning("Failed to get valid batch analysis result")
                # Fallback to individual analysis
                return self._fallback_individual_analysis(batch_data)
                
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            # Fallback to individual analysis
            return self._fallback_individual_analysis(batch_data)
    
    def _create_batch_analysis_prompt(self, batch_data: List[Dict[str, Any]]) -> str:
        """Create a comprehensive prompt for analyzing multiple invoices at once."""
        prompt = f"""You are an expert licensing analyst. Analyze the following {len(batch_data)} invoices for licensing cost optimization opportunities.

For each invoice, provide:
1. Cost variance percentage compared to industry standards
2. Overall assessment (At Standard, Above Standard, Critical)
3. Key findings about pricing and licensing
4. Cost optimization opportunities
5. Risk assessment

Return your analysis in this exact JSON format:
{{
    "batch_analysis": [
        {{
            "invoice_index": 0,
            "vendor": "vendor_name",
            "total_amount": 1000.00,
            "summary": {{
                "cost_variance_percentage": 15.5,
                "overall_assessment": "Above Standard",
                "key_findings": ["finding1", "finding2"],
                "cost_optimization_opportunities": ["opportunity1", "opportunity2"]
            }},
            "risk_assessment": {{
                "risk_level": "Medium",
                "high_risk_items": ["item1"],
                "medium_risk_items": ["item2"],
                "low_risk_items": ["item3"]
            }},
            "recommendations": {{
                "immediate_actions": ["action1"],
                "short_term_optimizations": ["optimization1"],
                "long_term_strategies": ["strategy1"]
            }}
        }}
    ]
}}

Invoice Data:
"""
        
        for i, invoice in enumerate(batch_data):
            prompt += f"""
Invoice {i + 1}:
- Vendor: {invoice.get('vendor', 'Unknown')}
- Bill To: {invoice.get('bill_to', 'Unknown')}
- Date: {invoice.get('invoice_date', 'Unknown')}
- Total Amount: ${invoice.get('total_amount', 0):,.2f}
- Line Items:
"""
            for item in invoice.get('line_items', []):
                prompt += f"  * {item.get('description', 'Unknown')} - Qty: {item.get('quantity', 1)} - Price: ${item.get('unit_price', 0):,.2f} - Total: ${item.get('total_amount', 0):,.2f}\n"
        
        prompt += "\nProvide your analysis in the exact JSON format specified above."
        return prompt
    
    def _parse_batch_results(self, batch_analysis: List[Dict[str, Any]], original_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse the batch analysis results and match them to original invoice data."""
        results = []
        
        for i, analysis in enumerate(batch_analysis):
            if i < len(original_data):
                # Combine original data with analysis
                result = {
                    "invoice_data": original_data[i],
                    "analysis": {
                        "summary": analysis.get("summary", {}),
                        "risk_assessment": analysis.get("risk_assessment", {}),
                        "recommendations": analysis.get("recommendations", {}),
                        "vendor": analysis.get("vendor", original_data[i].get("vendor", "Unknown")),
                        "total_amount": analysis.get("total_amount", original_data[i].get("total_amount", 0))
                    }
                }
                results.append(result)
            else:
                logger.warning(f"Batch analysis has more results than original data")
                break
        
        return results
    
    def _fallback_individual_analysis(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback to individual analysis if batch analysis fails."""
        logger.info("Falling back to individual analysis")
        results = []
        
        for invoice_data in batch_data:
            result = self.analyze_licensing_data(invoice_data)
            if result:
                results.append({
                    "invoice_data": invoice_data,
                    "analysis": result
                })
        
        return results
    
    def _create_comprehensive_analysis(self, results: List[Dict[str, Any]], total_cost: float, vendor_costs: Dict[str, float]) -> Dict[str, Any]:
        """Create comprehensive analysis from multiple invoice results."""
        if not results:
            return {"error": "No valid analysis results"}
        
        # Aggregate findings
        all_findings = []
        all_opportunities = []
        all_recommendations = []
        category_totals = {}
        risk_items = {"high": [], "medium": [], "low": []}
        
        for result in results:
            summary = result.get("summary", {})
            all_findings.extend(summary.get("key_findings", []))
            all_opportunities.extend(summary.get("cost_optimization_opportunities", []))
            
            category_analysis = result.get("category_analysis", {})
            for category, cat_data in category_analysis.items():
                if category not in category_totals:
                    category_totals[category] = {"cost": 0, "recommendations": []}
                category_totals[category]["cost"] += cat_data.get("cost", 0)
                category_totals[category]["recommendations"].extend(cat_data.get("recommendations", []))
            
            risk_assessment = result.get("risk_assessment", {})
            risk_items["high"].extend(risk_assessment.get("high_risk_items", []))
            risk_items["medium"].extend(risk_assessment.get("medium_risk_items", []))
            risk_items["low"].extend(risk_assessment.get("low_risk_items", []))
        
        # Calculate overall metrics
        avg_variance = np.mean([r.get("summary", {}).get("cost_variance_percentage", 0) for r in results])
        
        # Determine overall assessment
        if avg_variance > ANALYSIS_THRESHOLDS["cost_variance_critical"]:
            overall_assessment = "Critical"
        elif avg_variance > ANALYSIS_THRESHOLDS["cost_variance_warning"]:
            overall_assessment = "Above Standard"
        elif avg_variance < -ANALYSIS_THRESHOLDS["cost_variance_warning"]:
            overall_assessment = "Below Standard"
        else:
            overall_assessment = "At Standard"
        
        return {
            "comprehensive_summary": {
                "total_invoices_analyzed": len(results),
                "total_cost": total_cost,
                "average_cost_variance_percentage": avg_variance,
                "overall_assessment": overall_assessment,
                "top_vendors_by_cost": sorted(vendor_costs.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "aggregated_findings": {
                "key_findings": list(set(all_findings)),
                "cost_optimization_opportunities": list(set(all_opportunities)),
                "category_breakdown": category_totals,
                "risk_assessment": risk_items
            },
            "recommendations": {
                "immediate_actions": list(set([item for r in results for item in r.get("recommendations", {}).get("immediate_actions", [])])),
                "short_term_optimizations": list(set([item for r in results for item in r.get("recommendations", {}).get("short_term_optimizations", [])])),
                "long_term_strategies": list(set([item for r in results for item in r.get("recommendations", {}).get("long_term_strategies", [])]))
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_report(self, analysis_results: Dict[str, Any], output_format: str = "json") -> str:
        """Generate a report from analysis results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "json":
            filename = f"reports/licensing_analysis_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(analysis_results, f, indent=2)
        
        elif output_format == "excel":
            filename = f"excel/licensing_analysis_report_{timestamp}.xlsx"
            self._create_excel_report(analysis_results, filename)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        logger.info(f"Report generated: {filename}")
        return filename
    
    def _create_excel_report(self, analysis_results: Dict[str, Any], filename: str):
        """Create Excel report from analysis results."""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = analysis_results.get("comprehensive_summary", {})
            summary_df = pd.DataFrame([summary_data])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
            # Category breakdown
            category_data = analysis_results.get("aggregated_findings", {}).get("category_breakdown", {})
            if category_data:
                category_df = pd.DataFrame([
                    {"Category": cat, "Cost": data["cost"], "Recommendations": "; ".join(data["recommendations"])}
                    for cat, data in category_data.items()
                ])
                category_df.to_excel(writer, sheet_name="Category Analysis", index=False)
            
            # Risk assessment
            risk_data = analysis_results.get("aggregated_findings", {}).get("risk_assessment", {})
            if risk_data:
                risk_df = pd.DataFrame([
                    {"Risk Level": level, "Items": "; ".join(items)}
                    for level, items in risk_data.items()
                ])
                risk_df.to_excel(writer, sheet_name="Risk Assessment", index=False)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache_manager.get_stats()
    
    def get_cost_control_stats(self) -> Dict[str, Any]:
        """Get cost control statistics."""
        return self.cost_control_manager.get_cost_summary()
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get cost breakdown by vendor."""
        return self.cost_control_manager.get_vendor_cost_breakdown()
    
    def get_cost_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get cost trends over time."""
        return self.cost_control_manager.get_cost_trends(days)
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get cost optimization recommendations."""
        return self.cost_control_manager.get_optimization_recommendations()
    
    def export_analysis_data(self, output_file: str = None) -> str:
        """Export all analysis data for backup."""
        return self.cost_control_manager.export_analysis_data(output_file)
    
    def generate_human_readable_report(self, analysis_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate a human-readable report from analysis results."""
        formatter = ReportFormatter()
        return formatter.format_comprehensive_report(analysis_results, output_file)
    
    def generate_vendor_report(self, vendor_data: Dict[str, Any], vendor_name: str, output_file: str = None) -> str:
        """Generate a vendor-specific human-readable report."""
        formatter = ReportFormatter()
        return formatter.format_vendor_specific_report(vendor_data, vendor_name, output_file)
    
    def generate_cost_control_report(self, output_file: str = None) -> str:
        """Generate a human-readable cost control report."""
        formatter = ReportFormatter()
        cost_stats = self.get_cost_control_stats()
        return formatter.format_cost_control_report(cost_stats, output_file)

def main():
    """Main function for testing the licensing analyzer."""
    try:
        # Initialize analyzer
        analyzer = LicensingAnalyzer()
        
        # Example data for testing
        test_data = {
            "vendor": "Microsoft",
            "bill_to": "Great Gray, LLC",
            "invoice_date": "2025-01-15",
            "line_items": [
                {
                    "description": "Microsoft 365 E3 - Monthly",
                    "quantity": 100,
                    "unit_price": 42.0,
                    "total_amount": 4200.0
                },
                {
                    "description": "Azure Consumption",
                    "quantity": 1,
                    "unit_price": 1500.0,
                    "total_amount": 1500.0
                }
            ]
        }
        
        # Analyze the data
        result = analyzer.analyze_licensing_data(test_data)
        
        if result:
            print("Analysis completed successfully!")
            print(json.dumps(result, indent=2))
            
            # Generate report
            report_file = analyzer.generate_report(result, "json")
            print(f"Report saved to: {report_file}")
        else:
            print("Analysis failed")
        
        # Print cache stats
        cache_stats = analyzer.get_cache_stats()
        print(f"Cache stats: {cache_stats}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 