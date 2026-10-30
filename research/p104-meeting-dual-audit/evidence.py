"""Read authenticated source data without importing archived Python code.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retain PR5751, flyingviper PR5718 and every archived predecessor notice.
"""
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import gzip
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "8483f9a679d06c1e270141dbc686a7e76e7a7522"
PREFIX = "research/p104-paid-meeting-splits/"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / "SOURCES.json").read_bytes())["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(len(inputs) == 1, "One declared source export")
    for row in inputs:
        data = (ROOT / row["path"]).read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "source hash: " + row["path"])
        need(sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == row["git_blob"], "source blob: " + row["path"])


def bundle(data):
    payload = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and ".." not in path.parts
                 and "\\" not in member.name and member.name not in payload,
                 "Regular unique archive member")
            payload[member.name] = archive.extractfile(member).read()
    manifest = json.loads(payload[".research-export.json"])
    need(set(payload) == {".research-export.json"} | {r["path"] for r in manifest["files"]},
         "Complete archive inventory")
    for row in manifest["files"]:
        value = payload[row["path"]]
        need(len(value) == row["size"] and sha256(value).hexdigest() == row["sha256"],
             "Archived source hash: " + row["path"])
    return manifest, payload


def load():
    authenticate()
    manifest, top = bundle((HERE / "inputs/pr5751-source.tar").read_bytes())
    need(manifest["commit"] == SOURCE and manifest["package"] == PREFIX[:-1]
         and len(manifest["files"]) == 20, "Exact PR5751 export")
    previous_manifest, previous = bundle(top[PREFIX + "inputs/pr5718-source.tar"])
    need(previous_manifest["commit"] == "a1534ac45401c9a9c80c07aa65c89e00e33594f8",
         "Exact PR5718 source")
    controllers, inventory = [], []
    pending = [(manifest, top)]
    while pending:
        item, files = pending.pop()
        inventory.append({"commit": item["commit"], "files": len(item["files"])})
        for name, data in files.items():
            if name.endswith(".tar"):
                pending.append(bundle(data))
            if name == "research/p104-productive-controller/CONTROLLER.json":
                controllers.append(data)
    need(len(controllers) == 1, "One exact retained physical controller")
    return {
        "source": json.loads(gzip.decompress(previous[
            previous_manifest["package"] + "/WORD.json.gz"])),
        "source_result": json.loads(previous[previous_manifest["package"] + "/RESULT.json"]),
        "word": json.loads(gzip.decompress(top[PREFIX + "WORD.json.gz"])),
        "plan": json.loads(top[PREFIX + "PLAN.json"]),
        "witness": json.loads(top[PREFIX + "WITNESS.json"]),
        "result": json.loads(top[PREFIX + "RESULT.json"]),
        "controller": json.loads(controllers[0]),
        "controller_sha256": sha256(controllers[0]).hexdigest(),
        "archive_inventory": inventory,
    }
