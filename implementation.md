# Travel-AI Project Plan - Extracted from Planning Session

## Project Architecture & Tech Stack

### Overview
Travel-AI is an intelligent travel aggregation platform built with a multi-service Docker Compose architecture.

### Tech Stack

**Backend (Python FastAPI)**
- Framework: FastAPI 0.115+
- Package Manager: uv (Python)
- ORM: SQLAlchemy async with asyncpg driver
- Migrations: Alembic
- Cache: Redis
- Auth: Google OAuth 2.0 (authlib) + JWT tokens
- API Client: Anthropic (Claude API)
- External APIs: Amadeus, Skyscanner (RapidAPI), Kiwi (RapidAPI) — multi-source flight search
- Currency: Exchange rate conversion via open.er-api.com (no API key), Redis-cached 6h
- Email: FastAPI-mail with SMTP
- Job Scheduling: APScheduler
- Database: PostgreSQL 16

**Frontend (Next.js 15 + React 19)**
- Framework: Next.js 15
- Component Library: React 19
- State Management: Zustand
- Styling: Tailwind CSS v4
- Testing: Vitest, Playwright E2E
- Utilities: date-fns, lucide-react, clsx, tailwind-merge

**Monitor Service (Python)**
- Purpose: Price monitoring daemon
- Clients: Amadeus API (rate-limited); Skyscanner + Kiwi planned (Phase 5)
- Scheduling: APScheduler
- Database: PostgreSQL (shared)

**Infrastructure**
- Container Runtime: Docker & Docker Compose
- Database: PostgreSQL 16 (managed container)
- Cache: Redis 7 (managed container)
- Development: Hot-reload volumes, override compose file
- Production: Multi-build targets (development vs production)

---

## Backend Architecture

### Database Models (11 Tables)

1. **users** - User accounts with OAuth integration
   - Fields: id, email, name, avatar_url, google_id, tier (enum: basic/premium), tier_updated_at, last_login

2. **user_preferences** - User travel preferences
   - Fields: id, user_id, preferred_airlines[], excluded_airlines[], preferred_alliances[], cabin_classes[], max_stops, home_airports[]

3. **trips** - User travel trips
   - Fields: id, user_id, title, description, destination, start_date, end_date, metadata (JSONB)

4. **flights** - Flight search results and bookings
   - Fields: id, trip_id, airline, flight_no, origin, destination, departure, arrival, stops, duration_minutes, cabin_class, price_*, source, raw_data (JSONB)

5. **hotels** - Hotel search results
   - Fields: id, trip_id, name, location, check_in, check_out, stars, rating, price_per_night, source, description, raw_data (JSONB)

6. **activities** - Activities and attractions
   - Fields: id, trip_id, name, location, description, start_time, end_time, price_*, category, source, raw_data (JSONB)

7. **price_history** - Historical price tracking for alerts
   - Fields: id, origin, destination, departure_date, return_date, airline, price_*, source, cabin_class, stops, raw_data (JSONB)

8. **itineraries** - Generated day-by-day schedules
   - Fields: id, trip_id, title, description, schedule (JSONB - day-by-day breakdown)

9. **chat_sessions** - AI chat conversations
   - Fields: id, user_id, title, messages[] (JSONB - message history)

10. **subscriptions** - Price alert subscriptions
    - Fields: id, user_id, type (enum: bug_fare/price_drop/deal_digest), origin, destination, date_from, date_to, price_threshold, active, raw_filter (JSONB)

11. **subscription_emails** - Verified subscriber emails
    - Fields: id, user_id, email, verified, subscribed_types[], created_at, updated_at

Plus: **notification_log** - Audit trail for sent notifications

### API Endpoints (`/api/v1/`)

**Auth**
- `GET /auth/google` - Initiate Google OAuth flow
- `GET /auth/google/callback` - Google OAuth callback
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get authenticated user
- `PATCH /auth/me/tier` - Switch tier (dev/test only, `ALLOW_TIER_SWITCH=true`)
- `POST /auth/logout` - Logout

**Geo**
- `GET /geo/currency` - IP-based currency detection (ip-api.com, Redis-cached 24h)

**Search**
- `POST /search/flights` - Multi-source flight search (Amadeus + Skyscanner + Kiwi), returns `SearchResponse`
- `POST /search/direct` - Direct flights only (premium)
- `POST /search/adventure` - Inspiration mode
- `POST /search/hotels` - Search hotels

