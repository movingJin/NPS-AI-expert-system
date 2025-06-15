import streamlit as st
from typing import Dict, Any


def render_input_form():
    with st.form("asnwer_form", border=False):
        if "ui_query" not in st.session_state:
            st.session_state.ui_query = "2025년 6월 기준, 현재 나이 35세의 사람의 노령연금 수급연령을 알려줘."
            
        st.markdown(
            "<label for='custom_ui_query' style='font-size: 15px; font-weight: 700;'>"
            "국민연금제도에 대한 질문을 입력해주세요:"
            "</label>",
            unsafe_allow_html=True
        )
        st.text_area(
            label="",
            key="ui_query",
        )

        st.form_submit_button(
            "제출",
            on_click=lambda: st.session_state.update({"app_mode": "answer"}),
        )


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        render_input_form()