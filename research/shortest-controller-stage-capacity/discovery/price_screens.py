"""Print optimistic floating prices. These are not certified caller bounds.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
local = json.loads((ROOT / 'research/p104-helper-subspace-splits/RESULT.json').read_text())['local']
paid = {int(r): c for r, c in local['paid'].items()}
helpers = {int(r): c for r, c in local['helpers'].items()}


def screen(n, calls, degrees):
    def margin(kappa):
        t = 1-kappa
        return (104*sum(c*(1+8*d)**t for d, c in degrees.items())
                + calls*sum(c*r**t for r, c in helpers.items())
                - calls*sum(c*r**t for r, c in paid.items()))
    low, high = 0.0, 0.01
    root = None
    if margin(0) > 0 and margin(high) < 0:
        for _ in range(60):
            mid = (low+high)/2
            if margin(mid) > 0:
                low = mid
            else:
                high = mid
        root = round((low+high)/2, 12)
    return {'n': n, 'full_calls': calls, 'main_degree_counts': degrees,
            'floating_raw_crossing': root, 'floating_margin_at_003': round(margin(.003), 8)}


if __name__ == '__main__':
    print(json.dumps({'scope': 'Floating optimistic profiles only; no exact operator or complete kappa claim',
                      'source_head': '09dd0965711ca7eeb169057a420abab1c9052137',
                      'shortest_common_advance': [screen(n, n+1, {2: n-2, 3: 2}) for n in (4, 6, 8, 16)],
                      'paired_before_joint_cut': [screen(n, n+2, {2: n-4, 3: 4}) for n in (4, 8, 12, 16)],
                      'paired_after_one_lost_occurrence': [screen(n, n+2, {2: n-3, 3: 3}) for n in (12, 16, 50, 52, 56)]},
                     indent=2, sort_keys=True))
