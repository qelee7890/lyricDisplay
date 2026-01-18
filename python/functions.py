import os
import re
import csv

def findParentPath():
    thisDirPath = os.path.dirname(os.path.abspath(__file__))
    parentDirPath = os.path.dirname(thisDirPath)
    return parentDirPath


def findTargetDirPath(subDirName):
    parentDirPath = findParentPath()
    dirPath = joinPath(parentDirPath, subDirName)
    return dirPath


def joinPath(dirPath1, dirPath2):
    pathJoined = os.path.join(dirPath1, dirPath2)
    return pathJoined


def openTextFile(dirName, fileName, mode):
    file = open(joinPath(findTargetDirPath(dirName),
                fileName), mode, encoding="utf-8")
    return file


def countFilesInFolder(string):
    dirname = findTargetDirPath(f"dist/ccm/{string}")
    filelists = [name for name in os.listdir(
        dirname) if os.path.isfile(os.path.join(dirname, name))]
    if '.DS_Store' in filelists:
        filelists.remove('.DS_Store')
    # print(filelists)
    numFiles = len(filelists)
    return numFiles


def isFileExist(dirName, fileName):
    if os.path.isfile(joinPath(findTargetDirPath(dirName), fileName)):
        return True
    else:
        return False
    
def assembleHtml(content, domain, mode):
    if mode == "body":
        header = """<!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>lyricDisplay</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="dist/reset.css">
                <link rel="stylesheet" href="dist/reveal.css">
                <link rel="stylesheet" href="dist/ldstyle.css" id="theme">
            </head>
            <body>
                <div class="reveal">
                    <div class="slides">
                        <section data-background="dist/wallpaper/voyage_of_life-1.jpg" data-background-color="#222">
                            <div class="js-clock" style="text-align: left">
                                <h2>날짜</h2>
                                <h3>시간</h3>
                            </div>
                        </section>"""

        footer = """
                    </div>
                </div>
                <script src="dist/reveal.js"></script>
                <script src="dist/clock.js"></script>
                <script>
                    Reveal.initialize({
                width: 1280,
                height: 720,
                        controls: true,
                        progress: true,
                        center: false,
                        hash: true,
                        navigationMode: "linear",
                        parallaxBackgroundImage: "dist/wallpaper/Sea-beach-grass-sky_1920x800.jpg",
                        parallaxBackgroundSize: "2688px 1280px",
                        parallaxBackgroundHorizontal: 10,
                        parallaxBackgroundVertical: 0,
                        transition: "slide"
                    });
                </script>
            </body>
        </html>
        """
    elif mode == "table":
        header = f"""
                        <section id="{domain}">
                            <h2>{domain}</h2>
                            <table>
                                <tbody>
                                    <thead>
                                        <td></td>
                                        <td></td>
                                        <td></td>
                                    </thead>"""

        footer = f"""
                                </tbody>
                            </table>
                        </section>"""
    elif mode == "lyric":
        header = f"""
        		        <section id="{domain}">"""
        footer = f"""
        		        </section>"""
    block = header + content + footer
    return block


def makeHymnLyricSub(korLyric, engLyric, key, prop, totVerse):
    """
    수정 화면의 한글-영문 교대 형태를 프레젠테이션에서도 동일하게 유지
    """
    lyricSubHeader = f"""
                            <section data-transition="none">
                                <h2>{prop["hymnNumber"]}장<a>(새{prop["newHymnNumber"]})</a>. {prop["hymnTitle"]}</h2>
                                <div class="imageblock">"""
    lyricSubFooter = f"""
                                </div>
                                <h4>{key}절/{totVerse}절</h4>
                            </section>"""
    
    # 수정 화면에서 보는 것과 동일한 형태로 재구성
    korVerses = korLyric[key] if key in korLyric else []
    engVerses = engLyric[key] if key in engLyric else []
    
    if korVerses and engVerses and len(korVerses) == len(engVerses):
        # 한글-영문 쌍이 있는 경우 - 교대로 표시하되 하나의 슬라이드에
        combined_content = []
        
        for i in range(len(korVerses)):
            # 한글 부분 추가 (빈 라인 제거)
            korean_text = korVerses[i].replace("<br/>", "<br/>").strip()
            if korean_text:
                combined_content.append(korean_text)
            
            # 영문 부분 추가 (빈 라인 제거)
            english_text = engVerses[i].replace("<br/>", "<br/>").strip()
            if english_text:
                combined_content.append(english_text)
            
            # 각 쌍 사이에 빈 줄 추가 (마지막 쌍 제외)
            if i < len(korVerses) - 1:
                combined_content.append('<br/>')
        
        # 하나의 슬라이드로 생성
        lyricSubContent = f"""
                                    <p>
                                    {key+"."}<br/>
                                    {"<br/>".join(combined_content)}
                                    </p>"""
        return lyricSubHeader + lyricSubContent + lyricSubFooter
        
    elif korVerses:
        # 한글만 있는 경우
        lyricSub = ""
        for i in range(len(korVerses)):
            lyricSubContent = f"""
                                    <p>
                                    {key+"."}<br/>
                                    {korVerses[i]}
                                    </p>"""
            lyricSub += lyricSubHeader + lyricSubContent + lyricSubFooter
        return lyricSub
    
    return ""


