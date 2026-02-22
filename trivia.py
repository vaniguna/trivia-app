import streamlit as st
import pandas as pd
import random
import glob
import re
import os

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- CUSTOM CSS (Flat Blue Header, Slate Reveal Button) ---
st.markdown("""
    <style>
    .category-box {
        background-color: #060ce9;
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
    }
    .category-text {
        font-family: 'Arial Black', sans-serif;
        font-weight: bold;
        font-size: 26px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    /* Neutral Slate Reveal Button */
    div.stButton > button:first-child {
        background-color: #475569 !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- UNIVERSAL CATEGORY MAPPING ---
UNIVERSAL_MAP = {
    "Vietnam War": r"vietnam|saigon|hanoi|viet cong",
    "Revolutionary War": r"revolutionary war|lexington|saratoga|yorktown|cornwallis",
    "Canadian History": r"canada|ottawa|toronto|quebec|hudson's bay|prime minister",
    "European Mountains": r"alps|pyrenees|carpathians|caucasus|mont blanc|matterhorn",
    "Asian Rivers": r"mekong|yangtze|ganges|indus|yellow river|brahmaputra",
    "U.S. Presidents": r"president|white house|potus",
    "Shakespeare": r"shakespeare|hamlet|macbeth|othello|bard",
    "Science": r"molecule|element|physics|biology|chemistry"
}

def get_study_tag(row):
    text = f"{row.get('category', '')} {row.get('answer', '')}".lower()
    for label, pattern in UNIVERSAL_MAP.items():
        if re.search(pattern, text):
            return label
    return "Other"

# --- DATA LOADING ---
@st.cache_data(show_spinner="Shuffling the Archive...")
def load_all_data():
    files = glob.glob("*.tsv")
    if not files:
        return None
    
    all_dfs = []
    for f in files:
        try:
            temp = pd.read_csv(f, sep='\t', low_memory=False)
            # Find the season number from the filename
            s_match = re.search(r'\d+', f)
            temp['season_num'] = s_match.group() if s_match else "Unknown"
            all_dfs.append(temp)
        except:
            continue
            
    if not all_dfs:
        return None
        
    df = pd.concat(all_dfs, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

df = load_all_data()

# --- INITIALIZE SESSION STATE ---
if 'stats' not in st.session_state:
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in UNIVERSAL_MAP}
    st.session_state.stats["Other"] = {"correct": 0, "total": 0}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.current_tag = "Other"

# Helper to pick a new random clue
def shuffle_new():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df) - 1)
        st.session_state.show = False
        # Pre-tag the next clue
        row = df.iloc[st.session_state.idx]
        st.session_state.current_tag = get_study_tag(row)

# --- MAIN APP ---
if df is None:
    st.error("🚨 NO DATA FOUND. Please ensure your .tsv files are in the GitHub folder.")
else:
    # Trigger first clue on very first run
    if st.session_state.idx == 0 and not st.session_state.show and 'init' not in st.session_state:
        st.session_state.init = True
        shuffle_new()

    clue = df.iloc[st.session_state.idx]

    # Category Box
    st.markdown(f'<div class="category-box"><div class="category-text">{clue["category"]}</div></div>', unsafe_allow_html=True)
    
    # The Clue Text
    st.markdown(f"### {clue['answer']}")
    
    # Manual Tag Correction
    with st.expander(f"Study Tag: {st.session_state.current_tag}"):
        all_labels = list(st.session_state.stats.keys())
        # Safety check for index
        try:
            start_idx = all_labels.index(st.session_state.current_tag)
        except:
            start_idx = all_labels.index("Other")
            
        new_label = st.selectbox("Correct this tag:", options=all_labels, index=start_idx)
        st.session_state.current_tag = new_label

    st.caption(f"Value: ${clue.get('clue_value', 400)} | Season {clue['season_num']}")

    # Reveal Logic
    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", use_container_width=True):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue['question']).upper()}")
        
        c1, c2 = st.columns(2)
        tag = st.session_state.current_tag
        with c1:
            if st.button("✅ I GOT IT", use_container_width=True):
                st.session_state.stats[tag]["correct"] += 1
                st.session_state.stats[tag]["total"] += 1
                shuffle_new()
                st.rerun()
        with c2:
            if st.button("❌ I MISSED IT", use_container_width=True):
                st.session_state.stats[tag]["total"] += 1
                shuffle_new()
                st.rerun()

# --- SIDEBAR WEAKNESS TRACKER ---
st.sidebar.title("📊 Study Tracker")
for cat, data in st.session_state.stats.items():
    if data["total"] > 0:
        accuracy = (data["correct"] / data["total"]) * 100
        st.sidebar.write(f"**{cat}**")
        st.sidebar.caption(f"{accuracy:.0f}% accuracy ({data['total']} seen)")
        st.sidebar.progress(accuracy / 100)
        st.sidebar.divider()
