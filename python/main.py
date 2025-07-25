from functions import *

domainList = ['여는찬양', '찬양순서1', '찬양순서2', '찬양순서3', '닫는찬양', '특별찬양']
partList = [['94'],
            ['십자가 선물', '구원 열차'],
            ['내 평생 사는 동안', '204', '473'],
            ['495'],
            ['490', '184'],
            ['예수 나의 치료자', '나는 주를 섬기는 것에 후회가 없습니다']]
# '495'
# write table, lyric, interim section
body = str()
for index, domain in enumerate(domainList):
    songList = partList[index]
    table = makeTable(domain, songList)
    lyric = makeLyric(domain, songList)
    interim = makeInterim(index)
    body += table + lyric + interim

filename = open("praise.html", "w", encoding="utf-8")
filename.write(assembleHtml(body, str(), "body"))
filename.close()
