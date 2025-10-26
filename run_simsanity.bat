@echo off
title Simsanity Launcher (Debug Mode)
set "DEBUG_LOG=%~dp0debug_log.txt"
echo.
echo [DEBUG MODE ENABLED]
echo.
@echo on

rem -- Trace start
echo [TRACE] Command echo enabled. >> "%DEBUG_LOG%"
REM ===============================================
setlocal ENABLEDELAYEDEXPANSION
echo [TRACE] setlocal reached. >> "%DEBUG_LOG%"
echo ---- Simsanity Debug Run (%date% %time%) ---- > "%DEBUG_LOG%"

REM --- Default starting port (can be overridden by first arg) ---
set "START_PORT=8080"
set "MAX_PORT=8100"
if not "%~1"=="" set "START_PORT=%~1"

REM --- Determine script and base directory ---
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM --- Detect if running from a Mac shared path or network share ---
echo [TRACE] Checking if running from Mac share or network path... >> "%DEBUG_LOG%"
if /i "%SCRIPT_DIR:~0,5%"=="\\Mac\" (
  echo WARNING: You are running this script from a Mac shared folder path.
  echo.
  echo Running Simsanity from a Mac shared folder can cause major issues with Python networking.
  echo.
  set "TARGET_DIR=%USERPROFILE%\Documents\Simsanity"
  echo Recommended fix: move the project to:
  echo     %TARGET_DIR%
  echo.
  choice /C YN /M "Would you like to copy the Simsanity folder to your local Documents directory now?"
  if errorlevel 2 (
    echo User declined auto-move. Aborting.
    echo [ERROR] Mac shared path detected. User declined move. >> "%DEBUG_LOG%"
    pause
    exit /b 1
  )
  echo Copying project to %TARGET_DIR%...
  xcopy "%~dp0simsanity" "%TARGET_DIR%\simsanity" /E /I /H /Y
  if errorlevel 1 (
    echo ERROR: Failed to copy project files. Please move manually.
    echo [ERROR] Copy operation failed. >> "%DEBUG_LOG%"
    pause
    exit /b 1
  )
  echo Successfully copied project to %TARGET_DIR%.
  echo Launching Simsanity from new location...
  start "" "%TARGET_DIR%\..\run_simsanity.bat"
  exit /b 0
)

REM --- Dynamically locate the simsanity folder anywhere on the system ---
set "SIMSANITY_DIR="
set "USER_HOME=%USERPROFILE%"

rem --- Quick check of known common locations ---
for %%P in ("%~dp0" "%~dp0.." "%USER_HOME%\Documents" "%USER_HOME%\Desktop" "%USER_HOME%\Downloads") do (
    if exist "%%~P\simsanity\core\main.py" (
        set "SIMSANITY_DIR=%%~P\simsanity"
        goto :found_simsanity
    )
)

rem --- PowerShell deep search if not found ---
for /f "usebackq delims=" %%I in (`
    powershell -NoProfile -Command ^
    "Get-ChildItem -Path $env:USERPROFILE -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq 'simsanity' -and (Test-Path (Join-Path $_.FullName 'core\\main.py')) } | Select-Object -First 1 -ExpandProperty FullName"
`) do set "SIMSANITY_DIR=%%I"

if defined SIMSANITY_DIR goto :found_simsanity

echo ERROR: Could not find the "simsanity" folder on this computer.
echo Make sure Simsanity is installed at any location, such as Documents.
echo [ERROR] Simsanity folder not found even after search. >> "%DEBUG_LOG%"
pause
exit /b 1

:found_simsanity
set "MAIN_PATH=%SIMSANITY_DIR%\core\main.py"
echo [TRACE] Found Simsanity folder dynamically at: %SIMSANITY_DIR% >> "%DEBUG_LOG%"
echo [TRACE] MAIN_PATH resolved to: %MAIN_PATH% >> "%DEBUG_LOG%"

echo Detected SIMSANITY_DIR: "%SIMSANITY_DIR%"
if not exist "%SIMSANITY_DIR%" (
  echo ERROR: Simsanity folder not found under %BASE_DIR%
  echo Make sure this .bat is in the same folder as the "simsanity" folder.
  echo [ERROR] Simsanity folder not found. >> "%DEBUG_LOG%"
  pause
  exit /b 1
)

