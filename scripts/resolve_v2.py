"""On the box, after ComfyUI starts: finish and validate API graphs against the live /object_info. Exit 1 on any problem.

  - `_widgets` lists (X2 nodes, copied from a UI-format workflow) -> named inputs, in INPUT_TYPES order,
    skipping inputs that are already set (links) and non-widget types
  - "__ANIME_FACE__" -> the detector entry whose name ends with the anime face model file
  - every class_type must exist; every combo value must be one of the allowed options
Usage: python resolve_v2.py wf/round_*.json
"""
import json, sys, urllib.request

INFO = json.loads(urllib.request.urlopen("http://127.0.0.1:8188/object_info", timeout=60).read())
WIDGET_TYPES = ("INT", "FLOAT", "STRING", "BOOLEAN")
ANIME_FACE = "anime_face_v14s.pt"
bad = []
for path in sys.argv[1:]:
    g = json.load(open(path))
    for nid, node in g.items():
        ct = node["class_type"]
        if ct not in INFO:
            bad.append(f"{path}: node {nid} {ct} not installed"); continue
        spec = {**INFO[ct]["input"].get("required", {}), **INFO[ct]["input"].get("optional", {})}
        if "_widgets" in node:
            vals = list(node.pop("_widgets"))
            for name, s in spec.items():
                if name in node["inputs"] or not vals:
                    continue
                t = s[0]
                if isinstance(t, list) or t in WIDGET_TYPES or t == "COMBO":
                    node["inputs"][name] = vals.pop(0)
                    if t == "INT" and len(s) > 1 and s[1].get("control_after_generate") and vals:
                        vals.pop(0)
            if vals:
                bad.append(f"{path}: node {nid} {ct} has {len(vals)} unused widget values {vals}")
        for name, v in list(node["inputs"].items()):
            if v == "__ANIME_FACE__":
                opts = spec[name][0] if isinstance(spec[name][0], list) else spec[name][1].get("options", [])
                hit = [o for o in opts if o.replace("\\", "/").endswith(ANIME_FACE)]
                if not hit:
                    bad.append(f"{path}: {ANIME_FACE} not in detector list {opts}"); continue
                node["inputs"][name] = hit[0]; v = hit[0]
            s = spec.get(name)
            if s is None:
                if "." not in name:  # dotted names are dynamic/autogrow sub-inputs (ref_images.x, format.codec, values.a)
                    bad.append(f"{path}: node {nid} {ct} has unknown input {name}")
                continue
            opts = s[0] if isinstance(s[0], list) else (s[1].get("options") if s[0] == "COMBO" and len(s) > 1 else None)
            if opts is not None and not isinstance(v, list) and v not in opts:
                bad.append(f"{path}: node {nid} {ct}.{name} = {v!r} not in options {opts[:8]}")
    json.dump(g, open(path, "w"), indent=1, ensure_ascii=False)
if bad:
    print("RESOLVE_FAIL\n  " + "\n  ".join(bad)); sys.exit(1)
print(f"RESOLVE_OK {len(sys.argv) - 1} graphs")
