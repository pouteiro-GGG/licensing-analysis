#!/usr/bin/env python3
"""
Main Analysis Runner
Central script for running common analysis operations
"""

import sys
import subprocess
from pathlib import Path

def run_analysis(analysis_type):
    """Run a specific analysis type."""
    
    analysis_scripts = {
        "employee_growth": "scripts/analysis/employee_growth_analysis.py",
        "monthly_billing": "scripts/analysis/monthly_billing_analysis.py",
        "synoptek_licensing": "scripts/analysis/synoptek_licensing_analysis.py",
        "temporal": "scripts/analysis/comprehensive_temporal_analysis.py",
        "vendor": "scripts/analysis/executive_vendor_analysis.py",
        "comprehensive": "scripts/analysis/comprehensive_executive_analysis.py",
        "presentation_style": "scripts/analysis/presentation_style_analysis.py",
        "powerpoint": "scripts/analysis/presentation_style_ppt_generator.py",
        "template_powerpoint": "scripts/analysis/template_based_ppt_generator.py",
        "complete_presentation": "scripts/analysis/generate_complete_presentation.py"
    }
    
    if analysis_type not in analysis_scripts:
        print(f"Unknown analysis type: {analysis_type}")
        print(f"Available types: {', '.join(analysis_scripts.keys())}")
        return False
    
    script_path = Path(analysis_scripts[analysis_type])
    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return False
    
    print(f"Running {analysis_type} analysis...")
    try:
        result = subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"{analysis_type} analysis completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{analysis_type} analysis failed: {e}")
        return False

def main():
    """Main function."""
    
    if len(sys.argv) < 2:
        print("Usage: python main_runner.py <analysis_type>")
        print("Available analysis types:")
        print("  - employee_growth: Employee growth analysis")
        print("  - monthly_billing: Monthly billing analysis")
        print("  - synoptek_licensing: Synoptek licensing analysis")
        print("  - temporal: Comprehensive temporal analysis")
        print("  - vendor: Executive vendor analysis")
        print("  - comprehensive: Comprehensive executive analysis")
        print("  - presentation_style: Presentation-style charge assessment")
        print("  - powerpoint: PowerPoint presentation generator")
        print("  - template_powerpoint: Template-based PowerPoint (uses your template)")
        print("  - complete_presentation: Complete presentation (markdown + PowerPoint)")
        return
    
    analysis_type = sys.argv[1]
    run_analysis(analysis_type)

if __name__ == "__main__":
    main()
