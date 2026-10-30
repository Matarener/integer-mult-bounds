"""Source-bound complete macro lowering for the three pooled providers.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
This is a static exact compilation audit, not a physical execution theorem.
"""
import argparse
import ast
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
import types

HERE = Path(__file__).resolve().parent
BASE = "12fa8c5c844be21bfefb38a19503fbd867a11244"
BUNDLE_SHA256 = "91226b99943069f21d845c3242b54ba492418d1194422d04cf2569fd14cbb9ea"
SOURCE_PINS = {
    'research/physical-scalar-stream/scalar_words.py': 'f4293c5ea5a7b65be920997f2ff33ce046ae3d9707ecbcecb3bd163d821dfd00',
    'research/physical-scalar-stream/scalar_engine.py': 'be74c74862ff2b152d3752cb887c6682ddf2d889bc9f16f6328e418618e4c8b6',
    'research/physical-complex-controller/scalar_packets.py': 'cc48f726325c000ab2304eb691feb950ff4abeab5c537d6165d5b3322dc45c35',
    "research/t74-physical-layer/compile_word.py": "1ae8eeedd1a3e8fea68762550d6f7c9495112785ed82bf824d8f82eba21f64a2",
    "research/t74-physical-layer/t74_machine.py": "3bc4c40f275852cea82dbdcf41b8e586bae2e599112ee073a367acc66f37ce83",
    "research/t74-physical-layer/PROOF.md": "1054f13f3e370a2e5d5f5cbc0e767e84927d4879f4c7be54cccb9b9a6a58e8ba",
    "research/physical-complex-controller/scalar_program.py": "4c005167b4c2fe0d98d2dd93b7f931b251259417ff4392b67ee0fbe290f6d48a",
    "research/physical-complex-controller/bank_packets.py": "83e2f80fb72c906ccc7857f2b5139758ca8a997b17f51a5db29e2bb3c1143477",
    "research/physical-complex-controller/machine.py": "b648792a361fdf98597a2f56c634767508be8e818b82e482fbfc60b5c63cc855",
    "research/physical-complex-compact/PROOF.md": "ec6395822ae500242f3fe5e2cf40caf9a7f9fa259d475d2c14970d951ff4df48",
    "research/physical-gaussian-leaf/inputs/pr3087.tar": "d7e9c04a5e6d3f76158555d84080786c7cd8028ca31a61c9399de2b2c67bfd53",
}
NATIVE_PINS = {
    "gauge44": {
        "CANONICAL-WORD.json.gz": "f07fae1011160b53e2df1f3135465db1277a093319de2a1da52d648f00a39542",
        "LOCAL-PROGRAMS.json.gz": "67d700388eaa162e008e7d6f588278fb429872cfc5b56b7dcddc9f576316bc72",
        "CLIFFORD-RECIPES.json": "bf88fc775e883227bbea9532ebf97df9e29576054dc0a893f8dc7fa1dc9744e2",
        "RESIDUAL-ADAPTERS.json": "4711da8324861b5ab4d50dbcf1404c7f14c1b20b87bb750959912ff5da1c2e76",
    },
    "extra": {
        "CANONICAL-WORD.json.gz": "882271d70602354cbada8d77f479703ccc6c47e689e8ccd91f9e4c87de0f4379",
        "LOCAL-PROGRAMS.json.gz": "67d700388eaa162e008e7d6f588278fb429872cfc5b56b7dcddc9f576316bc72",
        "CLIFFORD-RECIPES.json": "3d90c6657966224c7b92e85dddec28633ef7fd56af9eafeeb44fef468605ff06",
        "RESIDUAL-ADAPTERS.json": "e14450952c98caa3f948527a3dd107555381eed6a08dd041bc859d142aa3522d",
    },
    "extra-four": {
        "CANONICAL-WORD.json.gz": "06168f8f432aa153a0605177e95239261d093894f1c3cc826fcd98fc5671c2f3",
        "LOCAL-PROGRAMS.json.gz": "d1f91c2d18262e4aff221fa0daa8441a968ececc4fd53ae3b52b4db9afb5aaba",
        "CLIFFORD-RECIPES.json": "d259754558d9616665069423644a71535b5c331a565c77211b9719f0a319d29d",
        "RESIDUAL-ADAPTERS.json": "e14450952c98caa3f948527a3dd107555381eed6a08dd041bc859d142aa3522d",
    },
}
PROFILES = {
    "gauge44": {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8},
    "extra": {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8},
    "extra-four": {1: 2489, 2: 713, 3: 227, 4: 99, 5: 20, 8: 8},
}


