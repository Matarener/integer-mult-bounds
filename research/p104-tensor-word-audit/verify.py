#!/usr/bin/env python3
"""Exact disjoint-fiber audit of frozen PR3979 word builders. Apache-2.0."""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PINS={'README.md':'7c57cda30963c1fc37a96b92182912b3942e4e2447ba599db9f7af2359414d9c',
      'PROOF.md':'259ba7b0926dd6db4e7c45ff7ccb10659dee06aef0a573547236c994ad304756',
      'verify.py':'27bae82fe247fe49b8fc3b5efbd429e2c8c0ee8f56cc4ace748cbb681a5abacc'}
FIXTURE='research/p104-native-channel/inputs/P104-FIXTURE.json'
FIXTURE_SHA='516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4'
B2_SHA='88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535'


def need(ok,message):
    if not ok:raise ValueError(message)


def unique(pairs):
    d={}
    for k,v in pairs:
        need(k not in d,'duplicate JSON key');d[k]=v
    return d


def load(path):return json.loads(path.read_text(),object_pairs_hook=unique)


def authenticate():
    for path,digest in [(HERE/'source'/n,s) for n,s in PINS.items()]+[(ROOT/FIXTURE,FIXTURE_SHA)]:
        need(not path.is_symlink(),'source symlink')
        need(hashlib.sha256(path.read_bytes()).hexdigest()==digest,'source bytes: '+str(path))


