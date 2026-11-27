# H3 Ref2VA box image: the exact software stack of set 8 (round 2), no models, no keys.
# torch 2.15.0+cu132 is required: on torch 2.8 SolAttn has no fused kernel and every step is ~2.6x slower.
FROM runpod/pytorch:2.2.0-cu1300-torch2150-ubuntu2404
LABEL org.opencontainers.image.source=https://github.com/RaiGaard/h3-comfy-image
ENV PIP_BREAK_SYSTEM_PACKAGES=1 PIP_NO_CACHE_DIR=1 HF_HUB_ENABLE_HF_TRANSFER=1 PYTHONUNBUFFERED=1
ARG COMFY_SHA=8b0f107157b58f9ec79a19fb3182e78cb30f0a23
ARG T8_SHA=be3a3e9219feb63848b3415f1dd1d1571b812203

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# ComfyUI + the T8 H3 node pack, pinned; torch/torchvision/torchaudio are held at the base image versions.
RUN git init -q /opt/ComfyUI && cd /opt/ComfyUI \
 && git fetch -q --depth 1 https://github.com/comfyanonymous/ComfyUI.git $COMFY_SHA && git checkout -q FETCH_HEAD \
 && git init -q custom_nodes/minimax-h3-audio-T8 && cd custom_nodes/minimax-h3-audio-T8 \
 && git fetch -q --depth 1 https://github.com/T8mars/comfyui-minimax-h3-audio-T8 $T8_SHA && git checkout -q FETCH_HEAD \
 && python -m pip freeze | grep -iE "^(torch|torchvision|torchaudio)==" > /opt/keep.txt \
 && python -m pip install -q -r /opt/ComfyUI/requirements.txt -c /opt/keep.txt \
 && python -m pip install -q -c /opt/keep.txt "huggingface_hub[cli,hf_transfer]" websocket-client spandrel \
 && python -c "import torch,sys; print('torch', torch.__version__); sys.exit(0 if torch.__version__.startswith('2.15') else 1)"

# Real-ESRGAN animevideov3 (BSD-3), the upscaler the user picked in round 3.
ADD https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth /opt/h3/models/realesr-animevideov3.pth
COPY scripts/ /opt/h3/
RUN chmod +x /opt/h3/*.sh && echo "comfy=$COMFY_SHA t8=$T8_SHA" > /opt/h3/VERSIONS
# CMD is the base image's own start script (sshd etc.); run /opt/h3/h3-init.sh once the box is up.
