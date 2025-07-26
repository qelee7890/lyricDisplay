# 🎵 LyricDisplay - 찬양 가사 프레젠테이션 시스템

교회 예배를 위한 전문적인 찬양 가사 프레젠테이션 웹 애플리케이션입니다. 찬송가와 CCM 가사를 아름답게 표시하고, 미디어 콘텐츠를 포함한 완전한 예배 순서를 관리할 수 있습니다.

## ✨ 주요 기능

### 📋 찬양 순서 관리
- **직관적인 드래그 앤 드롭**: 찬양 순서를 쉽게 변경
- **실시간 검색**: 찬송가 번호 또는 제목으로 빠른 검색
- **섹션 구분**: 여는찬양, 특별찬양 등 목적별 섹션 생성
- **미디어 삽입**: 이미지와 동영상을 예배 순서에 포함

### 🎼 찬송가 지원
- **한글-영문 이중 표시**: 전통적인 찬송가 형식 지원
- **실시간 편집**: 찬송가 제목과 가사 수정 가능
- **자동 절 구분**: 1절, 2절, 후렴 자동 인식
- **새 찬송가 추가**: 커스텀 찬송가 등록

### 🎵 CCM (Contemporary Christian Music)
- **이미지 기반**: 가사 이미지 슬라이드 업로드
- **가사 텍스트**: 직접 텍스트 입력으로 가사 관리
- **유연한 편집**: CCM 제목 및 가사 수정
- **다양한 형식**: JPG, PNG, GIF 등 다중 이미지 형식 지원

### 🖥️ 프레젠테이션 모드
- **풀스크린 지원**: Reveal.js 기반 전문적인 프레젠테이션
- **키보드 제어**: 화살표 키로 슬라이드 이동
- **배경 커스터마이징**: 다양한 배경 이미지 옵션
- **패럴랙스 효과**: 동적 배경 스크롤 효과

### 📱 멀티미디어 지원
- **이미지 표시**: 고해상도 이미지 프레젠테이션
- **동영상 재생**: MP4, AVI, MOV 등 동영상 지원
- **미디어 제어**: 재생/일시정지, 음소거 버튼
- **드래그 앤 드롭**: 직관적인 파일 업로드

## 🛠️ 기술 스택

- **Backend**: Python Flask 2.3.3
- **Database**: SQLite (Flask-SQLAlchemy 3.0.5)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Presentation**: Reveal.js
- **File Upload**: Werkzeug 2.3.7
- **UI Components**: Font Awesome, SortableJS

## 📁 프로젝트 구조

```
lyricDisplay/
├── app.py                 # Flask 메인 애플리케이션
├── run.bat               # Windows 실행 스크립트 (Git Pull 포함)
├── requirements.txt      # Python 패키지 의존성
├── python/
│   ├── functions.py      # 핵심 비즈니스 로직
│   └── main.py          # 보조 스크립트
├── templates/           # Jinja2 템플릿
│   ├── base.html        # 기본 레이아웃
│   ├── index.html       # 메인 페이지
│   ├── new_post.html    # 찬양 순서 작성
│   ├── edit_post.html   # 찬양 순서 편집
│   ├── presentation.html # 프레젠테이션 모드
│   ├── search.html      # 찬양 검색
│   └── ...
├── static/
│   ├── css/style.css    # 커스텀 스타일
│   └── js/script.js     # JavaScript 로직
├── dist/                # 정적 리소스
│   ├── hymn/           # 찬송가 데이터
│   │   ├── hymn.txt    # 찬송가 가사
│   │   └── hymnInfo.csv # 찬송가 정보
│   ├── ccm/            # CCM 데이터
│   ├── media/          # 업로드된 미디어
│   └── wallpaper/      # 배경 이미지
└── instance/
    └── praise.db       # SQLite 데이터베이스
```

## 🚀 빠른 시작

### Windows 사용자 (권장)

