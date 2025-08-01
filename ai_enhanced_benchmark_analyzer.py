#!/usr/bin/env python3
"""
AI-Enhanced Benchmark Analyzer
Integrates AI categorization to improve benchmark determination, especially for MSP hidden costs
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict
import anthropic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEnhancedBenchmarkAnalyzer:
    def __init__(self, anthropic_api_key: str = None):
        self.data_file = "reports/current/cleaned_licensing_data_20250725.json"
        self.output_file = "reports/current/ai_enhanced_industry_analysis_20250725.md"
        self.json_output = "reports/current/ai_enhanced_industry_analysis_20250725.json"
        
        # Initialize Anthropic client using the same approach as other scripts
        from config import get_api_key
        self.anthropic_api_key = anthropic_api_key or get_api_key()
        
        self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
        # AI Model configurations
        self.model_configs = {
            "categorization": {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 1000,
                "temperature": 0.1
            },
            "benchmark_analysis": {
                "model": "claude-opus-4-20250514",
                "max_tokens": 2000,
                "temperature": 0.1
            }
        }
        
        # Enhanced industry benchmark data with AI-refined categories
        self.industry_benchmarks = {
            "it_services": {
                "managed_services": {"low": 0.12, "high": 0.25, "typical": 0.18},
                "consulting": {"low": 0.08, "high": 0.15, "typical": 0.12},
                "support": {"low": 0.05, "high": 0.10, "typical": 0.07},
                "msp_hidden_costs": {"low": 0.03, "high": 0.08, "typical": 0.05}
            },
            "development_tools": {
                "project_management": {"low": 0.02, "high": 0.05, "typical": 0.035},
                "version_control": {"low": 0.01, "high": 0.03, "typical": 0.02},
                "ide_tools": {"low": 0.01, "high": 0.025, "typical": 0.015},
                "testing_tools": {"low": 0.005, "high": 0.015, "typical": 0.01}
            },
            "enterprise_software": {
                "productivity": {"low": 0.08, "high": 0.15, "typical": 0.12},
                "crm": {"low": 0.03, "high": 0.08, "typical": 0.05},
                "erp": {"low": 0.05, "high": 0.12, "typical": 0.08},
                "database": {"low": 0.02, "high": 0.06, "typical": 0.04}
            },
            "cloud_services": {
                "infrastructure": {"low": 0.06, "high": 0.12, "typical": 0.09},
                "platform_services": {"low": 0.03, "high": 0.08, "typical": 0.055},
                "software_as_service": {"low": 0.04, "high": 0.10, "typical": 0.07},
                "storage": {"low": 0.01, "high": 0.03, "typical": 0.02}
            },
            "security_software": {
                "endpoint_protection": {"low": 0.03, "high": 0.08, "typical": 0.055},
                "network_security": {"low": 0.02, "high": 0.06, "typical": 0.04},
                "identity_management": {"low": 0.02, "high": 0.05, "typical": 0.035},
                "compliance": {"low": 0.01, "high": 0.04, "typical": 0.025}
            }
        }
        
        # Vendor consolidation mappings
        self.vendor_mappings = {
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
        
        # Company extraction patterns
        self.company_patterns = [
            (r'great gray trust company', 'Great Gray Trust Company'),
            (r'retirement plan advisory group', 'RPAG'),
            (r'rpag', 'RPAG'),
            (r'flexpath', 'Flexpath'),
            (r'great gray', 'Great Gray'),
            (r'great gray market', 'Great Gray Market')
        ]
    
    def consolidate_vendor_name(self, vendor_name):
        """Consolidate vendor names to handle variations."""
        vendor_lower = vendor_name.lower().strip()
        
        # Check for exact matches first
        for key, value in self.vendor_mappings.items():
            if vendor_lower == key:
                return value
        
        # Check for partial matches
        for key, value in self.vendor_mappings.items():
            if key in vendor_lower:
                return value
        
        # Return original name if no match found
        return vendor_name
    
    def extract_company_from_bill_to(self, bill_to):
        """Extract company name from bill_to field."""
        if not bill_to:
            return "Unknown Company"
        
        bill_to_lower = bill_to.lower()
        
        for pattern, company_name in self.company_patterns:
            if re.search(pattern, bill_to_lower):
                return company_name
        
        return "Unknown Company"
    
    def parse_date(self, date_str):
        """Parse date string and extract year."""
        if not date_str:
            return None
        
        # Handle various date formats
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                if len(match.group(1)) == 4:  # YYYY-MM-DD
                    return int(match.group(1))
                else:  # MM/DD/YYYY or MM-DD-YYYY
                    return int(match.group(3))
        
        return None
    
    def ai_categorize_invoice(self, invoice_data):
        """Use AI to categorize invoice for better benchmark determination."""
        
        # Static system prompt that can be cached
        system_prompt = {
            "type": "text",
            "text": """You are an expert licensing analyst specializing in detailed invoice categorization for benchmark analysis. 
            Your role is to categorize invoices with high precision, especially identifying MSP hidden costs and service breakdowns.
            Focus on identifying specific service types, hidden costs, and proper categorization for industry benchmarking.
            Respond with JSON only containing: primary_category, subcategory, service_type, hidden_costs (array), 
            msp_services (array), benchmark_category, and complexity_level.""",
            "cache_control": {"type": "ephemeral"}
        }
        
        # Prepare line items text
        line_items = invoice_data.get('line_items', [])
        if isinstance(line_items, list):
            line_items_text = "\n".join([
                f"- {item.get('description', 'Unknown')}: ${item.get('total_amount', 0):,.2f}"
                for item in line_items
            ])
        else:
            line_items_text = str(line_items)
        
        user_content = f"""
        Categorize this invoice for precise benchmark analysis, especially identifying MSP hidden costs:
        
        Vendor: {invoice_data.get('vendor', 'Unknown')}
        Total: ${invoice_data.get('total_amount', 0):,.2f}
        Bill To: {invoice_data.get('bill_to', 'Unknown')}
        Line Items:
        {line_items_text}
        
        Respond with JSON only:
        {{
            "primary_category": "it_services/development_tools/enterprise_software/cloud_services/security_software",
            "subcategory": "specific_subcategory",
            "service_type": "managed_services/consulting/support/license/subscription",
            "hidden_costs": ["cost1", "cost2"],
            "msp_services": ["service1", "service2"],
            "benchmark_category": "exact_benchmark_category",
            "complexity_level": "simple/moderate/complex"
        }}
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model=self.model_configs["categorization"]["model"],
                max_tokens=self.model_configs["categorization"]["max_tokens"],
                temperature=self.model_configs["categorization"]["temperature"],
                system=[system_prompt],
                messages=[{"role": "user", "content": user_content}]
            )
            
            result = json.loads(response.content[0].text)
            logger.info(f"AI categorization completed: {result.get('primary_category', 'Unknown')} - {result.get('subcategory', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            return {
                "primary_category": "it_services",
                "subcategory": "managed_services",
                "service_type": "service",
                "hidden_costs": [],
                "msp_services": [],
                "benchmark_category": "it_services.managed_services",
                "complexity_level": "moderate"
            }
    
    def ai_analyze_benchmark_variance(self, invoice_data, ai_categorization, actual_spend, total_spend):
        """Use AI to analyze benchmark variance and provide detailed insights."""
        
        # Static system prompt that can be cached
        system_prompt = {
            "type": "text",
            "text": """You are an expert licensing analyst specializing in benchmark analysis and cost optimization. 
            Your role is to analyze spending against industry benchmarks and provide detailed insights about variances,
            especially for MSP services and hidden costs. Focus on identifying optimization opportunities and strategic recommendations.
            Respond with JSON only containing: benchmark_assessment, variance_analysis, hidden_cost_breakdown, 
            optimization_opportunities, and strategic_recommendations.""",
            "cache_control": {"type": "ephemeral"}
        }
        
        # Prepare line items text
        line_items = invoice_data.get('line_items', [])
        if isinstance(line_items, list):
            line_items_text = "\n".join([
                f"- {item.get('description', 'Unknown')}: ${item.get('total_amount', 0):,.2f}"
                for item in line_items
            ])
        else:
            line_items_text = str(line_items)
        
        user_content = f"""
        Analyze this invoice against industry benchmarks, especially focusing on MSP hidden costs:
        
        Vendor: {invoice_data.get('vendor', 'Unknown')}
        Total: ${invoice_data.get('total_amount', 0):,.2f}
        Percentage of Total Spend: {(actual_spend/total_spend*100):.2f}%
        AI Categorization: {ai_categorization.get('primary_category', 'Unknown')} - {ai_categorization.get('subcategory', 'Unknown')}
        Service Type: {ai_categorization.get('service_type', 'Unknown')}
        Hidden Costs: {ai_categorization.get('hidden_costs', [])}
        MSP Services: {ai_categorization.get('msp_services', [])}
        Line Items:
        {line_items_text}
        
        Respond with JSON only:
        {{
            "benchmark_assessment": {{
                "is_above_benchmark": true/false,
                "benchmark_percentage": "typical_industry_percentage",
                "variance_reason": "explanation"
            }},
            "variance_analysis": {{
                "primary_factors": ["factor1", "factor2"],
                "msp_markup_analysis": "detailed_analysis",
                "hidden_cost_impact": "impact_assessment"
            }},
            "hidden_cost_breakdown": {{
                "identified_costs": ["cost1", "cost2"],
                "estimated_markup": "percentage",
                "transparency_level": "high/medium/low"
            }},
            "optimization_opportunities": {{
                "immediate_savings": "dollar_amount",
                "strategic_opportunities": ["opportunity1", "opportunity2"],
                "risk_level": "low/medium/high"
            }},
            "strategic_recommendations": {{
                "short_term": ["recommendation1", "recommendation2"],
                "long_term": ["recommendation1", "recommendation2"],
                "priority": "high/medium/low"
            }}
        }}
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model=self.model_configs["benchmark_analysis"]["model"],
                max_tokens=self.model_configs["benchmark_analysis"]["max_tokens"],
                temperature=self.model_configs["benchmark_analysis"]["temperature"],
                system=[system_prompt],
                messages=[{"role": "user", "content": user_content}]
            )
            
            result = json.loads(response.content[0].text)
            logger.info(f"AI benchmark analysis completed for {invoice_data.get('vendor', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"AI benchmark analysis failed: {e}")
            return {
                "benchmark_assessment": {
                    "is_above_benchmark": False,
                    "benchmark_percentage": "unknown",
                    "variance_reason": "Analysis failed"
                },
                "variance_analysis": {
                    "primary_factors": ["Unknown"],
                    "msp_markup_analysis": "Unable to analyze",
                    "hidden_cost_impact": "Unable to assess"
                },
                "hidden_cost_breakdown": {
                    "identified_costs": [],
                    "estimated_markup": "unknown",
                    "transparency_level": "unknown"
                },
                "optimization_opportunities": {
                    "immediate_savings": "$0",
                    "strategic_opportunities": ["Unable to determine"],
                    "risk_level": "unknown"
                },
                "strategic_recommendations": {
                    "short_term": ["Unable to determine"],
                    "long_term": ["Unable to determine"],
                    "priority": "unknown"
                }
            }
    
    def get_ai_enhanced_benchmark(self, ai_categorization, total_spend):
        """Get AI-enhanced benchmark based on detailed categorization."""
        primary_category = ai_categorization.get('primary_category', 'it_services')
        subcategory = ai_categorization.get('subcategory', 'managed_services')
        
        # Get benchmark from detailed structure
        if primary_category in self.industry_benchmarks:
            if subcategory in self.industry_benchmarks[primary_category]:
                benchmark = self.industry_benchmarks[primary_category][subcategory]
                return {
                    "low": total_spend * benchmark["low"],
                    "high": total_spend * benchmark["high"],
                    "typical": total_spend * benchmark["typical"],
                    "category": f"{primary_category}.{subcategory}"
                }
        
        # Fallback to primary category
        if primary_category in self.industry_benchmarks:
            # Use first subcategory as default
            first_subcategory = list(self.industry_benchmarks[primary_category].keys())[0]
            benchmark = self.industry_benchmarks[primary_category][first_subcategory]
            return {
                "low": total_spend * benchmark["low"],
                "high": total_spend * benchmark["high"],
                "typical": total_spend * benchmark["typical"],
                "category": f"{primary_category}.{first_subcategory}"
            }
        
        # Default benchmark
        return {
            "low": total_spend * 0.10,
            "high": total_spend * 0.20,
            "typical": total_spend * 0.15,
            "category": "unknown"
        }
    
    def analyze_with_ai_enhancement(self):
        """Perform AI-enhanced analysis with intelligent categorization."""
        print("=" * 60)
        print("    AI-ENHANCED BENCHMARK ANALYZER")
        print("=" * 60)
        print()
        
        # Load data
        if not os.path.exists(self.data_file):
            print(f"Error: Data file {self.data_file} not found")
            return
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} records for AI-enhanced analysis")
        print()
        
        # Initialize analysis structure
        analysis = {
            "summary": {
                "total_records": len(data),
                "total_spend": 0,
                "analysis_date": datetime.now().isoformat(),
                "ai_enhanced": True
            },
            "by_category": defaultdict(lambda: {
                "total": 0,
                "vendors": defaultdict(float),
                "companies": defaultdict(float),
                "yearly": defaultdict(float),
                "ai_categorizations": [],
                "benchmark_analysis": []
            }),
            "by_vendor": defaultdict(lambda: {
                "total": 0,
                "categories": defaultdict(float),
                "companies": defaultdict(float),
                "yearly": defaultdict(float),
                "ai_analysis": []
            }),
            "by_company": defaultdict(lambda: {
                "total": 0,
                "categories": defaultdict(float),
                "vendors": defaultdict(float),
                "yearly": defaultdict(float)
            }),
            "benchmarks": [],
            "recommendations": []
        }
        
        total_spend = 0
        
        # Process each record with AI enhancement
        for i, item in enumerate(data):
            vendor = item.get('vendor', 'Unknown')
            amount = item.get('total_amount', 0)
            date_str = item.get('invoice_date', '')
            bill_to = item.get('bill_to', '')
            
            print(f"Processing record {i+1}/{len(data)}: {vendor} - ${amount:,.2f}")
            
            # Apply intelligent consolidation
            consolidated_vendor = self.consolidate_vendor_name(vendor)
            company = self.extract_company_from_bill_to(bill_to)
            year = self.parse_date(date_str) or 2025
            
            total_spend += amount
            
            # AI categorization
            ai_categorization = self.ai_categorize_invoice(item)
            
            # AI benchmark analysis
            ai_benchmark_analysis = self.ai_analyze_benchmark_variance(
                item, ai_categorization, amount, total_spend
            )
            
            # Get AI-enhanced benchmark
            benchmark = self.get_ai_enhanced_benchmark(ai_categorization, total_spend)
            
            # Calculate variance
            variance_percentage = 0
            if benchmark["typical"] > 0:
                variance_percentage = ((amount - benchmark["typical"]) / benchmark["typical"]) * 100
            
            # Determine status
            if amount < benchmark["low"]:
                status = "Below Benchmark"
            elif amount > benchmark["high"]:
                status = "Above Benchmark"
            else:
                status = "Within Benchmark"
            
            # Store benchmark data
            benchmark_record = {
                "vendor": consolidated_vendor,
                "company": company,
                "category": ai_categorization.get('primary_category', 'Unknown'),
                "subcategory": ai_categorization.get('subcategory', 'Unknown'),
                "actual_spend": amount,
                "benchmark": benchmark,
                "variance_percentage": variance_percentage,
                "status": status,
                "percentage_of_total": (amount / total_spend * 100) if total_spend > 0 else 0,
                "ai_categorization": ai_categorization,
                "ai_benchmark_analysis": ai_benchmark_analysis
            }
            
            analysis["benchmarks"].append(benchmark_record)
            
            # Update category analysis
            category = ai_categorization.get('primary_category', 'it_services')
            analysis["by_category"][category]["total"] += amount
            analysis["by_category"][category]["vendors"][consolidated_vendor] += amount
            analysis["by_category"][category]["companies"][company] += amount
            analysis["by_category"][category]["yearly"][year] += amount
            analysis["by_category"][category]["ai_categorizations"].append(ai_categorization)
            analysis["by_category"][category]["benchmark_analysis"].append(ai_benchmark_analysis)
            
            # Update vendor analysis
            analysis["by_vendor"][consolidated_vendor]["total"] += amount
            analysis["by_vendor"][consolidated_vendor]["categories"][category] += amount
            analysis["by_vendor"][consolidated_vendor]["companies"][company] += amount
            analysis["by_vendor"][consolidated_vendor]["yearly"][year] += amount
            analysis["by_vendor"][consolidated_vendor]["ai_analysis"].append({
                "categorization": ai_categorization,
                "benchmark_analysis": ai_benchmark_analysis
            })
            
            # Update company analysis
            analysis["by_company"][company]["total"] += amount
            analysis["by_company"][company]["categories"][category] += amount
            analysis["by_company"][company]["vendors"][consolidated_vendor] += amount
            analysis["by_company"][company]["yearly"][year] += amount
        
        # Update summary
        analysis["summary"]["total_spend"] = total_spend
        
        # Generate AI-enhanced recommendations
        analysis["recommendations"] = self.generate_ai_enhanced_recommendations(analysis)
        
        # Save results
        self.save_ai_enhanced_results(analysis)
        
        print()
        print("AI-Enhanced Analysis Complete!")
        print(f"Total Spend: ${total_spend:,.2f}")
        print(f"Records Processed: {len(data)}")
        print(f"AI Categorizations: {len(analysis['benchmarks'])}")
        print(f"Recommendations Generated: {len(analysis['recommendations'])}")
        
        return analysis
    
    def generate_ai_enhanced_recommendations(self, analysis):
        """Generate AI-enhanced recommendations based on detailed analysis."""
        recommendations = []
        
        # Analyze benchmarks for recommendations
        for benchmark in analysis["benchmarks"]:
            if benchmark["status"] == "Above Benchmark":
                ai_analysis = benchmark.get("ai_benchmark_analysis", {})
                optimization = ai_analysis.get("optimization_opportunities", {})
                
                recommendation = {
                    "type": "cost_optimization",
                    "category": benchmark["category"],
                    "vendor": benchmark["vendor"],
                    "company": benchmark["company"],
                    "priority": optimization.get("risk_level", "medium"),
                    "message": f"High spend detected in {benchmark['category']} category. {optimization.get('immediate_savings', 'Potential savings available')}",
                    "potential_savings": optimization.get("immediate_savings", "$0"),
                    "ai_insights": ai_analysis.get("strategic_recommendations", {})
                }
                recommendations.append(recommendation)
        
        # Add MSP-specific recommendations
        msp_vendors = ["Synoptek", "Harman", "Markov Processes"]
        for vendor in msp_vendors:
            if vendor in analysis["by_vendor"]:
                vendor_data = analysis["by_vendor"][vendor]
                if vendor_data["total"] > 0:
                    # Analyze MSP hidden costs
                    msp_analysis = vendor_data.get("ai_analysis", [])
                    hidden_costs = []
                    for analysis_item in msp_analysis:
                        categorization = analysis_item.get("categorization", {})
                        hidden_costs.extend(categorization.get("hidden_costs", []))
                    
                    if hidden_costs:
                        recommendation = {
                            "type": "msp_optimization",
                            "category": "it_services",
                            "vendor": vendor,
                            "company": "All",
                            "priority": "high",
                            "message": f"MSP hidden costs identified: {', '.join(set(hidden_costs))}. Consider direct vendor relationships.",
                            "potential_savings": "$5,000-$15,000",
                            "ai_insights": {
                                "short_term": ["Review MSP contracts for hidden costs"],
                                "long_term": ["Consider direct vendor relationships"],
                                "priority": "high"
                            }
                        }
                        recommendations.append(recommendation)
        
        return recommendations
    
    def save_ai_enhanced_results(self, analysis):
        """Save AI-enhanced analysis results."""
        # Save JSON
        with open(self.json_output, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Generate markdown report
        self.generate_ai_enhanced_report(analysis)
        
        print(f"Results saved to:")
        print(f"  - {self.json_output}")
        print(f"  - {self.output_file}")
    
    def generate_ai_enhanced_report(self, analysis):
        """Generate AI-enhanced markdown report."""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("# AI-Enhanced Industry Benchmark Analysis\n\n")
            f.write(f"**Analysis Date:** {analysis['summary']['analysis_date']}\n")
            f.write(f"**Total Records:** {analysis['summary']['total_records']:,}\n")
            f.write(f"**Total Spend:** ${analysis['summary']['total_spend']:,.2f}\n")
            f.write(f"**AI Enhanced:** {analysis['summary']['ai_enhanced']}\n\n")
            
            # Summary statistics
            f.write("## Summary Statistics\n\n")
            f.write("### By Category\n")
            for category, data in analysis["by_category"].items():
                f.write(f"- **{category.title()}:** ${data['total']:,.2f}\n")
            f.write("\n")
            
            # Benchmark analysis
            f.write("## AI-Enhanced Benchmark Analysis\n\n")
            f.write("### Above Benchmark Items\n")
            above_benchmark = [b for b in analysis["benchmarks"] if b["status"] == "Above Benchmark"]
            for benchmark in above_benchmark:
                f.write(f"- **{benchmark['vendor']}** ({benchmark['category']}): ${benchmark['actual_spend']:,.2f} ({benchmark['variance_percentage']:+.1f}%)\n")
            f.write("\n")
            
            # AI insights
            f.write("## AI-Generated Insights\n\n")
            for benchmark in analysis["benchmarks"][:10]:  # Top 10
                ai_analysis = benchmark.get("ai_benchmark_analysis", {})
                if ai_analysis:
                    f.write(f"### {benchmark['vendor']} - {benchmark['category']}\n")
                    f.write(f"- **Variance Reason:** {ai_analysis.get('benchmark_assessment', {}).get('variance_reason', 'N/A')}\n")
                    f.write(f"- **Hidden Costs:** {', '.join(ai_analysis.get('hidden_cost_breakdown', {}).get('identified_costs', []))}\n")
                    f.write(f"- **Optimization:** {ai_analysis.get('optimization_opportunities', {}).get('immediate_savings', 'N/A')}\n\n")
            
            # Recommendations
            f.write("## AI-Enhanced Recommendations\n\n")
            for rec in analysis["recommendations"]:
                f.write(f"### {rec['type'].title()} - {rec['vendor']}\n")
                f.write(f"- **Priority:** {rec['priority'].title()}\n")
                f.write(f"- **Message:** {rec['message']}\n")
                f.write(f"- **Potential Savings:** {rec['potential_savings']}\n")
                f.write(f"- **Short-term:** {', '.join(rec['ai_insights'].get('short_term', []))}\n")
                f.write(f"- **Long-term:** {', '.join(rec['ai_insights'].get('long_term', []))}\n\n")
    
    def run_analysis(self):
        """Run the complete AI-enhanced analysis."""
        try:
            return self.analyze_with_ai_enhancement()
        except Exception as e:
            logger.error(f"AI-enhanced analysis failed: {e}")
            print(f"Error: {e}")
            return None

def main():
    """Main function to run AI-enhanced benchmark analysis."""
    analyzer = AIEnhancedBenchmarkAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 