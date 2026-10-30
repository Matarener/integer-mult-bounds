#!/usr/bin/env python3
"""Run the frozen bounded covector search with component-cache acceleration.

Source identities are recorded in CACHE.json alongside the ordinary search
receipt.  Every proposed positive word must be checked without this cache.
The existing arbitrary-input identity and observer constraints are unchanged.
"""
from hashlib import sha256
from pathlib import Path
import json
import sys
import cached_opt_frames as cached

import joint_fanout_search as original


def main():
    original.optimize = cached.optimize
    original.main()
    argv = sys.argv[1:]
    out = Path(argv[argv.index('--out') + 1])
    sources = {}
    for path in [Path(__file__), Path(cached.__file__),
                 cached.FROZEN / 'joint_fanout_search.py',
                 cached.FROZEN / 'opt_frames.py',
                 cached.FROZEN / 'fanout_search.py']:
        sources[str(path)] = sha256(path.read_bytes()).hexdigest()
    (out / 'CACHE.json').write_text(json.dumps({
        'status': 'DISCOVERY_ACCELERATION_ONLY',
        'component_cache': dict(cached.STATS),
        'sources': sources,
        'obligation': 'Independently replay every positive word without cache before native admission.'
    }, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
