"""Source-bound finite R437 request/topology adapter; no all-size admission.

Derived from Jose Manuel's PR3562/PR2899 and David Arias/PR2753,
Nick Petalas's request/provider lineage, and ai-nanachi/Ali Romman's R437.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'sources/ordinary'))
import predecessor


def require(ok, message):
    if not ok:
        raise ValueError(message)


def replacement(source, before, after, count):
    require(source.count(before) == count, 'exact adaptation context: '+before[:65])
    return source.replace(before, after)


def load():
    ordinary, encoded, binary = predecessor.runtime()
    import catalogue, topology
    expected = json.loads((HERE/'sources/r437/EXPECTED.json').read_bytes())
    paths = {'word': HERE/'sources/r437/data/r0042/R437-COMPOSED-WORD.json.gz',
             'host': HERE/'sources/r437/generated/GLOBAL-TEMPLATE.json.gz',
             'geometry': HERE/'sources/r437/data/GEOMETRY.json'}
    require(hashlib.sha256(gzip.decompress(paths['word'].read_bytes())).hexdigest()
            == expected['word_content_sha256'], 'R437 actual word identity')
    require(hashlib.sha256(gzip.decompress(paths['host'].read_bytes())).hexdigest()
            == expected['template_content_sha256'], 'R437 complete template identity')
    original = Path(catalogue.__file__).read_text()
    source = replacement(original, 'private=661', 'private=659', 1)
    source = replacement(source, '==661', '==659', 3)
    source = replacement(source, 'self.old.WORD,self.old.HOST,self.old.GEO',
                         "R437_PATHS['word'],R437_PATHS['host'],R437_PATHS['geometry']", 1)
    source = replacement(source, 'expected={int(k):v for k,v in self.old.read("research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["profile"].items()}',
                         'expected={int(k):v for k,v in R437_EXPECTED["profile"].items()}', 1)
    source = replacement(source, '==904896', '==903456', 1)
    source = replacement(source, '"f5a4fb124709adc4b56376a3146e3609e91c0f4d3ed1931a61785a5d99bf8ee7"',
                         'R437_REQUEST_DIGEST', 1)
    module = types.ModuleType('r437_catalogue'); module.__file__ = str(HERE/'adapter.py')
    module.R437_PATHS = paths; module.R437_EXPECTED = expected
    module.R437_REQUEST_DIGEST = '0fb70d6838583f2f439a8704eb5dba84ce9dbd231d91f140da13440b680d73aa'
    sys.modules[module.__name__] = module
    exec(compile(source, '<authenticated PR2753 catalogue adaptation>', 'exec'), module.__dict__)
    # Committed ordered request digest; no discovery bypass in the adapter.
    module.R437_REQUEST_DIGEST = REQUEST_DIGEST
    value = module.Catalogue(3)
    code = Path(topology.__file__).read_text()
    code = replacement(code, '==661', '==659', 1)
    topo = types.ModuleType('r437_topology'); sys.modules[topo.__name__] = topo
    exec(compile(code, '<authenticated PR2753 topology adaptation>', 'exec'), topo.__dict__)
    return value, topo.SelectedTopology(value), ordinary, encoded, binary


REQUEST_DIGEST = '0fb70d6838583f2f439a8704eb5dba84ce9dbd231d91f140da13440b680d73aa'
