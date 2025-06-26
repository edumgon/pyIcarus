@echo off
setlocal enabledelayedexpansion

echo Checking environment for pyIcarus...

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

:: Function to check if a Python package is installed
:check_package
set package=%~1
python -c "import %package%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    exit /b 0
) else (
    exit /b 1
)

:: Check for GTK environment first
call :check_package gi
if %ERRORLEVEL% EQU 0 (
    echo GTK environment detected.
    
    :: Check GTK requirements
    set MISSING_PACKAGES=0
    
    :: Check for PyGObject
    python -c "import gi" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo PyGObject is not installed.
        set MISSING_PACKAGES=1
    )
    
    :: Check for requests
    python -c "import requests" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo requests module is not installed.
        set MISSING_PACKAGES=1
    )
    
    if !MISSING_PACKAGES! EQU 0 (
        echo All GTK requirements are satisfied. Starting GTK application...
        python ponto_app_gtk.py
        exit /b 0
    ) else (
        echo Installing missing requirements...
        pip install -r requirements.txt
        
        :: Check if installation was successful
        if %ERRORLEVEL% EQU 0 (
            echo Requirements installed successfully. Starting GTK application...
            python ponto_app_gtk.py
            exit /b 0
        ) else (
            echo Failed to install requirements. Please install them manually.
            pause
            exit /b 1
        )
    )
) else (
    :: Check for PyQt environment
    call :check_package PyQt6
    if %ERRORLEVEL% EQU 0 (
        echo PyQt environment detected.
        
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
            python ponto_app_pyqt.py
            exit /b 0
        ) else (
            echo Installing missing requirements...
            pip install -r requirements_pyqt.txt
            
            :: Check if installation was successful
            if %ERRORLEVEL% EQU 0 (
                echo Requirements installed successfully. Starting PyQt application...
                python ponto_app_pyqt.py
                exit /b 0
            ) else (
                echo Failed to install requirements. Please install them manually.
                pause
                exit /b 1
            )
        )
    ) else (
        echo No GUI environment detected. Installing PyQt by default...
        pip install -r requirements_pyqt.txt
        
        if %ERRORLEVEL% EQU 0 (
            echo PyQt requirements installed successfully. Starting PyQt application...
            python ponto_app_pyqt.py
            exit /b 0
        ) else (
            echo Failed to install PyQt requirements. Please install them manually.
            pause
            exit /b 1
        )
    )
)

endlocal
