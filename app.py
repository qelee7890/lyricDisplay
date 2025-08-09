from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))
from functions import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///praise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'wmv', 'webm'}

db = SQLAlchemy(app)

# 가사 형식 변환 함수
def convert_lyrics_to_original_format(lyrics_text):
    """
    편집된 가사 텍스트를 원본 hymn.txt 형식으로 변환
    한글-영문 교대 구조를 유지하면서 변환
    """
    lines = lyrics_text.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 절 제목 감지 (1절, 2절, 후렴 등)
        if line.endswith('절') or line == '후렴':
            if line.endswith('절'):
                # "1절" -> "1."
                verse_num = line[:-1]
                formatted_lines.append(verse_num + ".")
            else:
                # "후렴" -> "[후렴]"
                formatted_lines.append("[후렴]")
        else:
            # 일반 가사 줄 - 그대로 유지
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

# 데이터베이스 모델
class PraisePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    songs = db.relationship('Song', backref='praise_post', lazy=True, cascade='all, delete-orphan')
    
    # 프레젠테이션 설정
    background_image = db.Column(db.String(500))  # 전체 배경 이미지
    parallax_image = db.Column(db.String(500))  # 패럴랙스 배경 이미지

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    song_type = db.Column(db.String(50), nullable=False)  # 'hymn', 'ccm', 'section', 'media'
    hymn_number = db.Column(db.String(10))  # 찬송가 번호
    lyrics = db.Column(db.Text)  # 가사
    order = db.Column(db.Integer, nullable=False)
    praise_post_id = db.Column(db.Integer, db.ForeignKey('praise_post.id'), nullable=False)
    
    # 추가 필드들
    section_title = db.Column(db.String(200))  # 섹션 제목 (예: 찬양순서1)
    media_type = db.Column(db.String(50))  # 'image', 'video'
    media_url = db.Column(db.String(500))  # 미디어 파일 경로
    background_image = db.Column(db.String(500))  # 배경 이미지

class CCMImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_ccm_images(song_title):
    """CCM 이미지 목록을 가져오는 함수 (dist/ccm 폴더에서)"""
    import glob
    import unicodedata
    
    # 유니코드 정규화 문제를 해결하기 위해 glob으로 찾기
    pattern = os.path.join('dist', 'ccm', '*', '*.jpg')
    images = []
    
    for image_path in glob.glob(pattern):
        folder_path = os.path.dirname(image_path)
        folder_name = os.path.basename(folder_path)
        normalized_folder_name = unicodedata.normalize('NFC', folder_name)
        
        if normalized_folder_name == song_title:
            filename = os.path.basename(image_path)
            
            # 간단한 객체를 만들어서 기존 코드와 호환성 유지
            class ImageObj:
                def __init__(self, filename, order):
                    self.filename = filename
                    self.order = order
            
            # 파일명에서 순서 추출 (예: 1.jpg -> 1)
            try:
                order = int(filename.split('.')[0])
            except ValueError:
                order = 999  # 순서를 알 수 없는 경우 맨 뒤로
            
            images.append(ImageObj(filename, order))
    
    # PNG, JPEG, GIF도 체크
    for ext in ['*.png', '*.jpeg', '*.gif']:
        pattern = os.path.join('dist', 'ccm', '*', ext)
        for image_path in glob.glob(pattern):
            folder_path = os.path.dirname(image_path)
            folder_name = os.path.basename(folder_path)
            normalized_folder_name = unicodedata.normalize('NFC', folder_name)
            
            if normalized_folder_name == song_title:
                filename = os.path.basename(image_path)
                
                # 이미 추가된 파일인지 확인
                if not any(img.filename == filename for img in images):
                    class ImageObj:
                        def __init__(self, filename, order):
                            self.filename = filename
                            self.order = order
                    
                    try:
                        order = int(filename.split('.')[0])
                    except ValueError:
                        order = 999
                    
                    images.append(ImageObj(filename, order))
    
    # 순서대로 정렬
    images.sort(key=lambda x: x.order)
    return images

def get_ccm_lyrics(song_title):
    """CCM 가사를 가져오는 함수 (dist/ccm 폴더에서 lyrics.txt 파일)"""
    import glob
    import unicodedata
    
    # 유니코드 정규화를 위해 glob으로 찾기
    pattern = os.path.join('dist', 'ccm', '*', 'lyrics.txt')
    
    for lyrics_path in glob.glob(pattern):
        folder_path = os.path.dirname(lyrics_path)
        folder_name = os.path.basename(folder_path)
        normalized_folder_name = unicodedata.normalize('NFC', folder_name)
        
        if normalized_folder_name == song_title:
            try:
                with open(lyrics_path, 'r', encoding='utf-8') as f:
                    lyrics = f.read().strip()
                    return lyrics if lyrics else None
            except Exception:
                pass
    
    return None

def is_korean_line(line):
    """라인이 한글인지 영문인지 판단하는 함수 - 찬송가와 동일한 로직 사용"""
    if not line.strip():
        return False
    
    # 찬송가와 동일한 Unicode 기반 한글 판단 로직 사용
    return isUnicode(line[0], "가")

