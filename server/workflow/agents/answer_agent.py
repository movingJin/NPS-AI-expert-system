from workflow.agents.agent import Agent
from workflow.state import AnswerState, AgentType
from typing import List, Dict, Any, TypedDict


class AnswerAgent(Agent):
    def __init__(
        self, session_id: str = None
    ):
        self.role = AgentType.ANSWER
        self._setup_graph()  # 그래프 설정
        self.session_id = session_id  # langfuse 세션 ID