from workflow.agents.answer_agent import AnswerAgent
from workflow.agents.helper_agent import HelperAgent
from workflow.state import AnswerState, AgentType
from langgraph.graph import StateGraph, END


def create_expert_graph(session_id: str = ""):

    # 그래프 생성
    workflow = StateGraph(AnswerState)

    answer_agent = AnswerAgent(session_id=session_id)
    helper_agent = HelperAgent(session_id=session_id)

    # 노드 추가
    workflow.add_node(AgentType.ANSWER, answer_agent.run)
    workflow.add_node(AgentType.HELPER, helper_agent.run)
    workflow.add_edge(AgentType.ANSWER, AgentType.HELPER)

    workflow.set_entry_point(AgentType.ANSWER)
    workflow.add_edge(AgentType.HELPER, END)

    # 그래프 컴파일
    return workflow.compile()