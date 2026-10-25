#!/usr/bin/env python3
"""Necessary state/precision budgets; exact for the declared same-grid chain.

Apache-2.0; substantial OpenAI Codex assistance. Unbounded integer-domain
theorem, or sufficiently large input ranges; not a paid-query lower bound.
"""
import argparse
import json
from frontier import load, need


def budget(rounds, components=1, total_relative_guard_bits=0, side_states=1):
    need(type(rounds) is int and rounds >= 1, 'positive round count')
    need(type(components) is int and components >= 1, 'positive component count')
    need(type(total_relative_guard_bits) is int and total_relative_guard_bits >= 0,
         'nonnegative total relative refinement')
    need(type(side_states) is int and side_states >= 1, 'positive side alphabet')
    exponent = 8*rounds*components
    need(exponent <= 10000, 'integer budget exceeded: no decision')
    numerator = 13**exponent
    fractional_slots = 112*components*total_relative_guard_bits
    if fractional_slots >= numerator.bit_length():
        minimum = 1
    else:
        denominator = (1 << fractional_slots)*side_states
        minimum = (numerator+denominator-1)//denominator
    sharp = total_relative_guard_bits == 0 and side_states == 1
    return {'status': 'SHARP_SAME_GRID_HISTORY' if sharp else 'NECESSARY_HISTORY_BOUND',
            'rounds': rounds, 'components': components,
            'minimum_history_states': minimum, 'minimum_packed_bits': (minimum-1).bit_length(),
            'new_fractional_slots': fractional_slots, 'side_states': side_states,
            'large_input_range_required': True,
            'scope': 'Fixed known unimodular frames, bounded rounding residuals, all initial inputs recoverable. Refined/side-information bounds are necessary, not claimed attainable.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    args = parser.parse_args()
    data = load(args.file)
    need(isinstance(data, dict) and set(data) <= {'rounds', 'components',
         'total_relative_guard_bits', 'side_states'} and 'rounds' in data, 'budget fields')
    print(json.dumps(budget(**data), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
