# Morocco Price Data - All Sources

## Can We Build a Dataset from 19xx to Present?

### Realistic Assessment

| Period | What Exists | Granularity |
|--------|------------|-------------|
| **1960-present** | CPI index (World Bank, IMF) | National, annual, just an index number |
| **1991-present** | Food CPI + Producer prices (FAOSTAT) | National, annual, by commodity category |
| **2007-present** | Detailed CPI (Trading Economics, HCP) | Monthly, by city (18 cities) |
| **2010-present** | Food market prices (WFP) | By market/city, monthly, individual commodities (meat, bread, oil...) |
| **Pre-1960** | Almost nothing digitized | Would need library/archive research |

**Verdict:** A unified dataset is possible but with gaps:
- **1960-1990**: Only aggregate CPI index (no meat price, no city breakdown)
- **1991-2010**: National-level food categories (meat as a category, not per-kilo price)
- **2010-present**: Actual commodity prices (1kg beef, 1kg chicken, etc.) by city

For actual **meat prices per kg by region going back decades** - that data simply doesn't exist in any digital source. Morocco's statistical infrastructure wasn't collecting/publishing that granularly until recently.

---

## 1. FREE APIs (No Auth, Programmatic Access)

### World Bank API
- **CPI (2010=100):** https://data.worldbank.org/indicator/FP.CPI.TOTL?locations=MA
- **Inflation rate (annual %):** https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=MA
- **API endpoint:** `https://api.worldbank.org/v2/country/MAR/indicator/FP.CPI.TOTL?format=json&date=1960:2025&per_page=100`
- Coverage: **1960-2024**, annual, national
- Format: JSON, CSV, XML - free, no auth

### IMF Data
- **CPI dataset:** https://data.imf.org/en/datasets/IMF.STA:CPI
- **DataMapper Morocco:** https://www.imf.org/external/datamapper/profile/MAR
- **WEO bulk download:** https://www.imf.org/en/Publications/WEO/weo-database
- Coverage: 1980s-present + forecasts to 2030, national
- Format: CSV, JSON API

---

## 2. FREE DOWNLOADABLE DATASETS

### HCP Morocco (Official Stats Agency) - BEST FOR REGIONAL DATA
- **CPI by 18 cities (IPC):** https://www.hcp.ma/downloads/IPC-Indice-des-prix-a-la-consommation_t12173.html
- **IPC main page:** https://www.hcp.ma/Indices-des-prix-a-la-consommation-IPC_r348.html
- **All price indices:** https://www.hcp.ma/Indices-des-prix-et-production_r343.html
- **Databases portal:** https://www.hcp.ma/Bases-de-donnees_r631.html
- **Microdata (surveys):** https://www.hcp.ma/Micro-donnees-Open-data_r632.html
- Cities: Agadir, Casablanca, Fes, Kenitra, Marrakech, Oujda, Rabat, Tetouan, Meknes, Tangier, Laayoune, Dakhla, Guelmim, Settat, Safi, Beni Mellal, Al Hoceima, Errachidia
- Coverage: Monthly, base 100=2017, 546 articles in basket
- Format: Excel (XLS)

### data.gov.ma (Morocco Open Data Portal)
- **CPI base 2017:** https://data.gov.ma/data/fr/dataset/data_7_5
- **CPI base 2006:** https://data.gov.ma/data/fr/dataset/data_7_1
- **Household consumption expenditure:** https://data.gov.ma/data/dataset/data_12_9
- Format: XLSX
- Note: Portal may be sparsely populated

### WFP Food Prices (via HDX) - BEST FOR ACTUAL COMMODITY PRICES
- **Morocco food prices:** https://data.humdata.org/dataset/wfp-food-prices-for-morocco
- **Global food prices DB:** https://data.humdata.org/dataset/wfp-food-prices
- What: Retail prices for staple foods (wheat, rice, sugar, oil, meat, etc.) by market
- Coverage: Market-level, monthly, multiple years
- Format: CSV, free download

### FAOSTAT
- **Producer prices:** https://www.fao.org/faostat/en/#data/PP (filter for Morocco)
- **Consumer price indices:** https://www.fao.org/faostat/en/#data/CP
- **Catalog:** https://data.apps.fao.org/catalog/dataset/faostat-pp
- What: Farm-gate prices for 262+ agricultural products
- Coverage: Annual from 1991, monthly from 2010, national
- Format: CSV

### HDX - FAOSTAT Mirror
- **FAOSTAT food prices for Morocco:** https://data.humdata.org/dataset/faostat-food-prices-for-morocco
- Includes: Consumer Price Indices, Deflators, Producer Prices
- Coverage: 1991-2024, national
- Format: CSV direct download

