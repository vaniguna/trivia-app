import streamlit as st
import pandas as pd
import random
import glob
import re

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- UNIVERSAL CATEGORY ENGINE ---
# This maps messy board categories into the granular study topics you requested
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

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .category-box {
        background-color: #060ce9;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
    }
    .category-text {
        font-family: 'Arial Black', sans-serif;
        font-weight: bold;
        font-size: 28px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    /* Neutral Slate Reveal Button */
    div.stButton > button:first-child {
        background-color: #475569;
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_tag_data():
    files = glob.glob("*.tsv")
    if not files: return None
    all_df = pd.concat([pd.read_csv(f, sep='\t', low_memory=False) for f in files])
    all_df = all_df.dropna(subset=['answer', 'question'])
    return all_df.sample(frac=1).reset_index(drop=True)

df = load_and_tag_data()

# --- STATE ---
if 'stats' not in st.session_state:
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in UNIVERSAL_MAP}
    st.session_state.stats["Other"] = {"correct": 0, "total": 0}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False

def get_next():
    st.session_state.idx = random.randint(0, len(df)-1)
    st.session_state.show = False

# --- UI ---
if df is not None:
    clue = df.iloc[st.session_state.idx]
    u_cat = identify_universal_cat(clue)

    st.markdown(f'<div class="category-box"><div class="category-text">{clue["category"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f"### {clue['answer']}")
    st.caption(f"Study Tag: **{u_cat}** | Season {clue.get('season', '??')}")

    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", use_container_width=True):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue['question']).upper()}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ CORRECT"):
                st.session_state.stats[u_cat]["correct"] += 1
                st.session_state.stats[u_cat]["total"] += 1
                get_next(); st.rerun()
        with c2:
            if st.button("❌ MISSED"):
                st.session_state.stats[u_cat]["total"] += 1
                get_next(); st.rerun()

# --- SIDEBAR STATS ---
st.sidebar.title("📊 Weakness Tracker")
for cat, data in st.session_state.stats.items():
    if data["total"] > 0:
        acc = (data["correct"] / data["total"]) * 100
        st.sidebar.write(f"**{cat}**: {acc:.0f}% accuracy ({data['total']} seen)")
        st.sidebar.progress(acc / 100)
