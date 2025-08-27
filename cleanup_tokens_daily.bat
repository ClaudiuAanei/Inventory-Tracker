@echo off
setlocal

set "PROJECT_DIR=C:\Users\aanei\Inventory-Tracker"
set "PY=%PROJECT_DIR%\.venv\Scripts\python.exe"
set "SCRIPT=%PROJECT_DIR%\cleanup.py"
set "LOG=%PROJECT_DIR%\cleanup.log"

echo [START %DATE% %TIME%] Running cleanup >> "%LOG%"

if not exist "%PY%"     echo [ERR] Missing venv python: %PY% >> "%LOG%"
if not exist "%SCRIPT%" echo [ERR] Missing script: %SCRIPT% >> "%LOG%"

pushd "%PROJECT_DIR%"
"%PY%" "%SCRIPT%" >> "%LOG%" 2>&1
echo [DONE %DATE% %TIME%] ExitCode=%ERRORLEVEL% >> "%LOG%"
popd

endlocal
