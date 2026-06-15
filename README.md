# dataask

> Natural-language analytics for founders + PMs. Connect your warehouse. Ask "what was our DAU last week by region?". Get the answer + SQL in 5 seconds.

**Live demo:** [dataask.kartikaneja.com](https://dataask.kartikaneja.com) *(coming soon)*
**Status:** scaffold · last shipped 2026-06-15
**Built by:** [Kartik Aneja](https://kartikaneja.com) — AI/ML Platform Engineer

[![CI](https://github.com/anejakartik/evalstack/actions/workflows/ci.yml/badge.svg)](https://github.com/anejakartik/dataask/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## Why this exists

You're a founder or PM. You have data. You want answers. The data team is busy. Existing tools are $$$ or hallucinate.

See [PRODUCT.md](./PRODUCT.md) for the full writeup. TL;DR:

- **Who:** Founder / PM at a 10–100 person SaaS with a Postgres warehouse
- **Pain:** Hex/Outerbase cost money; OSS text-to-SQL hallucinates non-existent columns; Slacking the data team is slow
- **Why now:** NL→SQL is hot but accuracy is the blocker — an eval-driven approach wins

## What works today

- *(scaffolding — first working NL→SQL endpoint lands this week)*
- Repo + doc set
- FastAPI server skeleton with intended `/ask` endpoint
- DuckDB connection layer
- Read-only SQL enforcement helper (regex-based block on DDL/DML)
- CI workflow

## Try it (when shipped)

```bash
git clone https://github.com/anejakartik/dataask.git
cd dataask
docker compose up -d
# Connect to public NYC Taxi dataset by default
open http://localhost:3000
```

```python
# Or use the SDK
import dataask
client = dataask.Client(endpoint="http://localhost:8000")
result = client.ask("What were the top 5 pickup zones last December?")
print(result.sql)
print(result.rows)
```

## Architecture

See [docs/architecture.md](./docs/architecture.md). Stack: Python FastAPI + DuckDB + OpenAI + Next.js, deployed on Fly.io + Vercel. Plans to consume `evalstack` for accuracy regression CI.

## What's next

See [ROADMAP.md](./ROADMAP.md). Top items: NL→SQL with schema awareness, SQL safety layer, chat UI, eval suite.

## Contributing

PRs welcome. See [AGENTS.md](./AGENTS.md).

## License

MIT — see [LICENSE](./LICENSE).
