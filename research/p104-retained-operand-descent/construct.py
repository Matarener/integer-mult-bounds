"""Retain one operand and change the order of two additions.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source word is by DreamingOfClouds (PR6144); see NOTICE for earlier credit.
The full-payload comparison follows Douglas Colkitt's portability repair.
"""
from copy import deepcopy
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sources import base_word, need

# These positions refer to the authenticated PR6144 word.
REPLACEMENTS = {
    12913: (["MOVE", 451, 3, 737, False], [
        ["MOVE", 451, 3, 595, False]]),
    12918: (["ADD", 451, 228, "1", 737], [
        ["INIT", 770, 737], ["COPY", 770, 228, "1", 737]]),
    13486: (["MOVE", 772, 520, 737, True], []),
    13487: (["ADD", 451, 772, "-4", 737], []),
    13488: (["MOVE", 772, 737, 595, True], [
        ["MOVE", 772, 520, 595, True],
        ["ADD", 451, 772, "-4", 595],
        ["MOVE", 451, 595, 737, False],
        ["ADD", 451, 770, "1", 737],
        ["CLEAR", 770, 737]])
}


def construct(base):
    """Return the full word after the five declared replacements."""
    word = deepcopy(base)
    program = []
    for index, event in enumerate(base['program']):
        if index in REPLACEMENTS:
            expected, replacement = REPLACEMENTS[index]
            need(event == expected, 'Exact source event at ' + str(index))
            program.extend(deepcopy(replacement))
        else:
            program.append(deepcopy(event))
    word['program'] = program
    need(len(program) == 22821, 'Exact new event count')
    return word


def payload(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def matches_shipped(value, compressed):
    return gzip.decompress(compressed) == payload(value)


if __name__ == '__main__':
    word = construct(base_word())
    if '--write' in sys.argv:
        (HERE / 'WORD.json.gz').write_bytes(gzip.compress(payload(word), mtime=0))
    need(matches_shipped(word, (HERE / 'WORD.json.gz').read_bytes()),
         'Complete regenerated word payload')
    print('PASS_RETAINED_OPERAND_WORD')
