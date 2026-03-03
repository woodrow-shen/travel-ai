# Travel-AI 產品設計計畫

## 實作進度總覽

> 最後更新：2026-03-03

### 一、基礎架構

- [x] 專案骨架：目錄結構、pyproject.toml、package.json、Dockerfile（multi-stage）、docker-compose.yml、.env.example
- [x] 資料庫層：SQLAlchemy models（11 tables）、Alembic migration（001_initial_schema）、async session factory、Redis client
- [x] 認證系統：Google OAuth 2.0（authlib）、JWT 簽發（access 30min + refresh 7d）、用戶等級（Basic/Premium）、tier switch API
- [x] Docker Compose：5 services（backend, frontend, monitor, db, redis）+ dev override + prod compose
- [x] CI/CD：GitHub Actions test.yml（lint + pytest + PostgreSQL service container）+ deploy.yml（Railway）
- [x] Railway 部署配置：backend/frontend/monitor railway.toml

### 二、AI 代理系統

- [x] BaseAgent ABC：Anthropic tool-use agentic loop（max 10 turns）
- [x] CoordinatorAgent：意圖解析、代理分派（支援並行執行）、結果合成
- [x] SearchAgent：機票搜尋工具（search_flights）
- [x] PriceAgent：多源比價工具（compare_prices）
- [x] RecommendationAgent：航空公司評等、品質評分工具
- [x] ItineraryAgent：日程行程規劃、最近鄰 TSP 路線優化
- [x] BudgetAgent：每國每日預算估算（TWD）
- [ ] Agent 層整合 SearchService（Phase 4）— SearchAgent/PriceAgent 直接呼叫 API client，尚未透過 SearchService/PriceService（**已降優先級，Chat 為次要功能**）

### 三、外部 API 整合

- [x] Amadeus Client：Flight Offers Search + OAuth token 管理
- [x] RapidAPI Base Client：共用 HTTP client + header 管理
- [x] Skyscanner Client（fly-scraper）：航班搜尋（one-way / roundtrip / incomplete）
- [x] Kiwi Client（flights-scraper）：航班搜尋（oneway / return）
- [x] Normalizer：三來源回應正規化為統一 FlightResult 格式
- [x] 匯率轉換：open.er-api.com 取得匯率、Redis 快取 6h、Amadeus EUR→用戶幣別自動轉換
- [x] IP 偵測幣別：ip-api.com + Redis 快取 24h → `GET /geo/currency`
- [ ] Skyscanner 飯店搜尋整合（Phase 6）
- [ ] Kiwi 飯店搜尋整合（Phase 6）
- [ ] Google Flights Client（RapidAPI）— 尚未實作

### 四、後端 Service 層

- [x] SearchService：多來源並行搜尋（Amadeus + Skyscanner + Kiwi）+ 合併去重 + 匯率轉換
- [x] PriceService：多來源並行比價 + 匯率轉換
- [x] TripService：Trip CRUD
- [x] ItineraryService：行程生成（透過 Agent）
- [x] ChatService：SSE 串流聊天（透過 CoordinatorAgent）
- [x] SubscriptionService：訂閱 CRUD + Email 管理
- [ ] SubscriptionService 實際寄信功能（stub）
- [ ] NotificationService：觸發條件判斷 + 寄信（stub）
- [ ] PriceAgent._get_price_history()：未連接 DB
- [ ] RecommendationAgent._get_user_preferences()：未查詢 DB

### 五、後端 API 端點

- [x] Health：`GET /health`
- [x] Auth：Google OAuth、JWT refresh、me、tier switch、logout
- [x] Geo：`GET /geo/currency`（IP 偵測幣別）
- [x] Search：flights、hotels（stub）、direct（Premium）、adventure
- [x] Compare：flights、hotels（stub）
- [x] Trips：CRUD
- [x] Itineraries：POST
- [x] Chat：POST（SSE 串流）
- [x] Subscriptions：CRUD + emails + verify + unsubscribe
- [x] Users：preferences GET/PATCH

### 六、前端

