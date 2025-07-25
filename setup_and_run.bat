@echo off
chcp 65001 >nul
echo ============================================
echo 찬양 가사 프레젠테이션 웹앱 설치 및 실행
echo ============================================

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
echo 브라우저에서 http://127.0.0.1:5001 로 접속하세요.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

python app.py

pause