"""
Omugongo — Streamlit dashboard.

Run with:   streamlit run app.py
"""
from __future__ import annotations

from datetime import date

import streamlit as st

import config
from omugongo import cv, db, leads, llm, notify, pipeline

st.set_page_config(page_title="Omugongo", page_icon="🌳", layout="wide")
db.init_db()


# ── helpers ──────────────────────────────────────────────────────────────────
def days_left(closing: str | None) -> int | None:
    if not closing:
        return None
    try:
        return (date.fromisoformat(closing[:10]) - date.today()).days
    except (ValueError, TypeError):
        return None


def score_badge(score: int) -> str:
    dot = "🟢" if score >= 70 else "🟡" if score >= 50 else "⚪"
    return f"{dot} {score}%"


def render_opportunity(row: dict, context: str) -> None:
    """One opportunity as an expander with actions. `context` keeps keys unique."""
    dl = days_left(row.get("closing_date"))
    dl_txt = ""
    if dl is not None:
        dl_txt = f" · ⏰ {dl}d left" if dl >= 0 else " · ⌛ closed"
    header = f"{score_badge(row.get('fit_score', 0))} · {row.get('title', '(untitled)')[:90]}"
    with st.expander(header):
        st.caption(
            f"**{row.get('category', 'Other')}** · {row.get('source', '')}"
            + (f" · 📅 {row['closing_date']}{dl_txt}" if row.get("closing_date") else "")
        )
        if row.get("summary"):
            st.markdown(f"**Background:** {row['summary']}")
        if row.get("justification"):
            st.markdown(f"**Why apply (realistic optimist):** {row['justification']}")
        if row.get("url"):
            st.markdown(f"🔗 [Open original posting]({row['url']})")

        cols = st.columns(5)
        rid = row["id"]
        if context != "flagged" and cols[0].button("⭐ Flag", key=f"flag_{context}_{rid}"):
            db.update_status(rid, "flagged"); st.rerun()
        if context == "flagged" and cols[0].button("↩️ To New", key=f"unflag_{context}_{rid}"):
            db.update_status(rid, "new"); st.rerun()
        if cols[1].button("✅ Applied", key=f"app_{context}_{rid}"):
            db.update_status(rid, "applied"); st.rerun()
        if cols[2].button("🗑️ Dismiss", key=f"dis_{context}_{rid}"):
            db.update_status(rid, "dismissed"); st.rerun()
        rem_label = "🔕 Reminder off" if row.get("reminder_set") else "🔔 Remind me"
        if cols[3].button(rem_label, key=f"rem_{context}_{rid}"):
            db.set_reminder(rid, not row.get("reminder_set")); st.rerun()

        # Manual closing-date entry when the AI didn't detect one.
        new_dl = cols[4].date_input("Set deadline", value=None, key=f"dl_{context}_{rid}",
                                    format="YYYY-MM-DD")
        if new_dl and str(new_dl) != (row.get("closing_date") or ""):
            db.set_closing_date(rid, str(new_dl)); st.rerun()


def run_sweep_ui() -> None:
    with st.status("Sweeping the net… this can take a few minutes.", expanded=True) as box:
        log_lines: list[str] = []
        ph = st.empty()

        def logger(msg: str) -> None:
            log_lines.append(str(msg))
            ph.code("\n".join(log_lines[-18:]))

        try:
            summary = pipeline.run_sweep(logger=logger)
            box.update(label=f"Done — {summary['recommended']} new match(es).", state="complete")
            st.session_state["last_summary"] = summary
        except Exception as exc:  # noqa: BLE001
            box.update(label=f"Sweep failed: {exc}", state="error")


# ── sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌳 Omugongo")
    st.caption(config.APP_TAGLINE)

    status = llm.provider_status()
    brain = "Gemini (free)" if status["provider"] == "gemini" else "Claude"
    st.markdown(f"**Brain:** {brain} {'🟢' if status['active_ready'] else '🔴 no key'}")

    st.divider()
    st.subheader("📄 Your CV")
    up = st.file_uploader("Upload / update CV (PDF)", type=["pdf"])
    if up is not None:
        text = cv.save_uploaded_cv(up.getvalue())
        if text:
            st.success(f"CV indexed ({len(text):,} chars).")
        else:
            st.error("Couldn't read text from that PDF.")
    cv_now = cv.get_cv_text()
    if cv_now:
        st.caption(f"✅ CV on file ({len(cv_now):,} chars)")
        with st.expander("Preview"):
            st.text(cv_now[:1500])
    else:
        st.warning("No CV yet — using a fallback profile.")

    st.divider()
    if st.button("🔄 Run sweep now", use_container_width=True, type="primary"):
        run_sweep_ui()

    s = db.stats()
    st.caption(
        f"📊 {s.get('total', 0)} tracked · {s.get('new', 0)} new · "
        f"{s.get('flagged', 0)} flagged · {s.get('applied', 0)} applied"
    )


# ── tabs ─────────────────────────────────────────────────────────────────────
tab_new, tab_watch, tab_dl, tab_lead, tab_chat, tab_set = st.tabs(
    ["📥 New", "⭐ Watchlist", "📅 Deadlines", "🔎 Lead Finder", "💬 Assistant", "⚙️ Settings"]
)

with tab_new:
    st.subheader("Fresh opportunities")
    rows = db.get_opportunities(status="new")
    if "last_summary" in st.session_state:
        ls = st.session_state["last_summary"]
        st.info(f"Last sweep: {ls['evaluated']} evaluated · {ls['recommended']} surfaced · "
                f"notified {ls['notified']}.")
    if not rows:
        st.info("Nothing here yet. Hit **Run sweep now** in the sidebar, or wait for the 7 AM run.")
    for row in rows:
        render_opportunity(row, "new")

with tab_watch:
    st.subheader("Flagged for later")
    rows = db.get_opportunities(status="flagged")
    if not rows:
        st.info("Flag items from the New tab to keep them here.")
    for row in rows:
        render_opportunity(row, "flagged")
    st.divider()
    st.subheader("Applied")
    for row in db.get_opportunities(status="applied"):
        render_opportunity(row, "applied")

with tab_dl:
    st.subheader("Deadlines & reminders")
    rows = db.get_deadlines()
    if not rows:
        st.info("No deadlines yet. Set one on any item, or the AI fills it when detected.")
    else:
        table = []
        for r in rows:
            dl = days_left(r.get("closing_date"))
            table.append({
                "Title": r.get("title", "")[:70],
                "Closes": r.get("closing_date", ""),
                "Days left": dl if dl is not None else "",
                "Reminder": "🔔" if r.get("reminder_set") else "—",
                "Status": r.get("status", ""),
            })
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.caption("Reminder-flagged items closing within 7 days are pushed in your morning digest.")
        st.divider()
        for row in rows:
            render_opportunity(row, "deadline")

with tab_lead:
    st.subheader("🔎 Executive lead finder")
    st.caption("Find a likely contact + plausible email patterns for **genuine, "
               "one-to-one** outreach (e.g. asking about an internship). Guesses — verify before sending.")
    c1, c2, c3 = st.columns([2, 2, 2])
    company = c1.text_input("Company", value="Puma Energy")
    role = c2.text_input("Target role (optional)", value="Country Manager")
    domain = c3.text_input("Email domain (optional)", placeholder="pumaenergy.com")
    if st.button("Find contacts", type="primary"):
        with st.spinner("Searching public sources…"):
            st.session_state["lead_result"] = leads.find_and_generate(company, role, domain.strip())
    res = st.session_state.get("lead_result")
    if res:
        st.caption(f"Likely domain(s): {', '.join(res['domains']) or 'unknown'}")
        if not res["people"]:
            st.warning("No clear contacts surfaced. Try a different role or add the domain.")
        for i, p in enumerate(res["people"]):
            with st.expander(f"{p['name'] or 'Unknown name'} — {p['title'] or 'role unknown'}"):
                if p.get("snippet"):
                    st.caption(p["snippet"])
                if p.get("source_url"):
                    st.markdown(f"🔗 [Source]({p['source_url']})")
                if p["emails"]:
                    st.code("\n".join(p["emails"]))
                if p["name"] and st.button("💾 Save lead", key=f"savelead_{i}"):
                    db.add_lead(p["name"], p["title"], company, p.get("source_url", ""), p["emails"])
                    st.success("Saved.")
    saved = db.get_leads()
    if saved:
        st.divider()
        st.caption("Saved leads")
        st.dataframe(
            [{"Name": l["name"], "Title": l["title"], "Company": l["company"],
              "Emails": ", ".join(l["emails"][:3])} for l in saved],
            use_container_width=True, hide_index=True,
        )

