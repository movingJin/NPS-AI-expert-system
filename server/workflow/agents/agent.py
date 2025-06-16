from langchain.schema import HumanMessage, SystemMessage, AIMessage
from utils.config import get_llm
from workflow.state import AnswerState, AgentType
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langfuse.callback import CallbackHandler
from retrieval.search_service import get_search_chain, get_next_query


class AgentState(TypedDict):
    answer_state: Dict[str, Any]  # 전체 답변 상태
    messages: List[BaseMessage]  # LLM에 전달할 메시지
    response: str  # LLM 응답
    helps: List[str]


class Agent(ABC):
    def __init__(
        self, role: str, session_id: str = None
    ):
        self.role = role
        self._setup_graph()  # 그래프 설정
        self.session_id = session_id  # langfuse 세션 ID

    def _setup_graph(self):
        # 그래프 생성
        workflow = StateGraph(AgentState)

        # 노드 추가
        workflow.add_node("generate_response", self._generate_response)  # 응답 생성
        workflow.add_node("update_state", self._update_state)  # 상태 업데이트

        workflow.add_edge("generate_response", "update_state")

        workflow.set_entry_point("generate_response")
        workflow.add_edge("update_state", END)

        # 그래프 컴파일
        self.graph = workflow.compile()


    # LLM 호출
    @abstractmethod
    def _generate_response(self, state: AgentState) -> AgentState:
        pass

    # 상태 업데이트
    def _update_state(self, state: AgentState) -> AgentState:
        answer_state = state["answer_state"]
        response = state["response"]
        helps = state["helps"]

        new_answer_state = answer_state.copy()
        if self.role == AgentType.ANSWER:
            new_answer_state["messages"].append(
                {"role": self.role, "content": response, "helps": []}
            )
        elif self.role == AgentType.HELPER:
            new_answer_state["messages"][-1]["helps"] = helps
        new_answer_state["prev_node"] = self.role
        return {**state, "answer_state": new_answer_state}


    def run(self, state: AnswerState) -> AnswerState:
        agent_state = AgentState(
            answer_state=state, messages=[], response="", helps=[]
        )

        # 내부 그래프 실행
        langfuse_handler = CallbackHandler(session_id=self.session_id)
        result = self.graph.invoke(
            agent_state, config={"callbacks": [langfuse_handler]}
        )

        return result["answer_state"]