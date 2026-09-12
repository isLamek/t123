# 🌳 Omugongo

*The gathering tree for Namibian engineering opportunities.*

Omugongo reads your CV and quietly sweeps the net every morning for things you can
actually go after — **jobs, internships, industrial attachments, graduate & trainee
programmes, scholarships, bursaries, essay & innovation competitions, webinars, calls
for presenters, short courses and online events** — with a heavy tilt toward
**oil & gas, energy and green hydrogen** (Namibia's growth sector).

Every find is scored against your CV by an AI that thinks like a **realistic optimist**:
if a role is entry-level, your Mechanical Engineering degree is treated as proof of
competence — even for adjacent fields like data, operations or project controls. The
good ones land in your dashboard and a morning digest on **Telegram / WhatsApp / Email**.

It also includes a **lead finder** (find a likely country-manager + email pattern for a
cold email) and a **CV-aware AI assistant** for drafting outreach and cover letters.

---

## Quick start (Windows)

### 1. Install dependencies
```powershell
pip install -r requirements.txt
```

### 2. Add your keys
Copy the template and open it in a text editor:
```powershell
copy .env.example .env
notepad .env
```
You can leave everything blank and the app still runs (keyword matching, no alerts).
To unlock the full experience, fill in what you want:

| Setting | What it's for | How to get it (free) |
|---|---|---|
| `GEMINI_API_KEY` | The AI brain (free tier) | https://aistudio.google.com/app/apikey |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Telegram alerts | Message `@BotFather` → `/newbot`; chat id via `getUpdates` |
| `CALLMEBOT_PHONE` / `CALLMEBOT_APIKEY` | WhatsApp alerts | https://www.callmebot.com/blog/free-api-whatsapp-messages/ |
| `EMAIL_ADDRESS` / `EMAIL_APP_PASSWORD` | Email digest | Gmail App Password: https://myaccount.google.com/apppasswords |
| `ANTHROPIC_API_KEY` | *Optional* — use Claude instead of Gemini (paid) | https://console.anthropic.com/ |

> After editing `.env`, restart the app so it picks up the new values.

### 3. Launch the dashboard
```powershell
python -m streamlit run app.py
```
*(`python -m streamlit` always works even if the `streamlit` command isn't on your PATH.)*
Your CV is already loaded. Re-upload anytime from the sidebar to keep it current.
Hit **🔄 Run sweep now** to try a sweep on demand.

### 4. Schedule the 7 AM morning sweep
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_scheduler.ps1
```
This registers a Windows Task that runs `run_sweep.py` quietly every morning and
sends your digest. Test it immediately with:
```powershell
Start-ScheduledTask -TaskName "Omugongo_Morning_Sweep"
Get-Content .\data\sweep.log -Tail 30
```

### 5. (Optional) JavaScript-heavy career pages
Some corporate sites need a real browser. Only if you want them:
```powershell
pip install playwright
playwright install chromium
```

---

## How it works
1. **Gather** — registered Namibian sources (job boards, NamPower, Namcor, scholarship
   feeds…) + a wide net of web searches incl. *public* LinkedIn results.
2. **Dedupe** — a stable id per link; you never see the same thing twice.
3. **Evaluate** — each new item is scored 0-100 against your CV with the realistic-optimist
   prompt, which also writes a short background + "why apply" + any closing date.
4. **Store** — everything goes to SQLite (`data/omugongo.db`).
5. **Notify** — new matches at/above your fit threshold (default 55%) get pushed to your
   chosen channels, along with reminders for anything closing within 7 days.

Tune the threshold, search queries, geographic focus and channels in the **⚙️ Settings** tab.

## Cost
**Free by default.** Gemini's free tier comfortably covers a daily sweep and chat;
DuckDuckGo search and the notifiers are free. Switch to Claude in Settings only if you
want top quality (a few US$/month at this volume).

## Notes & etiquette
- Omugongo never logs into or scrapes LinkedIn directly — only public search results.
- Lead-finder emails are *educated guesses* for genuine, one-to-one outreach. Verify
  before sending; don't bulk-mail.
- Your CV, database and logs stay on your machine (the `data/` folder, gitignored).

Built with Claude Code. See `CLAUDE.md` for the developer guide.