with tab_chat:
    st.subheader("💬 Assistant")
    st.caption("CV-aware. Ask it to draft a cold email, a cover letter, tailor your CV, "
               "or judge whether to apply.")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if prompt := st.chat_input("e.g. Draft a short cold email to the Puma Energy country manager"):
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                reply = llm.chat(st.session_state.chat, cv.cv_for_matching())
            st.markdown(reply)
        st.session_state.chat.append({"role": "assistant", "content": reply})
    if st.session_state.chat and st.button("Clear chat"):
        st.session_state.chat = []
        st.rerun()

with tab_set:
    st.subheader("⚙️ Settings")
    cur = db.get_all_settings()

    st.markdown("**AI brain**")
    provider = st.radio("Provider", ["gemini", "anthropic"],
                        index=0 if cur.get("provider", "gemini") == "gemini" else 1,
                        horizontal=True,
                        help="Gemini = free tier. Anthropic = Claude (paid, cheap).")
    cstat = llm.provider_status()
    st.caption(f"Gemini key: {'✅' if cstat['gemini_key'] else '❌'} · "
               f"Anthropic key: {'✅' if cstat['anthropic_key'] else '❌'} "
               f"(set keys in the .env file, then restart)")
    colm = st.columns(2)
    gem_model = colm[0].text_input("Gemini model", value=cur.get("gemini_model", "gemini-2.5-flash"))
    ant_model = colm[1].text_input("Anthropic eval model",
                                   value=cur.get("anthropic_model_eval", "claude-haiku-4-5-20251001"))

    st.markdown("**Matching**")
    threshold = st.slider("Fit threshold (surface & notify at/above)", 0, 100,
                          int(cur.get("fit_threshold", 55)))
    locations = st.text_input("Geographic focus", value=cur.get("locations", "Namibia"))
    colc = st.columns(3)
    max_cand = colc[0].number_input("Max candidates/run", 10, 500,
                                    int(cur.get("max_candidates_per_run", 90)))
    max_eval = colc[1].number_input("Max AI evals/run", 5, 300,
                                    int(cur.get("max_evals_per_run", 60)))
    per_q = colc[2].number_input("Results per query", 3, 30,
                                 int(cur.get("max_results_per_query", 12)))

    st.markdown("**Search queries** (one per line — cast a wide net)")
    queries_text = st.text_area("queries", value="\n".join(cur.get("search_queries", [])),
                                height=200, label_visibility="collapsed")

    st.markdown("**Alerts**")
    cc = st.columns(3)
    ch_tg = cc[0].checkbox("Telegram", value=cur.get("channel_telegram", True))
    ch_wa = cc[1].checkbox("WhatsApp", value=cur.get("channel_whatsapp", True))
    ch_em = cc[2].checkbox("Email", value=cur.get("channel_email", True))

    if st.button("💾 Save settings", type="primary"):
        db.set_setting("provider", provider)
        db.set_setting("gemini_model", gem_model.strip())
        db.set_setting("anthropic_model_eval", ant_model.strip())
        db.set_setting("fit_threshold", int(threshold))
        db.set_setting("locations", locations)
        db.set_setting("max_candidates_per_run", int(max_cand))
        db.set_setting("max_evals_per_run", int(max_eval))
        db.set_setting("max_results_per_query", int(per_q))
        db.set_setting("search_queries", [q.strip() for q in queries_text.splitlines() if q.strip()])
        db.set_setting("channel_telegram", ch_tg)
        db.set_setting("channel_whatsapp", ch_wa)
        db.set_setting("channel_email", ch_em)
        st.success("Saved.")

    st.divider()
    if st.button("✉️ Send test alert to enabled channels"):
        with st.spinner("Sending…"):
            st.json(notify.test_channels())
