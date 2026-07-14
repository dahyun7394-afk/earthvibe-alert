import requests
from bs4 import BeautifulSoup

url = "https://earthstore.kr"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(url, headers=headers).text

keywords = [
    "PRE ORDER",
    "PREORDER",
    "프리오더",
    "예약판매"
]

found = False

for keyword in keywords:
    if keyword.lower() in html.lower():
        found = True
        break

if found:
    print("프리오더 발견!")
else:
    print("아직 없음")
