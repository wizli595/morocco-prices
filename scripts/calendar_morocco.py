"""Moroccan calendar helpers: Eid, Ramadan, seasons."""

from datetime import date, timedelta

# Eid Al Adha approximate dates (year → month, day)
EID_ADHA = {
    2015: (9, 24), 2016: (9, 12), 2017: (9, 1),
    2018: (8, 22), 2019: (8, 11), 2020: (7, 31),
    2021: (7, 20), 2022: (7, 9), 2023: (6, 29),
    2024: (6, 17), 2025: (6, 7), 2026: (5, 27),
    2027: (5, 16), 2028: (5, 5), 2029: (4, 24),
    2030: (4, 14),
}

# Ramadan approximate start dates
RAMADAN_START = {
    2020: (4, 24), 2021: (4, 13), 2022: (4, 2),
    2023: (3, 23), 2024: (3, 11), 2025: (3, 1),
    2026: (2, 18), 2027: (2, 8), 2028: (1, 28),
    2029: (1, 16), 2030: (1, 6),
}


def is_eid_adha(d: date) -> bool:
    """True if date is within 3 days of Eid Al Adha."""
    eid = EID_ADHA.get(d.year)
    if not eid:
        return False
    return abs((d - date(d.year, eid[0], eid[1])).days) <= 3


def is_ramadan(d: date) -> bool:
    """True if date falls within Ramadan (~30 days)."""
    ram = RAMADAN_START.get(d.year)
    if not ram:
        return False
    start = date(d.year, ram[0], ram[1])
    return start <= d <= start + timedelta(days=29)


def season(month: int) -> str:
    """Return season name for a given month."""
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    if month in (9, 10, 11):
        return "autumn"
    return "winter"
