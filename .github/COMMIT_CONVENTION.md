# Commit Convention

## Sign-off Requirement

All commits MUST include a sign-off line using `git commit -s`. This adds a `Signed-off-by` trailer to the commit message, certifying the Developer Certificate of Origin (DCO).

```bash
git commit -s -m "feat: add new feature"
```

## Conventional Commit Format

```
<type>(<scope>): <description>

[optional body]

Signed-off-by: Name <email>
```

### Types

- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation only
- `style` — Formatting, no code change
- `refactor` — Code restructuring, no feature/fix
- `test` — Adding or updating tests
- `chore` — Build, CI, or tooling changes

### Rules

- Keep the subject line under 72 characters
- Use imperative mood ("add", not "added")
- One logical change per commit
- Always sign off with `-s`
