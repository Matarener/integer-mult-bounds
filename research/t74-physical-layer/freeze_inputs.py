# SPDX-License-Identifier: Apache-2.0
"""Freeze the checked native/controller inputs and closed replay source subset.

Run after prepare_inputs.py. This creates a deterministic regular-file bundle;
it does not certify an endpoint or replace the bounded native/controller replay.
"""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import tarfile

from prepare_inputs import SOURCE_MANIFEST, inventory, need, read


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "prepared", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    source, prepared, output = args.source.resolve(), args.prepared.resolve(), args.output.resolve()
    need(not output.exists(), "fresh frozen bundle")
    manifest = (source / "MANIFEST.json").read_bytes()
    need(sha256(manifest).hexdigest() == SOURCE_MANIFEST, "complete derived-source manifest pin")
    source_pins = json.loads(manifest)
    need({k: v for k, v in inventory(source).items() if k != "MANIFEST.json"} == source_pins,
         "complete source inventory before export")
    need(read(prepared / "RESULT.json")["status"] == "PASS_T74_CONTROLLER_SOURCE_PREPARATION",
         "completed input preparation")
    paths = {"source/MANIFEST.json": source / "MANIFEST.json"}
    for pattern in ("NOTICE*", "LICENSE*", "*NOTICE"):
        for path in source.rglob(pattern):
            if path.is_file():
                paths["source/" + path.relative_to(source).as_posix()] = path
    for folder in ("new/fastnative", "new/borrow/words"):
        for path in (source / folder).rglob("*"):
            if path.is_file():
                paths["source/" + path.relative_to(source).as_posix()] = path
    for name in ("audit_allcold.py", "emit_allcold.py", "witness.py", "generated_identity.py"):
        paths["source/code/" + name] = source / "code" / name
    for folder in ("bound/base", "hosted"):
        for path in (prepared / folder).rglob("*"):
            if path.is_file():
                paths["prepared/" + path.relative_to(prepared).as_posix()] = path
    for name in ("CONTROLLER-AUDIT.json", "OWNERS-AND-PROFILE.json", "IDLE-REMAINDER-FRAMES.json",
                 "input-package/new/CONTROLLER-SPEC.json", "input-package/construction/leaver/PIVOT-SWAP-k8.json"):
        paths["prepared/" + name] = prepared / name
    bodies = {}
    for name, path in paths.items():
        need(path.is_file() and not path.is_symlink(), "regular frozen input")
        bodies[name] = path.read_bytes()
        if name.startswith("source/") and name != "source/MANIFEST.json":
            need(sha256(bodies[name]).hexdigest() == source_pins[name.removeprefix("source/")],
                 "retained source-subset byte binding")
    receipt = dict(format="t74-physical-inputs-v1", source_manifest_sha256=SOURCE_MANIFEST,
                   files={name: dict(size=len(raw), sha256=sha256(raw).hexdigest()) for name, raw in sorted(bodies.items())},
                   scope="Exact source subset and checked generated data; execute the separate mathematical replays.")
    bodies["INPUTS.json"] = json.dumps(receipt, sort_keys=True, indent=2).encode() + b"\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream, tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, raw in sorted(bodies.items()):
            info = tarfile.TarInfo(name)
            info.size = len(raw)
            info.mode = 0o644
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(raw))
    print(json.dumps(dict(status="FROZEN_INPUT_TRANSPORT_ONLY", files=len(bodies),
                          bytes=output.stat().st_size, sha256=sha256(output.read_bytes()).hexdigest()), sort_keys=True))


if __name__ == "__main__":
    main()
