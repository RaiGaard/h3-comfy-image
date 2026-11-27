#!/usr/bin/env bash
# Set-8 models (~40 GB) into /workspace/hf, symlinked into ComfyUI/models. Marker in the log: DL_MAIN_DONE.
set -u; M=/workspace/ComfyUI/models
get(){ repo=$1; file=$2; dir=$3; name=${4:-$(basename "$file")}; mkdir -p $M/$dir
  for t in 1 2 3; do hf download "$repo" "$file" --local-dir /workspace/hf/$repo >/dev/null 2>&1 && break; sleep 5; done
  [ -f /workspace/hf/$repo/$file ] && ln -sf /workspace/hf/$repo/$file $M/$dir/$name && echo "OK $name" || echo "FAIL $repo $file"; }
get Comfy-Org/MiniMax-H3 text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors text_encoders &
get Comfy-Org/MiniMax-H3 vae/minimax_h3_video_vae_int8_convrot.safetensors vae &
get Comfy-Org/MiniMax-H3 vae/minimax_h3_audio_vae_fp32.safetensors vae &
get WarmBloodAban/Minimax-h3_Singularity Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors diffusion_models &
get Comfy-Org/MiniMax-H3 loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors loras &
wait; echo DL_MAIN_DONE
