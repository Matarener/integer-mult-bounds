"""Paid cold build/load for root-owned, source-pinned serial feasibility only.

This source was not executed by its author. A caller supplies the frozen C
source digest explicitly. No implicit acceptance of freshly edited C source.
"""
import atexit
from hashlib import sha256
import importlib.util
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time

HERE = Path(__file__).resolve().parent
_loaded = None
_temporary = None
_receipt = None


def load(expected_source_sha256):
    global _loaded, _temporary, _receipt
    path = HERE / 'integer_format.c'
    if path.is_symlink() or not path.is_file():
        raise ValueError('owned C source is a regular non-symlink file')
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != expected_source_sha256:
        raise ValueError('exact frozen owned C source')
    if _loaded is not None:
        if _receipt['source_sha256'] != digest:
            raise ValueError('already loaded code has this exact source')
        return _loaded
    if platform.python_implementation() != 'CPython' or sys.version_info[:2] != (3, 12) or sys.platform != 'linux':
        raise RuntimeError('feasibility requires Linux CPython 3.12')
    compiler = shutil.which('cc')
    if compiler is None:
        raise RuntimeError('feasibility requires an existing C compiler')
    started = time.perf_counter()
    _temporary = tempfile.TemporaryDirectory(prefix='integer-format-owned-')
    atexit.register(_temporary.cleanup)
    directory = Path(_temporary.name)
    snapshot = directory / 'integer_format.c'
    snapshot.write_bytes(raw)
    snapshot.chmod(0o444)
    binary = directory / ('_integer_format' + sysconfig.get_config_var('EXT_SUFFIX'))
    flags = ['-O2', '-shared', '-fPIC', '-std=c11', '-Wall', '-Werror',
             '-I' + sysconfig.get_path('include')]
    command = [compiler, *flags, str(snapshot), '-o', str(binary)]
    build = subprocess.run(command, capture_output=True, text=True, check=False)
    if build.returncode or build.stdout or build.stderr:
        raise RuntimeError('native build rejected: ' + repr(dict(
            command=command, returncode=build.returncode,
            stdout=build.stdout, stderr=build.stderr)))
    if path.is_symlink() or sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('owned C source unchanged through cold build')
    binary.chmod(0o444)
    spec = importlib.util.spec_from_file_location('_integer_format', binary)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _receipt = dict(source_sha256=digest, compiler=compiler, flags=flags,
                    SOABI=sysconfig.get_config_var('SOABI'),
                    extension_suffix=sysconfig.get_config_var('EXT_SUFFIX'),
                    python=sys.version,
                    binary_sha256=sha256(binary.read_bytes()).hexdigest(),
                    cold_build_load_wall_seconds=time.perf_counter() - started,
                    compiler_cpu_accounting='parent outer process must include compiler children')
    _loaded = module
    return module


def receipt():
    return None if _receipt is None else dict(_receipt)
