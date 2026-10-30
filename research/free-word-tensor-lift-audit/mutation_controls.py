"""Two in-memory mutations of the actual FOUR-base word, with exact witnesses.

Uses the separately written independent.py pullback implementation. Frozen source
exports, existing code and receipts are not modified. Standard library only.
Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import copy
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_lift_audit', HERE / 'independent.py')
I = importlib.util.module_from_spec(spec)
spec.loader.exec_module(I)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def expected(output):
    result = {output: {(): Q(1)}}
    if 112 <= output < 224:
        result[output - 112] = {(): Q(1)}
    return result


def difference(got, want):
    result = copy.deepcopy(got)
    for register, polynomial in want.items():
        I.accumulate(result.setdefault(register, {}), polynomial, Q(-1))
    return {register: polynomial for register, polynomial in result.items() if polynomial}


def serialize(polynomials):
    return [{'initial_input': register,
             'terms': [{'operator_word': list(word), 'coefficient': str(coefficient)}
                       for word, coefficient in sorted(polynomial.items())]}
            for register, polynomial in sorted(polynomials.items())]


def witness(sequence, output):
    error = difference(I.pullback(sequence, output), expected(output))
    need(error, 'mutated literal sequence unexpectedly satisfies this output')
    return {'output_register': output, 'nonzero_error_terms': sum(map(len, error.values())),
            'error_polynomial': serialize(error)}


def compute():
    I.authenticate()
    raw = (HERE / 'source' / 'inputs' / 'FOUR-base.json.gz').read_bytes()
    word = json.loads(gzip.decompress(raw))
    baseline = I.literal(word, False)
    first = next(i for i, correction in enumerate(word['initial_corrections'])
                 if correction['operator_word'])
    correction = word['initial_corrections'][first]
    mutated = copy.deepcopy(word)
    mutated['initial_corrections'][first]['operator_word'] = []
    erased = I.literal(mutated, False)
    correction_witness = witness(erased, correction['target'])
    need(any(term['operator_word'] for item in correction_witness['error_polynomial'] for term in item['terms']),
         'erased-generator control has no surviving operator-word witness')
    # The input is the literal first nonidentity SCALE in the source sequence;
    # only that one executed event is omitted. No cleanup or export is rewritten.
    index = next(i for i, event in enumerate(baseline) if event[0] == 'scale' and event[2] != 1)
    event = baseline[index]
    dropped = baseline[:index] + baseline[index + 1:]
    scale_witness = witness(dropped, event[1])
    # Verify both chosen output functionals pass before their corresponding
    # mutation, so failure is attributed to the exact event edit.
    for output in {correction['target'], event[1]}:
        need(I.pullback(baseline, output) == expected(output), 'baseline witness output does not pass')
    lengths = sorted({len(c['operator_word']) for c in word['initial_corrections']})
    need(lengths == [1], 'source correction-word length census changed')
    return {'schema_version': 1, 'status': 'PASS_ACTUAL_PROGRAM_MUTATION_CONTROLS',
            'provider': 'FOUR-base',
            'erase_first_correction_generator': {
                'initial_correction_index': first, 'source': correction['source'],
                'target': correction['target'], 'coefficient': correction['coefficient'],
                'original_operator_word': correction['operator_word'], 'mutated_operator_word': [],
                'witness': correction_witness},
            'drop_first_nonidentity_scale': {
                'literal_event_index': index, 'register': event[1], 'coefficient': str(event[2]),
                'witness': scale_witness},
            'reordered_correction_word': {'status': 'NOT_APPLICABLE',
                                          'correction_terms': len(word['initial_corrections']),
                                          'distinct_correction_word_lengths': lengths,
                                          'reason': 'Every literal initial correction word has exactly one generator.'}}


if __name__ == '__main__':
    result = compute()
    need(json.loads((HERE / 'MUTATIONS.json').read_bytes()) == result,
         'frozen mutation witness differs')
    print(json.dumps(result, sort_keys=True, indent=2))
