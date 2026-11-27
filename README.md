# h3-comfy-image

Image for MiniMax H3 Ref2VA (set-8 recipe + latent upscaler download) on rented GPUs: `ghcr.io/raigaard/h3-comfy:latest`.

- Base `runpod/pytorch:2.2.0-cu1300-torch2150-ubuntu2404` (torch 2.15.0+cu132, needs a CUDA-13 driver host)
- ComfyUI `8b0f107`, T8 H3 audio nodes `be3a3e9`, spandrel, hf_transfer, ffmpeg
- Real-ESRGAN animevideov3 weights at `/opt/h3/models/`
- No models (license + size) and no keys. On the box: `bash /opt/h3/h3-init.sh > /workspace/init.log 2>&1`
- H3 Community License: do not run in the EU, UK, Republic of Korea or USA.

Every push to `main` that touches the Dockerfile or `scripts/` rebuilds it (GitHub Actions).
