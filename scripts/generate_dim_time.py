"""Generate dim_time rows (1960-2030) and insert into PostgreSQL."""

from datetime import date, timedelta

from psycopg2.extensions import cursor as PgCursor

from scripts.calendar_morocco import is_eid_adha, is_ramadan, season
from scripts.db import get_connection

START_YEAR = 1960
END_YEAR = 2030
DAILY_FROM = 2010


def _insert_annual(cur: PgCursor) -> int:
    for year in range(START_YEAR, END_YEAR + 1):
        cur.execute(
            "INSERT INTO serving.dim_time (time_key, year, grain) "
            "VALUES (%s, %s, 'annual') ON CONFLICT DO NOTHING",
            (year * 10000, year),
        )
    return END_YEAR - START_YEAR + 1


def _insert_monthly(cur: PgCursor) -> int:
    count = 0
    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            cur.execute(
                "INSERT INTO serving.dim_time "
                "(time_key, year, month, quarter, grain, season) "
                "VALUES (%s,%s,%s,%s,'monthly',%s) ON CONFLICT DO NOTHING",
                (
                    year * 10000 + month * 100,
                    year,
                    month,
                    (month - 1) // 3 + 1,
                    season(month),
                ),
            )
            count += 1
    return count


def _insert_daily(cur: PgCursor) -> int:
    count = 0
    d = date(DAILY_FROM, 1, 1)
    end = date(END_YEAR, 12, 31)
    while d <= end:
        tk = d.year * 10000 + d.month * 100 + d.day
        cur.execute(
            "INSERT INTO serving.dim_time "
            "(time_key,date,year,month,day,quarter,grain,"
            "season,is_ramadan,is_eid_adha) "
            "VALUES (%s,%s,%s,%s,%s,%s,'daily',%s,%s,%s) "
            "ON CONFLICT DO NOTHING",
            (
                tk,
                d,
                d.year,
                d.month,
                d.day,
                (d.month - 1) // 3 + 1,
                season(d.month),
                is_ramadan(d),
                is_eid_adha(d),
            ),
        )
        d += timedelta(days=1)
        count += 1
    return count


def main() -> None:
    """Generate full dim_time table."""
    print("Generating dim_time...")
    conn = get_connection()
    cur = conn.cursor()

    n = _insert_annual(cur)
    print(f"  Annual: {n}")
    n = _insert_monthly(cur)
    print(f"  Monthly: {n}")
    n = _insert_daily(cur)
    print(f"  Daily: {n}")

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