**Compare**
- `POST /compare` - Unified compare by item IDs from Redis cache, returns `list[CompareResult]`
- `POST /compare/flights` - Multi-source flight comparison (legacy)
- `POST /compare/hotels` - Hotel comparison (legacy)

**Trips**
- `GET /trips` - List user trips
- `POST /trips` - Create trip
- `GET /trips/{id}` - Get trip details
- `PUT /trips/{id}` - Update trip
- `DELETE /trips/{id}` - Delete trip

**Itineraries**
- `POST /itineraries` - Generate itinerary from trip

**Chat**
- `GET /chat/{session_id}` - Get chat session (SSE endpoint)
- `POST /chat` - Send message (returns stream)

**Subscriptions**
- `GET /subscriptions` - List subscriptions
- `POST /subscriptions` - Create subscription
- `PUT /subscriptions/{id}` - Update
- `DELETE /subscriptions/{id}` - Delete
- `POST /subscriptions/{id}/verify-email` - Verify subscriber email
- `POST /subscriptions/unsubscribe` - Unsubscribe (email-based)

**Users**
- `GET /users/preferences` - Get user travel preferences
- `PUT /users/preferences` - Update preferences

### Agent System

**BaseAgent (Abstract)**
- Manages Claude API tool_use loop
- Maintains conversation history
- Implements tool dispatch

**CoordinatorAgent**
- Routes user messages to specialist agents
- Orchestrates multi-agent responses
- Maintains chat context

**Specialist Agents** (dispatched by Coordinator)
1. **SearchAgent** - Flight/hotel search, gateway hubs, foreigner discounts
2. **PriceAgent** - Multi-source price comparison, anomaly detection
3. **RecommendationAgent** - Quality scoring, airline ratings
4. **ItineraryAgent** - Day-by-day schedule generation, TSP route optimization
5. **BudgetAgent** - Daily cost estimation, budget breakdowns by country

### Services

1. **SearchService** - Multi-source flight search (Amadeus + Skyscanner + Kiwi parallel query, normalizer, dedup, Redis cache); fetches exchange rates in parallel for Amadeus currency conversion
2. **PriceService** - Multi-source price comparison + unified compare via Redis cache; fetches exchange rates in parallel for Amadeus currency conversion
3. **ChatService** - SSE streaming, agent orchestration
4. **ItineraryService** - Schedule generation, optimization
5. **SubscriptionService** - Subscription management
6. **EmailService** - SMTP, templated notifications
7. **NotificationService** - Alert dispatch

### External API Clients

**AmadeusClient**
- Flight search (`search_flights`)
- Hotel search (`search_hotels`)
- Inspiration search (`search_inspiration` - for adventure mode)
- OAuth2 client credentials auth with token refresh

**RapidAPIBaseClient** (abstract base for RapidAPI clients)
- Shared HTTP client (`httpx.AsyncClient`)
- `x-rapidapi-key` / `x-rapidapi-host` header management
- Graceful error handling (returns empty dict/list on failure)

**SkyscannerClient** (extends RapidAPIBaseClient)
- `search_flights` - one-way and roundtrip
- `search_flights_incomplete` - poll for more results
- `search_everywhere` - origin to anywhere
- `price_calendar` - price trends across dates
- `search_hotels` - hotel search
- `autocomplete` - location autocomplete

**KiwiClient** (extends RapidAPIBaseClient)
- `search_flights` - one-way and return, with stops parameter
- `search_deals` - flight deals
- `price_trends` - price trend analysis
- `search_hotels` - hotel search by destination
- `autocomplete` - location autocomplete

**Normalizer** (`app/clients/normalizer.py`)
- `normalize_amadeus_flight(offer, currency, exchange_rates)` — accepts optional `exchange_rates` dict; auto-converts Amadeus EUR/USD prices to the user's currency
- `normalize_skyscanner_flight()` / `normalize_kiwi_flight()` → common dict format (prices already in requested currency)
- `deduplicate_flights()` - keeps lowest price per flight_number+departure_time
- `_parse_iso_duration()` - PT5H30M → minutes
- Output dict converted to `FlightResult` Pydantic model via `normalized_dict_to_flight_result()`

**Currency Utilities** (`app/lib/currency.py`)
- `get_exchange_rates(base)` — fetches from `open.er-api.com`, Redis-cached 6h, returns `dict[str, float]`
- `convert_price(amount, from_currency, to_currency, rates)` — pure function, graceful fallback if rate missing

---

## Frontend Architecture

