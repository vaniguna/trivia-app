import streamlit as st
import pandas as pd
import random
import glob
import re
import os

st.set_page_config(page_title="Jeopardy! Pro", page_icon="🏆", layout="centered")

# --- 1. BOARD CATEGORY ENGINE ---
# Mapping board categories to study tags strictly by category name
TAG_MAP = {
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
    # Strictly works off the actual board category
    cat_text = str(row.get('category', '')).lower()
    for label, pattern in TAG_MAP.items():
        if re.search(pattern, cat_text):
            return label
    return "Other"

# --- 2. STABLE DATA LOADER ---
@st.cache_data
def load_local_data():
    files = glob.glob("*.tsv")
    if not files:
        return None
    
    chunks = []
    for f in files:
        try:
            temp = pd.read_csv(f, sep='\t', low_memory=False)
            # Pull season number from filename (e.g., season40.tsv)
            match = re.search(r'\d+', f)
            temp['season'] = match.group() if match else "??"
            chunks.append(temp)
        except:
            continue
    
    if not chunks:
        return None
    full_df = pd.concat(chunks, ignore_index=True)
    return full_df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

df = load_local_data()

# --- 3. STATE INITIALIZATION ---
if 'stats' not in st.session_state:
    st.session_state.stats = {cat: {"ok": 0, "total": 0} for cat in TAG_MAP}
    st.session_state.stats["Other"] = {"ok": 0, "total": 0}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.reveal = False
    st.session_state.current_tag = "Other"

def next_clue():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df)-1)
        st.session_state.reveal = False
        row = df.iloc[st.session_state.idx]
        st.session_state.current_tag = get_study_tag(row)

# --- 4. UI AND CLUE DISPLAY ---
if df is None:
    st.error("No clue files found! Please ensure your .tsv files are in the same folder.")
else:
    # Set initial clue
    if st.session_state.idx == 0 and not st.session_state.reveal and 'init' not in st.session_state:
        st.session_state.init = True
        next_clue()

    clue = df.iloc[st.session_state.idx]
    tag = st.session_state.current_tag

    # Styling the header
    st.markdown(f"""
        <div style="background-color: #060ce9; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h1 style="margin:0; font-family: sans-serif; text-transform: uppercase;">{clue['category']}</h1>
        </div>
    """, unsafe_allow_html=True)

    st.subheader(clue['answer'])
    st.caption(f"Study Tag: **{tag}** | Season {clue['season']} | ${clue.get('clue_value', 400)}")

    if not st.session_state.reveal:
        if st.button("REVEAL RESPONSE", use_container_width=True, type="primary"):
