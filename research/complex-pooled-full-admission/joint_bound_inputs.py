#!/usr/bin/env python3
"""Run the unchanged exact engine with two byte-identical canonical inputs.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
Only the two input addresses change; all engine predicates and functions remain.
"""
from hashlib import sha256
import json
import types

from common import authenticate
from receipt_transport import HERE, check, need, regular, selected_path


def main():
    authenticate()
    check()
    path = HERE / 'joint_bound.py'
    raw = regular(path)
    recorded = json.loads(regular(HERE / 'EVIDENCE.json'))
    need(sha256(raw).hexdigest() == recorded['execution_source_sha256']['joint_bound.py'],
         'unchanged exact interval engine')
    module = types.ModuleType('pooled_joint_arithmetic_with_canonical_inputs')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec', optimize=0), module.__dict__)
    # Preserve the original readers for every other path, including release-work.
    original_read, original_sha = module.read, module.sha
    module.read = lambda name: original_read(selected_path(name))
    module.sha = lambda name: original_sha(selected_path(name))
    module.main()
    authenticate()


if __name__ == '__main__':
    main()
