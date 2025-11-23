@echo off
chcp 65001 >nul
title 찬양 가사 프레젠테이션 웹앱 (Auto Update & Run)

echo ========================================================
echo  찬양 가사 프레젠테이션 웹앱 - 업데이트 및 실행 모드
echo ========================================================
echo.

:: 1. Git 설치 확인
git --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Git이 설치되어 있지 않습니다.
    echo Git을 먼저 설치해주세요: https://git-scm.com/downloads
    pause
    exit /b 1
)
echo [OK] Git 설치 확인됨.

:: 2. Git 저장소 확인 및 강제 업데이트 (핵심 로직)
if exist ".git" (
    echo.
    echo [업데이트 시작] 원격 저장소와 동기화를 진행합니다...
    echo --------------------------------------------------------
    
    :: 원격 저장소 정보 갱신
    echo 1/4. 원격 저장소 정보 가져오는 중 (Fetch)...
    git fetch origin main

    :: 메인 브랜치로 전환 (혹시 다른 브랜치에 있을 경우 대비)
    echo 2/4. Main 브랜치로 전환 중...
    git checkout main

    :: 로컬 변경사항 무시하고 원격 내용으로 덮어쓰기
    echo 3/4. 로컬 변경사항 덮어쓰는 중 (Reset --hard)...
    git reset --hard origin/main

    :: 추적되지 않는 파일(새로 만든 파일 등) 삭제
    echo 4/4. 불필요한 파일 정리 중 (Clean)...
    git clean -fd

    if errorlevel 1 (
        echo.
        echo [경고] Git 업데이트 중 오류가 발생했습니다.
        echo 네트워크 상태나 저장소 설정을 확인해주세요.
        echo 기존 버전으로 실행을 계속합니다...
    ) else (
        echo.
        echo [완료] 최신 버전으로 업데이트되었습니다.
        echo --------------------------------------------------------
    )
) else (
    echo.
    echo [알림] 현재 폴더는 Git 저장소가 아닙니다.
    echo 자동 업데이트 기능을 사용할 수 없습니다.
    echo (최초 1회는 git clone으로 다운로드 받아야 합니다)
    echo.
)

:: 3. Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python 설치 확인됨.

:: 4. 필수 패키지 설치 (버전 고정)
echo.
echo [설정] 필요한 Python 라이브러리 확인 및 설치 중...
pip install Flask==2.3.3
pip install Flask-SQLAlchemy==3.0.5
pip install Werkzeug==2.3.7

if errorlevel 1 (
    echo [오류] 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)

:: 5. 데이터 디렉토리 생성 (없을 경우에만)
if not exist "dist" mkdir dist
if not exist "dist\hymn" mkdir dist\hymn
if not exist "dist\ccm" mkdir dist\ccm
if not exist "dist\media" mkdir dist\media

:: 6. 웹앱 실행
echo.
echo ========================================================
echo  모든 준비가 완료되었습니다. 웹앱을 시작합니다.
echo  잠시 후 브라우저가 자동으로 열립니다. (http://127.0.0.1:5001)
echo ========================================================
echo.
echo ※ 종료하려면 이 창에서 [Ctrl + C]를 누르세요.
echo.

:: 백그라운드에서 5초 대기 후 브라우저 실행
start /B timeout /t 5 /nobreak >nul && start http://127.0.0.1:5001

:: Flask 애플리케이션 실행
python app.py

pause