"""Replay combined evidence in temporary copies; retain immutable published bytes."""
from pathlib import Path
import gzip, hashlib, json, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
NAMES=("p104-joint-neutral-search", "p104-three-meeting-controllability")
def semantic(value):
    if isinstance(value,dict):return {k:semantic(v) for k,v in value.items() if k!="seconds"}
    if isinstance(value,list):return [semantic(v) for v in value]
    return value
def payload(path):
    raw=path.read_bytes()
    if path.name.endswith(".json.gz"):return semantic(json.loads(gzip.decompress(raw)))
    if path.suffix==".json":return semantic(json.loads(raw))
    return raw
source=REPO/"research"/NAMES[0]
final=REPO/"research"/NAMES[1]
manifest=json.loads((final/"SOURCES.json").read_text())
for item in manifest["vendored_predecessor_files"]:
    left=final/item["path"]
    right=source/item["path"].removeprefix("vendor/")
    if left.read_bytes()!=right.read_bytes():raise ValueError("Predecessor byte join: "+str(right))
# Authenticate every declared input, including wrappers and frozen records.
for item in json.loads((ROOT/"SOURCES.json").read_text())["files"]:
    if item["usage"]=="input":
        if hashlib.sha256((REPO/item["path"]).read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("Pinned input mismatch: "+item["path"])
with tempfile.TemporaryDirectory(prefix="p104-publication-") as folder:
    for name in NAMES:
        src=REPO/"research"/name;dst=Path(folder)/name
        shutil.copytree(src,dst,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        before={str(p.relative_to(dst)):payload(p) for p in dst.rglob("*") if p.is_file()}
        flags=["-O"] if sys.flags.optimize else []
        subprocess.run([sys.executable,*flags,"-B",str(dst/"verify.py")],check=True)
        after={str(p.relative_to(dst)):payload(p) for p in dst.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        if before!=after:raise ValueError("Replay changed proof-relevant contents: "+name)
print("PASS_P104_BOUNDARY_PUBLICATION: exact obstruction, constructive controls, source joins; no new kappa")
