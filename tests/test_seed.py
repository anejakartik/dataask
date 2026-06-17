"""Smoke tests for the seed + introspection layer."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

import duckdb  # noqa: E402

from db import (  # noqa: E402
    introspect_schema,
    render_schema_for_prompt,
)
from seed import seed_demo_dataset  # noqa: E402


def test_seed_creates_tables(monkeypatch):
    con = duckdb.connect(":memory:")

    # Point db.get_conn() at our connection for introspection.
    import db as db_mod

    monkeypatch.setattr(db_mod, "_conn", con)

    counts = seed_demo_dataset(con)
    assert counts["customers"] > 0
    assert counts["orders"] > 0
    assert counts["events"] > 0

    schema = introspect_schema()
    names = {t.name for t in schema}
    assert {"customers", "subscriptions", "orders", "events"}.issubset(names)


def test_render_schema_for_prompt_compact(monkeypatch):
    con = duckdb.connect(":memory:")
    import db as db_mod

    monkeypatch.setattr(db_mod, "_conn", con)
    seed_demo_dataset(con)

    text = render_schema_for_prompt(introspect_schema())
    assert "customers(" in text
    assert "orders(" in text
    # No newlines inside a table line.
    for line in text.splitlines():
        assert line.count("(") == 1
