# clean base image containing only comfyui, comfy-cli and comfyui-manager
FROM runpod/worker-comfyui:5.5.1-base

# install custom nodes into comfyui (first node with --mode remote to fetch updated cache)
RUN comfy node install --exit-on-fail rgthree-comfy@1.0.2512112053 --mode remote

# The following custom nodes are in the 'unknown_registry' group and have no aux_id (GitHub repo) provided.
# They could not be resolved automatically and are therefore skipped. If you can provide GitHub repos (aux_id)
# for these packages, I can add RUN git clone ... lines to install them.
# - Reroute
# - Reroute
# - Reroute
# - Fast Groups Bypasser (rgthree)
# - MarkdownNote
# - MarkdownNote
# - MarkdownNote
# - Fast Groups Bypasser (rgthree)

# download models into comfyui
RUN comfy model download --url https://huggingface.co/SeeSee21/Z-Image-Turbo-AIO/blob/main/z-image-turbo-fp8-aio.safetensors --relative-path models/diffusion_models --filename z-image-turbo-fp8-aio.safetensors
# download RealisticSnapshot-Zimage-Turbov5.safetensors
RUN wget -O /comfyui/models/loras/RealisticSnapshot-Zimage-Turbov5.safetensors https://huggingface.co/idan054/sxrxa/resolve/5cd5b3afd79b8e908d146a79b798c0f484877181/RealisticSnapshot-Zimage-Turbov5.safetensors?download=true
# copy all input data (like images or videos) into comfyui (uncomment and adjust if needed)
# COPY input/ /comfyui/input/
