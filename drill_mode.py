"""
drill_mode.py — Spaced repetition drill module for the Jeopardy Trainer.
Call render_drill_mode() from the main app to embed this as a tab.

Spaced Repetition algorithm (SM-2 simplified):
  Each card has:
    - ease: float (2.5 default, min 1.3)
    - interval: int days until next review (starts at 1)
    - repetitions: int times answered correctly in a row
    - due: date string YYYY-MM-DD
  On answer:
    - rating 1 (Wrong):   reset repetitions → 0, interval → 1, ease -= 0.2
    - rating 3 (Hard):    interval stays, ease -= 0.15
    - rating 4 (Good):    interval × ease, ease unchanged
    - rating 5 (Easy):    interval × ease × 1.3, ease += 0.1
"""

import streamlit as st
import json
import re
from datetime import date, timedelta
from drill_data import DRILL_DECKS

# ─── Persistence helpers ─────────────────────────────────────────────────────

STORAGE_KEY = "drill_srs_state"

def _load_srs() -> dict:
    raw = st.session_state.get(STORAGE_KEY, "{}")
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}

def _save_srs(state: dict):
    st.session_state[STORAGE_KEY] = state

def _card_key(deck_name: str, q: str) -> str:
    return f"{deck_name}||{q}"

def _get_card_state(srs: dict, deck_name: str, q: str) -> dict:
    key = _card_key(deck_name, q)
    return srs.get(key, {
        "ease": 2.5,
        "interval": 1,
        "repetitions": 0,
        "due": str(date.today()),
        "correct": 0,
        "total": 0,
    })

def _save_card_state(srs: dict, deck_name: str, q: str, card_state: dict):
    srs[_card_key(deck_name, q)] = card_state
    _save_srs(srs)

# ─── SM-2 update ─────────────────────────────────────────────────────────────

def _apply_rating(card: dict, rating: int) -> dict:
    """rating: 1=Wrong, 3=Hard, 4=Good, 5=Easy"""
    card = card.copy()
    today = date.today()

    if rating == 1:  # Wrong
        card["repetitions"] = 0
        card["interval"]    = 1
        card["ease"]        = max(1.3, card["ease"] - 0.2)
        card["correct"]     = card.get("correct", 0)
    else:
        card["correct"] = card.get("correct", 0) + 1
        if card["repetitions"] == 0:
            card["interval"] = 1
        elif card["repetitions"] == 1:
            card["interval"] = 6
        else:
            multiplier = card["ease"]
            if rating == 3:
                card["ease"] = max(1.3, card["ease"] - 0.15)
                multiplier = 1.0
            elif rating == 5:
                card["ease"] = min(3.0, card["ease"] + 0.1)
                multiplier = card["ease"] * 1.3
            card["interval"] = max(1, round(card["interval"] * multiplier))
        card["repetitions"] += 1

    card["total"] = card.get("total", 0) + 1
    card["due"]   = str(today + timedelta(days=card["interval"]))
    return card

# ─── Queue builder ────────────────────────────────────────────────────────────

def _build_queue(deck: dict, srs: dict) -> list:
    """
    Returns cards due today or overdue, sorted by due date ascending.
    New cards (never seen) are included and sorted after overdue ones.
    """
    today_str = str(date.today())
    due, new_cards = [], []

    for card in deck["cards"]:
        q   = card["q"]
        cs  = _get_card_state(srs, deck["name"], q)
        if cs["total"] == 0:
            new_cards.append(card)
        elif cs["due"] <= today_str:
            due.append((cs["due"], card))

    due.sort(key=lambda x: x[0])
    return [c for _, c in due] + new_cards

def _deck_stats(deck: dict, srs: dict) -> dict:
    today_str = str(date.today())
    total = len(deck["cards"])
    seen, due, mastered = 0, 0, 0
    correct_sum, attempt_sum = 0, 0

    for card in deck["cards"]:
        cs = _get_card_state(srs, deck["name"], card["q"])
        if cs["total"] > 0:
            seen += 1
            attempt_sum += cs["total"]
            correct_sum += cs["correct"]
            if cs["interval"] >= 21:
                mastered += 1
            if cs["due"] <= today_str:
                due += 1

    accuracy = round(correct_sum / attempt_sum * 100) if attempt_sum else 0
    return {
        "total": total,
        "seen": seen,
        "unseen": total - seen,
        "due": due,
        "mastered": mastered,
        "accuracy": accuracy,
    }

