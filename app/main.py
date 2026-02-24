import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from comfy_runner import run_comfy_workflow

app = FastAPI()

# GET /ping → usado pelo Runpod para health check (status 200 = healthy)
@app.get("/ping")
def ping():
    return {"status": "healthy"}

# Modelo de entrada para workflow JSON
class WorkflowIn(BaseModel):
    workflow: dict

# POST /generate → endpoint para geração
@app.post("/generate")
async def generate(data: WorkflowIn):
    workflow = data.workflow
    result = run_comfy_workflow(workflow)
    return {"result": result}