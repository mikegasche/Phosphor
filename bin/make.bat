@echo off
REM ------------------------------------------------------------------------------
REM make.bat - Build Phosphor.exe (Windows) using PyInstaller
REM ------------------------------------------------------------------------------

SETLOCAL ENABLEDELAYEDEXPANSION

REM --- 1. Detect architecture ---
echo ==> Detecting architecture...
IF "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    SET ARCH=x64
) ELSE (
    SET ARCH=x86
)
echo ==> Detected architecture: %ARCH%

REM --- 2. Set project root (parent directory of this script) ---
SET SCRIPT_DIR=%~dp0
SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
FOR %%I IN ("%SCRIPT_DIR%..") DO SET PROJECT_ROOT=%%~fI
cd /d "%PROJECT_ROOT%"
echo ==> Project root: %PROJECT_ROOT%

REM --- 3. Check virtual environment ---
IF NOT EXIST venv\Scripts\activate.bat (
    echo ERROR: virtual environment not found.
    echo Run setup.bat first.
    exit /b 1
)

REM --- 4. Activate virtual environment ---
call venv\Scripts\activate.bat
echo ==> Using Python:
python --version

REM --- 5. Environment variables ---
SET PYTHONPATH=%PROJECT_ROOT%\app;%PYTHONPATH%
SET LC_NUMERIC=C
SET LANG=C

echo ==> PYTHONPATH=%PYTHONPATH%
echo ==> Locale set: LC_NUMERIC=%LC_NUMERIC%, LANG=%LANG%

REM --- 6. Clean old builds ---
IF EXIST build rmdir /s /q build
IF EXIST dist rmdir /s /q dist
IF EXIST Phosphor.spec del /f /q Phosphor.spec

REM --- 7. PyInstaller build ---
pyinstaller ^
    --name Phosphor ^
    --windowed ^
    --icon app\resources\app_icon.ico ^
    --add-data "app\resources;resources" ^
    app\phosphor.py

IF ERRORLEVEL 1 (
    echo ERROR: Build failed.
    exit /b 1
)

echo ==> Build finished.
echo ==> Check dist\Phosphor\Phosphor.exe

ENDLOCAL
pause
