import json
import requests
import streamlit as st
from components.left_frame import render_sidebar
from utils.state_manager import init_session_state, reset_session_state

API_BASE_URL = "http://localhost:8002/api/v1"


class AgentType:
    ANSWER = "ANSWER_AGENT"
    HELPER = "HELPER_AGENT"

def on_help_click(help_text):
    st.session_state.ui_query = help_text
    st.session_state.app_mode = "next_query"


def process_event_data(event_data):

    # 이벤트 종료
    if event_data.get("type") == "end":
        return True

    # 새로운 메세지
    if event_data.get("type") == "update":
        data = event_data.get("data", {})

        role = data.get("role")
        response = data["response"]
        query = data["query"]
        messages = data["messages"]
        helps = data.get("helps", [])

        message = response

        if role == AgentType.ANSWER:
            st.subheader(f"질문: 『{query}』에 대한 AI 답변")
            avatar = "📣"
            with st.chat_message(role, avatar=avatar):
                st.markdown(response)

        elif role == AgentType.HELPER:
            avatar = "🔍"
            with st.chat_message(role, avatar=avatar):
                for u, help_text in enumerate(helps):
                    st.button(help_text, key=f"help_btn_{u}", on_click=on_help_click, args=(help_text,))
            
            st.session_state.app_mode = "results"
            st.session_state.viewing_history = False
            messages[-1]["query"] = query
            st.session_state.messages.extend(messages)
            st.session_state.helps = helps

    return False


def process_streaming_response(response):
    for chunk in response.iter_lines():
        if not chunk:
            continue
        line = chunk.decode("utf-8")
        if not line.startswith("data: "):
            continue

        data_str = line[6:]

        try:
            event_data = json.loads(data_str)
            is_complete = process_event_data(event_data)

            if is_complete:
                break

        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류: {e}")


def start_answer():
    query = st.session_state.ui_query
    with st.spinner("답변을 생성중입니다... 완료까지 잠시 기다려주세요."):
        data = {
            "query": query
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/workflow/answer/stream",
                json=data,
                stream=True,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return

            process_streaming_response(response)

        except requests.RequestException as e:
            st.error(f"API Request Error: {str(e)}")


def display_answer_results():
    for message in st.session_state.messages:
        role = message["role"]
        if role not in [
            AgentType.ANSWER,
            AgentType.HELPER,
        ]:
            continue

        st.subheader(f"질문: 『{message["query"]}』에 대한 AI 답변")
        if role == AgentType.ANSWER:
            avatar = "📣"
        elif role == AgentType.HELPER:
            avatar = "🔍"

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if role == AgentType.HELPER:
        st.session_state.answer_active = True
        st.session_state.viewing_history = False


def render_ui():
    st.set_page_config(page_title="국민연금 실무 전문가 AI 서비스", page_icon="🤖")
    st.title("국민연금 실무 전문가 AI 서비스")
    st.markdown(
        """
        ### 프로젝트 소개
        이 웹서비스는 국민연금 실무자가 관련 제도를 원활히 찾을 수 있도록 국민연금 실무자 메뉴얼을 참고하여 질문에 대한 답변을 생성합니다.
        답변이 완료된 이후엔 사용자가 궁금해할만한 관련된 추가 질문을 생성합니다.
        """
    )
    render_sidebar()
    current_mode = st.session_state.app_mode
    if current_mode == "answer":
        start_answer()
    elif current_mode == "results":
        display_answer_results()
    elif current_mode == "next_query":
        display_answer_results()
        start_answer()


if __name__ == "__main__":
    init_session_state()
    render_ui()