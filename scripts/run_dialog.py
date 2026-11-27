"""Run dialogue jobs sequentially with NO warm-up runs; the first job of a session includes model loading.
Usage: run_dialog.py [first|rest]   (PRICE env = $/h, default 1.14)
DEADLINE env (unix time): start no new job after it, so the box stops spending even if the Mac that watches it sleeps."""
import csv, json, os, sys, time, uuid, urllib.request, urllib.error
PRICE = float(os.environ.get("PRICE", "1.14")); S = "http://127.0.0.1:8188"
jobs = json.load(open(os.environ.get("JOBS", "wf/round_jobs.json")))
mode = sys.argv[1] if len(sys.argv) > 1 else "all"
if mode == "first": jobs = jobs[:1]
elif mode == "rest": jobs = jobs[1:]
out = csv.writer(open("results_dialog.csv", "a"))
DEADLINE = float(os.environ.get("DEADLINE", "inf"))
for i, (name, sec) in enumerate(jobs):
    if time.time() > DEADLINE:
        print("STOPPED_DEADLINE before", name, f"({len(jobs) - i} jobs not started)", flush=True); break
    wf = json.load(open(f"wf/round_{name}.json"))
    req = urllib.request.Request(S + "/prompt", data=json.dumps({"prompt": wf, "client_id": str(uuid.uuid4())}).encode(),
                                 headers={"Content-Type": "application/json"})
    try: pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    except urllib.error.HTTPError as e: print(name, "REJECTED", e.read().decode()[:1500], flush=True); continue
    t = time.time()
    while True:
        h = json.loads(urllib.request.urlopen(f"{S}/history/{pid}").read())
        if pid in h: st = h[pid]["status"]; break
        time.sleep(1)
    dt = time.time() - t; ok = st.get("status_str") == "success"; cold = (mode != "rest" and i == 0)
    thb = PRICE * dt / 3600 / sec * 33.7
    out.writerow([name, sec, round(dt, 1), ok, cold, round(thb, 4)])
    print(f"{name:8} {sec:>3}s video {dt:7.1f}s ok={ok} {'(includes model load)' if cold else ''} {thb:.3f} THB/s", flush=True)
    if not ok: print(json.dumps(st.get("messages"))[-1500:], flush=True)
print("ROUND_DONE", flush=True)
