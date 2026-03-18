# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Conventional Commits](https://www.conventionalcommits.org/).

**Versioning**: `MAJOR.MINOR.PATCH` — Minor (new features, API changes) and patch (bug fixes, tests, docs) are bumped by the dev team. Major bumps (1.0.0, 2.0.0, ...) are owner-decided only.

## [0.5.0] - 2026-03-18

### Added

- **Price monitoring dashboard**: New `/monitor` page with price trend visualization, subscription overview, and notification history
- **Price history API**: `GET /api/v1/price-history` endpoint returning price history for subscribed routes (JWT auth, origin/destination/days params)
- **Notification logs API**: `GET /api/v1/subscriptions/notifications` endpoint returning user's notification history
- **Recharts integration**: Line chart with per-source colored lines for price trend visualization
- **Monitor components**: RouteSelector, PriceTrendChart, SubscriptionOverview, NotificationHistory
- **Monitor store**: Zustand store (`monitor.ts`) + `useMonitor` hook for price history and notification state
- **Navigation**: "Monitor" added as top-level nav link in Header
- **i18n**: All 12 locale files updated with `monitor` namespace (~18 keys each)

## [0.4.0] - 2026-03-18

### Added

- **Frontend i18n**: next-intl integration with `[locale]` App Router routing, `localePrefix: "as-needed"` (zh-TW default, `/en/*` for English)
- **Translation files**: zh-TW + en message files (~200 keys each) covering all pages and components
- **String extraction**: All hardcoded UI strings replaced with `useTranslations()` calls across 8 pages and 7 components
- **LanguageSwitcher**: Toggle button in Header and Preferences page for locale switching
- **Backend locale middleware**: Accept-Language header parsing with `request.state.locale` injection
- **Backend error i18n**: `t(key, locale)` translation function with dotted key support, zh-TW + en error messages (~30 keys)
- **AI agent localization**: `BaseAgent` accepts `locale` parameter, system prompts append language instruction (6 agents)
- **Email template localization**: 4 templates × 2 languages = 8 locale-suffixed templates
- **User language preference**: `preferred_language` column in user_preferences + Alembic migration + API CRUD

## [0.3.0] - 2026-03-17

### Added

- **Hotel search integration**: Skyscanner + Kiwi hotel APIs as 2 search sources, parallel execution with unified normalizer and deduplication
- **Hotel autocomplete**: Location name → API-specific IDs with 7-day Redis cache
- **Hotel normalizer**: Source-specific raw data → unified HotelResult (17 fields), dedup by name + lowest price
- **Hotel comparison**: Cache-based `POST /compare/hotels` endpoint with cheapest/best-rated picks
- **Google Flights**: 4th flight search source via RapidAPI (one-way + roundtrip), booking details, price graph
- **Frontend hotel form**: Destination, check-in/check-out, guests, rooms fields in SearchForm
- **Agent hotel support**: SearchAgent and PriceAgent wired to multi-source hotel search
- **Frontend component tests**: HotelCard (19), SearchForm (12), Header (10), CompareTable (6) — 49 new tests
- **Email validation**: DNS/MX deliverability check via `email-validator` in add-email endpoint

### Fixed

- Subscription tests sending real SMTP emails to `example.com` (added auto-mock + `ENV=test` guard)
- mypy type error in Skyscanner hotel image extraction (`Any | None` → `str`)

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
