import requests
from bs4 import BeautifulSoup
import json
import os

STATE_FILE = "last_popup.json"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://earthstore.kr/home"


def get_popup_image():
    res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    img = soup.select_one("div#popup img.popupContent")
    return img["src"] if img and img.get("src") else None


def load_last():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f).get("src")
    return None


def save_last(src):
    with open(STATE_FILE, "w") as f:
        json.dump({"src": src}, f)


def send_telegram_photo(image_url):
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "caption": "🐄 어쓰빕(earthstore.kr) 새 팝업 감지!\n" + image_url,
            "photo": image_url,
        },
        timeout=15,
    )
    resp.raise_for_status()


def send_telegram_text(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=15,
    )


def check():
    try:
        current = get_popup_image()
    except Exception as e:
        # 사이트 접속 실패 등은 조용히 넘어감 (매번 알림 오면 피곤하니까)
        print(f"요청 실패: {e}")
        return

    last = load_last()
    print(f"이전: {last}\n현재: {current}")

    if current and current != last:
        send_telegram_photo(current)
        save_last(current)
        print("새 팝업 감지 -> 텔레그램 전송 완료")
    else:
        print("변경 없음")


if __name__ == "__main__":
    check()
