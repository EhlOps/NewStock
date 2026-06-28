"""
weights.py
==========
Credibility/quality weighting table for news source domains, intended for
ingest-broad / weight-downstream sentiment pipelines (GDELT GKG, RSS, social).

USAGE
-----
- Match GDELT `SourceCommonName` (or your RSS feed domain) against `domain`
  AFTER normalizing: lowercase, strip leading 'www.', 'm.', 'edition.', 'amp.'.
- Multiply that source's raw sentiment contribution by `weight`.
- `source_type` lets you handle press releases / social / aggregators
  differently (e.g. press releases signal EVENTS, not organic sentiment).
- `tier` is a coarse bucket; `weight` is the fine-grained multiplier you
  actually blend with. Tune `weight` over time in one place.

WEIGHT SCALE (suggested)
------------------------
1.00  gold-standard wire / primary market desk
0.90  major business/financial outlet
0.75  strong general outlet with serious business desk
0.60  solid regional / international financial
0.45  trader-focused / opinion-heavy / higher-noise
0.30  aggregator / syndicator (dedupe risk) or high-bias
0.20  press release wire (reliable fact, company-originated)
0.40  social / community (sentiment-native but noisy)

CAVEATS
-------
- Tiers 1-3 are well-verified. The long-tail regional/trade entries exist to
  give GDELT breadth a credibility floor; VERIFY them against real GDELT
  `SourceCommonName` values before trusting blindly (subdomains, regional
  editions, and renamed/defunct outlets are common failure points).
- These are CREDIBILITY weights, not sentiment-accuracy weights. Weight,
  don't gatekeep: a strong velocity spike from a low-weight source can still
  be the earliest real signal. Keep weights as a bias, not a filter.
- `source_type` values: wire | market | business | general | international |
  trader | aggregator | press_release | social
"""

from functools import lru_cache

# Prefixes stripped (in addition to lowercasing) when normalizing a domain.
_STRIP_PREFIXES = ("www.", "m.", "amp.", "edition.", "mobile.")


