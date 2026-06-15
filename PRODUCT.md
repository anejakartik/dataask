# Product — dataask

## Target user

**Persona:** Founder / PM at a 10–100 person SaaS. Has a Postgres data warehouse (or Snowflake/BigQuery). Wants quick answers without bothering data team.

**Job they're trying to do:** Convert "what was our DAU last week by region?" into a trustworthy answer in seconds.

**Current workflow:** Slack the data team. Wait 4 hours. Get back a chart that's almost right.

## The pain

1. **Time cost.** Data-team turnaround is slow for simple ad-hoc questions.
2. **Existing NL→SQL tools fail or cost money.** Hex/Outerbase = $$; OSS = hallucinations.
3. **No trust signal.** When a tool generates SQL, users have no way to verify it before running.
4. **Vendor lock-in risk.** They don't want to migrate their warehouse to use a tool.

## Existing alternatives — and why they fall short

| Alternative | Why it doesn't fit |
|---|---|
| **Hex / Outerbase** | $20–$50/user/month minimum, vendor account required |
| **Vanna.ai, sqlcoder** | Open-source but accuracy is mid-tier; no built-in safety |
| **ChatGPT with manual schema paste** | Schema goes stale; no execution + verification path |
| **Status quo: ask data team** | Slow; data team is the bottleneck |

## Our wedge

1. **Schema-aware.** Auto-discovers schema from your connection; refreshes nightly.
2. **Eval-driven.** Continuous accuracy regression suite (uses `evalstack`) — published score per release.
3. **Safety-first.** SQL preview + EXPLAIN cost + READ-ONLY enforcement before execution.
4. **Free + self-host.** Connect your DB, no vendor account.
5. **Source-cited answers.** Show the SQL + the columns referenced + warning if columns are guessed.

## MVP scope

**Must-have:**
- FastAPI server with `POST /ask` accepting `{question, connection_id}`
- DuckDB local connection (with NYC Taxi public dataset as default)
- LLM-backed NL→SQL (OpenAI gpt-4o-mini default)
- READ-ONLY enforcement (block DDL/DML via regex + parsed AST)
- EXPLAIN-based cost estimation before execution
- Next.js chat UI with SQL preview + execute button
- 50-case eval suite published with results

**Out of scope for MVP:**
- Postgres/Snowflake/BigQuery connectors (DuckDB only for v0.1)
- Multi-turn conversation memory
- Chart generation
- Authentication / multi-tenant
- Scheduled reports

## Success metric

- 70%+ accuracy on a 50-case eval suite vs hand-written SQL
- < 5s end-to-end latency (NL → answer rows displayed)
- 5+ external GitHub stars in 4 weeks

## Non-goals

- Not a replacement for BI tools (Hex/Mode). This is for ad-hoc questions.
- No write operations. Ever. Read-only is a permanent constraint.
- No fine-tuning. Use what's possible with prompt engineering + schema injection.
