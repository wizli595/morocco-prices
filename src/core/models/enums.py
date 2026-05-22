"""Domain enumerations for price observations."""

from enum import Enum, unique


@unique
class Confidence(str, Enum):
    """How trustworthy is this price observation."""

    OFFICIAL = "official"
    INSTITUTIONAL = "institutional"
    ESTIMATED = "estimated"
    RECONSTRUCTED = "reconstructed"
    JOURNALISTIC = "journalistic"
    ANECDOTAL = "anecdotal"


@unique
class Precision(str, Enum):
    """How precise is the reported value."""

    EXACT = "exact"
    RANGE = "range"
    APPROXIMATE = "approximate"
    INDEX_DERIVED = "index_derived"


@unique
class CollectionMethod(str, Enum):
    """How the data was obtained."""

    API = "api"
    FILE_DOWNLOAD = "file_download"
    SCRAPE = "scrape"
    MANUAL = "manual"
    CALCULATED = "calculated"


@unique
class PriceType(str, Enum):
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
class SourceReliability(str, Enum):
    """Priority ranking for conflict resolution."""

    OFFICIAL = "official"
    INSTITUTIONAL = "institutional"
    COMMERCIAL = "commercial"
    JOURNALISTIC = "journalistic"
    ACADEMIC = "academic"
    ANECDOTAL = "anecdotal"


@unique
class LocationLevel(str, Enum):
    """Geographic granularity of the observation."""

    NATIONAL = "national"
    REGIONAL = "regional"
    PROVINCIAL = "provincial"
    CITY = "city"
    MARKET = "market"


@unique
class TimeGrain(str, Enum):
    """Temporal granularity of the observation."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