1. **저장소 클론**
   ```bash
   git clone https://github.com/qelee7890/lyricDisplay.git
   cd lyricDisplay
   ```

2. **자동 실행**
   ```bash
   run.bat
   ```
   
   이 스크립트는 자동으로 다음 작업을 수행합니다:
   - Git에서 최신 코드 업데이트
   - Python 및 필요한 패키지 설치
   - 웹 애플리케이션 실행

3. **브라우저 접속**
   ```
   http://127.0.0.1:5001
   ```

### 수동 설치 (Mac/Linux)

1. **저장소 클론**
   ```bash
   git clone https://github.com/qelee7890/lyricDisplay.git
   cd lyricDisplay
   ```

2. **Python 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **애플리케이션 실행**
   ```bash
   python app.py
   ```

## 📖 사용 가이드

### 1. 찬양 순서 작성

1. **메인 페이지**에서 "새 찬양 순서 작성" 클릭
2. **제목과 설명** 입력
3. **오른쪽 검색창**에서 찬양 검색
4. **"+" 버튼**으로 찬양을 순서에 추가
5. **드래그 앤 드롭**으로 순서 변경
6. **저장** 클릭

### 2. 미디어 추가

1. 찬양 순서 작성 중 **"미디어 추가"** 클릭
2. **이미지/동영상** 선택
3. **파일 드래그 앤 드롭** 또는 클릭하여 업로드
4. **제목 입력** 후 추가

### 3. 프레젠테이션 실행

1. 찬양 순서 목록에서 **"프레젠테이션"** 버튼 클릭
2. **F11 키**로 풀스크린 모드 진입
3. **화살표 키**로 슬라이드 이동
4. **동영상 제어**: 화면의 제어 버튼 사용

### 4. 찬송가 편집

1. **찬양 검색** 페이지에서 수정할 찬송가 검색
2. **"편집"** 버튼 클릭
3. **제목, 가사** 수정 후 저장
4. 수정 내용이 즉시 검색에 반영됨

## 🔧 고급 기능

### 데이터베이스 관리
- SQLite 데이터베이스가 `instance/praise.db`에 저장됨
- 찬양 순서, 미디어 정보가 자동으로 백업됨

### 파일 관리
- 업로드된 미디어는 `dist/media/` 폴더에 저장
- CCM 이미지는 `dist/ccm/[CCM제목]/` 폴더에 정리
- 찬송가 데이터는 `dist/hymn/` 폴더에서 관리

### 커스터마이징
- `static/css/style.css`에서 스타일 수정
- `dist/wallpaper/`에 배경 이미지 추가 가능
- 템플릿 파일 수정으로 레이아웃 변경

## 🐛 문제 해결

### 일반적인 문제

**Q: 두 번째 미디어 업로드가 안 됩니다.**
A: 최신 버전으로 업데이트하세요. `run.bat` 실행 시 자동으로 업데이트됩니다.

**Q: 찬송가 수정 후 검색에 반영되지 않습니다.**
A: Windows와 macOS 호환성 문제가 해결되었습니다. 최신 버전을 사용하세요.

**Q: 프레젠테이션에서 이미지가 잘립니다.**
A: `data-background-size`가 "contain"으로 설정되어 있어 이미지 전체가 표시됩니다.

### 로그 확인
```bash
# Flask 개발 서버 로그 확인
python app.py
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 교회 및 비영리 목적으로 자유롭게 사용할 수 있습니다.

## 🙏 감사의 말

- **Reveal.js**: 프레젠테이션 프레임워크
- **Bootstrap**: UI 프레임워크
- **Flask Community**: 백엔드 지원
- **모든 기여자들**: 개발과 테스트에 참여해주신 분들

## 📞 지원

문제나 제안사항이 있으시면 [GitHub Issues](https://github.com/qelee7890/lyricDisplay/issues)에 등록해주세요.

---

**LyricDisplay**로 더욱 아름다운 예배를 만들어보세요! 🎵✨