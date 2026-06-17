"""Synthetic SaaS demo dataset.

Generates a small, realistic dataset (customers / subscriptions / orders / events)
that's representative enough for natural-language analytics questions a founder
or PM would actually ask.

Deterministic: same input → same dataset, so demos are reproducible.
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from typing import Iterable

import duckdb


SEED = 20260616
PLANS = ("starter", "pro", "enterprise")
COUNTRIES = ("US", "UK", "CA", "DE", "IN", "AU", "FR", "BR")
PLAN_MRR = {"starter": 29.0, "pro": 99.0, "enterprise": 499.0}
ORDER_STATUSES = ("paid", "refunded", "failed")
EVENT_NAMES = (
    "login",
    "dashboard_view",
    "report_run",
    "export_csv",
    "invite_sent",
    "settings_update",
)


def _date_between(start: date, end: date, rnd: random.Random) -> datetime:
    span = (end - start).days
    return datetime.combine(
        start + timedelta(days=rnd.randint(0, span)),
        datetime.min.time(),
    ) + timedelta(seconds=rnd.randint(0, 86399))


def seed_demo_dataset(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Idempotent: drops + recreates the demo tables.

    Returns a row-count summary for logging.
    """
    rnd = random.Random(SEED)

    today = date(2026, 6, 17)
    one_year_ago = today - timedelta(days=365)

    # ----- customers ------------------------------------------------------
    customers: list[tuple] = []
    for i in range(1, 201):
        signup = _date_between(one_year_ago, today, rnd)
        customers.append(
            (
                i,
                f"Customer {i:03d}",
                rnd.choice(PLANS),
                rnd.choice(COUNTRIES),
                signup.date(),
            )
        )

    # ----- subscriptions --------------------------------------------------
    # Each customer has 1-2 subscription history rows.
    subscriptions: list[tuple] = []
    sub_id = 1
    for cust_id, _, plan, _, signup_date in customers:
        first_start = datetime.combine(signup_date, datetime.min.time())
        first_plan = rnd.choice(PLANS)
        churned = rnd.random() < 0.18
        if churned:
            end = first_start + timedelta(days=rnd.randint(30, 250))
            if end.date() > today:
                end = datetime.combine(today, datetime.min.time())
            subscriptions.append(
                (
                    sub_id,
                    cust_id,
                    first_plan,
                    PLAN_MRR[first_plan],
                    first_start,
                    end,
                )
            )
            sub_id += 1
            # 20% chance they came back on a new plan
            if rnd.random() < 0.2:
                new_plan = rnd.choice(PLANS)
                new_start = end + timedelta(days=rnd.randint(7, 60))
                if new_start.date() <= today:
                    subscriptions.append(
                        (
                            sub_id,
                            cust_id,
                            new_plan,
                            PLAN_MRR[new_plan],
                            new_start,
                            None,
                        )
                    )
                    sub_id += 1
        else:
            subscriptions.append(
                (
                    sub_id,
                    cust_id,
                    plan,
                    PLAN_MRR[plan],
                    first_start,
                    None,
                )
            )
            sub_id += 1

    # ----- orders ---------------------------------------------------------
    orders: list[tuple] = []
    order_id = 1
    for cust_id, _, _, _, signup_date in customers:
        num_orders = rnd.choices([0, 1, 2, 3, 5, 8, 12], weights=[1, 4, 6, 5, 4, 3, 2])[0]
        for _ in range(num_orders):
            ts = _date_between(signup_date, today, rnd)
            amount = round(rnd.uniform(15, 850), 2)
            status = rnd.choices(ORDER_STATUSES, weights=[88, 7, 5])[0]
            orders.append((order_id, cust_id, amount, status, ts))
            order_id += 1

    # ----- events ---------------------------------------------------------
    events: list[tuple] = []
    event_id = 1
    for cust_id, _, _, _, signup_date in customers:
        n = rnd.randint(0, 35)
        for _ in range(n):
            ts = _date_between(signup_date, today, rnd)
            name = rnd.choice(EVENT_NAMES)
            events.append((event_id, cust_id, name, ts))
            event_id += 1

    # ----- write into DuckDB ---------------------------------------------
    con.execute("DROP TABLE IF EXISTS customers")
    con.execute("DROP TABLE IF EXISTS subscriptions")
    con.execute("DROP TABLE IF EXISTS orders")
    con.execute("DROP TABLE IF EXISTS events")

    con.execute(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            plan VARCHAR,
            country VARCHAR,
            signup_date DATE
        )
        """
    )
    con.execute(
        """
        CREATE TABLE subscriptions (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            plan VARCHAR,
            mrr DOUBLE,
            started_at TIMESTAMP,
            ended_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            amount DOUBLE,
            status VARCHAR,
            created_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            event_name VARCHAR,
            occurred_at TIMESTAMP
        )
        """
    )

    _bulk_insert(con, "customers", customers)
    _bulk_insert(con, "subscriptions", subscriptions)
    _bulk_insert(con, "orders", orders)
    _bulk_insert(con, "events", events)

    return {
        "customers": len(customers),
        "subscriptions": len(subscriptions),
        "orders": len(orders),
        "events": len(events),
    }


def _bulk_insert(
    con: duckdb.DuckDBPyConnection,
    table: str,
    rows: Iterable[tuple],
) -> None:
    rows = list(rows)
    if not rows:
        return
    placeholders = ",".join(["?"] * len(rows[0]))
    con.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
