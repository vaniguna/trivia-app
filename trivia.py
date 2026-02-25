"""
drill_mode.py — Spaced repetition drill module for the Jeopardy Trainer.
Call render_drill_mode() from the main app to embed this as a tab.

Persistence:
  Progress (SRS state, resume positions, shuffle prefs) is stored in Supabase.
  Credentials are read from Streamlit secrets — never hard-coded here.

  Required in Streamlit Cloud → Settings → Secrets:
    SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
    SUPABASE_KEY = "your-anon-key-here"

  Required Supabase table (run once in SQL Editor):
    CREATE TABLE drill_progress (
        user_id       TEXT PRIMARY KEY,
        srs           JSONB NOT NULL DEFAULT '{}',
        resume        JSONB NOT NULL DEFAULT '{}',
        shuffle_prefs JSONB NOT NULL DEFAULT '{}',
        updated_at    TIMESTAMPTZ DEFAULT NOW()
    );
    INSERT INTO drill_progress (user_id) VALUES ('default');
"""

import streamlit as st
import json
import re
import random
from datetime import date, timedelta
from drill_data import DRILL_DECKS

# ─── Supabase client ──────────────────────────────────────────────────────────

@st.cache_resource
def _get_supabase():
    """Create and cache the Supabase client for the lifetime of the server."""
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Could not connect to Supabase: {e}")
        return None

USER_ID = "default"  # single-user app; extend this for multi-user later

# ─── Database I/O ─────────────────────────────────────────────────────────────

def _empty_progress() -> dict:
    return {"srs": {}, "resume": {}, "shuffle_prefs": {}}

def _load_from_db() -> dict:
    """Fetch the progress row from Supabase. Returns empty structure on failure."""
    try:
        client = _get_supabase()
        if client is None:
            return _empty_progress()
        result = (
            client.table("drill_progress")
            .select("srs, resume, shuffle_prefs")
            .eq("user_id", USER_ID)
            .single()
            .execute()
        )
        row = result.data
        if not row:
            return _empty_progress()
        return {
            "srs":           row.get("srs")           or {},
            "resume":        row.get("resume")        or {},
            "shuffle_prefs": row.get("shuffle_prefs") or {},
        }
    except Exception as e:
        st.warning(f"⚠️ Could not load progress from database: {e}")
        return _empty_progress()

def _save_to_db(data: dict):
    """Upsert the full progress dict back to Supabase."""
    try:
        client = _get_supabase()
        if client is None:
            return
        client.table("drill_progress").upsert({
            "user_id":       USER_ID,
            "srs":           data.get("srs",           {}),
            "resume":        data.get("resume",        {}),
            "shuffle_prefs": data.get("shuffle_prefs", {}),
            "updated_at":    date.today().isoformat(),
        }).execute()
    except Exception as e:
        st.warning(f"⚠️ Could not save progress to database: {e}")

# ─── In-memory cache (one DB read per browser session, write-through on save) ─

def _get_progress() -> dict:
    """Load from DB the first time per browser session, then use cached copy."""
    if "drill_progress" not in st.session_state:
        st.session_state.drill_progress = _load_from_db()
    return st.session_state.drill_progress

def _flush():
    """Write current in-memory progress to Supabase."""
    _save_to_db(_get_progress())

# ─── Typed section accessors ──────────────────────────────────────────────────

def _load_srs() -> dict:
    return _get_progress().get("srs", {})

def _save_srs(srs: dict):
    _get_progress()["srs"] = srs
    _flush()

def _load_resume() -> dict:
    return _get_progress().get("resume", {})

def _save_resume(positions: dict):
    _get_progress()["resume"] = positions
    _flush()

def _load_shuffle_prefs() -> dict:
    return _get_progress().get("shuffle_prefs", {})

def _save_shuffle_prefs(prefs: dict):
    _get_progress()["shuffle_prefs"] = prefs
    _flush()

# ─── Card-level SRS helpers ───────────────────────────────────────────────────

def _card_key(deck_name: str, q: str) -> str:
    return f"{deck_name}||{q}"

