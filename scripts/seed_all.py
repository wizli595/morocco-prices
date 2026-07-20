"""Run all seed scripts in order."""

from scripts.generate_dim_time import main as generate_time
from scripts.seed_locations import seed_locations
from scripts.seed_products import seed_products
from scripts.seed_sources import seed_sources


def main() -> None:
    """Seed all dimension tables."""
    print("=== Seeding all dimensions ===")

    n = seed_products()
    print(f"  dim_product: {n} rows")

    n = seed_locations()
    print(f"  dim_location: {n} rows")

    n = seed_sources()
    print(f"  dim_source: {n} rows")

    generate_time()
    print("=== All seeds complete ===")


if __name__ == "__main__":
    main()
