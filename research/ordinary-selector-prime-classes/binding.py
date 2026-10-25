"""Read-only source binding for the conditional scalar selector projection.

No source module is imported or executed.  Complete reviewed module syntax is
bound in addition to explicit whole-declaration contracts below.  The latter
are deliberately source-specific, rather than a permissive Python recognizer.
Comments/locations are absent from the AST; docstrings, cleanup and exception
paths remain.  Empty Python-3.12 type_params fields are normalized for Python
version portability; nonempty type parameters are rejected.

Soundness boundary: syntax equality transfers the displayed control flow to
the pinned source.  The loop invariants explain its scalar projection *if*
Count/Counter operations have their retained nonnegative-integer meanings and
the admitted run terminates successfully.  This does not prove those primitive
meanings, physical resource/lifetime obligations, loader behavior, primality,
or native admission.  In particular, none of the archived producer checks is
executed here.  The prime-class theorem and its arithmetic checks are separate.
"""

import ast
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import textwrap


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENCODED = "research/physical-ordinary-interchange/encoded.py"
ORDINARY = "research/physical-ordinary-interchange/ordinary.py"
PRODUCTION = "research/physical-complex-controller/production_native.py"
INTERFACE = "research/retuned-ordinary-coupling/interface.py"
RETUNED = "research/t74-retuned-physical-layer/retuned_native.py"
ACTIVE = "research/t74-retuned-physical-layer/active_sources.py"
PREDECESSOR = "research/retuned-ordinary-coupling/predecessor.py"
ARCHIVE = "research/retuned-ordinary-coupling/inputs/pr2899-export.tar.gz"

# Independent byte authority: never derive these values from SOURCE-PINS.
# (size, SHA256, Git blob SHA1); SOURCE-PINS must agree with this subset.
PINS = {
    ENCODED: (7305, "10ad2fa5902a48d49cf2b89a30b3f2711d63a6a43b9512a6427affcdf07335a7", "2280fa98ff5e4da7c4909814ce4a1c405605ada8"),
    ORDINARY: (8660, "7f8338e748bcd42fbef1e7cc47b6c5040dfb3aad216e34759bcb12b8e14f7705", "81b330a4b886a0f4deab7b0811478bab3fbc107a"),
    PRODUCTION: (1222, "4c1f8f69212162bd297010c6e21a32e31755cbfe2e40f9935b8d87a9e4260d46", "045b0dd1aa6ec47051730fc01fa8b3c6a825ab72"),
    "research/retuned-ordinary-coupling/PROOF.md": (8312, "3e554832c38b4b801f55b20868679f3283bc90cd5a9d8ce1960f828ed2655f22", "8a0f47a1541a0b8e67866df4f65928de31073651"),
    INTERFACE: (858, "25707c61b9fc6c1f09388c7cc72d269be0f8f8cae4dbc7cd5c2d00ce7fadf839", "6479a08fe78f7f4fe93d144cec26ac84aebcf9d3"),
    "research/retuned-ordinary-coupling/check_setup.py": (4269, "5ccea0216b701e3e1adb6bb0890ba3db179b1d7b3d1a6e9913ac1fdc4d56bfca", "3a196ed2ae7030a75f4fadc423e15f0c4fb23193"),
    RETUNED: (890, "4b48f4a0d2900195201cdb8eaf715cb22460de391410e66bee5a6302fd1796dc", "7f51e925db0e4e6885107ad51e09f90b95757900"),
    "research/t74-retuned-physical-layer/check_active_contracts.py": (4148, "d3862b7720a484fef58afcf1c0f0c25f09e8cf33e767cc502a656c1dd65b15e7", "1b6d7f0663c26d170dfb6b33d1dc983f854e2a68"),
    PREDECESSOR: (3336, "4733b33a6a840f73ebc87f0c3f9e9f1aee95438b10eae7f8dbbf20d5b11b2306", "31c08659c843dc114ae84d9c431bd749919c40bc"),
    ARCHIVE: (8202240, "0fef1707c6460418fd01fd49faf0d8ff7945907fa57284765c852a12d2674d3c", "5c07cf429005658400d7a64e229162ea845e5bf7"),
    ACTIVE: (8835, "599c701b15d45f3dfee531a118e11a0aa0997d070e9cce4b6298d5b20defad49", "4f7f8d1aa8ea37aa7e66f6887606821a0b48bbba"),
}

