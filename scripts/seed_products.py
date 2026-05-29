"""Seed dim_product from products.csv."""

import csv
from pathlib import Path

from scripts.db import get_connection

SEED_PATH = Path(__file__).parent.parent / "data" / "seeds" / "products.csv"

INSERT_SQL = """
    INSERT INTO serving.dim_product
        (product_id, category, subcategory, product_name,
         variety, name_en, name_fr, name_ar,
         canonical_unit, is_subsidized, is_seasonal)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (product_id) DO NOTHING
"""


def seed_products() -> int:
    """Load products.csv into dim_product, return row count."""
    conn = get_connection()
    cur = conn.cursor()
    count = 0

    with open(SEED_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cur.execute(INSERT_SQL, (
                row["product_id"], row["category"],
                row["subcategory"], row["product_name"],
                row["variety"] or None, row["name_en"],
                row["name_fr"], row["name_ar"] or None,
                row["canonical_unit"],
                row["is_subsidized"] == "true",
                row["is_seasonal"] == "true",
            ))
            count += 1

    conn.commit()
    cur.close()
    conn.close()
    return count


if __name__ == "__main__":
    n = seed_products()
    print(f"dim_product: {n} rows loaded")
