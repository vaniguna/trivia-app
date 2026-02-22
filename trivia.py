import streamlit as st
import pandas as pd
import random
import glob

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- CUSTOM CSS FOR THE "BOARD" LOOK ---
st.markdown("""
    <style>
    .category-box {
        background-color: #060ce9;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 4px solid #d1a105;
        margin-bottom: 25px;
    }
    .category-text {
        font-family: 'ITC Korinna', 'Arial Black', sans-serif;
        font-weight: bold;
        font-size: 28px;
        letter-spacing: 2px;
        text-shadow: 2px 2px #000;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data(show_spinner="Shuffling the Archive...")
def load_all_seasons():
    files = glob.glob("*.tsv")
    if not files:
        return None
    
    all_data = []
    for f in files:
        try:
            temp_df = pd.read_csv(f, sep='\t', low_memory=False)
            # Ensure season mapping
            s_num = "".join(filter(str.isdigit, f))
            temp_df['season_num'] = s_num if s_num else "Unknown"
            all_data.append(temp_df)
        except:
            continue
            
    if not all_data:
        return None
        
    df = pd.concat(all_data, ignore_index=True)
    df = df.dropna(subset=['answer', 'question'])
    # Shuffle the entire dataframe once on load to ensure cross-season variety
    return df.sample(frac=1).reset_index(drop=True)

df = load_all_seasons()

# --- STATE MANAGEMENT ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.score = 0

def get_next():
    # Pick a random index from the already shuffled dataframe
    st.session_state.idx = random.randint(0, len(df) - 1)
    st.session_state.show = False

# --- UI ---
if df is None:
    st.error("No .tsv files detected! Ensure your season files are in your GitHub folder.")
else:
    # Handle the very first load
    if st.session_state.idx == 0 and not st.session_state.show:
        get_next()

    clue = df.iloc[st.session_state.idx]
    
    # 1. THE CATEGORY HEADER (Fixed HTML tag)
    st.markdown(f"""
        <div class="category-box">
            <div class="category-text">{str(clue['category']).upper()}</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. THE CLUE
    st.markdown(f"### {clue['answer']}")
    st.caption(f"Value: ${clue.get('clue_value', 400)} | Season {clue['season_num']}")

    # 3. INTERACTION
    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", type="primary", use_container_width=True):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue['question']).upper()}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ I GOT IT", use_container_width=True):
                val = str(clue.get('clue_value', '400')).replace('$', '').replace(',', '')
                st.session_state.score += int(val) if val.isdigit() else 400
                get_next()
                st.rerun()
        with c2:
            if st.button("❌ I MISSED IT", use_container_width=True):
                get_next()
                st.rerun()

st.sidebar.metric("Career Earnings", f"${st.session_state.score:,}")
st.sidebar.write(f"Total Bank: **{len(df):,} clues**")
if st.sidebar.button("Force Global Reshuffle"):
    st.cache_data.clear()
    st.rerun()