- [x] 頁面：Landing（/）、Search（/search）、Compare（/compare）、Trip（/trip）、Chat（/chat）、Auth Callback（/auth/callback）
- [x] Zustand stores：search、trip、chat（使用穩定 selector 模式）
- [x] Hooks：useAuth、useSearch、useChat（SSE）、useTrip、useCompare
- [x] API Client：RESTful + SSE 串流
- [x] Next.js API Proxy：/api/* → backend:8000/api/v1/*（可配置 NEXT_PUBLIC_API_URL）
- [ ] 飯店搜尋結果 UI（格式待對齊）
- [ ] 單元測試（Vitest）— 尚未撰寫
- [ ] E2E 測試（Playwright）— 尚未撰寫
- [ ] UI/UX 優化 — 待 review

### 七、價格監控 Daemon（Monitor）

- [x] 專案結構：獨立 Python service、pyproject.toml、Dockerfile
- [x] Scheduler：APScheduler 3 個 job 定義（price_scan、deal_digest、cleanup）
- [x] Anomaly Detector：Bug Fare 偵測演算法（歷史均價 + 標準差 + 多來源交叉驗證）
- [x] Amadeus Client：航班搜尋（rate-limited）
- [x] Rate Limiter：Token bucket 速率控制
- [ ] price_scan 任務實作（stub）
- [ ] deal_digest 任務實作（stub）
- [ ] cleanup 任務實作（stub）
- [ ] Notifier 實際寄信（stub）
- [ ] Monitor Skyscanner/Kiwi 客戶端（Phase 5）

### 八、測試

- [x] Backend：105 tests passing（models、agents、API、services、clients、normalizer、currency）
- [x] Monitor：10 tests passing（detector、clients、rate_limiter）
- [x] CI：GitHub Actions 自動執行 backend + monitor 測試
- [ ] Frontend 單元測試
- [ ] Frontend E2E 測試
- [ ] CI 中尚未啟用 Redis service

### 九、RapidAPI 整合階段

- [x] **Phase 1**：Config + RapidAPIBaseClient + SkyscannerClient（航班搜尋）
- [x] **Phase 2**：KiwiClient + normalizer + 88 unit tests
- [x] **Phase 3**：schemas 對齊 frontend + 多來源 SearchService/PriceService + 統一 Compare 端點 + Redis 快取
- [ ] **Phase 4**：Agent 層整合（SearchAgent/PriceAgent 使用多來源 Service）— **已降優先級**
- [ ] **Phase 5**：Monitor 客戶端 + price_scan 多來源 — **下一優先**
- [ ] **Phase 6**：飯店搜尋整合（Skyscanner + Kiwi hotels）

### 十、待辦事項優先排序

| 優先級 | 項目 | 說明 |
|---|---|---|
| **高** | Phase 5：Monitor 多來源 | Monitor 加入 Skyscanner + Kiwi，price_scan 實作 |
| **高** | 飯店搜尋 | SearchAgent/Service/API hotel 方法從 stub 變為實作 |
| **中** | 前端 UI/UX 優化 | 待 review 後決定改進方向 |
| **中** | 前端測試 | Vitest 單元 + Playwright E2E |
| **低** | Phase 4：Agent 層整合 | Chat 為次要功能，暫不急 |
| **低** | 通知寄信 | SubscriptionService + Monitor Notifier 實際寄信 |
| **低** | Price History DB 連接 | PriceAgent._get_price_history() 接 DB |
| **低** | Recommendation DB 連接 | RecommendationAgent._get_user_preferences() 接 DB |
| **低** | Caddyfile | docker-compose.prod.yml 參考但尚未建立 |

---

## Context

Travel-AI 是一個全新的智能旅遊聚合平台，透過多代理 AI 系統聚合、比較旅遊選項（機票、飯店、活動），並提供 AI 驅動的個人化推薦與行程規劃。目前專案只有 LICENSE 和基礎配置，需要從零開始建構。

**技術選型**：Python FastAPI + Next.js + Multi-Agent (Claude API) + Docker Compose

---

## 1. 多代理架構（Coordinator Pattern）

```
                    Coordinator Agent（協調者）
                           |
          +--------+-------+-------+--------+
          |        |       |       |        |
       Search   Price   Recommend  Itinerary  Budget
       Agent    Agent    Agent     Agent      Agent
```

- **Coordinator Agent**：接收用戶查詢 → 解析意圖 → 分派子代理（可並行） → 合成結果
- **Search Agent**：搜尋機票/飯店/活動，工具：`search_flights`, `search_hotels`, `search_activities`
- **Price Agent**：多源比價分析，工具：`compare_prices`, `get_price_history`
- **Recommendation Agent**：個人化推薦，工具：`get_user_preferences`, `analyze_reviews`
- **Itinerary Agent**：生成日程行程，工具：`create_itinerary`, `optimize_route`
- **Budget Agent**：預算規劃與替代方案，工具：`estimate_costs`, `find_alternatives`

所有代理繼承 `BaseAgent` ABC，使用 Anthropic SDK 的 tool_use 模式。

---

## 2. 專案結構

```
travel-ai/
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml                # uv/poetry
│   ├── alembic.ini + alembic/        # DB migrations
│   └── app/
│       ├── main.py                   # FastAPI app factory
│       ├── config.py                 # pydantic-settings
│       ├── api/v1/                   # search, trips, compare, itinerary, chat, auth
│       ├── agents/                   # base, coordinator, 5 specialist agents
│       │   └── tools/                # flight_tools, hotel_tools, etc.
│       ├── services/                 # search, price, trip, itinerary, user
│       ├── clients/                 # amadeus, rapidapi (google_flights, skyscanner, kiwi)
│       ├── models/                   # SQLAlchemy ORM (user, trip, flight, hotel, etc.)
│       ├── schemas/                  # Pydantic request/response
│       └── db/                       # session.py, redis.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── app/                      # Next.js App Router (search, compare, trip, chat)
│       ├── components/               # ui, search, compare, itinerary, chat, layout
│       ├── hooks/                    # useSearch, useChat (SSE), useTrip, useCompare
│       ├── stores/                   # Zustand (search, trip, chat)
│       ├── lib/                      # API client, utils
│       └── types/
├── docker-compose.yml                # backend, frontend, postgres, redis
├── docker-compose.override.yml       # dev overrides (hot reload)
└── .env.example
```

---

## 3. MVP 功能範圍（Phase 1）

| 功能 | 說明 |
|---|---|
| AI 對話介面 | SSE 串流聊天，用戶用自然語言描述需求 |
| 機票搜尋 | 多來源聚合（Amadeus + RapidAPI：Google Flights、Skyscanner、Kiwi） |
| 飯店搜尋 | 多來源聚合（Amadeus + RapidAPI） |
| 基本比價 | 跨來源價格比較、排序、篩選 |
| 行程生成 | AI 生成日程安排 |
| 用戶認證 | Google OAuth 2.0 登入，JWT session 管理 |
| 行程儲存 | Trip CRUD |
| 郵件訂閱 | 訂閱價格提醒、Bug Fare 通知，支援 Gmail 或自訂 Email |
| 直達模式 | 指定日期+目的地，推薦最佳直飛航班（Premium 限定） |
| 冒險模式 | 只給日期，探索任意目的地最便宜的前 10 航班 |

---

## 4. 核心 API 端點

```
GET    /api/v1/auth/google             # 導向 Google OAuth 授權頁
GET    /api/v1/auth/google/callback    # Google OAuth 回呼，建立/更新用戶，回傳 JWT
POST   /api/v1/auth/refresh            # 刷新 JWT
GET    /api/v1/auth/me                 # 取得當前用戶資料
POST   /api/v1/auth/logout             # 登出（清除 token）
POST   /api/v1/search/flights|hotels
POST   /api/v1/compare/flights|hotels
CRUD   /api/v1/trips
POST   /api/v1/itineraries
POST   /api/v1/chat                    # SSE 串流回應
```

Chat 端點使用 SSE，事件類型：`text`（AI 文字）、`data`（結構化資料如搜尋結果）、`done`（結束）。

### 認證流程（Google OAuth 2.0）

```
用戶點擊「Sign in with Google」
    |
    v
前端導向 GET /api/v1/auth/google
    |
    v
後端 redirect → Google OAuth 授權頁
    |
    v
用戶授權 → Google callback → GET /api/v1/auth/google/callback
    |
    v
後端用 authorization code 換取 Google token
    → 取得用戶資料（email, name, avatar）
    → 資料庫：找到就更新，找不到就建立新用戶
    → 簽發 JWT（access_token + refresh_token）
    → redirect 回前端，帶上 token
```

- **後端套件**：`authlib`（OAuth client）
- **用戶模型**：只需 `id`, `email`, `name`, `avatar_url`, `google_id`, `created_at`, `last_login`
- **不需要**：密碼欄位、register 端點、email 驗證
- **前端**：Next.js 中用 cookie 或 localStorage 存 JWT，請求帶 `Authorization: Bearer <token>`

---

## 5. 用戶等級與直達模式

### 用戶等級

| 等級 | 標識 | 功能權限 |
|---|---|---|
| **Basic** | 預設（Google 登入即取得） | 搜尋、比價、AI 聊天、訂閱（基本額度） |
| **Premium** | 手動升級 / 測試帳號切換 | Basic 全部 + 直達模式、進階推薦、更高訂閱額度 |

```
users 表新增欄位：
  tier (enum: basic / premium), default: basic
  tier_updated_at (timestamp)
```

### 測試帳號切換機制

開發/測試環境提供 API 切換用戶等級，方便測試不同權限行為：

```
# 僅限 development/test 環境（production 中停用）
PATCH  /api/v1/auth/me/tier            # 切換當前用戶等級
  Body: { "tier": "premium" }          # 或 "basic"
  Response: { "tier": "premium", "updated_at": "..." }
```

**實作方式**：
- 後端 `config.py` 中 `ALLOW_TIER_SWITCH: bool`，僅 `ENV=development|test` 時為 `True`
- API 端點加 guard：`if not settings.ALLOW_TIER_SWITCH: raise 403`
- 前端開發模式顯示「切換等級」按鈕（dev toolbar）
- 測試中可直接呼叫 API 切換，驗證 Basic vs Premium 行為差異

**權限守衛 Dependency**：
```python
# backend/app/dependencies.py
async def require_premium(user: User = Depends(get_current_user)):
    if user.tier != "premium":
        raise HTTPException(403, "此功能需要 Premium 帳戶")
    return user
```

### 直達模式（Premium 限定）

用戶只需指定「日期區間 + 目的地」，系統自動列出最推薦的直飛航班，不以價格為首要排序。

**輸入**：
```
POST   /api/v1/search/direct           # Premium 限定
  Body: {
    "origin": "TPE",                   # 或從 user_preferences.home_airports 取
    "destination": "NRT",
    "date_from": "2026-04-01",
    "date_to": "2026-04-10",
    "passengers": 1,
    "cabin_class": "economy"           # optional
  }
```

**推薦排序邏輯**（不以價格為主）：
1. **直飛篩選**：`max_stops = 0`，只保留直飛結果
2. **綜合評分排序**：
   - 航空公司評價（Skytrax 評等、用戶偏好航空加分）
   - 時段合理性（避免紅眼、優先上午/下午出發）
   - 飛行時間（同航線選最短）
   - 機型舒適度（寬體機加分）
   - 價格（作為次要參考，非主要排序）

**回應格式**：
```json
{
  "recommendations": [
    {
      "rank": 1,
      "score": 92,
      "flight": { "airline": "NH", "flight_no": "NH852", ... },
      "reasons": ["偏好航空 ANA", "上午出發", "787 寬體機", "飛行時間最短"],
      "price": { "amount": 15200, "currency": "TWD" }
    }
  ],
  "total_direct_flights": 8
}
```

**對應 Agent**：由 **Search Agent** 搜尋直飛 + **Recommendation Agent** 評分排序，Coordinator 合成結果。

### 多段銜接搜尋（國際線 + 國內線）

當目的地非首都或一線城市（無直飛/國際航班），Search Agent 自動拆解為「國際航班 + 國內線轉機」兩段式搜尋。特別針對日本等國內線發達的國家。

**觸發邏輯**：
```
1. 用戶搜尋 TPE → FKS（福島）
2. Search Agent 查詢直飛/國際航班 → 無結果或極少
3. 觸發多段銜接模式：
   a. 識別目的地所屬國家的主要國際機場（gateway hub）
   b. 搜尋 國際段：TPE → NRT/HND（東京）
   c. 搜尋 國內段：NRT/HND → FKS
   d. 組合最佳銜接方案（考慮轉機時間、總價、總時長）
```

**Gateway Hub 對應表**（初期支援）：

| 國家 | Gateway Hubs | 國內線覆蓋 |
|---|---|---|
| 日本 | NRT, HND, KIX, NGO | ANA/JAL 國內線網絡（200+ 航點） |
| 韓國 | ICN, GMP | 大韓/韓亞國內線 |
| 泰國 | BKK, DMK | Thai Airways/Nok Air 國內線 |
| 印尼 | CGK | Garuda/Lion Air 國內線 |

**日本特殊優惠整合**：

日本的 ANA 和 JAL 提供外國人專屬國內線優惠票價，價格遠低於一般票價：

| 航空 | 優惠名稱 | 單程價格 | 備註 |
|---|---|---|---|
| ANA | Experience JAPAN Fare | ~¥5,500 (~TWD 1,200) | 需持外國護照，國際線搭配 |
| JAL | Japan Explorer Pass | ~¥5,500 (~TWD 1,200) | 需持外國護照，國際線搭配 |

- Search Agent 搜尋國內段時，優先標註是否適用外國人優惠票價
- 在結果中顯示「一般票價」vs「外國人優惠票價」兩種價格
- 提示用戶優惠票價的購買條件（需搭配國際線、護照限制等）

**銜接方案排序邏輯**：
1. 總價（國際段 + 國內段，國內段以優惠票價計）
2. 轉機時間合理性（最短 2 小時，最長 6 小時，避免過夜）
3. 同機場轉機優先（NRT→NRT > NRT→HND）
4. 國內段時段（避免紅眼）

**回應格式**：
```json
{
  "type": "multi_segment",
  "segments": [
    {
      "leg": 1,
      "type": "international",
      "flight": { "airline": "BR", "flight_no": "BR198", "from": "TPE", "to": "NRT", ... },
      "price": { "amount": 8500, "currency": "TWD" }
    },
    {
      "leg": 2,
      "type": "domestic",
      "flight": { "airline": "NH", "flight_no": "NH1395", "from": "NRT", "to": "FKS", ... },
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

**Search Agent 工具新增**：
- `search_domestic_flights` — 搜尋國內線航班（含外國人優惠標註）
- `resolve_gateway_hubs` — 根據目的地國家解析 gateway hub 機場
- `combine_segments` — 組合國際+國內段，計算銜接時間與總價

### 冒險模式（Adventure Mode）

用戶只提供日期區間，系統從出發地搜尋全球任意目的地，列出最便宜的前 10 個目的地航班。適合「想出去玩但不知道去哪」的用戶。

**輸入**：
```
POST   /api/v1/search/adventure
  Body: {
    "origin": "TPE",                   # 或從 user_preferences.home_airports 取
    "date_from": "2026-04-01",
    "date_to": "2026-04-10",
    "passengers": 1,
    "cabin_class": "economy"           # optional
  }
```

**搜尋策略**：
1. Amadeus 的 Flight Inspiration Search API（根據出發地推薦最低價目的地）
2. RapidAPI 來源（Google Flights、Skyscanner、Kiwi）補充更多目的地選項
3. 合併多來源結果 → 去重 → 按價格排序 → 取前 10

**回應格式**：
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
    },
    ...
  ],
  "search_coverage": "搜尋了 150+ 目的地",
  "origin": "TPE"
}
```

**用戶偏好整合**：
- 若有設定偏好航空公司 → 結果中標註偏好航空的航班
- 若有排除航空公司 → 自動過濾
- 艙等/轉機偏好照常套用

**對應 Agent**：由 **Search Agent** 執行廣域搜尋，Coordinator 直接回傳排序結果（不需 Recommendation Agent，因為排序邏輯純粹以價格為主）。

---

## 6. 郵件訂閱系統（Mailing List）

### 訂閱類型

| 類型 | 說明 | 觸發條件 |
|---|---|---|
| **Bug Fare Alert** | 異常低價機票通知（錯誤票價、閃促） | 價格監控偵測到價格低於歷史均價 50%+ |
| **Price Drop Alert** | 自訂路線的價格下降通知 | 監控路線價格低於用戶設定的閾值 |
| **Deal Digest** | 每日/每週最划算的機票/飯店精選 | 定時排程（用戶選擇頻率） |

### 訂閱流程

```
用戶設定訂閱
    |
    ├─ 使用登入的 Gmail（預設）
    └─ 或指定其他 Email 地址（需驗證）
    |
    v
選擇訂閱類型 + 偏好設定
    - Bug Fare：選擇出發地、目的地（可多選或「任意」）
    - Price Drop：指定路線 + 目標價格
    - Deal Digest：選擇頻率（每日/每週）+ 偏好目的地
    |
    v
儲存至 DB → 背景任務持續監控 → 條件觸發時寄送 Email
```

### 用戶偏好設定

用戶可設定個人化篩選條件，所有訂閱通知會根據偏好過濾：

| 偏好類型 | 說明 | 範例 |
|---|---|---|
| **偏好航空公司** | 只通知特定航空公司的機票 | ANA, EVA Air, StarLux, China Airlines |
| **排除航空公司** | 排除不想搭的航空公司 | 特定廉航 |
| **偏好聯盟** | 按航空聯盟篩選（累積里程） | Star Alliance, SkyTeam, oneworld |
| **艙等偏好** | 只通知特定艙等 | 經濟艙、商務艙、頭等艙 |
| **轉機偏好** | 直飛 / 最多1轉 / 不限 | 直飛優先 |
| **出發地** | 預設出發機場 | TPE, TSA, KHH |

```
API: PATCH /api/v1/users/preferences
Body: {
  "preferred_airlines": ["NH", "BR", "JX", "CI"],   # IATA codes
  "excluded_airlines": ["XX"],
  "preferred_alliances": ["star_alliance"],
  "cabin_classes": ["economy", "business"],
  "max_stops": 1,
  "home_airports": ["TPE"]
}
```

**偏好如何作用於各訂閱類型**：
- **Bug Fare Alert**：只通知偏好航空公司的 Bug Fare（或全部，若未設定）
- **Price Drop Alert**：在自訂路線基礎上再用航空公司篩選
- **Deal Digest**：精選摘要依偏好排序，偏好航空置頂

**常見航空公司 IATA 代碼參考**：
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

### Email 地址管理
- **登入 Gmail**：直接可用，無需驗證
- **自訂 Email**：發送驗證信，點擊連結確認後啟用
- 每個用戶最多可設定 3 個接收 Email
- 每個 Email 可獨立管理訂閱偏好
- Email 底部附退訂連結（一鍵退訂）

### API 端點

```
GET    /api/v1/subscriptions                  # 列出用戶所有訂閱
POST   /api/v1/subscriptions                  # 建立新訂閱
PATCH  /api/v1/subscriptions/{id}             # 更新訂閱偏好
DELETE /api/v1/subscriptions/{id}             # 取消訂閱
POST   /api/v1/subscriptions/emails           # 新增接收 Email（觸發驗證信）
GET    /api/v1/subscriptions/emails/verify    # 驗證 Email（from 驗證連結）
GET    /api/v1/subscriptions/unsubscribe      # 一鍵退訂（from Email 連結，無需登入）
```

### 技術實作
- **郵件發送**：`FastAPI-Mail`（基於 `aiosmtplib`），使用 SMTP 或 SendGrid/AWS SES
- **背景任務**：`APScheduler` 排程檢查價格 + 觸發通知
- **Email 模板**：HTML 模板（`Jinja2`），包含機票資訊、價格比較、直接連結
- **防濫用**：每用戶每日通知上限、頻率限制、退訂 token 簽名驗證

### 資料模型

```
subscription_emails
  id, user_id (FK), email, is_verified, verified_at, created_at

user_preferences
  id, user_id (FK), preferred_airlines (TEXT[]),
  excluded_airlines (TEXT[]), preferred_alliances (TEXT[]),
  cabin_classes (TEXT[]), max_stops (INT), home_airports (TEXT[])

subscriptions
  id, user_id (FK), email_id (FK → subscription_emails),
  type (enum: bug_fare / price_drop / deal_digest),
  config (JSONB: origins, destinations, target_price, frequency,
          airline_override — 可覆蓋全域偏好，例如此訂閱只看 ANA),
  is_active, last_sent_at, created_at

notification_log
  id, subscription_id (FK), email, subject, sent_at, status (sent/failed)
```

### 專案結構新增

```
backend/app/
├── services/
│   ├── subscription_service.py       # 訂閱 CRUD + 邏輯
│   ├── notification_service.py       # 觸發條件判斷 + 寄信
│   └── email_service.py              # Email 發送（SMTP/SES）
├── api/v1/
│   └── subscriptions.py              # 訂閱 API 端點
├── models/
│   ├── subscription.py               # Subscription + SubscriptionEmail models
│   └── notification_log.py           # 通知紀錄
├── schemas/
│   └── subscription.py               # Pydantic schemas
└── templates/
    └── emails/                       # Jinja2 HTML 郵件模板
        ├── bug_fare_alert.html
        ├── price_drop_alert.html
        ├── deal_digest.html
        └── verify_email.html
```

---

## 7. 價格監控 Daemon

### 概述

獨立的 Python 背景服務，24/7 執行機票價格監控。以用戶訂閱驅動 — 只監控有人訂閱的航線，節省 API 額度。在 Docker Compose 中作為獨立 service 運行。

### 資料來源

| API | 額度 | 用途 | 覆蓋 |
|---|---|---|---|
| **Amadeus** | 5,000 次/月（免費，搜尋+報價） | 主力來源，精準報價 | 400+ 航空公司 |
| **Google Flights Search** (RapidAPI) | 依訂閱方案 | 第三方輔助，交叉驗證 | Google Flights 資料 |
| **Skyscanner Search** (RapidAPI) | 依訂閱方案 | 第三方輔助，廉航覆蓋 | 全球廉航+傳統航空 |
| **Kiwi Search** (RapidAPI) | 依訂閱方案 | 第三方輔助，組合票價 | 全球航線+虛擬聯程 |

### Daemon 架構

```
price-monitor (獨立 Docker service)
    |
    ├── Scheduler（APScheduler）
    │   ├── 每 4 小時：掃描所有活躍訂閱，聚合去重航線
    │   ├── 每次掃描：對每條航線查詢 Amadeus + RapidAPI 來源
    │   └── 每日凌晨：清理過期資料、產生 Deal Digest
    │
    ├── Price Fetcher
    │   ├── amadeus_client.py      # Amadeus Flight Offers Search
    │   ├── rapidapi_client.py     # RapidAPI（Google Flights / Skyscanner / Kiwi）
    │   └── rate_limiter.py        # 按 API 配額控制請求速率
    │
    ├── Anomaly Detector（Bug Fare 偵測）
    │   ├── 計算航線歷史均價 + 標準差
    │   ├── 價格低於均價 50%+ → 標記為 Bug Fare 候選
    │   ├── 多來源交叉驗證（只有單一來源低價 = 更可能是 Bug Fare）
    │   └── 觸發即時通知（Bug Fare 存活時間短，需秒級反應）
    │
    ├── Preference Filter
    │   ├── 載入用戶 user_preferences（全域偏好）
    │   ├── 合併訂閱級 airline_override（優先於全域）
    │   └── 過濾結果：航空公司、聯盟、艙等、轉機次數
    │
    ├── Notifier
    │   ├── 比對訂閱條件（type + config + 偏好過濾後結果）
    │   ├── 符合條件 → 呼叫 notification_service 寄信
    │   └── 記錄至 notification_log
    │
    └── Shared DB（與 backend 共用 PostgreSQL + Redis）
        ├── 讀取：subscriptions, subscription_emails
        ├── 寫入：price_history, notification_log
        └── Redis：API 回應快取、rate limit 計數器
```

### API 配額策略

```
月配額：Amadeus ~5,000 次 + RapidAPI 依訂閱方案

假設 50 條活躍航線：
  - 每條航線每天查 3 次（每 8 小時）= 150 次/天
  - Amadeus：150 次 × 30 天 = 4,500 次/月 ✅ 在免費額度內
  - RapidAPI：輪詢或按需查詢，依各 API 訂閱額度分配

自動調節機制：
  - 當訂閱航線 > 55 條 → 降頻為每 12 小時
  - 當訂閱航線 > 100 條 → 降頻為每日 + 升級付費方案提醒
  - Bug Fare 候選 → 立即加密查詢（不受降頻影響）
```

### Bug Fare 偵測演算法

```python
# 簡化版邏輯
def detect_anomaly(route, current_price, history):
    avg = mean(history[-90_days])        # 90 天移動平均
    std = stdev(history[-90_days])

    # 條件 1：價格低於均價 50%
    if current_price < avg * 0.5:
        confidence = "high"
    # 條件 2：價格低於 2 個標準差
    elif current_price < avg - 2 * std:
        confidence = "medium"
    else:
        return None

    # 條件 3：只有單一來源出現低價 → 更可能是 Bug Fare
    if only_one_source_shows_low_price:
        confidence = "high"

    return BugFareAlert(route, current_price, avg, confidence)
```

### 專案結構新增

```
monitor/                              # 獨立 Python 服務
├── Dockerfile
├── pyproject.toml                    # 獨立依賴（共用部分 backend 的 models）
├── app/
│   ├── __init__.py
│   ├── main.py                       # 入口：初始化 scheduler + 啟動
│   ├── config.py                     # 監控服務設定（頻率、閾值、API keys）
│   ├── scheduler.py                  # APScheduler 任務定義與排程
│   ├── clients/                      # API 客戶端
│   │   ├── __init__.py
│   │   ├── amadeus_client.py         # Amadeus Flight Offers Search
│   │   ├── rapidapi_client.py        # RapidAPI（Google Flights / Skyscanner / Kiwi）
│   │   ├── base_client.py            # 共用 HTTP client（httpx async）
│   │   └── rate_limiter.py           # Token bucket rate limiter
│   ├── detector.py                   # Bug Fare / Price Drop 偵測
│   ├── notifier.py                   # 觸發通知（寄信 + 記錄）
│   └── tasks/
│       ├── __init__.py
│       ├── price_scan.py             # 掃描航線價格任務
│       ├── deal_digest.py            # 產生每日/每週精選摘要
│       └── cleanup.py                # 過期資料清理
└── tests/
    ├── test_detector.py
    ├── test_clients.py               # Amadeus + RapidAPI clients
    └── test_tasks.py
```

### Docker Compose 新增 service

```yaml
services:
  monitor:
    build: ./monitor
    depends_on: [db, redis]
    env_file: .env
    restart: always                   # 24/7 常駐運行
    healthcheck:
      test: ["CMD", "python", "-c", "import app; app.healthcheck()"]
      interval: 60s
```

---

## 8. 資料庫設計

**PostgreSQL 16** — 主要存儲，JSONB 欄位存放半結構化資料
**Redis 7** — 快取（搜尋結果 15min、價格 1hr、靜態資料 24hr）+ 對話 session

核心表：`users`, `trips`, `flights`, `hotels`, `activities`, `price_history`, `itineraries`, `chat_sessions`

---

## 9. 實作順序

1. **專案骨架**：目錄結構、`pyproject.toml`、`package.json`、Dockerfile、`docker-compose.yml`、`.env.example`
2. **資料庫層**：SQLAlchemy models、Alembic migrations、session factory、Redis client
3. **認證系統**：User model（google_id）、Google OAuth 2.0（authlib）、JWT 簽發
4. **代理框架**：`BaseAgent` ABC、tool execution loop、Anthropic SDK 整合
5. **Search Agent + Search Service**：機票/飯店搜尋 + API 端點
6. **Coordinator Agent**：意圖解析、代理分派、結果合成
7. **Chat SSE 串流端點**：連接 Coordinator 到 API 層
8. **Price Agent**：多源比價邏輯
9. **Itinerary Agent**：日程規劃
10. **訂閱系統**：subscription models、Email 驗證、通知排程、郵件模板
11. **價格監控 Daemon**：Amadeus + RapidAPI clients、rate limiter、anomaly detector、notifier
12. **前端**：搜尋頁、結果展示、聊天介面、行程管理、訂閱設定頁

---

## 10. 關鍵技術決策

- **Coordinator Pattern**（非 Pipeline）：旅遊查詢非線性，可並行多個代理
- **SSE**（非 WebSocket）：AI 聊天只需 server→client 串流，SSE 更簡單
- **JSONB 欄位**：不同資料源 schema 不同，核心欄位用 column，其餘 JSONB
- **Zustand**（非 Redux）：輕量、少 boilerplate，足夠應用需求
- **uv**：現代 Python 套件管理，速度快

---

## Verification

### 自動化測試（使用 `/test`）

每完成一個實作步驟後，使用 `/test <component>` 針對該組件驗證，最終用 `/test all` 做全面檢查：

| 指令 | 範圍 | 測試內容 |
|---|---|---|
| `/test models` | `backend/tests/test_models/` | 所有 SQLAlchemy models CRUD（user, trip, flight, hotel, activity, itinerary, chat_session, subscription, subscription_email, notification_log, price_history）、Alembic migrations up/down |
| `/test agents` | `backend/tests/test_agents/` | BaseAgent tool loop、Coordinator 分派、Search/Price/Recommendation/Itinerary/Budget 各子代理回應格式 |
| `/test api` | `backend/tests/test_api/` | 所有 `/api/v1/*` 端點：auth（OAuth + JWT + tier switch）、search（flights/hotels/direct/adventure）、compare（flights/hotels）、chat（SSE）、trips（CRUD）、itineraries、subscriptions（CRUD + email 驗證 + 退訂）、users/preferences |
| `/test services` | `backend/tests/test_services/` | search_service、price_service、itinerary_service、chat_service、subscription_service、notification_service、email_service 邏輯 |
| `/test clients` | `backend/tests/test_clients/` | Amadeus + RapidAPI clients（Google Flights、Skyscanner、Kiwi）資料抓取與正規化 |
| `/test monitor` | `monitor/tests/` | Amadeus + RapidAPI clients、rate limiter、anomaly detector、scheduler、notifier、tasks（price_scan、deal_digest、cleanup） |
| `/test frontend` | `frontend/src/**/*.test.*` | React 組件、hooks（useSearch, useChat, useTrip, useCompare）、stores（Zustand）單元測試 |
| `/test e2e` | `frontend/e2e/` | Playwright E2E：搜尋→結果→比價→聊天→行程管理完整流程 |
| `/test all` | 全部 | 執行以上所有測試 |

**對應實作步驟的測試順序**：
1. 完成資料庫層 → `/test models`
2. 完成認證系統 + 用戶等級 → `/test api`（auth + tier switch + users/preferences）
3. 完成代理框架 → `/test agents`
4. 完成搜尋功能 → `/test services` + `/test clients` + `/test api`（search + compare）
5. 完成 Chat SSE → `/test api`（chat endpoint）+ `/test services`（chat_service）
6. 完成訂閱系統 → `/test api`（subscriptions）+ `/test services`（subscription + notification + email）
7. 完成價格監控 Daemon → `/test monitor`
8. 完成前端 → `/test frontend` + `/test e2e`
9. 最終驗證 → `/test all`

### 整合驗證
1. `docker compose up` 可啟動所有服務（backend, frontend, postgres, redis, monitor）
2. `/test all` 通過所有測試
3. 前端 `http://localhost:3000` 可正常操作

