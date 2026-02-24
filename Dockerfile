FROM runpod/worker-comfyui:5.5.1-base

WORKDIR /app

# Instala só o que é necessário
RUN python3 -m pip install --upgrade pip && \
    pip install fastapi uvicorn[standard] pydantic

COPY app /app

# Baixa modelo e lora
RUN comfy model download \
    --url https://huggingface.co/SeeSee21/Z-Image-Turbo-AIO/resolve/main/z-image-turbo-fp8-aio.safetensors \
    --relative-path models/diffusion_models \
    --filename z-image-turbo-fp8-aio.safetensors

RUN wget -O /comfyui/models/loras/RealisticSnapshot-Zimage-Turbov5.safetensors \
    https://huggingface.co/idan054/sxrxa/resolve/main/RealisticSnapshot-Zimage-Turbov5.safetensors

# Expor porta correta para runpod
ENV PORT=80
EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]