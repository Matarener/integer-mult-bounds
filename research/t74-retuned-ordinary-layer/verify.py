# SPDX-License-Identifier: Apache-2.0
"""Bounded source, rate and actual-constructor checks; no production GL64 run.

Hiroki KUMAZAKI, with substantial OpenAI Codex assistance.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rate import need

RETAINED = {
    "inputs/pr3562-PROOF.md": (
        "3e554832c38b4b801f55b20868679f3283bc90cd5a9d8ce1960f828ed2655f22",
        "8a0f47a1541a0b8e67866df4f65928de31073651"),
    "inputs/pr3562-interface.py": (
        "25707c61b9fc6c1f09388c7cc72d269be0f8f8cae4dbc7cd5c2d00ce7fadf839",
        "6479a08fe78f7f4fe93d144cec26ac84aebcf9d3"),
}


def retained_context():
    origin = json.loads((HERE / "inputs/ORIGIN.json").read_bytes())
    need(origin["commit"] == "abb93be8b9ceca07a2b17f3a97db7bb6b074271d"
         and origin["pull_request"] == 3562, "exact pending predecessor context")
    rows = {row["path"]: row for row in origin["files"]}
    need(set(rows) == set(RETAINED), "complete retained predecessor context")
    for relative, (digest, blob) in RETAINED.items():
        path = HERE / relative
        need(not path.is_symlink(), "regular retained context")
        value = path.read_bytes()
        need(sha256(value).hexdigest() == digest == rows[relative]["sha256"],
             "retained predecessor SHA256: " + relative)
        actual_blob = sha1(b"blob " + str(len(value)).encode() + b"\0" + value).hexdigest()
        need(actual_blob == blob == rows[relative]["git_blob"],
             "retained predecessor Git blob: " + relative)
    return dict(commit=origin["commit"], retained_files=len(rows),
                scope="Exact source context; PR3562's ordinary theorem remains an inherited conditional premise.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("rate", "factory"), required=True)
    args = parser.parse_args()
    context = retained_context()
    if args.suite == "rate":
        from rate import run
        from tree_check import run as tree_run
        from backend_identity import run as backend_run
        result = dict(rate=run(), tree=tree_run(), backend=backend_run())
    else:
        from factory_checks import run
        result = run()
    print(json.dumps(dict(status="PASS_RETUNED_T74_" + args.suite.upper(),
                          predecessor=context, result=result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
