# Morocco Price Research — Current Landscape (July 2026)

Field research to ground the MaPrix data model in real, current data. Complements
the source list in [all_sources.md](all_sources.md) and the sheep deep-dive in
[sheep_prices.md](sheep_prices.md). All figures verified against web sources
(July 2026); see **Sources** at the end.

---

## 1. Macro Price Environment

Morocco has moved from a 2022–2023 inflation spike back to low inflation, but the
*level* of food prices stayed high — the disinflation is a slowing of increases,
not a reversal.

| Year | Headline inflation (annual avg) | Note |
|------|--------------------------------|------|
| 2022 | ~6.6% | Ukraine war, grain/feed spike |
| 2023 | ~6.1% | Food-led; meat +21% vs 2019 |
| 2024 | ~1.0% | Sharp disinflation |
| 2025 | ~0.8% | Lowest in years |
| 2026 (YTD) | 1.2%–1.7% (monthly YoY) | Jan 0.3 → Apr 1.7 → May 1.2 |

- **HCP CPI (base 100 = 2017):** reached **121.0 at end of March 2026** (vs 119.6
  in Feb). Monthly prints in 2026 are volatile and **food-driven**: May 2026 CPI
  fell 0.9% MoM on a 2.1% drop in the food index; April rose on an 8.4% jump in
  transport after the Middle-East fuel spike.
- Divergence to model: **food inflation is easing while non-food (housing,
  transport) inflation is rising** (non-food 2.6% YoY in May 2026). A single
  headline number hides this — the split matters.

---

## 2. The CPI / Food-CPI / Inflation Distinction (resolves the collector question)

These are three *different* series and the collectors must not conflate them:

| Concept | What it is | Unit | Best free source |
|---------|-----------|------|------------------|
| **Headline CPI** | Price *index* of the whole basket | index_point (base 2017=100 HCP, 2010=100 WB) | HCP; World Bank `FP.CPI.TOTL` |
| **Inflation rate** | YoY % change of headline CPI | percent | World Bank `FP.CPI.TOTL.ZG` |
| **Food CPI** | Price index of the *food* sub-basket | index_point | **FAOSTAT CP** (FAO_CP); HCP food division |

Key finding: **World Bank's free WDI API does _not_ expose a Morocco food-CPI
series.** `FP.CPI.TOTL.ZG` is headline inflation-%, *not* food. The proper feed
for a food index is:

- **FAOSTAT "Consumer Price Indices" (CP domain / FAO_CP):** provides both a
  General CPI and a **Food CPI** for Morocco, a consistent monthly series from
  **2000 onward** (pre-2000 gap-filled by FAO estimation). Also mirrored on World
  Bank data360 as dataset `FAO_CP`.
- **HCP:** the food division of the national IPC (and by 18 cities), base 2017.

➡ **Modeling implication:** `FP.CPI.TOTL.ZG` should map to a national **inflation
rate** product, never to `CPI-FOOD`. Leave `CPI-FOOD` to be populated by FAOSTAT
CP / HCP food division. (This is exactly the bug found in the audit.)

---

## 3. Verified Data-Source Matrix (2026)

| Source | Series provided | Coverage | Grain / Geo | Access |
|--------|----------------|----------|-------------|--------|
| **World Bank WDI** | Headline CPI (`FP.CPI.TOTL`, 2010=100); inflation % (`FP.CPI.TOTL.ZG`) | 1960–2024 | Annual, national | Free REST JSON, no auth |
| **FAOSTAT CP** | General CPI + **Food CPI** | 2000– (est. pre-2000) | Monthly+annual, national | Free bulk CSV / HDX |
| **FAOSTAT PP** | Producer prices, 200+ items (incl. sheep 977) | 1991–2024 | Annual, national | Free bulk CSV (wide format) |
| **HCP (IPC)** | Full CPI, food vs non-food, COICOP divisions | 2017– (base 2017) | Monthly, national + **18 cities** | Free Excel/HTML |
| **WFP / HDX** | Retail market prices, staple foods | 2010– | Monthly, market-level | Free CSV |
| **Selina Wamucii** | Export/import prices (live sheep, beef, etc.) | ~2010– | Annual, national | Web (scrape) |
| **News (Medias24, Le360…)** | Eid sheep prices, weekly wholesale meat | 2005– | Irregular, by city | Scrape |
| **Bank Al-Maghrib** | MAD FX rates, real-estate index (IPAI) | 1990s– | Monthly/quarterly | Web / request |

