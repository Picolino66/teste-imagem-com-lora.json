import json
import logging
import subprocess
import time
import uuid
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def _compact_text(text: str, limit: int = 1200) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}... [truncated {len(text) - limit} chars]"


def run_comfy_workflow(workflow: dict, request_id: str = "no-request-id"):
    start = time.perf_counter()
    logger.info("request_id=%s runner iniciado", request_id)

    # salva o workflow em arquivo temporário
    filename = f"/tmp/workflow_{uuid.uuid4().hex}.json"
    logger.info("request_id=%s gravando workflow em %s", request_id, filename)
    with open(filename, "w") as f:
        json.dump(workflow, f)

    # comando que executa o workflow
    cmd = ["comfy", "run", "--workflow", filename]
    logger.info("request_id=%s executando comando: %s", request_id, " ".join(cmd))

    try:
        # roda o comando e captura stdout
        proc_start = time.perf_counter()
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        proc_elapsed = time.perf_counter() - proc_start
        logger.info(
            "request_id=%s comfy run finalizado com sucesso em %.3fs",
            request_id,
            proc_elapsed,
        )

        # tenta converter a saída para JSON
        try:
            parsed = json.loads(result.stdout)
            total_elapsed = time.perf_counter() - start
            logger.info(
                "request_id=%s stdout parseado como JSON; duracao total %.3fs",
                request_id,
                total_elapsed,
            )
            return parsed
        except json.JSONDecodeError:
            # se a saída não for JSON, devolve como texto
            logger.info(
                "request_id=%s stdout nao era JSON; retornando texto bruto",
                request_id,
            )
            return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        # devolve mensagem de erro da CLI com fallback para stdout
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        detail = stderr or stdout or str(e)
        logger.error(
            "request_id=%s erro no comfy run; returncode=%s stderr=%s stdout=%s",
            request_id,
            e.returncode,
            _compact_text(stderr),
            _compact_text(stdout),
        )
        raise HTTPException(
            status_code=500,
            detail={"message": detail, "returncode": e.returncode},
        )
    except FileNotFoundError as e:
        logger.error(
            "request_id=%s binario ausente para executar workflow: %s",
            request_id,
            str(e),
        )
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Binario do Comfy nao encontrado no container.",
                "error": str(e),
            },
        )
