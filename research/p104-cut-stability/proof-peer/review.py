"""Independent selected-row precision checks; no author code imports.

This verifies named witnesses and reviews the scanner's matrix recurrence,
not an independent exhaustive all-cut maximum census. Apache-2.0.
Prepared for thu-nmrc with OpenAI Codex assistance.
"""
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha256
import gzip,json
HERE=Path(__file__).resolve().parent
SHA='48f8734ca9c5adf5d60ded3a5fefbc24894d2c358ed7cb30fcc0d71718599446'
def need(ok,label):
    if not ok:raise ValueError(label)
def add(v,k,q):
    z=v.get(k,F(0))+q
    if z:v[k]=z
    else:v.pop(k,None)
def pull(row,event):
    op,r=event[:2]
    if op=='MOVE':return
    if op in ('INIT','CLEAR'):
        row.pop(r,None)
    elif op=='SCALE':
        if r in row:
            row[r]*=F(event[2])
            if not row[r]:row.pop(r)
    else:
        need(op in ('ADD','COPY'),'Known source opcode')
        if r in row:add(row,event[2],row[r]*F(event[3]))
def pull_to(program,output,start,stop):
    row={output:F(1)}
    for e in reversed(program[stop:start]):pull(row,e)
    return row
def encoded(row):return {str(k):str(v) for k,v in sorted(row.items())}
def run():
    raw=(HERE/'WORD.json.gz').read_bytes();need(sha256(raw).hexdigest()==SHA,'Published WORD hash')
    w=json.loads(gzip.decompress(raw));p=w['program'];public=w['public'];n=public+8
    a=json.loads((HERE/'AUTHOR-RESULT.json').read_bytes())
    need(len(p)==25310 and n==743 and public==735,'Actual dimensions')
    pw=a['prefix_max_witness'];sw=a['suffix_max_witness']
    forward_row=pull_to(p,pw['role'],pw['cut'],0)
    # Exact initial owned zeros are part of this forward-prefix boundary.
    forward_row={k:v for k,v in forward_row.items() if k<public}
    need(encoded(forward_row)==pw['row'],'Independent prefix maximum-row witness')
    need(sum(map(abs,forward_row.values()))==F(131072),'Prefix witness l1')
    suffix_row=pull_to(p,sw['output'],len(p),sw['cut'])
    need(encoded(suffix_row)==sw['row'],'Independent suffix maximum-row witness')
    need(sum(map(abs,suffix_row.values()))==F(135415,4),'Suffix witness l1')
    residuals=[]
    for c in a['owned_residual_controls']:
        # Pull only the listed output to the instant just before COPY.
        row=pull_to(p,c['output'],len(p),c['event'])
        need(row.get(c['owned'],F(0))==F(c['residual_response'])!=0,'Actual injected COPY residual response')
        # Re-evaluate that exact cut with assignment-COPY as a mutant.
        mutant=pull_to(p,c['output'],len(p),c['event']+1)
        mutant.pop(c['owned'],None)
        need(mutant.get(c['owned'],F(0))==0,'Assignment COPY discards injected residual')
        residuals.append({'event':c['event'],'owned':c['owned'],'output':c['output'],'response':c['residual_response']})
    need(len(residuals)==8,'All eight actual COPY controls')
    dims=list(map(len,w['frames']));imax=max(dims[f] for f in w['initial']);fmax=max(dims[f] for f in w['final'])
    pp,ss=imax+max(dims),fmax+max(dims);wp=ws=None;rank_sum=0
    for t,e in enumerate(p):
        if e[0]!='MOVE':continue
        _,role,old,new,private=e;r=abs(dims[new]-dims[old]);rank_sum+=r
        x,y=imax+dims[old]+r,fmax+dims[new]+r
        if x>pp:pp=x;wp={'event':t,'role':role,'old_dimension':dims[old],'new_dimension':dims[new],'rank':r}
        if y>ss:ss=y;ws={'event':t,'role':role,'old_dimension':dims[old],'new_dimension':dims[new],'rank':r}
    need((imax,fmax,max(dims),pp,ss)==(5,9,9,20,27),'Actual native-prefix and suffix bounds')
    need(rank_sum==5894 and len(p)-3624+2==21688,'Literal rounded-layer count')
    service=len(p)+2;v=service*F(135415,4);guard=0
    while 2**guard<v:guard+=1
    need(guard==30,'Completed-service suffix guard bits')
    coef=[F(e[3] if e[0] in ('ADD','COPY') else e[2]) for e in p if e[0] in ('ADD','COPY','SCALE')]
    need(max(map(abs,coef))==F(65537,2) and max(c.denominator.bit_length()-1 for c in coef)==16,'Scalar coefficient / accumulator constants')
    return {
      'status':'PASS_INDEPENDENT_SELECTED_ROW_AND_COPY_WITNESSES',
      'word_sha256':SHA,'author_result_sha256':sha256((HERE/'AUTHOR-RESULT.json').read_bytes()).hexdigest(),
      'prefix_witness':{'cut':pw['cut'],'role':pw['role'],'row':encoded(forward_row),'l1':'131072'},
      'suffix_witness':{'cut':sw['cut'],'output':sw['output'],'terms':len(suffix_row),'l1':'135415/4','row':encoded(suffix_row)},
      'COPY_residual_controls':residuals,
      'geometry':{'endpoint_prefix_exponent':14,'endpoint_suffix_exponent':18,'native_interior_prefix_exponent':pp,'native_interior_suffix_exponent':ss,'prefix_extremal_move':wp,'suffix_extremal_move':ws},
      'completed_service_K':service,'completed_service_guard_bits':guard,'literal_K_expression':'21688 + 5894 f',
      'limits':['Only named maximum-row witnesses independently reproduced; exhaustive maximality relies on reviewed author scanner recurrence','Native chart correctness remains a source-bound premise','Completed-service bound assumes output-error ABI for each recursive Gaussian service','Literal butterfly precision witness has no recursive-invoice runtime claim','No full uniform compiler, physical stock/tape proof, new kappa, formal-kernel/human scientific acceptance'],
    }
if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
