# SPDX-License-Identifier: Apache-2.0
"""One authenticated physical tape cohort for the integrated complex caller.

I adapt only the activation/recipe entry points. The inherited coefficient,
scalar-instruction and normalization bodies remain byte-identical. Their
original notices and frozen archives retain predecessor attribution.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import tarfile
import types

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "research/gaussian-normalization-stream/SOURCES.json": "c434302f4489366c1763f918ba59e2f57efc0a41d72310fd3c6bbe1553370275",
    "research/gaussian-normalization-stream/normalizer.py": "2b0acaa831219faf3e7776969bdcffc3f0f9c608b15d6b4c343ff20cf6a50107",
    "research/physical-scalar-stream/scalar_words.py": "f4293c5ea5a7b65be920997f2ff33ce046ae3d9707ecbcecb3bd163d821dfd00",
    "research/physical-scalar-stream/scalar_engine.py": "be74c74862ff2b152d3752cb887c6682ddf2d889bc9f16f6328e418618e4c8b6",
}
_loaded = None
_identities = None


def require(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    raw = {}
    for path, digest in PINS.items():
        value = (ROOT / path).read_bytes()
        require(sha256(value).hexdigest() == digest, "cohort source pin: " + path)
        raw[path] = value
    manifest = json.loads(raw["research/gaussian-normalization-stream/SOURCES.json"])
    for record in manifest["files"]:
        if record["usage"] == "input":
            path = record["path"]
            value = (ROOT / path).read_bytes()
            require(sha256(value).hexdigest() == record["sha256"], "inherited cohort input: " + path)
            if path in raw:
                require(raw[path] == value, "one source image per cohort input")
            raw[path] = value
    return raw


def module(name, path, raw):
    require(name not in sys.modules, "cold explicit cohort module: " + name)
    result = types.ModuleType(name)
    result.__file__ = str(path)
    sys.modules[name] = result
    exec(compile(raw, str(path), "exec"), result.__dict__)
    return result


def ready():
    """Explicit adapter for a predecessor's activation call, never cold-load twice."""
    require(_loaded is not None, "cohort initialized before dependent module")
    for name, value in _identities.items():
        require(sys.modules.get(name) is value, "physical cohort identity: " + name)
    return _loaded


def activate():
    global _loaded, _identities
    if _loaded is not None:
        return ready()
    cold = ("leaf_sources", "phase_sources", "native_sources", "source", "words",
            "records", "cardinal_counts", "scratch_pool", "session", "scalar_sources",
            "scalar_recipe", "scalar_words", "scalar_engine", "norm_sources", "normalizer")
    require(not any(name in sys.modules for name in cold), "cold unified physical namespace")
    raw = authenticate()
    prefix = "research/physical-gaussian-leaf/"
    leaf = module("leaf_sources", ROOT / (prefix + "leaf_sources.py"), raw[prefix + "leaf_sources.py"])
    leaf.activate()
    _identities = {name: sys.modules[name] for name in
                   ("leaf_sources", "phase_sources", "native_sources", "source")}
    _loaded = {"inputs": tuple(sorted(raw))}
    # The inherited modules call activate() at import. They now explicitly
    # join this authenticated cohort rather than invoking competing cold loaders.
    for name in ("scalar_sources", "norm_sources"):
        adapter = types.ModuleType(name)
        adapter.__file__ = __file__
        adapter.activate = ready
        adapter.controller_cohort_adapter = True
        sys.modules[name] = adapter
        _identities[name] = adapter
    for name in ("signed_linear", "axis_stream", "coefficient_engine"):
        _loaded[name] = module(name, ROOT / (prefix + name + ".py"), raw[prefix + name + ".py"])
    from scalar_program import ScalarProgram
    recipe_adapter = types.ModuleType("scalar_recipe")
    recipe_adapter.__file__ = __file__
    recipe_adapter.Recipe = ScalarProgram
    recipe_adapter.controller_cohort_adapter = True
    sys.modules["scalar_recipe"] = recipe_adapter
    _identities["scalar_recipe"] = recipe_adapter
    for name, directory in (("scalar_words", "physical-scalar-stream"),
                            ("scalar_engine", "physical-scalar-stream"),
                            ("normalizer", "gaussian-normalization-stream")):
        path = "research/" + directory + "/" + name + ".py"
        _loaded[name] = module(name, ROOT / path, raw[path])
    for name in ("words", "records", "cardinal_counts", "scratch_pool", "session",
                 "signed_linear", "axis_stream", "coefficient_engine", "scalar_words",
                 "scalar_engine", "normalizer"):
        _identities[name] = sys.modules[name]
    _loaded["identities"] = tuple(sorted(_identities))
    return ready()


def monomial_api():
    """Join the exact PR3087 recipe/physical bodies retained by the leaf archive."""
    api = activate()
    if "monomial_engine" in api:
        return ready()["monomial_engine"]
    path = ROOT / "research/physical-gaussian-leaf/inputs/pr3087.tar"
    require(sha256(path.read_bytes()).hexdigest() ==
            "d7e9c04a5e6d3f76158555d84080786c7cd8028ca31a61c9399de2b2c67bfd53",
            "frozen monomial cohort source")
    directory = Path(sys.modules["phase_sources"].__file__).parent
    with tarfile.open(path, "r:") as archive:
        for name in ("phase_recipe", "pair_dispatch", "signed_phase", "monomial_engine"):
            matches = [m for m in archive.getmembers() if m.name == name + ".py"]
            require(len(matches) == 1 and matches[0].isfile(), "frozen monomial member")
            raw = archive.extractfile(matches[0]).read()
            value = module(name, directory / (name + ".py"), raw)
            _identities[name] = value
            api[name] = value
    return ready()["monomial_engine"]