def need(condition, label):
    if not condition:
        raise ValueError(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def checked(path, expected):
    need(path.is_file() and not path.is_symlink(), "regular input: " + str(path))
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, "source drift: " + str(path))
    return raw


def module(name, raw):
    result = types.ModuleType(name)
    result.__file__ = name
    exec(compile(raw, name, "exec", optimize=0), result.__dict__)
    return result


def member(raw, name):
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        rows = [r for r in archive.getmembers() if r.name == name]
        need(len(rows) == 1 and rows[0].isfile(), "unique regular retained member")
        return archive.extractfile(rows[0]).read()


def affine_lowerer(archive):
    compact = member(archive, "inputs/pr3055.tar")
    need(sha256(compact).hexdigest() == "c76e11cce0696db643715a362631b60fb14f26ba66c1e3bb5b5b0389eb52e95d", "PR3055 nested pin")
    original = member(compact, "inputs/pr2250.tar")
    need(sha256(original).hexdigest() == "f7c4412bed944228e911c370d847d057a68d27b7d80aac86964b396df6a31756", "PR2250 nested pin")
    raw = member(original, "monomial.py")
    need(sha256(raw).hexdigest() == "394f9a465ac9148af0c20844d375e4befbef17d92b2fcc840d83419480dd4740", "PR2250 monomial body pin")
    tree = ast.parse(raw)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "binary_word"]
    need(len(nodes) == 1, "one retained pure affine lowerer")
    namespace = {"need": need}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "PR2250.binary_word", "exec", optimize=0), namespace)
    return namespace["binary_word"], raw


def check_recipe(record, binary_word):
    m = len(record["matrix_rows"])
    need(m == 9, "complete native nine-coordinate recipe")
    need(len(record["linear_Z4"]) == len(record["quadratic_rows"]) == m, "complete native phase")
    need(all(type(v) is int and 0 <= v < 4 for v in record["linear_Z4"]), "Z4 linear coefficients")
    need(type(record["phase"]) is int and 0 <= record["phase"] < 4, "Z4 constant")
    need(0 <= record["offset"] < (1 << m), "affine offset")
    extended = dict(matrix_rows=record["matrix_rows"] + [1 << i for i in range(m, 73)],
                    offset=record["offset"])
    code = binary_word(extended)
    # A row is an affine polynomial over F2. Equality proves all 2^73 addresses.
    constant = 1 << 73
    rows = [1 << i for i in range(73)]
    for kind, target, source in code:
        need(kind in ("add", "flip") and 0 <= target < 73, "fixed affine alphabet")
        rows[target] ^= rows[source] if kind == "add" else constant
    expected = [v ^ (constant if record["offset"] >> i & 1 else 0)
                for i, v in enumerate(extended["matrix_rows"])]
    need(rows == expected, "all-address affine identity")
    for kind, target, source in reversed(code):
        rows[target] ^= rows[source] if kind == "add" else constant
    need(rows == [1 << i for i in range(73)], "all-address inverse affine identity")
    # Exhaust every native address; higher 64 coordinates are explicit spectators.
    phases = []
    quadratic = tuple((i, j) for i in range(m) for j in range(i + 1, m)
                      if record["quadratic_rows"][i] >> j & 1)
    for x in range(1 << m):
        direct = record["phase"] + sum(a for i, a in enumerate(record["linear_Z4"]) if x >> i & 1)
        direct += 2 * sum(((record["quadratic_rows"][i] >> (i + 1)) & (x >> (i + 1))).bit_count()
                          for i in range(m) if x >> i & 1)
        compiled = record["phase"] + sum(a * (x >> i & 1) for i, a in enumerate(record["linear_Z4"]))
        compiled += 2 * sum((x >> i & 1) * (x >> j & 1) for i, j in quadratic)
        need(direct % 4 == compiled % 4, "complete native phase table")
        phases.append(direct % 4)
    # Both source orders incur their actual Compact multiplicity.
    compact_calls = sum(4 if kind == "flip" or source < target else 12
                        for kind, target, source in code)
    return len(code), len(quadratic), compact_calls, sha256(bytes(phases)).hexdigest()


