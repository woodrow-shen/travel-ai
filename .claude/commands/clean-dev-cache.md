# Claude Code User Command: Clean Dev Cache

Clean up all development caches, build artifacts, and temporary files from the project.

## Steps

1. Stop Docker Compose if running to prevent caches from being recreated:

```bash
docker compose down 2>/dev/null || true
```

2. Remove all known cache and build artifact directories (including root-owned files from Docker):

```bash
sudo find . -type d \( \
  -name "__pycache__" \
  -o -name ".pytest_cache" \
  -o -name ".mypy_cache" \
  -o -name ".ruff_cache" \
  -o -name ".next" \
  -o -name "node_modules" \
  -o -name ".turbo" \
  -o -name "dist" \
  -o -name "build" \
  -o -name ".eggs" \
  -o -name "*.egg-info" \
  -o -name ".tox" \
  -o -name ".coverage_cache" \
\) -exec rm -rf {} + 2>/dev/null
```

3. Remove stale temporary and generated files:

```bash
sudo find . -type f \( \
  -name "*.pyc" \
  -o -name "*.pyo" \
  -o -name ".coverage" \
  -o -name "coverage.xml" \
  -o -name ".DS_Store" \
  -o -name "*.log" \
\) -delete 2>/dev/null
```

4. Optionally prune Docker build cache if disk space is a concern:

```bash
docker builder prune -f 2>/dev/null || true
```

5. Report what was cleaned.
