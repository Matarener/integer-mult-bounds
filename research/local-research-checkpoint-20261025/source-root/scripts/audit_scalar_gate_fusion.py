#!/usr/bin/env python3
"""One source-bound common-frame fusion experiment; no new multiplier.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
Binary row reduction follows icekylinx's scripts/paired_cube/frames.py.
"""
import argparse
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path

import prepare_kappa_sixteenth as prep

D=prep.domain
PREFIX=D.PACKAGE+'selected/complex/'
PINS={PREFIX+name:digest for name,digest in {
    'word.json.gz':'0c4b720c57717c7e55e88f86a9e17ed75b3891f9d2e7ed29df0a188f8dfee67a',
    'frames.json.gz':'b516b59e7bd7e68c56c02e0041e7455b2eff445e81ac5fb69570d424cf0178a1',
    'graph.json.gz':'9f73a6a7f1a4410e954246c6ff95d9cad0582d0057f707a693cc2fd170995ead',
    'physical-frames.json.gz':'0e92261dbedacb1174ee58712f0a86dab00a4f2411e377faab7c08f54f8307f0',
    'physical-pairs.json.gz':'869b852cbfd63ef691336ea398280ef57896dd876f6a6c78edac88a2a304fffb',
    'sinks.json':'498f7ccc51db7d09d9dc191f0b0d44fd70f3f8bf374cf3f52548880bd42f04ec',
}.items()}
PINS['notes/general-clifford-frames.tex']='c9bb9655b594583c6b4bab8cb485233f1d1e588f83858cf1e4c3530cee8fed54'


def basis(rows):
    b={}
    for x in rows:
        for p,y in sorted(b.items(),reverse=True):
            if x>>p&1:x^=y
        if x:
            p=x.bit_length()-1
            for k,y in list(b.items()):
                if y>>p&1:b[k]=y^x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))


def perp(rows,h):
    piv={r.bit_length()-1:r for r in basis(rows)}
    out=[]
    for j in range(h):
        if j in piv:continue
        x=1<<j
        for p,r in piv.items():
            if r>>j&1:x|=1<<p
        out.append(x)
    return basis(out)


def select_region():
    data={}
    for name,digest in PINS.items():
        raw=D.pinned_bytes(D.ROOT/name,digest)
        if name.startswith(PREFIX):
            data[name[len(PREFIX):]]=json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    w,fw,g=[data[n+'.json.gz'] for n in ('word','frames','graph')]
    i,j=16579,16580
    D.require(w['ops'][i]==[6795,6766,8293] and w['ops'][j]==[6766,6983,8171], 'Region gates changed')
    D.require(w['opcoeff'][i]==w['opcoeff'][j]==[1,1], 'Region signs changed')
    phase=set(w['phase1'])
    rest=[k for k in range(len(w['ops'])) if k not in phase]
    position=rest.index(i)
    D.require(rest[position+1]==j, 'Not consecutive in physical forward schedule')
    roles={6795,6766,6983}
    pairs=data['physical-pairs.json.gz']
    D.require(not roles.intersection(s for a,b,t in pairs for s in (a,b)), 'Region crosses an alias')
    D.require(not roles.intersection(s['role'] for s in data['sinks.json']['sinks']), 'Region includes deleted sink')
    D.require(not any(t==j for a,b,t in pairs), 'Intervening compensation deadline')
    changed=dict(data['physical-frames.json.gz'])
    frames=[basis(changed[k]) if k in changed else perp(fw['annihilators'][w['ops'][k][2]],g['h']) for k in (i,j)]
    U,V=frames
    D.require(len(basis(U+V))==len(V) and len(U)<len(V), 'Frames not strictly nested')
    D.require((g['h'],len(U),len(V))==(22,5,8), 'Unexpected frame dimensions')
    return dict(operation_ids=[i,j],region_kind='Two consecutive retained auxiliary gates in the forward rest phase',
        roles=dict(y=6795,x=6766,z=6983),gates=['y += x at U','x += z at V'],
        local_dimension=g['h'],ambient_dimension=3*g['h'],
        U=list(U),V=list(V),U_dimension=len(U),V_dimension=len(V),transition_rank=len(V)-len(U),
        input_frames=['U','U','V'],output_frames=['U','V','V'],
        untouched_alias_and_sink_boundaries=True,intervening_compensation_deadline=False,
        boundary_scope='Incoming and outgoing edge endpoints fixed; outside movements and future restoration retained')


