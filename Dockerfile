FROM runpod/worker-comfyui:latest

WORKDIR /app

# Instala só o que é necessário
RUN python3 -m pip install --upgrade pip && \
    pip install fastapi uvicorn[standard] pydantic

COPY app /app
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Baixa modelos do novo workflow
RUN comfy model download \
    --url https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors \
    --relative-path models/text_encoders \
    --filename qwen_3_4b.safetensors

RUN comfy model download \
    --url https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors \
    --relative-path models/vae \
    --filename ae.safetensors

RUN comfy model download \
    --url https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors \
    --relative-path models/diffusion_models \
    --filename z_image_turbo_bf16.safetensors

# Expor porta correta para runpod
ENV PORT=80
EXPOSE 80

CMD ["/start.sh"]