# ─── Fuzzy grading (lightweight version) ─────────────────────────────────────

def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r'\b(a|an|the)\b', '', t)
    t = re.sub(r'[^a-z0-9\s]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def _similarity(a: str, b: str) -> int:
    a, b = list(_normalize(a)), list(_normalize(b))
    if not a or not b:
        return 0
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i-1][j-1] if a[i-1] == b[j-1] else 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    dist = dp[m][n]
    return int((max(m, n) - dist) / max(m, n) * 100)

# ─── Main render function ─────────────────────────────────────────────────────

def render_drill_mode():
    srs = _load_srs()

    # Init session state
    if "drill_screen" not in st.session_state:
        st.session_state.drill_screen   = "home"   # home | deck | card | result
        st.session_state.drill_deck_idx = None
        st.session_state.drill_queue    = []
        st.session_state.drill_card_idx = 0
        st.session_state.drill_show_ans = False
        st.session_state.drill_user_ans = ""
        st.session_state.drill_result   = None     # (rating, similarity)
        st.session_state.drill_session_correct = 0
        st.session_state.drill_session_total   = 0

    screen = st.session_state.drill_screen

    # ── HOME: deck picker ────────────────────────────────────────────────────
    if screen == "home":
        _render_home(srs)

    # ── DECK: overview before starting ───────────────────────────────────────
    elif screen == "deck":
        _render_deck_overview(srs)

    # ── CARD: active drilling ─────────────────────────────────────────────────
    elif screen == "card":
        _render_card(srs)

    # ── SESSION DONE ──────────────────────────────────────────────────────────
    elif screen == "session_done":
        _render_session_done(srs)

# ─── Home screen ─────────────────────────────────────────────────────────────

def _render_home(srs):
    st.markdown("## 🧠 Drill Mode")
    st.caption("Spaced repetition flashcards. Cards you miss come back sooner.")
    st.divider()

    for i, deck in enumerate(DRILL_DECKS):
        stats = _deck_stats(deck, srs)
        with st.container():
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                due_label = f"**{stats['due']} due**" if stats['due'] > 0 else "No cards due"
                st.markdown(f"### {deck['icon']} {deck['name']}")
                st.caption(deck['description'])

                # Progress bar
                pct = stats['seen'] / stats['total'] if stats['total'] else 0
                st.progress(pct)
                cols = st.columns(4)
                cols[0].metric("Total",    stats['total'])
                cols[1].metric("Due",      stats['due'],     delta=None)
                cols[2].metric("Mastered", stats['mastered'])
                cols[3].metric("Accuracy", f"{stats['accuracy']}%" if stats['seen'] else "—")

            with col_btn:
                st.write("")
                st.write("")
                btn_label = f"▶ Study ({stats['due']} due)" if stats['due'] > 0 else "▶ Review"
                if st.button(btn_label, key=f"deck_{i}", use_container_width=True, type="primary"):
                    st.session_state.drill_deck_idx = i
                    st.session_state.drill_screen   = "deck"
                    st.rerun()

                if stats['seen'] > 0:
                    if st.button("Reset", key=f"reset_{i}", use_container_width=True):
                        _reset_deck(srs, deck)
                        st.rerun()

            st.divider()

# ─── Deck overview ────────────────────────────────────────────────────────────

