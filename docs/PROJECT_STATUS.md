# Travel-AI Project Status Tracker

| Field         | Value                                  |
|---------------|----------------------------------------|
| **Product**   | Travel-AI                              |
| **Version**   | 0.2.0                                  |
| **Date**      | 2026-03-15                             |
| **Owner**     | Woodrow Shen (woodrow.shen@gmail.com)  |
| **Status**    | Active Development                     |

> **Purpose**: Single source of truth for project progress, feature completion, and outstanding work items. Updated after each milestone.

---

## Overall Progress

```
Features       ██████████████████░░░░  86%  (74/86 items)
Infrastructure ████████████████░░░░░░  85%  (11/13 items)
Quality        ███████████████░░░░░░░  70%  (19/27 items)
Documentation  █████████████████░░░░░  73%  (8/11 items)
─────────────────────────────────────────────
OVERALL        █████████████████░░░░░  82%  (112/137 items)
```

| Category | Done | Total | Remaining | Blocked |
|----------|------|-------|-----------|---------|
| Features (§3) | 74 | 86 | 7 | 5 (hotel, on hold) |
| Infrastructure (§4) | 11 | 13 | 2 | 0 |
| Quality Assurance (§5) | 19 | 27 | 8 | 0 |
| Documentation (§6) | 8 | 11 | 3 | 1 |
| **Total** | **109** | **137** | **23** | **6** |

**Top blockers**: None — all remaining items are unblocked and ready for development.

