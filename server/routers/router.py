from typing import Any
import uuid
import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langfuse.callback import CallbackHandler
from utils.config import save_vectorstore
from workflow.state import AgentType, AnswerState
from workflow.graph import create_expert_graph


router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["workflow"],
    responses={404: {"description": "Not found"}},
)


class WorkflowRequest(BaseModel):
    query: str


class WorkflowResponse(BaseModel):
    status: str = "success"
    result: Any = None


save_vectorstore()


async def answer_generator(answer_graph, initial_state, langfuse_handler):
    # 그래프에서 청크 스트리밍
    for chunk in answer_graph.stream(
        initial_state,
        config={"callbacks": [langfuse_handler]},
        subgraphs=True,
        stream_mode="updates",
    ):
        if not chunk:
            continue

        node = chunk[0] if len(chunk) > 0 else None
        if not node or node == ():
            continue

        node_name = node[0]
        role = node_name.split(":")[0]
        subgraph = chunk[1]
        subgraph_node = subgraph.get("update_state", None)

        if subgraph_node:
            response = subgraph_node.get("response", None)
            helps = subgraph_node.get("helps", [])
            answer_state = subgraph_node.get("answer_state", None)
            messages = answer_state.get("messages", [])
            query = answer_state.get("query")

            state = {
                "role": role,
                "response": response,
                "query": query,
                "messages": messages,
                "helps": helps,
            }

            event_data = {"type": "update", "data": state}
            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            print(event_data)

            await asyncio.sleep(0.01)

    yield f"data: {json.dumps({'type': 'end', 'data': {}}, ensure_ascii=False)}\n\n"


@router.post("/answer/stream")
async def stream_answer_workflow(request: WorkflowRequest):
    query = request.query

    session_id = str(uuid.uuid4())
    answer_graph = create_expert_graph(session_id)

    initial_state: AnswerState = {
        "query": query,
        "messages": [],
        "prev_node": "START",  # 이전 노드 START로 설정
        "helps": [],
    }

    langfuse_handler = CallbackHandler(session_id=session_id)

    # 스트리밍 응답 반환
    return StreamingResponse(
        answer_generator(answer_graph, initial_state, langfuse_handler),
        media_type="text/event-stream",
    )