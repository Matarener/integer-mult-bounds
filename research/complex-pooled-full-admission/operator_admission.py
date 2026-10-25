#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind PR4181's literal fill to the retained all-character phase operator.

This is a source-bound reuse of Cinna Davis's PR4088 owner/operator walkers
and David Ganz's PR4085 exact Z4 normalizer, not an independent algorithm.
The frozen PR4181 context supplies only its new selector. All phase, window,
nonaliasing, axis and complete-invoice predicates are executed unchanged.
Prepared by Ross Richardson with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import py_compile
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
PRED = HERE.parent / "staged544-mixed-fourth-entry"
CANDIDATE = HERE / "frozen/pr4181"
PINS = {
    "verify.py": "8dcb31e06abe2c92fca29a53d42a67f1b3358512b75b659e5fe2e0ba41e70cc8",
    "owner_verify.py": "7cc34c6cd6092550ca356093823252764f97bde8c3daecfe7d84afffe383ce72",
    "operator_verify.py": "9f1af2585df3f24ac0862d967cebc71c07c98bbc51506b0b95f82a2ab9ce6564",
    "vendor/audit_core.py": "888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951",
    "vendor/audit_verify.py": "99971d3cc143cc894600e08c8cfbad3e8f537a544212f21dfbe4271cfa97354d",
    "vendor/staged_pair.py": "25fc9b025dbb90358032013303adea650a5f19937fd3edf30b6c6fd023e2d747",
    "vendor/staged_entries_applier.py": "41f889bcdf6ef4e8033ac45bf4d2c0fdb20d7b51dd194806d79bba789e207661",
    "checks/inherited_frames.py": "25ba8774b1be4f0be27abeac94232eb8db657f02d7830bd93208c53649e65a04",
    "vendor/full_operator.py": "06f9f5128e19b6ea07756a9a11fcc9a9757a440a8048b5210422d12f183dfac3",
    "vendor/t360_admission.py": "d3c3786a54fd4b2e5df98a1b39319628e855f65ffacabe7ab4d0deba8fe13329",
    "vendor/exact_root.py": "565e0d7de2fcd7587045f11731dfaba202e18f93e3a7a8178374f4933e502fbe",
    "owner/ORDER.json": "743e74b538432e2b2045e754b0de9c18f36fc5039fdb8eb542177a898ec78e44",
    "owner/DISPATCH.json": "5d6fa711d704a1b498e5fe066ea821c4fa0217463702e82a7ce5be9da4023e8a",
    "owner/TEMPLATE.json.gz": "21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e",
    "owner/PLAN.json.gz": "d566cfb87b71639d4138e1f89b543e2dd6a7772070226a2a14c799a6835bf21e",
    "owner/old-NATIVE-base.json.gz": "bfe0cc0badac6c6d18461ceea0b299162c0f280c05f81b63f11fcc06cf9180e6",
    "owner/old-NATIVE-extra.json.gz": "c5eec94a64cecfd6b83de05619628ad4868e889d62a55b49973f09705cc60448",
    "inputs/THREE-base.json.gz": "df31495cff95a1e512da398f52841c6b5ade29067869b3d68b89d756a5641112",
    "inputs/THREE-extra.json.gz": "9a28f7ef91938c0866e408eb06e03eb5f8e727a00b44eb936ddd5ed48704bd4c",
    "inputs/FOUR-base.json.gz": "aecaddba48fdff6353a6511c3623346b05aa607e30103fb016604a2b1025ce95",
    "inputs/FOUR-extra.json.gz": "615093190aa5479034bb8acdd8925d7a910e082b84dec7df84b459b62421235a",
    "inputs/DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "inputs/OPERATOR-TEMPLATE.json.gz": "21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e",
    "INPUTS.json": "43ab5cd305ec23dbc63accaffb0dca8bdf201130bff89f5e807d919c5118fc98",
    "RESULT.json": "6346ee768637aa9a1891d1d61d800d640235420b320fb7e659d1bf664ec42b3d",
}
CANDIDATE_PINS = {
    "verify.py": "e89870761ddefe0a7f983512c6ae884ccff26235085238624e00f75a31cd6e76",
    "RESULT.json": "d823509ea38e545db6c287a85c00bc4257825fb2710728dfc776c8801d2becd9",
    "owner/MIXED-DISPATCH.json": "ab8c774b614730701435c0f5dc1bfba4a46d980690a1b6bc09225555ff9be6f4",
    "owner/FILL.json.gz": "5455c120a121a7ec70897fb2c58e1988ce01d7172d6a5622519bea6b25efe8fe",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def authenticate():
    pins = {}
    for root, expected in ((PRED, PINS), (CANDIDATE, CANDIDATE_PINS)):
        for name, digest in expected.items():
            path = root / name
            need(not path.is_symlink(), "ordinary source file: " + name)
            need(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                 "operator source pin: " + str(path))
            pins[path.relative_to(HERE.parent).as_posix()] = digest
    return pins


def exact_source_module(name, path, expected_digest):
    """Execute the same source bytes whose fixed digest was just checked.

    SourceFileLoader.exec_module may use an existing .pyc even when bytecode
    writes are disabled. Compilation here never consults that cache.
    """
    source = path.read_bytes()
    need(hashlib.sha256(source).hexdigest() == expected_digest,
         "executed source digest: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None, "explicit source module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def source_cache_control():
    """An unchecked-hash cache must never substitute for authenticated bytes."""
    name = "_pooled_operator_source_cache_control"
    clean = b"witness = 'authenticated_source'\n"
    stale = b"witness = 'stale_unchecked_hash_cache'\n"
    before = sys.modules.get(name)
    try:
        with tempfile.TemporaryDirectory(prefix="pooled-operator-source-cache-") as temp:
            path = Path(temp) / "fixture.py"
            path.write_bytes(stale)
            py_compile.compile(str(path), doraise=True,
                               invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
            path.write_bytes(clean)
            spec = importlib.util.spec_from_file_location(name, path)
            need(spec is not None and spec.loader is not None, "cache witness spec")
            stock = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(stock)
            need(stock.witness == "stale_unchecked_hash_cache",
                 "negative fixture must actually expose cached-source substitution")
            exact = exact_source_module(name, path, hashlib.sha256(clean).hexdigest())
            need(exact.witness == "authenticated_source", "authenticated source bypasses stale cache")
            rejected("executed_source_digest_mismatch",
                     lambda: exact_source_module(name, path, hashlib.sha256(stale).hexdigest()),
                     "executed source digest")
    finally:
        if before is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = before
    return {"unchecked_hash_pyc_fixture_exposes_stock_loader": True,
            "exact_loader_executes_authenticated_source": True,
            "wrong_source_digest_rejected": True}


@contextmanager
def retained_modules():
    """Import exact files without borrowing a caller's generic verify/vendor.

    A few upstream modules use absolute local imports. Temporarily provide their
    exact aliases before executing every dependent module, then restore the
    original module table and search path. Every nonstdlib transitive import
    resolves to one of these preloaded exact-source modules. No source text is
    changed and no bytecode is read from or written beside frozen sources.
    """
    aliases = {"audit_core", "audit_verify", "staged_pair",
               "staged_entries_applier", "inherited_frames", "verify",
               "owner_verify", "operator_verify", "full_operator",
               "pooled_owner_source"}
    def owned(name):
        return name in aliases or name == "vendor" or name.startswith("vendor.")
    saved = {n: m for n, m in sys.modules.items() if owned(n)}
    saved_path, saved_argv = list(sys.path), list(sys.argv)
    saved_bytecode = sys.dont_write_bytecode
    for name in saved:
        del sys.modules[name]
    sys.dont_write_bytecode = True
    sys.argv = [str(CANDIDATE / "verify.py")]

    def load(name, path):
        if path.is_relative_to(PRED):
            digest = PINS[path.relative_to(PRED).as_posix()]
        else:
            digest = CANDIDATE_PINS[path.relative_to(CANDIDATE).as_posix()]
        return exact_source_module(name, path, digest)

    try:
        for name, relative in (
            ("audit_core", "vendor/audit_core.py"),
            ("audit_verify", "vendor/audit_verify.py"),
            ("staged_pair", "vendor/staged_pair.py"),
            ("staged_entries_applier", "vendor/staged_entries_applier.py"),
            ("inherited_frames", "checks/inherited_frames.py"),
            ("verify", "verify.py"), ("owner_verify", "owner_verify.py"),
        ):
            load(name, PRED / relative)
        vendor = types.ModuleType("vendor")
        vendor.__path__ = [str(PRED / "vendor")]
        sys.modules["vendor"] = vendor
        full = load("vendor.full_operator", PRED / "vendor/full_operator.py")
        vendor.full_operator = full
        sys.modules["full_operator"] = full
        vendor.t360_admission = load("vendor.t360_admission", PRED / "vendor/t360_admission.py")
        vendor.exact_root = load("vendor.exact_root", PRED / "vendor/exact_root.py")
        operator = load("operator_verify", PRED / "operator_verify.py")
        pooled = load("pooled_owner_source", CANDIDATE / "verify.py")
        # Only its predecessor-directory location changes. Its selector and
        # context algorithm, including all imported owner predicates, are exact.
        pooled.PRED = PRED
        yield sys.modules["owner_verify"], operator, pooled
    finally:
        for name in list(sys.modules):
            if owned(name):
                del sys.modules[name]
        sys.modules.update(saved)
        sys.path[:] = saved_path
        sys.argv[:] = saved_argv
        sys.dont_write_bytecode = saved_bytecode


def bound_scan(operator, expected):
    """Execute the unchanged scan code with only its expected RESULT rebound."""
    original = operator.read
    expected_path = PRED / "RESULT.json"
    def read_bound(path):
        return deepcopy(expected) if path == expected_path else original(path)
    namespace = dict(operator.scan.__globals__, read=read_bound)
    return types.FunctionType(operator.scan.__code__, namespace, operator.scan.__name__,
                              operator.scan.__defaults__, operator.scan.__closure__)


def rejected(name, fn, expected_reason=None):
    try:
        fn()
    except ValueError as error:
        reason = str(error)
        need(expected_reason is None or expected_reason in reason,
             "wrong mutation rejection for " + name + ": " + reason)
        return {"name": name, "reason": reason}
    raise ValueError("accepted operator mutation: " + name)


def audit(controls=True):
    pins = authenticate()
    cache_control = source_cache_control()
    expected = read(CANDIDATE / "RESULT.json")
    with retained_modules() as (owner, operator, pooled):
        ctx, dispatch = pooled.context()
        need(dispatch == read(CANDIDATE / "owner/MIXED-DISPATCH.json"),
             "exact t<1080 dispatch")
        counts = dict(sorted(Counter(ctx[1].values()).items()))
        need(counts == {"extra": 592, "extra-four": 1080, "gauge44": 1568},
             "exact active provider counts")
        fill = read(CANDIDATE / "owner/FILL.json.gz")
        need(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"],
             "literal fill schema")
        need(fill["dispatch_overrides"] == [], "no hidden dispatch overrides")
        rows = fill["rows"]
        profile, idle = owner.walk(rows, ctx)
        need(profile == {int(k): v for k, v in expected["profile"].items()}, "pooled owner profile")
        need(idle == {int(k): v for k, v in expected["idle"].items()}, "pooled owner complement")
        template = read(PRED / "owner/TEMPLATE.json.gz")
        plan = read(PRED / "owner/PLAN.json.gz")
        phases = read(PRED / "inputs/DATA-PHASES.json")
        need(template["exact_data_phase_recipe_sha256"] == PINS["inputs/DATA-PHASES.json"],
             "exact phase recipe binding")
        ports = read(PRED / "inputs/THREE-base.json.gz")["ports"]
        for tag in ("base", "extra"):
            for kind in ("THREE", "FOUR"):
                need(read(PRED / f"inputs/{kind}-{tag}.json.gz")["ports"] == ports,
                     "common ordered all112 port interface")
        identities = operator.phase_checks(template, phases, ports)
        need(identities == 10416, "complete exact phase identity count")
        windows, pairs = operator.exact_windows(template, plan, ctx[0], phases)
        scan = bound_scan(operator, expected)
        need(scan(rows, ctx, windows, pairs, phases) == idle,
             "exact original-axis complement equals owner complement")
        results = []
        if controls:
            bad = deepcopy(phases)
            child = next(c for c in bad["recipes"][0]["idle_children"] if c["rank"] > 0)
            child["translation_after"] = int(child["translation_after"]) ^ 1
            results.append(rejected("wrong_global_phase",
                lambda: operator.phase_checks(template, bad, ports), "idle exact phase"))
            bad_template = deepcopy(template)
            bridge = next(e for e in bad_template["execution_schedule"] if e["kind"] == "bridge")
            bridge["coefficient"] = -bridge["coefficient"]
            results.append(rejected("wrong_signed_controller",
                lambda: operator.phase_checks(bad_template, phases, ports), "scalar controller identity"))
            original = rows[0][:]
            tick = rows[0][0]
            owner_id, child_id = next(k for k, (lo, hi, stream) in windows.items() if lo >= (tick, -1))
            rows[0][2:4] = owner_id, child_id
            try:
                results.append(rejected("cross_scalar_observation",
                    lambda: scan(rows, ctx, windows, pairs, phases), "strict exact observation window"))
            finally:
                rows[0][:] = original
            wrong_ctx, _ = pooled.context(lambda t: t * 109 % 324 < 109)
            results.append(rejected("pr4088_dispatch_on_pr4181_fill",
                lambda: scan(rows, wrong_ctx, windows, pairs, phases)))
            stale = deepcopy(expected)
            stale["idle"] = read(PRED / "RESULT.json")["idle"]
            results.append(rejected("stale_pr4088_idle_complement",
                lambda: bound_scan(operator, stale)(rows, ctx, windows, pairs, phases), "exact phase residual"))
        axis_mass = 360 * sum(len(c["orthogonal_axes"]) for r in phases["recipes"] for c in r["idle_children"])
        residual_mass = sum(rank * n for rank, n in idle.items())
        result = {
            "status": "PASS_POOLED_ALL_CHARACTER_OPERATOR_ADMISSION",
            "source_head_pr4088": "72d7efc181edb21806a878f174847c96dd410ab0",
            "source_head_pr4181": "4ed92bed95dd483f5662e98ef246b258c3cfe64f",
            "calls": len(ctx[0]), "active_provider_counts": counts,
            "authenticated_word_catalogue": ["extra", "extra-four", "gauge44", "gauge44-four"],
            "unused_catalogue_provider": "gauge44-four",
            "hosted_rows": len(rows), "physical_bins": len(ctx[2]) * 112,
            "exact_observation_windows": len(windows),
            "ports": len(ports), "exact_Z4_identities": identities,
            "all_characters": True, "all_positive_tensor_multiplicities": True,
            "global_phase_retained": True, "original_axis_mass": axis_mass,
            "hosted_width_mass": axis_mass - residual_mass,
            "residual_rank_mass": residual_mass, "idle": idle, "profile": profile,
            "paid_rank_mass": sum(rank * n for rank, n in profile.items()),
            "controls": results, "source_pins": pins,
            "source_execution_control": cache_control,
            "scope": "Exact phase/chronology binding of the PR4181 fill under the retained local native endpoint and common-cover embedding interfaces. Source-bound interpreter reuse; not an independent algorithm, native rerun, ordinary/outer release, or an all-size multiplication theorem.",
        }
    need(authenticate() == pins, "read-only source inputs after audit")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--controls", action="store_true", help="Retained for explicit replay commands; controls run by default.")
    args = parser.parse_args()
    result = audit()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
