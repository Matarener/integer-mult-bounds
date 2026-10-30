#!/usr/bin/env python3
"""Finite full-address residual algebra; no physical payload execution.
Apache-2.0. Chris R / Clear1nsight with OpenAI Codex assistance.
"""
from pathlib import Path
import json,hashlib,sys,argparse
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import compiler

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def need(x,msg):
    if not x:raise ValueError(msg)
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def mul(a,b,n):
    out=[[0]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]=(out[i][j]+x*y)%n
    return out

def inv(a,n):
    rows=[r[:]+e for r,e in zip(a,eye(len(a)))];m=len(a)
    import math
    for k in range(m):
        pivot=next(i for i in range(k,m) if math.gcd(rows[i][k],n)==1)
        rows[k],rows[pivot]=rows[pivot],rows[k]
        c=pow(rows[k][k],-1,n);rows[k]=[x*c%n for x in rows[k]]
        for i in range(m):
            if i!=k:
                c=rows[i][k];rows[i]=[(x-c*y)%n for x,y in zip(rows[i],rows[k])]
    return [r[m:] for r in rows]
def rational(a,n):return [[x.numerator*pow(x.denominator,-1,n)%n for x in row] for row in a]
def rowadd(a,i,k,c,n):a[i]=[(x+c*y)%n for x,y in zip(a[i],a[k])]
def coladd(a,i,k,c,n):
    for row in a:row[i]=(row[i]+c*row[k])%n

def derive(projector,rank,mod):
    m=len(projector);a=[list(reversed(row)) for row in projector];left=eye(m);right=eye(m)
    rows=[];tails=[];pivots=[]
    for k in range(rank):
        col=m-1-k;pivot=a[k][col];iv=pow(pivot,-1,mod);pivots.append(pivot)
        for i in range(k+1,m):
            c=-a[i][col]*iv%mod;rows.append(c);rowadd(a,i,k,c,mod);rowadd(left,i,k,c,mod)
        for j in range(col):
            c=-a[k][j]*iv%mod;tails.append(c);coladd(a,j,col,c,mod);coladd(right,j,col,c,mod)
    need(all(a[i][j]==(pivots[i] if i<rank and j==m-1-i else 0) for i in range(m) for j in range(m)),'complete rank endpoint')
    li=inv(left,mod);ri=inv(right,mod)
    a0=mul(mul(left,projector,mod)[:rank],li,mod)
    b=mul(ri,[row[:rank] for row in reversed(li)],mod)
    cross=[[0]*m for _ in range(m)]
    for k,pivot in enumerate(pivots):
        iv=pow(pivot,-1,mod)
        for i in range(m):cross[i][k]=(b[i][k]-(iv if i==m-1-k else 0))%mod
        for j in range(rank,m):cross[m-1-k][j]=-iv*a0[k][j]%mod
    return rows,tails,cross,pivots

def residual(projector,weights,mod):
    m=len(projector);out=[[0]*(2*m) for _ in range(2*m)]
    for i in range(m):
        for j in range(m):
            p=projector[i][j];d=(int(i==j)-p)%mod
            out[i][j]=weights[i]*d*pow(weights[j],-1,mod)%mod
            out[i][2*m-1-j]=weights[i]*p%mod
            out[2*m-1-i][j]=p*pow(weights[j],-1,mod)%mod
            out[2*m-1-i][2*m-1-j]=d
    return out

def compose(commands,coefficients,pivots,weights,mod,right=False,omit=None):
    m=len(weights);a=eye(2*m)
    def shear(target,source,c):
        if right:coladd(a,source,target,c,mod)
        else:rowadd(a,target,source,c,mod)
    for i,(cmd,c) in enumerate(zip(commands,coefficients)):
        if i!=omit:shear(cmd.target,cmd.source,c)
    for k,pivot in enumerate(pivots):
        left,tail=k,2*m-1-k;v=weights[k]*pivot%mod;iv=pow(v,-1,mod)
        if right:
            for row in a:row[left],row[tail]=row[tail]*iv%mod,row[left]*v%mod
        else:a[left],a[tail]=[x*v%mod for x in a[tail]],[x*iv%mod for x in a[left]]
    for i in reversed(range(len(commands))):
        if i!=omit:shear(commands[i].target,commands[i].source,-coefficients[i])
    return a

