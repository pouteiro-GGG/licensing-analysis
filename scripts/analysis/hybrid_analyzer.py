#!/usr/bin/env python3
"""
Hybrid Model Analyzer (Anthropic Only)
Uses different Anthropic models for different tasks to optimize speed and cost
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from anthropic import Anthropic, RateLimitError, APIError

from config import get_api_key, create_directories
from cost_control_manager import get_cost_control_manager

logger = logging.getLogger(__name__)

class HybridAnalyzer:
    """
    Hybrid analyzer that uses different Anthropic models for different tasks:
    - Fast/cheap Anthropic models for initial screening and categorization
    - Claude Opus 4 only for complex analysis that requires it
    """
    
    def __init__(self, anthropic_api_key: str = None):
        """Initialize the hybrid analyzer."""
        self.anthropic_api_key = anthropic_api_key or get_api_key()
        
        # Initialize Anthropic client
        self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
        
        # Cost control manager
        self.cost_control_manager = get_cost_control_manager()
        
        # Model configurations (all Anthropic models)
        self.model_configs = {
            "fast_screening": {
                "model": "claude-3-5-haiku-20241022",  # Claude Haiku 3.5 for fast screening
                "max_tokens": 500,
                "temperature": 0.1,
                "cost_per_1k_tokens": 0.0008  # $0.80 per MTok from docs
            },
            "categorization": {
                "model": "claude-3-5-haiku-20241022",  # Claude Haiku 3.5 for categorization
                "max_tokens": 300,
                "temperature": 0.1,
                "cost_per_1k_tokens": 0.0008
            },
            "complex_analysis": {
                "model": "claude-opus-4-20250514",  # Claude Opus 4 for complex analysis
                "max_tokens": 4000,
                "temperature": 0.1,
                "cost_per_1k_tokens": 0.015  # $15 per MTok from docs
            }
        }
        
        create_directories()
        logger.info("Hybrid Analyzer (Anthropic Only) initialized")
    
    def analyze_invoice_hybrid(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze invoice using hybrid approach:
        1. Fast screening to determine if analysis is needed
        2. Categorization if needed
        3. Complex analysis only for high-value or complex cases
        """
        # Check cache first
        cached_result = self.cost_control_manager.get_cached_analysis(invoice_data)
        if cached_result:
            logger.info("Using cached analysis result")
            return cached_result
        
        # Step 1: Fast screening
        screening_result = self._fast_screening(invoice_data)
        
        if not screening_result.get("needs_analysis", False):
            # Simple case - no complex analysis needed
            result = {
                "analysis_type": "simple",
                "screening_result": screening_result,
                "recommendation": "No complex analysis required",
                "cost_savings": "Used fast screening only"
            }
            self.cost_control_manager.store_analysis_result(invoice_data, result, 100, 0.000025)
            return result
        
        # Step 2: Categorization
        categorization_result = self._categorize_invoice(invoice_data)
        
        # Step 3: Determine if complex analysis is needed
        if self._needs_complex_analysis(invoice_data, categorization_result):
            # Use Claude Opus 4 for complex analysis
            complex_result = self._complex_analysis(invoice_data, categorization_result)
            result = {
                "analysis_type": "complex",
                "screening_result": screening_result,
                "categorization_result": categorization_result,
                "complex_analysis": complex_result
            }
        else:
            # Use categorization result with basic recommendations
            result = {
                "analysis_type": "categorized",
                "screening_result": screening_result,
                "categorization_result": categorization_result,
                "recommendation": "Standard analysis sufficient"
            }
        
        # Store result
        estimated_tokens = 500  # Rough estimate
        estimated_cost = (estimated_tokens / 1000) * 0.00025
        self.cost_control_manager.store_analysis_result(invoice_data, result, estimated_tokens, estimated_cost)
        
        return result
    
    def _fast_screening(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fast screening to determine if detailed analysis is needed."""
        
        # Static system prompt that can be cached
        system_prompt = {
            "type": "text",
            "text": """You are an expert licensing analyst specializing in quick invoice screening. 
            Your role is to rapidly assess whether an invoice requires detailed licensing analysis.
            Focus on vendor type, total amount, and line item complexity to make quick decisions.
            Respond with JSON only containing: needs_analysis (boolean), reason (string), 
            priority (low/medium/high), estimated_complexity (simple/moderate/complex).""",
            "cache_control": {"type": "ephemeral"}
        }
        
        # Dynamic user content
        user_content = f"""
        Quickly screen this invoice to determine if it needs detailed licensing analysis.
        
        Invoice Data:
        - Vendor: {invoice_data.get('vendor', 'Unknown')}
        - Total Amount: ${invoice_data.get('total_amount', 0):,.2f}
        - Line Items: {len(invoice_data.get('line_items', []))} items
        
        Respond with JSON only:
        {{
            "needs_analysis": true/false,
            "reason": "brief reason",
            "priority": "low/medium/high",
            "estimated_complexity": "simple/moderate/complex"
        }}
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model=self.model_configs["fast_screening"]["model"],
                max_tokens=self.model_configs["fast_screening"]["max_tokens"],
                temperature=self.model_configs["fast_screening"]["temperature"],
                system=[system_prompt],
                messages=[
                    {
                        "role": "user",
                        "content": user_content
                    }
                ]
            )
            
            # Extract and parse JSON response
            response_text = response.content[0].text
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from fast screening response")
                return {"needs_analysis": True, "reason": "JSON parsing failed", "priority": "medium", "estimated_complexity": "moderate"}
                
        except Exception as e:
            logger.error(f"Error in fast screening: {e}")
            return {"needs_analysis": True, "reason": f"Error: {str(e)}", "priority": "medium", "estimated_complexity": "moderate"}
    
    def _categorize_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize invoice for better analysis."""
        
        # Static system prompt that can be cached
        system_prompt = {
            "type": "text",
            "text": """You are an expert licensing analyst specializing in invoice categorization. 
            Your role is to categorize invoices based on vendor type, product categories, and risk factors.
            Focus on identifying software, hardware, services, and cloud components.
            Respond with JSON only containing: primary_category, secondary_categories (array), 
            vendor_type, contract_type, and risk_level.""",
            "cache_control": {"type": "ephemeral"}
        }
        
        # Dynamic user content
        line_items_text = "\n".join([
            f"- {item.get('description', 'Unknown')}: ${item.get('total_amount', 0):,.2f}"
            for item in invoice_data.get('line_items', [])
        ])
        
        user_content = f"""
        Categorize this invoice for licensing analysis:
        
        Vendor: {invoice_data.get('vendor', 'Unknown')}
        Total: ${invoice_data.get('total_amount', 0):,.2f}
        Line Items:
        {line_items_text}
        
        Respond with JSON only:
        {{
            "primary_category": "software/hardware/services/cloud",
            "secondary_categories": ["category1", "category2"],
            "vendor_type": "enterprise/smb/consumer",
            "contract_type": "subscription/one-time/consumption",
            "risk_level": "low/medium/high"
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
            logger.info(f"Categorization completed: {result.get('primary_category', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Categorization failed: {e}")
            return {"primary_category": "unknown", "risk_level": "medium"}
    
    def _needs_complex_analysis(self, invoice_data: Dict[str, Any], categorization: Dict[str, Any]) -> bool:
        """Determine if complex analysis is needed based on invoice and categorization."""
        # High-value invoices
        if invoice_data.get('total_amount', 0) > 10000:
            return True
        
        # High-risk categories
        if categorization.get('risk_level') == 'high':
            return True
        
        # Enterprise vendors
        if categorization.get('vendor_type') == 'enterprise':
            return True
        
        # Complex categories
        if categorization.get('primary_category') in ['software', 'cloud']:
            return True
        
        # Multiple line items (complex invoice)
        if len(invoice_data.get('line_items', [])) > 5:
            return True
        
        return False
    
    def _complex_analysis(self, invoice_data: Dict[str, Any], categorization: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complex analysis using Claude Opus 4."""
        
        # Static system prompt that can be cached
        system_prompt = {
            "type": "text",
            "text": """You are an expert licensing analyst specializing in detailed cost analysis and optimization. 
            Your role is to analyze licensing costs against industry standards and provide actionable recommendations.
            Focus on cost variance, optimization opportunities, risk assessment, and strategic recommendations.
            Provide detailed analysis in JSON format with cost_assessment, recommendations, and risk_assessment sections.""",
            "cache_control": {"type": "ephemeral"}
        }
        
        # Dynamic user content
        line_items_text = "\n".join([
            f"- {item.get('description', 'Unknown')}: ${item.get('total_amount', 0):,.2f}"
            for item in invoice_data.get('line_items', [])
        ])
        
        user_content = f"""
        Perform detailed licensing cost analysis for this invoice:
        
        Vendor: {invoice_data.get('vendor', 'Unknown')}
        Total Amount: ${invoice_data.get('total_amount', 0):,.2f}
        Category: {categorization.get('primary_category', 'Unknown')}
        Risk Level: {categorization.get('risk_level', 'Unknown')}
        
        Line Items:
        {line_items_text}
        
        Provide detailed analysis in JSON format:
        {{
            "cost_assessment": {{
                "overall_rating": "below_standard/at_standard/above_standard/critical",
                "cost_variance_percentage": number,
                "key_findings": ["finding1", "finding2"],
                "optimization_opportunities": ["opportunity1", "opportunity2"]
            }},
            "recommendations": {{
                "immediate_actions": ["action1", "action2"],
                "short_term": ["action1", "action2"],
                "long_term": ["action1", "action2"]
            }},
            "risk_assessment": {{
                "risk_level": "low/medium/high",
                "risk_factors": ["factor1", "factor2"]
            }}
        }}
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model=self.model_configs["complex_analysis"]["model"],
                max_tokens=self.model_configs["complex_analysis"]["max_tokens"],
                temperature=self.model_configs["complex_analysis"]["temperature"],
                system=[system_prompt],
                messages=[{"role": "user", "content": user_content}]
            )
            
            result = json.loads(response.content[0].text)
            logger.info(f"Complex analysis completed for {invoice_data.get('vendor', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Complex analysis failed: {e}")
            return {
                "cost_assessment": {
                    "overall_rating": "unknown",
                    "cost_variance_percentage": 0,
                    "key_findings": ["Analysis failed"],
                    "optimization_opportunities": []
                },
                "recommendations": {
                    "immediate_actions": [],
                    "short_term": [],
                    "long_term": []
                },
                "risk_assessment": {
                    "risk_level": "unknown",
                    "risk_factors": ["Analysis failed"]
                }
            }
    
    def analyze_batch_hybrid(self, invoices_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a batch of invoices using hybrid approach."""
        logger.info(f"Starting hybrid batch analysis of {len(invoices_data)} invoices")
        
        results = []
        for i, invoice_data in enumerate(invoices_data):
            logger.info(f"Analyzing invoice {i + 1}/{len(invoices_data)}")
            result = self.analyze_invoice_hybrid(invoice_data)
            results.append(result)
            
            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(invoices_data)} invoices analyzed")
        
        return results
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for hybrid analysis."""
        return self.cost_control_manager.get_cost_summary()
    
    def get_model_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics by model type."""
        # This would track which models were used for which tasks
        # Implementation depends on your tracking needs
        return {
            "fast_screening_calls": 0,  # Would track actual usage
            "categorization_calls": 0,
            "complex_analysis_calls": 0,
            "cost_savings": "Estimated based on model selection"
        }

def main():
    """Test the hybrid analyzer."""
    analyzer = HybridAnalyzer()
    
    # Test data
    test_invoice = {
        "vendor": "Microsoft",
        "total_amount": 5000.0,
        "line_items": [
            {"description": "Office 365 E3", "total_amount": 3000.0},
            {"description": "Azure Services", "total_amount": 2000.0}
        ]
    }
    
    # Analyze using hybrid approach
    result = analyzer.analyze_invoice_hybrid(test_invoice)
    print("Hybrid Analysis Result:")
    print(json.dumps(result, indent=2))
    
    # Show cost summary
    cost_summary = analyzer.get_cost_summary()
    print("\nCost Summary:")
    print(json.dumps(cost_summary, indent=2))

if __name__ == "__main__":
    main() 