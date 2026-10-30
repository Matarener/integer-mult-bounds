"""Exact unequal-triple closure, produced by Nick Petalas. Apache-2.0."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import gzip
import json
import random
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHIFTS = tuple(range(-3, 4))
ZERO = (0,) * 49


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_read(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "source capacity")
    return raw


def bound_sources():
    manifest = json.loads(bounded_read(HERE / "SOURCES.json", 65536))
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(len(inputs) == 2, "two declared live inputs")
    result = {}
    for row in inputs:
        raw = bounded_read(ROOT / row["path"], 64 * 1024 * 1024)
        digest = sha256(raw).hexdigest()
        need(digest == row["sha256"], "source drift: " + row["path"])
        result[row["path"]] = digest
    return result


def load_inputs():
    pins = bound_sources()
    archive = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
    values = []
    with tarfile.open(archive, "r:gz") as stream:
        members = stream.getmembers()
        need(len(members) <= 20000, "archive inventory capacity")
        for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            matches = [m for m in members if m.name == "slots/local/" + name]
            need(len(matches) == 1 and matches[0].isfile(), "unique regular member")
            member = matches[0]
            need(member.size <= 1024 * 1024, "compressed member capacity")
            with stream.extractfile(member) as source:
                with gzip.GzipFile(fileobj=source) as decoded:
                    raw = decoded.read(16 * 1024 * 1024 + 1)
            need(len(raw) <= 16 * 1024 * 1024, "decoded member capacity")
            values.append(json.loads(raw))
    path = ROOT / "research/k8-coherent-triples/CERTIFICATE.json"
    inherited = json.loads(bounded_read(path, 1024 * 1024))
    return values[0], values[1], inherited, pins


def eligible(word, programs):
    need((word["v"], word["R"]) == (112, 480), "source dimensions")
    need(set(programs) == {"forward", "backward"}, "orientations")
    excluded = set(word["centers"])
    for events in programs.values():
        need(len(events) <= 25000, "event capacity")
        for event in events:
            if event[0] == "residual_adapter":
                excluded.add(event[2])
            if event[0] == "scalar" and event[1][0] in ("copy", "clear"):
                excluded.update(r[1] for r in event[1][1:]
                                if isinstance(r, list) and r[0] == "L")
    helpers = tuple(h for h in range(224, 704) if h not in excluded
                    and word["start"][h] == 0 and word["final"][h] == 1)
    need(len(helpers) == 237, "eligible domain binding")
    return helpers


def terms_from(events, helpers):
    allowed = set(helpers)
    terms = []
    for event in events:
        if event[0] != "scalar" or event[1][0] != "add":
            continue
        gate = event[1]
        a, denominator = abs(gate[3]), abs(gate[4])
        need(0 < a <= 2**64 and 0 < denominator <= 2**32, "nonzero dyadic coefficient")
        need(denominator & (denominator - 1) == 0, "dyadic denominator")
        valuation = (a & -a).bit_length() - 1
        exponent = valuation - (denominator.bit_length() - 1)
        unit = a >> valuation == 1
        target, source = tuple(r[1] if r[0] == "L" and r[1] in allowed else -1
                               for r in gate[1:3])
        if target != -1 or source != -1:
            need(target != source and abs(exponent) <= 32, "ADD domain")
            terms.append((unit, exponent, target, source))
    need(len(terms) <= 16000, "term capacity")
    return tuple(terms)


def f(unit, exponent):
    return abs(exponent) - int(unit and exponent == 0)


def objective(terms, gauges):
    return 2 * sum(abs(k) for k in gauges.values()) + sum(
        f(u, e + gauges.get(t, 0) - gauges.get(s, 0)) for u, e, t, s in terms)


def graph(terms, helpers, gauges):
    incident = {h: Counter() for h in helpers}
    pairs = {h: defaultdict(Counter) for h in helpers}
    shared = defaultdict(Counter)
    for unit, e, target, source in terms:
        e += gauges.get(target, 0) - gauges.get(source, 0)
        for h, other, sign in ((target, source, 1), (source, target, -1)):
            if h in incident:
                incident[h][unit, e, sign] += 1
                if other in incident:
                    pairs[h][other][unit, e, sign] += 1
        if target in incident and source in incident:
            a, b = sorted((target, source))
            shared[a, b][unit, e, target == a] += 1
    return incident, pairs, shared


def slope(records, x, direction):
    return sum(n * (f(u, e + sign*x) - f(u, e + sign*(x-direction)))
               for (u, e, sign), n in records.items())


def clipping(helpers, gauges, incident, pairs):
    digest = sha256()
    count, minimum = 0, None
    for h in helpers:
        radius = max([abs(gauges.get(h, 0)), 3] + [abs(e) for _, e, _ in incident[h]]) + 2
        need(radius <= 40, "clipping radius capacity")
        for direction in (-1, 1):
            minima = {b: min(slope(ts, x, direction) for x in range(-radius, radius+1))
                      for b, ts in pairs[h].items()}
            for magnitude in range(4, radius+1):
                x = direction * magnitude
                base = 2 * (abs(gauges.get(h, 0)+x)
                            - abs(gauges.get(h, 0)+x-direction))
                base += slope(incident[h], x, direction)
                losses = sorted((max(0, slope(ts, x, direction)-minima[b])
                                 for b, ts in pairs[h].items()), reverse=True)
                lower = base - sum(losses[:2])
                need(lower >= 0, "unbounded clipping premise")
                minimum = lower if minimum is None else min(minimum, lower)
                count += 1
                digest.update(f"{h},{direction},{x},{lower}\n".encode())
    return {"tested_slopes": count, "minimum_lower_bound": minimum,
            "sha256": digest.hexdigest()}


def curves(helpers, gauges, incident, shared):
    singles = {}
    for h in helpers:
        singles[h] = tuple(2*(abs(gauges.get(h, 0)+d)-abs(gauges.get(h, 0)))
                           + sum(n*(f(u, e+sign*d)-f(u, e))
                                 for (u, e, sign), n in incident[h].items())
                           for d in SHIFTS)
    corrections = {}
    for edge, records in shared.items():
        row = []
        for a, b in product(SHIFTS, repeat=2):
            value = sum(n*(f(u, e+(a-b if first else b-a))
                           - f(u, e+(a if first else -a))
                           - f(u, e+(-b if first else b)) + f(u, e))
                        for (u, e, first), n in records.items())
            row.append(value)
        corrections[edge] = tuple(row)
    return singles, corrections


def pair_census(helpers, singles, corrections):
    digest, histogram = sha256(), Counter()
    count = 0
    for a, b in combinations(helpers, 2):
        correction = corrections.get((a, b), ZERO)
        minimum = min(singles[a][i]+singles[b][j]+correction[7*i+j]
                      for i in range(7) for j in range(7))
        need(minimum == 0, "improving unequal pair")
        histogram[minimum] += 1
        digest.update(f"{a},{b}:{minimum}\n".encode())
        count += 1
    return {"pairs": count, "evaluations": 49*count,
            "minimum_histogram": dict(histogram), "sha256": digest.hexdigest()}


def triple_census(helpers, singles, corrections):
    adjacency = {h: set() for h in helpers}
    for a, b in corrections:
        adjacency[a].add(b)
        adjacency[b].add(a)
    triples = sorted({tuple(sorted((h, a, b))) for h in helpers
                      for a, b in combinations(sorted(adjacency[h]), 2)})
    need(len(triples) <= 60000, "connected triple capacity")
    connected, disconnected = 0, 0
    for a, b, c in combinations(helpers, 3):
        edges = int(b in adjacency[a])+int(c in adjacency[a])+int(c in adjacency[b])
        connected += int(edges >= 2)
        disconnected += int(edges < 2)
    need(connected == len(triples), "independent all-triple coverage")
    digest, histogram = sha256(), Counter()
    for a, b, c in triples:
        ab = corrections.get((a, b), ZERO)
        ac = corrections.get((a, c), ZERO)
        bc = corrections.get((b, c), ZERO)
        sa, sb, sc = singles[a], singles[b], singles[c]
        minimum = 0
        for i in range(7):
            for j in range(7):
                fixed = sa[i]+sb[j]+ab[7*i+j]
                for k in range(7):
                    value = fixed+sc[k]+ac[7*i+k]+bc[7*j+k]
                    minimum = min(minimum, value)
        need(minimum == 0, "improving unequal triple")
        histogram[minimum] += 1
        digest.update(f"{a},{b},{c}:{minimum}\n".encode())
    return {"connected_triples": len(triples), "disconnected_triples": disconnected,
            "all_triples": connected+disconnected, "evaluations": 343*len(triples),
            "minimum_histogram": dict(histogram), "sha256": digest.hexdigest()}


def decomposed_delta(shifts, singles, corrections):
    total = sum(singles[h][d+3] for h, d in shifts.items())
    for a, b in combinations(sorted(shifts), 2):
        total += corrections.get((a, b), ZERO)[7*(shifts[a]+3)+shifts[b]+3]
    return total


def controls():
    rng = random.Random(1029)
    comparisons = 0
    for _ in range(40):
        helpers = (0, 1, 2)
        gauges = {h: rng.randrange(-1, 2) for h in helpers}
        terms = tuple((bool(rng.randrange(2)), rng.randrange(-2, 3), t, s)
                      for t, s in ((0, -1), (-1, 1), (0, 1), (2, 0), (1, 2)))
        incident, _, shared = graph(terms, helpers, gauges)
        singles, corrections = curves(helpers, gauges, incident, shared)
        before = objective(terms, gauges)
        for values in product(SHIFTS, repeat=3):
            shifts = dict(zip(helpers, values))
            after = {h: gauges[h]+shifts[h] for h in helpers}
            need(decomposed_delta(shifts, singles, corrections)
                 == objective(terms, after)-before, "literal objective control")
            comparisons += 1
    need(f(True, 0) == -1 and f(False, 0) == 0, "point discount control")
    terms = ((True, -1, 0, -1),)
    need(objective(terms, {0: 1}) == objective(terms, {}), "paid boundary control")
    need(f(True, 0)-f(True, -1) == -2, "boundary omission would improve")
    bad = ((True, 10, 0, -1),) * 3
    incident, pairs, _ = graph(bad, (0,), {})
    try:
        clipping((0,), {}, incident, pairs)
    except ValueError as error:
        need(str(error) == "unbounded clipping premise", "clipping rejection cause")
    else:
        raise ValueError("unjustified clipping accepted")
    return {"synthetic_graphs": 40, "literal_comparisons": comparisons,
            "tariff_controls": 3, "clipping_rejection_controls": 1}


def actual_clipping_controls(terms, helpers, gauges):
    rng = random.Random(237)
    before = objective(terms, gauges)
    for _ in range(16):
        chosen = rng.sample(helpers, 3)
        shifts = {h: rng.choice((-2**32, -16, -7, -4, 4, 7, 16, 2**32)) for h in chosen}
        changed = {h: gauges.get(h, 0)+shifts.get(h, 0) for h in helpers}
        clipped = {h: gauges.get(h, 0)+max(-3, min(3, shifts.get(h, 0))) for h in helpers}
        excess = sum(max(0, abs(d)-3) for d in shifts.values())
        need(objective(terms, changed)-objective(terms, clipped) >= 8*excess,
             "literal large-shift clipping")
        need(objective(terms, clipped) >= before, "literal clipped endpoint")
    return 16


def main():
    word, programs, inherited, pins = load_inputs()
    helpers = eligible(word, programs)
    need(tuple(inherited["eligible_helpers"]) == helpers, "predecessor domain")
    results = {}
    for orientation in ("forward", "backward"):
        gauges = {int(h): k for h, k in inherited["orientations"][orientation]["gauges"].items()}
        need(set(gauges) <= set(helpers), "gauge support")
        need(all(type(k) is int and abs(k) <= 2 for k in gauges.values()), "gauge capacity")
        terms = terms_from(programs[orientation], helpers)
        incident, pairs, shared = graph(terms, helpers, gauges)
        clip = clipping(helpers, gauges, incident, pairs)
        need(clip["minimum_lower_bound"] >= 8, "quantitative eight-unit clipping")
        singles, corrections = curves(helpers, gauges, incident, shared)
        need(all(min(row) == 0 for row in singles.values()), "improving singleton")
        results[orientation] = {"ADD_terms": len(terms), "helpers": len(helpers),
                                "interaction_edges": len(shared), "clipping": clip,
                                "singletons": {"count": len(helpers), "evaluations": 7*len(helpers)},
                                "pairs": pair_census(helpers, singles, corrections),
                                "triples": triple_census(helpers, singles, corrections),
                                "large_shift_controls": actual_clipping_controls(terms, helpers, gauges)}
    result = {"status": "PASS_K8_UNEQUAL_TRIPLE_CLOSURE", "orientations": results,
              "controls": controls(), "sources": pins}
    result["package_sha256"] = {p.name: sha256(bounded_read(p, 1024*1024)).hexdigest()
                                for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
