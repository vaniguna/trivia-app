"""
drill_mode.py — Spaced repetition drill module for the Jeopardy Trainer.
Call render_drill_mode() from the main app to embed this as a tab.

New features:
  - Random order toggle (shuffles session queue while preserving SRS priority)
  - Back / Forward navigation through visited cards
  - Re-rating a back-visited card replaces the original SRS rating
  - ⏭ Jump to frontier button (appears in nav bar only when behind the frontier)
  - Resume: picks up at the last-viewed card, continues forward through remaining
    queue, respecting the shuffle setting that was active when you left

Session state model:
  drill_queue       list of card dicts for this session (ordered or shuffled)
  drill_card_idx    current position in queue (the "cursor")
  drill_frontier    highest index reached so far (cards beyond here are unseen)
  drill_show_ans    whether answer is revealed for current card
  drill_user_ans    last typed answer text
  drill_result      tuple (type, sim, user_ans) or None
  drill_shuffled    bool — was shuffle on when session started?

  drill_resume_key  persists across page refreshes so we can find resume position
"""

import streamlit as st
import json
import re
import random
from datetime import date, timedelta
from drill_data import DRILL_DECKS

# ─── Persistence helpers ──────────────────────────────────────────────────────

STORAGE_KEY  = "drill_srs_state"
RESUME_KEY   = "drill_resume_positions"   # {deck_name: question_text}
SHUFFLE_KEY  = "drill_shuffle_prefs"      # {deck_name: bool}

def _load_srs() -> dict:
    raw = st.session_state.get(STORAGE_KEY, "{}")
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}

def _save_srs(state: dict):
    st.session_state[STORAGE_KEY] = state

def _load_resume() -> dict:
    raw = st.session_state.get(RESUME_KEY, "{}")
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}

def _save_resume(positions: dict):
    st.session_state[RESUME_KEY] = positions

def _load_shuffle_prefs() -> dict:
    raw = st.session_state.get(SHUFFLE_KEY, "{}")
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}

def _save_shuffle_prefs(prefs: dict):
    st.session_state[SHUFFLE_KEY] = prefs

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

# ─── SM-2 update ──────────────────────────────────────────────────────────────

def _apply_rating(card_state: dict, rating: int) -> dict:
    """rating: 1=Wrong, 3=Hard, 4=Good, 5=Easy"""
    cs    = card_state.copy()
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

# ─── Queue builder ────────────────────────────────────────────────────────────

def _build_queue(deck: dict, srs: dict, shuffled: bool) -> list:
    """
    Returns cards due today/overdue + new (never-seen) cards.
    Due cards sorted by due date; new cards appended after.
    If shuffled=True, each group is independently shuffled (preserving
    the SRS principle that overdue cards generally precede new ones).
    """
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

# ─── Fuzzy grading ────────────────────────────────────────────────────────────

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
            dp[i][j] = dp[i-1][j-1] if a[i-1] == b[j-1] \
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
    """Navigate to a specific index, updating frontier and persisting resume."""
    st.session_state.drill_card_idx = idx
    st.session_state.drill_frontier = max(st.session_state.drill_frontier, idx)

    queue    = st.session_state.drill_queue
    deck_idx = st.session_state.drill_deck_idx
    if queue and deck_idx is not None and idx < len(queue):
        deck   = DRILL_DECKS[deck_idx]
        resume = _load_resume()
        resume[deck["name"]] = queue[idx]["q"]
        _save_resume(resume)

    _reset_card_display()

# ─── Main render ──────────────────────────────────────────────────────────────

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

                if stats['seen'] > 0:
                    if st.button("Reset", key=f"reset_{i}", use_container_width=True):
                        _reset_deck(srs, deck)
                        resume = _load_resume()
                        resume.pop(deck["name"], None)
                        _save_resume(resume)
                        st.rerun()

            st.divider()

# ─── Deck overview ────────────────────────────────────────────────────────────

def _render_deck_overview(srs):
    deck   = DRILL_DECKS[st.session_state.drill_deck_idx]
    stats  = _deck_stats(deck, srs)
    queue  = _build_queue(deck, srs, shuffled=False)  # for count preview

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

    # Shuffle toggle
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