# Hashes use _syntax_bytes, not ast.dump's version-dependent textual display.
MODULE_AST_SHA256 = {
    ENCODED: "6051d9fa7ad3064d615b299e57e4ec4a465d8334be66def8cf78f21244689d8c",
    ORDINARY: "d713330bdd0c4fff25cc6692d578be7f3c85a7dd789958cca35f1ad803565a09",
    PRODUCTION: "879afa146ad5381b3804dff236f2a2223e525148388a83d5a011889296f224bf",
    INTERFACE: "708324a95141e74746aad0deeb7b0efb73d86c1db52da8f4c932f185ee553989",
    "research/retuned-ordinary-coupling/check_setup.py": "e970e047f36ed55a957f5b586ec432da97f79544dad9b111c7d45b4832208ce9",
    RETUNED: "36c2c9b17cb24a3fc7d4e0e84d6e10559ad1af49722b06cd75feb3d08e6be06a",
    "research/t74-retuned-physical-layer/check_active_contracts.py": "03bf096b40078b14dc43fd1ef5e85f8e3ef069bf8618e22ee719ea1f2e3202ea",
    PREDECESSOR: "3ec2b89aab0f0777bb9dee37f5fe500a644f2116aee510ee9c34c3540e7ca693",
    ACTIVE: "21ffd30c446237adf81d3996a14beba5072e98ca44af046ef30a666ae4100bbe",
}


class BindingError(ValueError):
    """Fail-closed source/contract mismatch, including a stable component."""

    def __init__(self, component, reason):
        self.component, self.reason = component, reason
        super().__init__(component + ": " + reason)


def _need(ok, component, reason):
    if not ok:
        raise BindingError(component, reason)


def _form(node):
    if isinstance(node, ast.AST):
        fields = []
        for name, value in ast.iter_fields(node):
            if name == "type_params":
                _need(value == [], "syntax", "nonempty type parameters")
                continue
            fields.append([name, _form(value)])
        return [type(node).__name__, fields]
    if isinstance(node, list):
        return [_form(value) for value in node]
    return node


def _syntax_bytes(node):
    return json.dumps(_form(node), ensure_ascii=True, sort_keys=True,
                      separators=(",", ":")).encode("ascii")


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _declaration(tree, qualified):
    scope = tree
    for name in qualified.split("."):
        found = [node for node in scope.body
                 if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name]
        _need(len(found) == 1, qualified, "exactly one declaration")
        scope = found[0]
    return scope