def _render_deck_overview(srs):
    deck  = DRILL_DECKS[st.session_state.drill_deck_idx]
    stats = _deck_stats(deck, srs)
    queue = _build_queue(deck, srs)

    st.markdown(f"## {deck['icon']} {deck['name']}")
    st.caption(deck['description'])
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cards Due",  stats['due'])
    c2.metric("New Cards",  stats['unseen'])
    c3.metric("Mastered",   stats['mastered'])
    c4.metric("Accuracy",   f"{stats['accuracy']}%" if stats['seen'] else "—")

    st.write("")

    if not queue:
        st.success("🎉 You're all caught up! No cards due today. Come back tomorrow.")
        if st.button("← Back to Decks"):
            st.session_state.drill_screen = "home"
            st.rerun()
        return

    st.info(f"**{len(queue)} cards** ready to review today ({stats['due']} due + {stats['unseen']} new)")

    col_start, col_back = st.columns([2, 1])
    with col_start:
        if st.button(f"▶ Start Session ({len(queue)} cards)", type="primary", use_container_width=True):
            st.session_state.drill_queue           = queue
            st.session_state.drill_card_idx        = 0
            st.session_state.drill_show_ans        = False
            st.session_state.drill_user_ans        = ""
            st.session_state.drill_result          = None
            st.session_state.drill_session_correct = 0
            st.session_state.drill_session_total   = 0
            st.session_state.drill_screen          = "card"
            st.rerun()
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.drill_screen = "home"
            st.rerun()

# ─── Card screen ─────────────────────────────────────────────────────────────

