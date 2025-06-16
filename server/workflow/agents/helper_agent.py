from workflow.agents.agent import Agent, AgentState
from workflow.state import AnswerState, AgentType
from typing import List, Dict, Any, TypedDict
from utils.config import get_llm
from retrieval.search_service import get_search_chain, get_next_query


class HelperAgent(Agent):
    def __init__(
        self, session_id: str = None
    ):
        self.role = AgentType.HELPER
        self._setup_graph()
        self.session_id = session_id


    def _generate_response(self, state: AgentState) -> AgentState:
        previous_messages = [m for m in state["answer_state"]["messages"] if m["role"] == AgentType.ANSWER]
        last_answer_message = previous_messages[-1]["content"] if previous_messages else ""
        next_quries = get_next_query(last_answer_message)
        helps = next_quries
            
        return {**state, "helps": helps}