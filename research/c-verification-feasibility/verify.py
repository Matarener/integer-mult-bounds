"""Scoped fresh checks. This command does not admit a performance improvement."""
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
from portable import prepared, require

HERE = Path(__file__).resolve().parent
require(len(sys.argv) == 2 and sys.argv[1] in ('baseline', 'integer', 'rational'), 'explicit finite scope')
mode = sys.argv[1]
manifest = json.loads((HERE / 'CODE-SOURCES.json').read_text())
for name, digest in manifest.items():
    path = HERE / name
    require(not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == digest,
            'exact qualified prototype source: ' + name)
with prepared(mode) as (root, baseline, stage):
    if mode == 'baseline':
        sys.path.insert(0, str(baseline))
        sys.argv = [str(baseline / 'verify.py')]
        runpy.run_path(sys.argv[0], run_name='__main__')
    elif mode == 'integer':
        sys.path.insert(0, str(stage))
        sys.argv = [str(stage / 'finite_probe.py'), '--source-sha256', manifest['integer/integer_format.c']]
        runpy.run_path(sys.argv[0], run_name='__main__')
    else:
        sys.path.insert(0, str(stage))
        import fractions
        print(json.dumps(dict(runtime_fraction_source_sha256=sha256(Path(fractions.__file__).read_bytes()).hexdigest(),python=sys.version,scope='rational-source-pin-diagnostic'),sort_keys=True))
        from finite_probe import main
        main(stage / 'package', micro=False)
        import arithmetic_binding as binding
        from fractions import Fraction as F
        token = binding.bind()
        require(token is not None, 'original arithmetic binding')
        F.__del__ = lambda self: None
        try:
            require(binding.bind() is None and not binding.fresh(token), 'destructor drift rejects')
        finally:
            del F.__del__
        # A populated expected-code cache must not admit an unknown file.
        import fractions, tempfile
        saved=fractions.__file__
        with tempfile.TemporaryDirectory(prefix='unknown-fraction-source-') as temp:
            foreign=Path(temp)/'fractions.py'
            foreign.write_bytes(Path(saved).read_bytes()+b'\n# unapproved source revision\n')
            fractions.__file__=str(foreign)
            try:
                require(binding.bind() is None, 'unknown Fraction source rejects after cache populated')
            finally:
                fractions.__file__=saved
        require(binding.bind() is not None, 'known Fraction source binding restored')
        print('PASS_ADDED_DESTRUCTOR_AND_UNKNOWN_SOURCE_BINDING_CONTROLS')
print('PASS_C_VERIFICATION_SCOPED_FINITE ' + mode)