def _start_session(deck_idx: int, srs: dict, resume: bool):
    """Build queue, optionally find resume position, jump to card screen."""
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

    if resume:
        resume_positions = _load_resume()
        last_q           = resume_positions.get(deck["name"])
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

    # Persist resume position immediately
    resume_positions = _load_resume()
    resume_positions[deck["name"]] = queue[start_idx]["q"]
    _save_resume(resume_positions)

    st.rerun()

# ─── Card screen ──────────────────────────────────────────────────────────────

def _render_card(srs):
    deck      = DRILL_DECKS[st.session_state.drill_deck_idx]
    queue     = st.session_state.drill_queue
    idx       = st.session_state.drill_card_idx
    frontier  = st.session_state.drill_frontier

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

    # ── Navigation bar: ← prev  [n/total]  next →  ⏭ ─────────────────────
    can_go_back    = idx > 0
    can_go_forward = idx < total - 1
    show_jump      = behind_frontier  # ⏭ only visible when behind frontier

    if show_jump:
        nav_cols = st.columns([1, 2, 1, 1])
    else:
        nav_cols = st.columns([1, 2, 1])

    with nav_cols[0]:
        if st.button("← Prev", disabled=not can_go_back,
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
        if st.button("Next →", disabled=not can_go_forward,
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
        # ── Answer reveal card ────────────────────────────────────────────────
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

        # ── Rating buttons ────────────────────────────────────────────────────
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
                if st.button(label, use_container_width=True, type="primary",
                             key=f"r5_{idx}"):
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
                if st.button("👍 Good", use_container_width=True, type="primary",
                             key=f"r4_{idx}"):
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

    # ── Exit ──────────────────────────────────────────────────────────────────
    st.write("")
    if st.button("↩ Exit Session", key="exit_session"):
        st.session_state.drill_screen = "home"
        st.rerun()


# ─── Rating submission ────────────────────────────────────────────────────────

def _submit_rating(srs: dict, deck: dict, card: dict, rating: int, at_frontier: bool):
    """
    Save SRS rating — always replaces the previous rating for this card.

    Back-navigated re-ratings:
      - Update SRS (overwrite previous)
      - Do NOT advance session counters (avoids double-counting)
      - Do NOT re-insert wrong cards into queue (already handled at frontier)
      - Just refresh the card display after saving

    Frontier ratings (normal flow):
      - Update SRS
      - Advance session counters
      - Re-insert wrong cards 3 positions ahead
      - Advance cursor to next card (or end session)
    """
    cs = _get_card_state(srs, deck["name"], card["q"])

    # If re-rating a previously rated card, back out the last increment
    # so _apply_rating's +1 to total/correct stays accurate
    if cs["total"] > 0:
        prev_was_correct = cs.get("repetitions", 0) > 0
        cs["total"]   = max(0, cs["total"] - 1)
        if prev_was_correct:
            cs["correct"] = max(0, cs.get("correct", 0) - 1)

    cs = _apply_rating(cs, rating)
    _save_card_state(srs, deck["name"], card["q"], cs)

    if at_frontier:
        # Session counters
        if rating >= 4:
            st.session_state.drill_session_correct += 1
        st.session_state.drill_session_total += 1

        # Wrong: re-insert 3 positions ahead
        if rating == 1:
            queue       = st.session_state.drill_queue
            idx         = st.session_state.drill_card_idx
            reinsert_at = min(idx + 3, len(queue))
            queue.insert(reinsert_at, card)
            st.session_state.drill_queue = queue

        # Advance cursor
        new_idx = st.session_state.drill_card_idx + 1
        if new_idx >= len(st.session_state.drill_queue):
            resume = _load_resume()
            resume.pop(deck["name"], None)
            _save_resume(resume)
            st.session_state.drill_screen = "session_done"
            st.rerun()
        else:
            _go_to_card(new_idx)
            st.session_state.drill_frontier = new_idx
    else:
        # Re-rating a back-visited card: just refresh display
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
    _save_srs(srs)
