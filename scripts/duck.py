#!/usr/bin/env python3
"""Tiny replacement for the `duckdb` CLI used in the dbt lab.

  duck.py [--readonly] <database> "<SQL; SQL; ...>"   run the statements, print each result
  duck.py [--readonly] <database> --audit              print the tables created by `dbt test --store-failures`
"""
import os
import sys

import duckdb


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    readonly = "--readonly" in args
    audit = "--audit" in args
    args = [a for a in args if a not in ("--readonly", "--audit")]
    db = args[0]
    con = duckdb.connect(db, read_only=readonly)
    if os.environ.get("LAB_BASE_URI", "").startswith("s3://"):
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")
    if audit:
        tables = con.execute(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema LIKE '%dbt_test__audit' ORDER BY ALL"
        ).fetchall()
        if not tables:
            print("No failure table (every test passed, or --store-failures was not used).")
        for schema, name in tables:
            print(f"--- {schema}.{name}")
            con.sql(f'SELECT * FROM "{schema}"."{name}" LIMIT 10').show(max_width=200)
        return
    for stmt in [s.strip() for s in args[1].split(";") if s.strip()]:
        res = con.sql(stmt)
        if res is not None:
            res.show(max_width=200)


if __name__ == "__main__":
    main()
