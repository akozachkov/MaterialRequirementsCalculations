@echo off
REM Usage example: calculateBOM.bat ArticleExampleProduct 1000.0

set PRODUCT_NAME=%1
set TARGET_AMOUNT=%2

python material_requirements_calculations.py %PRODUCT_NAME% %TARGET_AMOUNT%

pause



