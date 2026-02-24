import logging
import time
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from comfy_runner import run_comfy_workflow
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
def startup_event():
    logger.info("startup completo; API pronta para receber requisicoes")

# GET /ping → usado pelo Runpod para health check (status 200 = healthy)
@app.get("/ping")
def ping():
    logger.info("request recebida em /ping")
    return {"status": "healthy"}

# Modelo de entrada para workflow JSON
class WorkflowIn(BaseModel):
    workflow: dict

# POST /generate → endpoint para geração
@app.post("/generate")
async def generate(data: WorkflowIn):
    request_id = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    logger.info("request_id=%s inicio /generate", request_id)

    workflow = data.workflow
    workflow_size = len(str(workflow))
    node_count = len(workflow) if isinstance(workflow, dict) else 0
    logger.info(
        "request_id=%s payload validado; nodes=%s approx_chars=%s",
        request_id,
        node_count,
        workflow_size,
    )

    result = run_comfy_workflow(workflow, request_id=request_id)
    elapsed = time.perf_counter() - start
    logger.info("request_id=%s fim /generate com sucesso em %.3fs", request_id, elapsed)
    return {"result": result}
