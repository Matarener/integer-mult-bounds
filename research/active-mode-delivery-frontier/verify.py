"""Replay the complete scoped mode-delivery frontier. Apache-2.0."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from inputs import load, need, add
import cuts
import delivery


def channel_controls():
    basis, channels = {}, {}
    need(cuts.extend({0:F(1)}, [F(1)], {(1,2):F(1)}, basis, channels) is None,
         'One noisy response is not a pure mode')
    response = cuts.extend({0:F(1)}, [F(0)], {(3,4):F(1)}, basis, channels)
    need(response == ([F(1)], {(3,4):F(-1), (1,2):F(1)}),
         'Two times can cancel nuisance and create a clean mode')
    basis, channels = {}, {}
    need(cuts.extend({0:F(1)}, [F(1)], {0:F(1)}, basis, channels) is None, 'First independent nuisance')
    need(cuts.extend({1:F(1)}, [F(1)], {1:F(1)}, basis, channels) is None, 'Second independent nuisance')
    need(not channels, 'No false cancellation of independent nuisance coordinates')
    return 3


def run(write=False):
    channel_control_count = channel_controls()
    word, original, modes, core, ce, quadratic = load()
    need(len(modes) == 8 and all(len(row) == 112 for row in modes), 'Eight source modes')
    need(all(sum(x*y for x,y in zip(a,b)) == (56 if i==j else 0)
             for i,a in enumerate(modes) for j,b in enumerate(modes)), 'Exact independent mode matrix')
    scan = cuts.scan(word, modes)
    need(scan['contexts'] == 5331 and scan['projected_columns'] == 3963, 'Complete source state inventory')
    need(all(r['rank'] >= 8 for r in scan['responses']), 'No cheaper clean response in any frame state')
    need(scan['temporal_observations'] == 5715, 'Every distinct one-frame response over all times')
    need(all(r['rank'] >= 8 for r in scan['temporal_responses']), 'Arbitrary same-frame reuse has no cheaper clean channel')
    choices = delivery.choose(scan['responses'])
    candidate, omissions = delivery.emit(word, modes, choices)
    expected = [core.expected(i, True) for i in range(632)]
    raw, _ = delivery.replay(word, candidate, core, expected)
    simplified, final_word = delivery.replay(word, candidate, core, expected, True)
    final, checked_word = delivery.replay(word, final_word, core, expected)
    need(final['paid'] == simplified['paid'] and final['ordinary'] == simplified['ordinary'], 'Emitted zero cleanup is a complete replay')
    need(final_word == checked_word, 'No hidden emitter operation')
    base, _ = delivery.replay(word, original['programs']['backward'], core, expected)
    paid_base = Counter({int(k):v for k,v in base['paid'].items()})
    paid_candidate = Counter({int(k):v for k,v in final['paid'].items()})
    need(paid_candidate == paid_base, 'The legal repair spends exactly the original paid profile')
    # Restore the old precompensation while keeping all new deliveries.
    old = word['programs']['backward']
    capture_length = sum(1 + sum(bool(a) for a in row) for row in modes)
    old_prefix_length = capture_length + len(omissions)
    need(candidate[:capture_length] == [e for i,e in enumerate(old[:old_prefix_length]) if i not in omissions], 'Complete capture prefix')
    bad = deepcopy(old[:old_prefix_length]) + candidate[capture_length:]
    try: delivery.replay(word, bad, core, expected)
    except ValueError as error:
        need(str(error).startswith('All 632'), 'Helper control reaches the complete endpoint check')
    else: raise ValueError('Double helper debit accepted')
    missing = deepcopy(candidate)
    pos = next(i for i,e in enumerate(missing) if e[0]=='center')
    del missing[pos]
    try: delivery.replay(word, missing, core, expected)
    except ValueError: pass
    else: raise ValueError('Unpaid cross-frame delivery accepted')
    wrong = deepcopy(candidate)
    pos = next(i for i,e in enumerate(wrong) if e[0]=='center')
    wrong[pos+1][1][3] *= -1
    try: delivery.replay(word, wrong, core, expected)
    except ValueError: pass
    else: raise ValueError('Wrong delivery sign accepted')
    native = delivery.native(word, choices, ce, quadratic)
    result = dict(scope='Exact optimum for clean one-frame payload channels with arbitrary temporal reuse, and for at most eight such channels even if joint nuisance cancellation is allowed',
                  scan={k:v for k,v in scan.items() if k not in ('responses','temporal_responses')}, complete_mode_responses=len(scan['responses']), temporal_mode_responses=len(scan['temporal_responses']),
                  choices=choices, legal_delivery_native_maps=native, original=base,
                  raw_candidate=raw, simplified_candidate=final, zero_cleanup=simplified['dropped_zero_operations'],
                  omitted_helper_debits=len(omissions), exact_minimum='8 H8',
                  controls=dict(channel_space=channel_control_count, missing_paid_transport=True,double_helper_debit=True,wrong_payload_sign=True,wrong_native_phase=8))
    result = json.loads(json.dumps(result))
    if write:
        (ROOT/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        (ROOT/'CUTS.json').write_text(json.dumps(scan['responses'],indent=2,sort_keys=True)+'\n')
        (ROOT/'TEMPORAL.json').write_text(json.dumps(scan['temporal_responses'],indent=2,sort_keys=True)+'\n')
        (ROOT/'WORD.json').write_text(json.dumps(final_word,separators=(',',':'))+'\n')
    else:
        need(result == json.loads((ROOT/'RESULT.json').read_text()), 'Entire committed receipt')
        need(scan['responses'] == json.loads((ROOT/'CUTS.json').read_text()), 'Every attainable response witness')
        need(scan['temporal_responses'] == json.loads((ROOT/'TEMPORAL.json').read_text()), 'Every temporal response witness')
        need(final_word == json.loads((ROOT/'WORD.json').read_text()), 'Literal complete delivery word')
    return result


if __name__=='__main__':
    need(sys.argv[1:] in ([], ['--write-result']), 'Known replay mode')
    print(json.dumps(run(bool(sys.argv[1:])),indent=2,sort_keys=True))
    print('PASS_ACTIVE_MODE_DELIVERY_FRONTIER')
