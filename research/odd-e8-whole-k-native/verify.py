"""Read-only emitted-word verifier and executed negative controls.

This does not call core.calculate or regenerate any scientific input. Scalar
K is recomputed in integer-sixteenths from the pinned root Gram matrices;
the emitted word is interpreted on all independent u,v columns. The u,v
coordinates are the invertible input coordinates documented in PROOF.md.
Only --write explicitly authors VERIFY-RESULT.json.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
from itertools import product
import argparse, gzip, importlib.util, json, sys
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True

def need(ok,why):
    if not ok:raise ValueError(why)
def dot(a,b):return (a&b).bit_count()&1
def sparse(word,n):
    # Fresh Gaussian-integer evaluator; no author phase compiler is imported.
    values={0:(1,0)};den=0
    for e in word:
        k=e[0]
        if k=='P':values={sum(dot(r,x)<<i for i,r in enumerate(e[1])):a for x,a in values.items()}
        elif k=='X':values={x^e[1]:a for x,a in values.items()}
        elif k in ('D','phase'):
            out={}
            for x,(a,b) in values.items():
                if k=='phase':theta=e[1]
                else:
                    Q,alpha=e[1:]
                    theta=sum(alpha[i] for i in range(n) if x>>i&1)
                    theta+=2*sum(dot(Q[i]>>(i+1),x>>(i+1)) for i in range(n) if x>>i&1)
                out[x]=[(a,b),(-b,a),(-a,-b),(b,-a)][theta%4]
            values=out
        elif k=='C':
            q,sign=e[1:];out={}
            for x in values.keys()|{x^q for x in values}:
                a,b=values.get(x,(0,0));c,d=values.get(x^q,(0,0))
                v=(a-sign*b+c+sign*d,b+sign*a+d-sign*c)
                if v!=(0,0):out[x]=v
            values=out;den+=1
        else:raise ValueError('unknown sparse gate')
        need(len(values)<=65536,'bounded fresh sparse evaluator')
        while den and all(not(a&1) and not(b&1) for a,b in values.values()):
            den-=1;values={x:(a//2,b//2) for x,(a,b) in values.items()}
    return values,den

def calculate(root):
    payload=json.loads(gzip.decompress((root/'K-PROGRAM.json.gz').read_bytes()))
    receipt=json.loads((root/'K-MODULE.json').read_bytes())
    canonical=(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode()
    digest=sha256(canonical).hexdigest()
    need(digest==receipt['scientific_program_payload_sha256'],'scientific payload pin')
    for name,pin in payload['source_pins'].items():need(sha256((root/'inputs'/name).read_bytes()).hexdigest()==pin,'source pin '+name)
    n=payload['axis_dimension'];ports=payload['port_order'];definitions=payload['definitions']
    need(n==25 and len(ports)==len(set(ports))==512,'root25 cube512')
    need(payload['field_roles']=={str(p):[['X',p],['Y',p]]for p in ports},'independent role namespace')
    for key,word in definitions.items():need(sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()==key,'literal definition content hash')
    normal=json.loads((root/'inputs/NORMALIZERS.json').read_bytes());roots=list(zip(*normal['mode_columns']))
    cube_partition={}
    for p,r in enumerate(roots):cube_partition.setdefault(tuple(i for i,v in enumerate(r)if v),[]).append(p)
    cubes=[ps for support,ps in sorted(cube_partition.items())]
    selected=[cubes[j]for j in payload['cube_tuple']]
    triples=list(product(range(8),repeat=3))
    def port(t):return sum(selected[a][t[a]]*112**(2-a)for a in range(3))
    need(ports==list(map(port,triples)),'literal cube port enumeration')
    W=[]
    for ps in selected:
        A=[]
        for i in range(8):
            row=[]
            for j in range(8):
                gram=sum(a*b for a,b in zip(roots[ps[i]],roots[ps[j]]))
                need(gram%2==0,'even root Gram')
                row.append(2*int(i==j)-gram//2)
            A.append(row)
        W.append(A)
    expectedK={}
    for t in triples:
        row={}
        for u in triples:
            # W_a=2K_a; this evaluates every zero as well as every nonzero.
            c=4*sum(W[a][t[a]][u[a]]*all(t[b]==u[b]for b in range(3)if b!=a)for a in range(3))
            c-=W[0][t[0]][u[0]]*W[1][t[1]][u[1]]*W[2][t[2]][u[2]]
            if c:row[port(u)]=F(c,16)
        need(len(row)==76 and Counter(map(abs,row.values()))=={F(1,4):12,F(1,16):64},'independent scalar row76')
        expectedK[port(t)]=row
    literalK={int(r):{s:F(a,b)for s,a,b in row}for r,row in payload['literal_scalar_K_rows'].items()}
    need(literalK==expectedK,'all262144 integer16 scalar entries')
    spec=importlib.util.spec_from_file_location('wholeK_verify_primitive',root/'inputs/clifford_exact.py')
    ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    def literal(word):
        value=ce.ident(n)
        for e in word:
            k=e[0]
            if k=='P':part=ce.perm(n,e[1])
            elif k=='D':part=ce.diag(n,e[1],e[2])
            elif k=='X':part=ce.xgate(n,e[1])
            elif k=='phase':part=ce.Op(n,ce.identity(n),[tuple(e)])
            else:need(k=='C','known primitive');part=ce.cgate(n,e[1],e[2])
            value=value.then(part)
        return value
    opcache={}
    def op(key):
        if key not in opcache:opcache[key]=literal(definitions[key])
        return opcache[key]
    chartops={'ground':ce.ident(n),'full25':ce.fourier(n)}
    for p in ports:
        chartops['line:'+str(p)]=op(payload['entry_frames'][str(p)]['own_line_frame'])
        chartops['qperp24:'+str(p)]=op(payload['exit_frames'][str(p)]['frame_word'])
    for k,rec in payload['common_paths'].items():chartops['S9:'+k]=op(rec['frame_word'])
    def monomial(key):
        word=definitions[key];need(all(e[0]in('P','D','X','phase')for e in word),'ordinary wrappers contain no Gaussian');return word
    rankchecks=set()
    for e in payload['program']:
        if e[0]!='PAID_PATH':continue
        _,role,p,old,new,path=e
        key=json.dumps([old,new,path],sort_keys=True,separators=(',',':'))
        if key in rankchecks:continue
        pre,post=[path[k]for k in ['before_monomial','after_monomial']]
        monomial(pre);monomial(post)
        actual=op(pre).then(ce.fourier(n,path['child_axes'])).then(op(post))
        target=chartops[old].adjoint().then(chartops[new])
        need(actual.tab==target.tab,'actual paid path signed tableau')
        need(ce.rank([x for x,z,p in actual.tab[n:]])==path['rank']==len(path['child_axes']),'actual paid Gaussian rank')
        rankchecks.add(key)
    expected={('X',p):{('X',p):F(1)}for p in ports}
    expected.update({('Y',p):{('Y',p):F(1),**{('X',s):c for s,c in expectedK[p].items()}}for p in ports})
    expected_endpoint={'source_identity_fields':ports,'reader_rows':{str(p):[[role,s,c.numerator,c.denominator]for (role,s),c in sorted(expected['Y',p].items())]for p in ports}}
    need(payload['logical_endpoint_rows']==expected_endpoint,'recorded endpoint all1024 independent coordinates')
    first_add=next(i for i,e in enumerate(payload['program'])if e[0]=='ADD')
    growth={role:{'peak_l1':F(1),'max_dyadic_denominator_exponent':0}for role in ['X','Y']}
    def replay(mutation=None,measure=False):
        rows={(role,p):{(role,p):F(1)}for role in ['X','Y']for p in ports}
        charts={(role,p):'await_input_'+role for role,p in rows};paid=Counter();ordinary=Counter()
        for i,original in enumerate(payload['program']):
            e=list(original)
            if i==first_add and mutation:
                _,dr,dp,sr,sp,a,b,ch=e
                if mutation=='coefficient':c=F(a,b)+F(1,16);e[5:7]=[c.numerator,c.denominator]
                elif mutation=='source_overwrite':e[1:5]=[sr,sp,dr,dp]
                elif mutation=='wrong_source_chart':e[4]=next(p for p in ports if charts['X',p]!=ch)
            kind=e[0]
            if kind=='MONOMIAL':
                _,role,p,key,name=e;wrappers=payload['normalization_wrappers'][str(p)]
                names={'normalized_virtual_Q_entry':('X','input_X','await_input_X','line:'+str(p)),
                       'real_reader_entry':('Y','input_Y','await_input_Y','ground'),
                       'autonomous_source_D_exit':('X','output_X','full25','normalized_D'),
                       'reader_D_normalization':('Y','output_Y','qperp24:'+str(p),'normalized_D')}
                er,slot,old,new=names[name]
                need(role==er and key==wrappers[slot] and charts[role,p]==old,'literal normalized ordinary wrapper chronology')
                ordinary.update(g[0]for g in monomial(key));charts[role,p]=new
            elif kind=='PAID_PATH':
                _,role,p,old,new,path=e;need(charts[role,p]==old,'paid entrance chronology')
                if old.startswith('line:'):ref=payload['source_paths'][str(p)]
                elif old=='ground':ref=payload['common_paths'][new.split(':')[1]]['reader_entry']
                elif new=='full25':ref=payload['common_paths'][old.split(':')[1]]['source_exit']
                else:ref=payload['reader_paths'][str(p)]
                need(path==ref,'actual path reference');paid[path['rank']]+=1
                for k in ['before_monomial','after_monomial']:ordinary.update(g[0]for g in monomial(path[k]))
                charts[role,p]=new
            else:
                need(kind=='ADD','no hidden allocation/copy/clear')
                _,dr,dp,sr,sp,a,b,ch=e
                need(charts[dr,dp]==charts[sr,sp]==ch,'actual ADD source and destination physical charts differ')
                for source,c in list(rows[sr,sp].items()):
                    value=rows[dr,dp].get(source,F(0))+F(a,b)*c
                    if value:rows[dr,dp][source]=value
                    else:rows[dr,dp].pop(source,None)
                ordinary['ADD']+=1
                if measure:
                    g=growth[dr];g['peak_l1']=max(g['peak_l1'],sum(map(abs,rows[dr,dp].values()),F(0)))
                    for c in rows[dr,dp].values():
                        d=c.denominator;need(not d&(d-1),'dyadic coefficient')
                        g['max_dyadic_denominator_exponent']=max(g['max_dyadic_denominator_exponent'],d.bit_length()-1)
        need(all(ch=='normalized_D'for ch in charts.values()),'all actual normalization exits')
        return rows,paid,ordinary
    rows,paid,ordinary=replay(measure=True)
    need(rows==expected,'all1024 emitted scalar endpoint columns')
    need({str(k):v for k,v in paid.items()}==receipt['paid_profile'],'all actual paid applications')
    need(dict(ordinary)==receipt['ordinary_literal_profile'],'all actual ordinary instructions')
    badcoeff,_,_=replay('coefficient');badsource,_,_=replay('source_overwrite')
    need(badcoeff!=expected,'actual ADD coefficient mutant rejected')
    need(any(badsource['X',p]!=expected['X',p]for p in ports),'actual source-overwrite mutant damages autonomous source')
    wrong_rejected=False
    try:replay('wrong_source_chart')
    except ValueError as exc:wrong_rejected=str(exc)=='actual ADD source and destination physical charts differ'
    need(wrong_rejected,'actual wrong-source-chart mutant rejected')
    first_path=next(e[5]for e in payload['program']if e[0]=='PAID_PATH')
    firstword=definitions[first_path['before_monomial']]+[('C',1<<j,1)for j in first_path['child_axes']]+definitions[first_path['after_monomial']]
    phasebad=firstword+[('phase',1)]
    need(literal(firstword).tab==literal(phasebad).tab and sparse(firstword,n)!=sparse(phasebad,n),'actual phase-i word mutant rejected beyond tableau')
    transport=chartops['S9:0'].adjoint().then(chartops['S9:1'])
    wrong_rank=ce.rank([x for x,z,p in transport.tab[n:]])
    need(wrong_rank==2,'two common S9 charts need real rank2 transport')
    return {'schema':'odd-E8-whole-K-emitted-verification/v1','status':'PASS',
            'scientific_program_payload_sha256':digest,'scalar_entries_independently_checked':512**2,
            'independent_scalar_columns':1024,'distinct_paid_tableau_rank_checks':len(rankchecks),
            'paid_path_applications':sum(paid.values()),'paid_profile':dict(sorted(paid.items())),
            'ordinary_literal_profile':dict(sorted(ordinary.items())),
            'growth':{k:{**v,'peak_l1':str(v['peak_l1'])}for k,v in growth.items()},
            'executed_mutations':{'actual_ADD_coefficient_changed':True,'actual_source_overwrite':True,
                                  'actual_wrong_source_chart':True,'same_tableau_actual_phase_i':True},
            'wrong_parity_chart_transport_rank':wrong_rank,'new_kappa':False,
            'scope':'Emitted root cube, integer scalar K, exact paid tableaux/ranks, literal chronology and counts. Generic all-width and all-cube phase proofs remain PROOF.md; this is not a complete caller or frontier admission.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=HERE);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    root=args.package.resolve();result=calculate(root);target=root/'VERIFY-RESULT.json'
    if args.write:target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(target.read_bytes())==json.loads(json.dumps(result)),'frozen VERIFY-RESULT semantic replay')
    print('PASS whole-K emitted verification; scalar262144, columns1024, executed mutants4; '+result['scientific_program_payload_sha256'])
if __name__=='__main__':main()
