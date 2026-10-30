"""Pinned source-map reconstruction and literal cell-controller checks. Apache-2.0."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import gzip
import json
import sys
from pathlib import Path
import oracle
import router

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT = "research/joint-query/certificate.json.gz"
CERT_SHA = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"


def source_check():
    raw = (ROOT / CERT).read_bytes()
    router.need(sha256(raw).hexdigest() == CERT_SHA, "frozen joint-query bytes")
    packet = json.loads(gzip.decompress(raw))
    events = []
    for event in packet['programs']['B_1_2']:
        if event[0] == 'retained_core':
            events.extend(packet['core_words'][event[1]])
        elif event[0] in ('private_sweep', 'cover_sweep'):
            events.extend(event[2])
        else:
            events.append(event)
    used = Counter(e[2] for e in events if e[0] == 'cover_map')
    router.need(len(events) == 27019 and sum(used.values()) == 528 and len(used) == 512,
                "literal B1 map multiplicities")
    rows = []
    for name, multiplicity in sorted(used.items()):
        item = packet['map_registry'][name]
        router.need(item['action'] == 'out(d,z_1,...,z_lambda)=in(d*g,z_1 XOR d*delta,...,z_lambda XOR d*delta)', 'literal full-cover contract')
        g = item['owner_right_matrix_columns']; delta = item['payload_translation_at_identity_owner']
        cs = router.coefficients(73, 1, g, delta)
        h = oracle.inverse_rows(oracle.rows(g))
        router.need(oracle.cols(h) == router.inverse(g), 'independent inverse')
        gg=oracle.rows(g)
        router.need(oracle.product_matrix(h,gg) ==
                    [[int(i==j)for j in range(73)]for i in range(73)],
                    'independent row-matrix inverse')
        q_independent = 73*sum(map(sum, h)) + 73*(1+oracle.vector(h,delta).bit_count())
        router.need(q_independent == sum(map(len,cs)), 'independent row-based read bill')
        rows.append(dict(map=name, multiplicity=multiplicity,
                         relabel_reads=sum(map(len, cs)),
                         inverse_ones=sum(c.bit_count() for c in router.inverse(g)),
                         inverse_translation_ones=router.apply(router.inverse(g), delta).bit_count()))
    total = sum(a['multiplicity'] * a['relabel_reads'] for a in rows)
    dimension = 73*73 + 73
    return dict(map_events=528, unique_maps=512, dimension=dimension,
                total_relabel_reads=total, maps=rows,
                whole_word_per_owner=dict(N_constant=(2*dimension+2)*total +
                    528*(32*dimension+32)*(dimension+2),
                    N_times_W=1056*(32*dimension+32),
                    constant=528*64*(dimension+1)+528),
                source_sha256=sha256(raw).hexdigest())


def one_case(n, depth, g, delta, owners, payload_bits=12):
    inputs = []
    expected = {}
    for owner in owners:
        for zs in product(range(1 << n), repeat=depth):
            value = format(len(inputs) % (1 << payload_bits), '0'+str(payload_bits)+'b')
            router.need(len(value) == payload_bits, 'distinct fixture payload width')
            old = oracle.key(owner, zs, n)
            target_owner, target_z = oracle.push(g, delta, owner, zs)
            target = oracle.key(target_owner, target_z, n)
            router.need(oracle.pull(g, delta, target_owner, target_z) == (owner, list(zs)),
                        'independent semantic inverse')
            expected[target] = value
            inputs.append((old, value))
    inputs.sort()
    router.need(set(expected) == {k for k, _ in inputs}, 'actual owner-set closure')
    source = router.encode(inputs)
    machine = router.Machine(source, len(source))
    cs = router.coefficients(n, depth, g, delta)
    machine.run(cs)
    result = "".join(machine.tapes[0])
    router.need(machine.heads == [0]*4, "returned heads")
    router.need(all(set(t) <= {router.BLANK} for t in machine.tapes[1:]), "scratch restored")
    router.need(router.decode(result) == sorted(expected.items()), 'physical route versus independent oracle')
    router.need(machine.steps <= router.bound(len(cs), payload_bits, len(inputs), sum(map(len,cs))), 'proven time bound')
    return dict(n=n, depth=depth, records=len(inputs), steps=machine.steps,
                bound=router.bound(len(cs), payload_bits, len(inputs), sum(map(len,cs))),
                scratch_restored=True, heads_returned=True,
                visited_min=machine.low, visited_max=machine.high,
                actions=machine.counts)


def controls():
    g=[2,1]; delta=1; owners=list(oracle.all_invertible(2))
    good=router.coefficients(2,1,g,delta)
    sample=[(oracle.key(o,[z],2),format(i*4+z,'05b')) for i,o in enumerate(owners) for z in range(4)]
    sample.sort();s=router.encode(sample)
    expected={oracle.key(*oracle.push(g,delta,o,[z]),2):format(i*4+z,'05b')for i,o in enumerate(owners)for z in range(4)}
    bad=[list(a)for a in good];bad[-1]=bad[-1][:-1]
    m=router.Machine(s,len(s));m.run(bad);wrong="".join(m.tapes[0])
    router.need(router.decode(wrong)!=sorted(expected.items()),'translation mutant detected')
    m=router.Machine(s,len(s));m.relabel(good)
    for j in range(len(good)):m.partition(j)
    m.copy_back();router.need(router.decode(''.join(m.tapes[0]))!=sorted(expected.items()),'wrong radix direction detected')
    rejected=[]
    for name,operation in [('singular',lambda:router.coefficients(2,1,[1,1],0)),('translation range',lambda:router.coefficients(2,1,[1,2],4)),('exterior move',lambda:router.Machine(s,len(s)).move(0,-1))]:
        try:operation()
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted '+name)
    return ['translation mutant','wrong radix direction',*rejected]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',type=Path);ap.add_argument('--source-only',action='store_true');args=ap.parse_args()
    source=source_check()
    cases=[]
    if not args.source_only:
        cases.append(one_case(1,1,[1],1,[[0]],1))
        cases.append(one_case(2,1,[1,2],0,[[0,0]],1))
        gs=list(oracle.all_invertible(2))
        for g in gs:
            for delta in range(4):cases.append(one_case(2,1,g,delta,gs,5))
        cases.append(one_case(2,2,[2,1],3,gs,7))
        three=list(oracle.all_invertible(3));cases.append(one_case(3,1,[2,4,1],5,three,11))
    result=dict(status='PASS_PINNED_SOURCE_MAPS_ONLY' if args.source_only else 'PASS_TAGGED_COVER_ROUTE_CHECKS',scope='Exact finite map-source reconstruction and finite four-tape model tests; the universal physical theorem is an informal proof, not Lean-verified.',source=source,cases=cases,controls=[]if args.source_only else controls(),code_sha256={n:sha256((HERE/n).read_bytes()).hexdigest() for n in ['router.py','oracle.py','verify.py']},python=sys.version.split()[0])
    if not args.write and not args.source_only:
        expected=json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
        for field in ('status','source','cases','controls','code_sha256'):
            router.need(result[field] == expected[field], 'committed receipt mismatch: '+field)
    if args.write:
        router.need(not args.write.exists(),'fresh receipt required');args.write.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k!='source'}|{'source_summary':{k:v for k,v in source.items()if k!='maps'}},sort_keys=True))

if __name__=='__main__':main()
