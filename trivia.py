import streamlit as st
import requests

st.set_page_config(page_title="Jeopardy! Trainer", page_icon="🏆")

# Initialize Session State
if 'clue' not in st.session_state:
    st.session_state.clue = None
    st.session_state.show_answer = False
    st.session_state.score = 0

def get_new_clue():
    # jService uses a slightly different URL and returns a LIST of 1 item
    url = "https://jservice.io/api/random"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()[0] # jService returns [ {clue_data} ]
            st.session_state.clue = data
            st.session_state.show_answer = False
        else:
            st.error("jService is having a moment. Try clicking again.")
    except Exception as e:
        st.error(f"Connection failed: {e}")

st.title("🏆 Jeopardy! Mobile")

if st.session_state.clue is None:
    if st.button("GET RANDOM CLUE", type="primary"):
        get_new_clue()
        st.rerun()
else:
    c = st.session_state.clue
    # Mapping jService's specific names (they use 'question' instead of 'clue')
    category = c.get('category', {}).get('title', 'General').upper()
    question_text = c.get('question', 'No text found')
    answer_text = c.get('answer', 'No answer found')
    value = c.get('value') or 400

    st.info(f"CATEGORY: {category}")
    st.subheader(question_text)
    st.write(f"Value: ${value}")

    if not st.session_state.show_answer:
        if st.button("REVEAL ANSWER", type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.success(f"ANSWER: {answer_text.upper()}")
        if st.button("NEXT CLUE ⏩"):
            get_new_clue()
            st.rerun()

st.sidebar.metric("Bank", f"${st.session_state.score}")