**Next priorities**: Production deployment (Medium). Hotel search is **on hold** pending Skyscanner/Kiwi hotel API verification.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Milestone Overview](#2-milestone-overview)
3. [Feature Completion Checklist](#3-feature-completion-checklist)
4. [Infrastructure & DevOps Checklist](#4-infrastructure--devops-checklist)
5. [Quality Assurance Checklist](#5-quality-assurance-checklist)
6. [Documentation Checklist](#6-documentation-checklist)
7. [Known Issues & Technical Debt](#7-known-issues--technical-debt)
8. [Upcoming Work (Prioritized Backlog)](#8-upcoming-work-prioritized-backlog)
9. [Release History](#9-release-history)

---

## 1. Executive Summary

Travel-AI is an intelligent travel aggregation platform targeting Taiwanese travelers. The core platform (multi-agent AI, flight search, price monitoring, subscription alerts) is **feature-complete for MVP**. Current focus is on hardening test coverage and production readiness. Hotel search is **on hold** pending verification of Skyscanner/Kiwi hotel API availability on free tier.

| Metric                  | Value      |
|-------------------------|------------|
| Backend test count      | 105        |
| Monitor test count      | 20         |
| Frontend test count     | 111        |
| E2E test count          | 0          |
| Total API endpoints     | 25+        |
| Database tables         | 11         |
| AI agents               | 6 (1 coordinator + 5 specialists) |
| External data sources   | 4 (Amadeus, Skyscanner, Kiwi, Google Flights) |
| Docker services         | 5          |

---

## 2. Milestone Overview

| Phase | Name                                | Status           | Completion |
|-------|-------------------------------------|------------------|------------|
| 1     | Foundation & Infrastructure         | **Complete**     | 100%       |
| 2     | AI Agent System                     | **Complete**     | 100%       |
| 3     | External API Integration            | **Complete**     | 100%       |
| 4     | Multi-Source Service Layer + Frontend | **Complete**   | 100%       |
| 5     | Price Monitoring Daemon             | **Complete**     | 100%       |
| 6     | Test Coverage                       | **In Progress**  | 75%        |
| 7     | Upcoming Features                   | **Planned**      | 0%         |

---

## 3. Feature Completion Checklist

### 3.1 Authentication & User Management

- [x] Google OAuth 2.0 login (Authlib)
- [x] JWT access token (30 min) + refresh token (7 days)
- [x] User tiers: Basic / Premium
- [x] Dev tier switch API (`PATCH /auth/me/tier`)
- [x] User preferences CRUD (`GET/PATCH /preferences`)
- [x] User preferences settings page (`/settings/preferences`)
- [x] User dropdown menu (Subscriptions, Preferences, Sign out)

### 3.2 Flight Search

- [x] Amadeus Flight Offers Search (one-way, roundtrip)
- [x] Skyscanner flight search (one-way, roundtrip, incomplete)
- [x] Kiwi flight search (one-way, return)
- [x] Google Flights API integration as 4th flight search source (RapidAPI)
- [x] Multi-source parallel search with unified normalizer
- [x] Search results deduplication
- [x] Redis caching for search results
- [x] Direct mode — best non-stop flights (Premium)
- [x] Adventure mode — cheapest destinations from origin
- [x] Currency auto-detection (IP-based) + conversion (EUR/USD → user currency)
- [x] Search form state persistence (localStorage)

### 3.3 Flight Comparison

- [x] Cross-source price comparison endpoint (`POST /compare/flights`)
- [x] Floating comparison bar in frontend
- [x] Dark mode badges for source labels
- [x] Roundtrip compare label
- [x] 429 backoff handling for RapidAPI

### 3.4 Hotel Search (⏸️ On Hold)

> **On hold since 2026-03-14**: Skyscanner/Kiwi hotel APIs not yet verified on free tier. All hotel items deferred until API availability is confirmed.

- [ ] SearchService hotel method (stub → real integration) — ⏸️ on hold
- [ ] PriceService hotel method (stub → real integration) — ⏸️ on hold
- [ ] Hotel comparison endpoint — ⏸️ on hold
- [ ] Frontend hotel search page — ⏸️ on hold
- [ ] Frontend hotel comparison — ⏸️ on hold

### 3.5 AI Chat System

- [x] CoordinatorAgent (orchestrator with parallel dispatch)
- [x] SearchAgent — flight/hotel search, gateway hubs, multi-segment
- [x] PriceAgent — cross-source comparison
- [x] RecommendationAgent — airline ratings, quality scoring
- [x] ItineraryAgent — day-by-day planning, TSP route optimization
- [x] BudgetAgent — per-country daily cost estimates (TWD)
- [x] SSE streaming chat endpoint
- [x] Multi-turn conversation support
- [x] Agent layer integrated with multi-source search (Amadeus + Skyscanner + Kiwi + Google Flights)
- [x] PriceAgent wired to price_history DB (trend analysis: increasing/decreasing/stable)
- [x] RecommendationAgent wired to user preferences DB

### 3.6 Trip Management

- [x] Trip CRUD (create, read, update, delete)
- [x] Flight / Hotel / Activity / Itinerary associations
- [x] Trip detail page in frontend
- [x] Itinerary generation endpoint

### 3.7 Subscription & Notification System

- [x] Subscription CRUD endpoints
- [x] Email registration with verification flow
- [x] Email list & delete endpoints (`GET/DELETE /subscriptions/emails`)
- [x] Unsubscribe via token
- [x] Subscription management page (`/settings/subscriptions`)
- [x] Add/delete emails in UI
- [x] Create/toggle/delete subscriptions in UI
- [x] Verification status display

### 3.8 Price Monitoring Daemon

- [x] APScheduler with 3 jobs (price_scan, deal_digest, cleanup)
- [x] Bug Fare anomaly detection algorithm
- [x] price_scan — Amadeus search → price_history → anomaly detect → notify
- [x] deal_digest — price_history + inspiration → user preference filter → email
- [x] cleanup — price_history 180d + notification_log 90d purge
- [x] Notifier — email dispatch with trigger conditions + cooldown
- [x] Route filtering + user preference filtering
- [x] Multi-source monitoring (Skyscanner + Kiwi + Google Flights in addition to Amadeus)

### 3.9 Frontend Pages

- [x] Landing page
- [x] Search page
- [x] Compare page
- [x] Trip page
- [x] Chat page
- [x] Auth callback page
- [x] Settings — Subscriptions (`/settings/subscriptions`)
- [x] Settings — Preferences (`/settings/preferences`)

### 3.10 Frontend State Management

- [x] Auth store + useAuth hook
- [x] Search store + useSearch hook
- [x] Chat store + useChat hook (SSE)
- [x] Trip store + useTrip hook
- [x] Compare store + useCompare hook
- [x] Subscription store + useSubscription hook
- [x] Preferences store + usePreferences hook

---

## 4. Infrastructure & DevOps Checklist

### 4.1 Containerization

- [x] Backend Dockerfile (multi-stage: base → dev → prod)
- [x] Frontend Dockerfile (multi-stage: base → dev → builder → prod)
- [x] Monitor Dockerfile (multi-stage: base → dev → prod)
- [x] docker-compose.yml (5 services)
- [x] docker-compose.override.yml (dev: hot-reload, volume mounts)
- [x] docker-compose.prod.yml (Caddy proxy, no volumes)
- [ ] Caddyfile for TLS termination (referenced but not created)

### 4.2 CI/CD

- [x] GitHub Actions `test.yml` — lint + type-check + pytest (backend + monitor)
- [x] GitHub Actions `deploy.yml` — test → deploy to Railway (parallel)
- [x] PostgreSQL service container in CI
- [x] Frontend lint/type-check in CI (ESLint + TypeScript `--noEmit`)
- [x] Frontend unit tests in CI (Vitest)
- [x] Redis service container in CI (redis:7-alpine for backend + monitor)

### 4.3 Deployment

- [x] Railway configuration (`railway.toml` per service)
- [x] Environment variable documentation (`.env.example`)
- [ ] Production deployment verified end-to-end
- [ ] Monitoring / alerting setup (Grafana, Sentry, etc.)
- [ ] Backup strategy for PostgreSQL

---

## 5. Quality Assurance Checklist

### 5.1 Backend Tests (105 passing)

- [x] Model tests (SQLAlchemy ORM)
- [x] Auth API tests (Google OAuth, JWT, tiers)
- [x] Agent tests (BaseAgent, Coordinator, specialists)
- [x] Service tests (search, compare, subscription, email)
- [x] Client tests (Amadeus, Skyscanner, Kiwi, Google Flights)
- [x] Normalizer tests (multi-source → unified format)
- [x] Currency conversion tests

### 5.2 Monitor Tests (20 passing)

- [x] Anomaly detector tests
- [x] Client tests (Amadeus, RapidAPI base, Skyscanner, Kiwi, Google Flights)
- [x] Rate limiter tests
- [x] Normalizer tests (Skyscanner + Kiwi + Google Flights price extraction)

### 5.3 Frontend Tests (111 passing)

- [x] Auth store tests (Vitest)
- [x] Compare store tests (Vitest)
- [x] Subscription store tests (Vitest — 18 tests: CRUD, error handling, cascade delete)
- [x] Preferences store tests (Vitest — 8 tests: fetch, update, error paths)
- [x] Search store tests (Vitest — 17 tests: params, results, sorting, reset)
- [x] Component tests (Button, Input, Card, FlightCard, Footer — 40 tests)
- [x] Hook tests (useCompare, useTrip — 14 tests)

### 5.4 End-to-End Tests

- [ ] Search → results → compare flow
- [ ] Chat conversation flow
- [ ] Subscription create → verify → receive notification
- [ ] Settings pages (preferences, subscriptions)
- [ ] Auth flow (login → session → logout)

### 5.5 Code Quality

- [x] Backend linting (Ruff: E, F, I, N, W, UP)
- [x] Backend type checking (mypy)
- [x] Monitor linting (Ruff)
- [x] Frontend linting (ESLint via Next.js)
- [x] Frontend type checking (TypeScript strict)

---

## 6. Documentation Checklist

- [x] `CLAUDE.md` — Development guide and AI assistant instructions
- [x] `docs/PRD.md` — Product Requirements Document (Traditional Chinese)
- [x] `docs/ARCHITECTURE.md` — Technical Architecture Document with ADRs
- [x] `docs/PROJECT_STATUS.md` — This file (project management tracker)
- [x] `CHANGELOG.md` — Version history (Keep a Changelog format)
- [x] `README.md` — Quick start and overview
- [x] `.env.example` — Environment variable reference
- [x] `.github/COMMIT_CONVENTION.md` — Commit message standards
- [ ] API documentation (auto-generated Swagger at `/docs` — verify completeness)
- [ ] Deployment runbook (step-by-step production deployment guide)
- [ ] Incident response playbook

---

## 7. Known Issues & Technical Debt

| ID | Severity | Area | Description | Status |
|----|----------|------|-------------|--------|
| KI-01 | Medium | Backend | Hotel search methods are stubs returning empty results | On Hold — pending Skyscanner/Kiwi hotel API verification |
| KI-02 | Medium | Backend | `PriceAgent._get_price_history()` not wired to DB | Fixed |
| KI-03 | Medium | Backend | `RecommendationAgent._get_user_preferences()` not querying DB | Fixed |
| KI-05 | Low | Infra | Caddyfile for production TLS not created (Railway 不需要) | Open |
| KI-07 | Low | External | RapidAPI free tier rate limits (429 errors) — backoff implemented | Mitigated |
| KI-08 | Low | Testing | Frontend E2E tests not written (Playwright configured but empty) | Open |
| KI-09 | Low | Infra | `alembic.ini` has hardcoded dev DB URL | Open |
| KI-10 | Critical | Testing | Subscription tests sent real emails via SMTP (no mock/guard) | Fixed (#1, PR #2) |

---

## 8. Upcoming Work (Prioritized Backlog)

### Priority: Medium — 上線路徑（Launch Path）

| Item | Description | Estimated Effort | Blocked By |
|------|-------------|-----------------|------------|
| Production deployment | Railway 端到端驗證（env vars、health check、DB migration、域名設定） | Medium | — |

### Priority: Low

| Item | Description | Estimated Effort | Blocked By |
|------|-------------|-----------------|------------|
| E2E test suite | Playwright E2E 測試（搜尋→結果→比價→聊天完整流程），MVP 上線非必要 | Large | — |
| Frontend test coverage | Add component and hook tests (Vitest + @testing-library/react) | Medium | Done |
| Agent ↔ Service integration | Wire SearchAgent/PriceAgent to multi-source search（僅影響 Chat） | Medium | Done |
| Caddyfile | TLS config for VM deployment（僅 VM 部署需要，Railway 不需要） | Small | — |
| Deployment runbook | Step-by-step production deployment documentation | Small | — |
| Incident playbook | Monitoring alerts and response procedures | Small | Production deployment |

### On Hold

| Item | Description | Estimated Effort | Blocked By |
|------|-------------|-----------------|------------|
| Hotel search integration | Skyscanner/Kiwi hotel APIs not verified on free tier | Large | API verification |

---

## 9. Release History

| Version | Date       | Highlights |
|---------|------------|------------|
| 0.1.0   | 2026-03-03 | Initial release: multi-agent AI, flight search (3 sources), chat, subscriptions, monitoring daemon, CI/CD |
| 0.2.0   | 2026-03-13 | Subscription UI, preferences page, user dropdown, monitor tasks implemented, notifier email sending, docs reorganization |

---

*Last updated: 2026-03-15*