def _get_card_state(srs: dict, deck_name: str, q: str) -> dict:
    return srs.get(_card_key(deck_name, q), {
        "ease":        2.5,
        "interval":    1,
        "repetitions": 0,
        "due":         str(date.today()),
        "correct":     0,
        "total":       0,
    })

def _save_card_state(srs: dict, deck_name: str, q: str, card_state: dict):
    srs[_card_key(deck_name, q)] = card_state
    _save_srs(srs)

# ─── SM-2 update ──────────────────────────────────────────────────────────────

def _apply_rating(cs: dict, rating: int) -> dict:
    """rating: 1=Wrong, 3=Hard, 4=Good, 5=Easy"""
    cs    = cs.copy()
    today = date.today()

    if rating == 1:
        cs["repetitions"] = 0
        cs["interval"]    = 1
        cs["ease"]        = max(1.3, cs["ease"] - 0.2)
    else:
        cs["correct"] = cs.get("correct", 0) + 1
        if cs["repetitions"] == 0:
            cs["interval"] = 1
        elif cs["repetitions"] == 1:
            cs["interval"] = 6
        else:
            multiplier = cs["ease"]
            if rating == 3:
                cs["ease"] = max(1.3, cs["ease"] - 0.15)
                multiplier = 1.0
            elif rating == 5:
                cs["ease"] = min(3.0, cs["ease"] + 0.1)
                multiplier = cs["ease"] * 1.3
            cs["interval"] = max(1, round(cs["interval"] * multiplier))
        cs["repetitions"] += 1

    cs["total"] = cs.get("total", 0) + 1
    cs["due"]   = str(today + timedelta(days=cs["interval"]))
    return cs

# ─── Queue builders ───────────────────────────────────────────────────────────

def _build_queue(deck: dict, srs: dict, shuffled: bool) -> list:
    """Due today/overdue + never-seen cards. Mastered-and-not-due excluded."""
    today_str = str(date.today())
    due, new_cards = [], []

    for card in deck["cards"]:
        cs = _get_card_state(srs, deck["name"], card["q"])
        if cs["total"] == 0:
            new_cards.append(card)
        elif cs["due"] <= today_str:
            due.append((cs["due"], card))

    due.sort(key=lambda x: x[0])
    due_cards = [c for _, c in due]

    if shuffled:
        random.shuffle(due_cards)
        random.shuffle(new_cards)

    return due_cards + new_cards

def _build_full_queue(deck: dict, srs: dict, shuffled: bool) -> list:
    """All cards: overdue → upcoming → new → mastered.
    Used only for locating the first unmastered card across the whole deck."""
    today_str = str(date.today())
    overdue, upcoming, mastered_cards, new_cards = [], [], [], []

    for card in deck["cards"]:
        cs = _get_card_state(srs, deck["name"], card["q"])
        if cs["total"] == 0:
            new_cards.append(card)
        elif cs["interval"] >= 21:
            mastered_cards.append(card)
        elif cs["due"] <= today_str:
            overdue.append((cs["due"], card))
        else:
            upcoming.append((cs["due"], card))

    overdue.sort(key=lambda x: x[0])
    upcoming.sort(key=lambda x: x[0])
    result = [c for _, c in overdue] + [c for _, c in upcoming] + new_cards
    if shuffled:
        random.shuffle(result)
    return result + mastered_cards

# ─── Stats & helpers ──────────────────────────────────────────────────────────

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
        "total":    total,
        "seen":     seen,
        "unseen":   total - seen,
        "due":      due,
        "mastered": mastered,
        "accuracy": accuracy,
    }

def _find_first_unmastered(deck: dict, srs: dict, queue: list) -> int:
    for i, card in enumerate(queue):
        cs = _get_card_state(srs, deck["name"], card["q"])
        if cs["interval"] < 21:
            return i
    return 0

# ─── Fuzzy grading ────────────────────────────────────────────────────────────

_SHARED_SURNAMES = {"adams", "harrison", "johnson", "roosevelt", "bush"}
_PRESIDENT_ALIASES = {
    "jfk":             "john kennedy",
    "fdr":             "franklin roosevelt",
    "lbj":             "lyndon johnson",
    "teddy":           "theodore roosevelt",
    "teddy roosevelt": "theodore roosevelt",
    "ike":             "eisenhower",
}

