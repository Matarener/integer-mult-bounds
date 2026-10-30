#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound rational native audit, without predecessor code imports.

Ali Romman with substantial OpenAI Codex assistance. Retain the G20 native
and helper work of Dugongue, ai-nanachi and all source contributors.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from math import gcd,lcm
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research/g20-conjugation-admission'
sys.path.insert(0,str(HERE))
from algebra import (need,matrix,eye,transpose,product,difference,scale,inverse,
                     row_basis,diagonal,physical)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def authenticate():
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage']=='input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],
                 'source hash: '+row['path'])


class Geometry:
    def __init__(self,frames):
        self.frames=frames; self.projectors={}; self.edges={}; self.denominator=2

    def guard(self,*matrices):
        for a in matrices:
            for row in a:
                for value in row:
                    self.denominator=lcm(self.denominator,value.denominator)

    def projector(self,f):
        if f in self.projectors:
            return self.projectors[f]
        source=self.frames[str(f)];rank=source['dim']
        a,b=matrix(source['A']),matrix(source['B'])
        need(len(b)==rank and len(a)==8-rank and all(len(row)==8 for row in a+b),'frame dimensions')
        need(all(sum(x*y for x,y in zip(v,w))==0 for v in a for w in b),'orthogonal frame blocks')
        basis=transpose(b+a); inv=inverse(basis)
        need(product(basis,inv)==product(inv,basis)==eye(),'two-sided frame inverse')
        p=product(product(basis,diagonal(rank)),inv)
        need(p==transpose(p) and product(p,p)==p,'symmetric frame projector')
        self.guard(basis,inv,p); self.projectors[f]=p
        return p

    def edge(self,s,t,k):
        key=(s,t,k)
        if key in self.edges:
            return
        need(type(k) is int and 0<k<8,'proper residual rank')
        lo,hi=sorted((s,t),key=lambda f:self.frames[str(f)]['dim'])
        need(self.frames[str(hi)]['dim']-self.frames[str(lo)]['dim']==k,'residual dimension')
        p,q=self.projector(lo),self.projector(hi)
        need(product(p,q)==product(q,p)==p,'two-sided nesting')
        residual=difference(q,p)
        need(product(residual,residual)==residual and residual==transpose(residual),'residual projector')
        # A complete basis proves rank over every ring where its inverse exists.
        image=row_basis(residual); kernel=row_basis(difference(eye(),residual))
        need(len(image)==k and len(kernel)==8-k,'residual rank basis')
        basis=transpose(image+kernel); inv=inverse(basis)
        need(product(product(inv,residual),basis)==diagonal(k),'residual diagonal form')
        need(product(basis,inv)==product(inv,basis)==eye(),'residual basis inverse')
        left=product(difference(eye(),scale(self.projector(t),2)),
                     difference(eye(),scale(self.projector(s),2)))
        need(left==difference(eye(),scale(residual,2)),'ordered native difference-space identity')
        self.guard(basis,inv,residual); self.edges[key]=residual


