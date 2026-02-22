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
            s_match = re.search(r'\d+', f)
            temp['season_num'] = s_match.group() if s_match else "Unknown"
            all_dfs.append(temp)
        except:
            continue
            
    if not all_dfs:
        return None
        
    df = pd.concat(all_dfs, ignore_index=True)
    # Clean data: remove rows with empty answers or questions
