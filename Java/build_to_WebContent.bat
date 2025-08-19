@echo off
echo Compiling Java files directly into WEB-INF\classes...

REM Target directory for .class files
set TARGET_DIR=WebContent\WEB-INF\classes

REM Create target directory if it doesn't exist
if not exist "%TARGET_DIR%\com\kozachkov\material_requirements" mkdir "%TARGET_DIR%\com\kozachkov\material_requirements"

REM Compile all Java files with external libraries in classpath
javac -d "%TARGET_DIR%" -cp "%TARGET_DIR%;WebContent/WEB-INF/lib/*" src\com\kozachkov\material_requirements\*.java

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful!
    echo Class files are in: %TARGET_DIR%\com\kozachkov\material_requirements
) else (
    echo Compilation failed!
)

pause