# These are explicit complete declaration contracts, including ownership
# cleanup. They are specifications of the actual syntax, not executed copies.
DECLARATIONS = {
    (ENCODED, "atom_width"): '''
def atom_width(original, numerator=17, denominator=10000):
    """Least w with w^denominator >= e^numerator, by encoded bisection."""
    positive(original)
    target = fixed_power(original, numerator)
    low, high = Count.literal(1), Count(original)
    try:
        while compare(low, high) < 0:
            middle = Count(low)
            middle.add(high)
            middle.divide_small(2)
            power = fixed_power(middle, denominator, target)
            above = compare(power, target) >= 0
            power.close()
            if above:
                high.close()
                high = middle
            else:
                low.close()
                middle.increment()
                low = middle
        result, low = low, None
        return result
    finally:
        if low is not None:
            low.close()
        high.close()
        target.close()
''',
    (ENCODED, "Profile"): '''
@dataclass(frozen=True)
class Profile:
    numerator: int = 17
    denominator: int = 10000
    dimension: int = 64
    child_rank: int = 42
    row_factor: int = 269241600
''',
    (ENCODED, "select"): '''
def select(original, q, profile=Profile()):
    """Return owned encoded parameters; q/profile are compile-time constants."""
    width = atom_width(original, profile.numerator, profile.denominator)
    dimension, one = Count.literal(profile.dimension), Count.literal(1)
    cursor, depth = Count(original), Count.literal(0)
    stock, rows, borrowed = Count.literal(1), Count.literal(1), Count.literal(0)
    body, remainder = Count.literal(0), Count.literal(0)
    try:
        while compare(cursor, dimension) >= 0:
            cursor.divide_small(profile.dimension)
            if profile.child_rank != 1:
                cursor.multiply_small(profile.child_rank)
            depth.increment()
        if not depth.zero():
            order = 1
            for position in range(profile.dimension):
                order *= q ** profile.dimension - q ** position
            level = Count.literal(profile.row_factor * order)
            digits = subtract(width, one)
            repeats = Counter(digits)
            digits.close()
            try:
                while not repeats.finished:
                    level.multiply_small(q ** (profile.dimension ** 2))
                    repeats.decrement()
                levels = Counter(depth)
                try:
                    while not levels.finished:
                        following = Count.product(stock, level)
                        stock.close()
                        stock = following
                        levels.decrement()
                finally:
                    levels.close()
            finally:
                level.close()
                repeats.close()
        while compare(rows, stock) < 0:
            rows.multiply_small(q)
            borrowed.increment()
        twice = Count(borrowed)
        twice.multiply_small(2)
        fits = compare(twice, original) < 0
        twice.close()
        if fits:
            remaining = subtract(original, borrowed)
            body.close()
            remainder.close()
            try:
                body, remainder = divide(remaining, width)
            finally:
                remaining.close()
            fits = compare(body, dimension) >= 0
        return dict(fits=fits, width=width, depth=depth, stock=stock,
                    rows=rows, borrowed=borrowed, body=body, remainder=remainder)
    except BaseException:
        for value in (width, depth, stock, rows, borrowed, body, remainder):
            value.close()
        raise
    finally:
        dimension.close()
        one.close()
        cursor.close()
''',
    (ORDINARY, "Ordinary.execute_plan"): '''
def execute_plan(self, payload, original, prefixes, gap, suffix, plan_factory):
    if self.closed:
        self.rearm()
    need(self.output.read() == BLANK and borrowed_tape(payload) is not self.output,
         "distinct empty ordinary output port")
    for value in (original, prefixes, gap, suffix):
        positive(value)
    with sealed_constructors(), self.scope.installed():
        plan = plan_factory()
        try:
            result = (self.fitted(borrowed_tape(payload), plan, prefixes, gap, suffix)
                      if plan["fits"] else
                      self.fallback(borrowed_tape(payload), original, prefixes, gap, suffix))
            transfer(result, self.output)
            result.clear()
        finally:
            for name, value in plan.items():
                if name != "fits":
                    value.close()
        self.finish(plan["fits"])
    return self.output
''',
    (ORDINARY, "Ordinary.run"): '''
def run(self, payload, original, prefixes, gap, suffix):
    return self.execute_plan(payload, original, prefixes, gap, suffix,
                             lambda: select(original, self.q, self.profile))
''',
    (INTERFACE, "profile"): '''
def profile():
    _, encoded, _ = runtime()
    return encoded.Profile(numerator=1, denominator=577)
''',
    (INTERFACE, "ordinary"): '''
def ordinary(q, binding, topology, programs, **options):
    """Retain the source backend and its selected-source theorem premises.

    Reduced geometries may exercise the interface but do not establish the
    selected odd-prime theorem. This factory changes no global default.
    """
    require("profile" not in options, "one certified coupling profile")
    module, _, _ = runtime()
    return module.Ordinary(q, binding, topology, programs, profile=profile(), **options)
''',
    (INTERFACE, "binary"): '''
def binary(native):
    _, _, module = runtime()
    require(native.profile == profile(), "retuned binary consumer profile")
    return module.Binary(native)
''',
    (RETUNED, "profile"): '''
def profile():
    return active().encoded.Profile(numerator=1, denominator=577)
''',
    (RETUNED, "retune"): '''
def retune(native):
    cohort = active()
    require(isinstance(native, cohort.ordinary.Ordinary) and not native.closed
            and not native.pool.live and native.output.read() == cohort.ordinary.BLANK
            and all(not bank.live and not bank.initialized for bank in native.banks),
            "fresh native from the active cohort")
    current = native.profile
    require((current.dimension, current.child_rank, current.row_factor) == (64, 42, 269241600),
            "unchanged ordinary geometry and stock")
    native.profile = profile()
    return native
''',
    (RETUNED, "build_native"): '''
def build_native():
    cohort = active()
    return retune(cohort.production.build_native(cohort.production.PRIME))
''',
    (PRODUCTION, "build_native"): '''
def build_native(q=PRIME):
    """Fix a source-admissible prime q>2**80 before varying input precision.

    The caller must discharge the selected denominator/chart hypotheses.
    The inherited constructor also performs its finite primality check. This
    factory is explicit but not claimed practically executable at this q.
    """
    from catalogue import Catalogue, Specifications
    from node import selected_topology
    from macro_binding import SelectedBinding
    from macro_code import compile_node
    from encoded import Profile
    from ordinary import Ordinary
    from words import need
    need(type(q) is int and q > 1 << 80, "fixed selected native prime range")
    catalogue = Catalogue(q)
    specifications = Specifications(catalogue)
    topology = selected_topology(catalogue)
    binding = SelectedBinding(specifications)
    programs = (compile_node(topology, binding, mode=0),)
    return Ordinary(q, binding, topology, programs, capacity=1 << 24,
                    profile=Profile(), fixture_index_floor=0)
''',
}


