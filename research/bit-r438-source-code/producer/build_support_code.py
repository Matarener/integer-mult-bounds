#!/usr/bin/env python3
"""R438 source code that only deletes support from each K column.

Three actual source rows remain identity. Target repair is still three direct
source-pivot snapshots. A matched native global decoder is NOT supplied.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE  # rebound to fresh signed ancestry by reconstruct.py
sys.dont_write_bytecode = True
import bit_transvection as base
import bit_section_code as section
import bit_scalar_invoice as scalar
import bit_signed_lift as signed


def authenticate_predecessor(packed):
    raise ValueError('Use reconstruct.py to authenticate the regenerated predecessor payload')


def main():
    old_blob = (SOURCE/'BIT-SIGNED-WORD.json.gz').read_bytes()
    authenticate_predecessor(old_blob)
    old_word = json.loads(gzip.decompress(old_blob))
    original,builder,baseline,_ = base.load()
    raw = base.matrices(original)
    data = section.section(raw)
    selected = data['selected']
    pk = [raw['K'][p] for p in selected]
    y = [a^b for a,b in zip(data['N'],base.product(data['S'],pk))]
    base.require(base.rank(y) == 9,'Support-preserving quotient is singular')
    wprime = [0 if p in selected else row for p,row in enumerate(raw['K'])]
    a = [(1<<p)^row for p,row in enumerate(base.product(wprime,raw['R']))]
    ainv = base.inverse(a)
    base.require(base.product(raw['J'],ainv) ==
                 [(1<<p)^row for p,row in enumerate(data['Q'])], 'Same three-row repair fails')
    base.require(base.product(data['B0'],y) == pk,'Left-null section identity fails')
    base.require(base.rank(wprime) == 9 and
                 base.rank([v^(1<<p) for p,v in enumerate(a)]) == 9,'Code rank differs')
    data.update(H=a,Hinv=ainv,X=base.inverse(y),Y=y,D=pk,Wprime=wprime)
    # The old arbitrary kernel-completion choice is not part of this variant.
    data.pop('X0'); data.pop('T'); data.pop('W')
    code, code_meta = section.compact_code(data,raw['selected'])
    for rec in code:
        if rec[5] == 24:
            rec[3] = -1
    cut = next(i for i,r in enumerate(old_word['records']) if r[0] == 1 and r[5] == 21)
    records = [r[:] for r in old_word['records'][:cut]] + code
    episodes = []
    for p in selected:
        query = data['Q'][p]
        pivot = (query & -query).bit_length()-1
        sources = [i for i in base.bits(query) if i != pivot]
        cap = original['final'][111+p]
        records += [[1,pivot,i,1,1,31] for i in sources]
        records += [[2,pivot,660,1,cap,1],[1,111+p,660,1,cap,32],
                    [3,pivot,660,1,cap,0]]
        records += [[1,pivot,i,-1,1,33] for i in reversed(sources)]
        episodes.append(dict(target=p,query=query,source_pivot=pivot,
                             prepare_adds=len(sources),source_frame=1,private_frame=cap,copy_rank=1))
    ff=base.replay(original,builder,records,data)
    bf=base.replay(original,builder,records,data,reverse=True)
    expected=Counter({int(k):n for k,n in baseline['profile'].items()})
    expected[7]-=9;expected[1]+=3
    base.require(ff['profile'] == bf['profile'] == dict(sorted(expected.items())) and
                 ff['rank_mass'] == 5061 and ff['copies'] == 3,'Changed local bill')
    f,fs=scalar.execute(records,scalar.eye(660))
    b,bs=scalar.execute(records,scalar.eye(660),reverse=True)
    rt,rts=scalar.execute(records,f,reverse=True)
    base.require(rt == scalar.eye(660),'All-column integer roundtrip')
    az,aiz=signed.source_integer_code(records)
    for i in range(111):
        base.require(f[i] == az[i]+[0]*549 and b[i] == aiz[i]+[0]*549,'Integer source code')
        base.require(f[111+i][111:222] == [int(i==j) for j in range(111)] and
                     all(v%2 == 0 for v in f[111+i][222:]),'Integer target contract')
    for i in range(222,660):
        e=[int(i==j) for j in range(660)]
        base.require(f[i] == b[i] == e,'Integer helper restoration')
    ef=[1<<i for i in range(660)]+[0]; eb=ef[:]
    for p in range(111):
        ef[p]=a[p];ef[111+p]^=a[p];eb[p]=ainv[p];eb[111+p]^=1<<p
    base.require(scalar.parity(f)==ef and scalar.parity(b)==eb,'Full F2 coded endpoints')
    # The nine independent K coefficient vectors from the old output geometry
    # still have support rank7 or less after rows0,1,2 are deleted.
    geometry=[]
    for q in raw['M']:
        old_support=[p for p,row in enumerate(raw['K']) if (row&q).bit_count()&1]
        support=[p for p,row in enumerate(wprime) if (row&q).bit_count()&1]
        dim=builder.rank(original['lines'][p] for p in support)
        base.require(set(support).issubset(old_support) and dim<=7,'Output support cap failed')
        geometry.append(dict(coefficient=q,support=support,rank=dim))
    base.require(base.rank(raw['M'])==9,'Output support vectors do not form basis')
    controls=[base.must_fail('omit_pivot_unprepare',lambda:base.replay(original,builder,
                 [r for r in records if not(r[0]==1 and r[5]==33)],data)),
              base.must_fail('mutate_live_source_snapshot',lambda:base.replay(original,builder,
                 records,data,mutate_snapshot=True)),
              base.must_fail('wrong_source_inverse',lambda:base.replay(original,builder,
                 records,{**data,'Hinv':a},reverse=True))]
    container=dict(format='coded-r438-support-preserving-three-source-copy-v1',
                   public_registers=660,private_register=660,
                   source_word=str(base.WORD),source_gzip_sha256=base.WORD_SHA,
                   start=original['start'],final=original['final'],records=records,
                   record_schema='[op,dst,src,coefficient/sourceframe,frame/privateframe,phase/rank]',
                   copy_schema='[2,physical_source,660,sourceframe,privateframe,rank]',
                   erase_schema='[3,physical_source,660,sourceframe,privateframe,0]')
    payload=base.canonical(container)
    packed=gzip.compress(payload,mtime=0)
    (HERE/'BIT-SUPPORT-WORD.json.gz').write_bytes(packed)
    out=dict(status='PASS_LOCAL_SUPPORT_PRESERVING_CODE_THREE_COPIES_NO_GLOBAL_DECODER_NO_KAPPA',
             source_pin=base.MAIN_PIN,source_word_sha256=base.WORD_SHA,
             word_gzip_sha256=hashlib.sha256(packed).hexdigest(),
             word_canonical_sha256=hashlib.sha256(payload).hexdigest(),matrices=data,
             source_code=code_meta,episodes=episodes,output_support_basis=geometry,
             reader_pairing='Not established: output-basis rebasing changes reader rows; no free mixing of different ret frames.',
             forward_frames=ff,reverse_frames=bf,integer_forward=fs,integer_reverse=bs,
             integer_roundtrip=rts,ADDs=sum(r[0]==1 for r in records),
             source_code_ADDs=len(code),rank_mass_saved=60,negative_controls=controls,
             scope='All660 local integer/F2 columns, exact helper/source restoration, signed inverse, original frame paths and copied snapshot lifetime. Native cap and independent audit separate. No global endpoint, source reader, dirt timing, owner, precision, physical tape or kappa admission.')
    (HERE/'BIT-SUPPORT.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','word_canonical_sha256','ADDs','source_code_ADDs','rank_mass_saved')},sort_keys=True))


if __name__=='__main__':
    main()
