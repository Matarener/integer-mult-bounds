"""Authenticate the retained public source without extracting or executing it."""

import hashlib
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA = "0063d50073cce4cc5a673566c32212c7a1c863211ab63ff8d538c103b8904631"
MEMBERS = {
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "research/complex-budget-law/closures-2/small-units-h5/unit.py":
        "bcb51defdb9ebf255d07b4b87c15099dce2565580d22a41688f0c9d5f2bb0bf7",
    "research/complex-budget-law/closures-3/small-units-lp/README.md":
        "88811d8e8a6caa3aff86317cb206a3d57c0c820e9bf528e26c477701ed34a208",
    "research/complex-budget-law/closures-3/small-units-lp/core6.py":
        "d36b6222a5f9dab68de921d10b621bedc8b63bb829f4466d9d4b12e9d6249edc",
    "research/complex-budget-law/closures-3/small-units-lp/idem77.py":
        "316b88198a87a73dee019c8286da6943d6044f3743ebde505a94833ab534a26c",
}


def authenticate(path=None):
    path = Path(path) if path is not None else HERE / "inputs/small-unit-source.tar"
    if hashlib.sha256(path.read_bytes()).hexdigest() != ARCHIVE_SHA:
        raise ValueError("comparison archive SHA256 mismatch")
    seen = set()
    with tarfile.open(path, "r:") as archive:
        for member in archive:
            if member.isdir():
                continue
            if not member.isfile() or member.name in seen or member.name not in MEMBERS:
                raise ValueError("unexpected comparison archive member")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("unreadable comparison member")
            with stream:
                raw = stream.read()
            if hashlib.sha256(raw).hexdigest() != MEMBERS[member.name]:
                raise ValueError("comparison member SHA256 mismatch")
            seen.add(member.name)
    if seen != set(MEMBERS):
        raise ValueError("missing comparison archive member")
    return {"archive_sha256": ARCHIVE_SHA, "regular_members": len(seen)}