def _render_card(srs):
    deck  = DRILL_DECKS[st.session_state.drill_deck_idx]
    queue = st.session_state.drill_queue
    idx   = st.session_state.drill_card_idx

    if idx >= len(queue):
        st.session_state.drill_screen = "session_done"
        st.rerun()
        return

    card = queue[idx]
    total_in_session = len(queue)

    # Progress
    progress_pct = idx / total_in_session
    st.progress(progress_pct)
    st.caption(f"Card {idx + 1} of {total_in_session}  •  {deck['icon']} {deck['name']}")

    # Card display
    st.markdown(
        f"""
        <div style="
            background: #141420;
            border: 1px solid #2A2A40;
            border-radius: 16px;
            padding: 28px 24px 20px 24px;
            margin: 12px 0;
        ">
            <div style="color:#9090B0; font-size:11px; font-weight:900;
                        letter-spacing:2px; margin-bottom:14px;">QUESTION</div>
            <div style="color:#FFFFFF; font-size:22px; font-weight:600;
                        line-height:1.5;">{card['q']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Hint
    if card.get("hint") and not st.session_state.drill_show_ans:
        with st.expander("💡 Show hint"):
            st.write(card["hint"])

    # Answer phase
    if not st.session_state.drill_show_ans:
        user_ans = st.text_input(
            "Your answer:",
            value=st.session_state.drill_user_ans,
            placeholder="Type your answer…",
            key=f"drill_input_{idx}",
            label_visibility="collapsed"
        )
        col_check, col_reveal = st.columns([3, 1])
        with col_check:
            if st.button("✓ Check Answer", type="primary", use_container_width=True):
                st.session_state.drill_user_ans = user_ans
                sim = _similarity(user_ans, card["a"])
                st.session_state.drill_result   = ("check", sim, user_ans)
                st.session_state.drill_show_ans = True
                st.rerun()
        with col_reveal:
            if st.button("Reveal", use_container_width=True):
                st.session_state.drill_user_ans = ""
                st.session_state.drill_result   = ("reveal", None, "")
                st.session_state.drill_show_ans = True
                st.rerun()

    else:
        # Show correct answer
        st.markdown(
            f"""
            <div style="
                background: #1C1C2E;
                border: 1.5px solid #F0B429;
                border-radius: 12px;
                padding: 18px 20px;
                margin: 8px 0;
            ">
                <div style="color:#9090B0; font-size:10px; font-weight:900;
                            letter-spacing:2px; margin-bottom:8px;">CORRECT ANSWER</div>
                <div style="color:#F0B429; font-size:20px; font-weight:700;">{card['a']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        result_type, sim, user_ans = st.session_state.drill_result

        # Show match result if they typed something
        if result_type == "check" and user_ans:
            auto_correct = sim >= 75
            if auto_correct:
                st.success(f"✅ Match! Similarity: {sim}%  ·  You wrote: *\"{user_ans}\"*")
            else:
                st.error(f"❌ No match. Similarity: {sim}%  ·  You wrote: *\"{user_ans}\"*")

        # Rating buttons
        st.markdown("**How did you do?**")

        if result_type == "check" and user_ans:
            # 3-button layout when typed
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("❌ Wrong", use_container_width=True):
                    _submit_rating(srs, deck, card, 1)
            with c2:
                if st.button("😅 Hard", use_container_width=True):
                    _submit_rating(srs, deck, card, 3)
            with c3:
                label = "✅ Easy!" if auto_correct else "✅ Got It"
                if st.button(label, use_container_width=True, type="primary"):
                    _submit_rating(srs, deck, card, 5 if auto_correct else 4)
        else:
            # 4-button layout for reveal mode
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("❌ Wrong", use_container_width=True):
                    _submit_rating(srs, deck, card, 1)
            with c2:
                if st.button("😅 Hard", use_container_width=True):
                    _submit_rating(srs, deck, card, 3)
            with c3:
                if st.button("👍 Good", use_container_width=True, type="primary"):
                    _submit_rating(srs, deck, card, 4)
            with c4:
                if st.button("⚡ Easy", use_container_width=True):
                    _submit_rating(srs, deck, card, 5)

        st.caption("Wrong → repeat today  ·  Hard → soon  ·  Good → standard interval  ·  Easy → extended interval")

    # Quit session
    st.write("")
    if st.button("↩ Exit Session", use_container_width=False):
        st.session_state.drill_screen = "home"
        st.rerun()


def _submit_rating(srs, deck, card, rating):
    cs  = _get_card_state(srs, deck["name"], card["q"])
    cs  = _apply_rating(cs, rating)
    _save_card_state(srs, deck["name"], card["q"], cs)

    if rating >= 4:
        st.session_state.drill_session_correct += 1
    st.session_state.drill_session_total += 1

    # If wrong, re-insert card later in queue for this session
    if rating == 1:
        queue = st.session_state.drill_queue
        idx   = st.session_state.drill_card_idx
        reinsert_at = min(idx + 3, len(queue))
        queue.insert(reinsert_at, card)
        st.session_state.drill_queue = queue

    st.session_state.drill_card_idx  += 1
    st.session_state.drill_show_ans   = False
    st.session_state.drill_user_ans   = ""
    st.session_state.drill_result     = None

    if st.session_state.drill_card_idx >= len(st.session_state.drill_queue):
        st.session_state.drill_screen = "session_done"

    st.rerun()

# ─── Session done ─────────────────────────────────────────────────────────────

def _render_session_done(srs):
    deck    = DRILL_DECKS[st.session_state.drill_deck_idx]
    correct = st.session_state.drill_session_correct
    total   = st.session_state.drill_session_total
    pct     = round(correct / total * 100) if total else 0

    st.balloons()
    st.markdown("## 🎉 Session Complete!")
    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("Cards Reviewed", total)
    c2.metric("Correct",        f"{correct} ({pct}%)")
    stats = _deck_stats(deck, srs)
    c3.metric("Deck Mastered",  f"{stats['mastered']}/{stats['total']}")

    if pct == 100:
        st.success("Perfect session! 🌟")
    elif pct >= 75:
        st.success("Great work! Keep it up.")
    elif pct >= 50:
        st.warning("Solid effort — the missed cards will come back soon.")
    else:
        st.info("Tough session — the cards you missed will repeat until they stick.")

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔁 Study Again", use_container_width=True, type="primary"):
            st.session_state.drill_screen = "deck"
            st.rerun()
    with col2:
        if st.button("📚 All Decks", use_container_width=True):
            st.session_state.drill_screen = "home"
            st.rerun()

# ─── Reset helper ─────────────────────────────────────────────────────────────

def _reset_deck(srs: dict, deck: dict):
    for card in deck["cards"]:
        key = _card_key(deck["name"], card["q"])
        if key in srs:
            del srs[key]
    _save_srs(srs)
