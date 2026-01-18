import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))
from app import normalize_text, fuzzy_match, is_chosung_match

# 테스트
query = "사랑"
title1 = "하나님의 크신 사랑"
title2 = "예수님의 귀한 사랑"

print(f"query: {query}")
print(f"title1: {title1}")
print(f"title2: {title2}")
print()

print(f"normalize_text(query): {normalize_text(query)}")
print(f"normalize_text(title1): {normalize_text(title1)}")
print()

print(f"fuzzy_match(query, title1): {fuzzy_match(query, title1)}")
print(f"fuzzy_match(query, title2): {fuzzy_match(query, title2)}")
print()

# 초성 테스트
query2 = "ㅅㄹ"
print(f"is_chosung_match('{query2}', title1): {is_chosung_match(query2, title1)}")
print(f"is_chosung_match('{query2}', title2): {is_chosung_match(query2, title2)}")
