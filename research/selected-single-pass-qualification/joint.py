"""Run both unchanged PR5757 entry points with one shared source execution."""
import json
from pathlib import Path
import runpy
import sys

from orchestration import qualify, require
from source import prepared


def run(root):
    entry = root / 'research/selected-quadratic-replay'
    sys.path.insert(0, str(entry))
    verify = runpy.run_path(str(entry / 'verify.py'))
    cross = runpy.run_path(str(entry / 'cross.py'))
    import state_adapter as adapter
    import verify_source as source
    require(Path(source.__file__).resolve() == entry / 'verify_source.py', 'Exact source module')
    result = qualify(verify['main'], cross['main'], source, adapter)
    require(result['distinct_inputs'] == 17651, 'Complete actual input inventory')
    print('PASS_SINGLE_PASS_COMPLETE_QUALIFICATION', json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    require(not sys.argv[1:], 'No joint replay arguments')
    with prepared() as root:
        run(root)
