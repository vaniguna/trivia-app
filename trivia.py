import streamlit as st
import requests
import random

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓")

# The "Holy Grail" URL: A direct link to a massive JSON dump of real clues
DATA_URL = "https://raw.githubusercontent.com/fivethirtyeight/data/master/jeopardy/jeopardy.csv"
# Since CSVs are huge to load every time, we'll use a fast random-sampling API that 
# mimics the J-Archive structure but is actually stable in 2026.
API_URL = "https://cluebase.lukelav.in/clues/random?limit=20"

if 'bank' not in st.session_state:
    st.session_state.bank = []
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.score = 0

def refresh_clues():
    try:
        # Pulling 20 real clues at once to minimize loading screens
        r = requests.get(API_URL, timeout=10)
        if r.status_code == 200:
            st.session_state.bank = r.json()['data']
            st.session_state.idx = 0
            st.session_state.show = False
    except:
        st.error("Archive connection slow. Retrying...")

# --- UI ---
st.title("🏆 The J-Archive Pro-Trainer")

if not st.session_state.bank:
    if st.button("LOAD SHOW DATA", type="primary"):
        refresh_clues()
        st.rerun()
else:
    clue = st.session_state.bank[st.session_state.idx]
    
    st.info(f"CATEGORY: {clue['category'].upper()}")
    st.subheader(clue['clue'])
    st.caption(f"Round: {clue['round']} | Value: ${clue['value'] or 'Final'}")

    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", type="primary"):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {clue['response'].upper()}")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ YES"):
                st.session_state.score += (clue['value'] or 1000)
                st.session_state.idx += 1
                st.session_state.show = False
                st.rerun()
        with c2:
            if st.button("❌ NO"):
                st.session_state.score -= (clue['value'] or 1000)
                st.session_state.idx += 1
                st.session_state.show = False
                st.rerun()
        with c3:
            if st.button("⏩ SKIP"):
                st.session_state.idx += 1
                st.session_state.show = False
                st.rerun()

    # Automatic reload when bank is empty
    if st.session_state.idx >= len(st.session_state.bank):
        refresh_clues()
        st.rerun()

st.sidebar.metric("Career Earnings", f"${st.session_state.score}")
