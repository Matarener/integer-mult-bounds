#!/usr/bin/env python3
"""Pinned geometric premises for the no-axial three-mark invoice bound."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json

HERE=Path(__file__).resolve().parent
PINS={
    'research/p112-rational-decoder-gate/CANDIDATE.json':
        'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
        'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def rank(vectors):
    pivots={}
    for v in vectors:
        while v:
            p=v.bit_length()-1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p]=v
                break
    return len(pivots)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,
                        default=HERE.parents[1])
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args()
    source=[]
    for path,digest in PINS.items():
        data=(args.repo_root/path).read_bytes()
        need(sha256(data).hexdigest()==digest,'immutable input '+path)
        source.append(json.loads(data))
    candidate,data=source
    groups,marks=candidate['groups'],candidate['factor_supports']
    owner={p:i for i,ps in enumerate(groups) for p in ps}
    marked={p:j for j,ps in enumerate(marks) for p in ps}
    label={row['port']:row['q'] for row in data['recipes']}
    need(set(owner)==set(marked)==set(label)==set(range(112)),'all112 ports')
    need(sum(map(len,groups))==sum(map(len,marks))==len(data['recipes'])==112,
         'disjoint partitions and unique labels')
    need(all(0<v<512 for v in label.values()),'nonzero vectors in binary9-space')
    triads=[i for i,ps in enumerate(groups) if len(ps)==3]
    need(len(triads)==37,'37 triads')
    for g in triads:
        ps=groups[g]
        need(all((label[p]&label[q]).bit_count()%2==int(p==q)
                 for p in ps for q in ps),'orthonormal triads')
    def group_rank(indices):
        return rank(label[p] for i in indices for p in groups[i])
    pair_ranks=[[i,j,group_rank((i,j))] for i,j in combinations(triads,2)]
    need(Counter(r for i,j,r in pair_ranks)=={6:605,5:59,4:2},'pair rank profile')
    deficient=[(i,j) for i,j,r in pair_ranks if r==4]
    third_checks=[[i,j,k,group_rank((i,j,k))]
                  for i,j in deficient for k in triads if k not in (i,j)]
    need(len(third_checks)==70 and min(row[3] for row in third_checks)>=5,
         'no three physical triads fit in dimension4')
    roles=sorted({tuple(sorted(owner[p] for p in ps if len(groups[owner[p]])==3))
                  for ps in marks if len(ps)>=2})
    need(len(roles)==18 and all(len(r)==2 for r in roles),'18 paired roles')
    need(len({i for r in roles for i in r})==36,'disjoint role triads')
    need(all(group_rank(r)==6 for r in roles),'orthogonal paired roles span6')
    role_pair_ranks=[[a,b,group_rank(roles[a]+roles[b])]
                     for a,b in combinations(range(18),2)]
    need(Counter(r for a,b,r in role_pair_ranks)=={9:142,8:11},'role pair profile')
    ordinary=[ps for ps in marks if len(ps)==2 and all(len(groups[owner[p]])==3 for p in ps)]
    need(len(ordinary)==53,'53 ordinary marks')
    for ps in ordinary:
        rg=tuple(sorted(owner[p] for p in ps))
        need(len(set(rg))==2 and rg in roles,'ordinary mark occupies a paired role')
        vv=[label[p] for g in rg for p in groups[g]]
        gram=[sum(((x&y).bit_count()%2)<<j for j,y in enumerate(vv)) for x in vv]
        need(rank(gram)==6,'ordinary canonical invoice6')
    receipt={'scope':'finite geometry premises for the written arbitrary-coefficient 12+n bound',
             'source_sha256':PINS,'ports':112,'triad_count':37,'ordinary_marks':53,'ordinary_invoice':6,
             'triad_pair_checks':666,'triad_pair_rank_counts':dict(sorted(Counter(r for i,j,r in pair_ranks).items())),
             'rank4_triad_pairs':deficient,'rank4_pair_third_checks':third_checks,
             'minimum_third_union_rank':min(row[3] for row in third_checks),
             'paired_roles':roles,'role_pair_checks':153,
             'role_pair_rank_counts':dict(sorted(Counter(r for a,b,r in role_pair_ranks).items())),
             'status':'PASS_NO_AXIAL_THREE_MARK_GEOMETRY'}
    payload=json.dumps(receipt,indent=2)+'\n'
    path=HERE/'RESULT.json'
    if args.write_receipt:
        path.write_text(payload,encoding='utf-8',newline='\n')
    else:
        need(path.is_file(),'missing receipt')
        need(path.read_text(encoding='utf-8')==payload,'receipt mismatch')
    print(receipt['status'])


if __name__=='__main__':
    main()
