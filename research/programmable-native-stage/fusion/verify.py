"""Literal whole-K coded-thin fusion; only scalar ADD coefficients change.
Apache-2.0; substantial OpenAI Codex assistance. No new kappa is claimed.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json,sys
ROOT=Path(__file__).resolve().parent

def need(condition,message):
    if not condition:raise ValueError(message)

def inputs():
    pins=json.loads((ROOT/'SOURCES.json').read_text(encoding='utf-8'))['sources']
    out={}
    for record in pins:
        data=(ROOT/'inputs'/record['file']).read_bytes()
        need(hashlib.sha256(data).hexdigest()==record['sha256'],'Changed pinned source: '+record['file'])
        if record['file'].endswith('.gz'):
            data=gzip.decompress(data)
            need(hashlib.sha256(data).hexdigest()==record['payload_sha256'],'Changed scientific payload')
        if record['file'].endswith(('.json','.json.gz')):out[record['file']]=json.loads(data)
    return out

def fuse(word,extra):
    """Return the actual modified instruction stream for one added coded thin.
    `extra` is lambda; mu=1+lambda scales every existing cut ADD. No new
    oracle, monomial, paid path, memory field or chart change is introduced.
    """
    mu=1+F(extra);den=mu.denominator
    need(den&(den-1)==0,'The fixed caller coefficient must be dyadic')
    stream=[]
    for event in word['program']:
        if event[0]!='ADD':stream.append(event);continue
        if not mu:continue
        changed=list(event);coefficient=mu*F(event[5],event[6])
        changed[5],changed[6]=coefficient.numerator,coefficient.denominator
        stream.append(changed)
    return stream

def replay(word,stream,inverse=False):
    ports=word['port_order'];prefix='conjugate:'if inverse else''
    rows={(r,p):{(r,p):F(1)}for r in ['X','Y']for p in ports}
    charts={(r,p):prefix+('line:'+str(p)if r=='X'else'ground')for r,p in rows}
    paid,ordinary=Counter(),Counter()
    def monomial(key):
        literal=word['definitions'][key]
        need(all(op[0]in('P','D','X','phase')for op in literal),'Hidden Gaussian in ordinary map')
        ordinary.update(op[0]for op in literal)
    for index,event in enumerate(stream):
        kind=event[0]
        if kind in('MONOMIAL','BOUNDARY_MONOMIAL'):
            monomial(event[3])
        elif kind=='PAID_PATH':
            _,role,port,old,new,path=event
            need(charts[role,port]==old,'Paid path enters wrong actual chart')
            need(path['rank']==len(path['child_axes']),'Changed paid-child rank')
            charts[role,port]=new;paid[path['rank']]+=1
            monomial(path['before_monomial']);monomial(path['after_monomial'])
        else:
            need(kind=='ADD','Unknown literal event')
            _,dr,dp,sr,sp,a,b,chart=event
            need(charts[dr,dp]==charts[sr,sp]==chart,'ADD crosses different actual S9 charts')
            need((dr,dp)!=(sr,sp),'Overwriting a source during cut accumulation')
            for variable,value in rows[sr,sp].items():
                v=rows[dr,dp].get(variable,F(0))+F(a,b)*value
                if v:rows[dr,dp][variable]=v
                else:rows[dr,dp].pop(variable,None)
            ordinary['ADD']+=1
    return rows,charts,dict(sorted(paid.items())),dict(sorted(ordinary.items()))

def expected(word,mu,inverse=False):
    rows={(r,p):{(r,p):F(1)}for r in ['X','Y']for p in word['port_order']}
    for reader,row in word['literal_scalar_K_rows'].items():
        for source,a,b in row:
            target,variable=(('X',source),('Y',int(reader)))if inverse else(('Y',int(reader)),('X',source))
            value=F(a,b)*mu*(-1 if inverse else 1)
            if value:rows[target][variable]=value
    return rows

def involution(word):
    # K has denominator16. Check the exact integer matrix square, no float.
    matrix={int(r):{s:int(F(a,b)*16)for s,a,b in row}for r,row in word['literal_scalar_K_rows'].items()}
    checks=0
    for r,row in matrix.items():
        out={}
        for k,a in row.items():
            for s,b in matrix[k].items():out[s]=out.get(s,0)+a*b
        out={s:v for s,v in out.items()if v}
        need(out=={r:256},'Literal scalar K is not an involution');checks+=len(matrix)
    return checks

def check():
    source=inputs();forward=source['K-PROGRAM.json.gz'];backward=source['B-PROGRAM.json.gz']
    result={'status':'PASS_LITERAL_CODED_THIN_FUSION','new_kappa':False,
            'input_columns':2*len(forward['port_order']),'exact_K_square_entries':involution(forward),'cases':[]}
    for extra in [0,1,-1,-2,F(1,2)]:
        mu=1+extra
        for inverse,word,name in [(False,forward,'forward'),(True,backward,'backward')]:
            program=fuse(word,extra)
            rows,charts,paid,ordinary=replay(word,program,inverse)
            need(rows==expected(forward,mu,inverse),'Changed coefficient family endpoint')
            need(paid=={8:512,9:512,15:512,16:512},'A new paid child was introduced')
            need(ordinary.get('ADD',0)==(38912 if mu else 0),'Unpaid or missing ordinary ADD')
            need(all(charts['X',p]==('conjugate:'if inverse else'')+'full25'for p in word['port_order']),'Source final charts')
            need(all(charts['Y',p]==('conjugate:'if inverse else'')+'qperp24:'+str(p)for p in word['port_order']),'Reader final charts')
            result['cases'].append({'direction':name,'extra_coded_thin':str(extra),'total_transfer_multiplier':str(mu),
                                    'literal_events':len(program),'paid':paid,'ordinary':ordinary})
    controls=[]
    base=fuse(forward,1);index=next(i for i,e in enumerate(base)if e[0]=='ADD')
    bad=base.copy();bad[index]=list(bad[index]);bad[index][5]+=1
    rows,*_=replay(forward,bad)
    need(rows!=expected(forward,2),'Coefficient mutation accepted');controls.append('wrong_cut_coefficient')
    bad=base.copy();bad[index]=list(bad[index]);bad[index][7]='S9:wrong'
    try:replay(forward,bad)
    except ValueError as exc:need(str(exc)=='ADD crosses different actual S9 charts','Wrong frame rejection')
    else:raise ValueError('Wrong-chart mutation accepted')
    controls.append('wrong_physical_chart')
    need([e for e in base if e[0]!='ADD']==[e for e in forward['program']if e[0]!='ADD'],'A literal native/phase path changed')
    result['rejected_controls']=controls
    result['scope']='Exact all-column scalar/frame replay; all original monomial/paid/phase paths retained literally. Native physical correctness and all-width phase proof inherited from pinned upstream.'
    return json.loads(json.dumps(result))

if __name__=='__main__':
    report=check();path=ROOT/'RESULT.json'
    if '--emit'in sys.argv:path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    else:need(report==json.loads(path.read_text(encoding='utf-8')),'Frozen mathematical receipt differs')
    print(report['status'],'columns='+str(report['input_columns']),'cases='+str(len(report['cases'])))
