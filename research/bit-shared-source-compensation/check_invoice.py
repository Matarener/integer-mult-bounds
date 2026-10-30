#!/usr/bin/env python3
"""Literal repair bill and exact rational tariff intervals; Apache-2.0.

Substantial OpenAI Codex assistance. Does not certify semantic equivalence;
that obligation is independently checked in independent/.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parent


def need(test, message):
    if not test:
        raise ValueError(message)


def construct(word, recipe):
    remove = {row['index']: row for row in recipe['remove']}
    after = {row['index']: row for row in recipe['insert_after']}
    need(len(remove) == len(recipe['remove']) and len(after) == len(recipe['insert_after']),
         'unique recipe indices')
    out = []
    for i, row in enumerate(word['records']):
        if i in remove:
            need(row == remove[i]['expected'], 'matched removal context')
        else:
            out.append(row)
        if i in after:
            need(row == after[i]['expected'], 'matched insertion context')
            out.extend(after[i]['records'])
    return out


def invoice(records):
    h = Counter()
    adds = copies = erases = downward = 0
    for op, d, s, c, rank, section in records:
        if op == 0:
            h[rank] += 1
            downward += section == 40 and c == 509
        elif op == 1:
            adds += 1
        elif op == 2:
            copies += 1
            h[7] += 1
        elif op == 3:
            erases += 1
        else:
            raise ValueError('unknown opcode')
    return {'histogram': dict(sorted(h.items())), 'queries': sum(h.values()),
            'rank_mass': sum(k*v for k,v in h.items()), 'ADDs': adds,
            'COPY_episodes': copies, 'ERASEs': erases, 'new_downward_queries': downward,
            'records': len(records)}


def root_interval(n, power=500, digits=24):
    scale = 10**digits
    target = n * scale**power
    lo, hi = scale, 2*scale
    while lo+1 < hi:
        mid = (lo+hi)//2
        if mid**power <= target:
            lo = mid
        else:
            hi = mid
    need(lo**power <= target < hi**power, 'exact root interval')
    return lo, hi, scale


def main():
    raw = (ROOT/'inputs/WORD.json.gz').read_bytes()
    need(sha256(raw).hexdigest() == 'c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c', 'word bytes')
    blob = gzip.decompress(raw)
    recipe = json.loads((ROOT/'REPAIR.json').read_text())
    need(sha256(blob).hexdigest() == recipe['word_canonical_sha256'], 'canonical word')
    word = json.loads(blob)
    original = invoice(word['records'])
    changed = invoice(construct(word, recipe))
    expected = {1:1322,2:1342,3:79,4:39,5:102,6:11,7:18}
    need(original['histogram'] == expected, 'exact baseline histogram')
    new = expected.copy(); new[2] += 4
    need(changed['histogram'] == new, 'all source transport charged')
    need(original['ADDs'] == changed['ADDs'] == 36005, 'source reads retained once')
    need(original['COPY_episodes'] == changed['COPY_episodes'] == 9, 'COPYs fixed')
    need(original['ERASEs'] == changed['ERASEs'] == 9, 'ERASEs fixed')
    need(changed['queries']-original['queries'] == 4 and changed['rank_mass']-original['rank_mass'] == 8,
         'literal complete profile delta')
    need(changed['new_downward_queries'] == 2, 'both source returns paid')
    lo, hi, den = root_interval(32)
    result = {'status':'PASS_COMPLETE_REPAIR_INVOICE', 'baseline':original,
              'repaired':changed, 'new_families':0, 'new_private_fields':0,
              'raw_tariff_delta_m64_b1over500': {'formula':'8 * 32^(1/500)',
                 'lower_numerator':8*lo,'upper_numerator':8*hi,'denominator':den,
                 'strictly_positive':True},
              'covered':'literal query/ADD/COPY/ERASE/frame-return invoice, no native tape timing',
              'no_new_kappa':True}
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
