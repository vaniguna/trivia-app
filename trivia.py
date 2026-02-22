import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- DATA LOADING ---
@st.cache_data
def load_archive():
    # Looks for the file in the same directory as this script
    file_path = 'season41.tsv'
    
    if not os.path.exists(file_path):
        return None
    
    try:
        # JWolle dataset uses Tab separation
        df = pd.read_csv(file_path, sep='\t')
        
        # Mapping jwolle1 column names to our app logic:
        # 'answer' = The Clue on the board
        # 'question' = The Correct Response (e.g., "What is...")
        # 'category' = The Category
        # 'clue_value' = The Dollar amount
        return df.dropna(subset=['answer', 'question'])
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

df = load_archive()

# --- INITIALIZE SESSION STATE ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.score = 0

def get_next_clue():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df) - 1)
        st.session_state.show = False

# --- MAIN UI ---
st.title("🏆 Jeopardy! Season 41 Trainer")

if df is None:
    st.error("❌ 'season41.tsv' not found!")
    st.info("Please ensure 'season41.tsv' is uploaded to your GitHub repository in the same folder as this script.")
else:
    # Set the first clue if it's the start of the session
    if st.session_state.idx == 0 and not st.session_state.show:
        get_next_clue()

    clue_data = df.iloc[st.session_state.idx]
    
    # Extracting and cleaning data
    # Note: In the TSV, 'answer' is the text the host reads
    clue_text = str(clue_data['answer']) 
    correct_response = str(clue_data['question'])
    category = str(clue_data.get('category', 'UNCATEGORIZED')).upper()
    value = clue_data.get('clue_value', 400)

    # Display Board
    st.info(f"CATEGORY: {category}")
    st.markdown(f"### {clue_text}")
    st.caption(f"Clue Value: ${value}")

    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", type="primary"):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"CORRECT RESPONSE: {correct_response.upper()}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ I WAS RIGHT"):
                st.session_state.score += int(value or 400)
                get_next_clue()
                st.rerun()
        with col2:
            if st.button("❌ I WAS WRONG"):
                st.session_state.score -= int(value or 400)
                get_next_clue()
                st.rerun()

st.sidebar.metric("Career Earnings", f"${st.session_state.score}")
if st.sidebar.button("Reset Game"):
    st.session_state.score = 0
    get_next_clue()
    st.rerun()