### 測試策略
- 後端：`pytest` + `pytest-asyncio` + `httpx`（AsyncClient for FastAPI）
- 前端：`Vitest` + `@testing-library/react` + `Playwright`（E2E）
- Mock：模擬外部 API（Amadeus、RapidAPI：Google Flights / Skyscanner / Kiwi）和 Claude API 回應
- CI：GitHub Actions 自動執行 `/test all` 等價流程

---

## 11. Railway 正式環境部署計畫

### 背景

Travel-AI 目前透過 Docker Compose 在本機運行（5 個服務：backend, frontend, monitor, db, redis）。選擇 Railway 作為部署平台，同時保留 `.env` 供本地開發使用。Railway 各服務獨立運行、各有自己的 URL — 不使用 Docker Compose 網路 — 因此服務間通訊與密鑰管理需要調整。

### 關鍵變更

#### 1. 前端 API 代理 — 使後端 URL 可配置

**檔案：`frontend/next.config.ts`**
- 將寫死的 `http://backend:8000` 改為 `process.env.NEXT_PUBLIC_API_URL || "http://backend:8000"`
- 開發環境：繼續使用 Docker 內部 DNS（fallback）
- Railway：設定 `NEXT_PUBLIC_API_URL` 為後端的 Railway URL

#### 2. 後端 CORS — 無需修改程式碼

