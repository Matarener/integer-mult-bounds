"""Independent literal cut-direction audit; no candidate producer imports."""
import argparse
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip
import hashlib
import json
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
REPO = args.repo
ARCHIVE = REPO / 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX = 'candidate/strict/global/base/providers/gauge44/'

def require(test, description):
    if not test:
        raise ValueError(description)

require(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() ==
        'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
        'immutable selected archive bytes')
with tarfile.open(ARCHIVE, 'r:gz') as source:
    word_bytes = source.extractfile(PREFIX + 'CANONICAL-WORD.json.gz').read()
    native_bytes = source.extractfile(PREFIX + 'LOCAL-PROGRAMS.json.gz').read()
require(hashlib.sha256(word_bytes).hexdigest() ==
        '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
        'immutable canonical member bytes')
require(hashlib.sha256(native_bytes).hexdigest() ==
        '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
        'immutable native member bytes')
word = json.loads(gzip.decompress(word_bytes))
native = json.loads(gzip.decompress(native_bytes))['forward']
centres = {r: i for i, r in enumerate(word['centers'])}
expected = Counter()
for op in word['cut']:
    require(op[0] == 'add' and 112 <= op[1] < 224 and op[2] in centres,
            'actual destination/source membership')
    expected[(op[1], centres[op[2]], F(op[3], op[4]))] += 1
actual = Counter()
for event in native:
    if event[0] != 'scalar':
        continue
    gate = event[1]
    if (gate[0] == 'add' and gate[1][0] == 'L'
            and 112 <= gate[1][1] < 224 and gate[2][0] == 'C'):
        require(event[2] == 0, 'actual cut frame zero')
        actual[(gate[1][1], gate[2][1], F(gate[3], gate[4]))] += 1
require(expected == actual and sum(actual.values()) == 176,
        'entire native scatter equals canonical cut')
require((118, 1, F(1, 4)) in actual, 'named native gate exists')

# One local scalar event, with its exact typed destination and source. These
# are event-level inputs; no full-prefix reachability is asserted by this test.
before = {'L118': F(0), 'C1': F(4)}
correct = dict(before)
correct['L118'] += F(1, 4) * correct['C1']
reversed_gate = dict(before)
reversed_gate['C1'] += F(1, 4) * reversed_gate['L118']
require(correct == {'L118': F(1), 'C1': F(4)}, 'true scatter witness')
require(reversed_gate != correct and reversed_gate == before,
        'reversed-operand control rejects')

record = {
    'status': 'PASS_INDEPENDENT_NATIVE_CUT_DIRECTION_AUDIT',
    'canonical_cut_events': sum(expected.values()),
    'native_matching_events': sum(actual.values()),
    'named_native_gate': ['scalar', ['add', ['L', 118], ['C', 1], 1, 4], 0],
    'event_witness': {'before': {'L118': '0', 'C1': '4'},
                      'actual_after': {'L118': '1', 'C1': '4'},
                      'reversed_after': {'L118': '0', 'C1': '4'}},
    'hashes': {
        'archive': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'canonical_member': hashlib.sha256(word_bytes).hexdigest(),
        'native_member': hashlib.sha256(native_bytes).hexdigest(),
    },
    'scope': 'One exact scalar-event witness and all 176 canonical/native cut bindings. No full-prefix reachability or new supplier claim.',
}
args.output.write_text(json.dumps(record, indent=2) + '\n')
print(record['status'])