def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r'\b(a|an|the)\b', '', t)
    t = re.sub(r'[^a-z0-9\s]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def _similarity(a: str, b: str) -> int:
    """
    Returns 0-100 similarity score.
    - Bare shared presidential surnames (Adams, Harrison, Johnson, Roosevelt,
      Bush) return 0 — first name required.
    - Aliases (JFK, FDR, LBJ, Teddy, Ike) are expanded before matching.
    - A single word that exactly matches any word in the correct answer scores 100
      (handles "Nixon" matching "Richard Nixon").
    """
    u_raw = _normalize(a)
    c_norm = _normalize(b)
    if not u_raw or not c_norm:
        return 0

    # Reject bare shared surname
    parts = u_raw.split()
    if len(parts) == 1 and parts[0] in _SHARED_SURNAMES:
        return 0

    # Expand aliases
    u = _PRESIDENT_ALIASES.get(u_raw, u_raw)

    # Exact or substring match (also try stripping middle initials from correct)
    c_no_initials = re.sub(r'\b[a-z]\b', '', c_norm).strip()
    c_no_initials = re.sub(r'\s+', ' ', c_no_initials).strip()
    for c_variant in [c_norm, c_no_initials]:
        if u == c_variant or u in c_variant or c_variant in u:
            return 100

    # Single-word last-name match against any word in correct answer
    u_parts = u.split()
    c_parts = c_norm.split()
    if len(u_parts) == 1 and u_parts[0] in c_parts:
        return 100

    # Character-level edit distance
    ua, ca = list(u), list(c_norm)
    m, n = len(ua), len(ca)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i-1][j-1] if ua[i-1] == ca[j-1] \
                       else 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    dist = dp[m][n]
    return int((max(m, n) - dist) / max(m, n) * 100)

# ─── Session state helpers ────────────────────────────────────────────────────

def _init_session_state():
    defaults = {
        "drill_screen":          "home",
        "drill_deck_idx":        None,
        "drill_queue":           [],
        "drill_card_idx":        0,
        "drill_frontier":        0,
        "drill_show_ans":        False,
        "drill_user_ans":        "",
        "drill_result":          None,
        "drill_session_correct": 0,
        "drill_session_total":   0,
        "drill_shuffled":        False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _reset_card_display():
    st.session_state.drill_show_ans = False
    st.session_state.drill_user_ans = ""
    st.session_state.drill_result   = None

def _go_to_card(idx: int):
    """Move cursor, update frontier, persist resume position to DB."""
    st.session_state.drill_card_idx = idx
    st.session_state.drill_frontier = max(st.session_state.drill_frontier, idx)

    queue    = st.session_state.drill_queue
    deck_idx = st.session_state.drill_deck_idx
    if queue and deck_idx is not None and idx < len(queue):
        deck      = DRILL_DECKS[deck_idx]
        positions = _load_resume()
        positions[deck["name"]] = queue[idx]["q"]
        _save_resume(positions)

    _reset_card_display()

# ─── Main entry point ─────────────────────────────────────────────────────────

def render_drill_mode():
    _init_session_state()
    srs    = _load_srs()
    screen = st.session_state.drill_screen

    if screen == "home":
        _render_home(srs)
    elif screen == "deck":
        _render_deck_overview(srs)
    elif screen == "card":
        _render_card(srs)
    elif screen == "session_done":
        _render_session_done(srs)

# ─── Home screen ──────────────────────────────────────────────────────────────

def _render_home(srs):
    st.markdown("## 🧠 Drill Mode")
    st.caption("Spaced repetition flashcards. Cards you miss come back sooner.")
    st.divider()

    resume_positions = _load_resume()

    for i, deck in enumerate(DRILL_DECKS):
        stats      = _deck_stats(deck, srs)
        can_resume = deck["name"] in resume_positions

        with st.container():
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"### {deck['icon']} {deck['name']}")
                st.caption(deck['description'])
                pct = stats['seen'] / stats['total'] if stats['total'] else 0
                st.progress(pct)
                cols = st.columns(4)
                cols[0].metric("Total",    stats['total'])
                cols[1].metric("Due",      stats['due'])
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

                if can_resume:
                    if st.button("⏎ Resume", key=f"resume_{i}", use_container_width=True):
                        _start_session(deck_idx=i, srs=srs, resume=True)

                if stats['seen'] > 0 and stats['mastered'] < stats['total']:
                    if st.button("⏩ First unmastered", key=f"unmastered_{i}",
                                 use_container_width=True,
                                 help="Jump to the first card not yet mastered"):
                        _start_session(deck_idx=i, srs=srs, resume=False, first_unmastered=True)

                if stats['seen'] > 0:
                    if st.button("Reset", key=f"reset_{i}", use_container_width=True):
                        _reset_deck(srs, deck)
                        positions = _load_resume()
                        positions.pop(deck["name"], None)
                        _save_resume(positions)
                        st.rerun()

            st.divider()