HCP IPC basket (authoritative): **546 articles, 1391 product varieties**, 12
COICOP divisions, base 100 = 2017, monthly, 18 cities.

---

## 4. Current Price Levels — Key Products (2026)

### Subsidized / regulated (Caisse de Compensation)
The 2026 Finance Bill earmarks **MAD 13.77 bn (~$1.34 bn)** to subsidize butane,
sugar, and soft-wheat flour.

| Product | 2026 price | Notes |
|---------|-----------|-------|
| Khobz (bread) | **1.20 MAD / loaf** | Government-regulated, flat nationwide |
| Butane 12 kg | held ~**MAD 40** retail; state still covers >half | Multi-year decompensation (Dh10/yr since 2024); in mid-2026 state paid ~MAD 78/cylinder to freeze retail after intl. prices +68% |
| Sugar, flour | controlled | Part of the MAD 13.77 bn envelope |

### Meat (the standout 2026 stress point)
| Product | 2026 price | Note |
|---------|-----------|------|
| Beef retail | **80–120 MAD/kg** (≈$11.3/kg, +14% YoY) | Import quotas (40,000 T tariff-suspended; 20,000 T Brazilian VAT-exempt) failed to fully calm prices |
| Sheep/mutton retail | **~150 MAD/kg** (Apr 2026) | Post-drought; wholesale ~118–133 pre-Eid |
| Sheep live (Eid, May 27 2026) | 1,500–5,000 DH/head (souks to 10–12k) | Supply recovered to 8–9M head after 2025 Eid was **cancelled** by the King |
| Chicken | ~40 MAD/kg | Cheapest meat, daily staple |

### Other staples (2026 retail)
- Milk 1 L ~7.9 MAD; common vegetables (potato, onion, tomato, carrot) 4–6 DH/kg.
- **Olive oil:** spiked past **120 MAD/L** in 2024–2025 (drought); the strong
  2025/26 harvest is pulling it back toward **50–52 MAD/L** — a ~50% swing, and a
  textbook case for the platform's outlier/seasonality flags.

---

## 5. Major 2024–2026 Price Drivers (for dim_time / event flags)

- **6-year drought (2018–2024):** feed costs +60–100%; the core driver of red-meat
  and olive-oil inflation.
- **Eid Al Adha 2025 CANCELLED:** King Mohammed VI urged abstention; herds down
  ~38%. First cancellation since 1996 — a structural break in the sheep series.
- **Butane decompensation (from May 2024):** planned Dh10/yr rises; a deliberate
  policy step-change in a subsidized price.
- **Middle-East conflict fuel spike (2026):** transport +8.4% in April 2026;
  butane intl. price +68% since March 2026 → re-subsidized.
- **Meat-import liberalization (2025–2026):** tariff/VAT exemptions on bovine/ovine
  imports — a supply-side intervention that only partially transmitted to price.

---

## 6. Implications for MaPrix

1. **Split CPI cleanly** into `CPI-NATIONAL` (index, WB `FP.CPI.TOTL` + HCP),
   `CPI-FOOD` (FAOSTAT CP + HCP food division — *not* WB inflation), and a distinct
   national **inflation rate** for `FP.CPI.TOTL.ZG`.
2. **Add FAOSTAT CP as a collector** — it's the missing free source for the food
   index and directly fills `CPI-FOOD`.
3. **Model food vs non-food separately** in gold aggregations — 2026 shows them
   diverging; a single headline number is misleading.
4. **Event flags earn their keep:** Eid-2025 cancellation, drought years, and the
   butane step-changes are exactly the anomalies the `dim_time` flags and
   `outlier_flagger` exist to explain rather than silently smooth.
