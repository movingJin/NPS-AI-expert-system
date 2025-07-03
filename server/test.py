from retrieval.search_service import get_search_chain
from workflow.graph import create_expert_graph
from langfuse.callback import CallbackHandler
from workflow.state import AnswerState
from utils.config import save_vectorstore


if __name__ == '__main__':
    save_vectorstore()
    # vectorstore, chain = get_search_chain()
    # response = chain.invoke("2025년 6월 기준, 현재 나이 35세의 사람의 조기노령연금 수급연령을 알려줘.")
    # print(response)
    # response = chain.invoke("연천 지사의 전화번호를 알려줘.")
    # print(response)
    # response = chain.invoke("파주 지사의 전화번호를 알려줘.")
    # print(response)

    graph = create_expert_graph()
    graph_image = graph.get_graph().draw_mermaid_png()

    output_path = "expert_graph.png"
    with open(output_path, "wb") as f:
        f.write(graph_image)


    query = "파주지사의 전화번호를 알려줘."
    initial_state: AnswerState = {
        "query": query,
        "messages": [],
        "prev_node": "START",  # 이전 노드 START로 설정
        "docs": {},  # RAG 결과 저장
    }
    langfuse_handler = CallbackHandler()
    result = graph.invoke(
        initial_state
    )

    print(result["messages"])
    print(result.get("docs", {}))