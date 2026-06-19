"""dataask server — FastAPI NL→SQL endpoint backed by DuckDB.

Pipeline for POST /ask:
  question → schema introspection → LLM (OpenAI) → SQL → safety check → execute → rows.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db import (
    execute_select,
    explain_query,
    init_db,
    introspect_schema,
    render_schema_for_prompt,
)
from llm import LLMUnavailable, generate_sql
from safety import is_readonly


logging.basicConfig(
    level=os.environ.get("DATAASK_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
log = logging.getLogger("dataask")


app = FastAPI(
    title="dataask",
    version="0.1.0",
    description="Natural-language analytics for founders + PMs",
)

_cors_origins = os.environ.get("DATAASK_CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    counts = init_db()
    log.info("dataask: ready — %s", counts)


# --- API endpoints ---------------------------------------------------------


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "llm_configured": bool(os.environ.get("OPENAI_API_KEY"))}


class TableSchemaOut(BaseModel):
    name: str
    columns: list[dict[str, str]]


@app.get("/schema", response_model=list[TableSchemaOut])
def schema() -> list[TableSchemaOut]:
    """Return the live DuckDB schema. Useful for UIs and prompt debugging."""
    return [
        TableSchemaOut(
            name=t.name,
            columns=[{"name": c.name, "type": c.type} for c in t.columns],
        )
        for t in introspect_schema()
    ]


class AskRequest(BaseModel):
    question: str
    connection_id: str = "default"


class CostEstimateOut(BaseModel):
    estimated_rows: int | None
    operators: list[str]
    plan: str


class AskResponse(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool
    cost_estimate: CostEstimateOut | None = None
    warnings: list[str] = []


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    q = req.question.strip()
    if not q:
        raise HTTPException(400, "question is empty")

    schema_text = render_schema_for_prompt(introspect_schema())

    try:
        sql = generate_sql(q, schema_text)
    except LLMUnavailable as exc:
        raise HTTPException(503, str(exc))

    if not sql:
        raise HTTPException(502, "LLM returned an empty SQL response")

    safe, reason = is_readonly(sql)
    if not safe:
        raise HTTPException(
            400,
            f"Generated SQL was unsafe and refused. SQL was: {sql!r}. Reason: {reason}",
        )

    warnings: list[str] = []

    cost: CostEstimateOut | None = None
    try:
        estimate = explain_query(sql)
        cost = CostEstimateOut(
            estimated_rows=estimate.estimated_rows,
            operators=list(estimate.operators),
            plan=estimate.plan,
        )
        # Friendly warning if the planner thinks this is going to be huge.
        if estimate.estimated_rows is not None and estimate.estimated_rows > 100_000:
            warnings.append(
                f"Planner estimates ~{estimate.estimated_rows:,} rows; the result is capped at 200 for display"
            )
    except Exception as exc:  # noqa: BLE001 — EXPLAIN failure shouldn't block /ask
        warnings.append(f"EXPLAIN preview failed (non-fatal): {exc}")

    try:
        result = execute_select(sql)
    except Exception as exc:
        raise HTTPException(
            422,
            f"SQL parsed and was read-only, but execution failed. SQL: {sql!r}. Error: {exc}",
        )

    if result.truncated:
        warnings.append(f"Result truncated to {result.row_count} rows")

    return AskResponse(
        question=q,
        sql=sql,
        columns=list(result.columns),
        rows=result.rows,
        row_count=result.row_count,
        truncated=result.truncated,
        cost_estimate=cost,
        warnings=warnings,
    )


@app.post("/validate-sql")
def validate_sql(sql: str) -> dict[str, Any]:
    """Run the safety layer against arbitrary SQL. Useful for testing."""
    safe, reason = is_readonly(sql)
    return {"safe": safe, "reason": reason}


class ExplainRequest(BaseModel):
    sql: str


@app.post("/explain", response_model=CostEstimateOut)
def explain(req: ExplainRequest) -> CostEstimateOut:
    """Run the safety-gated EXPLAIN against arbitrary SQL.

    Lets clients preview cost without hitting the LLM at all.
    """
    safe, reason = is_readonly(req.sql)
    if not safe:
        raise HTTPException(400, f"unsafe SQL: {reason}")
    estimate = explain_query(req.sql)
    return CostEstimateOut(
        estimated_rows=estimate.estimated_rows,
        operators=list(estimate.operators),
        plan=estimate.plan,
    )


# --- Static demo UI --------------------------------------------------------

_STATIC_DIR = Path(__file__).resolve().parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(str(_STATIC_DIR / "index.html"))

else:
    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "dataask",
            "version": "0.1.0",
            "docs": "/docs",
            "github": "https://github.com/anejakartik/dataask",
        }
