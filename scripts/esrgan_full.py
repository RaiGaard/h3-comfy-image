"""Fast per-frame anime upscaler test: Real-ESRGAN animevideov3 (x4, SRVGGNetCompact) via spandrel, streamed with
ffmpeg pipes (no full-clip tensor in RAM). Output scaled on GPU to 1920x1080, source audio muxed back.
Usage: python esrgan_up.py MODEL IN.mp4 OUT.mp4"""
import subprocess, sys, time, json
import numpy as np, torch, torch.nn.functional as F
from spandrel import ModelLoader

model_path, src, dst = sys.argv[1:4]
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                   "stream=width,height,r_frame_rate", "-of", "json", src],
                                  capture_output=True, text=True).stdout)["streams"][0]
w, h, fps = probe["width"], probe["height"], probe["r_frame_rate"]
t0 = time.time()
m = ModelLoader().load_from_file(model_path).model.cuda().half().eval()
rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w*4}x{h*4}", "-r", fps,
                       "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", 
                       "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", dst],
                      stdin=subprocess.PIPE)
n, fb, B = 0, w * h * 3, 8
with torch.inference_mode():
    while True:
        buf = rd.stdout.read(fb * B)
        if not buf:
            break
        k = len(buf) // fb
        x = torch.from_numpy(np.frombuffer(buf[:k * fb], np.uint8).reshape(k, h, w, 3).copy()).cuda()
        x = x.permute(0, 3, 1, 2).half() / 255
        y = m(x)
        y = y.float().clamp(0, 1)
        wr.stdin.write((y * 255).round().byte().permute(0, 2, 3, 1).contiguous().cpu().numpy().tobytes())
        n += k
wr.stdin.close(); wr.wait(); rd.wait()
print(f"esrgan {n} frames {w}x{h} -> 4x -> 1920x1080 in {time.time() - t0:.1f}s (incl model load)")
