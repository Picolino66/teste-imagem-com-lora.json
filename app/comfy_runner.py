import subprocess
import json
import os
import uuid
from fastapi import HTTPException

# Função que roda comfycli com workflow JSON
def run_comfy_workflow(workflow: dict):
    # Cria arquivo temporário
    filename = f"/tmp/workflow_{uuid.uuid4().hex}.json"
    with open(filename, "w") as f:
        json.dump(workflow, f)

    # Chamada ao comfy-cli para execução (usa comfyui-manager)
    cmd = [
        "comfy", "run", filename,
        "--output", f"/tmp/output_{uuid.uuid4().hex}.json"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=e.stderr)