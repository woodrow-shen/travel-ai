---
name: restart
description: "Restart Docker services. Usage: /restart [services] [--no-cache]"
---

# Claude Code User Command: Restart

Restart Docker Compose services with a fresh build.

## Usage

```
/restart              # Restart all services
/restart backend      # Restart specific service(s)
/restart --no-cache   # Rebuild without Docker cache
```

`$ARGUMENTS` optionally contains: service names (e.g. `backend frontend`) and/or `--no-cache` flag.

## Instructions

### Step 1: Parse Arguments

- If `$ARGUMENTS` is empty → restart all services.
- If `$ARGUMENTS` contains service names (e.g. `backend`, `frontend`, `monitor`) → restart only those.
- If `$ARGUMENTS` contains `--no-cache` → run `docker compose build --no-cache` before `up`.

### Step 2: Restart

**All services (default):**

```bash
docker compose up --build -d
```

**Specific service(s):**

```bash
docker compose up --build -d <service1> <service2>
```

**With `--no-cache`:**

```bash
docker compose build --no-cache <services>
docker compose up -d <services>
```

### Step 3: Verify

- Run `docker compose ps` to confirm all targeted services are running.
- If any service is not `Up`, check logs with `docker compose logs --tail=20 <service>` and report the issue.

### Step 4: Report

Show the user:
- Which services were restarted
- Current status (`docker compose ps` output)
- Any errors found in logs