if not exist "%MAIN_PATH%" (
  echo ERROR: main.py not found at: "%MAIN_PATH%"
  echo [ERROR] main.py missing. >> "%DEBUG_LOG%"
  dir /b /s "%SIMSANITY_DIR%\core\main.py"
  pause
  exit /b 1
)

REM --- Auto-select an available port between START_PORT and MAX_PORT ---
set "PORT="
for /L %%p in (%START_PORT%,1,%MAX_PORT%) do (
  netstat -ano | findstr "%%p " >nul 2>&1
  if errorlevel 1 (
    set "PORT=%%p"
    goto :FOUND_PORT
  )
)
echo ERROR: No free ports found between %START_PORT% and %MAX_PORT%.
echo [ERROR] Port scan failed. >> "%DEBUG_LOG%"
pause
exit /b 1

:FOUND_PORT
echo Using available port: %PORT%

REM --- Paths ---
set "VENV_PATH=%SIMSANITY_DIR%\venv"
set "REQUIREMENTS=%SIMSANITY_DIR%\requirements.txt"
set "LOG_DIR=%SIMSANITY_DIR%\support\logs"

REM --- Create venv if missing ---
if not exist "%VENV_PATH%\Scripts\activate.bat" (
  echo Creating virtual environment at %VENV_PATH%...
  py -3 -m venv "%VENV_PATH%"
  if errorlevel 1 (
    echo ERROR: Failed to create venv. Make sure Python 3 is installed and on PATH.
    echo [ERROR] Venv creation failed. >> "%DEBUG_LOG%"
    pause
    exit /b 1
  )
)

REM --- Activate venv ---
echo Using virtual environment: %VENV_PATH%
call "%VENV_PATH%\Scripts\activate.bat"

REM --- Ensure Python is allowed through Windows Firewall ---
echo [TRACE] Checking Windows Firewall permissions for Python... >> "%DEBUG_LOG%"
for /f "delims=" %%A in ('where python') do set "PYTHON_PATH=%%A"
netsh advfirewall firewall show rule name="Allow Simsanity Python" | find "Allow" >nul 2>&1
if errorlevel 1 (
  echo Granting Windows Firewall access for Python executable...
  netsh advfirewall firewall add rule name="Allow Simsanity Python" dir=in action=allow program="%PYTHON_PATH%" enable=yes profile=any
  netsh advfirewall firewall add rule name="Allow Simsanity Python Out" dir=out action=allow program="%PYTHON_PATH%" enable=yes profile=any
  echo [INFO] Firewall rule added for Python at %PYTHON_PATH% >> "%DEBUG_LOG%"
) else (
  echo [TRACE] Firewall rule already exists for Python. >> "%DEBUG_LOG%"
)

REM --- Show Python identity ---
python -V
where python

REM --- Upgrade pip and install build tools ---
echo Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM --- Install from requirements.txt if present, otherwise minimal deps ---
if exist "%REQUIREMENTS%" (
  echo Installing dependencies from requirements.txt...
  python -m pip install -r "%REQUIREMENTS%"
) else (
  echo No requirements.txt found. Installing minimal runtime packages...
  python -m pip install flask colorama tqdm pyyaml
)

REM --- Ensure tqdm is available ---
python -c "import tqdm" >nul 2>&1
if errorlevel 1 (
  echo tqdm not found, installing...
  python -m pip install tqdm
)

REM --- Ensure log dir exists ---
if not exist "%LOG_DIR%" (
  mkdir "%LOG_DIR%"
)

REM --- Launch Simsanity from main entrypoint ---
cd /d "%SIMSANITY_DIR%"
set "LOG_FILE=%LOG_DIR%\simsanity-%PORT%.log"
echo Starting Simsanity from main entrypoint on port %PORT%...
echo Running: python -u "%MAIN_PATH%" --port %PORT%
python -u "%MAIN_PATH%" --port %PORT% > "%LOG_FILE%" 2>&1

set "RC=%ERRORLEVEL%"
echo Server stopped or closed with exit code %RC%.
echo Logs saved to: %LOG_FILE%

if exist "%LOG_FILE%" (
  echo ---- Tail of log ----
  for /f "usebackq delims=" %%L in (`powershell -NoProfile -Command "Get-Content -Tail 40 -Path '%LOG_FILE%'"`) do echo %%L
  echo ---- End tail ----
)

pause
echo [INFO] Finished launcher. >> "%DEBUG_LOG%"
endlocal