def makeInterim(index):
    if index == 0:
        interim = f"""
        			    <section data-background="dist/wallpaper/voyage_of_life-1.jpg" data-background-color="#222"></section>"""
    elif index == 1:
        interim = f"""
        			    <section data-background="dist/wallpaper/voyage_of_life-2.jpg" data-background-color="#222"></section>"""
    elif index == 2:
        interim = f"""
        			    <section data-background="dist/wallpaper/voyage_of_life-3.jpg" data-background-color="#222"></section>"""
    elif index == 3:
        interim = f"""
                        <section data-background="dist/wallpaper/prayer-bible.jpg" data-background-color="#222">
                        <h2>지금은 기도하는 시간입니다.</h2>
                        </section>"""
    elif index == 4:
        interim = f"""
        			    <section data-background-color="coral">
                            <img class="r-stretch" src="dist/wallpaper/prayerlist.png">
                        </section>"""
    elif index == 5:
        interim = f"""
        			    <section data-background="dist/wallpaper/voyage_of_life-1.jpg" data-background-color="#222"></section>"""
    elif index == 6:
        interim = f"""
        			    <section data-background="dist/wallpaper/voyage_of_life-1.jpg" data-background-color="#222"></section>"""
    elif index == 7:
        interim = f"""
                        <section data-background="dist/picture/wedding2.png" data-background-color="#222"></section>
                        
                        <section data-transition="none" data-background-color="#fff">
        			        <section data-background="dist/picture/wedding1.png"></section>

                            <section>
                                <video controls width="1024">
                                    <source src="dist/video/Seo-message.mp4" type="video/mp4">
                                </video>
                            </section>

                        </section>"""
    return interim


def makeTable(domain, songList):
    tableContent = str()
    for songTitle in songList:
        if isUnicode(songTitle[0], "0"):
            prop = findHymnInfo(songTitle)
            tableContent += f"""
                                <tr>
                                    <th> 찬송가 </th>
                                    <th> {prop["hymnNumber"]}장 </th>
                                    <th> {prop["hymnTitle"]} </th>
                                </tr> """
        else:
            tableContent += f"""
                                <tr>
                                    <th> 찬양곡 </th>
                                    <th> </th>
                                    <th> {songTitle} </th>
                                </tr > """
    table = assembleHtml(tableContent, domain, "table")
    return table


def makeLyric(domain, songList):
    lyric = str()

    for songTitle in songList:
        # print(songTitle)  # 디버그용 출력 비활성화
        lyricSub = str()
        if isUnicode(songTitle[0], "0"):  # hymn lyric
            hymnfile = openTextFile("dist/hymn", "hymn.txt", "r")

            prop = findHymnInfo(songTitle)
            korLyric, engLyric = classifyLyric(songTitle, hymnfile)

            keys = korLyric.keys()
            numKeys = len(keys)
            if "후렴" in keys:
                for i in range(len(keys)-1):
                    lyricSub += makeHymnLyricSub(korLyric,
                                                 engLyric, str(i+1), prop, numKeys-1)
                    lyricSub += makeHymnLyricSub(korLyric,
                                                 engLyric, "후렴", prop, numKeys-1)
            else:
                for i in range(len(keys)):
                    lyricSub += makeHymnLyricSub(korLyric,
                                                 engLyric, str(i+1), prop, numKeys)
            lyric += assembleHtml(lyricSub, domain, "lyric")

            hymnfile.close()
        else:  # ccm lyric
            numFiles = countFilesInFolder(songTitle)
            lyricSub = str()
            for i in range(numFiles):
                lyricSubHeader = f"""
                            <section data-transition="none">
                                <h2>{songTitle}</h2>
                                <div class="imageblock">"""
                lyricSubFooter = f"""
                                </div>
                                <h4>{i+1}장/{numFiles}장</h4>
                            </section>"""
                lyricSubContent = f"""
                	    	        <img class="cropped" src="dist/ccm/{songTitle}/{str(i+1)}.jpg" style="object-position: 0 0%; width: 100%;" />"""
                lyricSub += lyricSubHeader + lyricSubContent + lyricSubFooter
            lyric += assembleHtml(lyricSub, domain, "lyric")

    return lyric

def isUnicode(char, mode):
    result = False
    if mode == "0":
        # 0~9: 48~57
        if 47 < ord(char) < 58:
            result = True
    elif mode == "가":
        # 가~힣: 44032~55203
        if 44031 < ord(char) < 55204:
            result = True
    return result


def findHymnInfo(song):
    filename = openTextFile("dist/hymn", "hymnInfo.csv", "r")
    infos = csv.reader(filename)
    prop = dict()
    for info in infos:
        if info[0] == song:
            prop["hymnNumber"] = info[0]
            prop["newHymnNumber"] = info[1]
            prop["hymnTitle"] = info[2]
    filename.close()
    return prop


