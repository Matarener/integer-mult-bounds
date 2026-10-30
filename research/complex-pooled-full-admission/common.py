"""Source pins for the pooled-fill admission successor. Apache-2.0.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Frozen PR4180 (yssite) and PR4181 (Rohan Arun) retain their own notices.
"""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ADMISSION = HERE / "frozen/pr4180"
CANDIDATE = HERE / "frozen/pr4181"
MIXED = REPO / "research/staged544-mixed-fourth-entry"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if Path(path).suffix == ".gz" else data)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def check_no_python_caches(roots):
    """Fail closed on inherited loaders' compiled scientific-code caches.

    This is a clean-tree execution condition, not a claim that the inherited
    loaders are safe against concurrent cache injection. Every child receives
    PYTHONDONTWRITEBYTECODE=1 and all declared work directories start fresh.
    """
    roots = sorted(set(Path(p).resolve() for p in roots))
    for root in roots:
        need(root.is_dir(), "cache-check directory exists: " + str(root))
        for path in root.rglob("*"):
            need(not path.is_symlink(), "scientific source symlink refused: " + str(path))
            need(path.suffix not in (".pyc", ".pyo"),
                 "compiled scientific source cache refused: " + str(path))
    return len(roots)


def authenticate():
    pins = read(HERE / "INPUT-PINS.json")
    roots = {HERE}
    for row in pins["files"]:
        root = REPO if row["kind"] == "repository" else HERE
        path = root / row["path"]
        need(path.is_file() and not path.is_symlink()
             and path.resolve().is_relative_to(root.resolve()), "ordinary pinned input")
        need(sha(path) == row["sha256"], "input changed: " + row["path"])
        if row["kind"] == "repository":
            # All consumed repository sources are isolated research packages.
            need(Path(row["path"]).parts[0] == "research", "research input scope")
            roots.add(REPO / Path(*Path(row["path"]).parts[:2]))
    check_no_python_caches(roots)
    return len(pins["files"])
