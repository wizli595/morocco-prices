"""Seed dim_source from sources.csv."""

import csv
from pathlib import Path

from scripts.db import get_connection

SEED_PATH = Path(__file__).parent.parent / "data" / "seeds" / "sources.csv"

INSERT_SQL = """
    INSERT INTO serving.dim_source
        (source_id, source_name, organization,
         source_type, reliability, url, priority_rank)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (source_id) DO NOTHING
"""


def seed_sources() -> int:
    """Load sources.csv into dim_source, return row count."""
    conn = get_connection()
    cur = conn.cursor()
    count = 0

    with SEED_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cur.execute(
                INSERT_SQL,
                (
                    row["source_id"],
                    row["source_name"],
                    row["organization"],
                    row["source_type"],
                    row["reliability"],
                    row["url"] or None,
                    int(row["priority_rank"]),
                ),
            )
            count += 1

    conn.commit()
    cur.close()
    conn.close()
    return count


if __name__ == "__main__":
    n = seed_sources()
    print(f"dim_source: {n} rows loaded")