def source_weights():
    """Return the raw credibility table as `(domain, tier, source_type, weight)`
    tuples. This is the single place to edit/tune the data."""
    return [
        # ---------- TIER 1: WIRE SERVICES ----------
        ("reuters.com",            1, "wire",          1.00),
        ("apnews.com",             1, "wire",          1.00),
        ("bloomberg.com",          1, "wire",          1.00),
        ("ft.com",                 1, "wire",          0.98),
        ("wsj.com",                1, "wire",          0.98),
        ("afp.com",                1, "wire",          0.95),
        ("dowjones.com",           1, "wire",          0.95),

        # ---------- TIER 1.5: PRIMARY MARKET / BUSINESS DESKS ----------
        ("cnbc.com",               1, "market",        0.95),
        ("marketwatch.com",        1, "market",        0.92),
        ("barrons.com",            1, "market",        0.92),
        ("nasdaq.com",             1, "market",        0.88),
        ("finance.yahoo.com",      1, "market",        0.88),
        ("investors.com",          1, "market",        0.88),  # IBD

        # ---------- TIER 2: MAJOR BUSINESS / FINANCIAL ----------
        ("businessinsider.com",    2, "business",      0.78),
        ("fortune.com",            2, "business",      0.80),
        ("forbes.com",             2, "business",      0.72),
        ("economist.com",          2, "business",      0.88),
        ("fastcompany.com",        2, "business",      0.70),
        ("inc.com",                2, "business",      0.65),
        ("entrepreneur.com",       2, "business",      0.55),
        ("axios.com",              2, "business",      0.82),
        ("semafor.com",            2, "business",      0.72),
        ("quartz.com",             2, "business",      0.68),
        ("thestreet.com",          2, "market",        0.65),
        ("kiplinger.com",          2, "business",      0.55),

        # ---------- TIER 2: GENERAL OUTLETS w/ SERIOUS BUSINESS DESKS ----------
        ("nytimes.com",            2, "general",       0.85),
        ("washingtonpost.com",     2, "general",       0.82),
        ("theguardian.com",        2, "general",       0.78),
        ("bbc.com",                2, "general",       0.85),
        ("bbc.co.uk",              2, "general",       0.85),
        ("npr.org",                2, "general",       0.78),
        ("latimes.com",            2, "general",       0.70),
        ("usatoday.com",           2, "general",       0.62),
        ("time.com",               2, "general",       0.65),
        ("theatlantic.com",        2, "general",       0.70),
        ("newyorker.com",          2, "general",       0.68),
        ("politico.com",           2, "general",       0.75),
        ("thehill.com",            2, "general",       0.62),
        ("abcnews.go.com",         2, "general",       0.68),
        ("nbcnews.com",            2, "general",       0.68),
        ("cbsnews.com",            2, "general",       0.68),
        ("cnn.com",                2, "general",       0.66),
        ("foxbusiness.com",        2, "market",        0.70),
        ("foxnews.com",            2, "general",       0.55),

        # ---------- TIER 2: INTERNATIONAL / REGIONAL FINANCIAL ----------
        ("nikkei.com",             2, "international",  0.85),
        ("asia.nikkei.com",        2, "international",  0.85),
        ("scmp.com",               2, "international",  0.75),
        ("caixinglobal.com",       2, "international",  0.78),
        ("afr.com",                2, "international",  0.82),  # Australian Financial Review
        ("theglobeandmail.com",    2, "international",  0.78),
        ("handelsblatt.com",       2, "international",  0.80),
        ("lesechos.fr",            2, "international",  0.80),
        ("lemonde.fr",             2, "international",  0.72),
        ("faz.net",                2, "international",  0.75),
        ("spiegel.de",             2, "international",  0.72),
        ("zeit.de",                2, "international",  0.70),
        ("elpais.com",             2, "international",  0.70),
        ("expansion.com",          2, "international",  0.70),  # Spanish financial
        ("ilsole24ore.com",        2, "international",  0.78),  # Italian financial
        ("economictimes.indiatimes.com", 2, "international", 0.72),
        ("livemint.com",           2, "international",  0.72),
        ("business-standard.com",  2, "international",  0.70),
        ("moneycontrol.com",       2, "international",  0.65),
        ("thehindubusinessline.com",2,"international",  0.68),
        ("japantimes.co.jp",       2, "international",  0.70),
        ("koreaherald.com",        2, "international",  0.65),
        ("koreatimes.co.kr",       2, "international",  0.62),
        ("straitstimes.com",       2, "international",  0.70),
        ("businesstimes.com.sg",   2, "international",  0.72),
        ("channelnewsasia.com",    2, "international",  0.70),
        ("theedgemarkets.com",     2, "international",  0.66),
        ("bangkokpost.com",        2, "international",  0.60),
        ("gulfnews.com",           2, "international",  0.60),
        ("thenationalnews.com",    2, "international",  0.65),
        ("arabnews.com",           2, "international",  0.58),
        ("aljazeera.com",          2, "international",  0.65),
        ("rte.ie",                 2, "international",  0.62),
        ("irishtimes.com",         2, "international",  0.66),
        ("independent.co.uk",      2, "international",  0.60),
        ("telegraph.co.uk",        2, "international",  0.66),
        ("thetimes.co.uk",         2, "international",  0.72),
        ("cityam.com",             2, "international",  0.65),  # London business
        ("euronews.com",           2, "international",  0.62),
        ("dw.com",                 2, "international",  0.65),
        ("france24.com",           2, "international",  0.62),
        ("swissinfo.ch",           2, "international",  0.62),
        ("themoscowtimes.com",     2, "international",  0.50),
        ("smh.com.au",             2, "international",  0.66),
        ("theage.com.au",          2, "international",  0.64),
        ("abc.net.au",             2, "international",  0.70),
        ("nzherald.co.nz",         2, "international",  0.62),
        ("cbc.ca",                 2, "international",  0.70),
        ("financialpost.com",      2, "international",  0.74),
        ("nationalpost.com",       2, "international",  0.62),

        # ---------- TIER 2.5: MARKET-NATIVE / TRADER-FOCUSED ----------
        ("seekingalpha.com",       3, "trader",        0.55),
        ("benzinga.com",           3, "trader",        0.55),
        ("investing.com",          3, "trader",        0.52),
        ("morningstar.com",        2, "market",        0.78),
        ("fool.com",               3, "trader",        0.35),  # Motley Fool: promotional, down-weight
        ("zacks.com",              3, "trader",        0.40),
        ("tipranks.com",           3, "trader",        0.45),
        ("marketbeat.com",         3, "trader",        0.40),
        ("simplywall.st",          3, "trader",        0.45),
        ("gurufocus.com",          3, "trader",        0.48),
        ("finviz.com",             3, "trader",        0.50),
        ("stockanalysis.com",      3, "trader",        0.50),
        ("zerohedge.com",          3, "trader",        0.35),  # high volume, strong bias
        ("wolfstreet.com",         3, "trader",        0.52),
        ("calculatedriskblog.com", 3, "trader",        0.55),
        ("ritholtz.com",           3, "trader",        0.55),
        ("thereformedbroker.com",  3, "trader",        0.50),
        ("realclearmarkets.com",   3, "trader",        0.50),
        ("valuewalk.com",          3, "trader",        0.42),
        ("streetinsider.com",      3, "trader",        0.50),
        ("financialsamurai.com",   3, "trader",        0.35),
        ("bankrate.com",           3, "business",      0.45),
        ("nerdwallet.com",         3, "business",      0.40),
        ("investopedia.com",       3, "business",      0.50),
        ("thebalance.com",         3, "business",      0.42),
        ("247wallst.com",          3, "trader",        0.35),
        ("insidermonkey.com",      3, "trader",        0.38),
        ("smartmoney.com",         3, "trader",        0.35),
        ("etftrends.com",          3, "trader",        0.48),
        ("etf.com",                3, "trader",        0.55),

        # ---------- TECH / SECTOR TRADE PRESS (sector signal) ----------
        ("techcrunch.com",         2, "business",      0.68),
        ("theverge.com",           2, "business",      0.62),
        ("arstechnica.com",        2, "business",      0.62),
        ("wired.com",              2, "business",      0.60),
        ("theinformation.com",     2, "business",      0.85),  # strong tech scoops
        ("protocol.com",           3, "business",      0.55),
        ("engadget.com",           3, "business",      0.50),
        ("zdnet.com",              3, "business",      0.52),
        ("venturebeat.com",        3, "business",      0.52),
        ("cnet.com",               3, "business",      0.45),
        ("tomshardware.com",       3, "business",      0.50),
        ("anandtech.com",          3, "business",      0.55),
        ("eetimes.com",            2, "business",      0.65),  # semiconductors
        ("semiengineering.com",    2, "business",      0.66),
        ("digitimes.com",          2, "international",  0.68),  # Asia supply chain
        ("lightreading.com",       3, "business",      0.55),
        ("fiercepharma.com",       2, "business",      0.66),  # pharma
        ("fiercebiotech.com",      2, "business",      0.66),
        ("statnews.com",           2, "business",      0.72),  # health/biotech
        ("endpts.com",             2, "business",      0.70),  # Endpoints News, biotech
        ("biopharmadive.com",      3, "business",      0.58),
        ("medcitynews.com",        3, "business",      0.52),
        ("oilprice.com",           3, "business",      0.55),  # energy/commodities
        ("rigzone.com",            3, "business",      0.55),
        ("spglobal.com",           2, "business",      0.80),  # S&P Global / Platts
        ("argusmedia.com",         2, "business",      0.72),
        ("hellenicshippingnews.com",3,"business",      0.48),
        ("mining.com",             3, "business",      0.55),
        ("kitco.com",              3, "business",      0.50),  # precious metals
        ("agweb.com",              3, "business",      0.48),  # ag commodities
        ("autonews.com",           2, "business",      0.66),  # autos
        ("retaildive.com",         3, "business",      0.55),
        ("supplychaindive.com",    3, "business",      0.55),
        ("constructiondive.com",   3, "business",      0.52),
        ("bankingdive.com",        3, "business",      0.58),
        ("americanbanker.com",     2, "business",      0.70),
        ("housingwire.com",        3, "business",      0.55),
        ("globest.com",            3, "business",      0.52),  # commercial real estate
        ("therealdeal.com",        3, "business",      0.52),
        ("adweek.com",             3, "business",      0.48),
        ("variety.com",            3, "business",      0.52),  # media/entertainment
        ("hollywoodreporter.com",  3, "business",      0.50),
        ("deadline.com",           3, "business",      0.48),
        ("travelweekly.com",       3, "business",      0.45),
        ("aviationweek.com",       2, "business",      0.64),  # aerospace/defense
        ("defensenews.com",        2, "business",      0.64),
        ("spacenews.com",          2, "business",      0.62),
        ("maritime-executive.com", 3, "business",      0.50),
        ("freightwaves.com",       2, "business",      0.62),  # logistics
        ("joc.com",                3, "business",      0.55),
        ("utilitydive.com",        3, "business",      0.55),
        ("greentechmedia.com",     3, "business",      0.52),
        ("pv-magazine.com",        3, "business",      0.52),

        # ---------- CRYPTO (sector-native; noisy, weight moderately) ----------
        ("coindesk.com",           3, "business",      0.58),
        ("cointelegraph.com",      3, "business",      0.45),
        ("theblock.co",            2, "business",      0.62),
        ("decrypt.co",             3, "business",      0.50),
        ("blockworks.co",          3, "business",      0.52),

        # ---------- PRESS RELEASE WIRES (tag press_release; fact-reliable, company-originated) ----------
        ("businesswire.com",       2, "press_release", 0.20),
        ("prnewswire.com",         2, "press_release", 0.20),
        ("globenewswire.com",      2, "press_release", 0.20),
        ("accesswire.com",         3, "press_release", 0.15),
        ("newsfilecorp.com",       3, "press_release", 0.15),
        ("prweb.com",              3, "press_release", 0.10),
        ("einnews.com",            3, "press_release", 0.10),
        ("sec.gov",                1, "press_release", 0.30),  # primary filings; high fact value

        # ---------- AGGREGATORS / SYNDICATORS (dedupe risk; down-weight) ----------
        ("msn.com",                3, "aggregator",    0.30),
        ("news.google.com",        3, "aggregator",    0.25),
        ("flipboard.com",          3, "aggregator",    0.20),
        ("smartbrief.com",         3, "aggregator",    0.30),
        ("realclearpolitics.com",  3, "aggregator",    0.35),

        # ---------- SOCIAL / COMMUNITY (sentiment-native, separate handling) ----------
        ("stocktwits.com",         3, "social",        0.45),
        ("reddit.com",             3, "social",        0.40),
        ("seekingalpha.com",       3, "social",        0.45),  # crowd side
        ("substack.com",           3, "social",        0.35),  # varies wildly by author
        ("medium.com",             3, "social",        0.25),
    ]


