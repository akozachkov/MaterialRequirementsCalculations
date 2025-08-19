@echo off
echo Compiling Java files to build directory...

REM Create build directory if it doesn't exist
if not exist "build" mkdir build

REM Compile all Java files with external libraries in classpath
javac -d build -cp "WebContent/WEB-INF/lib/*" src\com\kozachkov\material_requirements\*.java

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful!
    echo Class files are in: build directory
) else (
    echo Compilation failed!
)

pause 