# SPDX-License-Identifier: Apache-2.0
"""Decode immutable selected input bytes without executing predecessor code.

Jose Manuel, with substantial OpenAI Codex assistance. I retain the R480,
native and compiler attribution in PR2287 and the selected source archive.
"""
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PREFIX = "candidate/strict/global/"
MEMBERS = {
    "programs": ("base/providers/gauge44/LOCAL-PROGRAMS.json.gz", "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"),
    "word": ("base/providers/gauge44/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "template": ("hosted/GLOBAL-TEMPLATE.json.gz", "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "phases": ("base/work/complex-nine-native/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
    "native": ("base/providers/gauge44/CLIFFORD-RECIPES.json", "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731"),
    "residuals": ("base/providers/gauge44/RESIDUAL-ADAPTERS.json", "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c"),
    "sigmas": ("hosted/ACTUAL-SIGMAS.json.gz", "f12383eb2691fe33cc9f0525ccb5f6429db6d7bbf0eec76e97f50e752f943dd9"),
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def load():
    path = ROOT / ARCHIVE
    require(sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA, "selected source archive")
    result = {}
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        for key, (suffix, digest) in MEMBERS.items():
            matches = [m for m in members if m.name == PREFIX + suffix]
            require(len(matches) == 1 and matches[0].isfile(), "unique regular selected member")
            raw = archive.extractfile(matches[0]).read()
            require(sha256(raw).hexdigest() == digest, "selected member: " + key)
            result[key] = json.loads(gzip.decompress(raw) if suffix.endswith(".gz") else raw)
    require(result["template"]["m"] == 73 and result["template"]["live"] == 14336,
            "selected global dimensions")
    require(len(result["template"]["calls"]) == 144 and
            len(result["template"]["execution_schedule"]) == 482, "selected schedule domain")
    for name in ("forward", "backward"):
        require(len(result["programs"][name]) == 24767, "complete selected program")
    return result
