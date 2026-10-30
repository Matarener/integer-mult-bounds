# SPDX-License-Identifier: Apache-2.0
"""Lower the two T74 native providers to explicit physical instructions.

Jose Manuel, with substantial OpenAI Codex assistance. I extend the finite
compiler in PR3385, retaining the PR2979 and PR2226 source-event semantics.
This module does not implement the whole-call controller or prove admission.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_native(directory):
    paths = {"word": "CANONICAL-WORD.json.gz", "programs": "LOCAL-PROGRAMS.json.gz",
             "native": "CLIFFORD-RECIPES.json", "residuals": "RESIDUAL-ADAPTERS.json"}
    result = {}
    for key, name in paths.items():
        raw = (Path(directory) / name).read_bytes()
        result[key] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    word = result["word"]
    need((word["h"], word["v"], word["R"]) == (9, 112, 408), "T74 local domain")
    need(len(word["start"]) == len(word["final"]) == 632 and
         len(word["centers"]) == 8 and len(set(word["zero_buffers"])) == 91,
         "complete persistent/centre/zero-buffer inventory")
    return result


class Compiler:
    slots = 632
    centres = 8
    private = 99

    def __init__(self, data, orientation):
        need(orientation in ("forward", "backward"), "literal orientation")
        self.data, self.orientation = data, orientation
        self.word = data["word"]
        self.zero_ids = tuple(sorted(self.word["zero_buffers"]))
        need(len(self.zero_ids) == len(set(self.zero_ids)) == 91, "91 private Z labels")
        self.zmap = {label: self.slots + self.centres + i for i, label in enumerate(self.zero_ids)}
        self.edges = {(r["old"], r["new"]): r for r in data["native"]["children"]}
        self.ends = {(r["role"], r["port"]): r for r in data["native"]["endpoint_adapters"]}
        self.warps = {(r["sign"], r["op"], r["old"], r["new"]): r for r in data["native"]["warps"]}
        need(len(self.edges) == len(data["native"]["children"]) and len(self.ends) == 224 and
             len(self.warps) == len(data["native"]["warps"]), "unambiguous native recipes")
        self.frames = list(self.word["start"])
        self.cframes, self.seen_centres, self.live_z, self.seen_z = {}, set(), set(), set()
        self.code, self.recipes, self.ranges = [], {}, []
        self.raw_index = -1

    def slot(self, role):
        need(type(role) in (list, tuple) and len(role) == 2, "typed source role")
        kind, index = role
        need(type(index) is int, "integer source role")
        if kind == "L":
            need(0 <= index < self.slots, "persistent role")
            return index
        if kind == "C":
            need(0 <= index < self.centres, "centre role")
            return self.slots + index
        need(kind == "Z" and index in self.zmap, "declared zero-buffer role")
        return self.zmap[index]

    def at_frame(self, role, frame):
        slot = self.slot(role)
        if role[0] == "L":
            need(self.frames[role[1]] == frame, "persistent scalar frame")
        elif role[0] == "C":
            need(self.cframes.get(slot) == frame, "live centre frame")
        else:
            need(slot in self.live_z and frame == 1, "live FULL-frame zero buffer")
        return slot

    def emit(self, kind, *arguments):
        self.code.append((kind, self.raw_index, *arguments))

    def mono(self, slot, record, inverse=False):
        need(type(record) is dict and type(inverse) is bool, "directed monomial")
        name = sha256(canonical(record)).hexdigest()
        need(name not in self.recipes or self.recipes[name] == record, "monomial identity")
        self.recipes[name] = record
        self.emit("monomial", slot, name, inverse)

    def scalar(self, event):
        _, op, frame = event
        kind, role = op[:2]
        target = self.slot(role)
        if kind == "clear":
            need(role[0] == "C", "only owned centre CLEAR in the source word")
            if target in self.cframes:
                need(self.cframes.pop(target) == frame, "centre discard frame")
            else:
                need(target not in self.seen_centres, "one owned centre lifetime")
                self.cframes[target] = frame
                self.seen_centres.add(target)
            self.emit("zero", target)
            return
        self.at_frame(role, frame)
        if kind == "copy":
            source = self.at_frame(op[2], frame)
            need(role[0] == "C" and source != target, "owned centre COPY")
            self.emit("copy", target, source)
            return
        need(kind in ("add", "scale"), "literal scalar opcode")
        offset = 3 if kind == "add" else 2
        value = Q(op[offset], op[offset + 1])
        need(value.denominator & (value.denominator - 1) == 0, "dyadic scalar")
        if kind == "scale":
            a = abs(value.numerator)
            need(a > 0 and a & (a - 1) == 0, "signed power-of-two SCALE")
        source = self.at_frame(op[2], frame) if kind == "add" else None
        need(source != target, "distinct scalar operands")
        self.emit("scalar", target, source, (kind, value.numerator, value.denominator))

    def child(self, event):
        if event[0] == "climb":
            _, _part, target, old, new, rank = event
            need(0 <= target < self.slots and self.frames[target] == old, "climb source frame")
            self.frames[target] = new
        else:
            _, index, old, new, rank = event
            target = self.slot(("C", index))
            need(self.cframes.get(target) == old, "live centre transport")
            self.cframes[target] = new
        record = self.edges[old, new]
        need(record["rank"] == rank and 0 < rank <= 8, "proper source child")
        self.mono(target, record["right"])
        self.emit("child", target, rank)
        self.mono(target, record["left"])

    def adapter(self, event):
        _, direction, target, frame = event
        need(direction in ("old_to_new", "new_to_old") and 0 <= target < self.slots,
             "endpoint adapter")
        need(frame == self.word["start" if direction == "old_to_new" else "final"][target],
             "adapter source binding")
        if direction == "old_to_new" and target < 112:
            record = self.ends["source", target]
        elif direction == "new_to_old" and 112 <= target < 224:
            record = self.ends["target", target - 112]
        else:
            need(frame == (0 if direction == "old_to_new" else 1), "literal identity adapter")
            self.emit("identity", target)
            return
        need(record["rank"] == 0 and record["frame"] == frame, "rank-zero endpoint")
        self.mono(target, record["left"], direction == "new_to_old")

    def residual(self, event):
        _, direction, target, entrance, *end = event
        terminal = end[0] if end else 1
        need(direction in ("pre", "post") and 224 <= target < self.slots and
             (entrance, terminal) == (self.word["start"][target], self.word["final"][target]),
             "residual helper contract")
        key = f"{entrance}:{terminal}" if end else str(entrance)
        record = self.data["residuals"]["recipes"][key]
        need(record["frame"] == entrance, "normalized residual entrance")
        self.mono(target, record["right" if direction == "pre" else "left"], True)

    def warp(self, event):
        _, role, operation, old, new = event
        target = self.at_frame(role, old)
        need(type(operation) is int and operation != 0 and not self.cframes, "warp outside centre lifetime")
        record = self.warps[1 if operation > 0 else -1, abs(operation), old, new]
        need(record["rank"] == 0 and record["right"] is None, "zero-rank physical warp")
        if role[0] == "L":
            self.frames[role[1]] = new
        else:
            need(role[0] == "Z" and old == new == 1, "private warp preserves FULL")
        self.mono(target, record["left"])

    def zero_buffer(self, event):
        _, action, label = event
        target = self.slot(("Z", label))
        if action == "alloc":
            need(target not in self.seen_z, "one owned zero-buffer lifetime")
            self.seen_z.add(target)
            self.live_z.add(target)
            self.emit("zero", target)
        else:
            need(action == "free" and target in self.live_z, "release live zero buffer")
            self.live_z.remove(target)
            # The physical interpreter must check zero before clearing this tape.
            self.emit("release_zero", target)

    def run(self):
        handlers = {"scalar": self.scalar, "climb": self.child, "center": self.child,
                    "adapter": self.adapter, "residual_adapter": self.residual,
                    "warp": self.warp, "zero_buffer": self.zero_buffer}
        for self.raw_index, event in enumerate(self.data["programs"][self.orientation]):
            first = len(self.code)
            if event[0] == "phase":
                need(not self.cframes, "centres close at phase boundaries")
                self.emit("marker", event[1])
            else:
                need(event[0] in handlers, "complete source event alphabet")
                handlers[event[0]](event)
            need(first < len(self.code), "explicit refinement of each source event")
            self.ranges.append((first, len(self.code)))
        need(self.frames == self.word["final"] and not self.cframes and not self.live_z,
             "complete native frame/lifetime return")
        need(self.seen_centres == set(range(632, 640)) and self.seen_z == set(self.zmap.values()),
             "complete private inventory")
        return tuple(self.code), self.recipes, tuple(self.ranges)


def check(directory):
    data = read_native(directory)
    output = {}
    expected = {1: 2445, 2: 706, 3: 232, 4: 108, 5: 18, 8: 8}
    for orientation in ("forward", "backward"):
        code, recipes, ranges = Compiler(data, orientation).run()
        profile = Counter(op[3] for op in code if op[0] == "child")
        need(dict(profile) == expected, "unchanged complete T74 local paid profile")
        need(all(code[j][1] == i for i, (start, end) in enumerate(ranges) for j in range(start, end)),
             "complete ordered source-event coverage")
        output[orientation] = dict(source_events=len(ranges), physical_instructions=len(code),
                                   counts=dict(Counter(op[0] for op in code)), monomials=len(recipes),
                                   paid_profile=dict(sorted(profile.items())),
                                   sha256=sha256(canonical(code)).hexdigest())
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.native_directory), sort_keys=True, indent=2))
