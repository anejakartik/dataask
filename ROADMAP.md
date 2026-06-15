# Roadmap — dataask

## Shipping log (newest on top)

### 2026-06-15 — Scaffold
- [x] Repo + doc set + CI workflow
- [x] FastAPI server skeleton with `/ask` endpoint stub
- [x] Read-only SQL safety helper (regex-based, AST-based coming)
- Notes: target a working NL→SQL endpoint on DuckDB within this week.

---

## Short-term — next 4 weeks

- [ ] **P0 / NL→SQL endpoint** — `POST /ask {question, schema_id}` → `{sql, rows, cost_estimate}`
- [ ] **P0 / Schema introspection** — auto-discover tables/columns/types from the connected DB
- [ ] **P0 / Schema injection in prompt** — `<schema>` block in system prompt with all tables
- [ ] **P0 / Read-only SQL enforcement** — sqlglot-based AST check (not just regex)
- [ ] **P0 / EXPLAIN cost preview** — before executing, run EXPLAIN and surface row estimates
- [ ] **P0 / Next.js chat UI** — message thread, SQL preview, execute button
- [ ] **P0 / Deploy** — Fly.io + Vercel, public dataset (NYC Taxi)
- [ ] **P1 / 50-case eval suite** — use `evalstack` to track accuracy over time
- [ ] **P1 / Citation rendering** — highlight which tables/columns were used

## Medium-term — months 2–3

- [ ] **Postgres / Snowflake / BigQuery connectors**
- [ ] **Multi-turn conversation memory**
- [ ] **Chart generation** — auto-suggest chart type from result shape
- [ ] **Scheduled reports** — "DM me DAU every Monday at 9am"
- [ ] **Semantic layer / metric definitions** — "DAU" maps to a canonical SQL pattern

## Long-term — 6+ months

- [ ] Fine-tuned schema-specific judge (uses `evalstack` for labeled data)
- [ ] Slack/Discord bot interface
- [ ] Self-host Helm chart

## Content posts derived from this roadmap

| Feature | Posted? |
|---|---|
| Launch (alpha) | _pending_ |
| Why text-to-SQL fails 40% of the time | _pending_ |
| Eval-driven improvements (50-case suite) | _pending_ |
