from typing import Dict, List, TypedDict


class AgentType:
    ANSWER = "ANSWER_AGENT"
    HELPER = "HELPER_AGENT"


class AnswerState(TypedDict):
    query: str
    messages: List[Dict]
    prev_node: str