def get_words():
    authenticate()
    spec=importlib.util.spec_from_file_location('frozen_3979_word_builders',HERE/'source/verify.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # Relocate only its canonical fixture root. No source bytes are changed and
    # no predecessor evaluator, result(), invoice or claimed receipt is called.
    module.ROOT=ROOT
    b=module.source_matrix()
    return ({'enc':list(module.code_word(b)), 'dec':list(module.code_word(b,True)),
             'coded':list(module.coded_pair(b)), 'reference':list(module.reference_pair(b))},b)


def eye(n):return [{i:Q(1)} for i in range(n)]


def transpose(a):
    out=[{} for _ in a]
    for i,row in enumerate(a):
        for j,v in row.items():out[j][i]=v
    return out


def multiply(a,b):
    out=[]
    for row in a:
        d={}
        for k,v in row.items():
            for j,w in b[k].items():d[j]=d.get(j,Q(0))+v*w
        out.append({j:v for j,v in d.items() if v})
    return out


def interpret(word,size):
    rows=eye(size)
    for op in word:
        need(isinstance(op,(tuple,list)) and op,'operation tuple')
        kind=op[0]
        need(kind in ('add','half','double'),'operation alphabet')
        need(len(op)==(4 if kind=='add' else 2),'operation arity')
        need(type(op[1]) is int and 0<=op[1]<size,'destination domain')
        dst=op[1]
        if kind=='add':
            need(type(op[2]) is int and 0<=op[2]<size,'source domain')
            need(type(op[3]) is int and op[3] in (-1,1),'unit sign')
            source=rows[op[2]].copy()
            for j,value in source.items():
                new=rows[dst].get(j,Q(0))+op[3]*value
                if new:rows[dst][j]=new
                else:rows[dst].pop(j,None)
        else:
            factor=Q(1,2) if kind=='half' else Q(2)
            rows[dst]={j:factor*v for j,v in rows[dst].items()}
    return rows


def audit_sweep(word,n):return interpret(word,n)
def audit_fiber(word,n):return interpret(word,2*n)


def expected_pair(k,source):
    n=len(k);target=1-source;out=eye(2*n);sign=1 if source==0 else -1
    for i,row in enumerate(k):
        for j,v in row.items():out[target*n+i][source*n+j]=sign*v
    return out


def localize(word,n,axis,fixed,bank=None):
    """Certify every physical index belongs to this declared disjoint fiber."""
    def local(index):
        need(type(index) is int and 0<=index<2*n*n,'global data index; helpers excluded')
        owner,offset=divmod(index,n*n);i,j=divmod(offset,n)
        need((j if axis==0 else i)==fixed,'fiber ownership/axis')
        need(bank is None or owner==bank,'bank ownership')
        return (owner*n if bank is None else 0)+(i if axis==0 else j)
    result=[]
    for op in word:
        need(isinstance(op,(tuple,list)) and op,'operation tuple')
        kind=op[0];need(kind in ('add','half','double'),'operation alphabet')
        need(len(op)==(4 if kind=='add' else 2),'operation arity')
        dst=local(op[1])
        if kind=='add':
            need(type(op[3]) is int and op[3] in (-1,1),'unit sign')
            result.append((kind,dst,local(op[2]),op[3]))
        else:result.append((kind,dst))
    return tuple(result)


def certify(words=None,certificate=None):
    published,b=get_words()
    if words is None:words=published
    need(isinstance(words,dict) and set(words)==set(published),'four complete words')
    p=len(b);q=len(b[0]);n=p+q
    need((p,q,n)==(8,96,104) and all(len(row)==q for row in b),'actual P104 dimensions')
    need(all(type(v) is int and v in (-1,0,1) for row in b for v in row),'signed-half source B')
    need(hashlib.sha256(json.dumps(b,separators=(',',':')).encode('ascii')).hexdigest()==B2_SHA,
         'complete B2 agreement with independent geometry')
    nonzeros=sum(v!=0 for row in b for v in row)
    need(nonzeros==384,'actual B support')
    U=eye(n);Ui=eye(n)
    for i,row in enumerate(b):
        for j,value in enumerate(row,p):
            if value:U[i][j]=Q(value,2);Ui[i][j]=-Q(value,2)
    Ut=transpose(U);Uit=transpose(Ui);P=[{i:Q(1)} if i<p else {} for i in range(n)]
    need(multiply(U,Ui)==eye(n) and multiply(Ut,Uit)==eye(n),'local sweep inverse')
    M=multiply(U,Ut);A=multiply(multiply(Ut,P),U)
    kernels={(False,False):U,(False,True):Ui,(True,False):Ut,(True,True):Uit}
    steps=[(0,1,True,True),(0,0,False,False),(1,1,False,False),(1,0,True,True)]
    cache={};fiber_instances=0;literal_ops=0

    def group(word,position,axis,fixeds,bank,expected,length):
        nonlocal fiber_instances,literal_ops
        pattern=None
        for fixed in fixeds:
            stop=position+length;need(stop<=len(word),'truncated fiber')
            ops=localize(word[position:stop],n,axis,fixed,bank)
            if pattern is None:
                pattern=ops
                if pattern not in cache:cache[pattern]=interpret(pattern,n if bank is not None else 2*n)
                need(cache[pattern]==expected,'exact fiber linear map')
            else:need(ops==pattern,'nonuniform fiber program')
            position=stop;fiber_instances+=1;literal_ops+=len(ops)
        return position

    for name,inverse in [('enc',False),('dec',True)]:
        layout=steps if not inverse else [(bank,axis,t,not inv) for bank,axis,t,inv in reversed(steps)]
        position=0
        for bank,axis,t,inv in layout:
            length=nonzeros+2*(p if t else q)
            position=group(words[name],position,axis,range(n),bank,kernels[t,inv],length)
        need(position==len(words[name]),'unconsumed encoder/decoder events')
    for name,k in [('coded',M),('reference',A)]:
        position=0
        for source,axis in ([(0,1),(1,0)] if name=='coded' else [(0,0),(1,1)]):
            count=p if name=='coded' else n
            length=4*nonzeros+5*n if name=='coded' else 4*q+3*p+3*nonzeros
            position=group(words[name],position,axis,range(count),None,expected_pair(k,source),length)
        need(position==len(words[name]),'unconsumed pair events')

    def invoice(word):
        c=Counter(op[0] for op in word)
        return {k:c[k] for k in ('add','half','double')}
    enc,dec=invoice(words['enc']),invoice(words['dec'])
    invoices={'boundary':{k:enc[k]+dec[k] for k in enc},'coded_pair':invoice(words['coded']),
              'reference_pair':invoice(words['reference'])}
    cert=load(HERE/'CERTIFICATE.json') if certificate is None else certificate
    expected={'schema_version':1,'ports':104,'pivot_ports':8,'invoices':invoices}
    need(json.dumps(cert,sort_keys=True)==json.dumps(expected,sort_keys=True),'complete typed invoice certificate')
    need(fiber_instances==1056 and len(cache)==8,'complete actual fiber coverage')
    # Every event is consumed by an exact fiber map. Disjoint supports give the
    # global tensor factors in PROOF; independent.py proves their full identities.
    return {'ports':n,'data_degrees':2*n*n,'audited_literal_operations':literal_ops,
            'fiber_instances':fiber_instances,'distinct_exact_local_maps':len(cache),
            'invoices':invoices,'two_pair_add_saving':2*invoices['reference_pair']['add']-invoices['boundary']['add']-2*invoices['coded_pair']['add'],
            'two_pair_half_saving':2*invoices['reference_pair']['half']-invoices['boundary']['half']-2*invoices['coded_pair']['half'],
            'all_helpers_untouched_by_index':True,'word_builders_reused':True,
            'predecessor_evaluator_reused':False,'new_code_construction':False,'new_kappa':False}


def audit():return certify()


if __name__=='__main__':print('PASS_P104_TENSOR_WORD_AUDIT '+json.dumps(audit(),sort_keys=True))
