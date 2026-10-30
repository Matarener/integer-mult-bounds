# SPDX-License-Identifier: Apache-2.0
"""Compare PR3562's exact backend manifest to the retained T74 archive closure.

No archive is extracted and no predecessor code is executed here.
Hiroki KUMAZAKI with substantial OpenAI Codex assistance; source credit is
Jose Manuel's PR3562/3477/3385 and the retained ordinary/native lineage.
"""
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

from rate import need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/t74-physical-layer/inputs/pr3385-controller.tar"
ARCHIVE_SHA = "85c1442175741317a6f17f39586ddef54a4be8e8942a0bc517fcafa103ff7498"
MANIFEST_SHA = "920cec57d358249261a539adb9265ee00fa2fb820641b83d3757158ff401f503"


def run():
    raw = (HERE / "inputs/pr3562-backend-manifest.json").read_bytes()
    need(sha256(raw).hexdigest() == MANIFEST_SHA, "verbatim PR3562 backend manifest")
    manifest = json.loads(raw)
    need(manifest["commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
         and manifest["package"] == "research/physical-ordinary-interchange",
         "PR3562 backend source context")
    identity = json.loads((HERE / "inputs/BACKEND-IDENTITY.json").read_bytes())
    need(identity["pr3562_head"] == "abb93be8b9ceca07a2b17f3a97db7bb6b074271d"
         and identity["pr3562_backend_manifest_sha256"] == MANIFEST_SHA,
         "pending ordinary theorem provenance")
    rows = {row["path"]: row for row in manifest["files"]}
    matches = {row["backend_path"]: row for row in identity["nested_t74_matches"]}
    need(len(rows) == len(manifest["files"]) == len(matches) ==
         len(identity["nested_t74_matches"]) == 35 and set(rows) == set(matches),
         "complete unique backend match inventory")
    root = ROOT / ARCHIVE
    need(root.is_file() and not root.is_symlink(), "regular retained controller archive")
    cache = {ARCHIVE: root.read_bytes()}
    need(sha256(cache[ARCHIVE]).hexdigest() == ARCHIVE_SHA, "retained archive authority")

    def member(path):
        if path in cache:
            return cache[path]
        need(path.startswith(ARCHIVE + "!") and path.count("!") <= 8,
             "bounded member path in retained archive")
        parent, name = path.rsplit("!", 1)
        posix = PurePosixPath(name)
        need(not posix.is_absolute() and ".." not in posix.parts and
             posix.as_posix() == name and "\\" not in name, "canonical archive member")
        with tarfile.open(fileobj=io.BytesIO(member(parent)), mode="r:*") as archive:
            found = [row for row in archive.getmembers() if row.name == name]
            need(len(found) == 1 and found[0].isfile() and found[0].size <= 2**26,
                 "unique bounded regular archived source")
            value = archive.extractfile(found[0]).read()
        cache[path] = value
        return value

    for archive in identity["nested_t74_archives"]:
        need(sha256(member(archive["path"])).hexdigest() == archive["sha256"],
             "nested controller archive identity")
    for path, row in rows.items():
        match = matches[path]
        value = member(match["archive_member"])
        need(len(value) == row["size"] and
             sha256(value).hexdigest() == row["sha256"] == match["sha256"],
             "same complete ordinary backend source: " + path)
    return dict(status="PASS_COMPLETE_ORDINARY_BACKEND_IDENTITY", files=len(rows),
                manifest_sha256=MANIFEST_SHA, controller_archive_sha256=ARCHIVE_SHA,
                scope="All 35 PR3562 export files occur byte-identically in the retained T74 closure; no all-size theorem validation.")


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
