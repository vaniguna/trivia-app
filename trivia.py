import streamlit as st
import requests
import html

# --- CONFIG ---
st.set_page_config(page_title="Jeopardy! Pro", page_icon="🏆")

# --- INITIALIZE STATE ---
if 'clues' not in st.session_state:
    st.session_state.clues = []
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.show_answer = False

def fetch_clues():
    # Using a backup API just in case Cluebase is slow
    url = "https://cluebase.com/api/clues/random?limit=10"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            st.session_state.clues = res.json().get('data', [])
            st.session_state.current_idx = 0
            st.session_state.show_answer = False
        else:
            st.error(f"API Error: {res.status_code}")
    except Exception as e:
        st.error(f"Connection Failed: {e}")

# --- UI ---
st.title("🏆 Jeopardy! Trainer")

if not st.session_state.clues:
    st.write("Click below to pull real clues from the archive.")
    if st.button("Start Training", type="primary"):
        fetch_clues()
        st.rerun()
else:
    # Safety check for index
    if st.session_state.current_idx >= len(st.session_state.clues):
        st.success("Set complete!")
        if st.button("Get More Clues"):
            fetch_clues()
            st.rerun()
    else:
        clue = st.session_state.clues[st.session_state.current_idx]
        
        # Display Info
        st.info(f"CATEGORY: {clue.get('category', 'UNKNOWN').upper()}")
        st.subheader(clue.get('clue', 'No clue text found'))
        st.write(f"Value: ${clue.get('value', 200)}")

        if not st.session_state.show_answer:
            if st.button("Reveal Answer", type="primary"):
                st.session_state.show_answer = True
                st.rerun()
        else:
            st.success(f"ANSWER: {clue.get('response', 'No response found')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Correct"):
                    st.session_state.score += (clue.get('value') or 200)
                    st.session_state.current_idx += 1
                    st.session_state.show_answer = False
                    st.rerun()
            with col2:
                if st.button("❌ Incorrect"):
                    st.session_state.score -= (clue.get('value') or 200)
                    st.session_state.current_idx += 1
                    st.session_state.show_answer = False
                    st.rerun()

st.sidebar.metric("Total Score", f"${st.session_state.score}")