INVARIANTS = [
    {"component": "encoded.atom_width", "invariant": "For e>=1 and profile (1,577), target=e; 1<=low<=ceil(e^(1/577))<=high<=e. Each iteration uses middle=floor((low+high)/2) and min(middle^577,target)>=target iff middle^577>=e, then high=middle or low=middle+1. The nonnegative integer high-low strictly decreases while positive; return low=high is the least w>=1 with w^577>=e."},
    {"component": "encoded.select.depth", "invariant": "Initially cursor=e and depth=0. Each loop with cursor>=64 sets cursor=42*floor(cursor/64) and increments depth once; this strictly contracts positive cursor. Thus depth=D(e), where D(e)=0 for e<64 and D(e)=1+D(42*floor(e/64)) otherwise. It is computed before borrowing from original, never from body or width."},
    {"component": "encoded.select.stock", "invariant": "For D=0 stock remains 1. Otherwise order=product_{i=0}^{63}(q^64-q^i); after j repeats level=269241600*order*q^(4096*j), j=0..w-1. After t levels stock=level^t, t=0..D. Therefore stock=(269241600*|GL_64(F_q)|*q^(4096*(w-1)))^D under the stated prime-field order identity."},
    {"component": "encoded.select.borrowing", "invariant": "Initially rows=1=q^0 and borrowed=0. Each iteration while rows<stock multiplies rows by q and increments borrowed. For integer q>=2 and stock>=1 it terminates at the least k>=0 with q^k>=stock; rows=q^k. Equality with stock terminates; this is covering, not strict padding."},
    {"component": "encoded.select.first_guard", "invariant": "body=remainder=0 initially. The first fits is exactly 2*k<e. If false, division is skipped, both zeros remain, and fits is false. If true, remaining=e-k>0, so divide receives a nonnegative numerator and positive w."},
    {"component": "encoded.select.body_guard", "invariant": "Only after the first guard, (body,remainder)=divmod(e-k,w); e=k+body*w+remainder and 0<=remainder<w. The final fits is body>=64. Body/remainder remain the computed values when this second guard fails. Both guards use original e and the selected w."},
    {"component": "ordinary.run/execute_plan", "invariant": "run passes select(original,self.q,self.profile) as the sole plan factory. execute_plan checks positive original/extents, calls that factory once, selects fitted iff plan['fits'] else fallback with original, transfers and clears the result, closes every non-fits plan value in finally, and finishes using the same fits boolean. This is a syntactic ownership/control-flow observation, not proof that the primitives discharge cleanup."},
    {"component": "profile/cohort", "invariant": "The default encoded Profile remains (17,10000,64,42,269241600); both opt-in retuned profile functions replace only numerator/denominator by (1,577). interface.ordinary forbids a competing profile option. retuned_native.retune checks the unchanged geometry and fresh active-cohort native; its factory reads that cohort's production.PRIME. The full active_sources AST binds its active encoded/ordinary/production references and compare_backend call; execution/cohort identity remains inherited, not activated here."},
]


