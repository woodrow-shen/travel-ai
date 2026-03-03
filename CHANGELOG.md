# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Conventional Commits](https://www.conventionalcommits.org/).

## [0.1.0] - 2026-03-03

### Added

- **Multi-agent AI system**: CoordinatorAgent + 5 specialist agents (Search, Price, Recommendation, Itinerary, Budget) using Anthropic Claude tool-use pattern
- **Multi-source flight search**: Amadeus + Skyscanner + Kiwi via RapidAPI, parallel execution with unified normalizer
- **Currency conversion**: Auto-detect user currency from IP (ip-api.com), exchange rates from open.er-api.com (Redis-cached 6h), Amadeus EUR prices auto-converted
- **Google OAuth 2.0**: Login via Google, JWT access/refresh tokens, Basic/Premium user tiers
- **Flight comparison**: Cross-source price comparison with unified `/compare` endpoint
- **Direct mode** (Premium): Best non-stop flight recommendations with quality scoring
- **Adventure mode**: Cheapest destinations from origin, explore anywhere
- **Trip management**: Full CRUD for trips with flight/hotel/activity/itinerary associations
- **AI chat**: SSE streaming chat via CoordinatorAgent, multi-turn conversation support
- **Subscription system**: Bug fare alerts, price drop alerts, deal digests with email verification
- **Price monitoring daemon**: APScheduler-based background service with anomaly detection (Bug Fare algorithm)
- **Frontend**: Next.js 15 + React 19 pages (landing, search, compare, trip, chat, auth callback), Zustand stores, Tailwind CSS
- **Infrastructure**: Docker Compose (5 services), multi-stage Dockerfiles, CI/CD (GitHub Actions), Railway deployment config
- **Database**: PostgreSQL 16 with 11 SQLAlchemy models, Alembic migrations, Redis 7 cache
- **Testing**: 105 backend tests + 10 monitor tests passing
- **Developer tooling**: Claude Code commands (`/bug`, `/review`, `/test`, `/commit`), token efficiency strategy, checkpoint validation process

### Known Limitations

- Hotel search methods are stubs (returning empty)
- Monitor tasks (price_scan, deal_digest, cleanup) are stubs
- Notification/email sending is stubbed
- Frontend unit tests and E2E tests not yet written
- Agent layer not yet integrated with SearchService (Phase 4, deprioritized)
