"""Cold-build the owned C source; reuse code only within this process."""
from hashlib import sha256
import atexit
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time

HERE=Path(__file__).resolve().parent
_loaded=None
_temporary=None
_receipt=None

def source_hash():
    path=HERE/'score_probe.c'
    digest=sha256(path.read_bytes()).hexdigest()
    expected=json.loads((HERE/'PROBE-SOURCE.json').read_text())['sha256']
    if path.is_symlink() or digest!=expected:raise ValueError('exact owned C source')
    return digest

def load():
    global _loaded,_temporary,_receipt
    digest=source_hash()
    if _loaded is not None:
        if _receipt['source_sha256']!=digest:raise ValueError('loaded native code has this exact source')
        return _loaded
    if platform.python_implementation()!='CPython' or sys.version_info[:2]!=(3,12) or sys.platform!='linux':
        raise RuntimeError('native feasibility requires Linux CPython 3.12')
    compiler=shutil.which('cc')
    if not compiler:raise RuntimeError('native feasibility requires an existing C compiler')
    start=time.perf_counter()
    _temporary=tempfile.TemporaryDirectory(prefix='fraction-native-owned-')
    atexit.register(_temporary.cleanup)
    root=Path(_temporary.name)
    raw=(HERE/'score_probe.c').read_bytes()
    if sha256(raw).hexdigest()!=digest:raise ValueError('C source remained authenticated at snapshot')
    snapshot=root/'score_probe.c';snapshot.write_bytes(raw);snapshot.chmod(0o444)
    destination=root/('_score_probe'+sysconfig.get_config_var('EXT_SUFFIX'))
    flags=['-O2','-shared','-fPIC','-std=c11','-Wall','-Werror','-I'+sysconfig.get_path('include')]
    command=[compiler,*flags,str(snapshot),'-o',str(destination)]
    build=subprocess.run(command,capture_output=True,text=True,check=False)
    if build.returncode or build.stderr or build.stdout:
        raise RuntimeError('native build rejected: '+json.dumps(dict(command=command,returncode=build.returncode,stdout=build.stdout,stderr=build.stderr)))
    destination.chmod(0o444)
    spec=importlib.util.spec_from_file_location('_score_probe',destination)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    _receipt=dict(source_sha256=digest,compiler=compiler,flags=flags,SOABI=sysconfig.get_config_var('SOABI'),
                  extension_suffix=sysconfig.get_config_var('EXT_SUFFIX'),python=sys.version,
                  binary_sha256=sha256(destination.read_bytes()).hexdigest(),cold_build_load_wall_seconds=time.perf_counter()-start,
                  compiler_cpu_accounting='outer GNU time user+system includes compiler children',
                  compiler_version=subprocess.run([compiler,'--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0])
    _loaded=value
    return value

def receipt():return None if _receipt is None else dict(_receipt)