# ─── Deck overview ────────────────────────────────────────────────────────────

def _render_deck_overview(srs):
    deck  = DRILL_DECKS[st.session_state.drill_deck_idx]
    stats = _deck_stats(deck, srs)
    queue = _build_queue(deck, srs, shuffled=False)

    shuffle_prefs = _load_shuffle_prefs()
    deck_shuffle  = shuffle_prefs.get(deck["name"], False)

    st.markdown(f"## {deck['icon']} {deck['name']}")
    st.caption(deck['description'])
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cards Due",  stats['due'])
    c2.metric("New Cards",  stats['unseen'])
    c3.metric("Mastered",   stats['mastered'])
    c4.metric("Accuracy",   f"{stats['accuracy']}%" if stats['seen'] else "—")

    st.write("")

    new_shuffle = st.toggle(
        "🔀 Random order",
        value=deck_shuffle,
        help="Shuffles the session queue. SRS still determines which cards are due — "
             "shuffle only changes the order they appear within due/new groups.",
    )
    if new_shuffle != deck_shuffle:
        shuffle_prefs[deck["name"]] = new_shuffle
        _save_shuffle_prefs(shuffle_prefs)

    st.write("")

    if not queue:
        st.success("🎉 You're all caught up! No cards due today. Come back tomorrow.")
        if st.button("← Back to Decks"):
            st.session_state.drill_screen = "home"
            st.rerun()
        return

    order_label = "shuffled" if new_shuffle else "SRS order"
    st.info(f"**{len(queue)} cards** ready ({stats['due']} due + {stats['unseen']} new) — {order_label}")

    col_start, col_back = st.columns([2, 1])
    with col_start:
        if st.button(f"▶ Start Session ({len(queue)} cards)", type="primary", use_container_width=True):
            _start_session(deck_idx=st.session_state.drill_deck_idx, srs=srs, resume=False)
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.drill_screen = "home"
            st.rerun()

# ─── Session launcher ─────────────────────────────────────────────────────────

def _start_session(deck_idx: int, srs: dict, resume: bool, first_unmastered: bool = False):
    deck          = DRILL_DECKS[deck_idx]
    shuffle_prefs = _load_shuffle_prefs()
    shuffled      = shuffle_prefs.get(deck["name"], False)
    queue         = _build_queue(deck, srs, shuffled=shuffled)

    if not queue:
        st.session_state.drill_screen   = "deck"
        st.session_state.drill_deck_idx = deck_idx
        st.rerun()
        return

    start_idx = 0

    if first_unmastered:
        full_queue     = _build_full_queue(deck, srs, shuffled=shuffled)
        unmastered_idx = _find_first_unmastered(deck, srs, full_queue)
        target_q       = full_queue[unmastered_idx]["q"] if full_queue else None
        if target_q:
            for i, card in enumerate(queue):
                if card["q"] == target_q:
                    start_idx = i
                    break
    elif resume:
        last_q = _load_resume().get(deck["name"])
        if last_q:
            for i, card in enumerate(queue):
                if card["q"] == last_q:
                    start_idx = i
                    break

    st.session_state.drill_deck_idx        = deck_idx
    st.session_state.drill_queue           = queue
    st.session_state.drill_card_idx        = start_idx
    st.session_state.drill_frontier        = start_idx
    st.session_state.drill_shuffled        = shuffled
    st.session_state.drill_session_correct = 0
    st.session_state.drill_session_total   = 0
    st.session_state.drill_screen          = "card"
    _reset_card_display()

    # Persist starting position immediately
    positions = _load_resume()
    positions[deck["name"]] = queue[start_idx]["q"]
    _save_resume(positions)

    st.rerun()

