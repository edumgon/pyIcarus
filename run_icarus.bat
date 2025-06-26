@echo off
setlocal enabledelayedexpansion

:: Get the directory where the batch file is located
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo Checking environment for pyIcarus...

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

:: Windows users should use PyQt directly
echo Windows environment detected, using PyQt...

:: Check PyQt requirements
set MISSING_PACKAGES=0

:: Check for PyQt6
python -c "import PyQt6" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyQt6 is not installed.
    set MISSING_PACKAGES=1
)

:: Check for requests
python -c "import requests" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo requests module is not installed.
    set MISSING_PACKAGES=1
)

:: Check for cryptography
python -c "import cryptography" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo cryptography module is not installed.
    set MISSING_PACKAGES=1
)

if !MISSING_PACKAGES! EQU 0 (
    echo All PyQt requirements are satisfied. Starting PyQt application...
    python "%SCRIPT_DIR%\ponto_app_pyqt.py"
    exit /b 0
) else (
    echo Installing missing requirements...
    pip install -r "%SCRIPT_DIR%\requirements_pyqt.txt"
    
    :: Check if installation was successful
    if %ERRORLEVEL% EQU 0 (
        echo Requirements installed successfully. Starting PyQt application...
        python "%SCRIPT_DIR%\ponto_app_pyqt.py"
        exit /b 0
    ) else (
        echo Failed to install requirements. Please install them manually.
        pause
        exit /b 1
    )
)

endlocal
