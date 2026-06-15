"""SQL safety layer — read-only enforcement via sqlglot AST.

HARD CONSTRAINT: no path may execute SQL without calling is_readonly() first.
"""

from __future__ import annotations

import sqlglot
from sqlglot import expressions as exp


def is_readonly(sql: str, dialect: str = "duckdb") -> tuple[bool, str]:
    """Return (is_safe, reason).

    Reject:
      - Anything that's not a single SELECT statement
      - Multi-statement input (would allow query stuffing)
      - DDL (CREATE/DROP/ALTER), DML (INSERT/UPDATE/DELETE)
      - PRAGMA, ATTACH, COPY TO (data exfiltration risk)
    """
    if not sql or not sql.strip():
        return False, "empty SQL"

    try:
        statements = sqlglot.parse(sql, read=dialect)
    except Exception as e:
        return False, f"unparseable: {e}"

    if len(statements) != 1:
        return False, f"expected 1 statement, got {len(statements)}"

    stmt = statements[0]
    if stmt is None:
        return False, "empty parse result"

    if not isinstance(stmt, exp.Select) and not _is_safe_with(stmt):
        return False, f"non-SELECT statement: {type(stmt).__name__}"

    return True, "ok"


def _is_safe_with(stmt: exp.Expression) -> bool:
    """Allow `WITH ... SELECT ...` (CTEs) but only if the final body is SELECT."""
    if isinstance(stmt, exp.With):
        body = stmt.this
        return isinstance(body, exp.Select)
    return False
