"""DuckDB connection + schema introspection + query execution."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

import duckdb

from seed import seed_demo_dataset


log = logging.getLogger("dataask.db")

# Single in-memory DuckDB connection shared across requests.
# DuckDB connections are thread-safe for read; serialize writes if added later.
_conn: duckdb.DuckDBPyConnection | None = None


def get_conn() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        raise RuntimeError("DB not initialized — call init_db() at startup")
    return _conn


def init_db() -> dict[str, int]:
    """Open the connection and seed the demo dataset. Idempotent within a process."""
    global _conn
    if _conn is None:
        _conn = duckdb.connect(":memory:")
        log.info("dataask: DuckDB :memory: connection opened")
    counts = seed_demo_dataset(_conn)
    log.info("dataask: seeded demo dataset %s", counts)
    return counts


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    type: str


@dataclass(frozen=True)
class TableSpec:
    name: str
    columns: tuple[ColumnSpec, ...]


def introspect_schema() -> list[TableSpec]:
    """Return all tables and their columns in `main` schema."""
    con = get_conn()
    rows = con.execute(
        """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'main'
        ORDER BY table_name, ordinal_position
        """
    ).fetchall()
    bucket: dict[str, list[ColumnSpec]] = {}
    for table_name, column_name, data_type in rows:
        bucket.setdefault(table_name, []).append(
            ColumnSpec(name=column_name, type=str(data_type))
        )
    return [
        TableSpec(name=name, columns=tuple(cols))
        for name, cols in sorted(bucket.items())
    ]


def render_schema_for_prompt(tables: list[TableSpec]) -> str:
    """Compact DDL-like text representation the LLM can read."""
    lines: list[str] = []
    for t in tables:
        cols = ", ".join(f"{c.name} {c.type}" for c in t.columns)
        lines.append(f"{t.name}({cols})")
    return "\n".join(lines)


@dataclass(frozen=True)
class CostEstimate:
    """Rough pre-execute cardinality + operator breakdown from DuckDB EXPLAIN."""
    estimated_rows: int | None
    operators: tuple[str, ...]
    plan: str


@dataclass(frozen=True)
class QueryResult:
    columns: tuple[str, ...]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool


_ROW_ESTIMATE = re.compile(r"~(\d[\d,]*)\s+Rows?")
_OPERATOR = re.compile(r"^\s*│\s*(?P<op>[A-Z][A-Z_]{2,})\s*│\s*$", re.MULTILINE)


def explain_query(sql: str) -> CostEstimate:
    """Run DuckDB EXPLAIN and pull a quick cost estimate.

    Cheap (sub-millisecond on the schemas we ship); the planner runs but the
    query doesn't execute. Returns None for `estimated_rows` if DuckDB's
    output didn't include a cardinality (e.g. constant expressions).
    """
    con = get_conn()
    plan_rows = con.execute(f"EXPLAIN {sql}").fetchall()
    plan = "\n".join(r[1] for r in plan_rows) if plan_rows else ""

    operators: list[str] = _OPERATOR.findall(plan)

    estimated: int | None = None
    m = _ROW_ESTIMATE.search(plan)
    if m:
        try:
            estimated = int(m.group(1).replace(",", ""))
        except ValueError:
            estimated = None

    return CostEstimate(
        estimated_rows=estimated,
        operators=tuple(operators),
        plan=plan,
    )


def execute_select(sql: str, row_limit: int = 200) -> QueryResult:
    """Run a SELECT and return at most `row_limit` rows as dicts.

    Caller MUST have already validated `sql` via safety.is_readonly.
    """
    con = get_conn()
    cursor = con.execute(sql)
    description = cursor.description or []
    columns = tuple(d[0] for d in description)
    fetched = cursor.fetchmany(row_limit + 1)
    truncated = len(fetched) > row_limit
    fetched = fetched[:row_limit]
    rows = [_row_to_dict(columns, r) for r in fetched]
    return QueryResult(
        columns=columns,
        rows=rows,
        row_count=len(rows),
        truncated=truncated,
    )


def _row_to_dict(columns: tuple[str, ...], row: tuple) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for col, val in zip(columns, row):
        # Make non-JSON-native types serializable.
        if hasattr(val, "isoformat"):
            out[col] = val.isoformat()
        else:
            out[col] = val
    return out