### Pages
- **Landing** - Marketing/intro
- **Search** - Flight/hotel search form + results
- **Compare** - Comparison view
- **Trip** - Trip planner/itinerary
- **Chat** - AI chat interface
- **Auth Callback** - OAuth redirect handler

### Components
- **SearchForm** - Multi-field search input
- **FlightCard** / **HotelCard** - Result cards
- **CompareTable** - Side-by-side comparison
- **ChatWindow** / **ChatMessage** - Chat UI
- **ItineraryView** - Day-by-day schedule display
- **Header** / **Footer** - Layout components
- **Button** / **Input** / **Card** - Shared UI primitives

### Hooks
- `useAuth()` - Authentication state + Google login
- `useSearch()` - Search form and results
- `useChat()` - SSE message streaming
- `useTrip()` - Trip management
- `useCompare()` - Comparison logic

### State Management (Zustand)
- **searchStore** - Search criteria, results, filters
- **tripStore** - Current trip, flights, hotels, activities
- **chatStore** - Messages, session ID, loading state

### API Communication
- Next.js API proxy rewrites: `/api/:path*` → `http://backend:8000/api/v1/:path*`
- Fallback to Docker DNS `http://backend:8000` for dev
- Environment variable: `NEXT_PUBLIC_API_URL` (Railway production)

---

## Monitor Service Architecture

### Price Monitoring Daemon

**Clients**
- **AmadeusClient** - Flight price data
- Rate limiting with token bucket algorithm

**Tasks**
- **PriceScanner** - Periodic price checks for subscriptions
- **NotificationDispatcher** - Send alerts when price drops detected

**Detector**
- Anomaly detection for "bug fares" (unusually low prices)
- Trend analysis for gradual price drops

**Schedule** (APScheduler)
- Every 6 hours: scan subscriptions
- Every 24 hours: send daily deal digests
- On-demand: email verification

---

## Authentication & Authorization

### OAuth Flow
1. Frontend: `GET /auth/google` redirects to Google
2. Google OAuth consent screen
3. Google redirects to `POST /auth/google/callback` with code
4. Backend exchanges code for Google user profile
5. Backend creates/updates User in DB, issues JWT
6. Frontend receives access token + refresh token in cookies
7. Subsequent requests include access token in Authorization header

### JWT Tokens
- **Access Token**: 30-minute expiry, includes user_id, email, tier
- **Refresh Token**: 7-day expiry, used to mint new access tokens
- **Algorithm**: HS256
- **Secret**: `JWT_SECRET_KEY` from environment

### User Tiers
- **Basic**: Search, compare, trips, chat, 1 subscription
- **Premium**: All basic + direct flights, adventure mode, unlimited subscriptions
- **Tier Switch**: Dev-only guard (set `ALLOW_TIER_SWITCH=true` in `.env`)

---

## Email & Notifications

### Subscription Email Management
1. User creates subscription via API
2. Verification email sent to `SubscriptionEmail` address
3. Email contains unsubscribe link with token
4. Tokens valid for 7 days, single-use
5. Price alerts sent only to verified emails

### Email Templates (Jinja2)
- **bug_fare_alert.html** - Unusually low fares detected
- **price_drop_alert.html** - Price decreased for watched route
- **deal_digest.html** - Weekly digest of deals
- **email_verification.html** - Verify subscription email

### SMTP Configuration
- Provider: Gmail (default) or custom SMTP
- Port: 587 (TLS)
- Credentials: `SMTP_USER` / `SMTP_PASSWORD` in `.env`

---

## Environment Variables Strategy

### Development (`.env` file)

| Variable | Dev Value | Purpose |
|---|---|---|
| `ENV` | `development` | App mode |
| `DEBUG` | `true` | Debug logging |
| `SECRET_KEY` | dev value | Session encryption |
| `FRONTEND_URL` | `http://localhost:3000` | CORS origins |
| `BACKEND_URL` | `http://localhost:8000` | Frontend API target |
| `DATABASE_URL` | `postgresql+asyncpg://travelai:...@db:5432/travelai` | Docker Postgres |
| `REDIS_URL` | `redis://redis:6379/0` | Docker Redis |
| `GOOGLE_CLIENT_ID` | placeholder | OAuth app ID |
| `GOOGLE_CLIENT_SECRET` | placeholder | OAuth app secret |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/api/v1/auth/google/callback` | OAuth redirect |
| `JWT_SECRET_KEY` | dev value | Token signing |
| `ANTHROPIC_API_KEY` | placeholder | Claude API key |
| `AMADEUS_API_KEY` | placeholder | Amadeus test key |
| `AMADEUS_API_SECRET` | placeholder | Amadeus test secret |
| `AMADEUS_BASE_URL` | `https://test.api.amadeus.com` | Amadeus test endpoint |
| `RAPIDAPI_KEY` | placeholder | RapidAPI key (Skyscanner + Kiwi) |
| `SMTP_HOST` | `smtp.gmail.com` | Email provider |
| `SMTP_USER` | `your-email@gmail.com` | Email account |
| `SMTP_PASSWORD` | placeholder | Email app password |
| `EMAIL_FROM` | `noreply@travel-ai.com` | Sender address |
| `ALLOW_TIER_SWITCH` | `true` | Dev-only tier switching |

