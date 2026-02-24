# ----- 1) Base comfyui, já com CLI e UI
FROM runpod/worker-comfyui:5.5.1-base

# Diretório da aplicação
WORKDIR /app

# Copy servidor
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app

# Baixa seu modelo + LoRA igual antes
RUN comfy model download \
    --url https://huggingface.co/SeeSee21/Z-Image-Turbo-AIO/resolve/main/z-image-turbo-fp8-aio.safetensors \
    --relative-path models/diffusion_models \
    --filename z-image-turbo-fp8-aio.safetensors

RUN wget -O /comfyui/models/loras/RealisticSnapshot-Zimage-Turbov5.safetensors \
    https://huggingface.co/idan054/sxrxa/resolve/main/RealisticSnapshot-Zimage-Turbov5.safetensors

# Porta principal e health
ARG PORT=80
ENV PORT=${PORT}
ENV PORT_HEALTH=${PORT}

# Exponha porta para o Runpod
EXPOSE ${PORT}

# Inicia servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]