# ─── Card screen ──────────────────────────────────────────────────────────────

def _render_card(srs):
    deck     = DRILL_DECKS[st.session_state.drill_deck_idx]
    queue    = st.session_state.drill_queue
    idx      = st.session_state.drill_card_idx
    frontier = st.session_state.drill_frontier

    if idx >= len(queue):
        st.session_state.drill_screen = "session_done"
        st.rerun()
        return

    card            = queue[idx]
    total           = len(queue)
    at_frontier     = (idx >= frontier)
    behind_frontier = (idx < frontier)

    # ── Progress ──────────────────────────────────────────────────────────────
    st.progress(idx / total)
    order_label = "🔀 shuffled" if st.session_state.drill_shuffled else "SRS order"
    st.caption(
        f"Card **{idx + 1}** of **{total}**  •  "
        f"{deck['icon']} {deck['name']}  •  {order_label}"
    )

    # ── Navigation bar: ← prev  [n/total]  next →  ⏭ new ─────────────────
    show_jump = behind_frontier
    nav_cols  = st.columns([1, 2, 1, 1]) if show_jump else st.columns([1, 2, 1])

    with nav_cols[0]:
        if st.button("← Prev", disabled=(idx == 0),
                     use_container_width=True, key="nav_prev"):
            _go_to_card(idx - 1)
            st.rerun()

    with nav_cols[1]:
        st.markdown(
            f"<div style='text-align:center; color:#9090B0; padding-top:8px; "
            f"font-size:13px; font-weight:600;'>{idx + 1} / {total}</div>",
            unsafe_allow_html=True,
        )

    with nav_cols[2]:
        if st.button("Next →", disabled=(idx >= total - 1),
                     use_container_width=True, key="nav_next"):
            _go_to_card(idx + 1)
            st.rerun()

    if show_jump:
        with nav_cols[3]:
            if st.button("⏭ New", use_container_width=True, key="nav_frontier",
                         help="Jump to the next unseen card at the frontier"):
                _go_to_card(frontier)
                st.rerun()

    st.write("")

    # ── Re-rating notice ──────────────────────────────────────────────────────
    if behind_frontier:
        cs = _get_card_state(srs, deck["name"], card["q"])
        if cs["total"] > 0:
            st.info("📝 You've rated this card before. Rating again will replace the previous rating.")

    # ── Question card ─────────────────────────────────────────────────────────
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
        unsafe_allow_html=True,
    )

    # ── Hint ──────────────────────────────────────────────────────────────────
    if card.get("hint") and not st.session_state.drill_show_ans:
        with st.expander("💡 Show hint"):
            st.write(card["hint"])

    # ── Answer phase ──────────────────────────────────────────────────────────
    if not st.session_state.drill_show_ans:
        user_ans = st.text_input(
            "Your answer:",
            value=st.session_state.drill_user_ans,
            placeholder="Type your answer…",
            key=f"drill_input_{idx}",
            label_visibility="collapsed",
        )
        col_check, col_reveal = st.columns([3, 1])
        with col_check:
            if st.button("✓ Check Answer", type="primary", use_container_width=True,
                         key=f"check_{idx}"):
                st.session_state.drill_user_ans = user_ans
                sim = _similarity(user_ans, card["a"])
                st.session_state.drill_result   = ("check", sim, user_ans)
                st.session_state.drill_show_ans = True
                st.rerun()
        with col_reveal:
            if st.button("Reveal", use_container_width=True, key=f"reveal_{idx}"):
                st.session_state.drill_user_ans = ""
                st.session_state.drill_result   = ("reveal", None, "")
                st.session_state.drill_show_ans = True
                st.rerun()

    else:
        # ── Answer reveal ─────────────────────────────────────────────────────
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
            unsafe_allow_html=True,
        )

        result_type, sim, user_ans = st.session_state.drill_result

        if result_type == "check" and user_ans:
            auto_correct = sim >= 75
            if auto_correct:
                st.success(f"✅ Match! Similarity: {sim}%  ·  You wrote: *\"{user_ans}\"*")
            else:
                st.error(f"❌ No match. Similarity: {sim}%  ·  You wrote: *\"{user_ans}\"*")

        st.markdown("**How did you do?**")

        if result_type == "check" and user_ans:
            auto_correct = sim >= 75
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("❌ Wrong", use_container_width=True, key=f"r1_{idx}"):
                    _submit_rating(srs, deck, card, 1, at_frontier)
            with c2:
                if st.button("😅 Hard", use_container_width=True, key=f"r3_{idx}"):
                    _submit_rating(srs, deck, card, 3, at_frontier)
            with c3:
                label = "✅ Easy!" if auto_correct else "✅ Got It"
                if st.button(label, use_container_width=True, type="primary", key=f"r5_{idx}"):
                    _submit_rating(srs, deck, card, 5 if auto_correct else 4, at_frontier)
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("❌ Wrong", use_container_width=True, key=f"r1_{idx}"):
                    _submit_rating(srs, deck, card, 1, at_frontier)
            with c2:
                if st.button("😅 Hard", use_container_width=True, key=f"r3_{idx}"):
                    _submit_rating(srs, deck, card, 3, at_frontier)
            with c3:
                if st.button("👍 Good", use_container_width=True, type="primary", key=f"r4_{idx}"):
                    _submit_rating(srs, deck, card, 4, at_frontier)
            with c4:
                if st.button("⚡ Easy", use_container_width=True, key=f"r5_{idx}"):
                    _submit_rating(srs, deck, card, 5, at_frontier)

        st.caption(
            "Wrong → repeat today  ·  Hard → soon  ·  "
            "Good → standard interval  ·  Easy → extended interval"
        )
        if behind_frontier:
            st.caption("ℹ️ Rating a back-visited card replaces its previous SRS rating.")

    st.write("")
    if st.button("↩ Exit Session", key="exit_session"):
        st.session_state.drill_screen = "home"
        st.rerun()

