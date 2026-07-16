"""
監控香港天文台現正生效警告 (紅雨/黑雨/風球等)
用 warnsum dataset：冇警告時回傳 {}，有就係 dict，key係警告種類代碼。
同上次執行嘅狀態 (state.json) 比對，有變化先發 Discord webhook。
"""
import os
import sys
import json
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
WARNSUM_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=tc"
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "state.json")

# 想特別關注/高亮嘅警告代碼（可自行增減）
HIGHLIGHT_CODES = {"WRAINB", "WRAINR", "TC8NE", "TC8SE", "TC8NW", "TC8SW", "TC9", "TC10"}


def fetch_warnings():
    resp = requests.get(WARNSUM_URL, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, dict) else {}


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def send_discord(title, description, color):
    if not WEBHOOK_URL:
        print("錯誤：未設定 DISCORD_WEBHOOK_URL", file=sys.stderr)
        sys.exit(1)
    embed = {"title": title, "description": description, "color": color}
    resp = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=15)
    resp.raise_for_status()


def main():
    current = fetch_warnings()
    previous = load_state()

    current_codes = set(current.keys())
    previous_codes = set(previous.keys())

    newly_issued = current_codes - previous_codes
    cancelled = previous_codes - current_codes

    for code in newly_issued:
        info = current[code]
        name = info.get("name", code)
        is_severe = info.get("code", "") in HIGHLIGHT_CODES
        color = 0xE74C3C if is_severe else 0xF39C12
        emoji = "🚨" if is_severe else "⚠️"
        send_discord(
            f"{emoji} 新警告生效：{name}",
            f"發出時間：{info.get('issueTime', '未知')}",
            color,
        )
        print(f"已發送新警告通知：{name}")

    for code in cancelled:
        info = previous[code]
        name = info.get("name", code)
        send_discord(
            f"✅ 警告已取消：{name}",
            "此警告現已解除。",
            0x2ECC71,
        )
        print(f"已發送取消通知：{name}")

    if newly_issued or cancelled:
        save_state(current)
    else:
        print("警告狀態冇變化。")


if __name__ == "__main__":
    main()
