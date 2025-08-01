#!/usr/bin/env python3
"""
Presentation Report Generator
Generates both Word and PowerPoint presentations from analysis data
"""

import os
import sys
from datetime import datetime

def main():
    """Generate both Word and PowerPoint presentations."""
    print("=" * 60)
    print("    PRESENTATION REPORT GENERATOR")
    print("=" * 60)
    print()
    print("This will generate professional presentation materials:")
    print("1. Comprehensive Word Document (Executive Report)")
    print("2. PowerPoint Presentation (Executive Slides)")
    print()
    
    # Check if analysis data exists
    required_files = [
        "reports/executive/cleaned_licensing_data_20250725.json",
        "reports/executive/enhanced_industry_analysis_20250725.json",
        "reports/executive/granular_msp_analysis_20250725.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required analysis files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print()
        print("Please run the complete analysis suite first:")
        print("   python run_complete_analysis.py")
        return
    
    print("✅ All required analysis files found!")
    print()
    
    # Generate Word document
    print("[1/2] Generating Comprehensive Word Document...")
    print("-" * 50)
    try:
        from comprehensive_executive_report import ComprehensiveExecutiveReport
        generator = ComprehensiveExecutiveReport()
        generator.generate_report()
        print("✅ Word document generated successfully!")
    except Exception as e:
        print(f"❌ Error generating Word document: {e}")
        return
    
    print()
    
    # Generate PowerPoint presentation
    print("[2/2] Generating PowerPoint Presentation...")
    print("-" * 50)
    try:
        from executive_presentation import ExecutivePresentation
        generator = ExecutivePresentation()
        generator.generate_presentation()
        print("✅ PowerPoint presentation generated successfully!")
    except Exception as e:
        print(f"❌ Error generating PowerPoint presentation: {e}")
        return
    
    print()
    print("🎉 Presentation Reports Generated Successfully!")
    print()
    print("📁 Generated Files:")
    print("   - reports/executive/comprehensive_executive_report_20250725.docx")
    print("   - reports/executive/executive_presentation_20250725.pptx")
    print("   - reports/charts/ (Professional charts for presentations)")
    print()
    print("📋 What's Included:")
    print("   • Executive Summary with Key Metrics")
    print("   • Industry Benchmark Analysis")
    print("   • MSP Service Breakdown")
    print("   • Data Quality Insights")
    print("   • Cost Optimization Recommendations")
    print("   • Strategic Action Plans")
    print("   • Professional Charts and Visualizations")
    print()
    print("💡 Usage Tips:")
    print("   • Word Document: Detailed analysis for stakeholders")
    print("   • PowerPoint: Executive presentation for meetings")
    print("   • Both use intelligent vendor consolidation")
    print("   • Charts are high-resolution (300 DPI)")
    print("   • Ready for immediate presentation to executives")

if __name__ == "__main__":
    main() 