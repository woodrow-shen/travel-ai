# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Conventional Commits](https://www.conventionalcommits.org/).

## [0.2.0] - 2026-03-13

### Added

- **Subscription management UI**: Full frontend page at `/settings/subscriptions` — add/delete emails, create/toggle/delete subscriptions, email verification status display
- **User preferences page**: `/settings/preferences` — home airports, preferred/excluded airlines, alliance and cabin class selection, max stops
- **User dropdown menu**: Replaced static nav with dropdown (Subscriptions, Preferences, Sign out) with click-outside-to-close
- **Backend email endpoints**: `GET /subscriptions/emails` and `DELETE /subscriptions/emails/{id}` for frontend integration
- **Frontend Zustand stores**: `subscription.ts` and `preferences.ts` with full CRUD actions
- **Frontend hooks**: `useSubscription` and `usePreferences` with auto-fetch on mount
- **Monitor tasks implemented**: `price_scan`, `deal_digest`, `cleanup` — fully functional with route filtering, user preference filtering, and anomaly detection
- **Monitor notifier**: Email sending with trigger conditions (bug fare, price drop thresholds)
- **Subscription email verification**: Wired `SubscriptionService` to `EmailService` for real verification emails
- **Compare flow improvements**: Zustand stores, dark mode badges, roundtrip compare label fix, 429 backoff for RapidAPI
- **Search persistence**: localStorage persistence for search form fields
- **Documentation**: `docs/PRD.md` (professional Product Requirements Document), `docs/ARCHITECTURE.md` (Technical Architecture Document with ADRs)

### Changed

- Moved `PRD.md` and `ARCHITECTURE.md` into `docs/` folder
- Updated all references in `CLAUDE.md`, `.claude/commands/bug.md`, `.claude/commands/review.md`

### Fixed

- 429 backoff handling for RapidAPI rate limits
- `SubscriptionType` enum values for PostgreSQL compatibility
- Ruff import sorting errors in CI
- 30 mypy type errors
- pytest cache root-owned file conflicts (redirect to `/tmp`)
- Amadeus API mocking in CI tests

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
- Frontend unit tests and E2E tests not yet written
- Agent layer not yet integrated with SearchService (deprioritized)
