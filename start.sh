#!/usr/bin/env bash
set -euo pipefail

COMFY_HOST="${COMFY_HOST:-0.0.0.0}"
COMFY_PORT="${COMFY_PORT:-8188}"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${PORT:-80}"

echo "[start] iniciando ComfyUI em ${COMFY_HOST}:${COMFY_PORT}"
python3 /comfyui/main.py --listen "${COMFY_HOST}" --port "${COMFY_PORT}" &

echo "[start] iniciando FastAPI em ${API_HOST}:${API_PORT}"
exec uvicorn main:app --host "${API_HOST}" --port "${API_PORT}"
