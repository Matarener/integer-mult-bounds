#!/usr/bin/env python3
"""Verify the scoped owned-coding boundaries; no new construction or bound."""
from pathlib import Path
from hashlib import sha256
import argparse
import copy
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
SOURCE_SHA = 'b2a98c4bd0dbe86c09e9d15ee060dcf1aab09dbef90aa1e2127676f4039f406b'


def load(name):
    path = HERE/(name+'.py')
    spec = importlib.util.spec_from_file_location('p104_coding_'+name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def need(ok, message):
    if not ok:
        raise ValueError(message)


def verify():
    raw = (HERE/'inputs/pr5580-WORD.json.gz').read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, 'retained PR5580 source bytes')
    word = json.loads(gzip.decompress(raw))
    classification = load('classification')
    delivery = load('delivery')
    boundary = load('joint_boundary')
    census, modes, producers = classification.classify(word)
    direct = delivery.verify_delivery(word, modes, producers)
    joint = boundary.verify(word)
    controls = {}

    def rejects(label, fn):
        try:
            fn()
        except ValueError as error:
            controls[label] = str(error)
        else:
            raise ValueError('accepted semantic corruption: '+label)

    rejects('missing_mode', lambda: delivery.verify_delivery(word, modes[:-1], producers))
    wrong = copy.deepcopy(modes)
    wrong[0]['coefficients'][0] = '1'
    if wrong == modes:
        wrong[0]['coefficients'][0] = '2'
    rejects('wrong_mode_coefficient', lambda: delivery.verify_delivery(word, wrong, producers))
    wrong_word = copy.deepcopy(word)
    first_copy = producers[0]['copy_event']
    wrong_word['program'][first_copy][3] = '2'
    rejects('wrong_copied_payload', lambda: boundary.verify(wrong_word))
    wrong_word2 = copy.deepcopy(word)
    move = next(e for e in wrong_word2['program'] if e[0] == 'MOVE' and e[4])
    move[4] = False
    rejects('owned_descent_declared_public', lambda: boundary.verify(wrong_word2))
    return {'status': 'PASS_P104_OWNED_CODING_BOUNDARIES', 'new_bound': False,
            'source': {'pr': 5580, 'head': '6efa248cf456d6101d757e9d09ba29711d18a13a', 'sha256': SOURCE_SHA},
            'classification': census, 'direct_delivery': direct,
            'joint_boundary': joint, 'negative_controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate RESULT.json')
    args = parser.parse_args()
    result = verify()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(encoded, encoding='utf-8')
    else:
        need(json.loads((HERE/'RESULT.json').read_bytes()) == result, 'committed result equals fresh exact replay')
    print(result['status'])


if __name__ == '__main__':
    main()
