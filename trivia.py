import streamlit as st
import pandas as pd
import random
import glob
import re
import os

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- 1. BOARD CATEGORY ENGINE ---
# This now looks specifically at the 'category' field from the board
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
    # CHANGED: Now only pulls from the actual board category name
    category_text = str(row.get('category', '')).lower()
    
    for label, pattern in UNIVERSAL_MAP.items():
        if re.search(pattern, category_text):
            return label
    return "Other"

# --- 2. CUSTOM CSS ---
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
        text-transform: uppercase;
    }
    div.stButton > button:first-child {
        background-color: #475569 !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING (SEASON CAPTURE) ---
@st.cache_data
def load_all_seasons():
    files = glob.glob("*.tsv")
    if not files:
        return None
    
    all_chunks = []
    for f in files:
        try:
            temp_df = pd.read_csv(f, sep='\t', low_memory=False)
            s_match = re.search(r'\d+', f)
            temp_df['season'] = s_match.group() if s_match else "??"
            all_chunks.append(temp_df)
        except:
            continue
            
    if not all_chunks:
        return None
    
    df = pd.concat(all_chunks, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

df = load_all_seasons()

# --- 4. STATE MANAGEMENT ---
if 'stats' not in st.session_state:
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in UNIVERSAL_MAP}
    st.session_state.stats["Other"] = {"correct": 0, "total": 0}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.current_tag = "Other"
    st.session_state.initialized = False

def get_next():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df) - 1)
        st.session_state.show = False
        row = df.iloc[st.session_state.idx]
        st.session_state.current_tag = identify_universal_cat(row)
        st.session_state.initialized = True

# --- 5. MAIN UI ---
if df is None:
    st.error("No .tsv files found in the folder!")
else:
    if not st.session_state.initialized:
        get_next()

    clue = df.iloc[st.session_state.idx]
    u_cat = st.session_state.current_tag

    st.markdown(f'<div class="category-box"><div class="category-text">{clue["category"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f"### {clue['answer']}")
    st.caption(f"Study Tag: **{u_cat}** | Season {clue['season']} | ${clue.get('clue_value', 400)}")

    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", use_container_width=True):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue['question']).upper()}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ I GOT IT", use_container_width=True):
                st.session_state.stats[u_cat]["correct"] += 1
                st.session_state.stats[u_cat]["total"] += 1
                get_next()
                st.rerun()
        with c2:
            if st.button("❌ I MISSED IT", use_container_width=True):
                st.session_state.stats[u_cat]["total"] += 1
                get_next()
                st.rerun()

# --- 6. SIDEBAR (WEAKNESS TRACKER & REFRESH) ---
st.sidebar.title("📊 Training Progress")

# Total Score Metric
total_correct = sum(d["correct"] for d in st.session_state.stats.values())
total_seen = sum(d["total"] for d in st.session_state.stats.values())
st.sidebar.metric("Total Correct Clues", f"{total_correct} / {total_seen}")

st.sidebar.divider()
st.sidebar.subheader("Weakness Tracker")
for cat, data in st.sidebar.container().items(): # Iterating through categories
    # Sort categories to show ones you have seen first
    sorted_stats = dict(sorted(st.session_state.stats.items(), key=lambda item: item[1]['total'], reverse=True))

for cat, data in sorted_stats.items():
    if data["total"] > 0:
        acc = (data["correct"] / data["total"]) * 100
        st.sidebar.write(f"**{cat}**")
        st.sidebar.progress(acc / 100)
        st.sidebar.caption(f"{acc:.0f}% accuracy ({data['total']} clues seen)")

st.sidebar.divider()
if st.sidebar.button("🔄 REFRESH ALL STATS", use_container_width=True):
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in UNIVERSAL_MAP}
    st.session_state.stats["Other"] = {"correct": 0, "total": 0}
    st.rerun()
