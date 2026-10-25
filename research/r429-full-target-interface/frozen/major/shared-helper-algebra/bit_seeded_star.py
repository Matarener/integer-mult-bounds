#!/usr/bin/env python3
"""Exact eight-input seeded fanout over F2[N]/(N^2-1).

This is the changed caller algebra; native factory/owner bindings are separate.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(b,m):
    if not b:raise ValueError(m)
def mul(a,b):
    a0,a1=a&1,a>>1;b0,b1=b&1,b>>1
    return ((a0*b0)^(a1*b1))|(((a0*b1)^(a1*b0))<<1)
def plus(a,b):return [x^y for x,y in zip(a,b)]
def scale(a,q):return[mul(x,q)for x in a]
def ident(n):return[[int(i==j)for j in range(n)]for i in range(n)]
def inverse_event(e):return e # Every declared GF2 primitive here is involutive.
def apply(z,e):
    z=[r[:]for r in z];i,j=e['source'],e['target'];k=e['kind']
    if k=='old_F':z[j]=plus(z[j],scale(z[i],2))
    elif k=='old_B':z[i]=plus(z[i],scale(z[j],2))
    elif k=='exchange':z[i],z[j]=z[j],z[i]
    elif k=='new_F':z[j]=plus(z[i],scale(z[j],2))
    elif k=='new_F_inverse':z[j]=scale(plus(z[j],z[i]),2)
    elif k=='CNOT':z[j]=plus(z[j],z[i])
    else:raise ValueError(k)
    return z

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    word=[{'kind':'old_F','source':0,'target':1,'stage':0},{'kind':'old_B','source':0,'target':1,'stage':1},{'kind':'old_F','source':0,'target':1,'stage':2},{'kind':'exchange','source':0,'target':1,'cut':'afterstage2'}]
    for j in range(2,8):word.append({'kind':'new_F','source':0,'target':j,'stage':j+1})
    # The source is unchanged by every fanout; terminal CNOTs cancel those
    # entering-source columns, once all eight fronts equal the common parent.
    for j in reversed(range(2,8)):word.append({'kind':'CNOT','source':0,'target':j,'cut':'terminal common NGamma'})
    z=ident(8);prefix=[]
    for e in word:
        z=apply(z,e);prefix.append(z)
    target=scale_identity=[[2*int(i==j)for j in range(8)]for i in range(8)]
    need(z==target,'all eight independent raw input columns reach common N')
    back=z
    for e in reversed(word):
        inv=dict(e)
        if inv['kind']=='new_F':inv['kind']='new_F_inverse'
        back=apply(back,inv)
    need(back==ident(8),'literal reverse-inverse all raw input columns')
    # Defect-sensitive negative controls alter actual words.
    bad=ident(8)
    for e in word:
        if e.get('stage')==1:continue
        bad=apply(bad,e)
    need(bad!=target,'omitted seed B rejected')
    bad=ident(8)
    for k,e in enumerate(word):
        if k==len(word)-1:continue
        bad=apply(bad,e)
    need(bad!=target,'omitted terminal CNOT rejected')
    # Pure new-F diagonalization cannot create source common-axis progress.
    single=apply(apply(ident(2),{'kind':'new_F','source':0,'target':1}),{'kind':'CNOT','source':0,'target':1})
    need(single==[[1,0],[0,2]],'source remains I under postCNOT diagonalization')
    windows=[{'bank':0,'active_stages':list(range(9)),'fresh_idle_query_ranks':[]},{'bank':1,'active_stages':[0,1,2],'fresh_idle_query_ranks':[42]}]
    for j in range(2,8):
        s=j+1;windows.append({'bank':j,'active_stages':[s],'fresh_idle_query_ranks':[x for x in(7*s,7*(8-s))if x]})
    out={'status':'PASS_SEEDED_STAR_EIGHT_RAW_INPUT_COLUMNS','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'coefficient_ring':'F2[N]/(N^2-1), entry encoded a+2*b for a+bN. Fresh Gs commute mutually and with N; cumulative Gamma is stripped only at matched fresh-prefix cuts.',
        'assumed_local_interfaces':['old_F_N=(x,y+Nx), old_B_N=(x+Ny,y), three clean rank7 stages, ordinary helper restoration as supplied by the old R438 factory.','new_F=(x,x+Ny), six stages, each from the changed R429 full-target factory. Its helpers and target preencoding must be admitted at the actual common-past prefix; this record does not establish that native binding.'],
        'word':word,'prefix_rows':prefix,'endpoint_rows':z,'inverse_endpoint_rows':back,
        'identity':'Three old F_N/B_N/F_N plus SWAP give diag(N,N). Six new F calls from bank0 to banks2..7 yield N(x0,x1,x2+x0,...,x7+x0). Six terminal CNOTs then yield N times I8.',
        'fresh_path':'Every active call advances its two banks by its stage G_s; complete every inactive fresh interval by the listed native idle query. All eight banks must reach Gamma9 before the terminal CNOTs.',
        'public_fresh_idle_windows':windows,
        'conditional_local_invoice':'3 old factories at private63 plus6 changed factories at private3; nominal raw rank deficit2*111-3*63-6*3=15 before padding, changed owner allocation, moments and precision. No unchanged nineteen-event owner witness applies.',
        'pure_newF_control':'PostCNOT * newF = diag(I,N). It leaves arbitrary raw source a unchanged, so it does not alone give common N on both raw inputs. An entrance normalization a=Nx must be paid or supplied by an explicit encoded-input caller contract.',
        'negative_controls':['Omit old seed B: wrong all-input endpoint.','Omit one terminal CNOT: one original x0 term remains.'],
        'all_size_scope':'The written word is a polynomial identity for every involution N over characteristic2 and every commuting fresh Gs. No finite Fourier expansion, one-bit support shortcut or clean data assumption is used.',
        'remaining':['Native source/target pre/post A admission at these changed cuts, all429 helper dirt and return identities require recursive lane producer binding.','New chronological whole-helper owner allocation and full moments, arity, rounding/precision and tape costs are not supplied.','No positive kappa follows from nominal D15.'],
        'attribution':'Recursive lane proposed three-old-call seed and six-new-call fanout; root proposed testing pure newF diagonalization. This lane independently verifies the changed word on all raw columns, inverse and defect controls, and separates the missing source input normalization.'}
    out=json.loads(json.dumps(out));target_path=HERE/'BIT-SEEDED-STAR.json'
    if a.write:target_path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(target_path.read_bytes())==out,'stored seeded star differs')
    print(out['status']);print('8 raw inputs; reverse-inverse;2 controls; changed idle windows PASS')
if __name__=='__main__':main()