def recognize(trees):
    """Check already-parsed source ASTs; deliberately has no byte-pin gate.

    Negative controls call this same function on mutated ASTs, so rejection
    must reach a declaration/control-flow contract rather than a changed hash.
    """
    _need(set(trees) == set(MODULE_AST_SHA256), "modules", "exact reviewed module set")
    declarations = []
    for (path, name), expected in DECLARATIONS.items():
        actual = _declaration(trees[path], name)
        contract = ast.parse(textwrap.dedent(expected)).body[0]
        _need(_syntax_bytes(actual) == _syntax_bytes(contract), path + ":" + name,
              "complete-declaration-ast")
        declarations.append({"path": path, "declaration": name,
                             "ast_sha256": _digest(_syntax_bytes(actual))})
    modules = []
    for path, expected in MODULE_AST_SHA256.items():
        actual = _digest(_syntax_bytes(trees[path]))
        _need(actual == expected, path, "complete-reviewed-module-ast")
        modules.append({"path": path, "ast_sha256": actual})
    return {"declarations": declarations, "modules": modules}


def _authenticate_inputs():
    rows = json.loads((HERE / "SOURCE-PINS.json").read_text(encoding="utf-8"))
    _need(type(rows) is list, "pins", "list manifest")
    indexed = {}
    for row in rows:
        _need(type(row) is dict and type(row.get("path")) is str,
              "pins", "typed manifest row")
        name = row["path"]
        _need(name not in indexed, "pins", "unique paths")
        indexed[name] = row
    data, receipts = {}, []
    for name, (size, digest, blob) in PINS.items():
        relative = PurePosixPath(name)
        _need(not relative.is_absolute() and ".." not in relative.parts,
              name, "contained source path")
        path = ROOT / name
        _need(path.is_file() and not path.is_symlink(), name, "regular source file")
        raw = path.read_bytes()
        _need(len(raw) == size and _digest(raw) == digest, name, "pinned bytes")
        actual_blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        _need(actual_blob == blob, name, "pinned Git blob")
        row = indexed.get(name)
        _need(type(row) is dict and row.get("usage") == "input"
              and row.get("bytes") == size and type(row.get("bytes")) is int
              and row.get("sha256") == digest and row.get("git_blob") == blob,
              name, "declared input pin agreement")
        data[name] = raw
        receipts.append({"path": name, "bytes": size, "sha256": digest, "git_blob": blob})
    return data, receipts


