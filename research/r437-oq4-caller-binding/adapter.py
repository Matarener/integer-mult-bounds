"""Current OQ4 source binding, derived from zxv/PR3690's adapter.

Reuse Jose Manuel/David Arias's canonical physical runtime without copying an
unrelated ordinary/T360 archive. Apache-2.0; substantial OpenAI Codex assistance.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL = ROOT / 'research/selected-bit-physical-caller'
REQUEST_DIGEST = 'cbfea55f5cd0b74a2a0d4292ad0139d2b5bb73127951127698030bc90c73c532'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def replacement(source, before, after, count):
    require(source.count(before) == count, 'exact adaptation context: ' + before[:65])
    return source.replace(before, after)


def load():
    sys.path.insert(0, str(PHYSICAL))
    import loader
    loader.activate()
    import catalogue, topology
    expected = json.loads((HERE / 'inputs/EXPECTED.json').read_bytes())
    paths = {name: HERE / ('inputs/' + name + '.json.gz')
             for name in ('word', 'template', 'geometry')}
    for name, field in [('word','word_content_sha256'), ('template','template_content_sha256')]:
        require(hashlib.sha256(gzip.decompress(paths[name].read_bytes())).hexdigest()
                == expected[field], 'current R437 ' + name + ' identity')
    require(expected['profile'].get('26') == 32 and '34' not in expected['profile'],
            'current OQ4 profile, not predecessor rank34')
    original = Path(catalogue.__file__).read_text()
    source = replacement(original, 'private=661', 'private=659', 1)
    source = replacement(source, '==661', '==659', 3)
    source = replacement(source, 'self.old.WORD,self.old.HOST,self.old.GEO',
                         "R437_PATHS['word'],R437_PATHS['template'],R437_PATHS['geometry']", 1)
    source = replacement(source, 'expected={int(k):v for k,v in self.old.read("research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["profile"].items()}',
                         'expected={int(k):v for k,v in R437_EXPECTED["profile"].items()}', 1)
    source = replacement(source, '==904896', '==903456', 1)
    source = replacement(source, '"f5a4fb124709adc4b56376a3146e3609e91c0f4d3ed1931a61785a5d99bf8ee7"',
                         'R437_REQUEST_DIGEST', 1)
    module = types.ModuleType('oq4_catalogue')
    module.__file__ = str(HERE / 'adapter.py')
    module.R437_PATHS, module.R437_EXPECTED = paths, expected
    module.R437_REQUEST_DIGEST = REQUEST_DIGEST
    sys.modules[module.__name__] = module
    exec(compile(source, '<PR3690 OQ4 catalogue adaptation>', 'exec'), module.__dict__)
    value = module.Catalogue(3)
    code = replacement(Path(topology.__file__).read_text(), '==661', '==659', 1)
    topo = types.ModuleType('oq4_topology')
    sys.modules[topo.__name__] = topo
    exec(compile(code, '<PR3690 OQ4 topology adaptation>', 'exec'), topo.__dict__)
    return value, topo.SelectedTopology(value)
