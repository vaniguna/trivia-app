import streamlit as st
import pandas as pd
import random
import glob
import re

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- UNIVERSAL CATEGORY ENGINE ---
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

def identify_universal_cat(row):
    text = f"{row['category']} {row['answer']}".lower()
    for label, pattern in UNIVERSAL_MAP.items():
        if re.search(pattern, text):
            return label
    return "Other"

# --- CUSTOM CSS (Updated: Flat Blue, No Gold, Slate Reveal) ---
st.markdown("""
    <style>
    .category-box {
        background-color: #060ce9;
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
        /* Removed gold border for cleaner look */
    }
    .category-text {
        font-family: 'Arial Black', sans-serif;
        font-weight: bold;
        font-size: 26px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    /* Slate Grey Reveal Button to prevent clashing */
    div.stButton > button:first-child {
        background-color: #475569 !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Shuffling Archive...")
def load_all_data():
    files = glob.glob("*.tsv")
    if not files: return None
    all_data = []
    for f in files:
        try:
            temp_df = pd.read_csv(f, sep='\t', low_memory=False)
            s_num = "".join(filter(str.isdigit, f))
            temp_df['season_num'] = s_num if s_num else "Unknown"
            all_data.append(temp_df)
        except: continue
    if not all_data: return None
    df = pd.concat(all_data, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

df = load_all_data()

# --- STATE MANAGEMENT ---
if 'stats' not in st.session_state:
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in UNIVERSAL_MAP}
    st.session_state.stats["Other"] = {"correct": 0, "total": 0}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.