def _authenticate_archive(data):
    # Read every member and its manifest; never extract or activate the backend.
    with tarfile.open(ROOT / ARCHIVE, "r:*") as archive:
        members = archive.getmembers()
        _need(len(members) == 36 and all(m.isfile() for m in members), ARCHIVE,
              "36 regular archive members")
        names = [m.name for m in members]
        _need(len(set(names)) == len(names), ARCHIVE, "unique archive members")
        content = {}
        for member in members:
            name = PurePosixPath(member.name)
            _need(not name.is_absolute() and ".." not in name.parts
                  and "\\" not in member.name and name.as_posix() == member.name
                  and 0 <= member.size <= 2**26, ARCHIVE, "bounded canonical member")
            reader = archive.extractfile(member)
            _need(reader is not None, ARCHIVE, "readable member")
            with reader:
                raw = reader.read()
            _need(len(raw) == member.size, member.name, "complete member read")
            content[member.name] = raw
    manifest_raw = content.get(".research-export.json")
    _need(manifest_raw is not None and _digest(manifest_raw) ==
          "920cec57d358249261a539adb9265ee00fa2fb820641b83d3757158ff401f503",
          ARCHIVE, "pinned export manifest")
    manifest = json.loads(manifest_raw)
    _need(manifest["commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
          and manifest["package"] == "research/physical-ordinary-interchange"
          and len(manifest["files"]) == 35, ARCHIVE, "export identity")
    rows = manifest["files"]
    _need(len({r["path"] for r in rows}) == 35 and
          set(content) == {r["path"] for r in rows} | {".research-export.json"},
          ARCHIVE, "exact export inventory")
    for row in rows:
        raw = content[row["path"]]
        _need(len(raw) == row["size"] and _digest(raw) == row["sha256"],
              row["path"], "export member bytes")
    for name in (ENCODED, ORDINARY):
        _need(content.get(name) == data[name], name, "current/archive bytes equal")
    return {"path": ARCHIVE, "sha256": PINS[ARCHIVE][1], "members_read": 36,
            "manifest_sha256": _digest(manifest_raw),
            "commit": manifest["commit"], "current_members_equal": [ENCODED, ORDINARY],
            "producer_imported": False, "extracted": False}


def _replace_expression(tree, old, new):
    wanted = _syntax_bytes(ast.parse(old, mode="eval").body)
    replacement = ast.parse(new, mode="eval").body

    class Replace(ast.NodeTransformer):
        count = 0

        def generic_visit(self, node):
            if isinstance(node, ast.expr) and _syntax_bytes(node) == wanted:
                self.count += 1
                return copy.deepcopy(replacement)
            return super().generic_visit(node)

    change = Replace()
    result = change.visit(tree)
    _need(change.count == 1, "mutation", "exactly one expected expression site")
    return result


def _negative_controls(trees):
    # (name, source, whole declaration, old expression, changed expression).
    cases = [
        ("first_guard_not_strict", ENCODED, "select", "compare(twice, original) < 0", "compare(twice, original) <= 0"),
        ("depth_from_body", ENCODED, "select", "Count(original)", "Count(body)"),
        ("omit_row_factor", ENCODED, "select", "profile.row_factor * order", "order"),
        ("body_threshold_strict", ENCODED, "select", "compare(body, dimension) >= 0", "compare(body, dimension) > 0"),
        ("strict_row_padding", ENCODED, "select", "compare(rows, stock) < 0", "compare(rows, stock) <= 0"),
        ("wrong_remaining_width", ENCODED, "select", "subtract(original, borrowed)", "subtract(original, width)"),
        ("failed_first_guard_body_not_zero", ENCODED, "select", "(Count.literal(0), Count.literal(0))", "(Count.literal(1), Count.literal(0))"),
        ("root_equality_excluded", ENCODED, "atom_width", "compare(power, target) >= 0", "compare(power, target) > 0"),
        ("bisection_stalls", ENCODED, "atom_width", "middle.increment()", "middle.add(Count.literal(0))"),
        ("run_uses_other_original", ORDINARY, "Ordinary.run", "select(original, self.q, self.profile)", "select(gap, self.q, self.profile)"),
        ("fallback_branch_inverted", ORDINARY, "Ordinary.execute_plan", "plan['fits']", "not plan['fits']"),
        ("retuned_denominator_changed", INTERFACE, "profile", "encoded.Profile(numerator=1, denominator=577)", "encoded.Profile(numerator=1, denominator=576)"),
        ("active_retuned_geometry_changed", RETUNED, "profile", "active().encoded.Profile(numerator=1, denominator=577)", "active().encoded.Profile(numerator=1, denominator=577, child_rank=41)"),
        ("active_factory_wrong_q", RETUNED, "build_native", "cohort.production.PRIME", "2"),
        ("production_q_range_inclusive", PRODUCTION, "build_native", "q > 1 << 80", "q >= 1 << 80"),
    ]
    receipts = []
    for label, path, name, old, new in cases:
        variant = copy.deepcopy(trees)
        declaration = _declaration(variant[path], name)
        if label == "fallback_branch_inverted":
            # plan['fits'] also appears in finish: mutate exactly its IfExp test.
            sites = [n for n in ast.walk(declaration) if isinstance(n, ast.IfExp)]
            _need(len(sites) == 1, label, "one fitted/fallback branch")
            sites[0].test = ast.UnaryOp(op=ast.Not(), operand=sites[0].test)
        else:
            _replace_expression(declaration, old, new)
        expected = path + ":" + name
        try:
            recognize(variant)
        except BindingError as error:
            _need(error.component == expected and error.reason == "complete-declaration-ast",
                  label, "rejection reached intended declaration contract")
            receipts.append({"name": label, "rejected": True, "component": error.component,
                             "reason": error.reason, "byte_pin_gate_used": False})
        else:
            raise BindingError(label, "semantic mutant accepted")
    # Defaults are AnnAssign values, not ast.expr sites unique across select.
    variant = copy.deepcopy(trees)
    profile = _declaration(variant[ENCODED], "Profile")
    sites = [n for n in profile.body if isinstance(n, ast.AnnAssign)
             and isinstance(n.target, ast.Name) and n.target.id == "child_rank"]
    _need(len(sites) == 1, "profile_default_changed", "one default")
    sites[0].value = ast.Constant(value=41)
    try:
        recognize(variant)
    except BindingError as error:
        _need(error.component == ENCODED + ":Profile" and error.reason == "complete-declaration-ast",
              "profile_default_changed", "intended default contract rejection")
        receipts.append({"name": "profile_default_changed", "rejected": True,
                         "component": error.component, "reason": error.reason,
                         "byte_pin_gate_used": False})
    else:
        raise BindingError("profile_default_changed", "semantic mutant accepted")
    return receipts


def run():
    """Return a JSON-ready receipt; raise BindingError on any mismatch."""
    data, inputs = _authenticate_inputs()
    trees = {path: ast.parse(data[path].decode("utf-8"), filename=path)
             for path in MODULE_AST_SHA256}
    syntax = recognize(trees)
    archive = _authenticate_archive(data)
    controls = _negative_controls(trees)
    # PRIME is an exact source expression, never evaluated with eval/exec.
    prime_sites = [n for n in trees[PRODUCTION].body if isinstance(n, ast.Assign)
                   and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                   and n.targets[0].id == "PRIME"]
    _need(len(prime_sites) == 1 and _syntax_bytes(prime_sites[0].value) ==
          _syntax_bytes(ast.parse("213 * (1 << 80) + 1", mode="eval").body),
          PRODUCTION, "exact selected prime expression")
    return {"status": "PASS_ORDINARY_SELECTOR_SOURCE_BINDING",
            "inputs": inputs, "bound_input_count": len(inputs),
            "syntax": syntax, "archive": archive, "negative_controls": controls,
            "profile": {"numerator": 1, "denominator": 577, "dimension": 64,
                        "child_rank": 42, "row_factor": 269241600},
            "production_prime": 213 * (1 << 80) + 1,
            "domain": "every integer original e>=1; fixed prime q>2^80 satisfying retained source premises",
            "scalar_contract": {"width": "min{w>=1 : w^577>=e}",
                                "depth": "D(e)=0 if e<64 else 1+D(42*floor(e/64))",
                                "stock": "(269241600*product(q^64-q^i,i=0..63)*q^(4096*(w-1)))^D(e)",
                                "borrowed": "min{k>=0 : q^k>=stock}",
                                "first_guard": "2*k<e",
                                "body_remainder": "divmod(e-k,w) if first_guard else (0,0)",
                                "fits": "first_guard and body>=64"},
            "loop_invariants": INVARIANTS,
            "scope": "Complete pinned source syntax/control-flow binding to a conditional scalar projection; no source imports, activation or payload execution.",
            "inherited_or_unproved": ["Count/Counter primitive arithmetic, comparison and lifetime semantics",
                                      "successful well-bracketed execution and physical cleanup/resource bounds",
                                      "active loader/cohort execution and selected prime/source admissibility",
                                      "tau, beta, supplier and multiplication transfer obligations"],
            "physical_admission": False}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
