#!/usr/bin/env python3
"""Bind the selected forward stream to PR2944's unchanged typed Lean word.

Copyright 2026 Sagar Thakrar. Substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/providers/gauge44/"
LABEL = "research/k8-lean-label-instance/"
BINDING = "research/k8-hpe450-binding/RESULT.json"
FORWARD_SHA = "071ecdacc0bb3ac16046aad4119ed551a945cb0ed6c57002a548a3e2232503d8"
FIRST, SECOND = 13944, 16501
REQUIRED = {ARCHIVE, BINDING, LABEL + "translate.py", LABEL + "generate.py",
            LABEL + "RESULT.json", LABEL + "KERNEL.json"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def decoded(data):
    return json.loads(data, object_pairs_hook=unique)


def authenticate(root=ROOT):
    """Return authenticated bytes; subsequent execution uses these same bytes."""
    root = Path(root).resolve()
    rows = decoded((HERE / "SOURCES.json").read_bytes())["files"]
    result = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        name = row["path"]
        path = (root / name).resolve()
        require(path.is_relative_to(root) and name not in result, "source inventory")
        data = path.read_bytes()
        require(digest(data) == row["sha256"], "Input changed: " + name)
        result[name] = data
    require(REQUIRED <= result.keys(), "missing required source input")
    return result


def retained_modules(inputs):
    """Execute the pinned adapters, including generate.py's exact local import."""
    translator = ModuleType("retained_k8_translate")
    translator.__file__ = LABEL + "translate.py"
    exec(compile(inputs[translator.__file__], translator.__file__, "exec"),
         translator.__dict__)
    generator = ModuleType("retained_k8_generate")
    generator.__file__ = LABEL + "generate.py"
    previous = sys.modules.get("translate")
    sys.modules["translate"] = translator
    try:
        exec(compile(inputs[generator.__file__], generator.__file__, "exec"),
             generator.__dict__)
    finally:
        if previous is None:
            del sys.modules["translate"]
        else:
            sys.modules["translate"] = previous
    return translator, generator


def archive_members(inputs):
    names = [MEMBER + name for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz")]
    with tarfile.open(fileobj=io.BytesIO(inputs[ARCHIVE]), mode="r:gz") as archive:
        members = archive.getmembers()
        require(all(sum(m.name == name for m in members) == 1 for name in names),
                "archive member multiplicity")
        payloads = []
        for name in names:
            member = archive.getmember(name)
            require(member.isfile(), "archive member type")
            payloads.append(gzip.decompress(archive.extractfile(member).read()))
    return payloads


def row_schedule(events):
    """Three untouched row blocks separated by the two cancelling ADDs."""
    require(len(events) == 24757, "complete translated length")
    require(events[FIRST] == ["add", 450, 230, 1, 1], "first active ADD")
    require(events[SECOND] == ["add", 450, 230, -1, 1], "second active ADD")
    blocks = [(0, FIRST, [450]), (FIRST + 1, SECOND, [450, 230]),
              (SECOND + 1, len(events), [450])]
    result = []
    for start, stop, protected in blocks:
        for event in events[start:stop]:
            require(event[0] in ("add", "scale", "copy", "clear", "relabel"),
                    "unknown translated constructor")
            require(event[0] == "relabel" or event[1] not in protected,
                    "protected row target")
        result.append({"start": start, "stop": stop, "length": stop - start,
                       "protected": protected})
    return result


def _translate(inputs):
    canonical_bytes, program_bytes = archive_members(inputs)
    canonical, programs = decoded(canonical_bytes), decoded(program_bytes)
    binding = decoded(inputs[BINDING])
    require(digest(canonical_bytes) == binding["canonical_content_sha256"],
            "canonical word binding")
    require(set(programs) == {"forward", "backward"}, "orientation inventory")
    forward = programs["forward"]
    forward_sha = digest(encoded(forward))
    require(forward_sha == binding["program_sha256"]["forward"] == FORWARD_SHA,
            "forward stream binding")
    require(len(forward) == 24767, "complete serialized length")
    translator, generator = retained_modules(inputs)
    start, events, indices = translator.translate(canonical, forward)
    prior = decoded(inputs[LABEL + "RESULT.json"])["orientations"]["forward"]
    translation_sha, indices_sha = digest(encoded([start, events])), digest(encoded(indices))
    require(translation_sha == prior["translation_sha256"], "translation binding")
    require(indices_sha == prior["source_indices_sha256"], "source index binding")
    require(indices[FIRST] == 13949 and indices[SECOND] == 16507, "active source indices")
    counts = dict(sorted(Counter(event[0] for event in events).items()))
    require(counts == prior["constructors"], "constructor inventory")
    receipt = {"archive": ARCHIVE, "member": MEMBER + "LOCAL-PROGRAMS.json.gz",
               "canonical_content_sha256": digest(canonical_bytes),
               "forward_sha256": forward_sha, "translation_sha256": translation_sha,
               "source_indices_sha256": indices_sha, "serialized_events": len(forward),
               "semantic_events": len(events), "omitted_phase_markers": len(forward) - len(events),
               "constructors": counts, "active_source_indices": [13949, 16507],
               "active_semantic_indices": [FIRST, SECOND], "row_blocks": row_schedule(events)}
    return events, start, indices, receipt, generator


def translated_events(root=ROOT):
    """Return (full events, initial labels, source indices, concise receipt)."""
    return _translate(authenticate(root))[:4]


def emit_existing(out, root=ROOT):
    """Emit byte-identical PR2944 Forward modules; return (paths, receipt)."""
    inputs = authenticate(root)
    events, start, _, receipt, generator = _translate(inputs)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    paths = generator.emit(out, "Forward", start, events)
    expected = decoded(inputs[LABEL + "KERNEL.json"])["generated_sha256"]
    actual = {path.name: digest(path.read_bytes()) for path in paths}
    require(actual == {name: sha for name, sha in expected.items() if name.startswith("Forward")},
            "retained generated source binding")
    receipt = dict(receipt, generated_sha256=actual)
    return paths, receipt
