import streamlit as st
import pandas as pd
import random
import glob
import re
import os

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- CUSTOM CSS ---
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
        font-size: 24px;
        text-transform: uppercase;
    }
    div.stButton > button:first-child {
        background-color: #475569 !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CATEGORY ENGINE ---
UNIVERSAL_MAP = {
    "Vietnam War": r"vietnam|saigon|hanoi",
    "Revolutionary War": r"revolutionary war|saratoga|yorktown",
    "Canadian History": r"canada|ottawa|toronto|quebec",
    "European Mountains": r"alps|pyrenees|mont blanc",
    "Asian Rivers": r"mekong|yangtze|ganges",
    "U.S. Presidents": r"president|white house",
    "Shakespeare": r"shakespeare|hamlet|macbeth",
    "Science": r"molecule|physics|biology|chemistry"
}

def get_tag(row):
    text = f"{row.get('category', '')} {row.get('answer', '')}".lower()
    for label, pattern in UNIVERSAL_MAP.items():
        if re.search(pattern, text):
            return label
    return "Other"

# --- DATA LOADING ---
@st.cache_data(show_spinner="Loading Season Data...")
def load_data():
    files = glob.glob("*.tsv")
    if not files:
        return None
    all_chunks = []
    for f in files:
        try:
            temp = pd.read_csv(f, sep='\t', low_memory=False)
            s_match = re.search(r'\d+', f)
            temp['season_num'] = s_match.group() if s_match else "??"
            all_chunks.append(temp)
        except:
            continue
    if not all_chunks:
        return None
    df = pd.concat(all_chunks, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

# --- EXECUTION ---
df = load_data()

# Initialize State
if 'stats' not in st.session_state:
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in UNIVERSAL_MAP}
    st.session_state.stats["Other"] = {"correct": 0, "total": 0}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.tag = "Other"
    st.session_state.ready = False

def next_clue():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df) - 1)
        st.session_state.show = False
        row = df.iloc[st.session_state.idx]
        st.session_state.tag = get_tag(row)
        st.session_state.ready = True

if df is None:
    st.error("No .tsv files found. Check your GitHub repository.")
else:
    if not st.session_state.ready:
