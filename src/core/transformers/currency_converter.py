"""Convert prices between currencies using historical rates."""

# Historical MAD/USD annual average rates (Bank Al-Maghrib)
# Source: World Bank, IMF
MAD_PER_USD: dict[int, float] = {
    1970: 5.06, 1975: 4.05, 1980: 3.94, 1985: 10.06,
    1990: 8.24, 1991: 8.71, 1992: 8.54, 1993: 9.30,
    1994: 9.20, 1995: 8.54, 1996: 8.72, 1997: 9.53,
    1998: 9.60, 1999: 9.80, 2000: 10.63, 2001: 11.30,
    2002: 11.02, 2003: 9.57, 2004: 8.87, 2005: 8.87,
    2006: 8.80, 2007: 8.20, 2008: 7.75, 2009: 8.06,
    2010: 8.42, 2011: 8.09, 2012: 8.63, 2013: 8.41,
    2014: 8.41, 2015: 9.75, 2016: 9.78, 2017: 9.69,
    2018: 9.39, 2019: 9.62, 2020: 9.50, 2021: 8.99,
    2022: 10.16, 2023: 10.13, 2024: 9.95,
}


def usd_to_mad(value: float, year: int) -> float | None:
    """Convert USD to MAD at the historical annual rate."""
    rate = _get_rate(year)
    if rate is None:
        return None
    return value * rate


def mad_to_usd(value: float, year: int) -> float | None:
    """Convert MAD to USD at the historical annual rate."""
    rate = _get_rate(year)
    if rate is None:
        return None
    return value / rate


def _get_rate(year: int) -> float | None:
    """Look up rate, interpolate if missing."""
    if year in MAD_PER_USD:
        return MAD_PER_USD[year]
    return _interpolate_rate(year)


def _interpolate_rate(year: int) -> float | None:
    """Linear interpolation between known years."""
    years = sorted(MAD_PER_USD.keys())
    if year < years[0] or year > years[-1]:
        return None

    for i in range(len(years) - 1):
        if years[i] <= year <= years[i + 1]:
            y0, y1 = years[i], years[i + 1]
            r0, r1 = MAD_PER_USD[y0], MAD_PER_USD[y1]
            frac = (year - y0) / (y1 - y0)
            return r0 + frac * (r1 - r0)
    return None