def parse_ccm_lyrics(lyrics):
    """CCM 가사를 파싱하는 함수 - 한글-영문 쌍별로 개별 슬라이드 생성"""
    import re
    
    if not lyrics:
        return {}
    
    # 절 제목을 기준으로 분할 (정규식 사용)
    # "숫자절" 또는 "후렴"으로 시작하는 라인을 찾음
    verse_pattern = r'\n(?=\d+절|\b후렴\b)'
    sections = re.split(verse_pattern, lyrics.strip())
    
    # 먼저 총 절 수 계산 (숫자절만 카운트, 후렴 제외)
    verse_numbers = set()
    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines = section.split('\n')
        if not lines:
            continue
        first_line = lines[0].strip()
        if first_line.endswith('절') and first_line[:-1].isdigit():
            verse_numbers.add(int(first_line[:-1]))
    
    total_verses = len(verse_numbers)
    
    parsed_verses = {}
    slide_index = 0
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        lines = section.split('\n')
        if not lines:
            continue
            
        # 첫 줄에서 절 번호 추출
        first_line = lines[0].strip()
        if first_line.endswith('절') and first_line[:-1].isdigit():
            verse_key = first_line[:-1]
            content_lines = lines[1:]
        elif '후렴' in first_line:
            verse_key = '후렴'
            content_lines = lines[1:]
        else:
            # 절 번호가 없으면 건너뜀
            continue
        
        # 빈 줄 제거하고 <br/> 태그 추가 (찬송가와 동일한 형식)
        formatted_lines = []
        for line in content_lines:
            if line.strip():
                formatted_lines.append(line.strip() + '<br/>')
        
        if formatted_lines:
            # 찬송가와 동일한 한글-영문 쌍 파싱 로직 적용
            kor_parts, eng_parts = parse_verse_content(formatted_lines)
            
            # 각 한글-영문 쌍을 개별 슬라이드로 생성
            max_pairs = max(len(kor_parts), len(eng_parts))
            
            for i in range(max_pairs):
                slide_key = f"{verse_key}_{slide_index}"
                slide_text = []
                
                # 한글 부분 추가
                if i < len(kor_parts) and kor_parts[i].strip():
                    kor_lines = kor_parts[i].rstrip('<br/>').split('<br/>')
                    slide_text.extend(kor_lines)
                
                # 구분자 추가
                slide_text.append('-')
                
                # 영문 부분 추가
                if i < len(eng_parts) and eng_parts[i].strip():
                    eng_lines = eng_parts[i].rstrip('<br/>').split('<br/>')
                    slide_text.extend(eng_lines)
                
                parsed_verses[slide_key] = {
                    'text': slide_text,
                    'verse_number': verse_key,
                    'slide_index': i + 1,
                    'total_slides_in_verse': max_pairs,
                    'total_verses': total_verses
                }
                
                slide_index += 1
    
    return parsed_verses

def has_ccm_lyrics(song_title):
    """CCM이 가사 파일을 가지고 있는지 확인하는 함수"""
    return get_ccm_lyrics(song_title) is not None

def ccm_exists(song_title):
    """CCM이 이미 존재하는지 확인하는 함수 (이미지 또는 가사)"""
    import glob
    import unicodedata
    
    # 이미지 파일 찾기
    for ext in ['*.jpg', '*.png', '*.jpeg', '*.gif']:
        pattern = os.path.join('dist', 'ccm', '*', ext)
        for file_path in glob.glob(pattern):
            folder_path = os.path.dirname(file_path)
            folder_name = os.path.basename(folder_path)
            normalized_folder_name = unicodedata.normalize('NFC', folder_name)
            if normalized_folder_name == song_title:
                return True
    
    # 가사 파일 찾기
    pattern = os.path.join('dist', 'ccm', '*', 'lyrics.txt')
    for lyrics_path in glob.glob(pattern):
        folder_path = os.path.dirname(lyrics_path)
        folder_name = os.path.basename(folder_path)
        normalized_folder_name = unicodedata.normalize('NFC', folder_name)
        if normalized_folder_name == song_title:
            return True
    
    return False

def hymn_exists(hymn_number):
    """find송가 번호가 이미 존재하는지 확인하는 함수"""
    try:
        filename = openTextFile("dist/hymn", "hymnInfo.csv", "r")
        infos = csv.reader(filename)
        for info in infos:
            if info[0] == str(hymn_number):
                filename.close()
                return True
        filename.close()
    except Exception:
        pass
    return False

def get_ccm_list_from_dist():
    """dist/ccm 폴더에서 CCM 목록을 가져오는 함수 (이미지 또는 가사 파일 기준)"""
    import glob
    import unicodedata
    
    # glob을 사용하여 모든 이미지가 있는 폴더 찾기
    ccm_folders = []
    pattern = os.path.join('dist', 'ccm', '*', '*.jpg')
    
    for image_path in glob.glob(pattern):
        folder_path = os.path.dirname(image_path)
        folder_name = os.path.basename(folder_path)
        # 유니코드 정규화 (NFD -> NFC)
        normalized_name = unicodedata.normalize('NFC', folder_name)
        if normalized_name not in ccm_folders:
            ccm_folders.append(normalized_name)
    
    # PNG, JPEG, GIF도 체크
    for ext in ['*.png', '*.jpeg', '*.gif']:
        pattern = os.path.join('dist', 'ccm', '*', ext)
        for image_path in glob.glob(pattern):
            folder_path = os.path.dirname(image_path)
            folder_name = os.path.basename(folder_path)
            # 유니코드 정규화 (NFD -> NFC)
            normalized_name = unicodedata.normalize('NFC', folder_name)
            if normalized_name not in ccm_folders:
                ccm_folders.append(normalized_name)
    
    # lyrics.txt 파일도 체크
    pattern = os.path.join('dist', 'ccm', '*', 'lyrics.txt')
    for lyrics_path in glob.glob(pattern):
        folder_path = os.path.dirname(lyrics_path)
        folder_name = os.path.basename(folder_path)
        # 유니코드 정규화 (NFD -> NFC)
        normalized_name = unicodedata.normalize('NFC', folder_name)
        if normalized_name not in ccm_folders:
            ccm_folders.append(normalized_name)
    
    return sorted(ccm_folders)

