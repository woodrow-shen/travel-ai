# CLAUDE.md — Travel-AI

## Overview

Travel-AI is an intelligent travel aggregation platform that uses a multi-agent AI system (Claude API) to search, compare, and recommend flights, hotels, and activities. It provides AI-driven chat, personalized recommendations, itinerary planning, and price monitoring with email alerts.

- **Owner**: Woodrow Shen (woodrow.shen@gmail.com)
- **License**: MIT
- **Stack**: Python FastAPI + Next.js 15 + PostgreSQL 16 + Redis 7 + Docker Compose
- **AI**: Anthropic Claude (multi-agent coordinator pattern)
- **Target audience**: Taiwanese travelers (default currency TWD, Asia-Pacific gateway hubs)

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repo-url> && cd travel-ai

# 2. Copy environment file and fill in API keys
cp .env.example .env
# Edit .env: set GOOGLE_CLIENT_ID/SECRET, ANTHROPIC_API_KEY, AMADEUS keys, JWT_SECRET_KEY, SMTP creds

# 3. Start all services (dev mode with hot-reload)
docker compose up --build

# 4. Access the app
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
# Health:   http://localhost:8000/health
```

## Project Structure

```
travel-ai/
├── backend/                          # FastAPI backend (Python 3.12)
│   ├── Dockerfile                    # Multi-stage: base → development → production
│   ├── pyproject.toml                # uv + hatchling
│   ├── alembic.ini + alembic/        # DB migrations (1 migration: 001_initial_schema)
│   └── app/
│       ├── main.py                   # FastAPI app, CORS, router mounting
│       ├── config.py                 # pydantic-settings (reads .env)
│       ├── dependencies.py           # Auth guards: get_current_user, require_premium
│       ├── api/v1/                   # Route handlers (auth, search, compare, trips, chat, etc.)
│       ├── agents/                   # AI agents: base, coordinator, 5 specialists
│       │   └── tools/                # Agent tool implementations
│       ├── services/                 # Business logic layer
│       ├── clients/                  # External API clients (Amadeus + RapidAPI: Skyscanner, Kiwi)
│       ├── lib/                      # Shared utilities (currency conversion, etc.)
│       ├── models/                   # SQLAlchemy ORM (11 models)
│       ├── schemas/                  # Pydantic request/response schemas
│       ├── db/                       # session.py (async engine), redis.py
│       └── templates/emails/         # Jinja2 email templates (4 templates)
├── frontend/                         # Next.js 15 + React 19
│   ├── Dockerfile                    # Multi-stage: base → development → builder → production
│   ├── package.json
│   ├── next.config.ts                # API proxy: /api/* → backend:8000/api/v1/*
│   └── src/
│       ├── app/                      # Pages: landing, search, compare, trip, chat, auth/callback
│       ├── components/               # UI components (search, compare, chat, itinerary, layout)
│       ├── hooks/                    # useAuth, useSearch, useChat (SSE), useTrip, useCompare
│       ├── stores/                   # Zustand v5 stores (search, trip, chat)
│       ├── lib/                      # API client, utilities (cn helper)
│       └── types/                    # TypeScript type definitions
├── monitor/                          # Price monitoring daemon (Python 3.12)
│   ├── Dockerfile                    # Multi-stage: base → development → production
│   ├── pyproject.toml
│   └── app/
│       ├── main.py                   # Entry: init scheduler + start
│       ├── config.py                 # Monitoring settings (frequencies, thresholds)
│       ├── scheduler.py              # APScheduler: 3 jobs (scan, digest, cleanup)
│       ├── detector.py               # Bug fare / price drop anomaly detection
│       ├── notifier.py               # Notification dispatch (stub)
│       ├── clients/                  # Amadeus + RapidAPI clients, rate limiter (token bucket)
│       └── tasks/                    # price_scan, deal_digest, cleanup (stubs)
├── docker-compose.yml                # 5 services: backend, frontend, monitor, db, redis
├── docker-compose.override.yml       # Dev overrides: hot-reload, volume mounts, .env mount
├── docker-compose.prod.yml           # Production: Caddy proxy, no volumes, env vars only
├── .env.example                      # All required environment variables
├── .github/
│   ├── COMMIT_CONVENTION.md          # Conventional Commits + sign-off rules
│   └── workflows/
│       ├── test.yml                  # CI: lint + type-check + pytest (backend + monitor)
│       └── deploy.yml                # CD: test → deploy to Railway
└── plan.md                           # Living design document (Traditional Chinese) — keep in sync with implementation
```

## Architecture

### Service Architecture

```
┌─────────────┐     rewrites /api/*     ┌──────────────┐
│  frontend   │ ──────────────────────► │   backend    │
│ Next.js     │                         │  FastAPI     │
│ :3000       │                         │  :8000       │
└─────────────┘                         └──┬───────┬───┘
                                           │       │
                                    ┌──────▼──┐ ┌──▼──────┐
                                    │   db    │ │  redis   │
                                    │ PG:16   │ │ Redis:7  │
                                    │ :5432   │ │ :6379    │
                                    └──▲──────┘ └──▲──────┘
                                       │          │
                                    ┌──┴──────────┴──┐
                                    │    monitor     │
                                    │  APScheduler   │
                                    │  (no port)     │
                                    └────────────────┘
```

### Multi-Agent AI System (Coordinator Pattern)

```
CoordinatorAgent (orchestrator — dispatches to specialists, supports parallel execution)
  ├── SearchAgent        — flight/hotel search, gateway hubs, multi-segment, foreigner discounts
  ├── PriceAgent         — cross-source price comparison, history
  ├── RecommendationAgent — airline ratings (Skytrax), quality scoring, reviews
  ├── ItineraryAgent     — day-by-day planning, nearest-neighbor TSP route optimization
  └── BudgetAgent        — per-country daily cost estimates (TWD), budget breakdowns
```

All agents inherit `BaseAgent` (ABC) which implements the Anthropic tool-use agentic loop:
1. Send messages + tools to Claude API
2. If `stop_reason == "tool_use"` → execute tool locally → feed result back
3. Repeat until `stop_reason == "end_turn"` or max 10 turns

### Database Models (11 tables, PostgreSQL)

`User` → `UserPreference` (1:1), `Trip` (1:N), `ChatSession` (1:N), `Subscription` (1:N), `SubscriptionEmail` (1:N)
`Trip` → `Flight` (1:N), `Hotel` (1:N), `Activity` (1:N), `Itinerary` (1:N)
`Subscription` → `NotificationLog` (1:N)
`PriceHistory` (standalone — no FK)

All IDs are UUIDs. JSONB columns for flexible data (`raw_data`, `metadata`, `schedule`, `messages`, `config`). PostgreSQL ARRAY columns for preferences.

### API Endpoints (`/api/v1/`)

| Group | Endpoints | Auth |
|---|---|---|
| Health | `GET /health` | None |
| Geo | `GET /geo/currency` (IP-based currency detection) | None |
| Auth | `GET /auth/google`, `GET /auth/google/callback`, `POST /auth/refresh`, `GET /auth/me`, `PATCH /auth/me/tier`, `POST /auth/logout` | Mixed |
| Search | `POST /search/flights`, `POST /search/hotels`, `POST /search/direct` (Premium), `POST /search/adventure` | JWT |
| Compare | `POST /compare/flights`, `POST /compare/hotels` | JWT |
| Trips | `GET /`, `POST /`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` | JWT |
| Itineraries | `POST /` | JWT |
| Chat | `POST /` (SSE stream: `text`, `data`, `done` events) | JWT |
| Subscriptions | CRUD + `POST /emails`, `GET /emails/verify`, `GET /unsubscribe` | JWT (verify/unsub are token-based) |
| Users | `GET /preferences`, `PATCH /preferences` | JWT |

### Currency Conversion

Amadeus API returns prices in EUR/USD regardless of the user's locale. The system auto-converts to the user's currency:
- `app/lib/currency.py`: fetches exchange rates from `open.er-api.com` (no API key), cached in Redis for 6 hours
- `app/api/v1/geo.py`: detects user's currency from IP via `ip-api.com`, cached in Redis for 24 hours
- `normalize_amadeus_flight()` accepts optional `exchange_rates` dict to convert prices inline
- Exchange rates are fetched in parallel with flight search API calls (no added latency)
- Graceful fallback: if rates unavailable, prices stay in the original currency

### Authentication Flow

Google OAuth 2.0 (Authlib) → JWT (python-jose, HS256)
- Access token: 30 min TTL
- Refresh token: 7 day TTL
- Two tiers: `BASIC` (default) / `PREMIUM` (gates direct flight search)
- `PATCH /auth/me/tier` for dev/test tier switching (`ALLOW_TIER_SWITCH=true`)

## Development

### Common Commands

```bash
# Start dev environment (hot-reload enabled)
docker compose up --build

# Restart a single service after .env changes
docker compose restart backend

# Stop all services
docker compose down

# Stop and destroy volumes (full reset)
docker compose down -v
```

### Running Tests

```bash
# Backend tests (requires PostgreSQL running)
cd backend
uv pip install --system ".[dev]"
pytest --cov=app --cov-report=term-missing

# Monitor tests
cd monitor
uv pip install --system ".[dev]"
pytest --cov=app --cov-report=term-missing

# Frontend tests
cd frontend
npm test                # vitest (unit tests, watch mode)
npm run test:e2e        # playwright (no E2E tests written yet)
```

Test environment variables:
```
DATABASE_URL=postgresql+asyncpg://travelai:travelai_test_password@localhost:5432/travelai_test
REDIS_URL=redis://localhost:6379/0
ENV=test
SECRET_KEY=test-secret-key
```

### Linting & Type Checking

```bash
# Backend (ruff: line-length=100, rules=E,F,I,N,W,UP)
cd backend
ruff check .            # lint
ruff check . --fix      # auto-fix
ruff format .           # format
mypy app/               # type check

# Monitor
cd monitor
ruff check .
ruff format .

# Frontend
cd frontend
npm run lint            # ESLint via Next.js
```

### Database Migrations (Alembic)

```bash
cd backend
alembic upgrade head                              # apply all migrations
alembic revision --autogenerate -m "description"  # create new migration
alembic downgrade -1                              # rollback one step
alembic current                                   # show current revision
```

Note: `alembic.ini` has a hardcoded dev DB URL. For production, override via environment or `-x` flag.

### Docker Build Targets

Each Dockerfile has multi-stage builds:

| Service | Development | Production |
|---|---|---|
| backend | `uvicorn --reload` | `uvicorn --workers 4` |
| frontend | `npm run dev` (Next.js dev server) | `npm start` (production build) |
| monitor | `python -m app.main` | `python -m app.main` |

## Deployment

### Railway (Primary)

Each service has a `railway.toml` with Dockerfile builder. CI/CD via GitHub Actions:
- `test.yml`: runs on all pushes/PRs — lint + type-check + pytest with PostgreSQL service container
- `deploy.yml`: runs on push to `main` — tests first, then deploys backend/frontend/monitor in parallel

Required GitHub secret: `RAILWAY_TOKEN`

Railway environment variables to set: see `PLAN.md` section 5 or `.env.example`.

### VM with Caddy (Alternative)

```bash
docker compose -f docker-compose.prod.yml up -d
```

Requires a `Caddyfile` at project root (not yet created) for TLS termination.

## Environment Variables

See `.env.example` for the complete list. Key groups:

| Group | Variables |
|---|---|
| App | `ENV`, `DEBUG`, `SECRET_KEY`, `FRONTEND_URL`, `BACKEND_URL`, `ALLOW_TIER_SWITCH` |
| Database | `POSTGRES_*`, `DATABASE_URL` |
| Redis | `REDIS_HOST`, `REDIS_PORT`, `REDIS_URL` |
| Google OAuth | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` |
| JWT | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_REFRESH_TOKEN_EXPIRE_DAYS` |
| AI | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |
| Amadeus | `AMADEUS_API_KEY`, `AMADEUS_API_SECRET`, `AMADEUS_BASE_URL` |
| RapidAPI | `RAPIDAPI_KEY` (Skyscanner + Kiwi flight search) |
| Email | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_FROM_NAME` |
| Frontend (prod) | `NEXT_PUBLIC_API_URL` (not set in dev — uses Docker DNS fallback) |

## Technology Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | >=3.12 | Runtime |
| FastAPI | >=0.115.0 | Web framework |
| SQLAlchemy | >=2.0.0 (async) | ORM |
| asyncpg | >=0.30.0 | PostgreSQL driver |
| Alembic | >=1.14.0 | Migrations |
| Anthropic SDK | >=0.42.0 | Claude API |
| Authlib | >=1.4.0 | OAuth2 |
| python-jose | >=3.3.0 | JWT |
| FastAPI-Mail | >=1.4.0 | Email |
| APScheduler | >=3.10.0 | Task scheduling |
| uv | latest | Package manager |
| Ruff | >=0.8.0 | Lint + format |
| mypy | >=1.13.0 | Type checking |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | ^15.1.0 | React framework |
| React | ^19.0.0 | UI |
| Zustand | ^5.0.0 | State management |
| Tailwind CSS | ^4.0.0 | Styling |
| TypeScript | ^5.7.0 | Types |
| Vitest | ^2.1.0 | Testing |
| Playwright | ^1.49.0 | E2E testing |

### Infrastructure
| Technology | Version | Purpose |
|---|---|---|
| PostgreSQL | 16-alpine | Database |
| Redis | 7-alpine | Cache / sessions |
| Docker | multi-stage | Containerization |

## Development Guidelines

### Commit Convention

All commits MUST follow **Conventional Commits** with **sign-off** (`git commit -s`):

```
<type>(<scope>): <description>

Signed-off-by: Name <email>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Rules:
- Subject line under 72 characters
- Imperative mood ("add", not "added")
- One logical change per commit
- Always sign off with `-s`

See `.github/COMMIT_CONVENTION.md` for full details.

### Rolling Plan Sync

`plan.md` is the living design document (Traditional Chinese). **Whenever implementation changes deviate from or extend the plan, update `plan.md` accordingly.** The plan and codebase must always stay in sync — treat `plan.md` as the single source of truth for design decisions, not a static spec.

**IMPORTANT**: When entering plan mode for a new feature or bug fix, after the plan is finalized and approved by the user, **automatically update `plan.md`** with the agreed-upon plan content before starting implementation. Do not wait until after coding — update the plan first so it reflects the latest design decisions at all times.

### Checkpoint Validation

**IMPORTANT**: After completing every feature or bug fix, perform a checkpoint validation before considering the task done. Verify that ALL of the following are consistent with each other:

1. **Code** — the actual implementation matches the intended design
2. **Design docs** — `plan.md` and `implementation.md` are updated to reflect the changes
3. **Tests** — unit tests cover the new/changed code and all tests pass (`uv run pytest tests/ -x -q`)
4. **Lint** — no lint errors in changed files (`uv run ruff check --no-cache <changed paths>`)

If any of these are out of sync, fix them before reporting the task as complete. Do not skip this step.

## Token Efficiency Strategy

The user has a **daily usage quota** and **weekly token limit** on Claude Code. Every interaction consumes tokens. Optimize aggressively to maximize value per token spent.

### Efficiency Algorithm

Before each action, evaluate using this cost-benefit framework:

```
Priority Score = (Impact × Urgency) / Estimated Token Cost

Where:
  Impact   = 1 (trivial) to 5 (critical feature / blocking bug)
  Urgency  = 1 (nice-to-have) to 5 (blocking progress)
  Token Cost = 1 (single edit) to 5 (broad exploration + multi-file changes)
```

**Rules**:
- **Score >= 2.0** → Proceed immediately
- **Score 1.0–1.9** → Proceed, but use minimal-cost approach
- **Score < 1.0** → Defer or ask user if this is worth the token spend

### Token-Saving Practices

1. **Read before exploring** — Use targeted `Glob`/`Grep` with specific patterns instead of broad `Agent` exploration. Only escalate to Agent when directed search fails.
2. **Batch parallel operations** — When multiple independent edits/reads are needed, always combine them into a single parallel tool call.
3. **Minimal diffs** — Use `Edit` (not `Write`) for existing files. Only touch lines that need changing.
4. **Skip unnecessary verification** — If you just wrote a 1-line fix and are confident it's correct, don't re-read the entire file to verify. Trust the Edit tool's output.
5. **Concise responses** — Keep explanations short. The user prefers results over verbose commentary.
6. **Reuse context** — Don't re-read files already read in this session unless they've been modified.
7. **Defer low-priority work** — If the user is near their weekly limit (>80%), proactively flag it and suggest deferring non-critical tasks. Prioritize high-impact items only.
8. **Plan mode for complex tasks** — Enter plan mode for multi-file features to align on approach before spending tokens on implementation. A rejected implementation costs far more than a rejected plan.
9. **Subagent sparingly** — Use `Agent` tool only when the task genuinely requires deep exploration or parallel workstreams. For single-file questions, read the file directly.
10. **One-shot fixes** — For bugs, aim to fix in a single edit cycle: read → identify → fix → verify. Avoid iterative guess-and-check loops.

### Weekly Budget Awareness

When the user reports their token usage level, adjust behavior:

| Usage Level | Strategy |
|---|---|
| **< 50%** | Normal operations. Full features, thorough testing, exploratory work OK. |
| **50–70%** | Efficient mode. Combine tasks, skip non-essential exploration, shorter responses. |
| **70–85%** | Conservation mode. Focus only on high-priority tasks. Suggest deferring medium/low priority items. Minimize Agent tool usage. |
| **> 85%** | Critical mode. Only handle blocking bugs and essential fixes. Ask before any broad exploration. Suggest resuming non-urgent work after token reset. |

**Proactive check**: If the user mentions token usage (e.g., "91% weekly"), immediately acknowledge and adjust strategy for the remainder of the session.

## Known Issues & Incomplete Areas

- **RapidAPI clients**: Skyscanner + Kiwi clients are implemented but subject to rate limits (429 errors on free tier)
- **Hotel search**: `SearchAgent`, `SearchService`, `PriceService` hotel methods are stubs returning empty (TODO)
- **Price history**: `PriceAgent._get_price_history()` not wired to DB (TODO)
- **Recommendation preferences**: `RecommendationAgent._get_user_preferences()` not querying DB (TODO)
- **Monitor tasks**: `price_scan`, `deal_digest`, `cleanup` task bodies are stubs (TODO)
- **Monitor notifier**: Does not actually send emails yet (TODO)
- **Subscription email sending**: Stub in `subscription_service.py` (TODO)
- **Frontend tests**: No unit tests or E2E tests written yet
- **Caddyfile**: Referenced in `docker-compose.prod.yml` but not created
- **No Redis in CI**: GitHub Actions test workflow does not spin up Redis