`backend/app/main.py` 已使用 `settings.FRONTEND_URL` 作為 CORS origins。只需在 Railway 設定正確的環境變數。

#### 3. Railway 服務設定

**建立：`backend/railway.toml`**
- Dockerfile builder，healthcheck 路徑 `/health`

**建立：`frontend/railway.toml`**
- Dockerfile builder，healthcheck 路徑 `/`

**建立：`monitor/railway.toml`**
- Dockerfile builder，無 healthcheck 路徑（背景 worker）

#### 4. 正式環境 Docker Compose（VM 替代方案）

**建立：`docker-compose.prod.yml`**
- 使用 `production` build targets
- 無 volume 掛載、無 `.env` 檔案
- 直接讀取環境變數
- 新增 Caddy 反向代理，自動 HTTPS
- 用於不使用 Railway 的 VM 部署

#### 5. 環境變數策略

| 變數 | 開發環境（`.env` 檔案） | Railway（dashboard） |
|---|---|---|
| `ENV` | `development` | `production` |
| `DEBUG` | `true` | `false` |
| `DATABASE_URL` | `...@db:5432/travelai` | Railway PostgreSQL URL |
| `REDIS_URL` | `redis://redis:6379/0` | Railway Redis URL |
| `FRONTEND_URL` | `http://localhost:3000` | `https://<frontend>.up.railway.app` |
| `BACKEND_URL` | `http://localhost:8000` | `https://<backend>.up.railway.app` |
| `GOOGLE_REDIRECT_URI` | `localhost:8000/...` | `<backend>.up.railway.app/...` |
| `ALLOW_TIER_SWITCH` | `true` | `false` |
| `NEXT_PUBLIC_API_URL` | 未設定（Docker DNS） | `https://<backend>.up.railway.app` |
| 所有密鑰/API keys | `.env` 中的開發值 | 在 Railway dashboard 設定 |

