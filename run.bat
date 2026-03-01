@echo off
setlocal enableextensions

chcp 65001 >NUL

if not exist "logs" mkdir "logs"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%i"
set "LOG_FILE=logs\run_%TS%.log"

echo ========================================================
echo  lyricDisplay launcher
echo ========================================================
echo [INFO] Log file: %LOG_FILE%
echo.

call :log "Launcher started"

set "PYTHON="
where py >NUL 2>&1
if not errorlevel 1 set "PYTHON=py -3"
if not defined PYTHON (
    where python >NUL 2>&1
    if not errorlevel 1 set "PYTHON=python"
)

if not defined PYTHON (
    echo [ERROR] Python was not found in PATH.
    call :log "ERROR: Python not found in PATH"
    pause
    exit /b 1
)

echo [OK] Python command: %PYTHON%
call :log "Python command resolved: %PYTHON%"
%PYTHON% --version >> "%LOG_FILE%" 2>&1

where git >NUL 2>&1
if errorlevel 1 (
    echo [ERROR] Git was not found in PATH.
    call :log "ERROR: Git not found in PATH"
    pause
    exit /b 1
)

if not exist ".git" (
    echo [ERROR] This folder is not a git repository ^(.git missing^).
    call :log "ERROR: .git folder missing"
    pause
    exit /b 1
)

echo [INFO] Force syncing to origin/main...
call :log "Running git fetch/checkout/reset/clean"

git fetch origin main >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] git fetch failed.
    call :log "ERROR: git fetch origin main failed"
    pause
    exit /b 1
)

git checkout main >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] git checkout main failed.
    call :log "ERROR: git checkout main failed"
    pause
    exit /b 1
)

git reset --hard origin/main >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] git reset --hard origin/main failed.
    call :log "ERROR: git reset --hard origin/main failed"
    pause
    exit /b 1
)

git clean -fd >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [WARN] git clean -fd failed. Continuing.
    call :log "WARN: git clean -fd failed"
)

echo [OK] Repository sync complete.
call :log "Repository synced to origin/main"

echo [INFO] Installing dependencies...
call :log "Installing dependencies with requirements.txt"
%PYTHON% -m pip install -q -r requirements.txt >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [WARN] requirements install failed. Trying fallback package list...
    call :log "WARN: requirements install failed; trying fallback list"
    %PYTHON% -m pip install -q Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Werkzeug==2.3.7 >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo [ERROR] package installation failed.
        call :log "ERROR: fallback package install failed"
        pause
        exit /b 1
    )
)

echo [OK] Dependencies are ready.
call :log "Dependency installation completed"

if not exist "dist" mkdir "dist"
if not exist "dist\hymn" mkdir "dist\hymn"
if not exist "dist\ccm" mkdir "dist\ccm"
if not exist "dist\media" mkdir "dist\media"
call :log "Ensured dist directories exist"

echo.
echo ========================================================
echo  Starting server at http://127.0.0.1:5001
echo ========================================================
echo Press Ctrl + C in this window to stop.
echo.

start "" /B powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5001'"
call :log "Browser opener scheduled"

call :log "Starting app.py"
%PYTHON% app.py >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo [ERROR] Application stopped with exit code %EXIT_CODE%.
    call :log "ERROR: app.py exited with code %EXIT_CODE%"
) else (
    echo [INFO] Application exited normally.
    call :log "app.py exited normally"
)

echo [INFO] Detailed logs saved to: %LOG_FILE%
pause
exit /b %EXIT_CODE%

:log
>> "%LOG_FILE%" echo [%date% %time%] %~1
exit /b 0