5. **Regulated prices need a `subsidized`/`regulated` price_type** — khobz at a flat
   1.20 MAD and butane's administered price aren't market prices and shouldn't be
   outlier-flagged against market series.

---

## 7. Discrepancies Found in Existing Docs

- **HCP basket size:** `03_product_catalog.md` says "478 articles"; the current HCP
  figure (and `02_data_model.md`/`all_sources.md`) is **546 articles / 1391
  varieties**. Standardize on 546.
- **CPI base year:** docs cite base 2017 (correct and current); the WB API series is
  base 2010 — normalization must rebase one to the other before comparison.

---

## Sources

- [World Bank — Inflation, consumer prices (annual %), Morocco (FP.CPI.TOTL.ZG)](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=MA)
- [World Bank — Consumer price index (2010=100), Morocco (FP.CPI.TOTL)](https://data.worldbank.org/indicator/FP.CPI.TOTL?locations=MA)
- [World Bank data360 — Consumer Price Indices (FAO_CP)](https://data360.worldbank.org/en/dataset/FAO_CP)
- [FAOSTAT — Consumer price indices (Global/National, Annual)](https://data.apps.fao.org/catalog/dataset/faostat-cp)
- [FAOSTAT — Food Prices for Morocco (HDX)](https://data.humdata.org/dataset/faostat-food-prices-for-morocco)
- [HCP — Indices des prix à la consommation (IPC)](https://www.hcp.ma/Indices-des-prix-a-la-consommation-IPC_r348.html)
- [HCP — IPC Mars 2026 (Base 2017=100)](https://www.hcp.ma/L-Indice-des-prix-a-la-consommation-IPC-du-mois-de-Mars-2026_a4304.html)
- [IndexBox — Morocco CPI May 2026 (food-driven drop)](https://www.indexbox.io/blog/morocco-cpi-declines-09-in-may-2026-driven-by-food-price-drop/)
- [Morocco World News — CPI January 2026](https://www.moroccoworldnews.com/2026/02/279570/morocco-consumer-prices-rise-0-3-in-january-2026-as-food-costs-climb/)
- [Macrotrends — Morocco inflation rate history](https://www.macrotrends.net/global-metrics/countries/mar/morocco/inflation-rate-cpi)
- [Morocco World News — Meat policy spending big, delivering little (2026)](https://www.moroccoworldnews.com/2026/05/303733/moroccos-meat-policy-is-spending-big-and-delivering-little/)
- [Selina Wamucii — Beef price in Morocco (July 2026)](https://www.selinawamucii.com/insights/prices/morocco/beef/)
- [Morocco World News — MAD 1.34bn to support basic goods prices in 2026](https://www.moroccoworldnews.com/2025/10/265030/morocco-allocates-1-34-billion-to-support-basic-goods-prices-in-2026/)
- [Barlaman Today — Butane subsidized at MAD 78/cylinder (Apr 2026)](https://barlamantoday.com/2026/04/03/morocco-subsidizes-butane-at-mad-78-per-cylinder-to-hold-prices-steady/)
- [Hespress — State still covers over half of butane price](https://en.hespress.com/123819-state-still-covers-over-half-of-butane-price-as-subsidy-burden-slowly-declines.html)
- [Olive Oil Times — Moroccan growers hope for record harvest](https://www.oliveoiltimes.com/business/moroccan-olive-growers-hope-for-record-harvest-and-exports/141854)
- [Morocco World News — Record olive harvest, prices to drop 50%](https://www.moroccoworldnews.com/2025/09/259360/morocco-heads-for-recorded-olive-harvest-prices-expected-to-drop-50/)
- [Heerby — Food prices in Morocco 2026](https://heerby.ma/en/blog/food-cost-morocco-price-guide)
- [Washington Post — Morocco urges skipping Eid sacrifice (2025)](https://www.washingtonpost.com/world/2025/02/27/morocco-islam-climate-change-livestock-eid-al-adha/)
