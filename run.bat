@echo off
chcp 65001 >nul
echo ============================================
echo 찬양 가사 프레젠테이션 웹앱 설치 및 실행
echo ============================================

:: Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo Git이 설치되어 있지 않습니다. Git을 먼저 설치해주세요.
    echo Git 공식 웹사이트: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Git이 설치되어 있습니다.

:: Check if this is a git repository
if exist ".git" (
    echo.
    echo Git 저장소에서 최신 코드를 가져오는 중...
    git pull origin main
    if errorlevel 1 (
        echo.
        echo Git pull 중 오류가 발생했습니다. 수동으로 확인해주세요.
        echo 그래도 계속 진행합니다...
        echo.
    ) else (
        echo.
        echo 최신 코드 업데이트가 완료되었습니다.
        echo.
    )
) else (
    echo.
    echo Git 저장소가 아닙니다. 최신 코드 업데이트를 건너뜁니다.
    echo 최신 코드를 사용하려면 다음 명령어로 클론하세요:
    echo git clone https://github.com/qelee7890/lyricDisplay.git
    echo.
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python이 설치되어 있지 않습니다. Python을 먼저 설치해주세요.
    echo Python 공식 웹사이트: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python이 설치되어 있습니다.

:: Install required packages
echo 필요한 Python 패키지를 설치하는 중...
pip install Flask==2.3.3
pip install Flask-SQLAlchemy==3.0.5
pip install Werkzeug==2.3.7

if errorlevel 1 (
    echo 패키지 설치 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo 패키지 설치가 완료되었습니다.
echo.

:: Create dist directory if it doesn't exist
if not exist "dist" mkdir dist
if not exist "dist\hymn" mkdir dist\hymn
if not exist "dist\ccm" mkdir dist\ccm
if not exist "dist\media" mkdir dist\media

echo 필요한 디렉토리를 생성했습니다.
echo.

:: Start the web application
echo 웹앱을 시작하는 중...
echo 5초 후 브라우저가 자동으로 열립니다.
echo.
echo ※ "개발 서버" 경고 메시지는 교회/개인 사용시 무시하셔도 됩니다.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

:: Start browser after 5 seconds in background
start /B timeout /t 5 /nobreak >nul && start http://127.0.0.1:5001

:: Start Flask application (this will block and show logs)
python app.py

pause