#!/usr/bin/env bash
# Run once on a fresh box: link ComfyUI into /workspace, download the set-8 models, start ComfyUI, check the fast path.
# Markers in /workspace/init.log: DL_MAIN_DONE, then H3_READY (or WARN_SLOW_PATH if SolAttn fell back).
set -u; mkdir -p /workspace && cd /workspace
[ -e /workspace/ComfyUI ] || ln -s /opt/ComfyUI /workspace/ComfyUI
cp -n /opt/h3/*.sh /opt/h3/*.py /workspace/ 2>/dev/null
mkdir -p /workspace/ComfyUI/input
cat /opt/h3/VERSIONS
python -c "import torch;print('torch',torch.__version__,torch.version.cuda,torch.cuda.get_device_name(0))"
nvidia-smi --query-gpu=driver_version --format=csv,noheader
bash /opt/h3/dl_models.sh 2>&1 | tee /workspace/dl.log
bash /opt/h3/start_comfy.sh
grep -iE "kernel failed|falling back|import failed" /workspace/comfy.log && echo WARN_SLOW_PATH
echo H3_READY
