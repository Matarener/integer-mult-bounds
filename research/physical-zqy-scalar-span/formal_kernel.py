#!/usr/bin/env python3
"""Source-bound right kernel over formal native free words.

THU New Media Research Center; substantial OpenAI Codex assistance. Apache-2.0.

Only immediately adjacent inverse letters are reduced. No actual monomial
operator identification or phase/group normalization is performed.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import argparse, json, sys, types
HERE = Path(__file__).resolve().parent
NATIVE_SHA = '1bad1ffe747c3977d1a6bc1cfa9faa4127e38cbf49d7fcf4ae8060fbc7f67d4e'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def left_row(row, op, backward):
    # Each nonzero integer is a distinct formal letter with its signed inverse.
    # Direction does not identify forward and backward letters: every direction
    # is tested as a separate word system and independent observation family.
    out = {}
    for (role, old), value in row.items():
        word = () if old == 0 else old
        reduced = word[1:] if word and word[0] == -op else (op,) + word
        key = role, (reduced if reduced else 0)
        q = out.get(key, F(0)) + value
        if q:
            out[key] = q
        else:
            out.pop(key, None)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runtime', type=Path, default=HERE)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    runtime = args.runtime.resolve()
    need(sha256((runtime/'native.py').read_bytes()).hexdigest() == NATIVE_SHA, 'actual native source pin')
    sys.path.insert(0, str(runtime))
    import native as N
    source, provider = N.read('source'), N.read('provider')
    namespace = vars(N).copy()
    namespace['left_row'] = left_row
    replay = types.FunctionType(N.native_replay.__code__, namespace)
    cases = {}
    expected = {'provider_backward': (4891, 119521), 'source_backward': (5019, 80007),
                'source_forward': (4968, 94439)}
    for name, program, backward in [
        ('provider_backward', provider['word'], True),
        ('source_backward', source['programs']['backward'], True),
        ('source_forward', source['programs']['forward'], False),
    ]:
        histories, _, _, _ = replay(source['canonical'], program, backward)
        terms, max_word = 0, 0
        for row in histories:
            residual = {}
            for (role, word), value in row.items():
                need(role[0] == 'L' and 0 <= role[1] < 632, 'original input binding')
                terms += 1
                max_word = max(max_word, 0 if word == 0 else len(word))
                active = role[1] < 224 if backward else 112 <= role[1] < 224
                if active:
                    key = role[1] % 112, word
                    q = residual.get(key, F(0)) + value
                    if q:
                        residual[key] = q
                    else:
                        residual.pop(key, None)
            need(not residual, name + ' exact freeword HK=0')
        need((len(histories), terms) == expected[name], 'frozen formal history family ' + name)
        cases[name] = {'full_frame_histories': len(histories), 'history_formal_terms': terms,
                       'maximum_surviving_word_length': max_word, 'exact_formal_HK_zero': True,
                       'kernel_formula': '[I_112;I_112;0_408x112]' if backward else '[0_112x112;I_112;0_408x112]'}
    result = {'schema': 'native-full-history-freeword-kernel/v1',
              'status': 'PASS_FORMAL_FREEWORD_RIGHT_KERNEL_THREE_CASES',
              'source_native_sha256': NATIVE_SHA, 'cases': cases,
              'distinct_native_generator_names': len(source['canonical']['warps']),
              'reductions': 'Only adjacent signed inverse cancellation on free words.',
              'actual_operator_identifications_used': False, 'phase_or_group_normalization_used': False,
              'matrix_sum_relations_used': False,
              'scope': 'Formal corroboration of the three frozen full-frame observation families, considered separately. Scalar identities over these formal words survive any consistent assignment of invertible operators, hence every tensor width. Ownership and legal native physical semantics remain inherited from the actual source.'}
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE/'FORMAL-KERNEL.json').write_text(encoded)
    else:
        need(json.loads((HERE/'FORMAL-KERNEL.json').read_text()) == result, 'stable formal receipt')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
