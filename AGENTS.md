# AGENTS.md — instructions for AI coding agents

## Before you touch code

1. Read [PRODUCT.md](./PRODUCT.md) — who this is for + what wedge we're pursuing
2. Read the top of [ROADMAP.md](./ROADMAP.md) — what's prioritized
3. Check open issues + PRs

## Conventions

- **Python:** type hints, ruff, pytest
- **TypeScript:** strict mode, eslint, vitest
- Small focused PRs

## Repo-specific guardrails

- **Read-only enforcement is a HARD CONSTRAINT** — never relax this. Any code path that could execute a DDL/DML statement must go through `safety.is_readonly()` first.
- **Schema awareness > clever prompting** — accuracy wins come from giving the LLM the right schema context, not from fancier templates
- **Eval first** — for any prompt change, add an eval case to the suite. Use `evalstack`.
- **Single LLM call by default** — multi-turn chain of thought is expensive; profile before adding

## Commits & PRs

- Imperative-mood, *why*-focused commit messages
- PR: problem + change + accuracy delta (run the 50-case suite)
- Squash on merge

## Deployment

- CI: `.github/workflows/ci.yml`
- Deploy: Fly.io (backend) + Vercel (frontend)
- Live: `dataask.kartikaneja.com` *(coming)*
- Free tier only

## Companion doc

[.github/copilot-instructions.md](./.github/copilot-instructions.md)