@app.route('/dist/<path:filename>')
def serve_dist_file(filename):
    """dist 폴더의 파일들 서빙"""
    return send_from_directory('dist', filename)

@app.route('/dist/ccm/<path:song_title>/<filename>')
def serve_ccm_image(song_title, filename):
    """CCM 이미지 서빙 (dist/ccm 폴더에서)"""
    return send_from_directory(os.path.join('dist', 'ccm', song_title), filename)

def get_hymn_info(number):
    """찬송가 정보를 가져오는 함수"""
    try:
        filename = openTextFile("dist/hymn", "hymnInfo.csv", "r")
        infos = csv.reader(filename)
        for info in infos:
            if info[0] == str(number):
                return {
                    "hymnNumber": info[0],
                    "newHymnNumber": info[1],
                    "hymnTitle": info[2]
                }
        filename.close()
    except Exception:
        pass
    return None

@app.route('/')
def index():
    posts = PraisePost.query.order_by(PraisePost.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        background_image = request.form.get('background_image', '')
        parallax_image = request.form.get('parallax_image', '')
        
        post = PraisePost(
            title=title, 
            content=content,
            background_image=background_image,
            parallax_image=parallax_image
        )
        db.session.add(post)
        db.session.commit()
        
        # 찬양 정보 처리
        songs_json = request.form.get('songs', '[]')
        if not songs_json.strip():
            songs_json = '[]'
        
        try:
            songs_data = json.loads(songs_json)
        except json.JSONDecodeError:
            flash('찬양 데이터 형식이 올바르지 않습니다.', 'error')
            return redirect(url_for('new_post'))
        
        for i, song_data in enumerate(songs_data):
            song = Song(
                title=song_data['title'],
                song_type=song_data['type'],
                hymn_number=song_data.get('hymn_number') if song_data.get('hymn_number') else None,
                lyrics=song_data.get('lyrics') if song_data.get('lyrics') else None,
                section_title=song_data.get('section_title') if song_data.get('section_title') else None,
                media_type=song_data.get('media_type') if song_data.get('media_type') else None,
                media_url=song_data.get('media_url') if song_data.get('media_url') else None,
                background_image=song_data.get('background_image') if song_data.get('background_image') else None,
                order=i,
                praise_post_id=post.id
            )
            db.session.add(song)
        
        db.session.commit()
        flash('찬양 순서가 성공적으로 저장되었습니다!', 'success')
        return redirect(url_for('index'))
    
    return render_template('new_post.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = PraisePost.query.get_or_404(post_id)
    return render_template('view_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = PraisePost.query.get_or_404(post_id)
    
    try:
        # 관련된 찬양들도 함께 삭제 (cascade 설정으로 자동 삭제됨)
        db.session.delete(post)
        db.session.commit()
        flash(f'"{post.title}" 찬양 순서가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('삭제 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
    
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/duplicate', methods=['POST'])
def duplicate_post(post_id):
    original_post = PraisePost.query.get_or_404(post_id)
    
    try:
        # 새로운 찬양 순서 생성 (제목에 "복사본" 추가)
        new_post = PraisePost(
            title=f"{original_post.title} - 복사본",
            content=original_post.content,
            background_image=original_post.background_image,
            parallax_image=original_post.parallax_image,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_post)
        db.session.flush()  # ID를 얻기 위해 flush
        
        # 원본의 모든 찬양들을 복제
        for original_song in original_post.songs:
            new_song = Song(
                song_type=original_song.song_type,
                title=original_song.title,
                hymn_number=original_song.hymn_number,
                lyrics=original_song.lyrics,
                section_title=original_song.section_title,
                media_type=original_song.media_type,
                media_url=original_song.media_url,
                background_image=original_song.background_image,
                order=original_song.order,
                praise_post_id=new_post.id
            )
            db.session.add(new_song)
        
        db.session.commit()
        flash(f'"{original_post.title}" 찬양 순서가 성공적으로 복제되었습니다.', 'success')
        
        # 복제된 찬양 순서의 편집 페이지로 이동
        return redirect(url_for('edit_post', post_id=new_post.id))
        
    except Exception as e:
        db.session.rollback()
        flash('복제 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
        return redirect(url_for('index'))

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = PraisePost.query.get_or_404(post_id)
    # 찬양들을 순서대로 정렬
    post.songs = sorted(post.songs, key=lambda x: x.order)
    
    if request.method == 'POST':
        # 기본 정보 업데이트
        post.title = request.form['title']
        post.content = request.form['content']
        post.background_image = request.form.get('background_image', '')
        post.parallax_image = request.form.get('parallax_image', '')
        
        # 기존 찬양 삭제
        for song in post.songs:
            db.session.delete(song)
        
        # 새로운 찬양 정보 처리
        songs_json = request.form.get('songs', '[]')
        if not songs_json.strip():
            songs_json = '[]'
        
        
        try:
            songs_data = json.loads(songs_json)
            
            # 데이터 검증
            if not isinstance(songs_data, list):
                flash('찬양 데이터 형식이 올바르지 않습니다.', 'error')
                return redirect(url_for('edit_post', post_id=post.id))
            
            # 각 song 객체 검증
            validated_songs = []
            for i, song_data in enumerate(songs_data):
                if not isinstance(song_data, dict):
                    continue
                
                if not song_data.get('title') or not song_data.get('type'):
                    continue
                
                # 문자열 필드 길이 제한
                if len(str(song_data.get('title', ''))) > 200:
                    continue
                
                validated_songs.append(song_data)
            
            songs_data = validated_songs
            
        except json.JSONDecodeError:
            flash('찬양 데이터 형식이 올바르지 않습니다.', 'error')
            return redirect(url_for('edit_post', post_id=post.id))
        except Exception:
            flash('찬양 데이터 처리 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('edit_post', post_id=post.id))
        
        for i, song_data in enumerate(songs_data):
            song = Song(
                title=song_data['title'],
                song_type=song_data['type'],
                hymn_number=song_data.get('hymn_number') if song_data.get('hymn_number') else None,
                lyrics=song_data.get('lyrics') if song_data.get('lyrics') else None,
                section_title=song_data.get('section_title') if song_data.get('section_title') else None,
                media_type=song_data.get('media_type') if song_data.get('media_type') else None,
                media_url=song_data.get('media_url') if song_data.get('media_url') else None,
                background_image=song_data.get('background_image') if song_data.get('background_image') else None,
                order=i,
                praise_post_id=post.id
            )
            db.session.add(song)
        
        db.session.commit()
        flash('찬양 순서가 성공적으로 수정되었습니다!', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    
    
    # 안전한 JSON 데이터 생성
    songs_data = []
    for song in post.songs:
        song_dict = {
            'title': song.title,
            'type': song.song_type,
            'hymn_number': song.hymn_number,
            'section_title': song.section_title,
            'media_type': song.media_type,
            'media_url': song.media_url,
            'background_image': song.background_image,
            'lyrics': song.lyrics or ''
        }
        songs_data.append(song_dict)
    
    # JSON으로 안전하게 직렬화
    songs_json = json.dumps(songs_data, ensure_ascii=False)
    
    return render_template('edit_post.html', post=post, songs_json=songs_json)

@app.route('/post/<int:post_id>/presentation')
def presentation(post_id):
    post = PraisePost.query.get_or_404(post_id)
    
    # 찬송가 가사 처리 함수
    def get_hymn_lyrics(hymn_number):
        try:
            hymnfile = openTextFile("dist/hymn", "hymn.txt", "r")
            korLyric, engLyric = classifyLyric(str(hymn_number), hymnfile)
            hymnfile.close()
            
            lyrics = ""
            
            # 후렴 여부 확인
            has_chorus = "후렴" in korLyric
            
            # 절 번호만 추출 (후렴 제외)
            verse_keys = [key for key in sorted(korLyric.keys()) if key != "후렴"]
            
            def add_verse_content(verse_key):
                """절 또는 후렴 내용을 추가하는 함수 - 한글-영문 쌍별로 슬라이드 분리"""
                nonlocal lyrics
                
                # 한글-영문 쌍으로 처리
                korean_parts = korLyric[verse_key] if verse_key in korLyric else []
                english_parts = engLyric[verse_key] if verse_key in engLyric else []
                
                max_parts = max(len(korean_parts), len(english_parts))
                for i in range(max_parts):
                    # 각 쌍마다 절 제목과 함께 새로운 슬라이드 생성
                    if verse_key == "후렴":
                        lyrics += "후렴\n"
                    else:
                        lyrics += f"{verse_key}절\n"
                    
                    # 한글 부분 추가
                    if i < len(korean_parts):
                        lyrics += korean_parts[i].replace("<br/>", "\n")
                    
                    # 한글과 영문 사이에 구분선 추가
                    if i < len(korean_parts) and i < len(english_parts):
                        lyrics += "\n-\n"
                    
                    # 영문 부분 추가 (같은 인덱스)
                    if i < len(english_parts):
                        lyrics += english_parts[i].replace("<br/>", "\n")
                    
                    lyrics += "\n\n\n\n"  # 각 쌍 사이의 구분 (4개의 줄바꿈으로 새 슬라이드)
            
            # 각 절을 처리하고, 후렴이 있으면 절 뒤에 후렴 추가
            for verse_key in verse_keys:
                # 절 추가
                add_verse_content(verse_key)
                
                # 후렴이 있으면 절 뒤에 후렴 추가
                if has_chorus:
                    add_verse_content("후렴")
            
            return lyrics.strip()
        except:
            return ""
    
    # 찬송가 가사 업데이트
    for song in post.songs:
        if song.song_type == 'hymn' and not song.lyrics:
            song.lyrics = get_hymn_lyrics(song.hymn_number)
    
    return render_template('presentation.html', post=post, get_ccm_images=get_ccm_images, get_ccm_lyrics=get_ccm_lyrics, has_ccm_lyrics=has_ccm_lyrics, parse_ccm_lyrics=parse_ccm_lyrics, get_hymn_info=get_hymn_info)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if request.headers.get('Accept') == 'application/json':
        # JSON API 응답
        if query:
            # 찬송가 검색
            hymn_results = []
            try:
                filename = openTextFile("dist/hymn", "hymnInfo.csv", "r")
                infos = csv.reader(filename)
                for info in infos:
                    if query in info[0] or query in info[2]:  # 번호나 제목으로 검색
                        hymn_results.append({
                            'number': info[0],
                            'title': info[2],
                            'new_number': info[1]
                        })
                filename.close()
            except Exception:
                pass
            
            # CCM 검색 - dist/ccm 폴더에서 검색
            ccm_list = get_ccm_list_from_dist()
            ccm_data = []
            for ccm_title in ccm_list:
                if query.lower() in ccm_title.lower():
                    # 가사 기반인지 이미지 기반인지 확인
                    if has_ccm_lyrics(ccm_title):
                        ccm_data.append({
                            'song_title': ccm_title, 
                            'image_count': '가사'
                        })
                    else:
                        images = get_ccm_images(ccm_title)
                        ccm_data.append({
                            'song_title': ccm_title, 
                            'image_count': f'{len(images)}장' if len(images) > 0 else '0장'
                        })
                if len(ccm_data) >= 10:  # 최대 10개만 반환
                    break
            
            return jsonify({
                'hymn_results': hymn_results[:10],
                'ccm_results': ccm_data[:10]
            })
        else:
            return jsonify({'hymn_results': [], 'ccm_results': []})
    
    # HTML 페이지 응답
    if query:
        # 찬송가 검색
        hymn_results = []
        try:
            filename = openTextFile("dist/hymn", "hymnInfo.csv", "r")
            infos = csv.reader(filename)
            for info in infos:
                if query in info[0] or query in info[2]:  # 번호나 제목으로 검색
                    hymn_results.append({
                        'number': info[0],
                        'title': info[2],
                        'new_number': info[1]
                    })
            filename.close()
        except:
            pass
        
        # CCM 검색 - dist/ccm 폴더에서 검색
        ccm_list = get_ccm_list_from_dist()
        ccm_results = []
        for ccm_title in ccm_list:
            if query.lower() in ccm_title.lower():
                # 가사 기반인지 이미지 기반인지 확인
                if has_ccm_lyrics(ccm_title):
                    ccm_results.append({
                        'song_title': ccm_title, 
                        'image_count': '가사'
                    })
                else:
                    images = get_ccm_images(ccm_title)
                    ccm_results.append({
                        'song_title': ccm_title, 
                        'image_count': f'{len(images)}장' if len(images) > 0 else '0장'
                    })
            if len(ccm_results) >= 10:  # 최대 10개만 반환
                break
        
        return render_template('search.html', 
                             query=query, 
                             hymn_results=hymn_results[:10], 
                             ccm_results=ccm_results[:10],
                             has_ccm_lyrics=has_ccm_lyrics)
    
    return render_template('search.html', query='', has_ccm_lyrics=has_ccm_lyrics)

@app.route('/upload_ccm', methods=['GET', 'POST'])
def upload_ccm():
    if request.method == 'POST':
        upload_type = request.form.get('upload_type', 'image')
        song_title = request.form['song_title']
        
        # 중복 확인
        if ccm_exists(song_title):
            flash(f'CCM "{song_title}"이(가) 이미 존재합니다. 다른 제목을 사용하세요.', 'error')
            return redirect(url_for('upload_ccm'))
        
        # dist/ccm 폴더에 생성
        upload_dir = os.path.join('dist', 'ccm', song_title)
        os.makedirs(upload_dir, exist_ok=True)
        
        if upload_type == 'image':
            # 이미지 업로드 처리
            files = request.files.getlist('images')
            
            for i, file in enumerate(files):
                if file and allowed_file(file.filename):
                    # 원본 파일 확장자 보존
                    file_ext = os.path.splitext(file.filename)[1]
                    filename = secure_filename(f"{i+1}{file_ext}")
                    file.save(os.path.join(upload_dir, filename))
                    
                    # 데이터베이스에 저장
                    ccm_image = CCMImage(
                        song_title=song_title,
                        filename=filename,
                        order=i+1
                    )
                    db.session.add(ccm_image)
            
            db.session.commit()
            flash('CCM 이미지가 성공적으로 업로드되었습니다!', 'success')
            
        elif upload_type == 'lyrics':
            # 가사 업로드 처리
            lyrics = request.form['lyrics']
            
            # 가사를 lyrics.txt 파일로 저장
            lyrics_file_path = os.path.join(upload_dir, 'lyrics.txt')
            with open(lyrics_file_path, 'w', encoding='utf-8') as f:
                f.write(lyrics)
            
            flash('CCM 가사가 성공적으로 저장되었습니다!', 'success')
        
        return redirect(url_for('upload_ccm'))
    
    return render_template('upload_ccm.html')

@app.route('/upload_hymn', methods=['GET', 'POST'])
def upload_hymn():
    if request.method == 'POST':
        hymn_title = request.form['hymn_title']
        hymn_number = request.form.get('hymn_number', '')
        new_hymn_number = request.form.get('new_hymn_number', '')
        lyrics = request.form['lyrics']
        
        if not hymn_title or not lyrics:
            flash('찬송가 제목과 가사를 입력하세요.', 'error')
            return redirect(url_for('upload_hymn'))
        
        # 중복 확인 (번호가 있는 경우만)
        if hymn_number and hymn_exists(hymn_number):
            flash(f'찬송가 {hymn_number}장이 이미 존재합니다. 다른 번호를 사용하세요.', 'error')
            return redirect(url_for('upload_hymn'))
        
        try:
            # hymn.txt 파일에 새 찬송가 추가
            hymn_file_path = os.path.join('dist', 'hymn', 'hymn.txt')
            
            # 기존 파일 읽기
            with open(hymn_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 새 찬송가 형식으로 추가
            new_hymn_content = f"\n<{hymn_number}장>\n{lyrics}\n"
            
            # 파일에 추가
            with open(hymn_file_path, 'a', encoding='utf-8') as f:
                f.write(new_hymn_content)
            
            # hymnInfo.csv에도 정보 추가 (번호가 있는 경우만)
            if hymn_number:
                hymn_info_path = os.path.join('dist', 'hymn', 'hymnInfo.csv')
                with open(hymn_info_path, 'a', encoding='utf-8', newline='') as f:
                    import csv
                    writer = csv.writer(f)
                    writer.writerow([hymn_number, new_hymn_number or '', hymn_title])
            
            flash('찬송가가 성공적으로 업로드되었습니다!', 'success')
            return redirect(url_for('upload_hymn'))
            
        except Exception as e:
            flash(f'찬송가 업로드 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('upload_hymn'))
    
    return render_template('upload_hymn.html')


@app.route('/edit_hymn/<int:hymn_number>', methods=['GET', 'POST'])
def edit_hymn(hymn_number):
    if request.method == 'POST':
        # 찬송가 정보 수정 로직
        new_title = request.form['title']
        new_lyrics = request.form['lyrics']
        new_number = request.form.get('new_number', '')
        
        
        try:
            # hymnInfo.csv 파일 업데이트
            import csv
            import shutil
            from functions import findTargetDirPath
            
            # CSV 파일 경로를 일관되게 처리
            csv_path = os.path.normpath(os.path.join(findTargetDirPath("dist/hymn"), "hymnInfo.csv"))
            
            # 백업 파일 생성
            backup_path = csv_path + '.backup'
            if os.path.exists(csv_path):
                shutil.copy2(csv_path, backup_path)
            
            # 기존 CSV 파일 읽기
            csv_data = []
            updated = False
            
            try:
                with open(csv_path, 'r', encoding='utf-8') as csv_file:
                    reader = csv.reader(csv_file)
                    for row in reader:
                        if len(row) >= 3 and row[0] == str(hymn_number):
                            # 해당 찬송가 정보 업데이트
                            csv_data.append([row[0], new_number, new_title] + row[3:])  # 나머지 컬럼 보존
                            updated = True
                        else:
                            csv_data.append(row)
                            
                if not updated:
                    raise ValueError(f"찬송가 {hymn_number}장을 찾을 수 없습니다.")
                    
            except Exception as e:
                flash(f'CSV 파일 읽기 오류: {str(e)}', 'error')
                return redirect(url_for('search'))
            
            # 새로운 내용으로 CSV 파일 쓰기
            try:
                with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerows(csv_data)
                    
                # 백업 파일 삭제 (성공적으로 저장된 경우)
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    
            except Exception as e:
                # 오류 발생 시 백업에서 복원
                if os.path.exists(backup_path):
                    shutil.move(backup_path, csv_path)
                flash(f'CSV 파일 저장 오류: {str(e)}', 'error')
                return redirect(url_for('search'))
            
            # hymn.txt 파일 처리
            hymn_path = os.path.normpath(os.path.join(findTargetDirPath("dist/hymn"), "hymn.txt"))
            hymn_backup_path = hymn_path + '.backup'
            
            try:
                # hymn.txt 파일 백업
                if os.path.exists(hymn_path):
                    shutil.copy2(hymn_path, hymn_backup_path)
                
                # hymn.txt 파일 읽기
                with open(hymn_path, 'r', encoding='utf-8') as hymnfile:
                    content = hymnfile.read()
                
                # 기존 찬송가 내용 찾기
                start_marker = f"<{hymn_number}장>"
                start_pos = content.find(start_marker)
                
                if start_pos == -1:
                    # 백업 파일 삭제
                    if os.path.exists(hymn_backup_path):
                        os.remove(hymn_backup_path)
                    flash('hymn.txt에서 찬송가를 찾을 수 없습니다.', 'error')
                    return redirect(url_for('search'))
                
                # 가사 시작 위치 (마커 다음 줄부터)
                lyrics_start = content.find('\n', start_pos) + 1
                if lyrics_start == 0:  # 줄바꿈을 찾지 못한 경우
                    lyrics_start = start_pos + len(start_marker)
                
                # 다음 찬송가 마커 찾기 - 더 넓은 범위로 검색
                end_pos = len(content)  # 기본값: 파일 끝
                
                # 다음 찬송가들을 찾기 위해 더 넓은 범위 검색
                for i in range(hymn_number + 1, hymn_number + 50):  # 최대 50개 찬송가까지 확인
                    next_marker = f"<{i}장>"
                    next_pos = content.find(next_marker, lyrics_start)
                    if next_pos != -1:
                        end_pos = next_pos
                        break
                
                # 새로운 가사를 원본 형식으로 변환
                formatted_lyrics = convert_lyrics_to_original_format(new_lyrics)
                
                # 새로운 가사로 교체 (마커는 유지하고 가사 부분만 교체)
                new_content = content[:lyrics_start] + formatted_lyrics + "\n" + content[end_pos:]
                
                # 파일에 저장
                with open(hymn_path, 'w', encoding='utf-8') as hymnfile:
                    hymnfile.write(new_content)
                
                # 백업 파일 삭제 (성공적으로 저장된 경우)
                if os.path.exists(hymn_backup_path):
                    os.remove(hymn_backup_path)
                    
            except Exception as e:
                # 오류 발생 시 백업에서 복원
                if os.path.exists(hymn_backup_path):
                    shutil.move(hymn_backup_path, hymn_path)
                flash(f'hymn.txt 파일 처리 오류: {str(e)}', 'error')
                return redirect(url_for('search'))
            
            flash('찬송가 정보가 성공적으로 수정되었습니다!', 'success')
        except Exception as e:
            flash(f'수정 중 오류가 발생했습니다: {str(e)}', 'error')
        
        return redirect(url_for('search'))
    
    # 기존 정보 가져오기
    hymn_info = get_hymn_info(hymn_number)
    
    # 기존 가사 가져오기
    lyrics = ""
    try:
        from functions import findTargetDirPath, classifyLyric
        hymn_path = os.path.normpath(os.path.join(findTargetDirPath("dist/hymn"), "hymn.txt"))
        
        with open(hymn_path, 'r', encoding='utf-8') as hymnfile:
            korLyric, engLyric = classifyLyric(str(hymn_number), hymnfile)
        
        # 가사를 텍스트로 변환
        # 숫자 키들을 먼저 정렬하고, 후렴은 맨 뒤에
        numeric_keys = []
        has_chorus = False
        
        for key in korLyric.keys():
            if key == "후렴":
                has_chorus = True
            else:
                try:
                    numeric_keys.append(int(key))
                except:
                    numeric_keys.append(key)
        
        # 숫자 키들을 정렬
        numeric_keys.sort()
        
        # 숫자 키들 먼저 처리 - 한글-영문 쌍으로 교대 표시
        for key in numeric_keys:
            key_str = str(key)
            if key_str in korLyric:
                lyrics += f"{key_str}절\n"
                
                # 각 부분을 한글-영문 쌍으로 처리
                korean_parts = korLyric[key_str]
                english_parts = engLyric.get(key_str, [])
                
                max_parts = max(len(korean_parts), len(english_parts))
                for i in range(max_parts):
                    # 한글 부분 추가
                    if i < len(korean_parts):
                        lyrics += korean_parts[i].replace("<br/>", "\n")
                    
                    # 영문 부분 추가 (같은 인덱스)
                    if i < len(english_parts):
                        lyrics += english_parts[i].replace("<br/>", "\n")
                    
                    lyrics += "\n"
        
        # 후렴이 있으면 마지막에 추가 - 한글-영문 쌍으로 교대 표시
        if has_chorus and "후렴" in korLyric:
            lyrics += "후렴\n"
            
            # 후렴도 한글-영문 쌍으로 처리
            korean_chorus = korLyric["후렴"]
            english_chorus = engLyric.get("후렴", [])
            
            max_parts = max(len(korean_chorus), len(english_chorus))
            for i in range(max_parts):
                # 한글 후렴 부분 추가
                if i < len(korean_chorus):
                    lyrics += korean_chorus[i].replace("<br/>", "\n")
                
                # 영문 후렴 부분 추가 (같은 인덱스)
                if i < len(english_chorus):
                    lyrics += english_chorus[i].replace("<br/>", "\n")
                
                lyrics += "\n"
    except Exception as e:
        print(f"가사 로드 오류: {e}")
    
    return render_template('edit_hymn.html', hymn_info=hymn_info, hymn_number=hymn_number, lyrics=lyrics)

@app.route('/edit_ccm_lyrics/<song_title>', methods=['GET', 'POST'])
def edit_ccm_lyrics(song_title):
    import urllib.parse
    import unicodedata
    
    song_title = urllib.parse.unquote(song_title)
    
    if request.method == 'POST':
        new_title = request.form['title']
        new_lyrics = request.form['lyrics']
        
        try:
            # 가사 파일 찾기
            import glob
            pattern = os.path.join('dist', 'ccm', '*', 'lyrics.txt')
            lyrics_path = None
            
            for file_path in glob.glob(pattern):
                folder_path = os.path.dirname(file_path)
                folder_name = os.path.basename(folder_path)
                normalized_folder_name = unicodedata.normalize('NFC', folder_name)
                if normalized_folder_name == song_title:
                    lyrics_path = file_path
                    break
            
            if not lyrics_path:
                flash('CCM 가사 파일을 찾을 수 없습니다.', 'error')
                return redirect(url_for('search'))
            
            # 제목 변경이 있는 경우 폴더 이름도 변경
            old_folder = os.path.dirname(lyrics_path)
            if new_title != song_title:
                new_folder = os.path.join('dist', 'ccm', new_title)
                if os.path.exists(new_folder):
                    flash(f'CCM "{new_title}"이(가) 이미 존재합니다.', 'error')
                    return redirect(url_for('edit_ccm_lyrics', song_title=song_title))
                
                import shutil
                shutil.move(old_folder, new_folder)
                lyrics_path = os.path.join(new_folder, 'lyrics.txt')
            
            # 가사 저장
            with open(lyrics_path, 'w', encoding='utf-8') as f:
                f.write(new_lyrics)
            
            flash('CCM 가사가 성공적으로 수정되었습니다!', 'success')
        except Exception as e:
            flash(f'수정 중 오류가 발생했습니다: {str(e)}', 'error')
        
        return redirect(url_for('search'))
    
    # 기존 가사 가져오기
    lyrics = get_ccm_lyrics(song_title)
    if not lyrics:
        flash('CCM 가사를 찾을 수 없습니다.', 'error')
        return redirect(url_for('search'))
    
    return render_template('edit_ccm_lyrics.html', song_title=song_title, lyrics=lyrics)

@app.route('/edit_ccm/<song_title>', methods=['GET', 'POST'])
def edit_ccm(song_title):
    if request.method == 'POST':
        # CCM 이미지 업로드 및 순서 변경 처리
        try:
            import urllib.parse
            import shutil
            import json
            from functions import findTargetDirPath
            
            song_title = urllib.parse.unquote(song_title)
            
            # 전체 이미지 교체 확인
            files = request.files.getlist('images')
            if files and files[0].filename:
                # 기존 이미지 삭제
                ccm_dir = os.path.join(findTargetDirPath("dist/ccm"), song_title)
                if os.path.exists(ccm_dir):
                    shutil.rmtree(ccm_dir)
                os.makedirs(ccm_dir, exist_ok=True)
                
                # 새 이미지 저장
                for i, file in enumerate(files):
                    if file and allowed_file(file.filename):
                        # 파일 확장자 보존
                        file_ext = os.path.splitext(file.filename)[1]
                        filename = f"{i+1}{file_ext}"
                        file.save(os.path.join(ccm_dir, filename))
                
                flash(f'{song_title} CCM 이미지가 성공적으로 업데이트되었습니다!', 'success')
            
            # 개별 이미지 교체 확인
            else:
                ccm_dir = os.path.join(findTargetDirPath("dist/ccm"), song_title)
                images = get_ccm_images(song_title)
                updated_count = 0
                
                # 각 개별 이미지 입력 필드 확인
                for i in range(len(images)):
                    file_key = f'individual_image_{i}'
                    file = request.files.get(file_key)
                    
                    if file and file.filename and allowed_file(file.filename):
                        # 기존 파일 정보 가져오기
                        old_filename = images[i].filename
                        file_ext = os.path.splitext(file.filename)[1]
                        new_filename = f"{images[i].order}{file_ext}"
                        
                        # 기존 파일 삭제
                        old_path = os.path.join(ccm_dir, old_filename)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                        
                        # 새 파일 저장
                        new_path = os.path.join(ccm_dir, new_filename)
                        file.save(new_path)
                        updated_count += 1
                
                if updated_count > 0:
                    flash(f'{song_title} CCM의 {updated_count}개 이미지가 성공적으로 교체되었습니다!', 'success')
                else:
                    # 순서 변경 처리
                    order_data = request.form.get('image_order')
                    if order_data:
                        new_order = json.loads(order_data)
                        
                        # 기존 이미지 파일들 가져오기
                        if images and len(new_order) == len(images):
                            # 임시 디렉토리에 파일 복사
                            temp_dir = ccm_dir + "_temp"
                            os.makedirs(temp_dir, exist_ok=True)
                            
                            # 새로운 순서로 파일 복사
                            for new_index, old_index in enumerate(new_order):
                                old_filename = images[old_index].filename
                                file_ext = os.path.splitext(old_filename)[1]
                                new_filename = f"{new_index + 1}{file_ext}"
                                
                                old_path = os.path.join(ccm_dir, old_filename)
                                new_path = os.path.join(temp_dir, new_filename)
                                
                                if os.path.exists(old_path):
                                    shutil.copy2(old_path, new_path)
                            
                            # 기존 디렉토리 삭제하고 임시 디렉토리를 원래 이름으로 변경
                            shutil.rmtree(ccm_dir)
                            shutil.move(temp_dir, ccm_dir)
                            
                            flash(f'{song_title} CCM 이미지 순서가 성공적으로 변경되었습니다!', 'success')
                        else:
                            flash('이미지 순서 변경 중 오류가 발생했습니다.', 'error')
                    else:
                        flash('교체할 이미지가 없습니다.', 'warning')
                        
        except Exception as e:
            flash(f'수정 중 오류가 발생했습니다: {str(e)}', 'error')
        
        return redirect(url_for('search'))
    
    # GET 요청 - 편집 화면 표시
    import urllib.parse
    song_title = urllib.parse.unquote(song_title)
    images = get_ccm_images(song_title)
    
    return render_template('edit_ccm.html', song_title=song_title, images=images)

@app.route('/upload_media', methods=['POST'])
def upload_media():
    """미디어 파일 업로드 API"""
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
    
    if file and allowed_file(file.filename):
        # 미디어 폴더 생성
        media_dir = os.path.join('dist', 'media')
        os.makedirs(media_dir, exist_ok=True)
        
        # 파일명 생성 (타임스탬프 + 원본 확장자)
        import time
        timestamp = str(int(time.time() * 1000))  # 밀리초 단위
        file_ext = os.path.splitext(secure_filename(file.filename))[1]
        filename = f"media_{timestamp}{file_ext}"
        
        # 파일 저장
        file_path = os.path.join(media_dir, filename)
        file.save(file_path)
        
        # 상대 경로 반환
        relative_path = f"dist/media/{filename}"
        
        return jsonify({
            'success': True,
            'file_path': relative_path,
            'filename': filename,
            'original_name': file.filename
        })
    
    return jsonify({'error': '허용되지 않는 파일 형식입니다.'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5001) 