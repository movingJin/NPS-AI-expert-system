import uvicorn
from fastapi import FastAPI
from routers import workflow

from db.database import Base, engine
#from server.routers import history

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NPS expert API",
    description="국민연금 실무 전문가 AI 서비스를 위한 API",
    version="0.0.1",
)

# app.include_router(history.router)
app.include_router(workflow.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)