def classifyLyric(songTitle, hymnfile):
    iscopy = False
    lyric = str()
    for line in hymnfile:
        if "<" + songTitle + "장>" in line:
            iscopy = True
            continue
        elif "<" + str(int(songTitle)+1) + "장>" in line:
            iscopy = False
            break

        if iscopy == True:
            lyric += line

    # remove multiple newlines
    while True:
        if not "\n\n" in lyric:
            break
        lyric = re.sub(r"\n\n", "\n", lyric)
    lyric = lyric.strip()
    lyric = lyric + "\n"
    
    # store line separately based on newline and replace it by htmltag
    lineList = list()
    prevIndex = 0
    for index, char in enumerate(lyric):
        if ord(char) == 10:  # ord("\n")
            lineList.append(lyric[prevIndex:index+1])
            prevIndex = index+1
    for index, line in enumerate(lineList):
        lineList[index] = re.sub(r"\n", "<br/>", line)
    
    # Parse lyrics maintaining Korean-English pairing structure
    korLyric = dict()
    engLyric = dict()
    current_verse = None
    verse_content = []  # 각 절의 모든 라인들을 순서대로 저장
    
    for line in lineList:
        if isUnicode(line[0], "0"):  # verse number
            # Save previous verse if exists
            if current_verse and verse_content:
                kor_parts, eng_parts = parse_verse_content(verse_content)
                korLyric[current_verse] = kor_parts
                engLyric[current_verse] = eng_parts
            
            current_verse = line[0]
            verse_content = []
            
        elif "후렴" in line:  # chorus marker
            # Save previous verse if exists
            if current_verse and verse_content:
                kor_parts, eng_parts = parse_verse_content(verse_content)
                korLyric[current_verse] = kor_parts
                engLyric[current_verse] = eng_parts
            
            current_verse = "후렴"
            verse_content = []
            
        else:
            # This is a lyric line - add to current verse content
            if current_verse and line.strip():
                verse_content.append(line)
    
    # Save the last verse
    if current_verse and verse_content:
        kor_parts, eng_parts = parse_verse_content(verse_content)
        korLyric[current_verse] = kor_parts
        engLyric[current_verse] = eng_parts
    
    return korLyric, engLyric

def parse_verse_content(verse_lines):
    """
    절의 모든 라인들을 한글-영문 쌍으로 파싱
    연속된 한글라인들과 그 다음 연속된 영문라인들을 하나의 쌍으로 처리
    연속된 빈 줄 2개 이상은 쌍의 구분자로 사용
    """
    kor_parts = []
    eng_parts = []

    current_korean = []
    current_english = []

    i = 0
    while i < len(verse_lines):
        line = verse_lines[i].strip()

        # 빈 줄을 만났을 때 연속된 빈 줄의 개수 확인
        if not line:
            empty_count = 0
            # 연속된 빈 줄 개수 세기
            j = i
            while j < len(verse_lines) and not verse_lines[j].strip():
                empty_count += 1
                j += 1

            # 연속된 빈 줄이 2개 이상일 때만 슬라이드 구분
            if empty_count >= 2:
                if current_korean or current_english:
                    kor_parts.append(''.join(current_korean))
                    eng_parts.append(''.join(current_english))
                    current_korean = []
                    current_english = []

            # 빈 줄들을 모두 건너뛰기
            i = j
            continue

        if isUnicode(line[0], "가"):  # Korean line
            # If we were collecting English, save the previous pair
            if current_english:
                kor_parts.append(''.join(current_korean))
                eng_parts.append(''.join(current_english))
                current_korean = []
                current_english = []

            # Collect all consecutive Korean lines
            current_korean.append(verse_lines[i])

        else:  # English line
            # Collect all consecutive English lines
            current_english.append(verse_lines[i])

        i += 1

    # Save the final pair
    if current_korean or current_english:
        kor_parts.append(''.join(current_korean))
        eng_parts.append(''.join(current_english))

    # Ensure both lists have the same length
    while len(eng_parts) < len(kor_parts):
        eng_parts.append("")
    while len(kor_parts) < len(eng_parts):
        kor_parts.append("")

    return kor_parts, eng_parts

def generate_sample_presentation():
    """샘플 프레젠테이션 생성 함수"""
    domainList = ['여는찬양','찬양순서1','찬양순서2','찬양순서3','닫는찬양','특별찬양']
    partList = [['94'], 
                ['하늘의 복이 함께하리','요셉처럼'],
                ['453', '나 무엇과도', '슬픈 마음 있는 자'], 
                ['495'], 
                ['427','184'], 
                ['충만']]
    # write table, lyric, interim section
    body = str()
    for index, domain in enumerate(domainList):  
        songList = partList[index]
        table = makeTable(domain, songList)
        lyric = makeLyric(domain, songList)
        interim = makeInterim(index)
        body += table + lyric + interim
    #
    filename = open("praise.html", "w", encoding="utf-8")
    filename.write(assembleHtml(body, str(), "body"))
    filename.close()

# 직접 실행될 때만 샘플 생성
if __name__ == "__main__":
    generate_sample_presentation()