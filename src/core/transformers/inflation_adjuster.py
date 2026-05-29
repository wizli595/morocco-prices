"""Adjust nominal MAD prices to real MAD using CPI."""

# CPI base 2010 = 100 (World Bank FP.CPI.TOTL for Morocco)
# We use 2017 as our reference year for "real MAD"
REFERENCE_YEAR = 2017

# Subset of CPI values (full series loaded at runtime from DB)
CPI_INDEX: dict[int, float] = {}


def load_cpi_from_rows(rows: list[tuple[int, float]]) -> None:
    """Populate CPI_INDEX from (year, cpi_value) tuples."""
    CPI_INDEX.clear()
    for year, cpi in rows:
        CPI_INDEX[year] = cpi


def adjust_to_real(
    nominal_mad: float,
    year: int,
) -> float | None:
    """Convert nominal MAD to real MAD (base = REFERENCE_YEAR)."""
    cpi_year = CPI_INDEX.get(year)
    cpi_ref = CPI_INDEX.get(REFERENCE_YEAR)

    if cpi_year is None or cpi_ref is None:
        return None
    if cpi_year == 0:
        return None

    return nominal_mad * (cpi_ref / cpi_year)


def inflation_rate(year_from: int, year_to: int) -> float | None:
    """Calculate cumulative inflation between two years."""
    cpi_from = CPI_INDEX.get(year_from)
    cpi_to = CPI_INDEX.get(year_to)

    if cpi_from is None or cpi_to is None:
        return None
    if cpi_from == 0:
        return None

    return (cpi_to - cpi_from) / cpi_from