#### 6. GitHub Actions CI/CD

**建立：`.github/workflows/test.yml`**
- 觸發：push 到任何分支、PRs
- 啟動 PostgreSQL service container → 執行 backend + monitor 測試

**建立：`.github/workflows/deploy.yml`**
- 觸發：push 到 `main`
- 先執行測試 → 透過 `railway up` CLI 部署到 Railway
- 使用 `RAILWAY_TOKEN` GitHub secret

### 需要建立/修改的檔案

| 動作 | 檔案 |
|---|---|
| 修改 | `frontend/next.config.ts` — 可配置的 API URL |
| 建立 | `backend/railway.toml` |
| 建立 | `frontend/railway.toml` |
| 建立 | `monitor/railway.toml` |
| 建立 | `docker-compose.prod.yml` |
| 建立 | `.github/workflows/test.yml` |
| 建立 | `.github/workflows/deploy.yml` |

不修改 `.env` 或 `.env.example` — 開發流程維持不變。

### 驗證步驟

1. **本地開發不受影響**：`docker compose up --build` 仍使用 `.env` + override
2. **CI**：Push 觸發 GitHub Actions → pytest 在 PostgreSQL service container 上執行
3. **Railway 部署**：Push 到 `main` → Railway 從 Dockerfile 自動建置各服務
4. **部署後驗證**：確認 Google OAuth callback 在正式環境 URL 上正常運作

---

## 12. RapidAPI 整合（Skyscanner + Kiwi）

### 概述

透過 RapidAPI 整合兩個第三方航班搜尋 API，與現有 Amadeus 形成多來源聚合搜尋：

| API | RapidAPI Host | 覆蓋 | 特色 |
|---|---|---|---|
| **Skyscanner (Fly Scraper)** | `fly-scraper.p.rapidapi.com` | 全球航空（含 LCC） | 即時 Skyscanner 資料、飯店+租車 |
| **Kiwi (Flights Scraper)** | `flights-scraper-real-time.p.rapidapi.com` | 全球航線+虛擬聯程 | 組合票價、隱藏城市票、彈性日期範圍 |

**認證方式**：所有請求帶 `x-rapidapi-key` + `x-rapidapi-host` header。

---

### 12.1 Skyscanner (Fly Scraper) API Endpoints

#### 航班搜尋（核心）

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/flights/autocomplete` | GET | 機場/城市自動完成 | `query*` |
| `/v2/flights/autocomplete` | GET | v2 版自動完成（含 inbound/outbound 日期） | `query*` |
| `/airports` | GET | 機場查詢 | `location` |
| `/v2/flights/search-one-way` | GET | 單程航班搜尋 | `originSkyId*` |
| `/v2/flights/search-roundtrip` | GET | 來回航班搜尋 | `originSkyId*` |
| `/v2/flights/search-multi-city` | POST | 多城市搜尋 | `flights*`（array） |
| `/v2/flights/search-incomplete` | GET | 繼續取得完整結果 | `sessionId*` |
| `/flights/search-detail` | POST | 航班詳情（booking deeplink） | `sessionId*`, `itineraryId*` |
| `/flights/price-calendar` | GET | 價格日曆（單程） | `originSkyId*`, `destinationSkyId*`, `fromDate*` |
| `/flights/price-calendar-return` | GET | 價格日曆（來回） | `originSkyId*`, `destinationSkyId*`, `fromDate*` |
| `/1.0/flights/search-roundtrip` | GET | 探索所有目的地（Anywhere 模式） | `originSkyId*` |
| `/currencies` | GET | 支援的 locale/market/currency 列表 | — |

#### 共用參數

| 參數 | 說明 | 預設值 |
|---|---|---|
| `originSkyId*` | 出發地 Sky ID（從 autocomplete 取得） | — |
| `destinationSkyId` | 目的地 Sky ID | — |
| `departureDate` / `returnDate` | 日期，格式 `YYYY-MM-DD` | — |
| `adults` | 成人人數 | `1` |
| `currency` | 貨幣代碼 | `USD`（我們用 `TWD`） |
| `market` | 市場 | `US`（我們用 `TW`） |
| `locale` | 語言 | `en-US`（我們用 `zh-TW`） |
| `cabinClass` | 艙等：`economy` / `premium_economy` / `business` / `first` | `economy` |
| `sort` | 排序：`best` / `cheapest` / `fastest` | `best` |
| `stops` | 轉機：`direct,1stop,2stops+`（逗號分隔） | 不限 |
| `carriersIds` | 篩選航空公司（從 filterStats 取得） | — |

#### 飯店搜尋

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/hotels/autocomplete` | GET | 飯店地點搜尋 | `query*` |
| `/hotels/search` | GET | 飯店搜尋 | `entityId*`, `checkin*`, `checkout*` |
| `/hotels/detail` | GET | 飯店詳情 | `hotelId*` |
| `/hotels/detail/price` | GET | 飯店價格 | `hotelId*`, `entityId*`, `checkin*`, `checkout*` |
| `/hotels/detail/reviews` | GET | 飯店評論 | `hotelId*` |
| `/hotels/detail/similarhotels` | GET | 類似飯店 | `hotelId*`, `checkin*`, `checkout*` |
| `/hotels/nearbymap` | GET | 附近飯店地圖 | `entityId*`, `latitude*`, `longitude*` |

#### 租車搜尋

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/cars/autocomplete` | GET | 租車地點搜尋 | `query*` |
| `/cars/search` | GET | 租車搜尋 | `pickUpEntityId*`, `pickUpDate*`, `pickUpTime*`, `dropOffDate*`, `dropOffTime*` |

#### 回應格式

**flights/autocomplete**：
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

**v2/flights/search-one-way | search-roundtrip**：
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
          "originPlaceId": "128667054",
          "destinationPlaceId": "128667080",
          "departureDateTime": { "year": 2026, "month": 4, "day": 1, "hour": 2, "minute": 40, "second": 0 },
          "arrivalDateTime": { "year": 2026, "month": 4, "day": 1, "hour": 6, "minute": 15, "second": 0 },
          "carriers": {
            "marketing": { "name": "金航", "iata": "LJ", "imageUrl": "https://logos.skyscnr.com/images/airlines/LJ.png" },
            "operating": { "name": "金航", "iata": "LJ" }
          }
        }]
      }],
      "pricingOptions": [{ "price": { "formatted": "NT$7,142" }, "items": [{ "deepLink": "https://..." }] }]
    }],
    "filterStats": {
      "carriers": [{ "name": "...", "minPrice": ... }],
      "stopPrices": { "direct": ..., "one": ..., "two_or_more": ... },
      "airports": { ... }
    }
  }
}
```

**價格轉換**：`price.raw` 單位為 milli，實際價格 = `raw / 1000`（例：`7121000` → `NT$7,121`）

**incomplete 結果處理**：首次搜尋回傳 `context.status = "incomplete"`，可用 `sessionId` 呼叫 `/v2/flights/search-incomplete` 取得更多結果。

---

### 12.2 Kiwi (Flights Scraper Real-Time) API Endpoints

