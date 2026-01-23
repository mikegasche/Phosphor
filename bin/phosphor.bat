@echo off
REM ------------------------------------------------------------------------------
REM run_phosphor.bat
REM Windows - Set PYTHONPATH, activate venv, run Phosphor
REM ------------------------------------------------------------------------------

SETLOCAL ENABLEDELAYEDEXPANSION

REM --- 1. Change to project root (one level up from this script) ---
SET "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
FOR %%I IN ("%SCRIPT_DIR%\..") DO SET "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"

REM --- 2. Set PYTHONPATH to include the 'app\' folder ---
SET "PYTHONPATH=%PROJECT_ROOT%\app;%PYTHONPATH%"
echo ==> PYTHONPATH=%PYTHONPATH%

REM --- 3. Activate virtual environment ---
call venv\Scripts\activate.bat

REM --- 4. Force locale for numeric parsing (approximation) ---
REM Windows does not use LC_NUMERIC in the same way; Python can handle it internally if needed
SET LC_NUMERIC=C
SET LANG=C
echo ==> Locale: LC_NUMERIC=%LC_NUMERIC%, LANG=%LANG%

REM --- 5. Run the main Phosphor Python script ---
python app\phosphor.py

ENDLOCAL
pause
