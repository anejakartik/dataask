# Roadmap — dataask

## Shipping log (newest on top)

### 2026-06-17 — Working NL→SQL endpoint + demo UI
- [x] `POST /ask` end-to-end — schema introspection → OpenAI → sqlglot safety check → DuckDB execute
- [x] Schema introspection (`information_schema.columns`) auto-injected into the LLM system prompt
- [x] Synthetic SaaS demo dataset (customers / subscriptions / orders / events) seeded on startup — deterministic for reproducible demos
- [x] `GET /schema` endpoint exposes the live schema for UI / debugging
- [x] Static demo UI at `/` — question box, generated-SQL display, result table, schema panel
- [x] CORS middleware (configurable via `DATAASK_CORS_ORIGINS`)
- Notes: cost-preview via EXPLAIN deferred; result rows capped at 200 for now (truncation flagged in response).

### 2026-06-15 — Scaffold
- [x] Repo + doc set + CI workflow
- [x] FastAPI server skeleton with `/ask` endpoint stub
- [x] Read-only SQL safety helper (sqlglot-based AST check)

---

## Short-term — next 4 weeks

- [ ] **P0 / EXPLAIN cost preview** — before executing, run EXPLAIN and surface row estimates
- [ ] **P0 / Proper Next.js chat UI** — replace the static HTML with multi-turn message thread + result history
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
