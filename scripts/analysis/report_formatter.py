#!/usr/bin/env python3
"""
Human-Readable Report Formatter
Converts JSON analysis results into beautifully formatted, easy-to-read reports
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
import textwrap

class ReportFormatter:
    """
    Formats licensing analysis results into human-readable reports.
    """
    
    def __init__(self):
        self.report_width = 80
        self.section_separator = "=" * self.report_width
        self.subsection_separator = "-" * self.report_width
    
    def format_comprehensive_report(self, analysis_data: Dict[str, Any], output_file: str = None) -> str:
        """
        Format comprehensive analysis results into a human-readable report.
        
        Args:
            analysis_data: Dictionary containing analysis results
            output_file: Optional file path to save the report
            
        Returns:
            Formatted report as string
        """
        report_lines = []
        
        # Header
        report_lines.extend(self._format_header())
        
        # Executive Summary
        if "comprehensive_summary" in analysis_data:
            report_lines.extend(self._format_executive_summary(analysis_data["comprehensive_summary"]))
        
        # Key Findings
        if "aggregated_findings" in analysis_data:
            report_lines.extend(self._format_key_findings(analysis_data["aggregated_findings"]))
        
        # Vendor Analysis
        if "comprehensive_summary" in analysis_data:
            report_lines.extend(self._format_vendor_analysis(analysis_data["comprehensive_summary"]))
        
        # Category Breakdown
        if "aggregated_findings" in analysis_data:
            report_lines.extend(self._format_category_breakdown(analysis_data["aggregated_findings"]))
        
        # Risk Assessment
        if "aggregated_findings" in analysis_data:
            report_lines.extend(self._format_risk_assessment(analysis_data["aggregated_findings"]))
        
        # Recommendations
        if "recommendations" in analysis_data:
            report_lines.extend(self._format_recommendations(analysis_data["recommendations"]))
        
        # Footer
        report_lines.extend(self._format_footer())
        
        # Combine all lines
        report_text = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Human-readable report saved to: {output_file}")
        
        return report_text
    
    def _format_header(self) -> List[str]:
        """Format report header."""
        return [
            self.section_separator,
            "                    LICENSING ANALYSIS REPORT",
            "                    Cost Optimization & Risk Assessment",
            self.section_separator,
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
        ]
    
    def _format_executive_summary(self, summary: Dict[str, Any]) -> List[str]:
        """Format executive summary section."""
        lines = [
            "📊 EXECUTIVE SUMMARY",
            self.subsection_separator,
            "",
        ]
        
        # Overall assessment with color coding
        assessment = summary.get("overall_assessment", "Unknown")
        if assessment == "Critical":
            assessment_display = "🔴 CRITICAL - Immediate Action Required"
        elif assessment == "Above Standard":
            assessment_display = "🟡 ABOVE STANDARD - Optimization Opportunities Available"
        elif assessment == "At Standard":
            assessment_display = "🟢 AT STANDARD - Costs Are Reasonable"
        else:
            assessment_display = f"⚪ {assessment.upper()}"
        
        lines.extend([
            f"Overall Assessment:     {assessment_display}",
            f"Total Invoices Analyzed: {summary.get('total_invoices_analyzed', 0):,}",
            f"Total Cost Analyzed:     ${summary.get('total_cost', 0):,.2f}",
            f"Average Cost Variance:   {summary.get('average_cost_variance_percentage', 0):.1f}%",
            "",
        ])
        
        # Top vendors
        top_vendors = summary.get("top_vendors_by_cost", [])
        if top_vendors:
            lines.extend([
                "🏢 TOP VENDORS BY COST:",
                "",
            ])
            for i, (vendor, cost) in enumerate(top_vendors[:5], 1):
                lines.append(f"  {i}. {vendor}: ${cost:,.2f}")
            lines.append("")
        
        return lines
    
    def _format_key_findings(self, findings: Dict[str, Any]) -> List[str]:
        """Format key findings section."""
        lines = [
            "🔍 KEY FINDINGS",
            self.subsection_separator,
            "",
        ]
        
        key_findings = findings.get("key_findings", [])
        if key_findings:
            # Group findings by type
            critical_findings = []
            optimization_findings = []
            informational_findings = []
            
            for finding in key_findings:
                finding_lower = finding.lower()
                if any(keyword in finding_lower for keyword in ["excessive", "above", "high", "critical", "overpaying"]):
                    critical_findings.append(finding)
                elif any(keyword in finding_lower for keyword in ["opportunity", "optimization", "savings", "negotiate"]):
                    optimization_findings.append(finding)
                else:
                    informational_findings.append(finding)
            
            # Critical findings
            if critical_findings:
                lines.extend([
                    "🚨 CRITICAL ISSUES:",
                    "",
                ])
                for i, finding in enumerate(critical_findings[:10], 1):
                    wrapped_finding = textwrap.fill(f"  {i}. {finding}", width=self.report_width-4, subsequent_indent="    ")
                    lines.append(wrapped_finding)
                    lines.append("")
            
            # Optimization opportunities
            if optimization_findings:
                lines.extend([
                    "💡 OPTIMIZATION OPPORTUNITIES:",
                    "",
                ])
                for i, finding in enumerate(optimization_findings[:10], 1):
                    wrapped_finding = textwrap.fill(f"  {i}. {finding}", width=self.report_width-4, subsequent_indent="    ")
                    lines.append(wrapped_finding)
                    lines.append("")
            
            # Informational findings
            if informational_findings:
                lines.extend([
                    "ℹ️  INFORMATIONAL FINDINGS:",
                    "",
                ])
                for i, finding in enumerate(informational_findings[:5], 1):
                    wrapped_finding = textwrap.fill(f"  {i}. {finding}", width=self.report_width-4, subsequent_indent="    ")
                    lines.append(wrapped_finding)
                    lines.append("")
        
        return lines
    
    def _format_vendor_analysis(self, summary: Dict[str, Any]) -> List[str]:
        """Format vendor analysis section."""
        lines = [
            "🏢 VENDOR ANALYSIS",
            self.subsection_separator,
            "",
        ]
        
        top_vendors = summary.get("top_vendors_by_cost", [])
        if top_vendors:
            lines.extend([
                "Top 5 Vendors by Total Cost:",
                "",
                f"{'Vendor':<40} {'Total Cost':<15} {'% of Total':<10}",
                "-" * 65,
            ])
            
            total_cost = summary.get("total_cost", 0)
            for vendor, cost in top_vendors[:5]:
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                vendor_short = vendor[:39] + "..." if len(vendor) > 40 else vendor
                lines.append(f"{vendor_short:<40} ${cost:<14,.2f} {percentage:<9.1f}%")
            
            lines.append("")
            
            # Vendor recommendations
            lines.extend([
                "📋 VENDOR RECOMMENDATIONS:",
                "",
            ])
            
            for vendor, cost in top_vendors[:3]:
                if cost > 1000000:  # Over $1M
                    lines.append(f"  • {vendor}: High-value vendor - prioritize negotiation efforts")
                elif cost > 100000:  # Over $100K
                    lines.append(f"  • {vendor}: Medium-value vendor - review pricing and terms")
                else:
                    lines.append(f"  • {vendor}: Standard vendor - monitor for cost increases")
            
            lines.append("")
        
        return lines
    
    def _format_category_breakdown(self, findings: Dict[str, Any]) -> List[str]:
        """Format category breakdown section."""
        lines = [
            "📊 CATEGORY BREAKDOWN",
            self.subsection_separator,
            "",
        ]
        
        category_breakdown = findings.get("category_breakdown", {})
        if category_breakdown:
            lines.extend([
                "Cost Analysis by Category:",
                "",
                f"{'Category':<30} {'Total Cost':<15} {'Key Insights':<30}",
                "-" * 75,
            ])
            
            for category, data in category_breakdown.items():
                cost = data.get("cost", 0)
                recommendations = data.get("recommendations", [])
                
                # Get key insight from recommendations
                key_insight = "No specific insights available"
                if recommendations:
                    key_insight = recommendations[0][:29] + "..." if len(recommendations[0]) > 30 else recommendations[0]
                
                category_short = category[:29] + "..." if len(category) > 30 else category
                lines.append(f"{category_short:<30} ${cost:<14,.2f} {key_insight:<30}")
            
            lines.append("")
        
        return lines
    
    def _format_risk_assessment(self, findings: Dict[str, Any]) -> List[str]:
        """Format risk assessment section."""
        lines = [
            "⚠️  RISK ASSESSMENT",
            self.subsection_separator,
            "",
        ]
        
        risk_assessment = findings.get("risk_assessment", {})
        
        # High risk items
        high_risk = risk_assessment.get("high", [])
        if high_risk:
            lines.extend([
                "🔴 HIGH RISK ITEMS:",
                "",
            ])
            for i, item in enumerate(high_risk[:5], 1):
                wrapped_item = textwrap.fill(f"  {i}. {item}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_item)
                lines.append("")
        
        # Medium risk items
        medium_risk = risk_assessment.get("medium", [])
        if medium_risk:
            lines.extend([
                "🟡 MEDIUM RISK ITEMS:",
                "",
            ])
            for i, item in enumerate(medium_risk[:5], 1):
                wrapped_item = textwrap.fill(f"  {i}. {item}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_item)
                lines.append("")
        
        # Low risk items
        low_risk = risk_assessment.get("low", [])
        if low_risk:
            lines.extend([
                "🟢 LOW RISK ITEMS:",
                "",
            ])
            for i, item in enumerate(low_risk[:3], 1):
                wrapped_item = textwrap.fill(f"  {i}. {item}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_item)
                lines.append("")
        
        return lines
    
    def _format_recommendations(self, recommendations: Dict[str, Any]) -> List[str]:
        """Format recommendations section."""
        lines = [
            "🎯 RECOMMENDATIONS",
            self.subsection_separator,
            "",
        ]
        
        # Immediate actions
        immediate_actions = recommendations.get("immediate_actions", [])
        if immediate_actions:
            lines.extend([
                "⚡ IMMEDIATE ACTIONS (Next 30 Days):",
                "",
            ])
            for i, action in enumerate(immediate_actions[:5], 1):
                wrapped_action = textwrap.fill(f"  {i}. {action}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_action)
                lines.append("")
        
        # Short-term optimizations
        short_term = recommendations.get("short_term_optimizations", [])
        if short_term:
            lines.extend([
                "📈 SHORT-TERM OPTIMIZATIONS (30-90 Days):",
                "",
            ])
            for i, optimization in enumerate(short_term[:5], 1):
                wrapped_opt = textwrap.fill(f"  {i}. {optimization}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_opt)
                lines.append("")
        
        # Long-term strategies
        long_term = recommendations.get("long_term_strategies", [])
        if long_term:
            lines.extend([
                "🚀 LONG-TERM STRATEGIES (3-12 Months):",
                "",
            ])
            for i, strategy in enumerate(long_term[:5], 1):
                wrapped_strategy = textwrap.fill(f"  {i}. {strategy}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_strategy)
                lines.append("")
        
        # Estimated savings
        estimated_savings = recommendations.get("estimated_savings", {})
        if estimated_savings:
            lines.extend([
                "💰 ESTIMATED SAVINGS:",
                "",
                f"  Immediate (30 days):     ${estimated_savings.get('immediate', 0):,.2f}",
                f"  Short-term (90 days):    ${estimated_savings.get('short_term', 0):,.2f}",
                f"  Long-term (12 months):   ${estimated_savings.get('long_term', 0):,.2f}",
                "",
            ])
        
        return lines
    
    def _format_footer(self) -> List[str]:
        """Format report footer."""
        return [
            self.section_separator,
            "📞 NEXT STEPS",
            "",
            "1. Review critical findings and immediate actions",
            "2. Schedule vendor negotiations for high-value contracts",
            "3. Implement cost optimization recommendations",
            "4. Set up regular cost monitoring and review cycles",
            "5. Consider implementing automated cost alerts",
            "",
            "For questions or additional analysis, contact your IT cost management team.",
            "",
            self.section_separator,
        ]
    
    def format_vendor_specific_report(self, vendor_data: Dict[str, Any], vendor_name: str) -> str:
        """Format vendor-specific analysis report."""
        lines = [
            self.section_separator,
            f"                    VENDOR ANALYSIS: {vendor_name.upper()}",
            "                    Detailed Cost Assessment & Recommendations",
            self.section_separator,
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
        ]
        
        # Vendor summary
        vendor_analysis = vendor_data.get("vendor_analysis", {})
        if vendor_analysis:
            lines.extend([
                "📊 VENDOR SUMMARY",
                self.subsection_separator,
                "",
                f"Vendor Name:              {vendor_analysis.get('vendor_name', vendor_name)}",
                f"Total Invoices:           {vendor_analysis.get('total_invoices', 0):,}",
                f"Total Cost:               ${vendor_analysis.get('total_cost', 0):,.2f}",
                f"Average Cost Variance:    {vendor_analysis.get('average_cost_variance', 0):.1f}%",
                f"Assessment:               {vendor_analysis.get('vendor_assessment', 'Unknown')}",
                "",
            ])
        
        # Key findings
        key_findings = vendor_analysis.get("key_findings", [])
        if key_findings:
            lines.extend([
                "🔍 KEY FINDINGS:",
                "",
            ])
            for i, finding in enumerate(key_findings[:10], 1):
                wrapped_finding = textwrap.fill(f"  {i}. {finding}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_finding)
                lines.append("")
        
        # Recommendations
        recommendations = vendor_analysis.get("recommendations", [])
        if recommendations:
            lines.extend([
                "🎯 RECOMMENDATIONS:",
                "",
            ])
            for i, rec in enumerate(recommendations[:10], 1):
                wrapped_rec = textwrap.fill(f"  {i}. {rec}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_rec)
                lines.append("")
        
        # Risk items
        risk_items = vendor_analysis.get("risk_items", [])
        if risk_items:
            lines.extend([
                "⚠️  RISK ITEMS:",
                "",
            ])
            for i, risk in enumerate(risk_items[:5], 1):
                wrapped_risk = textwrap.fill(f"  {i}. {risk}", width=self.report_width-4, subsequent_indent="    ")
                lines.append(wrapped_risk)
                lines.append("")
        
        lines.extend([
            self.section_separator,
        ])
        
        return "\n".join(lines)
    
    def format_cost_control_report(self, cost_stats: Dict[str, Any], output_file: str = None) -> str:
        """Format cost control statistics report."""
        lines = [
            self.section_separator,
            "                    COST CONTROL REPORT",
            "                    API Usage & Optimization Metrics",
            self.section_separator,
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "📊 COST SUMMARY",
            self.subsection_separator,
            "",
            f"Total API Calls:          {cost_stats.get('total_api_calls', 0):,}",
            f"Cache Hits:               {cost_stats.get('cache_hits', 0):,}",
            f"Cache Misses:             {cost_stats.get('cache_misses', 0):,}",
            f"Cache Hit Rate:           {cost_stats.get('cache_hit_rate', 0):.1%}",
            f"Total Cost:               ${cost_stats.get('total_cost_usd', 0):.4f}",
            f"Cost Savings:             ${cost_stats.get('cost_savings_usd', 0):.4f}",
            f"Net Cost:                 ${cost_stats.get('net_cost_usd', 0):.4f}",
            "",
        ]
        
        # Efficiency assessment
        hit_rate = cost_stats.get('cache_hit_rate', 0)
        if hit_rate >= 0.8:
            efficiency_status = "🟢 Excellent - High cache efficiency"
        elif hit_rate >= 0.6:
            efficiency_status = "🟡 Good - Moderate cache efficiency"
        elif hit_rate >= 0.4:
            efficiency_status = "🟠 Fair - Room for improvement"
        else:
            efficiency_status = "🔴 Poor - Low cache efficiency"
        
        lines.extend([
            f"Efficiency Status:        {efficiency_status}",
            "",
        ])
        
        lines.extend([
            self.section_separator,
        ])
        
        # Combine all lines
        report_text = "\n".join(lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Cost control report saved to: {output_file}")
        
        return report_text

def format_report_from_file(json_file_path: str, output_file: str = None) -> str:
    """
    Format a report from a JSON file.
    
    Args:
        json_file_path: Path to the JSON analysis file
        output_file: Optional path for the formatted report
        
    Returns:
        Formatted report as string
    """
    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Format the report
        formatter = ReportFormatter()
        report_text = formatter.format_comprehensive_report(analysis_data, output_file)
        
        return report_text
        
    except Exception as e:
        return f"Error formatting report: {e}"

def main():
    """Main function for testing the report formatter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Format licensing analysis reports")
    parser.add_argument("--input", required=True, help="Input JSON file path")
    parser.add_argument("--output", help="Output formatted report file path")
    parser.add_argument("--type", choices=["comprehensive", "vendor", "cost"], default="comprehensive", 
                       help="Type of report to format")
    
    args = parser.parse_args()
    
    try:
        # Load JSON data
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format based on type
        formatter = ReportFormatter()
        
        if args.type == "comprehensive":
            report_text = formatter.format_comprehensive_report(data, args.output)
        elif args.type == "vendor":
            vendor_name = "Unknown Vendor"
            report_text = formatter.format_vendor_specific_report(data, vendor_name)
        elif args.type == "cost":
            report_text = formatter.format_cost_control_report(data)
        
        if not args.output:
            print(report_text)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 