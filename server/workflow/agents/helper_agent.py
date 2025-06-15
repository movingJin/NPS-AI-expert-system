from workflow.agents.agent import Agent
from workflow.state import AnswerState, AgentType
from typing import List, Dict, Any, TypedDict


class HelperAgent(Agent):
    def __init__(
        self, session_id: str = None
    ):
        self.role = AgentType.HELPER
        self._setup_graph()
        self.session_id = session_id