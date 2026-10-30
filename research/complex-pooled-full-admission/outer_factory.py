"""Construct the pooled Gaussian/CRT consumers in one existing physical cohort.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
This module does not open a cold cohort or execute a production payload.
The caller supplies complete authenticated runtime source packages; the small
published proof-reference archive alone is intentionally insufficient.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile
from types import ModuleType, SimpleNamespace

HERE = Path(__file__).resolve().parent
GAUSSIAN = "research/physical-gaussian-tensor"
CRT = "research/crt-address-streams"
BASE = "12fa8c5c844be21bfefb38a19503fbd867a11244"
GAUSSIAN_HEAD = "f687fa171ef760fa98a4be1289717b47dd4ee0b3"
ASSEMBLY = "upstream/build/sections/08-assembly.tex"
GLOBAL_ALIAS = "pooled_outer_authenticated_global_bridge"
LOCAL_ALIAS = "pooled_physical_local_bridge"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(body):
    return sha256(body).hexdigest()


def checked(path, expected):
    need(path.is_file() and not path.is_symlink(), "regular constructor source: "+str(path))
    body = path.read_bytes()
    need(digest(body) == expected, "constructor source SHA256: "+str(path))
    return body


def contract_sources():
    """Read the bounded proof/constructor reference archive, without execution."""
    pins = json.loads((HERE/"OUTER-PINS.json").read_bytes())
    need(pins["schema"] == 1, "outer contract pin schema")
    manifest = json.loads(checked(HERE/pins["manifest"], pins["manifest_sha256"]))
    raw = checked(HERE/pins["archive"], pins["archive_sha256"])
    need(len(raw) == pins["bytes"] < 2**20, "bounded constructor reference archive")
    expected = {row["path"]: row for row in manifest["files"]}
    need(len(expected) == len(manifest["files"]) == pins["files"], "unique outer contract inventory")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and ".." not in path.parts
                 and path.as_posix() == member.name and "\\" not in member.name
                 and member.name in expected and member.name not in result
                 and member.size < 2**20, "declared regular constructor reference")
            body = archive.extractfile(member).read()
            row = expected[member.name]
            blob = sha1(b"blob "+str(len(body)).encode()+b"\0"+body).hexdigest()
            need(len(body) == row["bytes"] and digest(body) == row["sha256"]
                 and blob == row["git_blob"], "exact source contract member")
            result[member.name] = body
    need(set(result) == set(expected), "complete outer source contract set")
    return result, manifest


def runtime_pins():
    pins = json.loads((HERE/"OUTER-FACTORY-PINS.json").read_bytes())
    need(pins["schema"] == 1 and set(pins["packages"]) == {GAUSSIAN, CRT},
         "two exact outer runtime package identities")
    need(pins["packages"][GAUSSIAN]["commit"] == GAUSSIAN_HEAD
         and pins["packages"][CRT]["commit"] == BASE, "fixed runtime source heads")
    return pins["packages"]


@contextmanager
def global_bridge():
    """Compile the authenticated bridge bytes, without a bytecode-cache loader."""
    pins = json.loads((HERE/"OUTER-FACTORY-PINS.json").read_bytes())
    expected = pins["local_bridges"]["physical_global_bridge.py"]
    body = checked(HERE/"physical_global_bridge.py", expected)
    need(GLOBAL_ALIAS not in sys.modules, "fresh private global-bridge alias")
    need(LOCAL_ALIAS not in sys.modules, "fresh private local-bridge alias")
    module = ModuleType(GLOBAL_ALIAS)
    module.__file__ = str(HERE/"physical_global_bridge.py")
    sys.modules[GLOBAL_ALIAS] = module
    try:
        exec(compile(body, module.__file__, "exec", optimize=0), module.__dict__)
        yield module
    finally:
        local = getattr(module, "_local_bridge", None)
        if local is not None and sys.modules.get(LOCAL_ALIAS) is local:
            del sys.modules[LOCAL_ALIAS]
        if sys.modules.get(GLOBAL_ALIAS) is module:
            del sys.modules[GLOBAL_ALIAS]


def copy_runtime(source_root, destination, package, specification):
    """Copy only declared, authenticated files; unpinned siblings never enter sys.path."""
    target = destination/package
    target.mkdir(parents=True)
    for name, row in specification["files"].items():
        path = PurePosixPath(name)
        need(not path.is_absolute() and ".." not in path.parts and path.as_posix() == name,
             "relative runtime package file")
        body = checked(source_root/package/name, row["sha256"])
        need(len(body) == row["bytes"] and
             sha1(b"blob "+str(len(body)).encode()+b"\0"+body).hexdigest() == row["git_blob"],
             "complete runtime file identity")
        output = target/name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(body)
    return target


def authenticate_module(module, body):
    path = Path(module.__file__)
    need(path.is_file() and not path.is_symlink() and path.read_bytes() == body,
         "loaded module matches retained bytes: "+module.__name__)


@contextmanager
def crt_token(module, state):
    """Scoped loader token; authentication is performed before entering here."""
    need(module._active is None, "unbound CRT loader in existing tensor cohort")
    module._active = state
    try:
        need(module.activate() is state, "CRT and tensor share one active source state")
        yield
    finally:
        module._active = None


def consumers_idle(consumers):
    consumers.tensor.idle()
    consumers.converter.idle()
    from words import BLANK
    for owner in (consumers.tensor, consumers.converter):
        need(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
             "consume complete outer factory returns before leaving the cohort")


@contextmanager
def production_consumers(*, tensor_source_root, crt_source_root):
    """Yield actual Tensor/Converter owners inside tensor_sources.opened().

    tensor_source_root contains the complete f687 PR3935 package, including
    its immutable archives. crt_source_root contains the base CRT package.
    They may be distinct source trees. The caller must already have opened
    the authenticated tensor cohort. Four fresh ordinary instances are
    allocated before numerical input. Their finite compilation is charged.
    """
    contracts, _ = contract_sources()
    pins = runtime_pins()
    tensor_sources = sys.modules.get("tensor_sources")
    need(tensor_sources is not None, "open the authenticated tensor cohort first")
    authenticate_module(tensor_sources, contracts[GAUSSIAN+"/tensor_sources.py"])
    state = tensor_sources.active()
    crt_names = {name[:-3] for name in pins[CRT]["files"] if name.endswith(".py") and "/" not in name}
    need(not (crt_names & set(sys.modules)), "fresh CRT extension in the existing tensor cohort")
    old_path = sys.path[:]
    old_cache = sys.pycache_prefix
    old_write = sys.dont_write_bytecode
    before_modules = set(sys.modules)
    crt_module = None
    tensor_source_root = Path(tensor_source_root).resolve()
    crt_source_root = Path(crt_source_root).resolve()
    with tempfile.TemporaryDirectory(prefix="pooled-outer-factory-") as directory:
        staged = Path(directory)
        tensor_package = copy_runtime(tensor_source_root, staged, GAUSSIAN, pins[GAUSSIAN])
        crt_package = copy_runtime(crt_source_root, staged, CRT, pins[CRT])
        assembly = staged/ASSEMBLY
        assembly.parent.mkdir(parents=True)
        assembly.write_bytes(contracts[ASSEMBLY])
        try:
            sys.pycache_prefix = str(staged/"empty-bytecode")
            sys.dont_write_bytecode = True
            sys.path[:0] = [str(HERE), str(crt_package), str(tensor_package)]
            # Reject incompatible preloaded package modules before importing.
            for package, row in pins.items():
                for name, expected in row["files"].items():
                    if name.endswith(".py") and "/" not in name and name[:-3] in sys.modules:
                        module = sys.modules[name[:-3]]
                        checked(Path(module.__file__), expected["sha256"])
            spec = importlib.util.spec_from_file_location("crt_sources", crt_package/"crt_sources.py")
            crt_module = importlib.util.module_from_spec(spec)
            sys.modules["crt_sources"] = crt_module
            spec.loader.exec_module(crt_module)
            crt_module.authenticate()
            crt_module.check_tree(tensor_source_root, crt_module.source_manifest())
            with crt_token(crt_module, state):
                names = ("active_sources", "active_root", "retuned_native", "retuned_machine",
                         "composed_engine", "fourier_engine", "convolution_engine", "cyclic_engine",
                         "chirp_engine", "tensor_engine", "tensor_router", "crt_converter")
                modules = {name: importlib.import_module(name) for name in names}
                from cardinal_counts import Count
                from records import Tape
                for name, module in modules.items():
                    matches = [body for path, body in contracts.items() if path.endswith("/"+name+".py")]
                    need(len(matches) == 1, "one retained constructor body: "+name)
                    authenticate_module(module, matches[0])
                    need(not hasattr(module, "Count") or module.Count is Count,
                         "one physical Count vocabulary: "+name)
                    need(not hasattr(module, "Tape") or module.Tape is Tape,
                         "one physical Tape vocabulary: "+name)
                from router_engine import Router
                with global_bridge() as physical_global_bridge:
                    root = physical_global_bridge.production_layer()
                native = modules["retuned_native"].build_native
                support_native, gaussian_native, crt_native = native(), native(), native()
                complex_native = root.machine.monomial.compact.binary.native
                need(len({id(value) for value in (complex_native, support_native, gaussian_native, crt_native)}) == 4,
                     "four distinct complete ordinary owners")
                support = modules["composed_engine"].ComposedRoot(Router(support_native), root)
                fourier = modules["fourier_engine"].Fourier(support)
                convolution = modules["convolution_engine"].Convolution(fourier)
                cyclic = modules["cyclic_engine"].Cyclic(convolution)
                chirp = modules["chirp_engine"].Chirp(cyclic)
                tensor_router = modules["tensor_router"].FullRouter(gaussian_native)
                tensor = modules["tensor_engine"].Tensor(chirp, tensor_router)
                crt_router = modules["tensor_router"].FullRouter(crt_native)
                converter = modules["crt_converter"].Converter(crt_router)
                consumers = SimpleNamespace(tensor=tensor, converter=converter, root=root,
                                            support=support, source_state=state)
                consumers_idle(consumers)
                yield consumers
                consumers_idle(consumers)
        finally:
            if crt_module is not None:
                crt_module._active = None
            sys.path[:] = old_path
            sys.pycache_prefix = old_cache
            sys.dont_write_bytecode = old_write
            # Modules newly loaded from private staging must not survive it.
            for name in set(sys.modules)-before_modules:
                path = getattr(sys.modules[name], "__file__", None)
                if name == "crt_sources" or (path and Path(path).is_relative_to(staged)):
                    del sys.modules[name]
