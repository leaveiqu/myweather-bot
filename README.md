# HK Weather Bot

自動化香港天文台天氣通知：
- 每日 06:00 (HKT) 發送天氣摘要去 Discord
- 每 5 分鐘檢查一次現正生效嘅天氣警告 (紅雨/黑雨/風球等)，有變化先發通知

## 設定步驟

1. 喺 GitHub 建立一個新 **public** repository，將呢個資料夾嘅所有檔案上載/push 上去。
2. 喺 Discord 頻道設定 → 整合 → 建立 Webhook，複製 Webhook URL。
3. 去 repo 嘅 **Settings → Secrets and variables → Actions → New repository secret**：
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: 你嘅 webhook URL
4. 去 **Actions** tab，應該會見到兩個 workflow：`Daily Weather Summary` 同 `Weather Warning Monitor`。
5. 可以先手動按 `Run workflow` 測試吓，Discord 頻道有冇收到訊息。
6. 之後就完全自動：daily 每日6am、monitor 每5分鐘跑一次。

## 檔案結構

```
.github/workflows/
  daily_weather.yml      每日天氣摘要 workflow
  warning_monitor.yml    警告監控 workflow
scripts/
  daily_weather.py
  warning_monitor.py
state.json                儲存上次警告狀態 (monitor自動更新)
requirements.txt
```
