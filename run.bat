@echo off
chcp 65001 >NUL
title 찬양 가사 애플리케이션 실행

echo ========================================================
echo  찬양 가사 애플리케이션 실행
echo ========================================================
echo.

:: 1. Git 설치 확인
git --version >NUL 2>&1
if errorlevel 1 (
    echo [오류] Git이 설치되어 있지 않습니다.
    echo Git을 먼저 설치해주세요: https://git-scm.com/downloads
    echo.
    pause
    exit /b 1
)
echo [OK] Git 설치 확인됨.

:: 2. Python 설치 확인
python --version >NUL 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [OK] Python 설치 확인됨.

:: 3. 업데이트 여부 확인 (선택사항)
if exist ".git" (
    echo.
    echo 최신 코드로 업데이트하시겠습니까?
    echo [주의] 로컬 변경사항은 모두 삭제됩니다.
    echo.
    choice /C YN /M "업데이트를 진행하시겠습니까"
    if errorlevel 2 (
        echo 업데이트를 건너뜁니다.
    ) else (
        echo.
        echo [업데이트 시작] 최신 코드로 동기화합니다...
        git fetch origin main
        git checkout main
        git reset --hard origin/main
        git clean -fd
        echo [완료] 업데이트 완료. 스크립트를 다시 실행합니다...
        echo.
        pause
        start "" "%~f0"
        exit
    )
)

:: 4. 필수 패키지 설치
echo.
echo [진행] Python 라이브러리 설치 중...
pip install -q Flask==2.3.3
pip install -q Flask-SQLAlchemy==3.0.5
pip install -q Werkzeug==2.3.7
echo [OK] 패키지 설치 완료

:: 5. 필수 디렉토리 생성
if not exist "dist" mkdir dist
if not exist "dist\hymn" mkdir dist\hymn
if not exist "dist\ccm" mkdir dist\ccm
if not exist "dist\media" mkdir dist\media

:: 6. 앱 실행
echo.
echo ========================================================
echo  서버를 시작합니다.
echo  브라우저에서 http://127.0.0.1:5001 을 여세요.
echo ========================================================
echo.
echo 앱 종료: 이 창에서 [Ctrl + C] 누르기
echo.

:: 5초 후 브라우저 자동 열기
start /B timeout /t 5 /nobreak >NUL && start http://127.0.0.1:5001

:: Flask 실행
python app.py

echo.
echo 앱이 종료되었습니다.
pause
