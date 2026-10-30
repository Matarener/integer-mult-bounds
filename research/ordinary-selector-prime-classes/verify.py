#!/usr/bin/env python3
"""Fresh source binding, exact class certificates and complete finite census."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    represented = json.loads(json.dumps(value, ensure_ascii=True, allow_nan=False))
    return json.dumps(represented, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def module(name):
    spec = importlib.util.spec_from_file_location('_selector_audit_' + name,
                                                PACKAGE/(name+'.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def authenticate():
    count = 0
    for row in json.loads((PACKAGE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT/row['path']
        require(path.is_file() and not path.is_symlink(), 'regular exact input')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'input SHA256')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw,
                             usedforsecurity=False).hexdigest() == row['git_blob'],
                'input Git blob')
        count += 1
    require(count == 12, 'complete input inventory')
    return count


def run():
    inputs = authenticate()
    binding = module('binding').run()
    require(digest(binding) == digest(json.loads((PACKAGE/'EXPECTED-BINDING.json').read_text())),
            'complete typed fresh source-binding evidence')
    engine = module('engine').run()
    require(digest(engine) == digest(json.loads((PACKAGE/'EXPECTED-ENGINE.json').read_text())),
            'complete typed fresh arithmetic evidence')
    oracle_module = module('oracle')
    oracle = oracle_module.check(engine)
    require(digest(oracle) == digest(json.loads((PACKAGE/'EXPECTED-ORACLE.json').read_text())),
            'complete typed fresh independent bounded census')
    bad = copy.deepcopy(engine['prime_witnesses'][0])
    bad['a'] = 1
    try:
        oracle_module.prime_certificate(bad)
    except ValueError:
        pass
    else:
        raise ValueError('forged prime certificate accepted')
    # Preserve exact integer, Boolean and record structure in stored evidence.
    bad = copy.deepcopy(engine)
    bad['prime_witnesses'][0]['threshold_seams'][0]['k'] += 1
    require(digest(bad) != digest(engine), 'altered exact borrowed width rejected')
    bad = copy.deepcopy(oracle)
    bad['classes'][0]['complete_branch_runs'][0]['fits'] = 0
    require(digest(bad) != digest(oracle), 'integer cannot replace Boolean decision')
    bad = copy.deepcopy(engine)
    bad['prime_witnesses'].pop()
    require(digest(bad) != digest(engine), 'omitted prime class rejected')
    return dict(status='PASS_RETUNED_SELECTOR_PRIME_CLASSES', exact_inputs=inputs,
                profile=engine['profile'], prime_classes=engine['prime_classes'],
                cutoffs=engine['prime_class_cutoffs'],
                complete_bounded_decisions=oracle['complete_decisions'],
                bounded_limit=oracle['limit'],
                selector_controls_rejected=engine['semantic_controls_rejected'],
                source_binding_controls_rejected=len(binding['negative_controls']),
                forged_prime_control_rejected=True, stored_evidence_controls=3,
                binding_payload_sha256=digest(binding),
                engine_payload_sha256=digest(engine), oracle_payload_sha256=digest(oracle),
                proof='PROOF.md supplies forall-e and forall-permitted-prime theorem; finite census is separate evidence',
                scope='conditional scalar Count abstraction only; no native/payload/physical supplier/outer/tau/kappa acceptance')


if __name__ == '__main__':
    require(len(sys.argv) == 1, 'no arguments')
    print(json.dumps(run(), sort_keys=True, separators=(',', ':')))
