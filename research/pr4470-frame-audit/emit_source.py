"""Emit the exact pinned constructor's candidate; no proof functions are called."""
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / 'research/joint-helper-lattice'))
import native_joint

c, programs, baseline, before, changes = native_joint.construct()
print(json.dumps({'canonical': c, 'programs': programs, 'baseline': baseline,
                  'before': before, 'changes': dict(changes)}))
