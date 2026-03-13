# Claude Code User Command: Review

Product requirement review and discussion command. Enter plan mode to collaborate with the user on feature design, UX decisions, and implementation strategy.

## Usage

```
/review <feature or area to discuss>
```

`$ARGUMENTS` contains the feature, page, or area the user wants to review and discuss.

## What This Command Does

1. Enter plan mode immediately.
2. Explore the current codebase for the area described in `$ARGUMENTS`.
3. Provide insights on the current state: what exists, what's missing, what could be improved.
4. Collaborate with the user on product requirements and design decisions.
5. Finalize the plan and update `PRD.md` before exiting plan mode.

## Instructions

### Step 1: Enter Plan Mode

- Call `EnterPlanMode` immediately. No pre-work outside of plan mode.

### Step 2: Explore Current State

- Read the relevant source files for the area in `$ARGUMENTS`.
- Check `PRD.md` and `implementation.md` for existing design context.
- Summarize the current state to the user:
  - What's implemented
  - What's stubbed or incomplete
  - What's missing entirely

### Step 3: Provide Insights

- Identify UX issues, edge cases, or architectural concerns.
- Suggest improvements based on the project's target audience (Taiwanese travelers, TWD currency, Asia-Pacific focus).
- Reference industry best practices where relevant.
- Present options with trade-offs — let the user decide.

### Step 4: Discuss with the User

- Use `AskUserQuestion` to clarify requirements and preferences.
- Iterate on the design based on user feedback.
- Do NOT finalize unilaterally — this is a collaborative discussion.

### Step 5: Finalize Plan

- Write the agreed-upon plan to the plan file.
- Update `PRD.md` with the finalized design decisions before exiting plan mode.
- Exit plan mode with `ExitPlanMode`.

### After Plan Mode

- Once approved, follow the Checkpoint Validation process in CLAUDE.md after implementation:
  1. Code matches the plan
  2. `PRD.md` and `implementation.md` are in sync
  3. Tests cover the changes
  4. Lint passes
