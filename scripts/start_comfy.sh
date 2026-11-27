#!/usr/bin/env bash
# (Re)start ComfyUI with outputs on local container disk. Extra args are passed to main.py.
pkill -f "ComfyUI/main.py" ; sleep 3
mkdir -p /root/out
# Match CPU threads to the container CPU quota (pods report all host cores but are throttled).
Q=$(awk '{ if ($1!="max") printf "%d", $1/$2; }' /sys/fs/cgroup/cpu.max 2>/dev/null); [ -z "$Q" ] && [ -f /sys/fs/cgroup/cpu/cpu.cfs_quota_us ] && Q=$(( $(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us) / $(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us) )); [ "${Q:-0}" -le 0 ] && Q=; export OMP_NUM_THREADS=${Q:-8}; echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"
cd /workspace/ComfyUI && setsid nohup python /workspace/ComfyUI/main.py --listen 127.0.0.1 --port 8188 --output-directory /root/out "$@" > /workspace/comfy.log 2>&1 < /dev/null &
for i in $(seq 1 60); do curl -s -o /dev/null 127.0.0.1:8188/system_stats && { echo "comfy up ($*)"; exit 0; }; sleep 2; done; echo "comfy failed"; tail -20 /workspace/comfy.log
