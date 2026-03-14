# Travel-AI 產品需求文件（PRD）

| 項目 | 內容 |
|---|---|
| **產品名稱** | Travel-AI |
| **文件版本** | 2.0 |
| **最後更新** | 2026-03-14 |
| **負責人** | Woodrow Shen (woodrow.shen@gmail.com) |
| **授權** | MIT |
| **狀態** | 開發中 |

---

## 目錄

1. [產品願景與摘要](#1-產品願景與摘要)
2. [目標用戶與使用場景](#2-目標用戶與使用場景)
3. [產品功能](#3-產品功能)
4. [系統架構](#4-系統架構)
5. [技術規格](#5-技術規格)
6. [非功能需求](#6-非功能需求)
7. [實作路線圖](#7-實作路線圖)
8. [驗證與測試策略](#8-驗證與測試策略)
9. [部署策略](#9-部署策略)
10. [附錄：API 整合詳細規格](#10-附錄api-整合詳細規格)

---

## 1. 產品願景與摘要

Travel-AI 是一個智能旅遊聚合平台，透過多代理 AI 系統（基於 Anthropic Claude API）聚合、比較旅遊選項（機票、飯店、活動），並提供 AI 驅動的個人化推薦與行程規劃。

**核心價值主張**：

- **多來源聚合**：整合 Amadeus、Skyscanner、Kiwi 等多個資料來源，提供最全面的搜尋結果
- **AI 智能推薦**：透過多代理協作系統，以自然語言對話方式協助用戶規劃旅程
- **價格監控**：24/7 背景監控機票價格，偵測 Bug Fare 與價格下跌，即時通知用戶
- **台灣旅客優先**：預設 TWD 幣別、亞太轉機樞紐、外國人票價優惠整合

**技術選型**：Python FastAPI + Next.js 15 + Multi-Agent (Claude API) + PostgreSQL 16 + Redis 7 + Docker Compose

---

## 2. 目標用戶與使用場景

### 2.1 目標用戶

| 用戶類型 | 描述 | 需求 |
|---|---|---|
| **一般旅客（Basic）** | 透過 Google 登入的使用者 | 搜尋、比價、AI 聊天、訂閱通知（基本額度） |
| **進階旅客（Premium）** | 升級用戶或測試帳號 | Basic 全部 + 直達模式、進階推薦、更高訂閱額度 |

### 2.2 核心使用場景

| 場景 | 描述 | 對應功能 |
|---|---|---|
| 機票搜尋比價 | 用戶搜尋特定航線，跨來源比較價格 | 多來源搜尋、比價表 |
| AI 對話式規劃 | 用自然語言描述旅遊需求，AI 協助搜尋與推薦 | SSE 串流聊天、多 Agent 協作 |
| 直飛推薦 | 指定日期與目的地，取得最推薦的直飛航班（非僅最低價） | 直達模式（Premium） |
| 目的地探索 | 只有日期沒有目的地，探索全球最便宜航班 | 冒險模式 |
| 行程規劃 | AI 生成日程行程表，包含路線優化 | 行程生成 |
| 價格追蹤 | 訂閱特定航線，價格下降或出現 Bug Fare 時收到通知 | 郵件訂閱系統 |
| 多段銜接 | 搜尋無直飛的二線城市，自動拆解國際線 + 國內線 | 多段銜接搜尋 |
| ~~飯店搜尋~~ | ~~搜尋飯店，跨來源比較價格~~ | ~~暫時停用（見 §3.12）~~ |

---

## 3. 產品功能

### 3.1 AI 對話介面

透過 SSE 串流聊天，用戶以自然語言描述需求，系統透過多代理協作回應。

- **事件類型**：`text`（AI 文字）、`data`（結構化資料如搜尋結果）、`done`（結束）
- **多代理協調**：Coordinator Agent 解析意圖後分派至專職代理，支援並行執行

### 3.2 機票搜尋

多來源聚合搜尋，整合 Amadeus + Skyscanner + Kiwi 三個資料源，並行查詢後合併去重。

- 支援單程、來回搜尋
- 結果標記來源（`provider`），支援依價格、時間、轉機次數排序
- 自動匯率轉換（Amadeus EUR/USD 回應轉為用戶幣別）
- Redis 快取搜尋結果（TTL 30 分鐘）

### 3.3 直達模式（Premium 限定）

用戶指定日期區間 + 目的地，系統列出最推薦的直飛航班。排序非以價格為主，而是綜合評分：

1. **航空公司評價**：Skytrax 評等、用戶偏好航空加分
2. **時段合理性**：避免紅眼、優先上午/下午出發
3. **飛行時間**：同航線選最短
4. **機型舒適度**：寬體機加分
5. **價格**：作為次要參考

### 3.4 冒險模式

用戶只提供日期區間，系統從出發地搜尋全球任意目的地，列出最便宜的前 10 個目的地航班。

- 搜尋策略：Amadeus Flight Inspiration Search + Skyscanner Anywhere + Kiwi Deals
- 合併多來源結果，按價格排序
- 整合用戶偏好（偏好航空標註、排除航空過濾）

### 3.5 多段銜接搜尋

當目的地無直飛或國際航班時，Search Agent 自動拆解為「國際航班 + 國內線轉機」兩段式搜尋。

**Gateway Hub 對應表**（初期支援）：

| 國家 | Gateway Hubs | 國內線覆蓋 |
|---|---|---|
| 日本 | NRT, HND, KIX, NGO | ANA/JAL 國內線網絡（200+ 航點） |
| 韓國 | ICN, GMP | 大韓/韓亞國內線 |
| 泰國 | BKK, DMK | Thai Airways/Nok Air 國內線 |
| 印尼 | CGK | Garuda/Lion Air 國內線 |

**日本外國人優惠整合**：

| 航空 | 優惠名稱 | 單程價格 | 備註 |
|---|---|---|---|
| ANA | Experience JAPAN Fare | ~¥5,500 (~TWD 1,200) | 需持外國護照，國際線搭配 |
| JAL | Japan Explorer Pass | ~¥5,500 (~TWD 1,200) | 需持外國護照，國際線搭配 |

**銜接方案排序邏輯**：
1. 總價（國際段 + 國內段，國內段以優惠票價計）
2. 轉機時間合理性（最短 2 小時，最長 6 小時，避免過夜）
3. 同機場轉機優先（NRT→NRT 優於 NRT→HND）
4. 國內段時段（避免紅眼）

### 3.6 比價功能

跨來源價格比較，以表格形式呈現各來源對同一航班的報價。

- 統一比價端點：接收航班 ID 列表，回傳各來源價格
- 從 Redis 快取讀取搜尋結果組成比較表
- 標記最低價來源

### 3.7 行程管理

Trip CRUD 功能，支援儲存搜尋結果到行程、AI 生成日程行程表。

- 行程包含：機票、飯店、活動、行程表
- AI 行程生成：透過 ItineraryAgent 規劃日程，使用最近鄰 TSP 路線優化

### 3.8 郵件訂閱系統

#### 訂閱類型

| 類型 | 說明 | 觸發條件 |
|---|---|---|
| **Bug Fare Alert** | 異常低價機票通知（錯誤票價、閃促） | 價格低於歷史均價 50%+ |
| **Price Drop Alert** | 自訂路線的價格下降通知 | 價格低於用戶設定閾值 |
| **Deal Digest** | 每日/每週最划算的機票精選 | 定時排程（用戶選擇頻率） |

#### 訂閱流程

1. 用戶設定訂閱，選擇使用登入 Gmail（預設）或自訂 Email（需驗證）
2. 選擇訂閱類型 + 偏好設定（出發地、目的地、目標價格、頻率等）
3. 儲存至 DB，背景任務持續監控，條件觸發時寄送 Email

#### Email 地址管理

- 登入 Gmail 直接可用，無需驗證
- 自訂 Email 發送驗證信，點擊確認後啟用
- 每位用戶最多 3 個接收 Email
- Email 底部附一鍵退訂連結

### 3.9 用戶偏好設定

用戶可設定個人化篩選條件，所有訂閱通知依偏好過濾：

| 偏好類型 | 說明 | 範例 |
|---|---|---|
| 偏好航空公司 | 只通知特定航空的機票 | NH (ANA), BR (EVA), JX (StarLux), CI (華航) |
| 排除航空公司 | 排除不想搭的航空 | 特定廉航 |
| 偏好聯盟 | 按航空聯盟篩選 | Star Alliance, SkyTeam, oneworld |
| 艙等偏好 | 只通知特定艙等 | 經濟艙、商務艙 |
| 轉機偏好 | 直飛 / 最多1轉 / 不限 | 直飛優先 |
| 出發地 | 預設出發機場 | TPE, TSA, KHH |

**偏好在各訂閱類型的作用**：
- Bug Fare Alert：只通知偏好航空公司的 Bug Fare
- Price Drop Alert：在自訂路線基礎上再用航空公司篩選
- Deal Digest：精選摘要依偏好排序，偏好航空置頂

### 3.12 飯店功能（⏸️ 暫時停用）

> **狀態**：暫時停用（2026-03-14）
> **原因**：Skyscanner / Kiwi RapidAPI 的飯店搜尋端點尚未驗證是否可在免費方案下正常使用。在確認 API 可用性之前，所有飯店相關功能暫停開發。

**影響範圍**：
- `POST /search/hotels`：端點存在但回傳空結果（stub）
- `POST /compare/hotels`：端點存在但回傳空結果（stub）
- `SearchAgent.search_hotels` 工具：未接入實際 API
- 前端搜尋頁面：飯店搜尋 tab 保留但功能未實作

**恢復條件**：
1. 驗證 Skyscanner `/hotels/search` 端點在免費方案下可正常回傳結果
2. 驗證 Kiwi `/stays/search/by-dest` 端點在免費方案下可正常回傳結果
3. 確認任一來源可用後，重新啟用飯店搜尋整合

---

### 3.10 認證系統

Google OAuth 2.0 登入，JWT session 管理。

- Access token：30 分鐘 TTL
- Refresh token：7 天 TTL
- 用戶等級：Basic（預設）/ Premium
- 開發環境提供等級切換 API（`ALLOW_TIER_SWITCH=true` 時啟用）

### 3.11 匯率自動轉換

Amadeus API 回傳 EUR/USD 價格，系統自動轉為用戶幣別。

- 匯率來源：open.er-api.com（免費、無需 API key）
- Redis 快取 6 小時
- IP 偵測用戶幣別：ip-api.com + Redis 快取 24 小時
- 匯率與搜尋並行抓取，不增加延遲
- 匯率不可用時，保留原始幣別

---

## 4. 系統架構

### 4.1 服務架構

```
┌─────────────┐     rewrites /api/*     ┌──────────────┐
│  frontend   │ ──────────────────────► │   backend    │
│ Next.js 15  │                         │  FastAPI     │
│ :3000       │                         │  :8000       │
└─────────────┘                         └──┬───────┬───┘
                                           │       │
                                    ┌──────▼──┐ ┌──▼──────┐
                                    │   db    │ │  redis   │
                                    │ PG 16   │ │ Redis 7  │
                                    │ :5432   │ │ :6379    │
                                    └──▲──────┘ └──▲──────┘
                                       │          │
                                    ┌──┴──────────┴──┐
                                    │    monitor     │
                                    │  APScheduler   │
                                    │  (no port)     │
                                    └────────────────┘
```

5 個 Docker 服務：backend、frontend、monitor、db（PostgreSQL）、redis

### 4.2 多代理 AI 系統（Coordinator Pattern）

```
                    Coordinator Agent（協調者）
                           |
          +--------+-------+-------+--------+
          |        |       |       |        |
       Search   Price   Recommend  Itinerary  Budget
       Agent    Agent    Agent     Agent      Agent
```

| 代理 | 職責 | 工具 |
|---|---|---|
| **Coordinator** | 接收查詢、解析意圖、分派子代理（可並行）、合成結果 | — |
| **Search** | 機票/活動搜尋、Gateway Hub 解析、多段銜接（飯店暫時停用） | `search_flights`, ~~`search_hotels`~~, `search_activities`, `search_domestic_flights`, `resolve_gateway_hubs`, `combine_segments` |
| **Price** | 多來源比價分析、價格歷史 | `compare_prices`, `get_price_history` |
| **Recommendation** | 個人化推薦、航空公司評等、品質評分 | `get_user_preferences`, `analyze_reviews` |
| **Itinerary** | 日程行程規劃、最近鄰 TSP 路線優化 | `create_itinerary`, `optimize_route` |
| **Budget** | 每國每日預算估算（TWD）、替代方案 | `estimate_costs`, `find_alternatives` |

所有代理繼承 `BaseAgent` ABC，使用 Anthropic SDK tool_use 模式的代理迴圈：
1. 發送訊息 + 工具定義至 Claude API
2. 若 `stop_reason == "tool_use"` → 在地執行工具 → 將結果回饋
3. 重複直到 `stop_reason == "end_turn"` 或達到上限（10 輪）

### 4.3 價格監控 Daemon

獨立 Python 背景服務，24/7 執行機票價格監控，以用戶訂閱驅動——只監控有人訂閱的航線。

**架構組成**：

| 組件 | 說明 |
|---|---|
| **Scheduler** | APScheduler，3 個排程任務：price_scan（每 4 小時）、deal_digest（每日凌晨）、cleanup（每日） |
| **Price Fetcher** | Amadeus + RapidAPI 客戶端，token bucket 速率控制 |
| **Anomaly Detector** | Bug Fare 偵測：歷史均價 + 標準差 + 多來源交叉驗證 |
| **Preference Filter** | 載入全域偏好 + 訂閱級 airline_override，過濾結果 |
| **Notifier** | 比對訂閱條件，觸發寄信，記錄至 notification_log，含 cooldown 機制 |

**Bug Fare 偵測演算法**：

```
1. 計算航線 90 天移動平均價與標準差
2. 條件判斷：
   - 價格低於均價 50% → 高信心度
   - 價格低於 2 個標準差 → 中信心度
3. 交叉驗證：只有單一來源出現低價 → 提升信心度（更可能是 Bug Fare）
4. 觸發即時通知（Bug Fare 存活時間短，需快速反應）
```

**API 配額策略**：

假設 50 條活躍航線：每條每天查 3 次 = 150 次/天，Amadeus 4,500 次/月（在免費額度內）。

自動調節：
- 訂閱航線 > 55 條 → 降頻為每 12 小時
- 訂閱航線 > 100 條 → 降頻為每日 + 升級提醒
- Bug Fare 候選 → 立即加密查詢（不受降頻影響）

---

## 5. 技術規格

### 5.1 API 端點

| 群組 | 端點 | 認證 | 說明 |
|---|---|---|---|
| Health | `GET /health` | 無 | 健康檢查 |
| Geo | `GET /geo/currency` | 無 | IP 偵測幣別 |
| Auth | `GET /auth/google` | 無 | 導向 Google OAuth |
| Auth | `GET /auth/google/callback` | 無 | OAuth 回呼，建立用戶、簽發 JWT |
| Auth | `POST /auth/refresh` | JWT | 刷新 token |
| Auth | `GET /auth/me` | JWT | 取得當前用戶 |
| Auth | `PATCH /auth/me/tier` | JWT | 切換等級（僅 dev/test） |
| Auth | `POST /auth/logout` | JWT | 登出 |
| Search | `POST /search/flights` | JWT | 多來源機票搜尋 |
| Search | `POST /search/hotels` | JWT | 飯店搜尋 ⚠️ **暫時停用** |
| Search | `POST /search/direct` | JWT (Premium) | 直達模式 |
| Search | `POST /search/adventure` | JWT | 冒險模式 |
| Compare | `POST /compare` | JWT | 統一比價端點 |
| Compare | `POST /compare/flights` | JWT | 機票比價 |
| Compare | `POST /compare/hotels` | JWT | 飯店比價 ⚠️ **暫時停用** |
| Trips | CRUD `/trips` | JWT | 行程管理 |
| Itineraries | `POST /itineraries` | JWT | 行程表生成 |
| Chat | `POST /chat` | JWT | SSE 串流聊天 |
| Subscriptions | CRUD `/subscriptions` | JWT | 訂閱管理 |
| Subscriptions | `POST /subscriptions/emails` | JWT | 新增接收 Email |
| Subscriptions | `GET /subscriptions/emails/verify` | Token | 驗證 Email |
| Subscriptions | `GET /subscriptions/unsubscribe` | Token | 一鍵退訂 |
| Users | `GET /users/preferences` | JWT | 取得偏好 |
| Users | `PATCH /users/preferences` | JWT | 更新偏好 |

所有端點前綴為 `/api/v1/`。

### 5.2 資料模型

**PostgreSQL 16** — 主要存儲，JSONB 欄位存放半結構化資料
**Redis 7** — 快取（搜尋結果 30min、價格 1hr、匯率 6hr、IP 幣別 24hr）+ 對話 session

#### 核心表（11 個）

**關聯結構**：
`User` → `UserPreference` (1:1), `Trip` (1:N), `ChatSession` (1:N), `Subscription` (1:N), `SubscriptionEmail` (1:N)
`Trip` → `Flight` (1:N), `Hotel` (1:N), `Activity` (1:N), `Itinerary` (1:N)
`Subscription` → `NotificationLog` (1:N)
`PriceHistory`（獨立表，無外鍵）

所有 ID 為 UUID。JSONB 欄位用於彈性資料（`raw_data`, `metadata`, `schedule`, `messages`, `config`）。PostgreSQL ARRAY 欄位用於偏好設定。

#### 關鍵表結構

**user_preferences**：
- `id`, `user_id` (FK), `preferred_airlines` (TEXT[]), `excluded_airlines` (TEXT[]), `preferred_alliances` (TEXT[]), `cabin_classes` (TEXT[]), `max_stops` (INT), `home_airports` (TEXT[])

**subscriptions**：
- `id`, `user_id` (FK), `email_id` (FK → subscription_emails), `type` (enum: bug_fare / price_drop / deal_digest), `config` (JSONB: origins, destinations, target_price, frequency, airline_override), `is_active`, `last_sent_at`, `created_at`

**subscription_emails**：
- `id`, `user_id` (FK), `email`, `is_verified`, `verified_at`, `created_at`

**notification_log**：
- `id`, `subscription_id` (FK), `email`, `subject`, `sent_at`, `status` (sent/failed)

### 5.3 資料格式契約

#### 機票搜尋回應 (SearchResponse)

```json
{
  "search_id": "uuid",
  "type": "flight",
  "flights": [
    {
      "id": "stable-hash-id",
      "provider": "amadeus|skyscanner|kiwi",
      "price": 7121,
      "currency": "TWD",
      "airline": "CI",
      "airline_name": "China Airlines",
      "flight_number": "CI100",
      "origin": "TPE",
      "destination": "NRT",
      "outbound_segments": [
        {
          "airline": "CI",
          "flight_number": "CI100",
          "departure_airport": "TPE",
          "arrival_airport": "NRT",
          "departure_time": "2026-04-01T08:30:00",
          "arrival_time": "2026-04-01T12:30:00",
          "duration_minutes": 180,
          "cabin_class": "economy"
        }
      ],
      "return_segments": [],
      "total_duration_minutes": 180,
      "stops": 0,
      "booking_url": "https://...",
      "expires_at": "2026-04-01T23:59:59"
    }
  ],
  "total_results": 25,
  "search_params": { "..." },
  "created_at": "2026-03-13T10:00:00"
}
```

#### 直達模式回應

```json
{
  "recommendations": [
    {
      "rank": 1,
      "score": 92,
      "flight": { "airline": "NH", "flight_no": "NH852", "..." },
      "reasons": ["偏好航空 ANA", "上午出發", "787 寬體機", "飛行時間最短"],
      "price": { "amount": 15200, "currency": "TWD" }
    }
  ],
  "total_direct_flights": 8
}
```

#### 冒險模式回應

```json
{
  "adventures": [
    {
      "rank": 1,
      "destination": { "city": "Bangkok", "airport": "BKK", "country": "TH" },
      "best_flight": {
        "airline": "JX", "flight_no": "JX741",
        "departure": "2026-04-01T08:30", "arrival": "2026-04-01T11:45",
        "stops": 0, "duration_hours": 3.25
      },
      "price": { "amount": 4200, "currency": "TWD" },
      "tags": ["直飛", "最低價"]
    }
  ],
  "search_coverage": "搜尋了 150+ 目的地",
  "origin": "TPE"
}
```

#### 多段銜接回應

```json
{
  "type": "multi_segment",
  "segments": [
    {
      "leg": 1, "type": "international",
      "flight": { "airline": "BR", "flight_no": "BR198", "from": "TPE", "to": "NRT" },
      "price": { "amount": 8500, "currency": "TWD" }
    },
    {
      "leg": 2, "type": "domestic",
      "flight": { "airline": "NH", "flight_no": "NH1395", "from": "NRT", "to": "FKS" },
      "price": {
        "regular": { "amount": 5800, "currency": "TWD" },
        "foreigner_discount": { "amount": 1200, "currency": "TWD", "name": "Experience JAPAN Fare" }
      }
    }
  ],
  "total_price": { "amount": 9700, "currency": "TWD", "note": "含 ANA 外國人優惠" },
  "layover": { "airport": "NRT", "duration_minutes": 180 },
  "tags": ["兩段式", "外國人優惠適用"]
}
```

### 5.4 外部 API 整合

| API | 用途 | 額度 | 認證方式 |
|---|---|---|---|
| **Amadeus** | 主力來源：機票搜尋 + 報價 + Flight Inspiration | 5,000 次/月（免費） | OAuth token |
| **Skyscanner** (RapidAPI: fly-scraper) | 輔助來源：航班搜尋、Anywhere 模式（飯店 API 存在但未驗證） | 50 次/月（免費） | `x-rapidapi-key` + `x-rapidapi-host` |
| **Kiwi** (RapidAPI: flights-scraper) | 輔助來源：航班搜尋、虛擬聯程、特惠搜尋（飯店 API 存在但未驗證） | 120 次/月（免費） | `x-rapidapi-key` + `x-rapidapi-host` |
| **Anthropic Claude** | AI 多代理系統 | 依方案 | API Key |
| **Google OAuth 2.0** | 用戶認證 | 無限 | Client ID + Secret |
| **open.er-api.com** | 匯率轉換 | 無限（免費） | 無需 key |
| **ip-api.com** | IP 偵測幣別 | 45 次/分鐘（免費） | 無需 key |
| **SMTP** | 郵件發送 | 依 SMTP provider | SMTP credentials |

### 5.5 前端頁面

| 頁面 | 路由 | 功能 |
|---|---|---|
| 首頁 | `/` | 搜尋表單 + 登入入口 |
| 搜尋結果 | `/search` | 機票搜尋結果展示、排序、來源標記（飯店暫時停用） |
| 比價 | `/compare` | 多來源價格比較表，標記最低價 |
| 行程管理 | `/trip` | 行程 CRUD + 行程表瀏覽 |
| AI 聊天 | `/chat` | SSE 串流聊天（多 Agent 協作） |
| OAuth 回調 | `/auth/callback` | Google 登入 token 處理 |
| 訂閱管理 | `/settings` | 訂閱偏好設定頁 |

### 5.6 技術堆疊

#### 後端

| 技術 | 版本 | 用途 |
|---|---|---|
| Python | >=3.12 | 執行環境 |
| FastAPI | >=0.115.0 | Web 框架 |
| SQLAlchemy | >=2.0.0 (async) | ORM |
| asyncpg | >=0.30.0 | PostgreSQL 驅動 |
| Alembic | >=1.14.0 | 資料庫遷移 |
| Anthropic SDK | >=0.42.0 | Claude API |
| Authlib | >=1.4.0 | OAuth2 |
| python-jose | >=3.3.0 | JWT |
| FastAPI-Mail | >=1.4.0 | 郵件發送 |
| APScheduler | >=3.10.0 | 任務排程 |
| uv | latest | 套件管理 |
| Ruff | >=0.8.0 | Lint + 格式化 |
| mypy | >=1.13.0 | 型別檢查 |

#### 前端

| 技術 | 版本 | 用途 |
|---|---|---|
| Next.js | ^15.1.0 | React 框架 |
| React | ^19.0.0 | UI |
| Zustand | ^5.0.0 | 狀態管理 |
| Tailwind CSS | ^4.0.0 | 樣式 |
| TypeScript | ^5.7.0 | 型別系統 |
| Vitest | ^2.1.0 | 單元測試 |
| Playwright | ^1.49.0 | E2E 測試 |

#### 基礎設施

| 技術 | 版本 | 用途 |
|---|---|---|
| PostgreSQL | 16-alpine | 資料庫 |
| Redis | 7-alpine | 快取 / Session |
| Docker | multi-stage | 容器化 |

---

## 6. 非功能需求

### 6.1 效能

- 搜尋 API 回應時間 < 10 秒（含多來源並行查詢）
- 任一來源失敗不影響其他來源結果回傳（`return_exceptions=True`）
- 匯率與搜尋並行抓取，不增加延遲
- Redis 快取策略：搜尋結果 30min、價格 1hr、匯率 6hr、IP 幣別 24hr

### 6.2 可靠性

- Monitor daemon 24/7 常駐運行，Docker `restart: always`
- RapidAPI 429 自動 backoff（1 小時）
- Token bucket 速率控制，避免超出 API 配額
- Bug Fare 偵測即時觸發，不受排程降頻影響

### 6.3 安全

- Google OAuth 2.0 認證，無自建密碼系統
- JWT 簽名（HS256），Access token 30min + Refresh token 7d
- Premium 功能守衛（`require_premium` dependency）
- 退訂 token 簽名驗證，防止濫用
- 每用戶每日通知上限，防止濫發
- 等級切換 API 僅限 development/test 環境

### 6.4 可擴展性

- Coordinator Pattern 支援新增代理，無需修改現有代理
- RapidAPI 基礎 client 架構支援快速新增 API 來源
- JSONB 欄位支援不同資料源的彈性 schema
- Docker multi-stage builds 支援 dev/prod 環境切換

### 6.5 關鍵技術決策

| 決策 | 選擇 | 理由 |
|---|---|---|
| 代理模式 | Coordinator（非 Pipeline） | 旅遊查詢非線性，可並行多個代理 |
| 串流協議 | SSE（非 WebSocket） | AI 聊天只需 server→client 單向串流 |
| 彈性資料 | JSONB 欄位 | 不同資料源 schema 不同，核心欄位用 column，其餘 JSONB |
| 狀態管理 | Zustand（非 Redux） | 輕量、少 boilerplate |
| 套件管理 | uv | 速度快、現代 Python 生態 |

---

## 7. 實作路線圖

### Phase 1：基礎架構 -- 已完成

| 里程碑 | 狀態 | 內容 |
|---|---|---|
| 專案骨架 | 已完成 | 目錄結構、pyproject.toml、package.json、Dockerfile（multi-stage）、docker-compose.yml、.env.example |
| 資料庫層 | 已完成 | SQLAlchemy models（11 tables）、Alembic migration（001_initial_schema）、async session factory、Redis client |
| 認證系統 | 已完成 | Google OAuth 2.0（authlib）、JWT 簽發（access 30min + refresh 7d）、用戶等級（Basic/Premium）、tier switch API |
| Docker Compose | 已完成 | 5 services + dev override + prod compose |
| CI/CD | 已完成 | GitHub Actions test.yml + deploy.yml（Railway） |

### Phase 2：AI 代理系統 -- 已完成

| 里程碑 | 狀態 | 內容 |
|---|---|---|
| BaseAgent ABC | 已完成 | Anthropic tool-use agentic loop（max 10 turns） |
| CoordinatorAgent | 已完成 | 意圖解析、代理分派（支援並行）、結果合成 |
| 5 個專職代理 | 已完成 | Search、Price、Recommendation、Itinerary、Budget Agent |
| Chat SSE | 已完成 | SSE 串流聊天端點，透過 CoordinatorAgent |

### Phase 3：外部 API 整合 -- 已完成

| 里程碑 | 狀態 | 內容 |
|---|---|---|
| Amadeus Client | 已完成 | Flight Offers Search + OAuth token 管理 |
| RapidAPI 基礎 Client | 已完成 | 共用 HTTP client + header 管理 + 429 自動 backoff |
| Skyscanner Client | 已完成 | 航班搜尋（one-way / roundtrip / incomplete） |
| Kiwi Client | 已完成 | 航班搜尋（oneway / return） |
| Normalizer | 已完成 | 三來源回應正規化為統一 FlightResult 格式 |
| 匯率轉換 | 已完成 | open.er-api.com + Redis 快取 6h + Amadeus EUR→用戶幣別 |
| IP 偵測幣別 | 已完成 | ip-api.com + Redis 快取 24h |

### Phase 4：多來源 Service 層 + 前後端對齊 -- 已完成

| 里程碑 | 狀態 | 內容 |
|---|---|---|
| SearchService 多來源 | 已完成 | Amadeus + Skyscanner + Kiwi 並行搜尋 + 合併去重 + Redis 快取 |
| PriceService 多來源 | 已完成 | 多來源並行比價 + 統一 Compare 端點 |
| Schema 對齊 | 已完成 | FlightResult、FlightSegment、SearchResponse、CompareResult 對齊前端 types |
| 訂閱系統 | 已完成 | CRUD + Email 驗證 + 退訂 + 通知寄信 |
| 前端頁面 | 已完成 | Landing、Search、Compare、Trip、Chat、Auth Callback、Settings |
| 前端狀態管理 | 已完成 | Zustand stores（search、trip、chat、auth、compare）+ hooks |
| UI/UX 優化 | 已完成 | Dark mode badges、Compare flow（浮動比較列）、Auth state sharing |

### Phase 5：價格監控 Daemon -- 已完成

| 里程碑 | 狀態 | 內容 |
|---|---|---|
| 專案結構 | 已完成 | 獨立 Python service、pyproject.toml、Dockerfile |
| Scheduler | 已完成 | APScheduler 3 個 job（price_scan、deal_digest、cleanup） |
| Anomaly Detector | 已完成 | Bug Fare 偵測演算法 |
| price_scan 任務 | 已完成 | Amadeus + Skyscanner + Kiwi 多來源並行搜尋 → price_history 寫入 → 異常偵測 → 通知 |
| deal_digest 任務 | 已完成 | price_history + Amadeus inspiration → 用戶偏好過濾 → digest 寄信 |
| cleanup 任務 | 已完成 | price_history 180天 + notification_log 90天 清除 |
| Notifier 寄信 | 已完成 | bug_fare + price_drop + deal_digest，含路線過濾、偏好過濾、cooldown |
| Monitor 多來源 | 已完成 | Skyscanner + Kiwi 客戶端 + 多來源交叉驗證 bug fare 偵測 |

### Phase 6：測試覆蓋與 CI -- 已完成

| 里程碑 | 狀態 | 內容 |
|---|---|---|
| Backend 測試 | 已完成 | 105 tests（models、agents、API、services、clients、normalizer、currency） |
| Monitor 測試 | 已完成 | 10+ tests（detector、clients、rate_limiter、RapidAPI clients、normalizer） |
| Frontend 單元測試 | 已完成 | Vitest — auth、compare、search、subscription、preferences stores（57 tests） |
| CI 自動化 | 已完成 | GitHub Actions：backend + monitor + frontend（lint + type-check + unit tests） |
| CI Redis | 已完成 | GitHub Actions Redis 7 service container（backend + monitor jobs） |

### Phase 7：待開發功能

| 里程碑 | 優先級 | 工作量 | 內容 |
|---|---|---|---|
| Production 部署驗證 | 中 | 中 | Railway 端到端驗證（env vars、health check、DB migration、域名設定） |
| Price History DB 連接 | 中 | 小 | PriceAgent._get_price_history() 接上 price_history 資料表，提升 Chat 歷史價格查詢品質 |
| Recommendation DB 連接 | 中 | 小 | RecommendationAgent._get_user_preferences() 接上 user_preferences 資料表，使推薦考慮用戶偏好 |
| Subscription email 寄送 | 中 | 小 | subscription_service.py 的 email sending 從 stub 改為實際寄送 |
| Frontend E2E 測試 | 低 | 大 | Playwright E2E 測試（搜尋→結果→比價→聊天完整流程），MVP 上線非必要 |
| Agent 層整合 Service | 低 | 中 | SearchAgent/PriceAgent 改用 SearchService/PriceService（僅影響 Chat 功能） |
| Caddyfile | 低 | 小 | docker-compose.prod.yml 參考的 TLS 設定（僅 VM 部署需要，Railway 不需要） |
| 部署 Runbook | 低 | 小 | 上線 SOP、環境設定、rollback 流程文件 |
| Incident Playbook | 低 | 小 | 常見問題排查指引（API 配額耗盡、DB 連線失敗、email 寄送失敗等） |
| 飯店搜尋實作 | ⏸️ 暫停 | 大 | SearchService/PriceService hotel 方法——Skyscanner/Kiwi 飯店 API 尚未驗證可用性，待確認後再啟用 |

---

## 8. 驗證與測試策略

### 8.1 測試框架

| 層級 | 框架 | 範圍 |
|---|---|---|
| 後端單元 / 整合 | pytest + pytest-asyncio + httpx | Models、Agents、API、Services、Clients、Normalizer、Currency |
| 監控服務 | pytest | Detector、Clients、Rate Limiter、Tasks |
| 前端單元 | Vitest + @testing-library/react | Zustand stores、Hooks、Components |
| 前端 E2E | Playwright | 搜尋→結果→比價→聊天→行程完整流程 |

### 8.2 Mock 策略

模擬外部 API（Amadeus、Skyscanner、Kiwi）和 Claude API 回應，使用 `respx` mock HTTP 請求。

### 8.3 測試驗證順序

| 步驟 | 測試範圍 | 對應完成項目 |
|---|---|---|
| 1 | models | 資料庫層 |
| 2 | api (auth + tier + preferences) | 認證系統 + 用戶等級 |
| 3 | agents | 代理框架 |
| 4 | services + clients + api (search + compare) | 搜尋功能 |
| 5 | api (chat) + services (chat) | Chat SSE |
| 6 | api (subscriptions) + services (subscription + notification + email) | 訂閱系統 |
| 7 | monitor | 價格監控 Daemon |
| 8 | frontend + e2e | 前端 |

### 8.4 整合驗證

1. `docker compose up` 可啟動所有 5 個服務
2. 所有自動化測試通過
3. 前端 `http://localhost:3000` 可正常操作
4. 搜尋結果包含多來源（amadeus、skyscanner、kiwi）

---

## 9. 部署策略

### 9.1 Railway（主要）

每個服務有 `railway.toml`，使用 Dockerfile builder。CI/CD 透過 GitHub Actions：

- `test.yml`：所有 push/PR 觸發 — lint + type-check + pytest（含 PostgreSQL service container）
- `deploy.yml`：push 到 `main` 觸發 — 先測試，再並行部署 backend/frontend/monitor

所需 GitHub Secret：`RAILWAY_TOKEN`

### 9.2 VM + Caddy（替代方案）

使用 `docker-compose.prod.yml`，包含 Caddy 反向代理自動 HTTPS。適用於不使用 Railway 的 VM 部署。

### 9.3 環境變數策略

| 變數 | 開發環境（.env） | Railway（dashboard） |
|---|---|---|
| `ENV` | `development` | `production` |
| `DEBUG` | `true` | `false` |
| `DATABASE_URL` | `...@db:5432/travelai` | Railway PostgreSQL URL |
| `REDIS_URL` | `redis://redis:6379/0` | Railway Redis URL |
| `FRONTEND_URL` | `http://localhost:3000` | `https://<frontend>.up.railway.app` |
| `BACKEND_URL` | `http://localhost:8000` | `https://<backend>.up.railway.app` |
| `GOOGLE_REDIRECT_URI` | `localhost:8000/...` | `<backend>.up.railway.app/...` |
| `ALLOW_TIER_SWITCH` | `true` | `false` |
| `NEXT_PUBLIC_API_URL` | 未設定（Docker DNS fallback） | `https://<backend>.up.railway.app` |

### 9.4 Docker Build Targets

| 服務 | Development | Production |
|---|---|---|
| backend | `uvicorn --reload` | `uvicorn --workers 4` |
| frontend | `npm run dev` | `npm start`（production build） |
| monitor | `python -m app.main` | `python -m app.main` |

---

## 10. 附錄：API 整合詳細規格

### A.1 Skyscanner (Fly Scraper) API

**Host**: `fly-scraper.p.rapidapi.com`

#### 航班搜尋端點

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/flights/autocomplete` | GET | 機場/城市自動完成 | `query` |
| `/v2/flights/search-one-way` | GET | 單程搜尋 | `originSkyId` |
| `/v2/flights/search-roundtrip` | GET | 來回搜尋 | `originSkyId` |
| `/v2/flights/search-multi-city` | POST | 多城市搜尋 | `flights` (array) |
| `/v2/flights/search-incomplete` | GET | 取得完整結果 | `sessionId` |
| `/flights/search-detail` | POST | 航班詳情 + booking deeplink | `sessionId`, `itineraryId` |
| `/flights/price-calendar` | GET | 價格日曆（單程） | `originSkyId`, `destinationSkyId`, `fromDate` |
| `/flights/price-calendar-return` | GET | 價格日曆（來回） | `originSkyId`, `destinationSkyId`, `fromDate` |
| `/1.0/flights/search-roundtrip` | GET | Anywhere 模式（探索所有目的地） | `originSkyId` |

#### 飯店搜尋端點

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/hotels/autocomplete` | GET | 地點搜尋 | `query` |
| `/hotels/search` | GET | 飯店搜尋 | `entityId`, `checkin`, `checkout` |
| `/hotels/detail` | GET | 飯店詳情 | `hotelId` |
| `/hotels/detail/price` | GET | 價格 | `hotelId`, `entityId`, `checkin`, `checkout` |
| `/hotels/detail/reviews` | GET | 評論 | `hotelId` |
| `/hotels/detail/similarhotels` | GET | 類似飯店 | `hotelId`, `checkin`, `checkout` |

#### 共用參數

| 參數 | 說明 | Travel-AI 預設值 |
|---|---|---|
| `originSkyId` | 出發地 Sky ID | — |
| `destinationSkyId` | 目的地 Sky ID | — |
| `departureDate` / `returnDate` | 日期 `YYYY-MM-DD` | — |
| `adults` | 成人人數 | `1` |
| `currency` | 貨幣代碼 | `TWD` |
| `market` | 市場 | `TW` |
| `locale` | 語言 | `zh-TW` |
| `cabinClass` | 艙等 | `economy` |
| `sort` | 排序 | `best` |
| `stops` | 轉機篩選 | 不限 |

#### 回應格式特殊說明

- **價格單位**：`price.raw` 為 milli 單位，實際價格 = `raw / 1000`（例：`7121000` → NT$7,121）
- **incomplete 結果**：首次搜尋回傳 `context.status = "incomplete"`，可用 `sessionId` 呼叫 `search-incomplete` 取得更多結果

#### 回應結構範例

**autocomplete**：
```json
{
  "status": true,
  "data": [{
    "presentation": { "title": "Taipei Taiwan Taoyuan", "suggestionTitle": "...(TPE)", "subtitle": "Taiwan" },
    "navigation": {
      "entityId": "128667054", "entityType": "AIRPORT",
      "relevantFlightParams": { "skyId": "TPE", "entityId": "128667054", "flightPlaceType": "AIRPORT" }
    },
    "skyId": "TPE"
  }]
}
```

**search-one-way / search-roundtrip**：
```json
{
  "status": true,
  "data": {
    "context": { "sessionId": "...", "status": "incomplete|complete" },
    "itineraries": [{
      "id": "...",
      "price": { "formatted": "NT$7,121", "raw": "7121000", "unit": "PRICE_UNIT_MILLI" },
      "legs": [{
        "originPlaceId": "128667054",
        "destinationPlaceId": "128668889",
        "departureDateTime": { "year": 2026, "month": 4, "day": 1, "hour": 2, "minute": 40, "second": 0 },
        "arrivalDateTime": { "year": 2026, "month": 4, "day": 1, "hour": 10, "minute": 5, "second": 0 },
        "durationInMinutes": 385,
        "stopCount": 1,
        "segments": [{
          "marketingFlightNumber": "752",
          "durationInMinutes": 155,
          "carriers": {
            "marketing": { "name": "金航", "iata": "LJ", "imageUrl": "https://logos.skyscnr.com/images/airlines/LJ.png" },
            "operating": { "name": "金航", "iata": "LJ" }
          }
        }]
      }],
      "pricingOptions": [{ "price": { "formatted": "NT$7,142" }, "items": [{ "deepLink": "https://..." }] }]
    }],
    "filterStats": {
      "carriers": [{ "name": "...", "minPrice": "..." }],
      "stopPrices": { "direct": "...", "one": "...", "two_or_more": "..." }
    }
  }
}
```

---

### A.2 Kiwi (Flights Scraper Real-Time) API

**Host**: `flights-scraper-real-time.p.rapidapi.com`

#### 航班搜尋端點

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/flights/auto-complete` | GET | 機場/城市自動完成 | `query` |
| `/airports` | GET | 機場查詢 | `name` |
| `/airlines` | GET | 航空公司查詢 | `name` |
| `/configs` | GET | locale/market/currency | `name` |
| `/flights/search-oneway` | GET | 單程搜尋 | `originSkyId`, `destinationSkyId` |
| `/flights/search-return` | GET | 來回搜尋 | `originSkyId`, `destinationSkyId` |
| `/flights/price-table` | GET | 價格表（日期矩陣） | `originSkyId`, `destinationSkyId` |
| `/flights/price-trends` | GET | 價格趨勢 | `originSkyId`, `destinationSkyId` |
| `/flights/seat-info` | GET | 座位資訊 | `originSkyId`, `destinationSkyId`, `carrier`, `code` |
| `/deals/auto-complete` | GET | 特惠自動完成 | `query` |
| `/deals/search` | GET | 特惠搜尋 | `query` |

#### 飯店搜尋端點

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/stays/autocomplete` | GET | 地點搜尋 | `location` |
| `/stays/search/by-dest` | GET | 依目的地 | `dest_id`, `dest_type` |
| `/stays/search/by-coordinates` | GET | 依座標 | `latitude`, `longitude` |
| `/stays/search/by-coordinates-bounding` | GET | 依邊界框 | `ne_lat`, `ne_lon`, `sw_lat`, `sw_lon` |
| `/stays/get-detail` | GET | 飯店詳情 | `hotel_id` |
| `/stays/detail/rooms` | GET | 房型 | `hotel_id` |
| `/stays/detail/description` | GET | 描述 | `hotel_id` |
| `/stays/detail/review` | GET | 評論 | `hotel_id` |
| `/stays/detail/photos` | GET | 照片 | `hotel_id` |
| `/stays/detail/facilities` | GET | 設施 | `hotel_id` |
| `/stays/detail/availability-calendar` | GET | 可用日曆 | `hotel_id` |

#### Kiwi 獨有進階參數

| 參數 | 說明 | 預設值 |
|---|---|---|
| `cabinClass` | `ECONOMY` / `PREMIUM_ECONOMY` / `BUSINESS` / `FIRST` | `ECONOMY` |
| `sort` | `QUALITY` / `PRICE` / `FASTEST` / `OUTBOUND_DEPARTURE_TIME` | `QUALITY` |
| `stops` | `0`=直飛 / `1`=最多1轉 / `2`=最多2轉 | `0` |
| `limit` | 回傳數量上限 | `20` |
| `departureDateEnd` | 最晚出發日（彈性日期範圍） | — |
| `hiddenCity` | 隱藏城市票 | `true` |
| `throwAwayTicketing` | 棄票優化 | `true` |
| `selfTransfer` | 自行轉機（虛擬聯程） | `true` |
| `allowOvernightStopovers` | 允許過夜轉機 | `true` |

#### 回應格式特殊說明

- **價格單位**：`price.amount` 為整數字串，單位即為指定 `currency`（例：`"6790"` = TWD 6,790）
- **獨有資料**：`bagsInfo`（行李）、`bookingOptions`（多訂票來源）、`travelHack` / `hiddenCity` / `throwAwayTicketing`（特殊票價策略）、`pnrCount`（>1 表示虛擬聯程）

#### 回應結構範例

**auto-complete**：
```json
{
  "data": {
    "metadata": {
      "firstResultStations": {
        "edges": [{
          "node": {
            "id": "Station:airport:TPE",
            "legacyId": "TPE",
            "name": "Taiwan Taoyuan International",
            "type": "AIRPORT",
            "code": "TPE",
            "gps": { "lat": 25.0777778, "lng": 121.232778 },
            "city": { "legacyId": "taipei_tw", "name": "Taipei",
              "country": { "legacyId": "TW", "name": "Taiwan" }
            }
          }
        }]
      }
    }
  }
}
```

**search-oneway / search-return**：
```json
{
  "status": true,
  "data": {
    "itineraries": [{
      "id": "...",
      "price": { "amount": "6790", "priceBeforeDiscount": "6790" },
      "duration": 21000,
      "sector": {
        "duration": 21000,
        "sectorSegments": [{
          "segment": {
            "source": {
              "station": { "code": "TPE", "name": "臺灣桃園國際機場", "type": "AIRPORT",
                "city": { "name": "台北" }, "country": { "code": "TW" }
              },
              "localTime": "2026-04-01T02:50:00"
            },
            "destination": {
              "station": { "code": "NRT", "name": "成田國際機場", "type": "AIRPORT",
                "city": { "name": "東京" }, "country": { "code": "JP" }
              },
              "localTime": "2026-04-01T10:15:00"
            },
            "duration": 8400,
            "code": "6154",
            "carrier": { "name": "Jeju Air", "code": "7C" },
            "operatingCarrier": { "name": "Jeju Air", "code": "7C" },
            "cabinClass": "ECONOMY"
          },
          "layover": null
        }]
      },
      "bagsInfo": { "..." },
      "bookingOptions": [{ "edges": [{ "node": { "bookingUrl": "https://...", "price": { "amount": "6790" } } }] }]
    }]
  }
}
```

---

### A.3 兩 API 比較

| 面向 | Skyscanner (fly-scraper) | Kiwi (flights-scraper) |
|---|---|---|
| **航班搜尋** | v2 端點，快速回傳 | 進階篩選（彈性日期、時段、轉機時間） |
| **價格單位** | milli（÷1000） | 直接整數（原幣值） |
| **地點識別** | `skyId` + `entityId` | `skyId`（相容） |
| **分段搜尋** | `search-incomplete` + `sessionId` | 一次回傳（用 `limit` 控制） |
| **多城市** | `search-multi-city` (POST) | 無（只有單程+來回） |
| **獨有功能** | 價格日曆、Anywhere 搜尋 | 隱藏城市票、棄票優化、虛擬聯程、特惠搜尋、價格趨勢 |
| **飯店** | 基本搜尋+詳情 | 完整搜尋+篩選+排序+房型+評論+照片 |
| **租車** | 基本搜尋 | 搜尋+詳情+價格明細 |
| **行李資訊** | 無 | 有（bagsInfo） |
| **booking URL** | deepLink（在 pricingOptions 內） | bookingUrl（在 bookingOptions 內） |

### A.4 常見航空公司 IATA 代碼

| 代碼 | 航空公司 | 聯盟 |
|---|---|---|
| NH | ANA 全日空 | Star Alliance |
| BR | EVA Air 長榮 | Star Alliance |
| JX | StarLux 星宇 | — |
| CI | China Airlines 華航 | SkyTeam |
| CX | Cathay Pacific 國泰 | oneworld |
| JL | JAL 日本航空 | oneworld |
| SQ | Singapore Airlines 新航 | Star Alliance |
| TG | Thai Airways 泰航 | Star Alliance |
