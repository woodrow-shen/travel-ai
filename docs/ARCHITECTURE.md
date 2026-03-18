# Travel-AI Technical Architecture Document

| Field       | Value                                  |
|-------------|----------------------------------------|
| **Product** | Travel-AI                              |
| **Version** | 1.0                                    |
| **Date**    | 2026-03-13                             |
| **Owner**   | Woodrow Shen (woodrow.shen@gmail.com)  |
| **License** | MIT                                    |

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Monitor Service Architecture](#monitor-service-architecture)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Data Flow and Integration](#data-flow-and-integration)
7. [Email and Notification System](#email-and-notification-system)
8. [Infrastructure and Deployment](#infrastructure-and-deployment)
9. [Testing Architecture](#testing-architecture)
10. [Architecture Decision Records](#architecture-decision-records)

---

## System Overview

Travel-AI is an intelligent travel aggregation platform that uses a multi-agent AI system (Anthropic Claude) to search, compare, and recommend flights, hotels, and activities. It provides AI-driven chat, personalized recommendations, itinerary planning, and price monitoring with email alerts.

**Target audience:** Taiwanese travelers (default currency TWD, Asia-Pacific gateway hubs).

### Technology Stack

| Layer          | Technology                                | Version    |
|----------------|-------------------------------------------|------------|
| Backend        | Python, FastAPI, SQLAlchemy (async)       | 3.12, 0.115+ |
| Frontend       | Next.js, React, Zustand, Tailwind CSS     | 15, 19, 5, 4 |
| Database       | PostgreSQL (asyncpg driver)               | 16         |
| Cache          | Redis                                     | 7          |
| AI             | Anthropic Claude SDK                      | 0.42+      |
| Auth           | Google OAuth 2.0 (Authlib) + JWT (python-jose) | --     |
| Scheduling     | APScheduler                               | 3.10+      |
| Email          | FastAPI-Mail (Jinja2 templates, SMTP)     | 1.4+       |
| Migrations     | Alembic                                   | 1.14+      |
| Package Mgmt   | uv (Python), npm (Node.js)               | latest     |
| Containerization | Docker, Docker Compose                  | multi-stage |

### High-Level Architecture

```
                         ┌─────────────────┐
                         │    Browser /     │
                         │   Mobile Client  │
                         └────────┬────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     frontend (Next.js)     │
                    │     :3000                  │
                    │   rewrites /api/* ─────────┼──────┐
                    └───────────────────────────┘      │
                                                       ▼
                                           ┌───────────────────┐
                                           │  backend (FastAPI) │
                                           │  :8000             │
                                           └──┬────────┬───────┘
                                              │        │
                        ┌─────────────────────┤        ├──────────────────┐
                        ▼                     ▼        ▼                  ▼
                ┌──────────────┐    ┌──────────┐  ┌─────────┐   ┌───────────────┐
                │  PostgreSQL  │    │  Redis   │  │ Claude  │   │ External APIs │
                │  :5432       │    │  :6379   │  │   API   │   │ Amadeus,      │
                │  (16-alpine) │    │ (7-alpine)│  │         │   │ Skyscanner,   │
                └──────▲───────┘    └────▲─────┘  └─────────┘   │ Kiwi          │
                       │                 │                       └───────────────┘
                       │                 │
                ┌──────┴─────────────────┴──────┐
                │     monitor (APScheduler)     │
                │     (no exposed port)         │
                └───────────────────────────────┘
```

**Services:**

| Service    | Role                                                   | Port  |
|------------|--------------------------------------------------------|-------|
| `frontend` | Next.js 15 app; proxies `/api/*` requests to backend   | 3000  |
| `backend`  | FastAPI REST API, AI agent orchestration, business logic | 8000  |
| `db`       | PostgreSQL 16 with JSONB and ARRAY column support       | 5432  |
| `redis`    | Cache layer for search results, exchange rates, sessions | 6379  |
| `monitor`  | Background daemon for price scanning and deal alerts     | none  |

---

## Backend Architecture

### Database Models (11 Tables)

All primary keys are UUIDs. JSONB columns store flexible data (`raw_data`, `metadata`, `schedule`, `messages`, `config`). PostgreSQL ARRAY columns store preference lists.

```
User ──┬── UserPreference  (1:1)
       ├── Trip            (1:N) ──┬── Flight     (1:N)
       ├── ChatSession     (1:N)   ├── Hotel      (1:N)
       ├── Subscription    (1:N)   ├── Activity   (1:N)
       └── SubscriptionEmail (1:N) └── Itinerary  (1:N)

Subscription ── NotificationLog  (1:N)
PriceHistory  (standalone, no FK)
```

**Table details:**

| Table                | Key Fields                                                                 |
|----------------------|----------------------------------------------------------------------------|
| `users`              | id, email, name, avatar_url, google_id, tier (basic/premium), last_login   |
| `user_preferences`   | user_id, preferred_airlines[], excluded_airlines[], preferred_alliances[], cabin_classes[], max_stops, home_airports[] |
| `trips`              | user_id, title, description, destination, start_date, end_date, metadata (JSONB) |
| `flights`            | trip_id, airline, flight_no, origin, destination, departure, arrival, stops, duration_minutes, cabin_class, price_*, source, raw_data (JSONB) |
| `hotels`             | trip_id, name, location, check_in, check_out, stars, rating, price_per_night, source, raw_data (JSONB) |
| `activities`         | trip_id, name, location, description, start_time, end_time, price_*, category, source, raw_data (JSONB) |
| `price_history`      | origin, destination, departure_date, return_date, airline, price_*, source, cabin_class, stops, raw_data (JSONB) |
| `itineraries`        | trip_id, title, description, schedule (JSONB day-by-day breakdown)          |
| `chat_sessions`      | user_id, title, messages[] (JSONB message history)                         |
| `subscriptions`      | user_id, type (bug_fare/price_drop/deal_digest), origin, destination, date_from, date_to, price_threshold, active, raw_filter (JSONB) |
| `subscription_emails`| user_id, email, verified, subscribed_types[], created_at                   |
| `notification_log`   | Audit trail for sent notifications (linked to Subscription)                |

### API Endpoints

All endpoints are under the `/api/v1/` prefix.

**Health and Geo (no auth)**

| Method | Path             | Description                                      |
|--------|------------------|--------------------------------------------------|
| GET    | `/health`        | Service health check                             |
| GET    | `/geo/currency`  | IP-based currency detection (ip-api.com, cached 24h in Redis) |

**Auth (mixed auth)**

| Method | Path                      | Auth    | Description                              |
|--------|---------------------------|---------|------------------------------------------|
| GET    | `/auth/google`            | None    | Initiate Google OAuth flow               |
| GET    | `/auth/google/callback`   | None    | Google OAuth callback                    |
| POST   | `/auth/refresh`           | None    | Refresh access token                     |
| GET    | `/auth/me`                | JWT     | Get authenticated user profile           |
| PATCH  | `/auth/me/tier`           | JWT     | Switch tier (dev-only, `ALLOW_TIER_SWITCH=true`) |
| POST   | `/auth/logout`            | JWT     | Logout and invalidate session            |

**Search (JWT required)**

| Method | Path                 | Description                                        |
|--------|----------------------|----------------------------------------------------|
| POST   | `/search/flights`    | Multi-source flight search (Amadeus + Skyscanner + Kiwi) |
| POST   | `/search/hotels`     | Hotel search (stub)                                |
| POST   | `/search/direct`     | Direct flights only (Premium tier required)        |
| POST   | `/search/adventure`  | Inspiration mode search                            |

**Compare (JWT required)**

| Method | Path               | Description                                          |
|--------|--------------------|------------------------------------------------------|
| POST   | `/compare/flights`  | Multi-source flight comparison                      |
| POST   | `/compare/hotels`   | Hotel comparison                                    |

**Trips (JWT required)**

| Method | Path            | Description        |
|--------|-----------------|--------------------|
| GET    | `/trips`        | List user trips    |
| POST   | `/trips`        | Create trip        |
| GET    | `/trips/{id}`   | Get trip details   |
| PATCH  | `/trips/{id}`   | Update trip        |
| DELETE | `/trips/{id}`   | Delete trip        |

**Itineraries (JWT required)**

| Method | Path             | Description                     |
|--------|------------------|---------------------------------|
| POST   | `/itineraries`   | Generate itinerary from trip    |

**Chat (JWT required)**

| Method | Path      | Description                                          |
|--------|-----------|------------------------------------------------------|
| POST   | `/chat`   | Send message; returns SSE stream (`text`, `data`, `done` events) |

**Subscriptions (JWT required, except token-based verify/unsubscribe)**

| Method | Path                          | Description                  |
|--------|-------------------------------|------------------------------|
| GET    | `/subscriptions`              | List subscriptions           |
| POST   | `/subscriptions`              | Create subscription          |
| PATCH  | `/subscriptions/{id}`         | Update subscription          |
| DELETE | `/subscriptions/{id}`         | Delete subscription          |
| POST   | `/subscriptions/emails`       | Add subscriber email         |
| GET    | `/subscriptions/emails/verify`| Verify email (token-based)   |
| GET    | `/subscriptions/unsubscribe`  | Unsubscribe (token-based)    |

**Users (JWT required)**

| Method | Path                  | Description               |
|--------|-----------------------|---------------------------|
| GET    | `/users/preferences`  | Get user travel preferences |
| PATCH  | `/users/preferences`  | Update preferences         |

### Multi-Agent AI System

The AI system follows a coordinator pattern where a central orchestrator dispatches requests to specialist agents. All agents support parallel execution.

```
CoordinatorAgent (orchestrator)
  ├── SearchAgent           — flight/hotel search, gateway hubs, foreigner discounts
  ├── PriceAgent            — cross-source price comparison, history
  ├── RecommendationAgent   — airline ratings (Skytrax), quality scoring
  ├── ItineraryAgent        — day-by-day planning, nearest-neighbor TSP optimization
  └── BudgetAgent           — per-country daily cost estimates (TWD), budget breakdowns
```

**Agent execution loop (BaseAgent):**

All agents inherit from `BaseAgent` (ABC) which implements the Anthropic tool-use agentic loop:

1. Send messages + tool definitions to Claude API.
2. If `stop_reason == "tool_use"`, execute the tool locally, feed the result back.
3. Repeat until `stop_reason == "end_turn"` or max 10 turns.

**CoordinatorAgent** routes user messages to specialist agents, orchestrates multi-agent responses, and maintains chat context across turns.

### Services Layer

| Service               | Responsibility                                                                |
|-----------------------|-------------------------------------------------------------------------------|
| `SearchService`       | Multi-source flight search (Amadeus + Skyscanner + Kiwi parallel query), normalizer, deduplication, Redis cache; fetches exchange rates in parallel for currency conversion |
| `PriceService`        | Multi-source price comparison + unified compare via Redis cache; parallel exchange rate fetch |
| `ChatService`         | SSE streaming, agent orchestration                                            |
| `ItineraryService`    | Schedule generation, optimization                                             |
| `SubscriptionService` | Subscription CRUD, email verification lifecycle                               |
| `EmailService`        | SMTP dispatch, Jinja2 templated notifications                                 |
| `NotificationService` | Alert dispatch routing                                                        |

### External API Clients

**AmadeusClient**
- Flight search (`search_flights`), hotel search (`search_hotels`), inspiration search (`search_inspiration`)
- OAuth2 client credentials auth with automatic token refresh

**RapidAPIBaseClient** (abstract base)
- Shared `httpx.AsyncClient` instance
- Automatic `x-rapidapi-key` / `x-rapidapi-host` header injection
- Graceful error handling: returns empty dict/list on failure

**SkyscannerClient** (extends RapidAPIBaseClient)
- `search_flights` (one-way and roundtrip), `search_flights_incomplete` (polling), `search_everywhere`, `price_calendar`, `search_hotels`, `autocomplete`

**KiwiClient** (extends RapidAPIBaseClient)
- `search_flights` (one-way and return, with stops parameter), `search_deals`, `price_trends`, `search_hotels`, `autocomplete`

**Normalizer** (`app/clients/normalizer.py`)

Converts provider-specific flight data into a unified format:

| Function                          | Description                                              |
|-----------------------------------|----------------------------------------------------------|
| `normalize_amadeus_flight()`      | Accepts optional `exchange_rates` dict for currency conversion |
| `normalize_skyscanner_flight()`   | Prices already in requested currency                     |
| `normalize_kiwi_flight()`         | Prices already in requested currency                     |
| `deduplicate_flights()`           | Keeps lowest price per flight_number + departure_time    |
| `normalized_dict_to_flight_result()` | Converts normalized dict to `FlightResult` Pydantic model |
| `_parse_iso_duration()`           | Converts PT5H30M to minutes                              |

---

## Frontend Architecture

### Pages

| Page            | Path                  | Description                          |
|-----------------|-----------------------|--------------------------------------|
| Landing         | `/[locale]`                   | Marketing and introduction           |
| Search          | `/[locale]/search`             | Flight/hotel search form + results   |
| Compare         | `/[locale]/compare`            | Side-by-side comparison view         |
| Trip            | `/[locale]/trip`               | Trip planner and itinerary display   |
| Chat            | `/[locale]/chat`               | AI chat interface                    |
| Settings        | `/[locale]/settings/*`         | User preferences and subscriptions   |
| Auth Callback   | `/[locale]/auth/callback`      | OAuth redirect handler               |

### Components

| Component        | Description                            |
|------------------|----------------------------------------|
| `SearchForm`     | Multi-field search input               |
| `FlightCard`     | Flight result display card             |
| `HotelCard`      | Hotel result display card              |
| `CompareTable`   | Side-by-side comparison table          |
| `ChatWindow`     | Chat interface container               |
| `ChatMessage`    | Individual message display             |
| `ItineraryView`  | Day-by-day schedule renderer           |
| `Header`/`Footer`| Layout components                     |
| `LanguageSwitcher` | Locale toggle (zh-TW ↔ en)         |
| `Button`/`Input`/`Card` | Shared UI primitives            |

### Hooks

| Hook           | Purpose                                  |
|----------------|------------------------------------------|
| `useAuth()`    | Authentication state + Google login flow |
| `useSearch()`  | Search form state and result management  |
| `useChat()`    | SSE message streaming                    |
| `useTrip()`    | Trip CRUD management                     |
| `useCompare()` | Comparison logic and state               |

### State Management (Zustand v5)

| Store          | State                                    |
|----------------|------------------------------------------|
| `searchStore`  | Search criteria, results, filters        |
| `tripStore`    | Current trip, flights, hotels, activities |
| `chatStore`    | Messages, session ID, loading state      |

### API Communication

The frontend communicates with the backend through a Next.js API proxy:

- **Rewrite rule:** `/api/:path*` is rewritten to `http://backend:8000/api/v1/:path*`
- **Development:** Uses Docker internal DNS (`http://backend:8000`) as fallback
- **Production:** Uses `NEXT_PUBLIC_API_URL` environment variable (set to the backend's public URL)

The `NEXT_PUBLIC_` prefix makes the variable available in the browser bundle.

---

## Monitor Service Architecture

The monitor is a headless Python daemon that runs alongside the main application. It shares the PostgreSQL database and Redis cache with the backend.

### Components

| Component          | Description                                                      |
|--------------------|------------------------------------------------------------------|
| `scheduler.py`     | APScheduler with three registered jobs                           |
| `detector.py`      | Anomaly detection for bug fares and gradual price drops          |
| `notifier.py`      | Notification dispatch (stub)                                     |
| `clients/`         | AmadeusClient + RapidAPI clients with token-bucket rate limiter  |

### Scheduled Tasks

| Task           | Frequency   | Description                                |
|----------------|-------------|--------------------------------------------|
| `price_scan`   | Every 6h    | Scan active subscriptions for price changes |
| `deal_digest`  | Every 24h   | Compile and send daily deal digest emails   |
| `cleanup`      | Daily       | Purge stale price history and expired data  |

### Detection Algorithms

The `detector.py` module implements two detection strategies:

1. **Bug fare detection** -- identifies anomalously low prices that deviate significantly from historical averages, suggesting potential pricing errors.
2. **Price drop trend analysis** -- tracks gradual price decreases over time and triggers alerts when a watched route drops below a user-defined threshold.

---

## Authentication and Authorization

### OAuth Flow

```
1. Browser        GET /auth/google
2. Browser   -->  Google OAuth consent screen
3. Google    -->  GET /auth/google/callback?code=...
4. Backend        Exchange code for Google user profile
5. Backend        Create or update User in DB
6. Backend        Issue JWT access + refresh tokens
7. Browser        Stores tokens; sends access token in Authorization header
```

### JWT Token Configuration

| Token          | TTL     | Payload                         | Algorithm |
|----------------|---------|----------------------------------|-----------|
| Access token   | 30 min  | user_id, email, tier             | HS256     |
| Refresh token  | 7 days  | Used to mint new access tokens   | HS256     |

Signing secret: `JWT_SECRET_KEY` environment variable.

### User Tiers

| Tier      | Capabilities                                                     |
|-----------|------------------------------------------------------------------|
| **Basic** | Search, compare, trips, chat, 1 subscription                    |
| **Premium** | All Basic features + direct flight search, adventure mode, unlimited subscriptions |

Tier switching is available for development and testing only when `ALLOW_TIER_SWITCH=true` is set in the environment.

---

## Data Flow and Integration

### Multi-Source Flight Search

```
SearchService.search_flights()
  │
  ├── [parallel] AmadeusClient.search_flights()
  ├── [parallel] SkyscannerClient.search_flights()
  ├── [parallel] KiwiClient.search_flights()
  └── [parallel] get_exchange_rates()
  │
  ▼
  normalize_amadeus_flight(offer, exchange_rates)
  normalize_skyscanner_flight(leg)
  normalize_kiwi_flight(flight)
  │
  ▼
  deduplicate_flights()     # lowest price per flight_number + departure_time
  │
  ▼
  Cache results in Redis    # keyed by search params, short TTL
  │
  ▼
  Return SearchResponse { flights, total_results, sources }
```

### Currency Conversion

Amadeus API returns prices in EUR/USD regardless of the user's locale. The system auto-converts to the user's preferred currency.

| Component                | Description                                                    |
|--------------------------|----------------------------------------------------------------|
| `app/lib/currency.py`   | Fetches exchange rates from `open.er-api.com` (no API key needed), cached in Redis for 6 hours |
| `app/api/v1/geo.py`     | Detects user's currency from IP via `ip-api.com`, cached in Redis for 24 hours |
| `normalize_amadeus_flight()` | Accepts optional `exchange_rates` dict to convert prices inline |

Exchange rates are fetched in parallel with flight search API calls, adding no extra latency. If rates are unavailable, prices remain in the original currency (graceful fallback).

### RapidAPI Rate Limiting

Both Skyscanner and Kiwi clients operate through RapidAPI's free tier, which imposes rate limits. The `RapidAPIBaseClient` handles HTTP 429 responses gracefully by returning empty results rather than raising exceptions. The monitor service uses an additional token-bucket rate limiter to stay within API quotas.

---

## Email and Notification System

### Subscription Email Lifecycle

1. User creates a subscription via the API.
2. A verification email is sent to the `SubscriptionEmail` address.
3. User clicks the verification link (token-based, valid for 7 days, single-use).
4. Once verified, price alerts are sent to the address.
5. Each email includes an unsubscribe link with a unique token.

### Email Templates (Jinja2)

| Template                     | Trigger                              |
|------------------------------|--------------------------------------|
| `bug_fare_alert.html`        | Anomalously low fare detected        |
| `price_drop_alert.html`      | Price decreased for a watched route  |
| `deal_digest.html`           | Weekly digest of deal opportunities  |
| `email_verification.html`    | Email address verification request   |

### SMTP Configuration

| Variable        | Default           | Description          |
|-----------------|-------------------|----------------------|
| `SMTP_HOST`     | `smtp.gmail.com`  | SMTP server hostname |
| `SMTP_PORT`     | `587`             | TLS port             |
| `SMTP_USER`     | --                | Email account        |
| `SMTP_PASSWORD`  | --               | App password         |
| `EMAIL_FROM`    | `noreply@travel-ai.com` | Sender address |
| `EMAIL_FROM_NAME`| `Travel-AI`      | Sender display name  |

---

## Infrastructure and Deployment

### Docker Compose (Development)

Development uses `docker-compose.yml` with `docker-compose.override.yml` for hot-reload volume mounts:

```bash
docker compose up --build
```

All five services start: backend (:8000), frontend (:3000), monitor, db (:5432), redis (:6379).

### Docker Build Targets

Each Dockerfile uses multi-stage builds:

| Service    | Development Target       | Production Target             |
|------------|--------------------------|-------------------------------|
| `backend`  | `uvicorn --reload`       | `uvicorn --workers 4`         |
| `frontend` | `npm run dev` (HMR)     | `npm start` (production build)|
| `monitor`  | `python -m app.main`     | `python -m app.main`          |

### Railway Deployment (Primary)

Each service has a `railway.toml` with Dockerfile builder configuration. Railway provides managed PostgreSQL and Redis add-ons.

**CI/CD via GitHub Actions:**

| Workflow       | Trigger              | Steps                                           |
|----------------|----------------------|--------------------------------------------------|
| `test.yml`     | All pushes and PRs   | Spin up PostgreSQL service container, lint (`ruff check`), type-check (`mypy`), run `pytest` for backend and monitor |
| `deploy.yml`   | Push to `main`       | Run tests, then deploy backend/frontend/monitor to Railway in parallel |

Required GitHub secret: `RAILWAY_TOKEN`.

### VM Deployment (Alternative)

```bash
docker compose -f docker-compose.prod.yml up -d
```

Uses production build targets, no volume mounts, reads environment variables directly (no `.env` file). Includes a Caddy reverse proxy for automatic TLS via Let's Encrypt.

### Secrets Management

| Environment | Storage              | Method                        |
|-------------|----------------------|-------------------------------|
| Development | `.env` file          | Local file (gitignored)       |
| Production  | Railway Dashboard    | Platform environment variables |

Secrets are never committed to version control.

### Environment Variables

See `.env.example` for the complete list. Key variable groups:

| Group         | Variables                                                              |
|---------------|------------------------------------------------------------------------|
| App           | `ENV`, `DEBUG`, `SECRET_KEY`, `FRONTEND_URL`, `BACKEND_URL`, `ALLOW_TIER_SWITCH` |
| Database      | `POSTGRES_*`, `DATABASE_URL`                                           |
| Redis         | `REDIS_HOST`, `REDIS_PORT`, `REDIS_URL`                               |
| Google OAuth  | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`     |
| JWT           | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_REFRESH_TOKEN_EXPIRE_DAYS` |
| AI            | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`                                 |
| Amadeus       | `AMADEUS_API_KEY`, `AMADEUS_API_SECRET`, `AMADEUS_BASE_URL`           |
| RapidAPI      | `RAPIDAPI_KEY` (shared by Skyscanner + Kiwi)                          |
| Email         | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_FROM_NAME` |
| Frontend (prod) | `NEXT_PUBLIC_API_URL`                                                |

---

## Testing Architecture

### Test Summary

| Component               | Test Count | Key Areas                                          | Requires DB |
|-------------------------|------------|-----------------------------------------------------|-------------|
| Backend Clients         | 48         | RapidAPI base, Skyscanner, Kiwi, normalizer, dedup, currency | No |
| Backend Lib             | 6          | Currency conversion (`convert_price`)                | No          |
| Backend Agents          | 9          | BaseAgent ABC, SearchAgent tool dispatch, gateway hubs | No       |
| Backend Services        | 2          | SearchService multi-source, HotelSearch stub         | No          |
| Backend API             | 14         | Auth, search, trips, subscriptions CRUD, auth guards | Yes         |
| Backend Models          | 4          | User CRUD, preferences, tier, relationships          | Yes         |
| Backend Subscriptions   | 8          | Email add/verify, subscription CRUD, max limits      | Yes         |
| Monitor                 | 10         | Price detection, rate limiting, tasks                | No          |
| **Total**               | **105**    |                                                      |             |

### Test Categories

**Unit tests (no infrastructure required):**

- `tests/test_clients/` -- API client mocking with `respx`, normalizer logic, deduplication, currency conversion
- `tests/test_lib/` -- Utility tests (currency converter)
- `tests/test_agents/` -- Agent instantiation, tool execution, gateway hub resolution
- `tests/test_services/` -- Service logic with mocked clients (Amadeus, Skyscanner, Kiwi)

These suites have their own `conftest.py` that overrides the root `setup_database` fixture with a no-op.

**Integration tests (require PostgreSQL):**

- `tests/test_api/` -- Full HTTP request/response via `httpx.AsyncClient` + ASGI transport
- `tests/test_models/` -- SQLAlchemy ORM operations against real PostgreSQL
- `tests/test_subscriptions/` -- Email verification flows, subscription lifecycle

These use the root `conftest.py` which creates/drops tables per test via `setup_database` (autouse).

### Test Database

- Tests use a separate database `travelai_test` (derived from `DATABASE_URL` by replacing the DB name).
- Tables are created before each test and dropped after for full isolation.
- The root `conftest.py` automatically replaces Docker Compose internal hostnames (`@db:` to `@localhost:`, `redis://redis:` to `redis://localhost:`) so pytest works on the host machine without manual environment variable overrides.

### Mocking Strategy

| Target                              | Technique                                | Test Location          |
|-------------------------------------|------------------------------------------|------------------------|
| External HTTP APIs (Amadeus, RapidAPI) | `respx` (mock httpx)                  | `test_clients/`        |
| Service-level clients               | `unittest.mock.AsyncMock` + `patch.object` | `test_services/`    |
| Database (for unit tests)           | `conftest.py` no-op override of `setup_database` | `test_agents/`, `test_clients/`, `test_services/` |
| User fixtures (unit tests)          | `MagicMock(spec=User)`                   | `test_services/conftest.py` |
| User fixtures (integration tests)   | Real DB insert via `db_session`          | root `conftest.py`     |
| FastAPI dependency injection        | `app.dependency_overrides[get_db]`       | root `conftest.py`     |

### CI Pipeline

The `.github/workflows/test.yml` workflow runs on all pushes and PRs:

1. Spin up PostgreSQL 16 service container.
2. Install backend + monitor dependencies via `uv`.
3. Run `ruff check` and `mypy` (lint + type check).
4. Run `pytest` for backend and monitor.

Note: CI does not spin up Redis. Tests that require Redis should degrade gracefully.

---

## Architecture Decision Records

### ADR-1: PostgreSQL over SQLite

**Decision:** Use PostgreSQL 16 as the primary database.

**Rationale:**
- Native JSONB support for flexible metadata storage (raw API responses, schedules, messages).
- ARRAY column types for preference lists (airlines, alliances, cabin classes).
- Native UUID support for primary keys.
- Async driver (`asyncpg`) for non-blocking I/O with FastAPI.
- Production-grade replication, backups, and connection pooling.

### ADR-2: Multi-Source Flight Search with Normalizer

**Decision:** Query Amadeus, Skyscanner, and Kiwi in parallel and normalize results into a unified format.

**Rationale:**
- No single API provides comprehensive global coverage.
- Parallel execution eliminates sequential latency.
- The normalizer layer isolates provider-specific data formats from business logic.
- Deduplication ensures users see the best price per flight.

### ADR-3: Coordinator Agent Pattern

**Decision:** Use a coordinator agent that dispatches to specialist agents rather than a monolithic AI agent.

**Rationale:**
- Each specialist agent has a focused tool set and system prompt, improving response quality.
- The coordinator can dispatch to multiple agents in parallel for complex queries.
- Adding a new capability means adding a new specialist without modifying existing ones.

### ADR-4: Railway for Production Hosting

**Decision:** Deploy to Railway as the primary production platform.

**Rationale:**
- Native multi-service Docker Compose support.
- Managed PostgreSQL and Redis add-ons (reduced operational overhead).
- Environment variable management for secrets (no `.env` files in production).
- Auto-deploy on git push with integrated CI/CD.
- Cost-effective pricing tiers.

### ADR-5: Configurable Frontend API URL

**Decision:** Make the frontend API URL configurable via `NEXT_PUBLIC_API_URL` with a Docker DNS fallback.

**Rationale:**
- Development uses Docker internal DNS (`http://backend:8000`).
- Production uses a public URL (e.g., Railway's generated URL).
- The `NEXT_PUBLIC_` prefix ensures the variable is available in the browser bundle.

### ADR-6: Alembic for Schema Migrations

**Decision:** Use Alembic for all database schema changes.

**Rationale:**
- Version-controlled schema changes with rollback capability.
- Safe production deployments with migration ordering.
- Reproducible environments across development, CI, and production.
- Team collaboration on concurrent schema changes.

### ADR-7: Redis for Ephemeral Caching

**Decision:** Use Redis for search result caching, exchange rates, and session data.

**Rationale:**
- Search results are ephemeral (prices change frequently) and benefit from short-TTL caching.
- Exchange rates are fetched from an external API and cached for 6 hours to avoid excessive calls.
- IP-based currency detection is cached for 24 hours.
- Redis provides atomic operations and TTL expiry without additional application logic.

### ADR-8: SSE for Chat Streaming

**Decision:** Use Server-Sent Events (SSE) for AI chat responses rather than WebSockets.

**Rationale:**
- Chat is a unidirectional stream (server to client) during response generation.
- SSE is simpler to implement and debug than WebSocket connections.
- Native browser support via `EventSource` API.
- Compatible with HTTP/2 and standard reverse proxies without special configuration.

### ADR-9: next-intl for Frontend i18n

**Decision:** Use `next-intl` with URL path prefix (`localePrefix: "as-needed"`) for frontend internationalization.

**Rationale:**
- Best integration with Next.js 15 App Router (`[locale]` dynamic segment, server/client components).
- `localePrefix: "as-needed"` — default locale (zh-TW) has no URL prefix; `/en/*` for English. Clean URLs for primary audience.
- Built-in middleware for locale detection and routing.
- ICU message format for plurals and interpolation.
- Locale resolution order: URL path prefix → Accept-Language header → default (zh-TW).
- Backend locale resolution: Accept-Language header → user `preferred_language` in DB → default (zh-TW).

---

## Known Limitations

The following areas are currently stubs or incomplete:

| Area                          | Status                                           |
|-------------------------------|--------------------------------------------------|
| Caddyfile                     | Referenced in `docker-compose.prod.yml` but not created |
