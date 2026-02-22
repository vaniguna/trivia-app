import streamlit as st
import pandas as pd
import random
import glob
import re
import os

# 1. Page Config
st.set_page_config(page_title="Jeopardy! Pro", page_icon="🎓", layout="centered")

# 2. Simplified CSS (Avoids multi-line string errors)
st.markdown("<style>.cat-box { background-color: #060ce9; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-family: sans-serif; font-weight: bold; font-size: 24px; text-transform: uppercase; }</style>", unsafe_allow_html=True)

# 3. Category Engine
TAGS = ["Vietnam War", "Revolutionary War", "Canadian History", "European Mountains", "Asian Rivers", "U.S. Presidents", "Shakespeare", "Science", "Other"]

def auto_tag(row):
    combined = f"{row.get('category','')} {row.get('answer','')}".lower()
    mapping = {
        "Vietnam War": "vietnam|saigon|hanoi",
        "Revolutionary War": "revolutionary war|yorktown|saratoga",
        "Canadian History": "canada|ottawa|toronto|quebec",
        "European Mountains": "alps|pyrenees|mont blanc",
        "Asian Rivers": "mekong|yangtze|ganges",
        "U.S. Presidents": "president|white house|potus",
        "Shakespeare": "shakespeare|hamlet|macbeth",
        "Science": "molecule|physics|biology|chemistry"
    }
    for tag, pattern in mapping.items():
        if re.search(pattern, combined): return tag
    return "Other"

# 4. Reliable Data Loader
@st.cache_data(show_spinner="Loading Season Data...")
def load_data():
    files = glob.glob("*.tsv")
    if not files: return None
    all_chunks = []
    for f in files:
        try:
            temp = pd.read_csv(f, sep='\t', low_memory=False)
            s_num = re.search(r'\d+', f).group() if re.search(r'\d+', f) else "??"
            temp['season'] = s_num
            all_chunks.append(temp)
        except: continue
    if not all_chunks: return None
    df = pd.concat(all_chunks, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

df = load_data()

# 5. Initialization
if 'stats' not in st.session_state:
    st.session_state.stats = {t: {"ok": 0, "total": 0} for t in TAGS}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.current_tag = "Other"
    st.session_state.ready = False

def get_next():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df)-1)
        st.session_state.show = False
        row = df.iloc[st.session_state.idx]
        st.session_state.current_tag = auto_tag(row)
        st.session_state.ready = True

# 6. Main App UI
if df is None:
    st.error("No data found! Check your folder for .tsv files.")
else:
    if not st.session_state.ready:
        get_next()

    clue = df.iloc[st.session_state.idx]

    # Category Display
    st.markdown(f'<div class="cat-box">{clue["category"]}</div>', unsafe_allow_html=True)
    st.write(f"### {clue['answer']}")

    # Study Tag Logic
    with st.expander(f"Study Tag: {st.session_state.current_tag}"):
        try:
            def_idx = TAGS.index(st.session_state.current_tag)
        except:
            def_idx = TAGS.index("Other")
        
        st.session_state.current_tag = st.selectbox("Change Tag:", TAGS, index=def_idx)

    st.caption(f"Season {clue['season']} | ${clue.get('clue_value', 400)}")

    # Reveal and Scoring
    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", use_container_width=True):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue['question']).upper()}")
        c1, c2 = st.columns(2)
        t = st.session_state.current_tag
        with c1:
            if st.button("✅ CORRECT", use_container_width=True):
                st.session_state.stats[t]["ok"] += 1
                st.session_state.stats[t]["total"] += 1
                get_next()
                st.rerun()
        with c2:
            if st.button("❌ MISSED", use_container_width=True):
                st.session_state.stats[t]["total"] += 1
                get_next()
                st.rerun()

# 7. Sidebar
st.sidebar.title("📊 Accuracy")
for tag, data in st.session_state.stats.items():
    if data["total"] > 0:
        score = (data["ok"] / data["total"]) * 100
        st.sidebar.write(f"**{tag}**")
        st.sidebar.progress(score / 100)
        st.sidebar.caption(f"{score:.0f}% accuracy ({data['total']} clues)")
