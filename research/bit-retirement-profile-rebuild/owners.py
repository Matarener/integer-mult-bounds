"""Independent literal parent-owner and QUERY census for compact PR4326.

Only standard-library data readers are used. No retained producer/checker is
imported or executed. The terminal geometry is rational, not binary rank.
ai-nanachi's compact source and internal independent checks retain credit.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json


SOURCE = Path(__file__).resolve().parent / "source"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                   separators=(",", ":")).encode()).hexdigest()


def rational_span(rows, dimension):
    """Canonical row space over Q; enough for exact projector-image equality."""
    matrix = [[Fraction(x) for x in row] for row in rows]
    require(all(len(row) == dimension for row in matrix), "rational vector size")
    pivot_row = 0
    for column in range(dimension):
        pivot = next((r for r in range(pivot_row, len(matrix))
                      if matrix[r][column]), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        divisor = matrix[pivot_row][column]
        matrix[pivot_row] = [x / divisor for x in matrix[pivot_row]]
        for r in range(len(matrix)):
            if r != pivot_row and matrix[r][column]:
                factor = matrix[r][column]
                matrix[r] = [x - factor * y
                             for x, y in zip(matrix[r], matrix[pivot_row])]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return tuple(tuple(row) for row in matrix[:pivot_row])


def orthogonal(matrix, dimension, label):
    require(len(matrix) == dimension
            and all(len(row) == dimension for row in matrix), label + " shape")
    for i in range(dimension):
        for j in range(dimension):
            require(sum(matrix[r][i] * matrix[r][j] for r in range(dimension))
                    == int(i == j), label + " orthogonality")


def geometry_contract(word, geometry, caller, charts, widths):
    """Bind chart images to actual terminal Q spans and full relative maps."""
    h, m = geometry["h"], caller["m"]
    require(type(h) is int and h > 1 and type(m) is int and m > h,
            "address dimensions")
    ports = caller["ports"]
    require(ports and [p["port"] for p in ports] == list(range(len(ports))),
            "ordered actual source ports")
    require(caller["h"] == h and caller["ambient_form"] == f"I_{m}/2"
            and geometry["form"] == "<x,y>/2", "rational geometry contract")
    data_roles = 2 * len(ports)
    require(len(word["final"]) == data_roles + len(widths),
            "actual helper namespace")
    family = charts["family_charts"]
    require(len(family) == len(ports), "all family factors retained")
    for port, matrix in zip(ports, family):
        matrix = [[Fraction(x) for x in row] for row in matrix]
        orthogonal(matrix, h, "family chart")
        q = list(map(Fraction, port["q"]))
        require(q == list(map(Fraction, geometry["lines"][port["port"]])),
                "family q source binding")
        complement = [[Fraction(x) for x in row]
                      for row in port["complement_columns"]]
        basis = [[q[r] / 2, *complement[r]] for r in range(h)]
        orthogonal(basis, h, "family q/complement")
        # The old caller and new chart may choose different orthonormal
        # complements of q. Bind the actual full isometry and distinguished
        # q direction; do not silently identify those complement conventions.
        require([matrix[r][0] for r in range(h)] == [x / 2 for x in q],
                "actual family factor q direction")

    terminal = {}
    for frame in set(word["final"][data_roles:]):
        require(type(frame) is int and 0 <= frame < len(geometry["frames"]),
                "terminal frame index")
        span = rational_span([geometry["lines"][i]
                              for i in geometry["frames"][frame]], h)
        matrix = [[Fraction(x) for x in row]
                  for row in charts["terminal_bases"][str(frame)]]
        orthogonal(matrix, h, "terminal chart")
        k = len(span)
        require(rational_span([[matrix[r][j] for r in range(h)]
                               for j in range(k)], h) == span,
                "actual terminal projector image")
        terminal[frame] = (matrix, k)
    for helper, width in enumerate(widths):
        require(type(width) is int and 0 < width <= h
                and terminal[word["final"][data_roles + helper]][1] == width,
                "independently supplied helper width differs from Q rank")

    relative = {}
    for chart in charts["relative_charts"]:
        identifier, frame, axes = chart["id"], chart["terminal_frame"], chart["axes"]
        require(type(identifier) is int and identifier not in relative,
                "relative chart id")
        require(frame in terminal, "unbound terminal relative chart")
        basis, width = terminal[frame]
        permutation = chart["permutation"]
        require(sorted(permutation) == list(range(m))
                and permutation[:width] == axes, "literal relative support")
        inverse = {target: source for source, target in enumerate(permutation)}
        actual = chart["relative_matrix"]
        require(len(actual) == m and all(len(row) == m for row in actual),
                "relative map shape")
        # The complete map is P (B^T direct_sum I), not just its rank.
        for target in range(m):
            source = inverse[target]
            for column in range(m):
                expected = (basis[column][source]
                            if source < h and column < h
                            else Fraction(int(source == column and source >= h)))
                require(Fraction(actual[target][column]) == expected,
                        "complete relative terminal map")
        relative[identifier] = (frame, tuple(axes), width)
    return h, m, len(ports), relative


def controller_contract(order, caller, h, m):
    """Derive child axes and inactivity intervals from literal controller events."""
    events, calls = order["controller"], order["calls"]
    local = {event["stage"]: (position, event)
             for position, event in enumerate(events) if event["kind"] == "local"}
    require(len(local) == sum(e["kind"] == "local" for e in events)
            and set(local) == set(range(len(local))), "one controller per stage")
    stages = len(local)
    require(stages == caller["stages"] and m == 1 + (h - 1) * stages,
            "nested exterior-block address decomposition")
    pairs = {e["pair"] for e in events if "pair" in e}
    require(pairs == set(range(len(pairs))), "complete pair labels")
    levels, touched = {p: -1 for p in pairs}, {p: -1 for p in pairs}
    children, windows = {}, {}
    for position, event in enumerate(events):
        kind = event["kind"]
        if kind == "local":
            pair, stage = event["pair"], event["stage"]
            require(type(event["reverse"]) is bool and levels[pair] < stage,
                    "ordered local level advance")
            levels[pair], touched[pair] = stage, position
        elif kind == "idle":
            child, pair = event["idx"], event["pair"]
            before, after = levels[pair], event["target_level"]
            require(child not in children and event["source_level"] == before
                    and before <= after < stages, "literal child level transition")
            axes = list(range(1 + (h - 1) * (before + 1),
                              1 + (h - 1) * (after + 1)))
            require(event["axes"] == axes and event["rank"] == len(axes),
                    "child axes derived from nested levels")
            children[child] = {"pair": pair, "axes": axes}
            eligible = [stage for stage, (at, _) in sorted(local.items())
                        if touched[pair] < at < position]
            windows[child] = {"lower_open_event": touched[pair],
                               "upper_open_event": position, "stages": eligible}
            levels[pair] = after
        elif kind == "bridge":
            src, dst = event["src"], event["dst"]
            require(src in pairs and dst in pairs and src != dst
                    and event["coefficient"] in (-1, 1)
                    and levels[src] == levels[dst], "literal bridge boundary")
            touched[src] = touched[dst] = position
        elif kind == "exchange":
            for pair in pairs:
                touched[pair] = position
        else:
            raise ValueError("unknown parent controller event")
    require(set(children) == set(range(len(children))), "all child labels")
    require({str(k): v for k, v in windows.items()} == order["windows"],
            "saved windows differ from actual controller chronology")
    replicas = {row["replica"] for row in calls}
    require(replicas == set(range(len(replicas))) and replicas, "replica labels")
    expected = [{"event": local[stage][0], "replica": replica, "stage": stage}
                for stage in sorted(local) for replica in sorted(replicas)]
    require(calls == expected, "all literal calls exactly once in event order")
    return local, children, windows, len(pairs), len(replicas)


def profile_from_factors(local_profile, calls, factors, replicas):
    profile = Counter()
    for _ in calls:
        profile.update(local_profile)
    for _ in range(replicas):
        profile.update(len(axes) for _, _, axes in factors if axes)
    return profile


def compare_claims(profile, live, private, record):
    require(sum(profile.values()) == record["query_count"],
            "derived QUERY count disagrees with copied RECORD")
    require(sum(r * n for r, n in profile.items()) == record["rankmass"],
            "derived rank mass disagrees with copied RECORD")
    require(live == record["W"] and private == record["private"],
            "DATA/private stock disagrees with copied RECORD")


def run(helper_widths, local_profile, *, source_dir=None, controls=True):
    """Return a fresh full census; claims and saved complements are outputs only."""
    source = Path(source_dir) if source_dir is not None else SOURCE
    provider = source / "provider"
    word = read(provider / "inputs/WORD.json.gz")
    geometry = read(provider / "inputs/GEOMETRY.json.gz")
    caller = read(provider / "inputs/CALLER-GEOMETRY.json.gz")
    charts = read(provider / "new-owners/CHARTS.json.gz")
    order = read(provider / "new-owners/ORDER.json.gz")
    slots = read(provider / "new-owners/SLOTS.json.gz")
    dispatch = read(provider / "new-owners/DISPATCH.json.gz")
    widths = list(helper_widths)
    local_profile = Counter({int(rank): count for rank, count in local_profile.items()})
    h, m, ports, relative = geometry_contract(word, geometry, caller, charts, widths)
    require(local_profile and all(type(n) is int and n > 0 and 0 < r < h
                                 for r, n in local_profile.items()), "local profile")
    local, children, windows, pairs, replicas = controller_contract(order, caller, h, m)
    members, data_roles = 2 * ports, 2 * ports
    nominations, used, support = {}, defaultdict(set), defaultdict(set)
    for child, member, offset, width, stage, helper in slots:
        require(all(type(x) is int for x in (child, member, offset, width, stage, helper)),
                "integer literal owner slot")
        require(child in children and 0 <= member < members
                and stage in local and 0 <= helper < len(widths), "owner slot labels")
        require((stage, helper) not in nominations, "duplicate helper occurrence")
        require(width == widths[helper], "slot width differs from actual terminal rank")
        require(stage in windows[child]["stages"]
                and children[child]["pair"] != local[stage][1]["pair"],
                "owner not inactive/unobserved at actual local call")
        all_axes = children[child]["axes"]
        require(offset >= 0 and width > 0 and offset + width <= len(all_axes),
                "occupied owner axis extent")
        axes = all_axes[offset:offset + width]
        key = (child, member)
        require(not used[key].intersection(axes), "overlapping child owner support")
        physical = (children[child]["pair"], member)
        require(not support[physical].intersection(axes), "overlapping physical owner support")
        used[key].update(axes)
        support[physical].update(axes)
        nominations[stage, helper] = (child, member, offset, width, tuple(axes))
    require(set(nominations) == {(stage, helper) for stage in local
                                 for helper in range(len(widths))},
            "every helper in every stage exactly once")
    factors = []
    for child in sorted(children):
        axes = children[child]["axes"]
        for member in range(members):
            occupied = used[child, member]
            require(occupied == set(axes[:len(occupied)]), "noncompact occupied prefix")
            factors.append([child, member, [a for a in axes if a not in occupied]])

    require(len(dispatch) == len(order["calls"]), "dispatch/call count")
    live = replicas * pairs * members
    data_families, private_families, occurrence_count = set(), set(), 0
    chart_ids = set()
    for call, emitted in zip(order["calls"], dispatch):
        stage, replica = call["stage"], call["replica"]
        event = local[stage][1]
        pair, reverse = event["pair"], event["reverse"]
        require((emitted["stage"], emitted["replica"], emitted["pair"], emitted["orientation"])
                == (stage, replica, pair, "reverse" if reverse else "forward"),
                "literal call orientation/owner identity")
        owners = emitted["owners"]
        require(len(owners) == data_roles + len(widths), "actual compact dispatch arity")
        for role in range(data_roles):
            half, port = divmod(role, ports)
            member = (half ^ int(reverse)) * ports + port
            family = replica * pairs * members + pair * members + member
            require(owners[role] == [family, ["data", stage, port]], "literal DATA owner")
            data_families.add(family)
        for helper in range(len(widths)):
            child, member, offset, width, axes = nominations[stage, helper]
            family = (replica * pairs * members
                      + children[child]["pair"] * members + member)
            actual_family, descriptor = owners[data_roles + helper]
            require(isinstance(descriptor, list) and len(descriptor) == 5,
                    "hosted owner descriptor")
            kind, actual_child, actual_offset, actual_width, chart_id = descriptor
            require((actual_family, kind, actual_child, actual_offset, actual_width)
                    == (family, "hosted", child, offset, width), "literal hosted owner")
            require(chart_id in relative, "bound relative chart id")
            require(relative[chart_id] == (word["final"][data_roles + helper], axes, width),
                    "hosted terminal operator support")
            chart_ids.add(chart_id)
            occurrence_count += 1
        private = emitted["private_owner"]
        require(private == [live + stage, ["private", "d"]], "separate private family")
        private_families.add(private[0])
    require(data_families == set(range(live)) and not data_families & private_families,
            "complete original DATA stock with no private credit")
    claimed = read(provider / "new-owners/REMAINDERS.json.gz")
    require(factors == claimed, "derived literal idle complements differ from saved output")
    profile = profile_from_factors(local_profile, order["calls"], factors, replicas)
    require(all(0 < rank < m for rank in profile), "proper global QUERY ranks")
    record = read(source / "RECORD.json")
    compare_claims(profile, live, len(private_families), record)
    negative = []
    if controls:
        bad = list(widths)
        altered = next(i for i, width in enumerate(bad) if width < h)
        bad[altered] += 1
        try:
            geometry_contract(word, geometry, caller, charts, bad)
        except ValueError as error:
            negative.append({"control": "alter_terminal_width_copied_RECORD_unchanged",
                             "rejected_by": str(error)})
        else:
            raise ValueError("altered terminal width accepted")
        omitted = next(i for i, (_, _, axes) in enumerate(factors) if axes)
        defective = profile_from_factors(local_profile, order["calls"],
                                         factors[:omitted] + factors[omitted + 1:], replicas)
        try:
            compare_claims(defective, live, len(private_families), record)
        except ValueError as error:
            negative.append({"control": "omit_nonzero_idle_copied_RECORD_unchanged",
                             "omitted": factors[omitted], "rejected_by": str(error)})
        else:
            raise ValueError("omitted nonzero idle accepted")
    histogram = Counter(len(axes) for _, _, axes in factors)
    return {"status": "PASS_INDEPENDENT_LITERAL_PARENT_PROFILE",
            "calls": len(order["calls"]), "stages": len(local), "replicas": replicas,
            "ports": ports, "pairs": pairs, "helpers_per_call": len(widths),
            "helper_occurrences": occurrence_count, "all_call_owners_checked": True,
            "local_profile": dict(sorted(local_profile.items())),
            "helper_width_histogram": dict(sorted(Counter(widths).items())),
            "parent_children": len(children), "idle_factors_per_replica_including_zero": len(factors),
            "derived_idle_histogram_including_zero": dict(sorted(histogram.items())),
            "derived_idle_factors_sha256": digest(factors),
            "occupied_support_sha256": digest([[child, member, sorted(axes)]
                                              for (child, member), axes in sorted(used.items())]),
            "full_profile": dict(sorted(profile.items())), "QUERYs": sum(profile.values()),
            "rankmass": sum(rank * count for rank, count in profile.items()),
            "W": live, "private_families": len(private_families),
            "private_receives_DATA_credit": False, "terminal_relative_charts_checked": len(relative),
            "terminal_relative_charts_used": len(chart_ids), "family_factors_checked": ports,
            "negative_controls": negative,
            "scope": "Literal compact owner supports, chronology and paid profile only; no full native/SOURCE operator, physical tape, all-size supplier or outer theorem."}
