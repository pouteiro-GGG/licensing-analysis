@echo off
echo.
echo ========================================
echo    COMPLETE LICENSING ANALYSIS SUITE
echo ========================================
echo.
echo This will run the complete analysis sequence:
echo 1. Data Quality Analysis & Cleaning
echo 2. Granular MSP Service Analysis
echo 3. Licensing Analysis (AI-powered)
echo 4. Enhanced Industry Benchmark Analysis (2024-2025 data)
echo 5. Executive Summary Reports
echo 6. Professional Document with Charts
echo 7. Interactive Dashboard
echo.
echo Starting sequence...
echo.

REM Step 1: Data Quality Analysis & Cleaning
echo [1/7] Running Data Quality Analysis & Cleaning...
echo ========================================
python data_quality_analyzer.py
if %errorlevel% neq 0 (
    echo ❌ Data Quality Analysis failed!
    pause
    exit /b 1
)
echo ✅ Data Quality Analysis completed successfully!
echo.

REM Step 2: Granular MSP Service Analysis
echo [2/7] Running Granular MSP Service Analysis...
echo ========================================
python granular_msp_analyzer.py
if %errorlevel% neq 0 (
    echo ❌ Granular MSP Analysis failed!
    pause
    exit /b 1
)
echo ✅ Granular MSP Analysis completed successfully!
echo.

REM Step 3: Run Licensing Analysis
echo [3/7] Running Licensing Analysis...
echo ========================================
python licensing_analyzer.py
if %errorlevel% neq 0 (
    echo ❌ Licensing Analysis failed!
    pause
    exit /b 1
)
echo ✅ Licensing Analysis completed successfully!
echo.

REM Step 4: Enhanced Industry Benchmark Analysis
echo [4/7] Running Enhanced Industry Benchmark Analysis...
echo ========================================
python enhanced_industry_analyzer.py
if %errorlevel% neq 0 (
    echo ❌ Enhanced Industry Benchmark Analysis failed!
    pause
    exit /b 1
)
echo ✅ Enhanced Industry Benchmark Analysis completed successfully!
echo.

REM Step 5: Executive Summary Reports
echo [5/7] Generating Executive Summary Reports...
echo ========================================
python simple_executive_report.py
if %errorlevel% neq 0 (
    echo ❌ Executive Summary Reports failed!
    pause
    exit /b 1
)
echo ✅ Executive Summary Reports completed successfully!
echo.

REM Step 6: Professional Document with Charts
echo [6/7] Generating Professional Document with Charts...
echo ========================================
python report_exporter.py
if %errorlevel% neq 0 (
    echo ❌ Professional Document generation failed!
    pause
    exit /b 1
)
echo ✅ Professional Document with Charts completed successfully!
echo.

REM Step 7: Launch Interactive Dashboard
echo [7/7] Launching Interactive Dashboard...
echo ========================================
echo.
echo 🎉 Complete Analysis Suite Finished Successfully!
echo.
echo 📁 Generated Files:
echo    - reports/executive/clean_licensing_analysis_*.md
echo    - reports/executive/granular_msp_analysis_*.md
echo    - reports/executive/enhanced_industry_benchmark_analysis_*.md
echo    - reports/executive/enhanced_executive_summary_*.md
echo    - reports/executive/licensing_analysis_report_*.docx
echo    - reports/charts/*.png (5 professional charts)
echo.
echo 🌐 Dashboard will be available at: http://localhost:5000
echo.
echo Press any key to launch the interactive dashboard...
pause >nul

echo Starting interactive dashboard...
python dashboard.py 