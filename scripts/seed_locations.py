"""Seed dim_location from locations.csv."""

import csv
from pathlib import Path

from scripts.db import get_connection

SEED_PATH = Path(__file__).parent.parent / "data" / "seeds" / "locations.csv"

INSERT_SQL = """
    INSERT INTO serving.dim_location
        (location_id, country, region, province,
         city, market, level, latitude, longitude)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (location_id) DO NOTHING
"""


def _parse_float(val: str) -> float | None:
    return float(val) if val else None


def seed_locations() -> int:
    """Load locations.csv into dim_location, return row count."""
    conn = get_connection()
    cur = conn.cursor()
    count = 0

    with open(SEED_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cur.execute(INSERT_SQL, (
                row["location_id"], row["country"],
                row["region"] or None, row["province"] or None,
                row["city"] or None, row["market"] or None,
                row["level"],
                _parse_float(row["latitude"]),
                _parse_float(row["longitude"]),
            ))
            count += 1

    conn.commit()
    cur.close()
    conn.close()
    return count


if __name__ == "__main__":
    n = seed_locations()
    print(f"dim_location: {n} rows loaded")
