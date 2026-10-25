# SPDX-License-Identifier: Apache-2.0
"""Authenticate the unchanged P104 channel and pooled support source."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "research/p104-pooled-cut-independent/verify.py": "b647a3302a9be663c1e7eb4e5aa7a8e586c1dfcd21e74585ea9fb6a6af2c7840",
    "research/p104-pooled-cut-independent/SOURCES.json": "1ea79069d5ca0cec5a46bf6b02bdbd86e467b42695fa0316e8018ba5e7ed7acd",
    "research/p104-pooled-cut-independent/RESULT.json": "46ed5cb1c4d6562ed9c13b6da52a4d0b0cd002af7f40a1ca35abf48b4514e5a1",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "research/p104-native-channel/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    "research/p104-native-channel/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    "research/p104-native-channel/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-native-channel/check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    "research/p104-memory-relaxation-soundness/memory.py": "6810e0118b44ab4ed027c89feaea2626e58e46c1958783e4a982b90129863e6a",
    "research/p104-memory-relaxation-soundness/PROOF.md": "fb86cb83bb8a09b643b91cde1aa531bab18ce7ed47e5b3422bbf4b14375e11ed",
    "research/complex-local-word-ceiling/ceiling.py": "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
    "research/community-frontier1094-audit/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticate():
    raw = {}
    for path, digest in PINS.items():
        value = (ROOT / path).read_bytes()
        need(sha256(value).hexdigest() == digest, "source hash: " + path)
        raw[path] = value
    return raw


def module(raw, name, path):
    need(path in PINS and sha256(raw[path]).hexdigest() == PINS[path], "authenticated executable")
    result = types.ModuleType(name)
    result.__file__ = str(ROOT / path)
    sys.modules[name] = result
    exec(compile(raw[path], result.__file__, "exec", optimize=0), result.__dict__)
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