def rejection(compiler, original, mutation):
    data = deepcopy(original)
    mutation(data)
    try:
        compiler(data, "forward").run()
    except (ValueError, KeyError):
        return True
    raise ValueError("accepted invalid lifetime or recursive tariff")


def audit_new_instructions(compiler, data, direction, code, ranges):
    """Independent event-to-macro checks for the added source alphabet."""
    instance = compiler(data, direction)
    events = data["programs"][direction]
    need(len(events) == len(ranges), "one ordered range per authenticated event")
    next_index = 0
    for i, event in enumerate(events):
        start, end = ranges[i]
        need(start == next_index and start < end <= len(code), "contiguous source ranges")
        need(all(op[1] == i for op in code[start:end]), "exact source-event provenance")
        next_index = end
        if event[0] == "warp":
            _, role, operation, old, new = event
            key = (1 if operation > 0 else -1, abs(operation), old, new)
            record = instance.warps[key]
            digest = sha256(canonical(record["left"])).hexdigest()
            need(code[start:end] == (("monomial", i, instance.slot(role), digest, False),),
                 "exact directed warp recipe, target and non-inverted invocation")
        elif event[0] == "zero_buffer":
            opcode = "zero" if event[1] == "alloc" else "release_zero"
            need(code[start:end] == ((opcode, i, instance.zmap[event[2]]),),
                 "allocate/checked-release exact private Z slot")
    need(next_index == len(code), "no trailing unbound instructions")


