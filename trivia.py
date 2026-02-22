import streamlit as st
import requests

st.set_page_config(page_title="Jeopardy! Mobile", page_icon="🏆")

# Initialize Session State
if 'clue' not in st.session_state:
    st.session_state.clue = None
    st.session_state.show_answer = False
    st.session_state.score = 0

def get_new_clue():
    st.session_state.show_answer = False
    # API 1: jService (Real Jeopardy clues)
    try:
        r = requests.get("https://jservice.io/api/random", timeout=5)
        if r.status_code == 200:
            data = r.json()[0]
            st.session_state.clue = {
                "question": data.get('question', 'No question text provided'),
                "answer": data.get('answer', 'No answer provided'),
                "category": data.get('category', {}).get('title', 'GENERAL'),
                "value": data.get('value') or 400
            }
            return
    except:
        pass

    # API 2: OpenTDB (Backup high-quality trivia)
    try:
        r = requests.get("https://opentdb.com/api.php?amount=1&type=multiple", timeout=5)
        if r.status_code == 200:
            data = r.json()['results'][0]
            st.session_state.clue = {
                "question": data['question'],
                "answer": data['correct_answer'],
                "category": data['category'],
                "value": 500
            }
            return
    except:
        st.error("All trivia servers are busy. Please try again in a moment.")

st.title("🏆 Jeopardy! Mobile")

if st.session_state.clue is None:
    if st.button("GET RANDOM CLUE", type="primary"):
        get_new_clue()
        st.rerun()
else:
    c = st.session_state.clue
    
    # Safe Display Logic
    cat_text = str(c.get('category', 'GENERAL')).upper()
    
    st.info(f"CATEGORY: {cat_text}")
    # Using markdown to handle any HTML symbols in the questions
    st.markdown(f"### {c.get('question')}")
    st.write(f"Value: ${c.get('value')}")

    if not st.session_state.show_answer:
        if st.button("REVEAL ANSWER", type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        ans_text = str(c.get('answer', 'N/A')).upper()
        st.success(f"ANSWER: {ans_text}")
        
        if st.button("NEXT CLUE ⏩"):
            get_new_clue()
            st.rerun()

st.sidebar.metric("Bank", f"${st.session_state.score}")