#### 航班搜尋（核心）

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/flights/auto-complete` | GET | 機場/城市自動完成 | `query*` |
| `/airports` | GET | 機場查詢 | `name` |
| `/airlines` | GET | 航空公司查詢 | `name` |
| `/configs` | GET | 支援的 locale/market/currency | `name`（搜尋過濾） |
| `/flights/search-oneway` | GET | 單程航班搜尋 | `originSkyId*`, `destinationSkyId*` |
| `/flights/search-return` | GET | 來回航班搜尋 | `originSkyId*`, `destinationSkyId*` |
| `/flights/price-table` | GET | 價格表（日期矩陣） | `originSkyId*`, `destinationSkyId*` |
| `/flights/price-trends` | GET | 價格趨勢 | `originSkyId*`, `destinationSkyId*` |
| `/flights/seat-info` | GET | 座位資訊 | `originSkyId*`, `destinationSkyId*`, `carrier*`, `code*` |
| `/deals/auto-complete` | GET | 特惠搜尋自動完成 | `query*` |
| `/deals/search` | GET | 特惠航班搜尋 | `query*` |

#### Kiwi 獨有進階參數

| 參數 | 說明 | 預設值 |
|---|---|---|
| `cabinClass` | `ECONOMY` / `PREMIUM_ECONOMY` / `BUSINESS` / `FIRST` | `ECONOMY` |
| `sort` | `QUALITY` / `PRICE` / `FASTEST` / `OUTBOUND_DEPARTURE_TIME` / ... | `QUALITY` |
| `stops` | `0`=直飛 / `1`=最多1轉 / `2`=最多2轉 | `0` |
| `limit` | 回傳數量上限 | `20` |
| `departureDate` | 最早出發日 `YYYY-MM-DD` | 當日 |
| `departureDateEnd` | 最晚出發日（彈性日期範圍） | — |
| `returnDate` / `returnDateEnd` | 回程日期範圍 | — |
| `maxDuration` | 最大飛行時間（分鐘） | — |
| `minPrice` / `maxPrice` | 價格範圍 | — |
| `carriers` | 篩選航空公司（從 `/airlines` 取得） | — |
| `cabinBaggage` / `checkedBaggage` | 行李數量 | — |
| `hiddenCity` | 隱藏城市票（Kiwi 特色） | `true` |
| `throwAwayTicketing` | 棄票優化 | `true` |
| `selfTransfer` | 自行轉機（虛擬聯程） | `true` |
| `allowOvernightStopovers` | 允許過夜轉機 | `true` |
| `outboundDepartureTimes` / `inboundDepartureTimes` | 出發/回程時段範圍 `min,max` | — |
| `stopoverTime` | 轉機時間範圍 `min,max`（分鐘） | — |

#### 飯店搜尋

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/stays/autocomplete` | GET | 住宿地點搜尋 | `location*` |
| `/stays/search/by-dest` | GET | 依目的地搜尋 | `dest_id*`, `dest_type*` |
| `/stays/search/by-location` | GET | 依地點名稱搜尋 | `location*` |
| `/stays/search/by-coordinates` | GET | 依座標搜尋 | `latitude*`, `longitude*` |
| `/stays/search/by-coordinates-bounding` | GET | 依邊界框搜尋 | `ne_lat*`, `ne_lon*`, `sw_lat*`, `sw_lon*` |
| `/stays/search/by-dest/filters` | GET | 搜尋篩選條件 | `dest_id*`, `dest_type*` |
| `/stays/search/by-dest/sorters` | GET | 排序選項 | `dest_id*`, `dest_type*` |
| `/stays/get-detail` | GET | 飯店詳情 | `hotel_id*` |
| `/stays/detail/rooms` | GET | 房型列表 | `hotel_id*` |
| `/stays/detail/description` | GET | 飯店描述 | `hotel_id*` |
| `/stays/detail/review` | GET | 評論列表 | `hotel_id*` |
| `/stays/detail/photos` | GET | 飯店照片 | `hotel_id*` |
| `/stays/detail/facilities` | GET | 設施列表 | `hotel_id*` |
| `/stays/detail/availability-calendar` | GET | 可用日曆 | `hotel_id*` |
| `/stays/detail/book-process-info` | GET | 訂房流程資訊 | `hotel_id*`, `blockIds*` |

#### 租車搜尋

| Endpoint | Method | 說明 | 必要參數 |
|---|---|---|---|
| `/cars/auto-complete` | GET | 租車地點搜尋 | `query*` |
| `/cars/search` | GET | 租車搜尋 | `pickUpLocation*` |
| `/cars/details` | GET | 租車詳情 | `id*`, `searchKey*` |
| `/cars/price-breakdown` | GET | 租車價格明細 | `id*`, `searchKey*` |

#### 回應格式

**flights/auto-complete**：
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

**flights/search-oneway | search-return**：
```json
{
  "status": true,
  "data": {
    "itineraries": [{
      "id": "...",
      "price": { "amount": "6790", "priceBeforeDiscount": "6790" },
      "duration": 21000,
      "sector": {
        "id": "...",
        "duration": 21000,
        "sectorSegments": [{
          "segment": {
            "source": {
              "station": { "code": "TPE", "name": "臺灣桃園國際機場", "type": "AIRPORT",
                "city": { "name": "台北" }, "country": { "code": "TW" }
              },
              "localTime": "2026-04-01T02:50:00",
              "utcTimeIso": "2026-03-31T18:50:00Z"
            },
            "destination": {
              "station": { "code": "NRT", "name": "成田國際機場", "type": "AIRPORT",
                "city": { "name": "東京" }, "country": { "code": "JP" }
              },
              "localTime": "2026-04-01T10:15:00",
              "utcTimeIso": "2026-04-01T01:15:00Z"
            },
            "duration": 8400,
            "type": "FLIGHT",
            "code": "6154",
            "carrier": { "name": "Jeju Air", "code": "7C" },
            "operatingCarrier": { "name": "Jeju Air", "code": "7C" },
            "cabinClass": "ECONOMY"
          },
          "layover": null
        }]
      },
      "provider": "...",
      "bagsInfo": { ... },
      "bookingOptions": [{ "edges": [{ "node": { "bookingUrl": "https://...", "price": { "amount": "6790" } } }] }]
    }],
    "metadata": { ... }
  }
}
```

**價格單位**：Kiwi 的 `price.amount` 為整數字串，單位即為指定 `currency`（例：`"6790"` = TWD 6,790）。

**Kiwi 獨有資料**：
- `bagsInfo`：行李資訊（含手提/托運）
- `bookingOptions`：多個訂票來源含價格與 booking URL
- `travelHack` / `hiddenCity` / `throwAwayTicketing`：特殊票價策略標記
- `isVanilla`：是否為標準票（非組合票）
- `pnrCount`：PNR 數量（>1 表示組合票/虛擬聯程）

---

### 12.3 兩 API 比較

| 面向 | Skyscanner (fly-scraper) | Kiwi (flights-scraper) |
|---|---|---|
| **航班搜尋** | v2 endpoints，快速回傳 | 進階篩選（彈性日期、時段、轉機時間） |
| **價格單位** | milli（÷1000） | 直接整數（原幣值） |
| **地點識別** | `skyId` + `entityId` | `skyId`（相容） |
| **分段搜尋** | `search-incomplete` + `sessionId` | 一次回傳（用 `limit` 控制） |
| **多城市** | `search-multi-city` (POST) | 無（只有單程+來回） |
| **獨有功能** | 價格日曆、Anywhere 搜尋 | 隱藏城市票、棄票優化、虛擬聯程、特惠搜尋、價格趨勢 |
| **飯店** | 基本搜尋+詳情 | 完整搜尋+篩選+排序+房型+評論+照片 |
| **租車** | 基本搜尋 | 搜尋+詳情+價格明細 |
| **行李資訊** | 無 | 有（bagsInfo） |
| **booking URL** | deepLink（在 pricingOptions 內） | bookingUrl（在 bookingOptions 內） |

---

### 12.4 實作計畫

#### Step 1: 新增 Config 設定

**檔案**：`backend/app/config.py`、`monitor/app/config.py`

```python
# 新增至 Settings / MonitorSettings
RAPIDAPI_KEY: str = ""
RAPIDAPI_SKYSCANNER_HOST: str = "fly-scraper.p.rapidapi.com"
RAPIDAPI_KIWI_HOST: str = "flights-scraper-real-time.p.rapidapi.com"
```

**檔案**：`.env.example` — 更新 host 預設值

#### Step 2: 建立 RapidAPI 基礎 Client

**新檔案**：`backend/app/clients/rapidapi_base.py`

```python
class RapidAPIBaseClient:
    """所有 RapidAPI clients 的基礎類別"""
    def __init__(self, base_url: str, host: str):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self._headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": host,
        }

    async def _get(self, path: str, params: dict) -> dict: ...
    async def _post(self, path: str, json: dict) -> dict: ...
    async def close(self): ...
```

#### Step 3: 建立 SkyscannerClient

**新檔案**：`backend/app/clients/skyscanner_client.py`