def calculate(repo, providers):
    raw = {name: checked(repo / name, digest) for name, digest in SOURCE_PINS.items()}
    native = module("pooled_retained_t74_compiler", raw["research/t74-physical-layer/compile_word.py"])
    scalar = module("pooled_retained_scalar_lowerer", raw["research/physical-complex-controller/scalar_program.py"])
    binary_word, monomial_raw = affine_lowerer(raw["research/physical-gaussian-leaf/inputs/pr3087.tar"])
    reports, recipes, scalars, originals = {}, {}, {}, {}
    for provider, pins in NATIVE_PINS.items():
        for name, digest in pins.items():
            checked(providers / provider / name, digest)
        data = native.read_native(providers / provider)
        originals[provider] = data
        reports[provider] = {}
        for direction in ("forward", "backward"):
            code, selected, ranges = native.Compiler(data, direction).run()
            es = data["programs"][direction]
            need(len(ranges) == len(es), "all source events covered")
            need(all(code[j][1] == i for i, (a, b) in enumerate(ranges) for j in range(a, b)), "ordered event coverage")
            audit_new_instructions(native.Compiler, data, direction, code, ranges)
            profile = Counter(op[3] for op in code if op[0] == "child")
            need(dict(profile) == PROFILES[provider], "changed complete positive-child profile")
            expected = 22808 if provider == "extra-four" else 22807
            need(len(es) == expected, "actual changed event inventory")
            for i, event in enumerate(es):
                a, b = ranges[i]
                if event[0] == "warp":
                    need(b == a + 1 and code[a][0] == "monomial", "one monomial and zero children per warp")
                elif event[0] == "zero_buffer":
                    need(b == a + 1 and code[a][0] == ("zero" if event[1] == "alloc" else "release_zero"), "one full-packet zero operation per Z event")
            need(len(code) < 65536, "local program counter capacity")
            for key, record in selected.items():
                need(key not in recipes or recipes[key] == record, "shared monomial content")
                recipes[key] = record
            for op in code:
                if op[0] == "scalar" and op[4] not in scalars:
                    scalars[op[4]] = scalar.ScalarProgram(*op[4])
            reports[provider][direction] = {
                "source_events": len(es), "instructions": len(code),
                "instruction_counts": dict(Counter(op[0] for op in code)),
                "paid_profile": dict(sorted(profile.items())),
                "local_code_sha256": sha256(canonical(code)).hexdigest(),
                "zero_map": {str(k): v for k, v in native.Compiler(data, direction).zmap.items()},
                "source_warps": sum(e[0] == "warp" for e in es),
                "source_zero_events": sum(e[0] == "zero_buffer" for e in es),
                "scalar_recipe_instructions_plus_packet_zero_copy_release": sum(len(scalars[op[4]].program) if op[0] == "scalar" else
                                                int(op[0] in ("zero", "copy", "release_zero")) for op in code),
            }
    need(len(scalars) == 36, "actual pooled scalar vocabulary")
    guards = [scalar.prefix_guard(value) for value in scalars.values()]
    need(max(g[0] for g in guards) == 3 and max(g[1] for g in guards) == 9, "exact scalar prefix guards")
    recipe_rows = {key: check_recipe(rec, binary_word) for key, rec in sorted(recipes.items())}
    controls = []
    original = originals["extra-four"]
    def missing_release(data):
        es = data["programs"]["forward"]
        es.pop(next(i for i, e in enumerate(es) if e[:2] == ["zero_buffer", "free"]))
    def early_release(data):
        next(e for e in data["programs"]["forward"] if e[:2] == ["zero_buffer", "alloc"])[1] = "free"
    def wrong_frame(data):
        next(e for e in data["programs"]["forward"] if e[0] == "warp")[3] = -1
    def paid_warp(data):
        e = next(e for e in data["programs"]["forward"] if e[0] == "warp")
        row = next(r for r in data["native"]["warps"] if (r["sign"], r["op"], r["old"], r["new"]) == (1 if e[2] > 0 else -1, abs(e[2]), e[3], e[4]))
        row["rank"] = 1
    for label, fn in (("missing_Z_release", missing_release), ("Z_release_before_allocation", early_release),
                      ("wrong_warp_source_frame", wrong_frame), ("unpriced_positive_rank_warp", paid_warp)):
        rejection(native.Compiler, original, fn)
        controls.append(label)
    code, _, ranges = native.Compiler(original, "forward").run()
    warp_index = next(i for i, event in enumerate(original["programs"]["forward"]) if event[0] == "warp")
    w = ranges[warp_index][0]
    free_index = next(i for i, event in enumerate(original["programs"]["forward"]) if event[:2] == ["zero_buffer", "free"])
    z = ranges[free_index][0]
    mutations = {
        "lowered_warp_omitted": lambda c: c.__setitem__(w, ("identity", *c[w][1:3])),
        "lowered_warp_inverted": lambda c: c.__setitem__(w, (*c[w][:-1], True)),
        "lowered_warp_wrong_recipe": lambda c: c.__setitem__(w, (*c[w][:3], "0" * 64, False)),
        "Z_release_changed_to_unchecked_clear": lambda c: c.__setitem__(z, ("zero", *c[z][1:])),
        "Z_release_wrong_private_slot": lambda c: c.__setitem__(z, (*c[z][:-1], c[z][-1] + 1)),
    }
    for label, mutate in mutations.items():
        changed = list(code)
        mutate(changed)
        try:
            audit_new_instructions(native.Compiler, original, "forward", tuple(changed), ranges)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError("accepted wrong lowering: " + label)
    return {
        "status": "PASS_POOLED_SIX_PROGRAM_LOCAL_LOWERING_NOT_GLOBAL_MACHINE_ADMISSION",
        "base_commit": BASE, "source_sha256": SOURCE_PINS, "native_sha256": NATIVE_PINS,
        "programs": reports, "persistent_roles": 632, "private_centre_roles": 8, "private_Z_roles": 91,
        "local_packet_roles": 731, "scalar_literals": len(scalars),
        "scalar_maximum_instructions": max(len(value.program) for value in scalars.values()),
        "scalar_prefix_denominator_bits": 3, "scalar_prefix_l1": "9",
        "monomial_literals": len(recipes), "native_phase_columns_per_literal": 512,
        "maximum_affine_gates": max(row[0] for row in recipe_rows.values()),
        "maximum_quadratic_terms": max(row[1] for row in recipe_rows.values()),
        "maximum_ordinary_calls_per_outer_row_per_monomial": max(row[2] for row in recipe_rows.values()),
        "affine_coverage": "Every 73-bit address by symbolic affine forms, both directions",
        "recipe_sha256": sha256(canonical(recipe_rows)).hexdigest(),
        "inherited_affine_source_sha256": sha256(monomial_raw).hexdigest(),
        "controls": controls,
        "scope": "Unchanged retained compiler on all six exact current programs; independent symbolic affine check; complete finite native phase table; source-preserving scalar prefix identities. All-width primitive, complete global owner binding, physical ordinary B2 and outer transfer are separate written contracts. No physical payload execution or formal-kernel proof.",
    }


