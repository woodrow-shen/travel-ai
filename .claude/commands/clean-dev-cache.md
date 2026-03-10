# Claude Code User Command: Clean Dev Cache

Remove all development cache directories (root-owned from Docker and local).

Run this command:

```bash
sudo find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name ".next" \) -exec rm -rf {} +
```

Stop Docker Compose first if caches keep getting recreated.
