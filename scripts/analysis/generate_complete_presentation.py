#!/usr/bin/env python3
"""
Complete Presentation Generator
Runs both presentation-style analysis and PowerPoint generation
"""

import subprocess
import sys
import os

def run_complete_presentation():
    """Run both presentation-style analysis and PowerPoint generation."""
    print("=" * 70)
    print("    COMPLETE PRESENTATION GENERATOR")
    print("=" * 70)
    print()
    
    # Step 1: Run presentation-style analysis
    print("📊 Step 1: Generating presentation-style analysis...")
    try:
        result = subprocess.run([sys.executable, "scripts/analysis/presentation_style_analysis.py"], 
                              check=True)
        print("✅ Presentation-style analysis completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Presentation-style analysis failed: {e}")
        return False
    
    print()
    
    # Step 2: Run PowerPoint generation
    print("📈 Step 2: Generating PowerPoint presentation...")
    try:
        result = subprocess.run([sys.executable, "scripts/analysis/presentation_style_ppt_generator.py"], 
                              check=True)
        print("✅ PowerPoint presentation completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ PowerPoint generation failed: {e}")
        return False
    
    print()
    print("🎉 COMPLETE PRESENTATION GENERATED SUCCESSFULLY!")
    print()
    print("📁 Output files:")
    print("   - reports/current/presentation_style_analysis_20250725/charge_assessment_presentation_report.md")
    print("   - reports/current/presentation_style_analysis_20250725/synoptek_charge_assessment_presentation.pptx")
    print("   - reports/current/presentation_style_analysis_20250725/charge_assessment_presentation.png")
    print("   - reports/current/presentation_style_analysis_20250725/*.csv (detailed data)")
    print()
    print("📋 Ready for executive presentation!")
    print("💼 Use PowerPoint for charge assessment and negotiations")
    
    return True

def main():
    """Main function."""
    success = run_complete_presentation()
    
    if success:
        print()
        print("🚀 All presentation materials generated successfully!")
        print("📊 Both markdown report and PowerPoint presentation available")
    else:
        print("❌ Presentation generation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())