@contextmanager
def frozen_inputs():
    """Validate the complete immutable closure before writing regular members."""
    pin_path = HERE / "PHYSICAL-PINS.json"
    need(pin_path.is_file() and not pin_path.is_symlink(), "regular physical manifest")
    pins = json.loads(pin_path.read_bytes())
    need(pins["base_commit"] == BASE and pins["source_sha256"] == SOURCE_PINS
         and pins["native_sha256"] == NATIVE_PINS, "manifest scientific commitments")
    bundle = pins["bundle"]
    need(bundle["path"] == "frozen/physical-t74/SOURCE-BUNDLE.tar.gz"
         and bundle["sha256"] == BUNDLE_SHA256, "fixed physical closure archive")
    compressed = checked(HERE / bundle["path"], BUNDLE_SHA256)
    need(len(compressed) == bundle["bytes"] and len(compressed) < 3 * 2**20, "bounded compressed closure")
    raw = gzip.decompress(compressed)
    need(len(raw) < 12 * 2**20, "bounded decompressed closure")
    members = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        for entry in archive.getmembers():
            path = PurePosixPath(entry.name)
            need(entry.isfile() and not path.is_absolute() and ".." not in path.parts
                 and "\\" not in entry.name and path.as_posix() == entry.name
                 and entry.name not in members, "unique regular contained archive member")
            need(entry.name in bundle["files"] and entry.size <= 2 * 2**20, "declared bounded member")
            value = archive.extractfile(entry).read()
            expected = bundle["files"][entry.name]
            need(len(value) == entry.size == expected["bytes"]
                 and sha256(value).hexdigest() == expected["sha256"], "exact physical source member")
            members[entry.name] = value
    need(set(members) == set(bundle["files"]) and len(members) == 26, "complete physical closure inventory")
    with tempfile.TemporaryDirectory(prefix="pooled-physical-local-") as directory:
        root = Path(directory)
        for name, value in members.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        yield root / "source", root / "native"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--release-providers", type=Path,
                   help="Also bind all twelve native files to a fresh completed release provider directory")
    p.add_argument("--out", type=Path, help="Optional receipt outside this published package")
    a = p.parse_args()
    if a.out:
        target = a.out.resolve()
        need(target != HERE and HERE not in target.parents, "receipt must be outside the published package")
    if a.release_providers:
        for provider, paths in NATIVE_PINS.items():
            for name, digest in paths.items():
                checked(a.release_providers / provider / name, digest)
    with frozen_inputs() as (repo, providers):
        result = calculate(repo, providers)
    result["source_bundle_sha256"] = BUNDLE_SHA256
    if a.out:
        a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(result["status"], "programs", 6, "monomials", result["monomial_literals"], "controls", len(result["controls"]))


if __name__ == "__main__":
    main()
