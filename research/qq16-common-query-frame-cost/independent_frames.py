"""No inherited-code execution: row matrices and direct character polarization."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import gzip
import io
import json
import tarfile
from fractions import Fraction as F
from query_frame_sources import ROOT,authenticate,need


def mul_rows(a,b):
    return tuple(_xor_selected(b,row) for row in a)


def _xor_selected(rows,mask):
    result=0
    for j,row in enumerate(rows):
        if mask>>j&1:
            result^=row
    return result


def apply_rows(rows,value):
    return sum(((r&value).bit_count()%2)<<i for i,r in enumerate(rows))


def native_owner(recipe,stage):
    # Build rows from I + sum s_i s_i^T, independently of column routing.
    swaps=[v^(1<<(9+8*(stage-1)+j)) for j,v in enumerate(recipe['idle_children'][0]['orthogonal_axes'][:8])]
    return tuple((1<<i)^_xor_selected(swaps,sum(((v>>i)&1)<<j for j,v in enumerate(swaps))) for i in range(73))


def sampled_gram(vectors):
    def phase(x):
        return sum((v&x).bit_count()%2 for v in vectors)%4
    single=[phase(1<<i) for i in range(73)]
    rows=[(v%2)<<i for i,v in enumerate(single)]
    for i in range(73):
        for j in range(i+1,73):
            c=(phase((1<<i)|(1<<j))-single[i]-single[j])%4
            need(c in (0,2),'even character polarization')
            if c==2:
                rows[i]^=1<<j;rows[j]^=1<<i
    return tuple(rows)


def elementary_rank(vectors):
    rows=[[(v>>j)&1 for j in range(73)] for v in vectors]
    pivot=0
    for column in range(73):
        found=next((i for i in range(pivot,len(rows)) if rows[i][column]),None)
        if found is None:continue
        rows[pivot],rows[found]=rows[found],rows[pivot]
        for i in range(pivot+1,len(rows)):
            if rows[i][column]:rows[i]=[a^b for a,b in zip(rows[i],rows[pivot])]
        pivot+=1
    return pivot


def check(receipt):
    authenticate()
    raw=(ROOT/'research/community-frontier1042-audit/selected-replay.tar.gz').read_bytes()
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        data=json.load(archive.extractfile('t16/global/base/work/complex-nine-native/DATA-PHASES.json'))
    packet=json.loads(gzip.decompress((ROOT/'research/joint-query/certificate.json.gz').read_bytes()))
    ports=packet['U_ports']+packet['T_ports']
    expected={row[0]:row for row in receipt['records']}
    found=[]
    for p in ports:
        recipe=data['recipes'][p]
        a=native_owner(recipe,1);b=native_owner(recipe,2)
        h=mul_rows(b,a);inv=mul_rows(a,b)
        q=recipe['q'];u=apply_rows(inv,q)
        need([p,q,u,apply_rows(h,1)]==expected[p][:4],'independent owner/direction certificate')
        vectors=[apply_rows(h,1<<j) for j in range(17)]
        observed=sampled_gram(vectors)
        target=tuple((1<<j) if 9<=j<25 else 0 for j in range(73))
        delta=tuple(x^y for x,y in zip(observed,target))
        qq=tuple(q if q>>j&1 else 0 for j in range(73))
        need(delta==qq,'independent full-coordinate phase polarization')
        r=[F(packet['R_rows'][j].get(str(p),0)) for j in range(8)]
        need(sum(x*x for x in r)==4,'independent nonzero branch matrix')
        found.append(u)
    need(len(found)==len(set(found))==104,'independent distinct pulled-back directions')
    partition=json.loads((Path(__file__).resolve().parent/'PARTITION.json').read_text())
    groups=partition['groups'];flat=[p for g in groups for p in g]
    need(len(flat)==len(set(flat))==104 and set(flat)==set(ports),'independent partition coverage')
    direction={p:expected[p][2] for p in ports}
    need(all(elementary_rank([direction[p] for p in g])==len(g) for g in groups),'independent partition ranks')
    need(elementary_rank(found)==9 and len(groups)==12,'independent optimal partition count')
    return {'ports':len(found),'phase_samples_per_port':73+73*72//2,'inherited_code_executed':False,'independent_groups':12,'direction_span_rank':9}


if __name__=='__main__':
    from pathlib import Path
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    result=check(json.loads((Path(__file__).resolve().parent/'CERTIFICATE.json').read_text()))
    print('PASS_INDEPENDENT_QQ16_FRAME_POLARIZATION '+json.dumps(result,sort_keys=True))
