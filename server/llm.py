"""OpenAI client + NL → SQL prompt orchestration.

Design notes:
- Single-turn for now (multi-turn memory is on the roadmap).
- Schema injected verbatim in system prompt so the model never invents columns.
- Forces SQL-only output via response_format=text + a strict system instruction;
  we then strip code fences defensively.
"""

from __future__ import annotations

import logging
import os
import re

from openai import OpenAI

log = logging.getLogger("dataask.llm")


SYSTEM_TEMPLATE = """You are a senior analytics engineer. You convert natural-language
questions into a single read-only SQL query for DuckDB.

RULES (HARD):
- Output ONLY the SQL. No prose, no markdown, no explanation, no leading "SQL:" label.
- Use exactly ONE statement. No semicolons except at the very end (optional).
- Use only SELECT (CTEs via WITH ... SELECT are allowed). Never DDL or DML.
- Reference only the tables and columns provided in the SCHEMA below.
- If the question is unanswerable with the schema, return:
  SELECT 'unanswerable: <short reason>' AS error
- Prefer descriptive column aliases in the result.
- For date-bucketing use date_trunc('month', col), date_trunc('week', col), etc.
- Today is 2026-06-17. "this month" = June 2026. "last month" = May 2026.

SCHEMA:
{schema}
"""


class LLMUnavailable(RuntimeError):
    """Raised when the OpenAI key is missing or the API call fails."""


def generate_sql(question: str, schema_text: str, *, model: str | None = None) -> str:
    """Return a single SQL string. Raises LLMUnavailable on configuration / API issues."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMUnavailable(
            "OPENAI_API_KEY is not set. Configure your key in .env and restart the server."
        )

    chosen_model = model or os.environ.get("DATAASK_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    system_prompt = SYSTEM_TEMPLATE.format(schema=schema_text)
    try:
        resp = client.chat.completions.create(
            model=chosen_model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question.strip()},
            ],
        )
    except Exception as exc:  # network / auth / quota — surface to the user.
        log.exception("OpenAI call failed")
        raise LLMUnavailable(f"LLM call failed: {exc}") from exc

    raw = (resp.choices[0].message.content or "").strip()
    return _strip_sql(raw)


_CODE_FENCE = re.compile(r"^```[a-zA-Z]*\s*|\s*```$", re.MULTILINE)


def _strip_sql(text: str) -> str:
    """Remove markdown fences, leading 'sql:' labels, trailing semicolons."""
    cleaned = _CODE_FENCE.sub("", text).strip()
    # Drop leading labels like "SQL:" or "Query:".
    for prefix in ("sql:", "SQL:", "Query:", "query:"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    # Trim a single trailing semicolon (multi-statement safety blocks more than one).
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()
    return cleaned
