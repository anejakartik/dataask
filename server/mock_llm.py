"""Deterministic mock SQL generator — for demos and CI when no LLM is available.

Enable with `DATAASK_USE_MOCK=1`. The mock matches on keyword substrings in
the question and returns a hand-written SQL query against the demo SaaS
schema. Falls back to a friendly error SQL if no pattern matches.

Pure-Python, zero dependencies — safe to run in any environment.
"""

from __future__ import annotations


# Order matters — first match wins. Each entry: (keyword_set, sql).
PATTERNS: list[tuple[set[str], str]] = [
    (
        {"mrr", "plan"},
        """
        SELECT
            s.plan,
            COUNT(DISTINCT s.customer_id) AS active_subscriptions,
            SUM(s.mrr) AS mrr_usd
        FROM subscriptions s
        WHERE s.ended_at IS NULL
        GROUP BY s.plan
        ORDER BY mrr_usd DESC
        """,
    ),
    (
        {"signup", "may"},
        """
        SELECT
            COUNT(*) AS new_customers
        FROM customers
        WHERE signup_date >= DATE '2026-05-01'
          AND signup_date <  DATE '2026-06-01'
        """,
    ),
    (
        {"country", "order"},
        """
        SELECT
            c.country,
            SUM(o.amount) AS paid_order_amount
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        WHERE o.status = 'paid'
        GROUP BY c.country
        ORDER BY paid_order_amount DESC
        LIMIT 5
        """,
    ),
    (
        {"weekly", "active"},
        """
        SELECT
            date_trunc('week', occurred_at) AS week,
            COUNT(DISTINCT customer_id) AS weekly_active_users
        FROM events
        WHERE occurred_at >= DATE '2026-06-01'
          AND occurred_at <  DATE '2026-07-01'
        GROUP BY 1
        ORDER BY 1
        """,
    ),
    (
        {"churn"},
        """
        WITH plan_totals AS (
            SELECT plan, COUNT(*) AS total_subs
            FROM subscriptions
            GROUP BY plan
        ),
        plan_churn AS (
            SELECT plan, COUNT(*) AS churned
            FROM subscriptions
            WHERE ended_at IS NOT NULL
            GROUP BY plan
        )
        SELECT
            t.plan,
            t.total_subs,
            COALESCE(c.churned, 0) AS churned,
            ROUND(COALESCE(c.churned, 0)::DOUBLE / t.total_subs, 4) AS churn_rate
        FROM plan_totals t
        LEFT JOIN plan_churn c USING (plan)
        ORDER BY churn_rate DESC
        LIMIT 1
        """,
    ),
    (
        {"top", "customer"},
        """
        SELECT
            c.name,
            c.plan,
            SUM(o.amount) AS lifetime_value
        FROM customers c
        JOIN orders o ON o.customer_id = c.id
        WHERE o.status = 'paid'
        GROUP BY c.id, c.name, c.plan
        ORDER BY lifetime_value DESC
        LIMIT 10
        """,
    ),
    (
        {"count", "customer"},
        "SELECT COUNT(*) AS total_customers FROM customers",
    ),
]


def mock_generate_sql(question: str) -> str:
    """Return a hand-written SQL for the demo dataset, or a friendly error SQL."""
    words = {w.lower() for w in question.split()}
    for keywords, sql in PATTERNS:
        if keywords.issubset(words):
            return _dedent_one_line(sql)
    return (
        "SELECT 'mock mode does not have an answer for this question. "
        "Try one of the example queries or set OPENAI_API_KEY for real LLM-backed SQL.' "
        "AS error"
    )


def _dedent_one_line(sql: str) -> str:
    return " ".join(line.strip() for line in sql.strip().splitlines() if line.strip())
