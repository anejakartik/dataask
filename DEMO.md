# Demo — dataask

## Live demo

**URL:** [dataask.kartikaneja.com](https://dataask.kartikaneja.com) *(coming soon)*

Connected to a public **NYC Taxi** dataset (~few GB). Anyone can ask natural-language questions and see the generated SQL + result rows.

**Hosting plan:**
- Backend: Fly.io free tier (DuckDB + FastAPI + OpenAI client)
- Frontend: Vercel free hobby tier (Next.js chat UI)
- Cost: $0/month under demo traffic + your own OpenAI credit

## Sample questions to try

- "What were the top 5 pickup zones in December 2023?"
- "Average tip percent by payment type, last 6 months"
- "Show daily trip counts for the past 30 days"
- "Which day of the week has the highest average trip distance?"

## Local fallback (once shipped)

```bash
git clone https://github.com/anejakartik/dataask.git
cd dataask
docker compose up -d
export OPENAI_API_KEY=sk-...
open http://localhost:3000
```
