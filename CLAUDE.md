# Omugongo — project guide for Claude Code

**What it is:** a personal, mostly-free opportunity-intelligence agent for Lamek
Indongo (final-year BSc Mechanical Engineering, University of Namibia). It sweeps
the Namibian job market + scholarships, graduate/trainee programmes, internships,
essay/innovation competitions, webinars, calls for presenters, short courses and
online events — with extra weight on **oil & gas / energy / green hydrogen**. It
scores each find against the user's uploaded CV using a **"realistic optimist"**
philosophy, stores results in SQLite, surfaces them in a Streamlit dashboard, and
pushes a morning digest to Telegram / WhatsApp / Email.

## Core philosophy (do not dilute)
"Realistic optimist" — see `omugongo/prompts.py`:
- Entry-level (intern/attachment/graduate/trainee) = **competency hire**; a final-year
  Mechanical Engineering background is treated as proof of analytical ability.
- **Bridge adjacent fields** (data, ops, supply chain, project controls, QA, HSE,
  sales/field eng, analyst) instead of rejecting them.
- Cast a **wide net** beyond jobs; honest about gaps but encouraging.
- Stay disciplined: don't recommend genuinely senior/irrelevant roles.

## Architecture
```
config.py            paths, secrets (via .env), DEFAULT_SETTINGS, SOURCES, email maps
app.py               Streamlit dashboard (New/Watchlist/Deadlines/Leads/Assistant/Settings)
run_sweep.py         headless morning entrypoint (Task Scheduler runs this)
setup_scheduler.ps1  registers the 7AM Windows scheduled task
omugongo/
  db.py        SQLite: opportunities, settings(KV/JSON), leads. ALL db access here.
  cv.py        PDF -> text (pypdf); cached in settings["cv_text"]
  prompts.py   realistic-optimist persona + JSON eval instructions
  llm.py       provider-agnostic REST client: gemini (default) | anthropic; keyword fallback
  search.py    free web search (DuckDuckGo html; Brave if key) incl. public LinkedIn dorks
  scraper.py   requests/BS4 + RSS; optional Playwright (js=True sources only)
  sources.py   gather_candidates(): registered sources + search queries -> deduped list
  leads.py     executive finder: public search + email-pattern guesses
  notify.py    Telegram + WhatsApp(CallMeBot) + Email; compose_digest()
  pipeline.py  run_sweep(): gather -> dedupe -> enrich -> evaluate -> store -> notify
```

## Conventions / gotchas
- **Python 3.14** on Windows. Console is cp1252 — scripts call
  `sys.stdout.reconfigure(encoding="utf-8")`; always pass `encoding="utf-8"` on file I/O.
- **Secrets** live only in `.env` (gitignored). Non-secret tunables live in the
  `settings` table, seeded from `DEFAULT_SETTINGS`, editable in the Settings tab.
- **No LLM SDKs** — we call Gemini/Anthropic REST with `requests` to avoid version
  churn on a new Python. Model IDs: Gemini `gemini-2.5-flash`; Claude Haiku
  `claude-haiku-4-5-20251001`, Sonnet `claude-sonnet-4-6`.
- **Free by default:** no API key => `llm.evaluate` uses a keyword heuristic so the
  app still works. Gemini free tier has RPM/daily caps — hence per-run caps and
  `eval_delay` in the pipeline.
- **LinkedIn:** never log in or scrape directly. Only public results via search.
- **Lead emails are guesses** for legitimate 1:1 outreach, not bulk mail.
- The DB path, CV and logs live under `data/` (gitignored).

## Run
```
pip install -r requirements.txt
copy .env.example .env             # then fill in keys
python -m streamlit run app.py     # dashboard
python run_sweep.py                # one manual sweep
powershell -ExecutionPolicy Bypass -File .\setup_scheduler.ps1   # 7AM daily
```
Optional JS scraping: `pip install playwright && playwright install chromium`.
