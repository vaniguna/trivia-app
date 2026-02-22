import streamlit as st
import pandas as pd
import random
import glob
import re
import os

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓")

# --- DEBUGGING: Show files in directory to screen if logs are empty ---
with st.sidebar:
    if st.checkbox("Debug: Show Files"):
        st.write("Current Directory Files:", os.listdir("."))

# --- DATA LOADING ---
@st.cache_data(show_spinner="Loading Data...")
def load_all_data():
    # Force search in current directory
    path = os.path.join(os.getcwd(), "*.tsv")
    files = glob.glob(path)
    
    if not files:
        # Fallback check for standard relative path
        files = glob.glob("*.tsv")
        
    if not files:
        return None
        
    all_data = []
    for f in files:
        try:
            # Explicitly setting low_memory=False to prevent silent crashes
            temp_df = pd.read_csv(f, sep='\t', low_memory=False)
            
            # Extract Season Number
            s_match = re.search(r'\d+', f)
            temp_df['season_num'] = s_match.group() if s_match else "Unknown"
            
            all_data.append(temp_df)
        except Exception as e:
            st.error(f"Error loading {f}: {e}")
            continue
            
    if not all_data:
        return None
        
    df = pd.concat(all_data, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

# Try to load the data
df = load_all_data()

# --- APP START ---
if df is None:
    st.error("🚨 No .tsv files found in the repository!")
    st.info("Check your GitHub: Are 'season40.tsv' and 'season41.tsv' in the root folder?")
    st.stop() # Prevents further execution to stop the "blank screen"

# --- REST OF THE LOGIC ---
if 'idx' not in st.session_state:
    st.session_state.idx = random.randint(0, len(df) - 1)
    st.session_state.show = False
    st.session_state.score = 0

# (Your UI code below this...)
st.title("🏆 Jeopardy! Pro Trainer")
clue = df.iloc[st.session_state.idx]

st.info(f"CATEGORY: {clue['category']}")
st.write(f"### {clue['answer']}")
st.caption(f"Season: {clue['season_num']}")

if st.button("REVEAL"):
    st.success(f"RESPONSE: {clue['question']}")
