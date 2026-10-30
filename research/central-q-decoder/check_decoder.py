"""Independent exact checks for native data, lift, decoder and charges."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import importlib.util, json, sys, time
ROOT=Path(__file__).resolve().parent
# Compile audited source bytes directly; do not trust pre-existing bytecode.
ns={'__name__':'decoder_checked','__file__':str(ROOT/'decoder.py')}
exec(compile((ROOT/'decoder.py').read_bytes(),str(ROOT/'decoder.py'),'exec',dont_inherit=True,optimize=0),ns)
need=ns['need']

def data_checks(cube):
    ports=cube.ports;rows=cube.rows;need(len(ports)==512,'512 actual ports')
    entries=0
    for i,row in rows.items():
        need(len(row)==76 and sum(abs(a)for a in row.values())==112,'76 terms and row norm seven')
        product=Counter()
        for j,c in row.items():
            need(rows[j].get(i)==c,'K symmetric')
            for k,d in rows[j].items():product[k]+=c*d
        need({k:v for k,v in product.items()if v}=={i:256},'Every entry of K squared equals identity')
        entries+=512
    for p in ports:
        fw,bw=cube.forward[p],cube.inverse[p]
        need([x[0]for x in fw]==['P','D'] and [x[0]for x in bw]==['D','P'],'Source normalizer grammar')
        G=fw[0][1];Gi=bw[1][1]
        need(all(ns['mv'](Gi,ns['mv'](G,1<<j))==1<<j for j in range(25)),'Inverse linear map')
        need(fw[1][1]==[0]*25 and bw[0][1]==[0]*25,'Actual normalizer has linear sign only')
        need(all(x in (0,2)for x in fw[1][2]) and fw[1][2]==bw[0][2],'Exact inverse real sign')
        # Test lifted phase as a SUM of digit-column phases, not once per field.
        for f in (1,2,3):
            x=sum((1<<((j*7)%25))* (1<<(25*j)) for j in range(f))
            axes=tuple(range(25));a,t=ns['lifted'](fw,x,f,axes);b,u=ns['lifted'](bw,a,f,axes)
            need(b==x and (t+u)%4==0,'Lifted inverse including phase')
    return {'scalar_matrix_entries':entries,'inverse_normalizers':512,'lifted_inverse_cases':1536}

def gaussian_checks():
    cases=0
    for f in range(1,7):
        state={(0,j):((j*7)%19-9,(j*3)%17-8) for j in range(1<<f)}
        state={k:v for k,v in state.items()if v!=(0,0)}
        actual,e=ns['q_pass'](state,0,f)
        # Independent dense Hamming-distance formula: ((1+i)/2)^f (-i)^dist.
        factor=(1,0)
        for _ in range(f):factor=(factor[0]-factor[1],factor[0]+factor[1])
        expect={}
        for y in range(1<<f):
            a=b=0
            for (owner,x),(u,v) in state.items():
                c,d=ns['phase'](factor,-(x^y).bit_count());a+=c*u-d*v;b+=c*v+d*u
            if a or b:expect[0,y]=(a,b)
        expect,den=ns['normalize'](expect,f)
        need((actual,e)==(expect,den),'Butterfly differs from exact Hamming kernel')
        need(ns['q_pass'](actual,e,f,-1)==(state,0),'Gaussian inverse')
        need(e<=(f+1)//2,'Sharp Gaussian denominator')
        cases+=1
    return cases

def native_replays(cube):
    result=[]
    seed={(cube.ports[0],1):(1,0)}
    c1,e1=cube.code(seed,0,1,ns['stage_axes'](0));c12,e12=cube.code(c1,e1,1,ns['stage_axes'](1))
    c2,e2=cube.code(seed,0,1,ns['stage_axes'](1));c21,e21=cube.code(c2,e2,1,ns['stage_axes'](0))
    need((c12,e12)!=(c21,e21),'Actual fresh codes must retain noncommutativity')
    for stages,f,which in [(1,1,0),(1,2,7),(1,3,19),(2,1,3)]:
        owner=cube.ports[which]
        original={(owner,0):(1,0),(owner,1):(2,-1)}
        s,e=ns['gauge_input'](cube,original,0,f,stages)
        y,den=ns['run_recipe'](cube,s,e,f,stages)
        need((y,den)==(original,0),'Actual sparse native gauge recovery')
        dropped=ns['run_recipe'](cube,s,e,f,stages,False)
        need(dropped==ns['q_pass'](original,0,f,-1),'One-pass lower-rank repair')
        need(e<=4*stages+2*((f+1)//2),'Actual terminal denominator bound')
        # Missing the first Q is a concrete wrong-side mutation on actual data.
        if stages==1 and f==1:
            z,k=cube.code(s,e,f,ns['stage_axes'](0));z,k=ns['q_pass'](z,k,f)
            need((z,k)!=(original,0),'Omitted Gaussian mutation must fail')
            bad=ns['Cube'](ns['source']())
            bad.inverse={p:[['D',[0]*25,[0]*25],word[1]] for p,word in bad.inverse.items()}
            need(ns['run_recipe'](bad,s,e,f,stages)!=(original,0),'Omitted actual native phase mutation must fail')
        result.append({'stages':stages,'width':f,'input_terms':len(original),'coded_terminal_terms':len(s),'restored':True})
    return result

def emission_checks(cube):
    for m in (1,2,19):
        r=ns['recipe'](m);ev=r['chronological_events']
        need(sum(e.get('count',0)for e in ev if e['op']=='GAUSSIAN_Q')==1024,'Actual two-query charge')
        need([e['stage']for e in ev if e['op']=='ACCUMULATE_K_INTO_OWNED']==list(reversed(range(m))),'Actual inverse order')
        need(sum(e.get('ADD',0)for e in ev)==38912*m,'Actual ADD charge')
        need(sum(e.get('count',0)for e in ev if e['op']=='CLEAR_OWNED')==1024*m,'Owned initialization and return')
    for m in (1,19):
        for full in (True,False):
            count=Counter()
            for ev in ns['literal_events'](cube,m,full):
                count[ev[0]]+=1
                if ev[0]=='ADD':need(cube.rows[ev[2]][ev[4]]==ev[5] and ev[6]==16,'Literal coefficient binding')
            need(count['PAID_Q']==512*(2 if full else 1),'Every paid field counted')
            need(count['ADD']==38912*m and count['CLEAR']==1024*m,'Full emitted cost ledger')
            need(count['MONOMIAL']==1024*m and count['SWAP']==512*m,'Full recoding routing ledger')
    return 7

def word_checks():
    def reduce(w):
        out=[]
        for x in w:
            if out and out[-1]==-x:out.pop()
            else:out.append(x)
        return out
    for m in (1,2,19):
        p=list(reversed(range(2,m+2)));pi=[-x for x in reversed(p)]
        w=[-1]+p+[-1];repair=[1]+pi+[1]
        need(reduce(repair+w)==[],'Universal free-word decoder identity')
        if m>1:need(reduce([1]+list(reversed(pi))+[1]+w)!=[],'Wrong inverse-order mutation')
    return 3

def run():
    cube=ns['Cube'](ns['source']())
    return {'status':'PASS_EXACT_PAID_CENTRAL_Q_DECODER','source':data_checks(cube),'free_noncommuting_word_cases':word_checks(),'gaussian_widths':gaussian_checks(),
            'actual_native_sparse_replays':native_replays(cube),'emission_cases':emission_checks(cube),
            'all_width_evidence':'PROOF.md; finite executions corroborate rather than replace it',
            'new_kappa':False,'profitable_closure':False}
if __name__=='__main__':print(json.dumps(run(),indent=2))