# ─── Rating submission ────────────────────────────────────────────────────────

def _submit_rating(srs: dict, deck: dict, card: dict, rating: int, at_frontier: bool):
    cs = _get_card_state(srs, deck["name"], card["q"])

    # Back out previous rating's contribution before re-applying
    if cs["total"] > 0:
        was_correct   = cs.get("correct", 0) > 0 and cs.get("repetitions", 0) > 0
        cs["total"]   = max(0, cs["total"] - 1)
        if was_correct:
            cs["correct"] = max(0, cs.get("correct", 0) - 1)

    cs = _apply_rating(cs, rating)
    _save_card_state(srs, deck["name"], card["q"], cs)  # writes to Supabase

    if at_frontier:
        if rating >= 4:
            st.session_state.drill_session_correct += 1
        st.session_state.drill_session_total += 1

        if rating == 1:
            queue       = st.session_state.drill_queue
            idx         = st.session_state.drill_card_idx
            reinsert_at = min(idx + 3, len(queue))
            queue.insert(reinsert_at, card)
            st.session_state.drill_queue = queue

        new_idx = st.session_state.drill_card_idx + 1
        if new_idx >= len(st.session_state.drill_queue):
            positions = _load_resume()
            positions.pop(deck["name"], None)
            _save_resume(positions)
            st.session_state.drill_screen = "session_done"
            st.rerun()
        else:
            _go_to_card(new_idx)
            st.session_state.drill_frontier = new_idx
    else:
        _reset_card_display()

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
    col1, col2 = st.columns(2)
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
    _save_srs(srs)  # writes to Supabase
