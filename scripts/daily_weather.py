"""
每日天氣摘要 -> 發送去 Discord webhook
資料來源：香港天文台 Open Data API
"""
import os
import sys
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

RHRREAD_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
FND_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"


def fetch_json(url):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


def build_embed():
    rhrread = fetch_json(RHRREAD_URL)
    fnd = fetch_json(FND_URL)

    # 即時溫度／濕度 (揀香港天文台總站作代表，你可以改做自己屋企附近嘅站)
    temp_data = rhrread.get("temperature", {}).get("data", [])
    humidity_data = rhrread.get("humidity", {}).get("data", [])

    hko_temp = next((d["value"] for d in temp_data if d.get("place") == "香港天文台"), None)
    humidity = humidity_data[0]["value"] if humidity_data else None

    general_situation = rhrread.get("generalSituation", "冇資料")

    # 今日預報 (九天預報第一日)
    today_forecast = fnd.get("weatherForecast", [{}])[0]
    today_desc = today_forecast.get("forecastWeather", "冇資料")
    min_temp = today_forecast.get("forecastMintemp", {}).get("value", "?")
    max_temp = today_forecast.get("forecastMaxtemp", {}).get("value", "?")
    min_rh = today_forecast.get("forecastMinrh", {}).get("value", "?")
    max_rh = today_forecast.get("forecastMaxrh", {}).get("value", "?")

    fields = [
        {
            "name": "🌡️ 現時天氣 (天文台總站)",
            "value": f"溫度：{hko_temp}°C　濕度：{humidity}%",
            "inline": False,
        },
        {
            "name": "📋 現況",
            "value": general_situation,
            "inline": False,
        },
        {
            "name": "📅 今日預報",
            "value": f"{today_desc}\n氣溫：{min_temp}–{max_temp}°C　濕度：{min_rh}–{max_rh}%",
            "inline": False,
        },
    ]

    embed = {
        "title": "☀️ 香港天氣早晨速報",
        "color": 0x3498DB,
        "fields": fields,
        "footer": {"text": "資料來源：香港天文台 Open Data API"},
    }
    return embed


def send_to_discord(embed):
    if not WEBHOOK_URL:
        print("錯誤：未設定 DISCORD_WEBHOOK_URL", file=sys.stderr)
        sys.exit(1)
    resp = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=15)
    resp.raise_for_status()


def main():
    embed = build_embed()
    send_to_discord(embed)
    print("已發送每日天氣摘要。")


if __name__ == "__main__":
    main()