def run():
    cat,top=compiler.load('D');record=compiler.early_source87(cat,top,0)
    from catalogue import Specifications
    prep=cat.template_for(record['identifier'],True).preparation
    low=inv(rational(prep,3),3)
    specs=Specifications(cat);handle=compiler.source_handle(cat,record['identifier'],True,tuple(map(tuple,low)))
    spec=compiler.resolve_handle(cat,specs,handle);plan=specs.plan(handle.code)
    need(plan.good and plan.rank==2 and len(plan.commands)==4346,'actual rank2 full good plan')
    reverse_record=compiler.early_source87(cat,top,1)
    need(cat.template_for(reverse_record['identifier'],True).preparation==prep,'both orientation source preparation matches')
    results=[]
    for mod in (3,9):
        high=[[((i*5+j*7+1)%3) if i<3 or j<3 else 0 for j in range(64)] for i in range(64)]
        raw=[[(low[i][j]+3*high[i][j])%mod for j in range(64)] for i in range(64)]
        header=mul(raw,rational(prep,mod),mod);hinv=inv(header,mod)
        projector=mul([row[:2] for row in header],hinv[:2],mod)
        need(mul(projector,projector,mod)==projector,'actual source projector')
        rows,tails,cross,pivots=derive(projector,2,mod)
        weights=[2]*64
        coefficients=[]
        for cmd in plan.commands:
            r=cmd.reference
            if r.kind=='head':c=rows[r.index]*weights[r.first]*pow(weights[r.second],-1,mod)
            elif r.kind=='tail':c=tails[r.index]
            else:
                need(r.kind=='cross','actual good reference');c=cross[r.first][r.second]*pow(weights[r.second],-1,mod)
            coefficients.append(c*r.sign%mod)
        expected=residual(projector,weights,mod)
        left=compose(plan.commands,coefficients,pivots,weights,mod)
        right=compose(plan.commands,coefficients,pivots,weights,mod,True)
        need(left==expected,'actual chronological forward-address composition gives full128 residual')
        need(mul(left,left,mod)==eye(128),'residual involution converts pushforward to Boolean pullback')
        controls=[]
        if mod==9:
            need(right!=expected,'nonzero-high fixture discriminates reversed composition')
            stale_rows,stale_tails,stale_cross,stale_pivots=derive(mul([row[:2] for row in mul(low,rational(prep,mod),mod)],inv(mul(low,rational(prep,mod),mod),mod)[:2],mod),2,mod)
            stale=[]
            for cmd in plan.commands:
                ref=cmd.reference
                if ref.kind=='head':v=stale_rows[ref.index]*weights[ref.first]*pow(weights[ref.second],-1,mod)
                elif ref.kind=='tail':v=stale_tails[ref.index]
                else:v=stale_cross[ref.first][ref.second]*pow(weights[ref.second],-1,mod)
                stale.append(v*ref.sign%mod)
            need(compose(plan.commands,stale,stale_pivots,weights,mod)!=expected,'stale high-field form rejected')
            bad=next((i for i,c in enumerate(coefficients) if c and compose(plan.commands,coefficients,pivots,weights,mod,omit=i)!=expected),None)
            need(bad is not None,'omitting a nonzero adapter and its inverse rejected')
            controls=[{'stale_high_form_rejected':True},{'nonzero_command_omission_rejected':bad}]
        # A same-output losing algebraic control inserts a cancelling nonzero
        # shear pair outside the residual: two extra mandatory passes.
        losing=[row[:] for row in left];rowadd(losing,127,0,2,mod);rowadd(losing,127,0,-2,mod)
        need(losing==expected,'same-output two-extra-shear control')
        results.append({'modulus':mod,'row_composition_matches':left==expected,'column_composition_matches':right==expected,'pivots':pivots,'nonzero_adapter_commands':sum(bool(c) for c in coefficients),'source_request':record['identifier'],'source_code_sha256':digest(str(handle.code)),'header_sha256':digest(header),'raw_high_sha256':digest(high),'raw_high_nonzero_entries':sum(bool(v) for row in high for v in row), 'projector_sha256':digest(projector),'coefficients_sha256':digest(coefficients),'expected_residual_sha256':digest(expected),'unit_weights':[2]*64,'adapter_commands_each_direction':len(plan.commands),'adapter_commands_total':2*len(plan.commands),'zero_adapter_commands_each_direction':sum(not c for c in coefficients),'central_weighted_pairs':[[k,127-k,weights[k]*pivots[k]%mod] for k in range(2)],'controls':controls,'same_output_losing_extra_shears':2})
    return {'status':'PASS_FULL_RESIDUAL_ADDRESS_ALGEBRA','source_identity':cat.source_identity,'source_records':[record,reverse_record],'cases':results,'primitive_passes_per_prefix':8708,'adapter_coefficient_invocations_per_prefix':17384,'child_coefficient_invocations_per_prefix':12,'scope':'Finite complete128-address operator certificate; independently calculated ring coefficients from fresh source preparation, q3 moduli3/9, uniform unit2 ancestors. All4346 adapter commands each direction count including zeros. No full physical payload execution, universal primitive refinement, or arbitrary-history coefficient-cost theorem.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();r=run();target=P/'RESIDUAL-ALGEBRA.json'
    if args.write:target.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(json.dumps(r))==json.loads(target.read_text()),'immutable residual receipt')
    print(r['status'])
