#!/usr/bin/env python3
"""Independent mathematical audit of serialized owner artifacts; no producer import.

Consumes the owner construction credited in OWNER-PROOF.md.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations
from math import gcd
from pathlib import Path
import gzip
import hashlib
import json

PKG = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--artifacts", required=True, type=Path,
                    help="directory emitted by owner.py --emit")
ART = parser.parse_args().artifacts


def need(x, why):
    if not x:
        raise ValueError(why)


def load(name, compressed=False):
    p = ART / (name + (".json.gz" if compressed else ".json"))
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if compressed else raw)


def mm(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q()) for col in zip(*b)] for row in a]


def tr(a):
    return [list(x) for x in zip(*a)]


def ident(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def swap_projector(p):
    n = len(p)
    return [[Q(i == j)-p[i][j] for j in range(n)]+p[i] for i in range(n)]+[
        p[i]+[Q(i == j)-p[i][j] for j in range(n)] for i in range(n)]


def project(vectors):
    basis = []
    for vector in vectors:
        z = list(map(Q, vector))
        for u in basis:
            factor = sum(x*y for x, y in zip(z, u))/sum(x*x for x in u)
            z = [x-factor*y for x, y in zip(z, u)]
        if any(z):
            basis.append(z)
    return [[sum((v[i]*v[j]/sum(x*x for x in v) for v in basis), Q())
             for j in range(8)] for i in range(8)]


order = load("ORDER")
charts = load("CHARTS")
slots = load("SLOTS")
remainders = load("REMAINDERS")
fill = load("FILL", True)
dispatch = load("DISPATCH", True)
owners = json.loads((PKG/"OWNERS.json").read_text())
word = json.loads(gzip.decompress((PKG/"inputs/WORD.json.gz").read_bytes()))
geometry = json.loads(gzip.decompress((PKG/"inputs/GEOMETRY.json.gz").read_bytes()))

# Prove terminal conjugation and the complemented reverse residual, including
# partial q-perpendicular pieces rather than only their numerical ranks.
bases = {int(f): [[Q(x) for x in row] for row in b]
         for f, b in charts["terminal_bases"].items()}
terminal_p = {}
for f, b in bases.items():
    k = 8 if f == 1 else 4
    d = [[Q(i == j and i < k) for j in range(8)] for i in range(8)]
    p = project([geometry["lines"][i] for i in geometry["frames"][f]])
    need(mm(tr(b), b) == ident(8), "terminal isometry")
    need(mm(mm(b, d), tr(b)) == p, "terminal image")
    complement = [[Q(i == j)-p[i][j] for j in range(8)] for i in range(8)]
    need(mm(swap_projector(ident(8)), swap_projector(complement)) == swap_projector(p),
         "reverse complemented residual")
    terminal_p[f] = p

for q, a in zip(geometry["lines"], charts["family_charts"]):
    a = [[Q(x) for x in row] for row in a]
    need(mm(tr(a), a) == ident(8), "family isometry")
    need([row[0] for row in a] == [Q(x, 2) for x in q], "family root axis")

relative = []
for c in charts["relative_charts"]:
    m = [[Q(x) for x in row] for row in c["relative_matrix"]]
    perm = c["permutation"]
    need(sorted(perm) == list(range(64)), "complete chart permutation")
    b = bases[c["terminal_frame"]]
    expected = [[Q() for _ in range(64)] for _ in range(64)]
    for i in range(64):
        expected[perm[i]] = tr(b)[i]+[Q()]*56 if i < 8 else [Q(j == i) for j in range(64)]
    need(m == expected, "entire relative chart including spectator axes")
    e = terminal_p[c["terminal_frame"]]
    # E is supported on the first eight input axes. Compute only those
    # columns when conjugating: full 64-axis matrix, exact rational output.
    thin = [row[:8] for row in m]
    got = mm(mm(thin, e), tr(thin))
    s = set(c["axes"])
    need(got == [[Q(i == j and i in s) for j in range(64)] for i in range(64)],
         "actual relative terminal image")
    need(0 not in s, "hosted slice leaves port line unchanged")
    relative.append({(i, j): x for i, row in enumerate(m) for j, x in enumerate(row) if x})

# Reconstruct strict source windows from literal events, not recorded windows.
events = order["controller"]
calls = {e["stage"]: (pos, e) for pos, e in enumerate(events) if e["kind"] == "local"}
children = {e["idx"]: (pos, e) for pos, e in enumerate(events) if e["kind"] == "idle"}
need(len(calls) == 9 and len(children) == 10 and len(events) == 29, "controller census")
windows = {}
for child, (end, c) in children.items():
    touches = [i for i, e in enumerate(events[:end])
               if ((e["kind"] == "local" and e["pair"] == c["pair"])
                   or (e["kind"] == "bridge" and c["pair"] in (e["src"], e["dst"])))]
    begin = max(touches, default=-1)
    windows[child] = {s for s, (pos, e) in calls.items() if begin < pos < end}
    source_level, target_level = c["source_level"], c["target_level"]
    expected_axes = list(range(1 if source_level == -1 else 8+7*source_level,
                               8+7*target_level))
    need(c["axes"] == expected_axes, "pending projector axis range")

role_slots = {}
occupied = defaultdict(set)
widths = [8 if frame == 1 else 4 for frame in word["final"][222:]]
for child, cp, offset, width, stage, helper in slots:
    need((stage, helper) not in role_slots, "duplicate slot role")
    need(stage in windows[child] and calls[stage][1]["pair"] != children[child][1]["pair"],
         "strict source window")
    need(width == widths[helper], "actual terminal width")
    axes = children[child][1]["axes"][offset:offset+width]
    need(len(axes) == width and not occupied[child, cp].intersection(axes), "slice overlap")
    occupied[child, cp].update(axes)
    role_slots[stage, helper] = (child, cp, offset, width, axes)
need(set(role_slots) == {(s, h) for s in range(9) for h in range(438)}, "complete slot coverage")
idle = Counter()
for child, cp, rest in remainders:
    whole = children[child][1]["axes"]
    used = occupied[child, cp]
    need(rest == [x for x in whole if x not in used], "exact idle complement")
    need(rest == whole[len(used):], "compacted suffix")
    idle[len(rest)] += 1
need(len(remainders) == 2220 and sum(idle.values()) == 2220, "complete idle bins")
need(idle == Counter({int(r): n for r, n in owners["idle_per_replica_including_zero"].items()}),
     "idle histogram")

physical_axes = defaultdict(set)
same_family = defaultdict(list)
bound_fill = {}
for stage, rep, helper, family, child, offset, width, cid in fill:
    c, cp, off, w, axes = role_slots[stage, helper]
    need((child, offset, width) == (c, off, w), "fill slot binding")
    need(0 <= rep < 32 and family == rep*888+2*children[child][1]["pair"]*111+cp,
         "physical family and replica")
    need(charts["relative_charts"][cid]["axes"] == axes
         and charts["relative_charts"][cid]["terminal_frame"] == word["final"][222+helper],
         "fill actual chart and terminal frame")
    need(not physical_axes[family].intersection(axes), "cross-child physical disjointness")
    physical_axes[family].update(axes)
    need((stage, rep, helper) not in bound_fill, "duplicate full helper role")
    bound_fill[stage, rep, helper] = [family, ["hosted", child, offset, width, cid]]
    same_family[stage, family].append(cid)
need(len(bound_fill) == 126144, "complete physical helper count")
pairs = Counter()
for cids in same_family.values():
    pairs.update(tuple(sorted(x)) for x in combinations(cids, 2))
gcds = Counter()
for (a, b), count in pairs.items():
    left, right = relative[a], relative[b]
    g = 0
    for coordinate in left.keys() | right.keys():
        g = gcd(g, abs((left.get(coordinate, Q())-right.get(coordinate, Q())).numerator))
    need(g > 0 and g & (g-1) == 0, "complete low-packet owner separation for every odd q")
    gcds[g] += count
need(gcds == Counter({1: 180736}), "same-family pair census")

seen = set()
for desc in dispatch:
    s, r, pair = desc["stage"], desc["replica"], desc["pair"]
    expected = calls[s][1]
    need(desc["orientation"] == ("reverse" if expected["reverse"] else "forward")
         and pair == expected["pair"], "literal orientation")
    need(desc["private_owner"] == [28416+s, ["private", "d"]], "private reserve")
    need(len(desc["owners"]) == 660, "all ordinary owners")
    for role, actual in enumerate(desc["owners"]):
        if role < 222:
            side, port = divmod(role, 111)
            if expected["reverse"]:
                side = 1-side
            wanted = [r*888+(2*pair+side)*111+port, ["data", s, port]]
        else:
            wanted = bound_fill[s, r, role-222]
        need(actual == wanted, "actual dispatch owner")
    need((s, r) not in seen, "duplicate call")
    seen.add((s, r))
need(seen == {(s, r) for s in range(9) for r in range(32)}, "complete dispatch")

route_count = max(len(charts["terminal_programs"][str(c["terminal_frame"])]["program"])
                  +len(c["permutation_program"])+p["primitive_count"]
                  for c in charts["relative_charts"] for p in charts["family_programs"])
need(route_count == 151 and 4*route_count == 604, "full chart/inverse coordinate charge")
need(240+144+4*route_count+2+63+64 == owners["routing_invoice"]["selector_G"] == 1117,
     "complete inherited coordinate tariff")
result = {
    "status": "PASS_INDEPENDENT_SERIALIZED_OWNER_AUDIT",
    "owner_receipt_sha256": hashlib.sha256((PKG/"OWNERS.json").read_bytes()).hexdigest(),
    "helper_occurrences": len(bound_fill), "call_descriptors": len(seen),
    "relative_charts": len(relative), "family_charts": len(charts["family_charts"]),
    "same_family_pairs": sum(pairs.values()), "difference_numerator_gcds": dict(gcds),
    "nonzero_idle_per_replica": sum(n for r, n in idle.items() if r),
    "idle_rank_per_replica": sum(r*n for r, n in idle.items()),
    "selector_G": 1117,
    "scope": "Independent serialized schedule/projector/packet-separation audit; all-size callee and physical tariffs remain hypotheses.",
}
print(json.dumps(result, indent=2, sort_keys=True))
