# dataask

> Natural-language analytics for founders + PMs. Connect your warehouse. Ask "what was our DAU last week by region?". Get the answer + SQL in 5 seconds.

**Live demo:** [dataask.kartikaneja.com](https://dataask.kartikaneja.com) *(coming soon)*
**Status:** alpha · last shipped 2026-06-17
**Built by:** [Kartik Aneja](https://kartikaneja.com) — AI/ML Platform Engineer

[![CI](https://github.com/anejakartik/dataask/actions/workflows/ci.yml/badge.svg)](https://github.com/anejakartik/dataask/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## Why this exists

You're a founder or PM. You have data. You want answers. The data team is busy. Existing tools are $$$ or hallucinate.

See [PRODUCT.md](./PRODUCT.md) for the full writeup. TL;DR:

- **Who:** Founder / PM at a 10–100 person SaaS with a Postgres warehouse
- **Pain:** Hex/Outerbase cost money; OSS text-to-SQL hallucinates non-existent columns; Slacking the data team is slow
- **Why now:** NL→SQL is hot but accuracy is the blocker — an eval-driven approach wins

## What works today (alpha MVP)

- **`POST /ask`** — schema introspection → OpenAI `gpt-4o-mini` → sqlglot AST safety check → DuckDB execute → rows back
- **Read-only enforcement** — sqlglot AST rejects DDL/DML, multi-statement queries, PRAGMA/ATTACH/COPY
- **Synthetic SaaS demo dataset** — `customers` / `subscriptions` / `orders` / `events` seeded on startup (deterministic for reproducible demos)
- **Minimal chat UI** — single-page HTML at `/` with question box, generated-SQL display, result table, schema panel
- **`GET /schema`** — live table+column listing for prompt debugging and UI render
- **CORS** — configurable via `DATAASK_CORS_ORIGINS`

## Try it (60 seconds, local)

```bash
git clone https://github.com/anejakartik/dataask.git
cd dataask
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up --build
open http://localhost:8000  # ask "What was our MRR by plan last month?"
```

Sample questions the demo dataset can answer:

- "What was our MRR by plan last month?"
- "How many customers signed up in May 2026?"
- "Top 5 countries by total paid order amount"
- "Weekly active users in June 2026"
- "Which plan has the highest churn rate?"

## Architecture

See [docs/architecture.md](./docs/architecture.md). Stack: Python FastAPI + DuckDB + OpenAI. Plans to consume `evalstack` for accuracy regression CI.

## What's next

See [ROADMAP.md](./ROADMAP.md). Top items: EXPLAIN cost preview, proper Next.js chat UI with conversation history, public deployment, 50-case eval suite via `evalstack`.

## Contributing

PRs welcome. See [AGENTS.md](./AGENTS.md).

## License

MIT — see [LICENSE](./LICENSE).
