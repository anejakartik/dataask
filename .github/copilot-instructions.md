# Copilot instructions for dataask

> Same intent as [../AGENTS.md](../AGENTS.md), Copilot-format.

## Product context

This repo is **dataask** — natural-language analytics for founders + PMs. See [PRODUCT.md](../PRODUCT.md).

- **Target user:** Founder / PM at a 10–100 person SaaS
- **Their pain:** Existing tools cost money or hallucinate; Slacking the data team is slow
- **Our wedge:** Schema-aware + eval-driven + safety-first + free

## Hard constraints

- **READ-ONLY enforcement.** Every SQL execution path goes through `safety.is_readonly()`. No exceptions.
- **Single LLM call by default.** Multi-turn CoT is expensive — needs justification.
- **Eval-gated.** Any prompt change must include an eval case + accuracy report.

## Code style

- Python: type hints, ruff, pytest, sqlglot for SQL parsing
- TypeScript: strict, eslint, vitest
- Small focused changes

## Repo layout

```
dataask/
├── README.md, PRODUCT.md, ROADMAP.md, AGENTS.md, DEMO.md
├── .github/
├── docs/architecture.md
├── server/
│   ├── main.py        # FastAPI
│   ├── nl2sql.py      # LLM prompt + schema injection
│   ├── safety.py      # read-only enforcement (sqlglot AST)
│   └── connections/   # DuckDB now, Postgres/Snowflake later
├── web/               # Next.js chat UI
├── evals/             # 50-case eval suite (consumed by evalstack)
└── docker-compose.yml
```
