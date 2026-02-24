import base64
import logging
import os
import time
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qs, unquote, urlparse
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from comfy_runner import run_comfy_workflow
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
OUTPUT_DIR = Path("/comfyui/output")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    response_format: Literal["text", "base64", "blob"] = "text"


def _extract_output_path(raw_output: str) -> Path | None:
    for line in raw_output.splitlines():
        if "/view?filename=" not in line:
            continue
        parsed = urlparse(line.strip())
        params = parse_qs(parsed.query)
        filename = params.get("filename", [None])[0]
        subfolder = params.get("subfolder", [""])[0]
        if not filename:
            continue

        filename = unquote(filename)
        subfolder = unquote(subfolder)
        candidate = (OUTPUT_DIR / subfolder / filename).resolve()
        output_root = OUTPUT_DIR.resolve()
        if os.path.commonpath([str(output_root), str(candidate)]) != str(output_root):
            return None
        if candidate.exists() and candidate.is_file():
            return candidate
    return None

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

    if data.response_format in {"base64", "blob"}:
        raw_output = result.get("output", "") if isinstance(result, dict) else ""
        output_path = _extract_output_path(raw_output)
        if output_path is None:
            logger.error(
                "request_id=%s nao foi possivel localizar arquivo de output para response_format=%s",
                request_id,
                data.response_format,
            )
            return {"result": result}

        image_bytes = output_path.read_bytes()
        logger.info(
            "request_id=%s arquivo de output localizado: %s (%s bytes)",
            request_id,
            output_path.name,
            len(image_bytes),
        )

        if data.response_format == "blob":
            elapsed = time.perf_counter() - start
            logger.info(
                "request_id=%s fim /generate com sucesso (blob) em %.3fs",
                request_id,
                elapsed,
            )
            return Response(
                content=image_bytes,
                media_type="image/png",
                headers={"X-Output-Filename": output_path.name},
            )

        encoded = base64.b64encode(image_bytes).decode("ascii")
        elapsed = time.perf_counter() - start
        logger.info(
            "request_id=%s fim /generate com sucesso (base64) em %.3fs",
            request_id,
            elapsed,
        )
        return {
            "result": {
                "filename": output_path.name,
                "mime_type": "image/png",
                "image_base64": encoded,
            }
        }

    elapsed = time.perf_counter() - start
    logger.info("request_id=%s fim /generate com sucesso em %.3fs", request_id, elapsed)
    return {"result": result}
