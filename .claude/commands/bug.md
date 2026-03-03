# Claude Code User Command: Bug

Rapid bug triage and fix command. The user is reporting a bug — act fast.

## Usage

```
/bug <description of the bug>
```

`$ARGUMENTS` contains the bug description: symptoms, affected page/feature, error messages, or a screenshot path.

## What This Command Does

1. Immediately reproduce/locate the bug from the description in `$ARGUMENTS`.
2. Identify root cause with minimal exploration.
3. Fix it directly — no planning phase, no asking for confirmation.
4. Verify the fix (run relevant tests, type-check, lint).
5. Report what was wrong and what was changed.

## Severity Classification

Before diving into the fix, assess severity:

- **Trivial**: Typo, styling glitch, minor UI issue, single-line fix. → Follow the fast path below (Steps 1–5).
- **Critical**: Infinite loop, data loss, crash, security issue, architectural flaw, multi-file systemic bug. → Enter **plan mode** first. Design the fix with the user, then update `plan.md` and `implementation.md` after the fix is complete (per the Checkpoint Validation process in CLAUDE.md).

Use your judgement. When in doubt, treat it as critical — it's cheaper to plan than to revert a bad fix.

## Instructions

Follow these steps strictly:

### Step 1: Triage

- Parse `$ARGUMENTS` for: affected file/page, error message, reproduction steps, screenshot path.
- If a screenshot path is provided, read it immediately.
- Check Docker logs (`docker compose logs --tail=30 <service>`) if the bug involves runtime errors.
- Locate the relevant source files quickly using Grep/Glob. Do NOT do broad exploration — be surgical.

### Step 2: Root Cause

- Read only the files needed to understand the bug.
- Identify the exact line(s) causing the issue.
- State the root cause in one sentence before fixing.

### Step 3: Fix

- Apply the minimal fix. Do not refactor surrounding code.
- Do not add features, comments, or "improvements" beyond the fix.
- If the fix spans multiple files, edit them all in parallel.

### Step 4: Verify

- Run the relevant tests (`uv run pytest` for backend, `npx tsc --noEmit` for frontend).
- If tests fail, fix them immediately.
- Run lint on changed files.

### Step 5: Report

Provide a brief summary:
- **Severity**: trivial or critical
- **Bug**: what was broken
- **Cause**: why it was broken (one line)
- **Fix**: what was changed (file:line)
- **Verified**: test/lint results

### Step 6: Checkpoint (critical bugs only)

For critical bugs, run the full Checkpoint Validation per CLAUDE.md:
1. **Code** — implementation matches the intended fix
2. **Design docs** — `plan.md` and `implementation.md` updated to reflect the change
3. **Tests** — relevant tests added/updated and all pass
4. **Lint** — no lint errors in changed files
