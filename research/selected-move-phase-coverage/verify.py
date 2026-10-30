"""Independent rank-one closed-form audit; no native state/tableau engine used for verdict.

Prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0.
Producer is used only to obtain the selected recipe; the checker is direct Q(i) arithmetic.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

if len(sys.argv) != 1:
    raise SystemExit('usage: verify.py')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/p104-native-channel/vendor/clifford_exact.py'
WORD = ROOT / 'research/p104-helper-subspace-splits/WORD.json.gz'
EXPECTED_WORD_SHA256 = 'bbb072bced5824a8d9094c49be2fc51fbfdd05fb2b7dab8106e1275053075099'

def need(value, message):
    if not value:
        raise ValueError(message)

def authenticate():
    """Authenticate the inspected source closure before executing either engine."""
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    checked = []
    for row in rows:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
             == row['git_blob'], 'source Git blob: ' + row['path'])
        checked.append(row['path'])
    return checked

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    sys.modules[name] = out
    spec.loader.exec_module(out)
    return out

def rotate(pair, power):
    # Exact multiplication in Z[i], deliberately no source helper.
    re, im = pair
    for _ in range(power % 4):
        re, im = -im, re
    return re, im

def monomial_image(record, x):
    bits = [(x >> j) & 1 for j in range(9)]
    exponent = record['phase']
    exponent += sum(record['linear_Z4'][j] * bits[j] for j in range(9))
    for j in range(9):
        for k in range(j + 1, 9):
            exponent += 2 * ((record['quadratic_rows'][j] >> k) & 1) * bits[j] * bits[k]
    out = record['offset']
    for j, row in enumerate(record['matrix_rows']):
        bit = sum(((row >> k) & 1) * bits[k] for k in range(9)) % 2
        out ^= bit << j
    return out, exponent % 4

def literal_rank_one_column(recipe, x):
    need(recipe['rank'] == 1, 'rank-one domain')
    y, phase_right = monomial_image(recipe['right'], x)
    column = {}
    # (I+iI+X-iX)/2; all stored values are numerators over 2.
    for middle, numerator in [(y, (1, 1)), (y ^ 1, (1, -1))]:
        z, phase_left = monomial_image(recipe['left'], middle)
        term = rotate(numerator, phase_left + phase_right)
        old = column.get(z, (0, 0))
        column[z] = old[0] + term[0], old[1] + term[1]
    return {k: v for k, v in column.items() if v != (0, 0)}

def closed_form_column(x):
    # From K = D_Q P_G, G e_0 = 11 and q_Q(x)=2*x_3*(x_0+x_1):
    # K C_1 K^-1 = (1+i)/2 I + (1-i)/2 X_11 Z_3.
    sign = -1 if ((x & 1) ^ ((x >> 1) & 1)) else 1
    return {x: (1, 1), x ^ 11: (sign, -sign)}

authenticated_inputs = authenticate()
need(hashlib.sha256(WORD.read_bytes()).hexdigest() == EXPECTED_WORD_SHA256, 'source word hash')
w = json.loads(gzip.decompress(WORD.read_bytes()))
moves = [e for e in w['program'] if e[0] == 'MOVE']
pair_count = len({tuple(e[2:4]) for e in moves})
need((len(moves), pair_count, sum(e[4] for e in moves)) == (3447, 2887, 11),
     'selected MOVE inventory')
index, move = next((i, e) for i, e in enumerate(w['program']) if e[0] == 'MOVE')
need(index == 9589 and move == ['MOVE', 224, 3, 0, False], 'selected first MOVE binding')
need(w['frames'][3] == [] and w['frames'][0] == [11], 'selected chart binding')
need(hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962', 'compiler source hash')
with tempfile.TemporaryDirectory(prefix='move-phase-bytecode-') as cache:
    old_cache = sys.pycache_prefix
    sys.pycache_prefix = cache
    try:
        C = module(SOURCE, 'independent_first_move_producer')
    finally:
        sys.pycache_prefix = old_cache
operation = C.canonical_frame(9, ()).adjoint().then(C.canonical_frame(9, (11,)))
recipe, _ = C.lower_child(operation)
mutant = copy.deepcopy(recipe)
mutant['left']['phase'] = (mutant['left']['phase'] + 1) % 4
offset_mutant = copy.deepcopy(recipe)
offset_mutant['left']['offset'] ^= 1
for x in range(512):
    actual = literal_rank_one_column(recipe, x)
    expected = closed_form_column(x)
    need(actual == expected, 'closed-form operator mismatch at ' + str(x))
    changed = literal_rank_one_column(mutant, x)
    need(changed == {a: rotate(b, 1) for a, b in expected.items()}, 'mutation not exactly i*U')
    need(changed != expected, 'phase-only fault invisible at ' + str(x))
    need(literal_rank_one_column(offset_mutant, x) != expected,
         'address fault invisible at ' + str(x))
# V is used only after the independent verdict, to test its rejection branch.
checker_path = ROOT / 'research/p104-native-channel/vendor/native_verify.py'
need(hashlib.sha256(checker_path.read_bytes()).hexdigest() == '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38', 'checker source hash')
with tempfile.TemporaryDirectory(prefix='move-phase-bytecode-') as cache:
    old_cache = sys.pycache_prefix
    sys.pycache_prefix = cache
    try:
        V = module(checker_path, 'selected_native_checker')
    finally:
        sys.pycache_prefix = old_cache
expected_circuit = V.adjoint(V.frame(w['frames'][3], 9)) + V.frame(w['frames'][0], 9)
V.equal(V.recipe(recipe), expected_circuit, 'positive source control')
need(V.tableau(V.recipe(mutant)) == V.tableau(expected_circuit), 'mutant changed signed action')
try:
    V.equal(V.recipe(mutant), expected_circuit, 'phase-only control')
except ValueError as error:
    need(str(error) == 'phase-only control: exact global phase', 'unexpected rejection path')
    rejection = str(error)
else:
    raise ValueError('source checker accepted phase-only mutation')
report = {
    'status': 'PASS_INDEPENDENT_FIRST_MOVE_CLOSED_FORM',
    'base': 'de5ec2e7a6074068452f45b1a191b5c72832df4a',
    'word_sha256': EXPECTED_WORD_SHA256,
    'producer_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'checker_sha256': hashlib.sha256((ROOT / 'research/p104-native-channel/vendor/native_verify.py').read_bytes()).hexdigest(),
    'event_index_zero_based': index,
    'event': move,
    'domain': 'all 512 width-one basis columns of the first actual MOVE',
    'closed_form': '((1+i)I + (1-i)X_11 Z_3)/2',
    'columns_checked': 512,
    'phase_fault_columns_detected': 512,
    'address_fault_columns_detected': 512,
    'move_occurrences_counted': len(moves),
    'distinct_move_pairs_counted': pair_count,
    'owned_move_occurrences_counted': sum(e[4] for e in moves),
    'newly_replayed_move_pairs': 1,
    'mutant_relation': 'i times original operator',
    'source_signed_tableau_unchanged': True,
    'source_rejection': rejection,
    'origin_column_numerators_over_2': sorted(literal_rank_one_column(recipe, 0).items()),
    'mutant_origin_column_numerators_over_2': sorted(literal_rank_one_column(mutant, 0).items()),
    'new_checker_dependencies': 'standard library; source compiler produces fixture; independent direct column formula decides equality before retained verifier diagnostic',
    'authenticated_inputs': authenticated_inputs,
}
need(json.loads(json.dumps(report)) == json.loads((HERE / 'RESULT.json').read_bytes()),
     'saved audit receipt')
print(json.dumps(report, indent=2))
