import streamlit as st
import pandas as pd
import random
import glob

st.set_page_config(page_title="J! Super-Archive", page_icon="🎓")

# --- DATA LOADING (Optimized for 10+ Seasons) ---
@st.cache_data(show_spinner="Loading the Archive...")
def load_all_seasons():
    files = glob.glob("*.tsv")
    if not files:
        return None
    
    all_data = []
    for f in files:
        try:
            # Low_memory=False helps with large datasets
            temp_df = pd.read_csv(f, sep='\t', low_memory=False)
            
            # Extract season from filename if missing in columns
            if 'season' not in temp_df.columns:
                s_num = "".join(filter(str.isdigit, f))
                temp_df['season_num'] = s_num if s_num else "??"
            else:
                temp_df['season_num'] = temp_df['season']
                
            all_data.append(temp_df)
        except:
            continue
            
    if not all_data:
        return None
        
    df = pd.concat(all_data, ignore_index=True)
    # Filter out clues that are missing text or are 'Media' clues
    df = df.dropna(subset=['answer', 'question'])
    return df

df = load_all_seasons()

# --- STATE MANAGEMENT ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.score = 0

def get_next():
    st.session_state.idx = random.randint(0, len(df) - 1)
    st.session_state.show = False

# --- UI ---
st.title("🏆 J! Championship Trainer")

if df is None:
    st.error("No data files found! Upload your .tsv files (Seasons 30-41) to GitHub.")
else:
    if st.session_state.idx == 0 and not st.session_state.show:
        get_next()

    clue = df.iloc[st.session_state.idx]
    
    st.info(f"CATEGORY: {str(clue['category']).upper()}")
    st.markdown(f"### {clue['answer']}")
    
    # Season & Value (The requested unobtrusive tag)
    st.caption(f"Value: ${clue.get('clue_value', 400)} | Season {clue['season_num']}")

    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", type="primary"):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue['question']).upper()}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ CORRECT"):
                # Ensure we add a valid integer to the score
                val = str(clue.get('clue_value', '400')).replace('$', '').replace(',', '')
                try:
                    st.session_state.score += int(val)
                except:
                    st.session_state.score += 400
                get_next()
                st.rerun()
        with col2 if 'col2' in locals() else c2:
            if st.button("❌ MISSED"):
                get_next()
                st.rerun()

st.sidebar.metric("Career Earnings", f"${st.session_state.score:,}")
st.sidebar.write(f"Total Clues in Bank: **{len(df):,}**")
