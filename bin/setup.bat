@echo off
REM ------------------------------------------------------------------------------
REM setup.bat
REM Windows - Python env, venv, PySide6 + Pillow + PyInstaller
REM ------------------------------------------------------------------------------

SETLOCAL ENABLEDELAYEDEXPANSION

REM --- 0. Detect architecture ---
echo == Detecting architecture...
IF "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    SET ARCH=x64
) ELSE (
    SET ARCH=x86
)
echo ==> Detected architecture: %ARCH%

REM --- 1. Determine project root (bin\ is parallel to app\) ---
SET "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
REM Project root is one level up
FOR %%I IN ("%SCRIPT_DIR%\..") DO SET "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"

REM --- 2. Check for Python installation ---
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found. Please install Python 3.11.x first.
    exit /b 1
)

REM --- 3. Remove old venv ---
echo ==> Removing old venv...
rmdir /s /q venv

REM --- 4. Create new venv ---
echo ==> Creating new venv...
python -m venv venv

REM --- 5. Activate venv ---
call venv\Scripts\activate.bat

REM --- 6. Upgrade pip, setuptools, wheel ---
echo ==> Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel

REM --- 7. Install required packages ---
echo ==> Installing required packages...
pip install PySide6 pyinstaller python-mpv

REM --- 8. Check installed packages ---
echo ==> Installed packages:
python -m pip show PySide6
python -m pip show pyinstaller
python -m pip show python-mpv

python --version

echo ==> Setup complete. You can now run bin\make.bat to build the app.
ENDLOCAL
pause