# Entries are Laurent polynomials in the actual invertible operator R.
# No relation such as R^2=I is assumed; exact Clifford phases are retained.
def add(a,b):
    out=dict(a)
    for k,v in b.items():out[k]=out.get(k,Q(0))+v
    return {k:v for k,v in out.items() if v}


def mul(a,b):
    out={}
    for i,x in a.items():
        for j,y in b.items():out[i+j]=out.get(i+j,Q(0))+x*y
    return {k:v for k,v in out.items() if v}


def identity(n=3):return [[{0:Q(1)} if i==j else {} for j in range(n)] for i in range(n)]


def matmul(a,b):
    n=len(a)
    D.require(len(b)==n and all(len(row)==n for row in a+b),'Matrix shape mismatch')
    out=[[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):out[i][j]=add(out[i][j],mul(a[i][k],b[k][j]))
    return out


def operation(spec,n=3):
    out=identity(n)
    if spec[0]=='shear':
        _,dst,src,c=spec
        D.require(dst!=src,'Shear must have distinct operands')
        out[dst][src]={0:Q(c)}
    elif spec[0] in ('copy','clear'):
        out[spec[1]]=[{} for _ in range(n)]
        if spec[0]=='copy':out[spec[1]][spec[2]]={0:Q(1)}
    else:
        D.require(spec[0]=='frames','Unknown operation')
        for i,power in enumerate(spec[1]):out[i][i]={power:Q(1)}
    return out


def compose(sequence,n=3):
    result=identity(n)
    for spec in sequence:result=matmul(operation(spec,n),result)
    return result


def inverse(sequence):
    D.require(all(s[0] in ('shear','frames') for s in sequence),'Copy/clear is not an independent reversible role')
    return [('shear',s[1],s[2],-s[3]) if s[0]=='shear' else ('frames',tuple(-p for p in s[1]))
            for s in reversed(sequence)]


def operator_controls():
    gates=[('shear',0,1,1),('shear',1,2,1)]
    baseline=[gates[0],('frames',(0,1,0)),gates[1]]
    at_V=[('frames',(1,1,0)),*gates,('frames',(-1,0,0))]
    at_U=[('frames',(0,0,-1)),*gates,('frames',(0,1,1))]
    expected=[[{0:Q(1)},{0:Q(1)},{}],[{},{1:Q(1)},{0:Q(1)}],[{},{},{0:Q(1)}]]
    for name,seq in [('baseline',baseline),('at_U',at_U),('at_V',at_V)]:
        D.require(compose(seq)==expected,'Wrong full operator: '+name)
        D.require(compose(seq+inverse(seq))==identity(),'Reverse does not restore arbitrary inputs: '+name)
        D.require(compose(inverse(seq)+seq)==identity(),'Left inverse failed: '+name)
    wrong=dict(omit_restore=at_V[:-1],pretend_involution=at_V[:-1]+[('frames',(1,0,0))],
               omit_other_input_alignment=[('frames',(0,1,0)),*gates,('frames',(-1,0,0))],
               commute_without_alignment=[('frames',(0,1,0)),*gates])
    for tag,seq in wrong.items():D.require(compose(seq)!=expected,'Adverse control accepted: '+tag)
    copied=[('copy',3,2),('frames',(0,0,0,-1)),gates[0],('shear',1,3,1),
            ('frames',(0,1,0,0)),('clear',3)]
    copy_map=compose(copied,4)
    D.require([row[:3] for row in copy_map[:3]]==expected and
              all(not row[3] for row in copy_map) and all(not x for x in copy_map[3]),
              'Retained-control copy schedule fails endpoint or scratch clearing')
    return dict(exact_endpoint=['y_out = y + x','x_out = R*x + z','z_out = z'],
        full_operator=[ [{str(k):str(v) for k,v in entry.items()} for entry in row] for row in expected],
        R='T_V T_U^(-1), actual exact relative Clifford; no involution assumption',
        both_common_frame_schedules_equal_baseline=True,
        every_input_and_inverse_checked_symbolically=True,
        rejected_controls=list(wrong),borrowed_workspace_roles=0,
        copied_control_schedule_checked=True,
        temporary_copy='One dependent stream, cleared by a scan; no new independent role or extra normalization volume')


def scalar_checks():
    """Independent numerical action of the complex C on exact real/imag parts."""
    C=[[Q(1,2),Q(1,2),Q(-1,2),Q(1,2)],
       [Q(1,2),Q(1,2),Q(1,2),Q(-1,2)],
       [Q(1,2),Q(-1,2),Q(1,2),Q(1,2)],
       [Q(-1,2),Q(1,2),Q(1,2),Q(1,2)]]
    CI=list(map(list,zip(*C)))
    def apply(M,x):return [sum(a*b for a,b in zip(row,x)) for row in M]
    def plus(x,y):return [a+b for a,b in zip(x,y)]
    def run(M,x):return apply(M,x)
    for column in range(12):
        xs=[[Q(int(4*i+j==column)) for j in range(4)] for i in range(3)]
        y,x,z=xs
        expected=[plus(y,x),plus(run(C,x),z),z]
        yy,xx,zz=run(C,y),run(C,x),z
        yy=plus(yy,xx);xx=plus(xx,zz);yy=run(CI,yy)
        D.require([yy,xx,zz]==expected,'Exact complex column differs')
        temp=run(CI,z)
        D.require([plus(y,x),run(C,plus(x,temp)),z]==expected,'Copied complex column differs')
        D.require(run(CI,run(C,x))==x,'Exact inverse control failed')
    e=[Q(1),Q(0),Q(0),Q(0)]
    D.require(run(C,run(C,e))!=e,'Toy incorrectly involutory')
    return dict(exact_rational_realification_columns=12,complex_C_not_an_involution=True,
                scope='Small operator check, not a construction of the ambient-66 circuit')


def audit():
    region=select_region();ops=operator_controls();small=scalar_checks()
    m,d=region['ambient_dimension'],region['transition_rank']
    sigma=Q(37,40)
    L,U=prep.enclosure_tools()['log_interval'](Q(2))
    low,high=prep.extended_exp(sigma*L,sigma*U)
    D.require(low**40 <= Q(2)**37 <= high**40 and low>1,'Pooling comparison failed')
    return dict(status='REJECTED specified common-frame fusion; no stronger supplier',
        source_sha256=PINS,region=region,operator=ops,small_complex_check=small,
        paid_comparison=dict(baseline_positive_children=[d],best_common_frame_positive_children=[d,d],
            inplace_common_frame_positive_children=[d,d,d],
            comparison='Aligned-register model with untouched z bypass: 3*A^sigma+2*B^sigma >= 2*d^sigma',
            assumptions='Both updated streams align to K and return; unchanged z may be copied. A=distance(L_U,L_K), B=distance(L_V,L_K), A+B>=d; 0<sigma<=1; fixed boundary frames and role volumes. General coded boundary adapters are not covered.',
            best_common_frame_to_baseline_ratio='2',baseline_rank=d,minimum_fused_rank=2*d,
            even_unproved_cross_role_pooling_child=2*d,
            pooling_to_baseline_ratio_lower=str(low),pooling_to_baseline_ratio_upper=str(high),
            tested_saving=str(1-sigma),
            scalar_gates_and_restoration='Both scalar gates and all boundary returns retained; original future cleanup unchanged'),
        conclusion='Stop this common-frame region. Different distributed or typed recursive operations remain untested.',
        published_control=D.published_control())


def main():
    p=argparse.ArgumentParser(description=__doc__);group=p.add_mutually_exclusive_group()
    group.add_argument('--write',type=Path);group.add_argument('--check',type=Path)
    args=p.parse_args();result=audit()
    if args.check:
        D.require(json.loads(args.check.read_text())==result,'Fusion receipt differs')
        print('PASS exact scoped fusion rejection; published witness unchanged')
    elif args.write:args.write.write_text(json.dumps(result,indent=2)+'\n')
    else:print(json.dumps(result,indent=2))


if __name__=='__main__':main()