### Production (Railway Dashboard Env Vars)

| Variable | Railway Value | Purpose |
|---|---|---|
| `ENV` | `production` | Production mode |
| `DEBUG` | `false` | No debug logging |
| `SECRET_KEY` | Strong random value | Session encryption |
| `FRONTEND_URL` | `https://<frontend-railway-url>` | CORS origins |
| `BACKEND_URL` | `https://<backend-railway-url>` | Internal reference |
| `DATABASE_URL` | Railway PostgreSQL connection string | Managed PostgreSQL |
| `REDIS_URL` | Railway Redis connection string | Managed Redis |
| `GOOGLE_CLIENT_ID` | Production OAuth ID | OAuth app ID |
| `GOOGLE_CLIENT_SECRET` | Production OAuth secret | OAuth app secret |
| `GOOGLE_REDIRECT_URI` | `https://<backend-railway-url>/api/v1/auth/google/callback` | OAuth redirect |
| `JWT_SECRET_KEY` | Strong random value | Token signing |
| `ANTHROPIC_API_KEY` | Production key | Claude API key |
| `AMADEUS_API_KEY` | Production key | Amadeus production key |
| `AMADEUS_API_SECRET` | Production secret | Amadeus production secret |
| `AMADEUS_BASE_URL` | `https://api.amadeus.com` | Amadeus production endpoint |
| `RAPIDAPI_KEY` | Production key | RapidAPI key (Skyscanner + Kiwi) |
| `SMTP_HOST` | `smtp.gmail.com` or provider | Email provider |
| `SMTP_USER` | Production email | Email account |
| `SMTP_PASSWORD` | Production app password | Email app password |
| `EMAIL_FROM` | `noreply@travel-ai.com` | Sender address |
| `ALLOW_TIER_SWITCH` | `false` | Production disabled |
| `NEXT_PUBLIC_API_URL` | `https://<backend-railway-url>` | Frontend API endpoint |

---

## Railway Production Deployment Plan

### Context
Travel-AI currently runs via Docker Compose locally (5 services: backend, frontend, monitor, db, redis). Railway is the chosen platform because it:
- Supports native Docker Compose multi-service deployments
- Provides managed PostgreSQL and Redis add-ons
- Handles secrets via environment variables
- Auto-deploys on git push
- Supports custom domains with auto HTTPS

### Key Architecture Changes for Railway

#### 1. Frontend API Proxy Configuration

**File: `frontend/next.config.ts`**
- Change hardcoded `http://backend:8000` to `process.env.NEXT_PUBLIC_API_URL || "http://backend:8000"`
- Dev: continues using Docker internal DNS (fallback)
- Railway: set `NEXT_PUBLIC_API_URL` to the backend's Railway URL (e.g., `https://travel-ai-backend.up.railway.app`)

**Rationale**: Dev and production have different backend URLs. Docker Compose uses internal DNS; Railway uses public URLs.

#### 2. Backend CORS Configuration

**File: `backend/app/main.py`**
- Already uses `settings.FRONTEND_URL` for CORS origins - no code change needed
- Just ensure `FRONTEND_URL` is set correctly in Railway dashboard

#### 3. Railway Service Configs

Create per-service `railway.toml` configuration files:

**Create: `backend/railway.toml`**
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

**Create: `frontend/railway.toml`**
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

