#!/usr/bin/env python3
"""Bind the pruned invoice to the literal local word and every pending operator.

The native operator implementation is the retained PR2653 checker, not an
independent implementation. The independent owner reconstruction is separate.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import gzip
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('portable_check', ROOT/'verify.py')
v = importlib.util.module_from_spec(spec)
exec(compile((ROOT/'verify.py').read_bytes(),str(ROOT/'verify.py'),'exec',dont_inherit=True,optimize=0),v.__dict__)
need = v.need


def local_profile(word, program, rank):
    dims = [rank([word['lines'][j] for j in frame]) for frame in word['frames']]
    masks = [sum(1 << j for j in frame) for frame in word['frames']]
    deleted = set(program['deleted_public_families'])
    need(deleted == set(range(471,480)), 'deleted local families')
    need(program['start'] == [f for i,f in enumerate(word['start']) if i not in deleted], 'local start binding')
    need(program['final'] == [f for i,f in enumerate(word['final']) if i not in deleted], 'local final binding')
    state = program['start'][:] + [None]
    copied = None
    paid, count = Counter(), Counter()
    for op,x,y,c,f,phase in program['records']:
        count[op] += 1
        if op == 0:
            need(state[x] == y and dims[c]-dims[y] == f > 0, 'literal local MOVE rank')
            need(not masks[y] & ~masks[c], 'local MOVE nesting')
            need(x != copied, 'live copied source moved')
            state[x] = c
            paid[f] += 1
        elif op == 1:
            need(x != y and x != copied and state[x] == state[y] == f, 'local ADD frame or copied source')
        elif op == 2:
            need(copied is None and y == 651 and state[y] is None, 'local COPY lifecycle')
            need(state[x] == c and not masks[f] & ~masks[c], 'local COPY frame')
            need(dims[c]-dims[f] == phase == 1, 'local COPY rank')
            state[y],copied = f,x
            paid[phase] += 1
        else:
            need(op == 3 and y == 651 and copied == x and state[x] == c and state[y] == f and phase == 0,
                 'local ERASE original snapshot')
            state[y],copied = None,None
    need(copied is None and state[:-1] == program['final'], 'local final state')
    need(count[2] == count[3] == 3 and count[1] == 13223, 'local event coverage')
    need(paid == Counter({1:1298,2:1342,3:79,4:44,5:93,6:11,7:9}), 'local paid histogram')
    return paid, count


def main():
    p = v.Portable(ROOT)
    p.check_all(); p.install()
    m = p.load('frozen/upstream/research/r438-rehost-projectors/verify.py')
    m.source_check()
    base = ROOT/'frozen/upstream/research'
    word = json.loads(gzip.decompress(p.authenticate(base/'bit-r438-transport-rehost/words/r438-t154.json.gz')))
    program = json.loads(gzip.decompress(p.authenticate(base/'bit-r438-source-code/WORD.json.gz')))
    local, counts = local_profile(word,program,m.rank)
    _,children,windows = m.chronology()
    layout = json.loads(p.authenticate(base/'bit-r438-transport-rehost/verify_rehost.receipt.json'))['placement']['selection']
    old,_ = m.expand(layout,children,windows,438)
    new = [s[:5]+(s[5]-(9 if s[5]>257 else 0),) for s in old if not 249 <= s[5] <= 257]
    audit,signatures,complements = m.audit(new,children,windows,429)
    columns = m.operator_check(word['lines'],signatures)
    rejected=[]
    def reject(name, action, marker):
        try: action()
        except ValueError as e:
            need(marker in str(e),'wrong control rejection: '+str(e)); rejected.append(name)
        else: raise ValueError('control accepted: '+name)
    reject('missing_retained_helper',lambda:m.audit(new[1:],children,windows,429),'missing helper')
    reject('duplicate_retained_helper',lambda:m.audit(new+[new[0]],children,windows,429),'duplicate helper')
    target,parts=next(s for s in signatures if any(x and x & ~255 for x in s[1]))
    victim=next(x for x in parts if x & ~255)
    bit=(victim & ~255) & -(victim & ~255)
    bad=tuple(x^bit if x==victim else x for x in parts)
    reject('missing_pending_axis',lambda:m.factorization(bad,target),'wrong pending operator')
    outside=next(i for i in range(8,64) if not target>>i&1)
    wrong=tuple((x^bit^(1<<outside)) if x==victim else x for x in parts)
    reject('equal_rank_wrong_axis',lambda:m.operator_check(word['lines'][:1],{(target,wrong)}),'exterior address operator')
    corrupted=dict(program,records=[x for x in program['records'] if x[0]!=2])
    reject('missing_local_copy',lambda:local_profile(word,corrupted,m.rank),'local ADD frame')
    result={'status':'PASS_PRUNED_OWNER_NATIVE_REMAINDERS','local_profile':dict(sorted(local.items())),
            'local_event_counts':dict(sorted(counts.items())),'owner_audit':audit,
            'distinct_pending_signatures':len(signatures),'ports':len(word['lines']),
            'address_basis_columns':columns,'controls':rejected,'no_new_kappa':True}
    p.equal(ROOT/'NATIVE-REMAINDERS.json',result)
    p.check_all()
    print(v.canonical(result))


if __name__ == '__main__':main()
