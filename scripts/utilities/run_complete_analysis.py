#!/usr/bin/env python3
"""
Complete Licensing Analysis Suite
Runs the entire analysis sequence from data cleaning through all reports and dashboard
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description, step_num, total_steps):
    """Run a command and handle errors."""
    print(f"\n[{step_num}/{total_steps}] {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print("Output:", result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e}")
        if e.stdout:
            print("Output:", e.stdout.strip())
        if e.stderr:
            print("Error Output:", e.stderr.strip())
        return False

def main():
    """Run the complete analysis sequence."""
    
    print("=" * 60)
    print("    COMPLETE LICENSING ANALYSIS SUITE")
    print("=" * 60)
    print()
    print("This will run the complete analysis sequence:")
    print("1. Data Quality Analysis & Cleaning")
    print("2. Granular MSP Service Analysis")
    print("3. Licensing Analysis (AI-powered)")
    print("4. Enhanced Industry Benchmark Analysis (2024-2025 data)")
    print("5. AI-Enhanced Benchmark Analysis (Intelligent Categorization)")
    print("6. Executive Summary Reports")
    print("7. Professional Document with Charts")
    print("8. Interactive Dashboard")
    print()
    
    # Check if required files exist
    required_files = [
        "data_quality_analyzer.py",
        "granular_msp_analyzer.py",
        "licensing_analyzer.py",
        "enhanced_industry_analyzer.py",
        "ai_enhanced_benchmark_analyzer.py",
        "simple_executive_report.py",
        "report_exporter.py",
        "dashboard.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\nPlease ensure all analysis scripts are present.")
        input("Press Enter to exit...")
        return False
    
    print("✅ All required files found!")
    print("Starting sequence...")
    print()
    
    # Step 1: Data Quality Analysis & Cleaning
    if not run_command("python data_quality_analyzer.py", "Running Data Quality Analysis & Cleaning", 1, 7):
        input("Press Enter to exit...")
        return False
    
    # Step 2: Granular MSP Service Analysis
    if not run_command("python granular_msp_analyzer.py", "Running Granular MSP Service Analysis", 2, 7):
        input("Press Enter to exit...")
        return False
    
    # Step 3: Licensing Analysis
    if not run_command("python licensing_analyzer.py", "Running Licensing Analysis", 3, 7):
        input("Press Enter to exit...")
        return False
    
    # Step 4: Enhanced Industry Benchmark Analysis
    if not run_command("python enhanced_industry_analyzer.py", "Running Enhanced Industry Benchmark Analysis", 4, 8):
        input("Press Enter to exit...")
        return False
    
    # Step 5: AI-Enhanced Benchmark Analysis
    if not run_command("python ai_enhanced_benchmark_analyzer.py", "Running AI-Enhanced Benchmark Analysis", 5, 8):
        input("Press Enter to exit...")
        return False
    
    # Step 6: Executive Summary Reports
    if not run_command("python simple_executive_report.py", "Generating Executive Summary Reports", 6, 8):
        input("Press Enter to exit...")
        return False
    
    # Step 7: Professional Document with Charts
    if not run_command("python report_exporter.py", "Generating Professional Document with Charts", 7, 8):
        input("Press Enter to exit...")
        return False
    
    # Step 8: Launch Interactive Dashboard
    print(f"\n[8/8] Launching Interactive Dashboard")
    print("=" * 50)
    
    print("\n🎉 Complete Analysis Suite Finished Successfully!")
    print()
    
    # Show generated files
    print("📁 Generated Files:")
    reports_dir = "reports/executive"
    charts_dir = "reports/charts"
    
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith(('.md', '.docx', '.json')):
                print(f"   - {reports_dir}/{file}")
    
    if os.path.exists(charts_dir):
        chart_count = len([f for f in os.listdir(charts_dir) if f.endswith('.png')])
        print(f"   - {charts_dir}/ (5 professional charts)")
    
    print()
    print("🌐 Dashboard will be available at: http://localhost:5000")
    print()
    
    # Ask user if they want to launch dashboard
    response = input("Launch interactive dashboard now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("Starting interactive dashboard...")
        print("Press Ctrl+C to stop the server")
        print()
        
        try:
            # Launch dashboard
            subprocess.run("python dashboard.py", shell=True, check=True)
        except KeyboardInterrupt:
            print("\nDashboard stopped by user.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Dashboard failed to start: {e}")
    else:
        print("Dashboard launch skipped. You can run it later with:")
        print("   python dashboard.py")
        print("   or")
        print("   launch_dashboard.bat")
    
    print("\n✅ Complete analysis suite finished!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1) 