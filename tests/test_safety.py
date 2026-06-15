"""Smoke tests for the safety layer."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

from safety import is_readonly


def test_simple_select_allowed():
    ok, _ = is_readonly("SELECT 1")
    assert ok


def test_drop_blocked():
    ok, reason = is_readonly("DROP TABLE users")
    assert not ok
    assert "DROP" in reason or "non-SELECT" in reason


def test_insert_blocked():
    ok, reason = is_readonly("INSERT INTO users VALUES (1)")
    assert not ok


def test_update_blocked():
    ok, reason = is_readonly("UPDATE users SET name='x'")
    assert not ok


def test_multi_statement_blocked():
    ok, reason = is_readonly("SELECT 1; DROP TABLE users")
    assert not ok
    assert "statement" in reason.lower()


def test_empty_rejected():
    ok, _ = is_readonly("")
    assert not ok


def test_unparseable_rejected():
    ok, _ = is_readonly("this is not sql")
    assert not ok


def test_with_select_allowed():
    sql = "WITH cte AS (SELECT 1 AS x) SELECT x FROM cte"
    ok, _ = is_readonly(sql)
    assert ok