**Create: `monitor/railway.toml`**
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
restartPolicyType = "on_failure"
```

**Rationale**: Railway needs to know how to build and health-check each service independently.

#### 4. Production Docker Compose (VM Alternative)

**Create: `docker-compose.prod.yml`**
- Uses `production` build targets (multi-stage Dockerfiles)
- No volume mounts (no hot-reload)
- No `.env` file - reads environment variables directly
- Adds Caddy reverse proxy for HTTPS with auto Let's Encrypt
- For deploying to a plain VM without Railway

#### 5. GitHub Actions CI/CD

**Create: `.github/workflows/test.yml`**
- Trigger: push to any branch, PRs
- Spin up PostgreSQL service container
- Run backend tests: `pytest backend/tests`
- Run monitor tests: `pytest monitor/tests`
- Report coverage

**Create: `.github/workflows/deploy.yml`**
- Trigger: push to `main` only
- Run tests first
- Deploy to Railway via `railway up` CLI
- Uses `RAILWAY_TOKEN` GitHub secret

**Rationale**: Automated testing + deployment pipeline for reliability.

#### 6. Secrets Management

| Environment | Storage | Method |
|---|---|---|
| Dev | `.env` file | Local file (gitignored) |
| Production | Railway Dashboard | Environment variables |

**Railway Secrets Setup**:
1. Log into Railway dashboard
2. Navigate to project → environment (production)
3. Add environment variables for all `*_KEY`, `*_SECRET`, `DATABASE_URL`, `REDIS_URL`
4. No `.env` file stored in production

**Rationale**: Secrets never committed to git; stored securely in platform.

---

## Files to Create/Modify

| Action | File | Purpose |
|---|---|---|
| **Modify** | `frontend/next.config.ts` | Make API URL configurable via env var |
| **Create** | `backend/railway.toml` | Railway build config |
| **Create** | `frontend/railway.toml` | Railway build config |
| **Create** | `monitor/railway.toml` | Railway build config |
| **Create** | `docker-compose.prod.yml` | Production compose (VM alternative) |
| **Create** | `.github/workflows/test.yml` | CI test pipeline |
| **Create** | `.github/workflows/deploy.yml` | CD to Railway |

**No changes to**:
- `.env` / `.env.example` - dev workflow stays as-is

---

## Verification Steps

1. **Local dev unchanged**
   - `docker compose up --build` still works with `.env` + override
   - All 5 services (backend, frontend, monitor, db, redis) start
   - Frontend accessible at `http://localhost:3000`
   - Backend accessible at `http://localhost:8000`

2. **CI/CD Pipeline**
   - Push to any branch triggers `test.yml`
   - Tests run against PostgreSQL service container
   - All 88 backend tests pass

3. **Railway Deployment**
   - Push to `main` triggers `deploy.yml`
   - Runs tests first
   - Railway auto-builds each service from its Dockerfile
   - Each service gets a public URL (backend, frontend, monitor)

4. **Post-Deploy Verification**
   - Frontend loads at `https://<frontend-railway-url>`
   - API accessible at `https://<backend-railway-url>/api/v1/health`
   - Google OAuth callback URL matches production domain
   - Email notifications work with updated SMTP config
   - Database migrations run automatically on deploy

---

## Architecture Decisions (Why)

### Why Railway?
- Multi-service Docker Compose support (unlike Replit)
- Managed DB/Redis (less ops overhead)
- Environment variables for secrets (no `.env` files in prod)
- Auto-deploy on git push (CI/CD integrated)
- Free tier for testing, $5-50/mo production tier

### Why separate `railway.toml` per service?
- Railway monorepo setup requires per-service config
- Each service builds independently
- Allows service-specific health checks

### Why make `NEXT_PUBLIC_API_URL` configurable?
- Dev uses Docker internal DNS (`http://backend:8000`)
- Production uses Railway public URL
- Frontend needs different URL per environment
- `NEXT_PUBLIC_` prefix makes it available in browser

### Why PostgreSQL over SQLite?
- JSONB support for flexible metadata storage
- ARRAY types for preferences (airlines, alliances)
- UUID native support
- Production-grade replication/backups
- Async driver (asyncpg) for FastAPI compatibility

### Why Alembic migrations?
- Schema versioning and rollback capability
- Team collaboration on DB changes
- Production deployment safety
- Reproducible environments

---

## Testing Strategy

### Current Test Coverage: 95 Backend Tests + 10 Monitor Tests

| Component | Test Count | Key Areas | Requires DB |
|---|---|---|---|
| **Backend Clients** | 48 | RapidAPI base, Skyscanner, Kiwi, normalizer, deduplication, currency conversion | No |
| **Backend Lib** | 6 | Currency conversion (convert_price) | No |
| **Backend Agents** | 9 | BaseAgent ABC, SearchAgent tool dispatch, gateway hubs | No |
| **Backend Services** | 2 | SearchService multi-source, HotelSearch stub | No |
| **Backend API** | 14 | Auth, search, trips, subscriptions CRUD, auth guards | Yes |
| **Backend Models** | 4 | User CRUD, preferences, tier, relationships | Yes |
| **Backend Subscriptions** | 8 | Email add/verify, subscription CRUD, max limits | Yes |
| **Monitor** | 10 | Price detection, rate limiting, tasks | No |
| **Total** | **105** | All core functionality | |

