"""Exact all-width terminal decoder, with explicit Gaussian charges.
Apache-2.0. Dugongue with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from hashlib import sha256
from collections import defaultdict
import argparse, gzip, json
ROOT=Path(__file__).resolve().parent

def need(ok, message):
    if not ok: raise ValueError(message)

def source():
    pins=json.loads((ROOT/'source/PINS.json').read_text(encoding='utf8'))
    for name,digest in pins['files'].items():
        need(sha256((ROOT/'source'/name).read_bytes()).hexdigest()==digest,'Changed source: '+name)
    return json.loads(gzip.decompress((ROOT/'source/K-PROGRAM.json.gz').read_bytes()))

def mv(rows,x): return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))
def phase(z,k):
    a,b=z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[k%4]
def add(out,key,z):
    a,b=out.get(key,(0,0)); a+=z[0];b+=z[1]
    if a or b:out[key]=(a,b)
    else:out.pop(key,None)
def normalize(state,e):
    while e and state and all(not ((a|b)&1) for a,b in state.values()):
        state={k:(a//2,b//2) for k,(a,b) in state.items()};e-=1
    return state,e if state else 0

def monomial_column(word,x):
    theta=0
    for op in word:
        if op[0]=='P': x=mv(op[1],x)
        elif op[0]=='D':
            rows,alpha=op[1:]
            theta+=sum(alpha[i] for i in range(25) if x>>i&1)
            theta+=2*sum(((rows[i]>>(i+1))&(x>>(i+1))).bit_count() for i in range(25) if x>>i&1)
        elif op[0]=='X':x^=op[1]
        elif op[0]=='phase':theta+=op[1]
        else:raise ValueError('A Gaussian is hidden in a monomial word')
    return x,theta%4

def lifted(word,address,f,axes):
    """Stage axis j is the f-bit block axes[j]; scalars are never tensorized."""
    out=address;theta=0
    for col in range(f):
        x=sum(((address>>(a*f+col))&1)<<j for j,a in enumerate(axes))
        y,t=monomial_column(word,x);theta+=t
        for j,a in enumerate(axes):
            if (x^y)>>j&1:out^=1<<(a*f+col)
    return out,theta%4

def q_pass(state,e,f,sign=1):
    """Literal central C^{tensor f}; no external numerical/oracle dependency."""
    need(sign in (-1,1),'Gaussian orientation')
    need(type(f)is int and f>=1,'Positive address width')
    for col in range(f):
        out={}
        for (owner,x),(a,b) in state.items():
            add(out,(owner,x),(a-sign*b,b+sign*a))
            add(out,(owner,x^(1<<col)),(a+sign*b,b-sign*a))
        state,e=normalize(out,e+1)
    return state,e

class Cube:
    def __init__(self,data):
        self.ports=data['port_order']
        self.rows={int(r):{s:a*(16//b) for s,a,b in row} for r,row in data['literal_scalar_K_rows'].items()}
        self.columns={s:[] for s in self.ports}
        for r,row in self.rows.items():
            for s,a in row.items():self.columns[s].append((r,a))
        self.forward={p:data['definitions'][data['normalization_wrappers'][str(p)]['input_Y']] for p in self.ports}
        self.inverse={p:data['definitions'][data['normalization_wrappers'][str(p)]['output_X']] for p in self.ports}
    def code(self,state,e,f,axes):
        need(len(axes)==25 and axes[0]==0 and len(set(axes))==25,'Invalid fresh-stage embedding')
        aligned={}
        for (p,x),v in state.items():
            y,t=lifted(self.forward[p],x,f,axes);add(aligned,(p,y),phase(v,t))
        mixed={}
        for (s,x),(a,b) in aligned.items():
            for r,c in self.columns[s]:add(mixed,(r,x),(c*a,c*b))
        out={}
        for (p,x),v in mixed.items():
            y,t=lifted(self.inverse[p],x,f,axes);add(out,(p,y),phase(v,t))
        return normalize(out,e+4)

def stage_axes(stage):return (0,)+tuple(range(1+24*stage,25+24*stage))
def recipe(stages,owners=512,keep_central=True):
    need(type(stages)is int and stages>=0 and type(owners)is int and owners>0,'Invalid decoder dimensions')
    events=[{'op':'GAUSSIAN_Q','rank':1,'count':owners}]
    for s in reversed(range(stages)):
        events += [{'op':'CLEAR_OWNED','count':owners},
                   {'op':'NORMALIZE_L','stage':s,'count':owners},
                   {'op':'ACCUMULATE_K_INTO_OWNED','stage':s,'ADD':76*owners,'denominator_exponent':4},
                   {'op':'SWAP_WITH_OWNED','count':owners},
                   {'op':'NORMALIZE_L_INVERSE','stage':s,'count':owners},
                   {'op':'CLEAR_OWNED','count':owners}]
    if keep_central: events += [{'op':'GAUSSIAN_Q','rank':1,'count':owners}]
    return {'schema':'central-q-terminal-decoder/v1','chronological_events':events,
            'stage_order':list(reversed(range(stages))),
            'paid':{'1':(2 if keep_central else 1)*owners},'keep_central':keep_central,'owned_peak_fields_per_cube':owners if stages else 0,
            'ordinary':{'ADD':76*owners*stages,'normalizer_maps':2*owners*stages,
                        'SWAP':owners*stages,'CLEAR':2*owners*stages},
            'scope':'One coded negative terminal cohort. Gaussian charges are additional, not free. Exact arithmetic and tape/movement costs remain explicitly charged by the caller.'}

def literal_events(cube,stages,keep_central=True):
    """Fully expand owned routing and every actual source-bound scalar ADD.
    MONOMIAL references a source definition, with explicit stage-axis embedding.
    Each referenced definition is exactly two P/D primitives; it hides no Q.
    """
    for p in cube.ports:yield ['PAID_Q','MAIN',p,1]
    for stage in reversed(range(stages)):
        for p in cube.ports:yield ['CLEAR','OWNED',p]
        for p in cube.ports:yield ['MONOMIAL','MAIN',p,stage,'L']
        for r,row in cube.rows.items():
            for source,c in row.items():yield ['ADD','OWNED',r,'MAIN',source,c,16]
        for p in cube.ports:yield ['SWAP','MAIN',p,'OWNED',p]
        for p in cube.ports:yield ['MONOMIAL','MAIN',p,stage,'L_INVERSE']
        for p in cube.ports:yield ['CLEAR','OWNED',p]
    if keep_central:
        for p in cube.ports:yield ['PAID_Q','MAIN',p,1]


def run_recipe(cube,state,e,f,stages,keep_central=True):
    state,e=q_pass(state,e,f)
    for stage in reversed(range(stages)):state,e=cube.code(state,e,f,stage_axes(stage))
    return q_pass(state,e,f) if keep_central else (state,e)

def gauge_input(cube,state,e,f,stages):
    # W R^{-1}=Q^{-1} P Q^{-1}, with R=DQ and P=C_last ... C_first.
    state,e=q_pass(state,e,f,-1)
    for stage in range(stages):state,e=cube.code(state,e,f,stage_axes(stage))
    return q_pass(state,e,f,-1)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stages',type=int,default=19);ap.add_argument('--output',type=Path)
    a=ap.parse_args();data=recipe(a.stages)
    raw=json.dumps(data,indent=2)+'\n'
    if a.output:
        with a.output.open('x',encoding='utf8',newline='\n') as out:out.write(raw)
    else:print(raw,end='')
if __name__=='__main__':main()