def normalize_domain(domain):
    """Normalize a raw domain (e.g. GDELT SourceCommonName) for matching:
    strip surrounding whitespace, lowercase, and drop a leading mobile/AMP
    prefix such as 'www.' or 'm.'."""
    normalized = domain.strip().lower()
    for prefix in _STRIP_PREFIXES:
        if normalized.startswith(prefix):
            return normalized[len(prefix):]
    return normalized


@lru_cache(maxsize=1)
def weight_lookup():
    """Build (once, then cache) a `normalized_domain -> {tier, source_type,
    weight}` lookup from `source_weights()`.

    NOTE: a few domains appear twice intentionally (e.g. seekingalpha as trader
    AND social) — last-write-wins here; split into separate keys if you need
    both."""
    lookup = {}
    for domain, tier, source_type, weight in source_weights():
        lookup[normalize_domain(domain)] = {
            "tier": tier,
            "source_type": source_type,
            "weight": weight,
        }
    return lookup


def get_source_weight(domain, default_weight=0.15, default_type="unknown"):
    """Look up a source's weighting by domain.

    Unknown domains get a low-but-nonzero default so they still contribute a
    little (ingest-broad / weight-downstream), rather than being silently
    dropped."""
    info = weight_lookup().get(normalize_domain(domain))
    if info is not None:
        return info
    return {"tier": 4, "source_type": default_type, "weight": default_weight}
