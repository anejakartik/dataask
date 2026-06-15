"""dataask server — FastAPI NL->SQL endpoint.

Scaffold: the /ask endpoint accepts a question + returns a SAFETY-CHECKED SQL plan.
Full LLM-backed SQL generation lands this week — see ROADMAP.md.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from safety import is_readonly


app = FastAPI(
    title="dataask",
    version="0.1.0",
    description="Natural-language analytics for founders + PMs",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "dataask",
        "version": "0.1.0",
        "docs": "/docs",
        "github": "https://github.com/anejakartik/dataask",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True}


class AskRequest(BaseModel):
    question: str
    connection_id: str = "default"


class AskResponse(BaseModel):
    sql: str
    rows: list[dict[str, Any]]
    cost_estimate: dict[str, Any] | None = None
    citations: list[str] = []
    warnings: list[str] = []


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    """NL → SQL → safety check → execute (when wired).

    SCAFFOLD: currently returns a placeholder. Full implementation this week.
    """
    # Placeholder SQL — proves the safety layer works end-to-end
    sql = "SELECT 'placeholder' AS info"
    safe, reason = is_readonly(sql)
    if not safe:
        raise HTTPException(400, f"Unsafe SQL generated: {reason}")
    return AskResponse(
        sql=sql,
        rows=[{"info": "placeholder"}],
        cost_estimate={"rows": 1, "bytes": 16},
        citations=[],
        warnings=["Scaffold — LLM-backed SQL generation lands this week"],
    )


@app.post("/validate-sql")
def validate_sql(sql: str) -> dict[str, Any]:
    """Public endpoint to test the safety layer in isolation."""
    safe, reason = is_readonly(sql)
    return {"safe": safe, "reason": reason}
