import streamlit as st


def init_session_state():
    if "app_mode" not in st.session_state:
        reset_session_state()


def reset_session_state():
    st.session_state.app_mode = False
    st.session_state.viewing_history = False
    st.session_state.loaded_answer_id = None
    st.session_state.setdefault = ""
    st.session_state.messages = []
    st.session_state.helps = []


def set_answer_to_state(query, messages, answer_id, helps):
    st.session_state.app_mode = True
    st.session_state.messages = messages
    st.session_state.viewing_history = True
    st.session_state.answer_query = query
    st.session_state.loaded_answer_id = answer_id
    st.session_state.helps = helps