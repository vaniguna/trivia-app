import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓")

# --- DATA LOADING (Fast & Offline) ---
@st.cache_data
def load_archive():
    # This pulls a 120,000+ clue dataset directly from a high-speed mirror
    url = "https://raw.githubusercontent.com/jwolle1/jeopardy_clue_dataset/master/jeopardy_questions.csv"
    try:
        # We sample it so it's fast on your iPhone
        df = pd.read_csv(url).sample(5000) 
        return df
    except Exception as e:
        st.error(f"Failed to fetch show data: {e}")
        return None

df = load_archive()

# --- APP STATE ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.score = 0

def get_new_clue():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df) - 1)
        st.session_state.show = False

# --- UI ---
st.title("🏆 J-Archive Offline Trainer")

if df is None:
    st.error("Data file not found. Please upload 'season41.tsv' to your GitHub.")
else:
    # First-time load
    if st.session_state.idx == 0 and not st.session_state.show:
        get_new_clue()

    clue_data = df.iloc[st.session_state.idx]
    
    st.info(f"CATEGORY: {str(clue_data['category']).upper()}")
    st.subheader(clue_data['clue'])
    st.caption(f"Season {clue_data.get('season', '??')} | Value: ${clue_data.get('value', 400)}")

    if not st.session_state.show:
        if st.button("REVEAL ANSWER", type="primary"):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue_data['answer']).upper()}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ GOT IT"):
                st.session_state.score += int(clue_data.get('value', 400))
                get_new_clue()
                st.rerun()
        with c2:
            if st.button("❌ MISSED"):
                st.session_state.score -= int(clue_data.get('value', 400))
                get_new_clue()
                st.rerun()

st.sidebar.metric("Bank", f"${st.session_state.score}")

