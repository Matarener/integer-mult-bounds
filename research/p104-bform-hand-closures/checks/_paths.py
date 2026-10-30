# Import paths for the checks: the repo's research/nine-term-outside-colspace/checks (E8 lines, frames: common2,
# frames_data, lib) and research/p104-bform-nine-term-floor/checks (lbz: flat list, exact root rank, <= 4 exceptions).  Apache-2.0.
import sys
from pathlib import Path
_R = Path(__file__).resolve().parents[3]
for p in (_R / 'research' / 'p104-bform-nine-term-floor' / 'checks', _R / 'research' / 'nine-term-outside-colspace' / 'checks'):
    if str(p) not in sys.path: sys.path.insert(0, str(p))
