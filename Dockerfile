# --------- 1) Base comfyui
FROM runpod/worker-comfyui:5.5.1-base

# --------- 2) Define app directory
WORKDIR /app

# --------- 3) Copia requirements.txt primeiro
COPY requirements.txt /app/

# --------- 4) Atualiza pip e instala requirements
RUN python3 -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --------- 5) Copia o restante da app
COPY app /app

# --------- 6) Modelos e LoRA
RUN comfy model download \
    --url https://huggingface.co/SeeSee21/Z-Image-Turbo-AIO/resolve/main/z-image-turbo-fp8-aio.safetensors \
    --relative-path models/diffusion_models \
    --filename z-image-turbo-fp8-aio.safetensors

RUN wget -O /comfyui/models/loras/RealisticSnapshot-Zimage-Turbov5.safetensors \
    https://huggingface.co/idan054/sxrxa/resolve/main/RealisticSnapshot-Zimage-Turbov5.safetensors

# --------- 7) Expor porta e comando
ENV PORT=80
EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]