### Test Architecture

Tests are split into two categories by dependency:

**Unit tests (no infrastructure needed)**
- `tests/test_clients/` — API client mocking with `respx`, normalizer logic, deduplication, currency conversion
- `tests/test_lib/` — Utility tests (currency converter)
- `tests/test_agents/` — Agent instantiation, tool execution, gateway hub resolution
- `tests/test_services/` — Service logic with mocked clients (Amadeus, Skyscanner, Kiwi)
- These suites have their own `conftest.py` that overrides the root `setup_database` fixture with a no-op

**Integration tests (require PostgreSQL)**
- `tests/test_api/` — Full HTTP request/response via `httpx.AsyncClient` + ASGI transport
- `tests/test_models/` — SQLAlchemy ORM operations against real PostgreSQL
- `tests/test_subscriptions/` — Email verification flows, subscription lifecycle
- These use the root `conftest.py` which creates/drops tables per test via `setup_database` (autouse)

### Running Tests

```bash
cd backend

# Unit tests only (no DB/Redis needed)
.venv/bin/python -m pytest tests/test_clients/ tests/test_agents/ tests/test_services/ -v

# All tests (requires PostgreSQL + Redis running via Docker Compose)
.venv/bin/python -m pytest tests/ -v

# Monitor tests (separate venv, run inside Docker or set up locally)
cd ../monitor
.venv/bin/python -m pytest tests/ -v
```

**Docker hostname auto-resolution:** The root `conftest.py` automatically replaces Docker Compose internal hostnames (`@db:` → `@localhost:`, `redis://redis:` → `redis://localhost:`) so pytest works on the host machine without manual env var overrides. Tests use the forwarded ports from `docker compose up` (PostgreSQL 5432, Redis 6379).

### Test Database

- Tests use a separate database `travelai_test` (derived from `DATABASE_URL` by replacing the DB name)
- Tables are created before each test and dropped after (full isolation)
- The root `conftest.py` `setup_database` fixture is `autouse=True` — every test triggers it unless overridden

### Mocking Strategy

| What | How | Where |
|---|---|---|
| External HTTP APIs (Amadeus, RapidAPI) | `respx` (mock httpx) | `test_clients/` |
| Service-level clients | `unittest.mock.AsyncMock` + `patch.object` | `test_services/` |
| Database (for unit tests) | `conftest.py` no-op override of `setup_database` | `test_agents/`, `test_clients/`, `test_services/` |
| User fixtures (unit tests) | `MagicMock(spec=User)` | `test_services/conftest.py` |
| User fixtures (integration tests) | Real DB insert via `db_session` | root `conftest.py` |
| FastAPI dependency injection | `app.dependency_overrides[get_db]` | root `conftest.py` |

### CI (GitHub Actions)

`.github/workflows/test.yml` runs on all pushes/PRs:
1. Spins up PostgreSQL 16 service container
2. Installs backend + monitor dependencies via `uv`
3. Runs `ruff check` + `mypy` (lint + type check)
4. Runs `pytest` for backend and monitor
5. Note: CI does **not** spin up Redis — tests that need Redis should gracefully degrade

### Test Fixes Applied (Historical)
- Switched test DB from SQLite to PostgreSQL (JSONB/ARRAY support)
- Fixed enum casing (lowercase in PostgreSQL, uppercase in Python)
- Fixed connection pooling (per-test engine isolation)
- Mocked external APIs (Amadeus, Google OAuth)
- Fixed flaky timing tests (token bucket tolerance)
- Added `conftest.py` DB overrides for `test_agents/` and `test_services/` (Phase 3)
- Updated `test_search_service.py` to mock all 3 clients and assert new `SearchResponse` fields (Phase 3)
- Updated `test_api/test_search.py` assertions for `SearchResponse` format: `flights`/`total_results` (Phase 3)

---

## Next Steps (After Deployment)

1. Monitor service health on Railway
2. Set up error tracking (Sentry or similar)
3. Add frontend E2E tests (Playwright)
4. Implement rate limiting on API endpoints
5. Add comprehensive logging/observability
6. Scale monitor service for more price sources
7. Add payment processing for premium tier
8. Performance optimization (caching strategies)
