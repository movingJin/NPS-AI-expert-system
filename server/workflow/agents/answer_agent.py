from workflow.agents.agent import Agent, AgentState
from workflow.state import AnswerState, AgentType
from typing import List, Dict, Any, TypedDict
from retrieval.search_service import get_search_chain, get_next_query


class AnswerAgent(Agent):
    def __init__(
        self, session_id: str = None
    ):
        self.role = AgentType.ANSWER
        self._setup_graph()  # 그래프 설정
        self.session_id = session_id  # langfuse 세션 ID

    def _generate_response(self, state: AgentState) -> AgentState:
        query = state["answer_state"]["query"]
        chain = get_search_chain()
        response = chain.invoke(query)
            
        return {**state, "response": response}