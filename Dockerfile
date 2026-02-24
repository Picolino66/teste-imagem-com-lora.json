FROM runpod/comfyui:latest

WORKDIR /app

# Instala só o que é necessário
RUN python3 -m pip install --upgrade pip && \
    pip install fastapi uvicorn[standard] pydantic

COPY app /app
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Baixa modelos do novo workflow
RUN mkdir -p /comfyui/models/text_encoders /comfyui/models/vae /comfyui/models/diffusion_models

RUN wget -O /comfyui/models/text_encoders/qwen_3_4b.safetensors \
    https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors

RUN wget -O /comfyui/models/vae/ae.safetensors \
    https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors

RUN wget -O /comfyui/models/diffusion_models/z_image_turbo_bf16.safetensors \
    https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors

# Expor porta correta para runpod
ENV PORT=80
EXPOSE 80

CMD ["/start.sh"]