```python
class SkyscannerClient(RapidAPIBaseClient):
    def __init__(self):
        super().__init__("https://fly-scraper.p.rapidapi.com", settings.RAPIDAPI_SKYSCANNER_HOST)

    async def autocomplete(self, query: str, ...) -> list[dict]
    async def search_flights(self, origin_sky_id, destination_sky_id, departure_date,
                             return_date=None, adults=1, cabin_class="economy",
                             currency="TWD", market="TW", locale="zh-TW") -> list[dict]
        # 自動選擇 one-way / roundtrip endpoint
    async def search_flights_incomplete(self, session_id, ...) -> list[dict]
    async def search_everywhere(self, origin_sky_id, ...) -> list[dict]
        # 用 /1.0/flights/search-roundtrip（Anywhere 模式，冒險模式用）
    async def price_calendar(self, origin_sky_id, destination_sky_id, from_date, ...) -> list[dict]
    async def search_hotels(self, entity_id, checkin, checkout, ...) -> list[dict]
```

#### Step 4: 建立 KiwiClient

**新檔案**：`backend/app/clients/kiwi_client.py`

```python
class KiwiClient(RapidAPIBaseClient):
    def __init__(self):
        super().__init__("https://flights-scraper-real-time.p.rapidapi.com", settings.RAPIDAPI_KIWI_HOST)

    async def autocomplete(self, query: str) -> list[dict]
    async def search_flights(self, origin_sky_id, destination_sky_id, departure_date,
                             return_date=None, adults=1, cabin_class="ECONOMY",
                             currency="TWD", market="TW", locale="zh-TW",
                             limit=20, stops=None) -> list[dict]
        # 自動選擇 search-oneway / search-return endpoint
    async def search_deals(self, query, ...) -> list[dict]
        # 特惠航班搜尋（冒險模式可用）
    async def price_trends(self, origin_sky_id, destination_sky_id, ...) -> dict
    async def search_hotels(self, dest_id, dest_type, checkin, checkout, ...) -> list[dict]
```

#### Step 5: 正規化層

**新檔案**：`backend/app/clients/normalizer.py`

統一三個來源的回應為共用格式：

```python
def normalize_skyscanner_flight(itinerary: dict) -> dict:
    """Skyscanner itinerary → 統一格式"""
    return {
        "source": "skyscanner",
        "price": itinerary["price"]["raw"] / 1000,  # milli → 原幣值
        "currency": ...,
        "airline": leg.segments[0].carriers.marketing.iata,
        "airline_name": leg.segments[0].carriers.marketing.name,
        "flight_number": f"{iata}{segment.marketingFlightNumber}",
        "origin": ..., "destination": ...,
        "departure_time": ..., "arrival_time": ...,  # 從 year/month/day/hour/minute 組合
        "duration_minutes": leg.durationInMinutes,
        "stops": leg.stopCount,
        "segments": [...],
        "booking_url": pricingOptions[0].items[0].deepLink,
    }

def normalize_kiwi_flight(itinerary: dict) -> dict:
    """Kiwi itinerary → 統一格式"""
    return {
        "source": "kiwi",
        "price": int(itinerary["price"]["amount"]),  # 直接整數
        "currency": ...,
        "airline": segment.carrier.code,
        "airline_name": segment.carrier.name,
        "flight_number": f"{carrier.code}{segment.code}",
        "origin": segment.source.station.code,
        "destination": segment.destination.station.code,
        "departure_time": segment.source.localTime,  # ISO 8601
        "arrival_time": segment.destination.localTime,
        "duration_minutes": sector.duration / 60,  # 秒 → 分
        "stops": len(sectorSegments) - 1,
        "segments": [...],
        "booking_url": bookingOptions[0].edges[0].node.bookingUrl,
        "bags_info": itinerary.get("bagsInfo"),
        "is_virtual_interlining": itinerary.get("pnrCount", 1) > 1,
    }
```

#### Step 6: 整合到 Service 層

**檔案**：`backend/app/services/search_service.py`

```python
class SearchService:
    def __init__(self):
        self.amadeus = AmadeusClient()
        self.skyscanner = SkyscannerClient()  # 新增
        self.kiwi = KiwiClient()              # 新增

    async def search_flights(self, params):
        # 並行呼叫三個來源
        amadeus_task = self.amadeus.search_flights(...)
        skyscanner_task = self.skyscanner.search_flights(...)
        kiwi_task = self.kiwi.search_flights(...)

        results = await asyncio.gather(
            amadeus_task, skyscanner_task, kiwi_task,
            return_exceptions=True  # 任一失敗不影響其他來源
        )

        # 正規化 + 合併 + 去重
        normalized = []
        for source_results, normalizer in zip(results, [normalize_amadeus, normalize_skyscanner, normalize_kiwi]):
            if isinstance(source_results, Exception):
                logger.warning(f"Source failed: {source_results}")
                continue
            normalized.extend([normalizer(r) for r in source_results])

        return self._deduplicate_and_sort(normalized)

    def _deduplicate_and_sort(self, flights):
        # 去重：相同航班號+日期+時間 → 保留最低價
        # 排序：預設按價格
```

**檔案**：`backend/app/services/price_service.py`
- `compare_flights`：新增 Skyscanner + Kiwi 作為比價來源

#### Step 7: 整合到 Agent 層

**檔案**：`backend/app/agents/search_agent.py`
- `_search_flights`：呼叫 `SearchService.search_flights()`（已含多來源）
- 結果標記 `source` 欄位，AI 回覆可引用來源

**檔案**：`backend/app/agents/price_agent.py`
- `_compare_prices`：呼叫 `PriceService.compare_flights()`（已含多來源）

#### Step 8: 整合到 Monitor

**檔案**：`monitor/app/clients/` — 建立 `skyscanner_client.py` + `kiwi_client.py`
（可共用 backend 的邏輯，或簡化版僅包含 search_flights）

**檔案**：`monitor/app/tasks/price_scan.py`
- 每次掃描：Amadeus + Skyscanner + Kiwi 並行查詢
- 多來源價格用於 Bug Fare 交叉驗證

---

### 12.5 實作優先順序

| 階段 | 內容 | 依賴 |
|---|---|---|
| **Phase 1** | ✅ Config + RapidAPIBaseClient + SkyscannerClient（航班搜尋） | — |
| **Phase 2** | ✅ KiwiClient（航班搜尋）+ normalizer + 88 unit tests | Phase 1 |
| **Phase 3** | ✅ schemas 對齊 frontend + 多來源 SearchService/PriceService + 統一 Compare 端點 + Redis 快取 | Phase 1-2 |
| **Phase 4** | Agent 層整合（SearchAgent/PriceAgent 使用多來源 Service） | Phase 3 |
| **Phase 5** | Monitor 客戶端 + price_scan 多來源 | Phase 1-2 |
| **Phase 6** | 飯店搜尋整合（Skyscanner + Kiwi hotels） | Phase 3 |

---

### 12.6 需要建立/修改的檔案

| 動作 | 檔案 | 說明 |
|---|---|---|
| 修改 | `backend/app/config.py` | 新增 `RAPIDAPI_*` settings |
| 修改 | `monitor/app/config.py` | 新增 `RAPIDAPI_*` settings |
| **新建** | `backend/app/clients/rapidapi_base.py` | RapidAPI 基礎 HTTP client |
| **新建** | `backend/app/clients/skyscanner_client.py` | Skyscanner flight/hotel 搜尋 |
| **新建** | `backend/app/clients/kiwi_client.py` | Kiwi flight/hotel/deals 搜尋 |
| **新建** | `backend/app/clients/normalizer.py` | 三來源回應正規化 |
| 修改 | `backend/app/services/search_service.py` | 多來源並行搜尋 + 合併去重 |
| 修改 | `backend/app/services/price_service.py` | 多來源比價 |
| 修改 | `backend/app/agents/search_agent.py` | 使用多來源 SearchService |
| 修改 | `backend/app/agents/price_agent.py` | 使用多來源 PriceService |
| **新建** | `monitor/app/clients/skyscanner_client.py` | Monitor 用 Skyscanner client |
| **新建** | `monitor/app/clients/kiwi_client.py` | Monitor 用 Kiwi client |
| 修改 | `monitor/app/tasks/price_scan.py` | 多來源價格掃描 |
| 修改 | `.env.example` | 更新 RapidAPI host 預設值 |

---

### 12.7 驗證方式

1. **單元測試**：`pytest` + `respx` mock 各 API 回應，測試正規化邏輯
2. **整合測試**：
   - `docker compose up` → `POST /api/v1/search/flights` 搜尋 TPE→NRT
   - 確認回應包含 `source: "amadeus"`, `source: "skyscanner"`, `source: "kiwi"` 結果
3. **比價驗證**：`POST /api/v1/compare/flights` 確認多來源比價
4. **冒險模式**：`POST /api/v1/search/adventure` 確認 Skyscanner Anywhere + Kiwi deals 結果
5. **API 直接驗證**（curl）：
   ```bash
   # Skyscanner autocomplete
   curl "https://fly-scraper.p.rapidapi.com/flights/autocomplete?query=taipei" \
     -H "x-rapidapi-key: $RAPIDAPI_KEY" -H "x-rapidapi-host: fly-scraper.p.rapidapi.com"

   # Kiwi flight search
   curl "https://flights-scraper-real-time.p.rapidapi.com/flights/search-oneway?originSkyId=TPE&destinationSkyId=NRT&departureDate=2026-04-01&currency=TWD&market=TW&locale=zh-TW" \
     -H "x-rapidapi-key: $RAPIDAPI_KEY" -H "x-rapidapi-host: flights-scraper-real-time.p.rapidapi.com"
   ```

---

## 13. 功能面與 Webpage 對應

本節對應 frontend 各頁面與 backend API 的整合現況、資料格式差異、以及接下來的對齊工作。

