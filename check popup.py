import requests
import json
import os
from playwright.sync_api import sync_playwright

STATE_FILE = "last_popup.json"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://earthstore.kr/home"


def get_popup_image():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        # 팝업이 JS로 뒤늦게 채워지는 구조라 잠깐 대기
        page.wait_for_timeout(3000)

        src = None
        try:
            el = page.query_selector("div#popup img.popupContent")
            if el:
                src = el.get_attribute("src")
        except Exception:
            pass

        browser.close()
        return src if src else None


def load_last():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f).get("src")
    return None


def save_last(src):
    with open(STATE_FILE, "w") as f:
        json.dump({"src": src}, f)


def send_telegram_photo(image_url):
    # 사이트에서 이미지를 직접 받아서(핫링크 차단 우회) 텔레그램에 파일로 업로드
    img_resp = requests.get(
        image_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://earthstore.kr/",
        },
        timeout=15,
    )
    img_resp.raise_for_status()

    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "caption": "🐄 어쓰빕(earthstore.kr) 새 팝업 감지!\n" + image_url,
        },
        files={"photo": ("popup.png", img_resp.content)},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"텔레그램 응답 코드: {resp.status_code}")
        print(f"텔레그램 응답 내용: {resp.text}")
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
