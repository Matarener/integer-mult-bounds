"""Capture and authenticate the exact retained sources before executing them.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Original mathematical and implementation credit is retained in SOURCES.json.
"""

import gzip
import hashlib
import json
from pathlib import Path
from types import ModuleType


SIZE = 512
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PINNED = {
    "research/p104-rounded-collector/inputs/WORD.json":
        "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    "research/p104-rounded-collector/inputs/NATIVE.json.gz":
        "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    "inputs/pr3467/source.py":
        "c54dabffe141de6befb6069e145c5ccbde629e76afb0f0afa3eb07bd72ab4b25",
    "inputs/pr3467/classifier.py":
        "3e42ba4e5fa1cc819f3e7b773b38ca47476bf85f581f888cc99690e1cf2f2b40",
    "inputs/pr3467/admission.py":
        "00bd8c666fa758e76e47fb3e8835dd71770d1ce32c55d71d8d003dca2da15709",
    "inputs/pr3467/inputs/pr3382_model.py":
        "74c83367887dd885137b222155c86389fe0be9f1293a6f0e5fdb51d71f435fdd",
}


class SourceError(ValueError):
    """A source, receipt or finite reference contract failed."""


def require(condition, message):
    if not condition:
        raise SourceError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise SourceError("noninteger JSON numeric token: " + value)

    return json.loads(data, object_pairs_hook=pairs,
                      parse_float=invalid, parse_constant=invalid)


def typed_equal(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            typed_equal(actual[key], expected[key]) for key in actual)
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            typed_equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def read_regular(path):
    path = Path(path)
    require(not any(part.is_symlink() for part in (path, *path.parents)),
            "source path contains a symbolic link: " + str(path))
    require(path.is_file() and not path.is_symlink(),
            "regular source missing: " + str(path))
    with path.open("rb") as stream:
        data = stream.read(32 * 1024 * 1024 + 1)
    require(len(data) <= 32 * 1024 * 1024, "source exceeds bounded size")
    return data


def module_from_bytes(data, path, name):
    result = ModuleType(name)
    result.__file__ = str(path)
    exec(compile(data, str(path), "exec"), result.__dict__)
    return result


def check_pinned_bytes(data, expected, name):
    require(hashlib.sha256(data).hexdigest() == expected,
            "source digest mismatch: " + name)


def capture_inputs(root=ROOT, package=PACKAGE):
    root, package = Path(root), Path(package)
    captured = {}
    paths = {}
    for name, expected in PINNED.items():
        path = (root if name.startswith("research/") else package) / name
        data = read_regular(path)
        check_pinned_bytes(data, expected, name)
        captured[name], paths[name] = data, path
    modules = {}
    for name, short in (("source.py", "source"),
                        ("classifier.py", "classifier"),
                        ("admission.py", "admission"),
                        ("inputs/pr3382_model.py", "model")):
        key = "inputs/pr3467/" + name
        modules[short] = module_from_bytes(captured[key], paths[key],
                                          "p104_retained_" + short)
    word = json.loads(captured["research/p104-rounded-collector/inputs/WORD.json"])
    native = json.loads(gzip.decompress(
        captured["research/p104-rounded-collector/inputs/NATIVE.json.gz"]))
    return {"word": word, "native": native, **modules,
            "captured": captured, "paths": paths}


def recheck_inputs(context):
    for name, data in context["captured"].items():
        require(read_regular(context["paths"][name]) == data,
                "source changed during replay: " + name)
