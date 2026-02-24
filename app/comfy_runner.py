import subprocess
import json
import uuid
from fastapi import HTTPException

def run_comfy_workflow(workflow: dict):
    # salva o workflow em arquivo temporário
    filename = f"/tmp/workflow_{uuid.uuid4().hex}.json"
    with open(filename, "w") as f:
        json.dump(workflow, f)

    # comando que executa o workflow
    cmd = ["comfy", "run", "--workflow", filename]
    
    try:
        # roda o comando e captura stdout
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # tenta converter a saída para JSON
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # se a saída não for JSON, devolve como texto
            return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        # devolve mensagem de erro da CLI com fallback para stdout
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        detail = stderr or stdout or str(e)
        raise HTTPException(
            status_code=500,
            detail={"message": detail, "returncode": e.returncode},
        )
