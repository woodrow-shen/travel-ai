# Travel-AI

[![CI](https://github.com/woodrow-shen/travel-ai/actions/workflows/test.yml/badge.svg)](https://github.com/woodrow-shen/travel-ai/actions/workflows/test.yml)
[![Deploy](https://github.com/woodrow-shen/travel-ai/actions/workflows/deploy.yml/badge.svg)](https://github.com/woodrow-shen/travel-ai/actions/workflows/deploy.yml)

Intelligent travel aggregation platform powered by multi-agent AI (Claude). Search, compare, and plan flights, hotels, and activities with AI-driven recommendations.

## Stack

- **Backend**: Python FastAPI + SQLAlchemy + PostgreSQL 16 + Redis 7
- **Frontend**: Next.js 15 + React 19 + Zustand + Tailwind CSS
- **AI**: Anthropic Claude (multi-agent coordinator pattern)
- **Monitor**: APScheduler price monitoring daemon
- **Infrastructure**: Docker Compose + GitHub Actions CI/CD + Railway

## Quick Start

```bash
cp .env.example .env   # fill in API keys
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

See [CLAUDE.md](CLAUDE.md) for full development guide.