def audit_word(word,geometry):
    n=len(word['start']); owned=set(word['owned']); state=word['start'][:]
    need(n==685 and len(owned)==48 and len(word['final'])==n,'source field contract')
    rows=[1<<i for i in range(n)]; norms=[1]*n; peak=1
    paid=Counter();ops=Counter()
    for f in state+word['final']:
        if f is not None:
            geometry.projector(f)
    for event,e in enumerate(word['records']):
        op,d=e[:2];need(type(d) is int and 0<=d<n,'actual owner');ops[op]+=1
        if op=='ADD':
            s,f=e[2:];need(type(s) is int and 0<=s<n and d!=s,'actual scalar source')
            need(f is not None and state[d]==state[s]==f,'actual common frame')
            rows[d]^=rows[s];norms[d]+=norms[s];peak=max(peak,norms[d])
        elif op in ('ERASE','INIT'):
            need(d in owned and (op=='ERASE' or rows[d]==0),'owned clear or whole zero initialization')
            if op=='ERASE':rows[d]=0;norms[d]=0
            state[d]=e[2]
            if e[2] is not None:geometry.projector(e[2])
        elif op in ('Q','ZERO_Q'):
            s,t,k=e[2:];need(state[d]==s,'actual query source frame');geometry.edge(s,t,k)
            if op=='ZERO_Q':need(rows[d]==0,'zero-header whole function')
            else:paid[k]+=1
            state[d]=t
        else:
            raise ValueError('unknown opcode')
    expected=[0 if i in owned else (1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
    need(state==word['final'],'every final frame')
    need(rows==expected,'all arbitrary public and dirty-owned input columns')
    return {'events':len(word['records']),'columns':n,'public':n-len(owned),'owned':len(owned),
            'paid':dict(sorted(paid.items())),'operations':dict(sorted(ops.items())),
            'positive_majorant':peak,'scalar_endpoint_sha256':sha256(json.dumps(rows).encode()).hexdigest()}


def matcher_check(source,geometry):
    total=0;details=[]
    for prefix,frame,count in [('',source['frame'],source['global_occurrences']),
                              ('new_target_',source['new_target_frame'],source['new_target_count'])]:
        forward=matrix(source[prefix+'forward']); back=matrix(source[prefix+'inverse'])
        need(product(forward,back)==product(back,forward)==eye(),'both matcher directions')
        p=geometry.projector(frame); transformed=product(product(back,p),forward)
        need(transformed in (diagonal(4),difference(eye(),diagonal(4))),'matcher separates both rank4 jobs')
        need(all(source['common_denominator']%x.denominator==0 for a in (forward,back) for row in a for x in row),'charged matcher denominators')
        coeff=sum(x!=0 for a in (forward,back) for row in a for x in row)
        charge=2*count*coeff; total+=charge;geometry.guard(forward,back)
        expected=source['new_target_coefficient_terms'] if prefix else count*source['paired_address_coefficient_terms_per_call']
        need(charge==expected,'both directions and address halves charged')
        details.append({'frame':frame,'count':count,'coefficients':coeff,'charged_terms':charge})
    need(total==10944,'complete matcher coefficient charge')
    return details


def probe_alias():
    p=(1,2,4,8,16,32,64,128,3,5,7,11,13,17,19,23)
    q=(1,3,9,27,2,6,18,54,5,15,45,34,7,21,63,88)
    v=(-192,289,-53,0,0,0,0,0); norm=sum(x*x for x in v)
    r=matrix([[Q(x*y,norm) for y in v] for x in v]);h=physical(r)
    need(product(h,h)==eye(16) and h!=eye(16),'nonidentity involution control')
    for point in (p,q):
        need(product(h,tuple((Q(x),) for x in point))==tuple((Q(x),) for x in point),'both probes alias')
    need(all(gcd(norm,m)==1 for m in (101,10201)),'published probe moduli valid')
    need(any(h[i][0]!=eye(16)[i][0] for i in range(16)),'unit input detects alias')
    return {'direction':list(v),'squared_norm':norm,'fixes_both_published_points':True,
            'nonidentity_involution':True,'first_unit_column_rejects':True}


def negative_controls(word,frames,matcher):
    failures=[]
    cases=[]
    e=next(i for i,v in enumerate(word['records']) if v[0]=='Q')
    bad=deepcopy(word);bad['records'][e][4]=8;cases.append(('rank8_direct_query',bad))
    bad=deepcopy(word);bad['records'][e][2]=bad['records'][e][3];cases.append(('stale_query_frame',bad))
    bad=deepcopy(word);bad['records'][e][0]='ZERO_Q';cases.append(('unpaid_nonzero_query',bad))
    bad=deepcopy(word);j=next(i for i,v in enumerate(bad['records']) if v[0]=='ADD');bad['records'][j][3]=-1;cases.append(('false_contact_frame',bad))
    bad=deepcopy(word);bad['records'].insert(0,['ERASE',0,word['start'][0]]);cases.append(('public_erasure',bad))
    bad=deepcopy(word);d=word['owned'][0];bad['records'].insert(0,['INIT',d,word['start'][d]]);cases.append(('dirty_initialization',bad))
    g=Geometry(frames)
    for name,case in cases:
        try:audit_word(case,g)
        except ValueError:failures.append(name)
        else:raise ValueError('mutant accepted: '+name)
    for name,change in [('missing_inverse',('new_target_inverse',0,0)),('false_forward',('new_target_forward',0,0))]:
        bad=deepcopy(matcher);key,i,j=change;bad[key][i][j]=str(Q(bad[key][i][j])+1)
        try:matcher_check(bad,g)
        except ValueError:failures.append(name)
        else:raise ValueError('mutant accepted: '+name)
    bad=deepcopy(matcher);bad['new_target_coefficient_terms']//=2
    try:matcher_check(bad,g)
    except ValueError:failures.append('one_address_half_unpaid')
    else:raise ValueError('half charge accepted')
    bad=deepcopy(frames);bad['508']['B'][0][0]+=1
    try:Geometry(bad).projector(508)
    except ValueError:failures.append('false_target_coframe')
    else:raise ValueError('false target coframe accepted')
    return failures


def run():
    authenticate();word=read(SOURCE/'WORD.json.gz')
    frames=read(SOURCE/'prior/prior/prior/source/vendor/g20/inputs/FRAMES.json')['frames']
    matcher=read(SOURCE/'MATCHER.json');source=read(SOURCE/'LOCAL-RESULT.json')['stats']
    g=Geometry(frames);stats=audit_word(word,g);normalizers=matcher_check(matcher,g)
    need(stats['paid']=={int(k):v for k,v in source['paid'].items()},'exact source paid bill')
    need(stats['operations']==source['operation_counts'] and stats['positive_majorant']==int(source['positive_majorant']),'exact source operations and growth')
    return {'source_head':'829d01fc031f7323ffcfa423fdfd1f24dcbe3190',
            'local':stats,'rational_frames':len(g.projectors),'directed_residuals':len(g.edges),
            'sufficient_modulus_guard':{'odd_and_coprime_to':g.denominator},
            'normalizers':normalizers,'probe_alias':probe_alias(),
            'negative_controls':negative_controls(word,frames,matcher)}


if __name__=='__main__':
    result=run()
    if '--emit' not in sys.argv:
        need(json.loads(json.dumps(result))==read(HERE/'RESULT.json'),'result receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
    if '--emit' not in sys.argv:print('PASS_G20_RATIONAL_ALL_ADDRESS_AUDIT')
