"""
Omugongo — central configuration.

Two kinds of config live in this project:
  * Secrets  -> .env file (API keys, tokens). Loaded via python-dotenv.
  * Tunables -> DEFAULT_SETTINGS below, seeded into the SQLite `settings`
                table on first run and editable live from the Settings tab.

Static, code-level data (the source registry, industry targets, the geography
and engineering vocabularies that power the relevance sieve, email patterns)
stays here.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CV_DIR = DATA_DIR / "cv"
DB_PATH = DATA_DIR / "omugongo.db"
LOG_PATH = DATA_DIR / "sweep.log"
CV_PDF_PATH = CV_DIR / "current_cv.pdf"

for _d in (DATA_DIR, CV_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Load .env (no-op if the file is missing)
load_dotenv(BASE_DIR / ".env")

APP_NAME = "Omugongo"
APP_TAGLINE = "The gathering tree for Namibian engineering opportunities"

# ── Secrets (read from environment / .env) ───────────────────────────────────
def env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()

GEMINI_API_KEY = env("GEMINI_API_KEY")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
BRAVE_API_KEY = env("BRAVE_API_KEY")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")

CALLMEBOT_PHONE = env("CALLMEBOT_PHONE")
CALLMEBOT_APIKEY = env("CALLMEBOT_APIKEY")

EMAIL_ADDRESS = env("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = env("EMAIL_APP_PASSWORD")
EMAIL_TO = env("EMAIL_TO") or EMAIL_ADDRESS


# ── Industry targets ─────────────────────────────────────────────────────────
# The companies/organisations most relevant to Lamek's oil & gas / energy /
# green-hydrogen focus in Namibia. Each entry feeds THREE engines:
#   1. opportunity dorks  (careers-page + "Namibia vacancy" search queries)
#   2. public Facebook / LinkedIn dorks (site:facebook.com / site:linkedin.com)
#   3. the lead finder (domain for email guesses; people search)
# `careers` is a direct careers URL when one is reliably scrapeable.
# We NEVER log into or scrape Facebook/LinkedIn directly — only public search.
INDUSTRY_TARGETS: list[dict] = [
    # ---- Operators / explorers in the Namibian basins ----
    {"name": "TotalEnergies", "domain": "totalenergies.com", "sector": "oil & gas",
     "fb": "TotalEnergies", "linkedin": "totalenergies"},
    {"name": "Shell", "domain": "shell.com", "sector": "oil & gas",
     "fb": "Shell", "linkedin": "shell"},
    {"name": "Galp", "domain": "galp.com", "sector": "oil & gas",
     "fb": "GalpEnergia", "linkedin": "galp"},
    {"name": "BW Energy", "domain": "bwenergy.no", "sector": "oil & gas",
     "fb": "BWEnergy", "linkedin": "bw-energy"},
    {"name": "Rhino Resources", "domain": "rhinoresources.com", "sector": "oil & gas",
     "fb": "", "linkedin": "rhino-resources-ltd"},
    {"name": "ReconAfrica", "domain": "reconafrica.com", "sector": "oil & gas",
     "fb": "ReconAfrica", "linkedin": "reconnaissance-energy-africa-ltd"},
    {"name": "Chevron", "domain": "chevron.com", "sector": "oil & gas",
     "fb": "chevron", "linkedin": "chevron"},
    {"name": "Woodside Energy", "domain": "woodside.com", "sector": "oil & gas",
     "fb": "WoodsideEnergyGroup", "linkedin": "woodside"},
    {"name": "QatarEnergy", "domain": "qatarenergy.qa", "sector": "oil & gas",
     "fb": "", "linkedin": "qatarenergy"},
    {"name": "NAMCOR", "domain": "namcor.com.na", "sector": "oil & gas",
     "fb": "namcor.namibia", "linkedin": "namcor"},

    # ---- FPSO / offshore services / shipyards ----
    {"name": "Yinson", "domain": "yinson.com", "sector": "oil & gas",
     "fb": "yinsonproduction", "linkedin": "yinson"},
    {"name": "SBM Offshore", "domain": "sbmoffshore.com", "sector": "oil & gas",
     "fb": "SBMOffshore", "linkedin": "sbm-offshore"},
    {"name": "SLB", "domain": "slb.com", "sector": "oil & gas",
     "fb": "SLB", "linkedin": "slb"},
    {"name": "Halliburton", "domain": "halliburton.com", "sector": "oil & gas",
     "fb": "Halliburton", "linkedin": "halliburton"},
    {"name": "Baker Hughes", "domain": "bakerhughes.com", "sector": "oil & gas",
     "fb": "bakerhughesco", "linkedin": "baker-hughes"},
    {"name": "EBH Namibia", "domain": "ebhnamibia.com", "sector": "marine/oil & gas",
     "fb": "EBHNamibia", "linkedin": "ebh-namibia"},

    # ---- Green hydrogen / new energy (Namibia flagship sector) ----
    {"name": "Hyphen Hydrogen Energy", "domain": "hyphenafrica.com", "sector": "green hydrogen",
     "fb": "", "linkedin": "hyphen-hydrogen-energy"},
    {"name": "HDF Energy", "domain": "hdf-energy.com", "sector": "green hydrogen",
     "fb": "HDFEnergy", "linkedin": "hdf-energy"},
    {"name": "Cleanergy Solutions Namibia", "domain": "cleanergynamibia.com", "sector": "green hydrogen",
     "fb": "", "linkedin": "cleanergy-solutions-namibia"},
    {"name": "Daures Green Hydrogen Village", "domain": "dauresghv.com", "sector": "green hydrogen",
     "fb": "", "linkedin": "daures-green-hydrogen-consortium"},

    # ---- Power / utilities / renewables ----
    {"name": "NamPower", "domain": "nampower.com.na", "sector": "power",
     "fb": "NamPower", "linkedin": "nampower",
     "careers": "https://www.nampower.com.na/Careers.aspx"},
    {"name": "Debmarine Namibia", "domain": "debmarinenamibia.com", "sector": "marine mining",
     "fb": "DebmarineNamibia", "linkedin": "debmarine-namibia"},
    {"name": "Namdeb", "domain": "namdeb.com", "sector": "mining",
     "fb": "NamdebDiamond", "linkedin": "namdeb"},
    {"name": "Orano Mining Namibia", "domain": "orano.group", "sector": "uranium/energy",
     "fb": "", "linkedin": "orano"},
    {"name": "Swakop Uranium", "domain": "swakopuranium.com.na", "sector": "uranium/energy",
     "fb": "SwakopUranium", "linkedin": "swakop-uranium"},
    {"name": "Rössing Uranium", "domain": "rossing.com", "sector": "uranium/energy",
     "fb": "RossingUranium", "linkedin": "rossing-uranium-limited"},

    # ---- Industrial / engineering employers worth tracking ----
    {"name": "Puma Energy", "domain": "pumaenergy.com", "sector": "energy/downstream",
     "fb": "PumaEnergy", "linkedin": "puma-energy",
     "careers": "https://pumaenergy.com/careers/"},
    {"name": "Ohlthaver & List", "domain": "ol.na", "sector": "industrial group",
     "fb": "OhlthaverList", "linkedin": "ohlthaver-&-list-group"},
    {"name": "Namibia Breweries", "domain": "nambrew.com", "sector": "manufacturing",
     "fb": "NamibiaBreweries", "linkedin": "namibia-breweries-limited"},
]

# ── Source registry (RSS + sites). The sieve + AI filter everything. ──────────
# type: "rss" | "html" | "search_site"
#   rss          -> parsed with feedparser (clean, structured)
#   html         -> fetched + posting links extracted (set "js": True for Playwright)
SOURCES: list[dict] = [
    # ---- Namibian job boards (broad) ----
    {"name": "Jobs Namibia", "url": "https://www.jobsnamibia.net/", "type": "html",
     "category_hint": "Job"},
    {"name": "Careerjet Namibia", "url": "https://www.careerjet.com.na/jobs?s=graduate+engineering&l=",
     "type": "html", "category_hint": "Job"},
    {"name": "Careerjet Namibia (energy)", "url": "https://www.careerjet.com.na/jobs?s=oil+gas+energy&l=",
     "type": "html", "category_hint": "Job"},
    {"name": "MyJobo Namibia", "url": "https://www.myjobo.com/jobs-in-namibia", "type": "html",
     "category_hint": "Job"},
    {"name": "Jobseekers Namibia", "url": "https://www.jobseekersnamibia.com/", "type": "html",
     "category_hint": "Job"},
    {"name": "Namibia Internships", "url": "https://www.namibiainternships.com/", "type": "html",
     "category_hint": "Internship"},
    {"name": "Hot Jobs Namibia", "url": "https://hotjobsnamibia.com/", "type": "html",
     "category_hint": "Job"},

    # ---- Corporate / oil & gas / utilities (often JS — dorks cover them too) ----
    {"name": "Puma Energy", "url": "https://pumaenergy.com/careers/", "type": "html",
     "category_hint": "Job", "js": True},
    {"name": "NamPower", "url": "https://www.nampower.com.na/Careers.aspx", "type": "html",
     "category_hint": "Job"},
    {"name": "Namcor", "url": "https://www.namcor.com.na/vacancies", "type": "html",
     "category_hint": "Job"},
    {"name": "Debmarine / Namdeb", "url": "https://www.debmarinenamibia.com/careers", "type": "html",
     "category_hint": "Job"},

    # ---- Scholarship / opportunity aggregators (RSS) ----
    {"name": "Opportunity Desk", "url": "https://opportunitydesk.org/feed/", "type": "rss",
     "category_hint": "Scholarship"},
    {"name": "Opportunities For Africans", "url": "https://www.opportunitiesforafricans.com/feed/",
     "type": "rss", "category_hint": "Scholarship"},
    {"name": "After School Africa", "url": "https://www.afterschoolafrica.com/feed/", "type": "rss",
     "category_hint": "Scholarship"},
    {"name": "Youth Opportunities", "url": "https://www.youthop.com/feed", "type": "rss",
     "category_hint": "Opportunity"},
    {"name": "OYA Opportunities", "url": "https://oyaop.com/feed/", "type": "rss",
     "category_hint": "Opportunity"},

    # ---- Namibian funding / official ----
    {"name": "NSFAF", "url": "https://www.nsfaf.na/", "type": "html",
     "category_hint": "Bursary"},
]

# ── Industry NEWS sources (the "what is the industry saying" feed) ────────────
# Surfaced under category "News" with a sector-relevance bar (not personal fit).
NEWS_SOURCES: list[dict] = [
    {"name": "Energy Capital & Power", "url": "https://energycapitalpower.com/feed/", "type": "rss"},
    {"name": "OilPrice", "url": "https://oilprice.com/rss/main", "type": "rss"},
    {"name": "Rigzone", "url": "https://www.rigzone.com/news/rss/rigzone_latest.aspx", "type": "rss"},
    {"name": "Offshore Energy", "url": "https://www.offshore-energy.biz/feed/", "type": "rss"},
    {"name": "ESI Africa", "url": "https://www.esi-africa.com/feed/", "type": "rss"},
    {"name": "Namibia Economist", "url": "https://economist.com.na/feed/", "type": "rss"},
    {"name": "The Namibian", "url": "https://www.namibian.com.na/feed/", "type": "rss"},
    {"name": "Hydrogen Insight", "url": "https://www.hydrogeninsight.com/rss", "type": "rss"},
]

# Search queries that keep the news feed fresh even when an RSS feed is dead.
NEWS_SEARCH_QUERIES: list[str] = [
    "Namibia oil and gas news latest",
    "Namibia Orange Basin offshore discovery news",
    "Namibia green hydrogen project news latest",
    "NAMCOR OR TotalEnergies OR Galp OR Shell Namibia news",
    "Namibia energy sector jobs hiring news",
]

# ── Relevance-sieve vocabularies ─────────────────────────────────────────────
# Geography: keep anything that signals Namibia / Southern Africa OR is global by
# nature (remote/online study, scholarships). Used by omugongo/relevance.py.
LOCAL_TERMS: list[str] = [
    "namibia", "namibian", "windhoek", "walvis bay", "swakopmund", "oranjemund",
    "luderitz", "lüderitz", "otjiwarongo", "ongwediva", "oshakati", "rundu",
    "katima", "henties", "tsumeb", "rosh pinah", "namib", "erongo", "khomas",
    "southern africa", "sadc", "unam", "nust namibia",
]
# Signals that an item is global / location-agnostic, so geography never blocks it.
GLOBAL_OK_TERMS: list[str] = [
    "remote", "online", "virtual", "anywhere", "worldwide", "global",
    "fully funded", "fully-funded", "scholarship", "bursary", "fellowship",
    "grant", "webinar", "mooc", "e-learning", "distance learning", "work from home",
    "pan-african", "africa-wide", "open to all", "international students",
]
# Country/city terms that, when present WITHOUT a local or global signal, mark an
# item as "elsewhere" for job-type categories (so Lagos/Nairobi roles drop out).
FOREIGN_HINT_TERMS: list[str] = [
    "nigeria", "lagos", "abuja", "port harcourt", "kenya", "nairobi", "ghana",
    "accra", "tanzania", "uganda", "kampala", "ethiopia", "egypt", "cairo",
    "india", "pakistan", "bangladesh", "philippines", "indonesia", "vietnam",
    "dubai", "abu dhabi", "qatar", "doha", "saudi", "riyadh", "oman", "kuwait",
    "netherlands", "amsterdam", "united kingdom", "london", "united states",
    "houston", "canada", "australia", "perth", "malaysia", "kuala lumpur",
    "relocate to", "must be based in", "eligible to work in",
]

# Engineering / sector vocabulary — the "engineering only" sieve for job-type items.
ENGINEERING_TERMS: list[str] = [
    "engineer", "engineering", "mechanical", "electrical", "mechatronic",
    "industrial", "civil", "chemical", "process", "design", "cad", "solidworks",
    "autocad", "inventor", "draught", "draft", "maintenance", "reliability",
    "rotating equipment", "static equipment", "piping", "hvac", "pump",
    "fabrication", "welding", "machining", "manufacturing", "production",
    "plant", "commissioning", "inspection", "ndt", "qa/qc", "quality",
    "hse", "safety", "technician", "artisan", "fitter", "millwright",
    "instrumentation", "automation", "controls", "project controls",
    "drilling", "subsea", "offshore", "fpso", "well", "completion",
    "operations", "supply chain", "logistics", "procurement", "planning",
    "data", "analyst", "graduate engineer", "trainee engineer",
]
SECTOR_TERMS: list[str] = [
    "oil", "gas", "petroleum", "upstream", "downstream", "midstream", "offshore",
    "onshore", "fpso", "drilling", "rig", "refinery", "lng", "energy", "power",
    "electricity", "renewable", "solar", "wind", "hydrogen", "ammonia",
    "green hydrogen", "mining", "uranium", "diamond", "water", "utility",
    "utilities", "decarbonisation", "decarbonization", "net zero", "exploration",
]
# Opportunity types that are valuable regardless of pure-engineering wording.
OPPORTUNITY_TYPE_TERMS: list[str] = [
    "scholarship", "bursary", "fellowship", "grant", "competition", "hackathon",
    "essay", "challenge", "innovation", "award", "webinar", "course",
    "certificate", "certification", "conference", "summit", "workshop",
    "call for", "fully funded", "internship", "graduate programme",
    "graduate program", "trainee", "attachment", "learnership", "apprenticeship",
]

# ── Tunable defaults (seeded into DB, editable in the UI) ─────────────────────
DEFAULT_SETTINGS: dict = {
    # AI brain. "gemini" (free) or "anthropic" (paid, cheap). One-line switch.
    "provider": "gemini",
    "gemini_model": "gemini-2.5-flash",          # free-tier eligible
    "anthropic_model_eval": "claude-haiku-4-5-20251001",   # cheap bulk matching
    "anthropic_model_chat": "claude-sonnet-4-6",           # assistant chat

    # Realistic-optimist threshold. Items scoring >= this are surfaced/notified.
    "fit_threshold": 55,

    # Per-run caps — bigger than before for a genuinely DEEP sweep, still free-tier
    # safe because the sieve culls junk BEFORE we spend AI evals, and the matcher
    # degrades to a keyword heuristic if the free tier rate-limits.
    "max_candidates_per_run": 220,
    "max_evals_per_run": 120,
    "max_results_per_query": 12,
    "eval_delay": 1.2,              # seconds between AI evals (protects RPM caps)
    "fetch_page_text": True,        # fetch the real posting page before scoring

    # Relevance sieve (pre-AI culling so depth doesn't mean noise).
    "sieve_geo": True,              # drop clearly-foreign job-type items
    "sieve_engineering": True,      # require engineering/sector OR opportunity-type

    # Industry news feed.
    "news_enabled": True,
    "news_max_per_run": 30,

    # Auto lead + outreach collection for top oil & gas / energy matches.
    "auto_leads": True,
    "leads_per_run": 6,

    # Notification channels to use for the morning digest.
    "channel_telegram": True,
    "channel_whatsapp": True,
    "channel_email": True,
    "digest_max_items": 14,
    "digest_news_items": 5,

    # Geography focus (used to bias matching, not to hard-filter).
    "locations": "Namibia, Windhoek, Walvis Bay, Swakopmund, Remote, Southern Africa",

    # Wide-net base queries. The pipeline ALSO generates many more dynamically
    # from your CV profile + the industry targets above (see omugongo/search.py).
    "search_queries": [],          # filled from DEFAULT_SEARCH_QUERIES on seed
}

# ── Wide-net base search queries. Cast broad — the sieve + AI filter. ─────────
DEFAULT_SEARCH_QUERIES: list[str] = [
    # Jobs / graduate / internship / attachment
    "Namibia graduate trainee programme 2026 apply",
    "Namibia internship 2026 engineering apply",
    "Namibia mechanical engineering vacancy 2026",
    "Namibia industrial attachment student engineering 2026",
    '"graduate programme" Namibia 2026 application engineering',
    "entry level engineering jobs Namibia 2026",
    "Namibia learnership OR apprenticeship engineering 2026",
    # Oil, gas & energy (Lamek's focus sector)
    "Namibia oil and gas internship OR graduate 2026",
    "Namibia offshore oil gas vacancy 2026",
    "green hydrogen Namibia internship OR graduate OR trainee 2026",
    "Namibia energy sector graduate programme 2026 apply",
    # Public LinkedIn / Facebook (via search, never login)
    "site:linkedin.com/jobs Namibia graduate OR intern engineering",
    'site:na.linkedin.com Namibia "graduate programme" 2026',
    "site:facebook.com Namibia engineering vacancy OR internship 2026",
    # Scholarships / bursaries
    "scholarship Namibian students 2026 engineering OR energy fully funded",
    "bursary Namibia engineering 2026 apply",
    "fully funded masters scholarship Namibia OR Africa engineering 2026",
    # Competitions / essays / innovation (e.g. AAKRUTI SolidWorks tournament)
    "engineering student competition Africa 2026 apply",
    "SolidWorks design competition OR tournament students 2026",
    "AAKRUTI design tournament 2026",
    "student innovation OR hackathon Africa engineering 2026 apply",
    "call for proposals green hydrogen OR energy Namibia 2026",
    # Webinars / courses / calls for presenters
    "oil and gas webinar 2026 call for presenters",
    "free online course oil and gas OR renewable energy 2026 certificate",
    "SPE student paper contest OR webinar 2026",
]

# ── Executive lead finder: corporate email patterns ──────────────────────────
# Known/likely domain formats for cold-outreach guesses (verify before sending).
# Auto-extended from INDUSTRY_TARGETS below.
EMAIL_DOMAIN_MAP: dict[str, str] = {
    "telecom namibia": "telecom.na",
    "mtc": "mtc.com.na",
    "bank windhoek": "bankwindhoek.com.na",
    "fnb namibia": "fnbnamibia.com.na",
    "standard bank": "standardbank.com.na",
    "nedbank": "nedbank.com.na",
    "pupkewitz": "pupkewitz.com",
    "petrofund": "petrofund.com.na",
}
# Fold every industry target's domain into the email map automatically.
for _t in INDUSTRY_TARGETS:
    EMAIL_DOMAIN_MAP.setdefault(_t["name"].lower(), _t["domain"])

# Patterns are .format()-ed with first, last, f (first initial), l (last initial).
EMAIL_PATTERNS: list[str] = [
    "{first}.{last}@{domain}",
    "{f}{last}@{domain}",
    "{first}@{domain}",
    "{first}{last}@{domain}",
    "{first}_{last}@{domain}",
    "{last}{f}@{domain}",
    "{f}.{last}@{domain}",
]

# Generic inbox fallbacks worth trying when a person can't be pinned down.
GENERIC_INBOXES = ["careers", "info", "hr", "recruitment", "jobs"]

# Seed fresh installs with the base query set (runtime unions these with the
# CV-profile + industry dorks generated in omugongo/search.py).
DEFAULT_SETTINGS["search_queries"] = DEFAULT_SEARCH_QUERIES
