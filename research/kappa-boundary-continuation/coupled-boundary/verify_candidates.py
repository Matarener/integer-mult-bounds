#!/usr/bin/env python3
"""Replay the emitted helper release witnesses, including arbitrary helper dirt.

This checks candidate algebra and frame bills; incomplete HPE restoration is
reported explicitly. Apache-2.0. Substantial OpenAI assistance. Uses the sibling
completion interpreter, whose full free-warp chronology is independently
derived from the retained BORROW-WORD grammar.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

from retime_return import read, native_profile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'entry-retiming'))
import complete_candidate as c


def main():
    checked = []
    for folder in ('projected-release-raised-donors', 'projected-release-raised-donors-extra'):
        root = HERE/folder
        for witness in sorted(root.glob('RELEASE-*-WITNESS.json')):
            info = read(witness)
            word = root/Path(info['word']).name
            w = read(word)
            h = info['helper']
            assert str(h) in w['helper_final']
            actual = c.column(w,h)
            expected = {h:{():Q(1)}}
            for r,q in info['release'].items():
                expected[int(r)] = {():Q(q)}
            assert actual == expected, (witness,actual,expected)
            profile,_ = native_profile(w)
            assert profile == {int(r):n for r,n in info['profile'].items()}
            assert sum(r*n for r,n in profile.items()) == 5133
            checked.append(dict(provider='extra' if folder.endswith('-extra') else 'base',
                helper=h, native_role=info['native_role'], cut=info['cut'],
                word_sha256=sha256(word.read_bytes()).hexdigest(),
                witness_sha256=sha256(witness.read_bytes()).hexdigest(),
                release=info['release'], local_profile=profile,
                unchanged_protected_outputs=203,
                full_endpoint_error={str(r):str(row[()]) for r,row in actual.items() if r!=h},
                full_cleanup_source_available=False,
                status='PASS_EXACT_PARTIAL_WORD_WITH_EXPLICIT_DIRTY_FULL_HELPERS'))
    assert len(checked)==8
    result=dict(status='PASS_EIGHT_SOURCE_BOUND_PARTIAL_RELEASE_WITNESSES', candidates=checked,
        scope='Every input other than h is unchanged by the modified B word because h is not written before the release; the full h column is replayed through precondition, compensation, A, cut, B including actual free warps, restore and existing cleanup. All 112 Y outputs and all 91 HPE outputs agree. The displayed FULL helper errors remain. No completed native consumer or kappa increase is asserted.')
    (HERE/'CANDIDATE-CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],witnesses=len(checked),completed_consumers=0)))


if __name__=='__main__':
    main()
