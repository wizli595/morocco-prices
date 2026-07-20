"""Domain enumerations for price observations."""

from enum import StrEnum, unique


@unique
class Confidence(StrEnum):
    """How trustworthy is this price observation."""

    OFFICIAL = "official"
    INSTITUTIONAL = "institutional"
    ESTIMATED = "estimated"
    RECONSTRUCTED = "reconstructed"
    JOURNALISTIC = "journalistic"
    ANECDOTAL = "anecdotal"


@unique
class Precision(StrEnum):
    """How precise is the reported value."""

    EXACT = "exact"
    RANGE = "range"
    APPROXIMATE = "approximate"
    INDEX_DERIVED = "index_derived"


@unique
class CollectionMethod(StrEnum):
    """How the data was obtained."""

    API = "api"
    FILE_DOWNLOAD = "file_download"
    SCRAPE = "scrape"
    MANUAL = "manual"
    CALCULATED = "calculated"


@unique
class PriceType(StrEnum):
    """What kind of price this represents."""

    RETAIL = "retail"
    WHOLESALE = "wholesale"
    PRODUCER = "producer"
    FARMGATE = "farmgate"
    IMPORT = "import"
    EXPORT = "export"
    SUBSIDIZED = "subsidized"
    INDEX = "index"


@unique
class SourceReliability(StrEnum):
    """Priority ranking for conflict resolution."""

    OFFICIAL = "official"
    INSTITUTIONAL = "institutional"
    COMMERCIAL = "commercial"
    JOURNALISTIC = "journalistic"
    ACADEMIC = "academic"
    ANECDOTAL = "anecdotal"


@unique
class LocationLevel(StrEnum):
    """Geographic granularity of the observation."""

    NATIONAL = "national"
    REGIONAL = "regional"
    PROVINCIAL = "provincial"
    CITY = "city"
    MARKET = "market"


@unique
class TimeGrain(StrEnum):
    """Temporal granularity of the observation."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