### FRED (Federal Reserve)
- **CPI Morocco (World Bank source):** https://fred.stlouisfed.org/series/DDOE01MAA086NWDB (1960-2017)
- **Inflation annual %:** https://fred.stlouisfed.org/series/FPCPITOTLZGMAR (1960-2024)
- **CPI inflation (IMF source):** https://fred.stlouisfed.org/series/MARPCPIPCHPT (2000-2030)
- **Core CPI inflation:** https://fred.stlouisfed.org/series/MARPCPICOREPCHPT
- Format: CSV download

### Macrotrends
- **Historical inflation rate:** https://www.macrotrends.net/global-metrics/countries/mar/morocco/inflation-rate-cpi
- Coverage: 1960-2024, national
- Format: CSV/Excel

### Morocco OpenDataForAfrica
- **Portal:** https://morocco.opendataforafrica.org/
- What: CPI data sourced from HCP, 385 items basket (base 2006)
- Format: Interactive portal with export

---

## 3. KAGGLE DATASETS

### Morocco Housing Prices
- https://www.kaggle.com/datasets/yassinesadiki/housing-data-in-morocco
- Updated: April 2025, by city, CSV

### Morocco Food Dataset
- https://www.kaggle.com/datasets/othmanehilal/morocco-food-dataset
- Format: CSV

### Global Food Prices (includes Morocco)
- https://www.kaggle.com/datasets/jboysen/global-food-prices
- https://www.kaggle.com/datasets/salehahmedrony/global-food-prices
- WFP data mirrored on Kaggle

### Global Cost of Living (includes Moroccan cities)
- https://www.kaggle.com/datasets/mvieira101/global-cost-of-living
- 4,500+ cities worldwide

---

## 4. PAID / RESTRICTED SOURCES

### Trading Economics
- **CPI:** https://tradingeconomics.com/morocco/consumer-price-index-cpi
- **Food inflation:** https://tradingeconomics.com/morocco/food-inflation
- **Housing index:** https://tradingeconomics.com/morocco/housing-index
- **All indicators:** https://tradingeconomics.com/morocco/indicators
- Coverage: 2007-2026, monthly
- API starts at ~$49/month

### Numbeo (Cost of Living by City)
- **Morocco:** https://www.numbeo.com/cost-of-living/country_result.jsp?country=Morocco
- **Casablanca:** https://www.numbeo.com/cost-of-living/in/Casablanca
- 51+ price items, 17+ Moroccan cities
- Paid API for bulk data

### Bank Al-Maghrib (Central Bank)
- **Statistics:** https://www.bkam.ma/Statistiques
- **Real Estate Price Index (IPAI):** Published quarterly, covers major cities by property type
- Some data may require requesting access

---

## 5. REAL ESTATE (Scraping Required)

### Mubawab
- https://www.mubawab.ma
- Listings across all Moroccan cities, prices in MAD
- URL pattern: `/fr/ct/casablanca/immobilier-a-vendre`

### Sarouty
- https://www.sarouty.ma
- Residential + commercial listings
- URL pattern: `/acheter/{property-type}/`

### Avito
- https://www.avito.ma/fr/maroc/immobilier
- Largest classifieds platform, SPA (hard to scrape)

---

## 6. FAO FOOD PRICE MONITORING
- **GIEWS FPMA tool:** https://fpma.fao.org/giews/fpmat4/
- Interactive tool with CSV download for individual commodities by market
- Covers wheat, bread, sugar, cooking oil, etc. for Moroccan markets

---

## Strategy to Build the Best Possible Dataset

### Phase 1: Aggregate what exists (free, easy)
1. World Bank API -> CPI + inflation 1960-2024 (national, annual)
2. FAOSTAT/HDX -> Food CPI + producer prices 1991-2024 (national, by category)
3. WFP/HDX -> Actual food commodity prices 2010+ (by market, monthly)
4. HCP Excel downloads -> CPI by 18 cities (monthly, recent years)

### Phase 2: Enrich (more effort)
5. Kaggle housing dataset -> Property prices by city
6. Numbeo scrape -> 51 price items across 17+ cities (current snapshot)
7. FAO GIEWS -> Individual commodity prices by market

### Phase 3: Historical research (hardest)
8. Bank Al-Maghrib PDFs -> Extract historical data from annual reports
9. French colonial archives -> Pre-independence price data (academic research)
10. HCP household surveys (2007, 2014) -> Microdata on spending patterns

### Final dataset structure:
```
year | month | region/city | category | item | price_mad | price_usd | source
1960 | NULL  | National    | CPI      | Index| 12.3      | NULL      | WorldBank
2015 | 03    | Casablanca  | Food     | Beef | 85.0      | 8.70      | WFP
2024 | 01    | Marrakech   | CPI      | Index| 122.5     | NULL      | HCP
```
