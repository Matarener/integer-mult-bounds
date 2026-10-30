#!/usr/bin/env python3
"""Replay the chronological connector theorem package without a solver.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
PREFIX = 'research/coupled31-chronology/'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name):
    spec = importlib.util.spec_from_file_location('coupled31_'+name, PACKAGE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    sources = json.loads((PACKAGE/'SOURCES.json').read_text())
    provenance = {row.get('pin'): row['sha256'] for row in sources['files']
                  if row['usage'] == 'provenance'}
    authenticated = 0
    for row in sources['files']:
        if row['usage'] == 'input':
            require(row['path'].startswith(PREFIX), 'package-local source contract')
            path = PACKAGE/row['path'][len(PREFIX):]
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                    'source hash: '+row['path'])
            require(provenance.get(row['copied_from']) == row['sha256'],
                    'retained copy differs from original provenance')
            authenticated += 1
    checker, prices = load('check'), load('pricing')
    evidence = checker.run()
    price = prices.run()
    endpoint = evidence['endpoints']['long_word']
    invoice = price['complete_binary_word31']
    require(endpoint['thin_rank']*invoice['binary_blocks']
            == invoice['H1_thin_calls_at_104_ports'], 'endpoint/invoice thin rank')
    require(endpoint['full_calls'] == invoice['full_calls']
            and endpoint['thin_maps'] == invoice['thin_maps'], 'endpoint/invoice call counts')
    return {'status': 'PASS_CHRONOLOGICAL_CONNECTOR_RANK_BOUND',
            'scope': 'Paired full star stages over characteristic two; arbitrary thin maps',
            'authenticated_inputs': authenticated,
            'proof_sha256': {name: hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest()
                             for name in ('PROOF.md', 'COST.md', 'COMMUTING.md')},
            'evidence': evidence, 'pricing': price,
            'limits': ['No kappa increase', 'No native lift or complete physical caller',
                       'Written universal proofs with finite controls; no proof-assistant acceptance',
                       'Two finite seed solver timeouts remain unknown']}


if __name__ == '__main__':
    result = run()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if '--write-result' in sys.argv:
        (PACKAGE/'RESULT.json').write_text(encoded)
    else:
        require((PACKAGE/'RESULT.json').read_text() == encoded, 'saved result differs')
    print(encoded, end='')
