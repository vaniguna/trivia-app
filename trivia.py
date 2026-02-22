import streamlit as st
import requests

st.set_page_config(page_title="Jeopardy! Pro", page_icon="🏆")

# Initialize Session State
if 'clue' not in st.session_state:
    st.session_state.clue = None
    st.session_state.show_answer = False
    st.session_state.score = 0

def get_new_clue():
    try:
        # Step 1: Attempt to get a real clue
        response = requests.get("https://cluebase.com/api/clues/random", timeout=7)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and data.get('data'):
                st.session_state.clue = data['data'][0]
                st.session_state.show_answer = False
                return
        
        # Step 2: Fallback if API is up but empty/errored
        st.warning("API responded but found no clues. Using a backup training clue.")
        st.session_state.clue = {
            "category": "BACKUP TRAINING",
            "clue": "This 'Great' lake is the only one located entirely within the U.S. border.",
            "response": "Lake Michigan",
            "value": 200
        }
    except Exception as e:
        # Step 3: Emergency Fallback for timeouts/crashes
        st.error(f"Connection Error: {e}")
        st.session_state.clue = {
            "category": "OFFLINE MODE",
            "clue": "To test the app, what is the chemical symbol for Tungsten?",
            "response": "W",
            "value": 1000
        }

st.title("🏆 Jeopardy! Fast-Track")

# UI Logic
if st.session_state.clue is None:
    if st.button("START TRAINING", type="primary"):
        get_new_clue()
        st.rerun()
else:
    c = st.session_state.clue
    st.info(f"CATEGORY: {c['category'].upper()}")
    st.subheader(c['clue'])
    st.caption(f"Value: ${c.get('value') or 'N/A'}")

    if not st.session_state.show_answer:
        if st.button("REVEAL ANSWER", type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {c['response'].upper()}")
        if st.button("NEXT CLUE ⏩"):
            get_new_clue()
            st.rerun()

st.sidebar.metric("Bank", f"${st.session_state.score}")