### 13.1 頁面總覽

| 頁面 | 路由 | 功能 | 現況 |
|---|---|---|---|
| 首頁 | `/` | 搜尋表單 + 登入入口 | ✅ 可運作 |
| 搜尋結果 | `/search` | 機票/飯店搜尋結果展示、排序 | ✅ 機票格式已對齊；⚠️ 飯店格式待對齊 |
| 比價 | `/compare` | 多來源價格比較表 | ✅ 統一端點已建立（`POST /compare`） |
| 行程管理 | `/trip` | 行程 CRUD + 行程表瀏覽 | ✅ 可運作 |
| AI 聊天 | `/chat` | SSE 串流聊天（多 Agent） | ✅ 可運作 |
| OAuth 回調 | `/auth/callback` | Google 登入 token 處理 | ✅ 可運作 |

### 13.2 資料格式差異：機票搜尋

Frontend `FlightResult`（`frontend/src/types/index.ts`）與 Backend `FlightResult`（`backend/app/schemas/search.py`）欄位不一致：

| 用途 | Frontend 期待 | Backend 現有 | 對齊方向 |
|---|---|---|---|
| 唯一 ID | `id: string` | `id: UUID \| None` | backend 確保回傳 |
| 來源/供應商 | `provider: string` | `source: string` | 改名為 `provider` |
| 價格 | `price: number` (頂層) | `price: PriceInfo` (嵌套 `{amount, currency}`) | 拆成 `price` + `currency` 頂層欄位 |
| 幣別 | `currency: string` (頂層) | 在 `PriceInfo.currency` 裡 | 同上 |
| 出發段 | `outbound_segments: FlightSegment[]` | 無 segments 欄位 | 新增 `outbound_segments` |
| 回程段 | `return_segments?: FlightSegment[]` | 無 | 新增（來回程時） |
| 總時長 | `total_duration_minutes: number` | `duration_minutes: int \| None` | 改名為 `total_duration_minutes` |
| 經停 | `stops: number` | `stops: int` | ✅ 一致 |
| 訂票連結 | `booking_url?: string` | 無此欄位 | 新增 `booking_url` |
| 到期時間 | `expires_at?: string` | 無 | 新增（可選） |

Frontend `FlightSegment`（每段航班）所需欄位：

```typescript
{
  airline: string;           // 航空公司 IATA code
  airline_logo?: string;     // logo URL（可由前端組合）
  flight_number: string;     // e.g. "CI100"
  departure_airport: string; // IATA code
  arrival_airport: string;   // IATA code
  departure_time: string;    // ISO 8601
  arrival_time: string;      // ISO 8601
  duration_minutes: number;
  cabin_class: string;
}
```

**對齊計畫**：修改 backend `FlightResult` schema + `SearchService` 回傳格式，使 response 直接符合 frontend types。Normalizer 的 dict 輸出需要轉換為新 schema。

### 13.3 資料格式差異：飯店搜尋

Frontend `HotelResult` 期待豐富資料，Backend `HotelResult` 只有基本欄位：

| 用途 | Frontend 期待 | Backend 現有 | 對齊方向 |
|---|---|---|---|
| 唯一 ID | `id: string` | `id: UUID \| None` | backend 確保回傳 |
| 來源 | `provider: string` | `source: string` | 改名 |
| 名稱 | `name: string` | `name: string` | ✅ 一致 |
| 地址 | `address: string` | `location: string \| None` | 改名為 `address` |
| 座標 | `latitude?`, `longitude?` | 無 | 新增 |
| 星級 | `star_rating: number` | `stars: int \| None` | 改名 |
| 用戶評分 | `user_rating?: number` | `rating: float \| None` | 改名 |
| 評論數 | `review_count?: number` | 無 | 新增 |
| 每晚價格 | `price_per_night: number` | `price_per_night: float` | ✅ 近似一致 |
| 總價 | `total_price: number` | 無 | 新增 |
| 幣別 | `currency: string` | `price_currency: string` | 改名 |
| 設施 | `amenities: string[]` | 無 | 新增 |
| 圖片 | `images: string[]` | 無 | 新增 |
| 訂票連結 | `booking_url?: string` | 無 | 新增 |
| 取消政策 | `cancellation_policy?: string` | 無 | 新增 |

### 13.4 Compare 端點不對齊

- **Frontend** 呼叫 `POST /api/compare`，送 `{ item_ids: string[], item_type: "flight" | "hotel" }`
- **Backend** 有分開的 `POST /compare/flights` 和 `POST /compare/hotels`

**對齊方案**：在 backend 新增統一的 `POST /compare` 端點，接收 `item_type` 參數後分流到對應 service。

### 13.5 SearchResponse 格式差異

Frontend `useSearch` hook 期待 `SearchResponse`：
```typescript
{
  search_id: string;       // 搜尋 session ID
  type: "flight" | "hotel";
  flights?: FlightResult[];
  hotels?: HotelResult[];
  total_results: number;
  search_params: SearchParams;
  created_at: string;
}
```

Backend 目前回傳 `FlightSearchResponse`：
```python
{
  "results": [FlightResult, ...],  # 而非 "flights"
  "total": int                      # 而非 "total_results"
}
```

**對齊方案**：修改 backend response schema，使欄位名稱與 frontend types 一致，或統一成 `SearchResponse` 格式。

### 13.6 對齊實作順序

Phase 3 工作（✅ 已完成 — 串接 SearchService 多來源 + 對齊 frontend/backend 格式）：

#### Step 1: 修改 Backend Schemas ✅

| 檔案 | 修改內容 |
|---|---|
| `backend/app/schemas/search.py` | ✅ 重構 `FlightResult`：`id`(stable hash)、`provider`、`price`(float)、`currency`、`outbound_segments: list[FlightSegment]`、`return_segments`、`total_duration_minutes`、`booking_url`、`expires_at` |
| `backend/app/schemas/search.py` | ✅ 新增 `FlightSegment` schema（airline, flight_number, departure/arrival_airport/time, duration_minutes, cabin_class） |
| `backend/app/schemas/search.py` | ✅ 新增 `SearchResponse`（search_id, type, flights, hotels, total_results, search_params, created_at） |
| `backend/app/schemas/search.py` | ✅ 新增 helpers：`_stable_flight_id()`, `normalized_dict_to_flight_result()` |
| `backend/app/schemas/search.py` | ✅ 保留 `PriceInfo`（給 DirectSearch/Adventure 用）、保留所有 request schemas 不變 |
| `backend/app/schemas/compare.py` | ✅ 新增 `UnifiedCompareRequest`、`PricePoint`、`CompareResult` |
| `backend/app/schemas/compare.py` | ✅ 保留 `FlightCompareRequest/Response`、`HotelCompareRequest/Response`（向後相容） |

#### Step 2: 整合 SearchService 多來源 ✅

| 檔案 | 修改內容 |
|---|---|
| `backend/app/services/search_service.py` | ✅ 引入 `SkyscannerClient`, `KiwiClient`，`asyncio.gather` 並行查詢三來源 |
| `backend/app/services/search_service.py` | ✅ 使用 `normalizer` 統一格式 + `deduplicate_flights` 去重 + `normalized_dict_to_flight_result` 轉換 |
| `backend/app/services/search_service.py` | ✅ Redis 快取搜尋結果（`flight:{stable_id}`, TTL 30min），Redis 不可用時 gracefully skip |
| `backend/app/services/search_service.py` | ✅ `search_direct()` 改用 normalizer + 新 FlightResult |
| `backend/app/services/search_service.py` | ✅ `search_adventure()` 改用 stub FlightSegment + 新 FlightResult |
| `backend/app/services/search_service.py` | ✅ 刪除 `_normalize_amadeus_flight()` 方法 |

#### Step 3: 整合 PriceService 多來源 + 統一 Compare ✅

| 檔案 | 修改內容 |
|---|---|
| `backend/app/services/price_service.py` | ✅ 新增 `unified_compare()` — 從 Redis 讀取快取 → 組成 `CompareResult` |
| `backend/app/services/price_service.py` | ✅ `compare_flights()` 多來源並行（Amadeus + Skyscanner + Kiwi） |
| `backend/app/services/price_service.py` | ✅ 刪除 `_normalize_amadeus()` hack |
| `backend/app/api/v1/compare.py` | ✅ 新增 `POST ""` 統一端點（`list[CompareResult]`） |
| `backend/app/api/v1/search.py` | ✅ `/flights` response_model 改為 `SearchResponse` |

#### Step 4: 飯店搜尋串接（留給下一 Phase）

| 檔案 | 修改內容 |
|---|---|
| `backend/app/services/search_service.py` | `search_hotels` 串接 Skyscanner + Kiwi hotels |

### 13.7 完成後各頁面預期效果

| 頁面 | 效果 |
|---|---|
| `/search`（機票） | 同時顯示 Amadeus + Skyscanner + Kiwi 結果，每張 FlightCard 有航段明細、經停數、來源標記、訂票連結 |
| `/search`（飯店） | 顯示 Skyscanner + Kiwi 飯店結果，含圖片、設施、評分 |
| `/compare` | 輸入航班 ID 列表後，表格顯示各來源的價格比較，標記最低價 |
| `/chat` | 聊天 Agent 可調用多來源搜尋工具，回傳更豐富的結果 |
