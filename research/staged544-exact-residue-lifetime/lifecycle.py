"""Literal helper277 lifetime, physical climbs, and exact dyadic decode bounds.
The free-operator audit and frame trace are credited frozen predecessor modules.
"""
import gzip,json,sys,hashlib
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'frozen'))
import audit_core as a
import retiming as t
import clifford_exact as ce
from mersenne import need

def load(tag):return json.loads(gzip.decompress((P/'frozen'/('WORD-'+tag+'.json.gz')).read_bytes()))
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def source_trace(w):
    bill,widths,chain,start,end=a.frame_bill(w)
    need(a.same_cleanup(w['cleanup'],a.derive_cleanup(w)),'literal derived inverse cleanup')
    a.hygiene(w)
    actual=[]
    for section in ('A','B','restore'):
        for i,g in enumerate(w[section]):
            if 277 in a.touched(g):actual.append({'section':section,'index':i,'gate':g})
    tail=[{'section':'cleanup','index':i,'gate':g}for i,g in enumerate(w['cleanup'])if 981 in a.touched(g)]
    climbs=[];previous=start[277]
    for address,d,mask in chain[277]:
        if d:climbs.append({'address':list(address),'before':list(t.basis(previous)),'after':list(t.basis(mask)),'rank':d})
        previous=mask
    # Use exactly source-supplied frame bases, because the source canonical
    # frame constructor's byte-level recipe is bound to its chosen basis.
    for q in climbs:
        address=q['address']
        q['after']=w['helper_final']['277'] if address==['end']else w[address[0]][address[1]][-1]
    for i,q in enumerate(climbs):q['before']=[]if i==0 else climbs[i-1]['after']
    need([x['rank']for x in climbs]==[1]*5,'five rank-one charges')
    need([x['address']for x in climbs]==[['A',2340],['A',2381],['A',2391],['A',2409],['end']],'literal climb addresses')
    need(len(actual)==len(tail)==49,'49 touches each')
    snap={};rows=a.forward_rows(w,snapshot=lambda x:snap.update({k:dict(v)for k,v in x.items()}))
    need(not a.boundary_defects(w,snap),'restored before cleanup')
    need(a.endpoint_defects(w,rows)==([],[],[],True),'all arbitrary dirty endpoint rows')
    need(snap[277]==rows[277]=={(277,()):F(1)},'helper277 exact logical return')
    need(rows[981]=={(981,()):F(1)},'buffer981 exact logical return')
    dual=a.forward_rows(w,dual=True)
    need(a.endpoint_defects(w,dual,dual=True)==([],[],[],True),'dual endpoints')
    return {'helper':277,'cleanup_buffer':981,'forward':actual,'cleanup':tail,'climbs':climbs,'local_profile':bill,'width_inventory':widths,'helper_entry':[],'helper_terminal':w['helper_final']['277'],'whole_word_primal_and_dual_dirty_identity':True,'scalar_counts':dict(Counter(x['gate'][0]for x in actual+tail))}

def generate_climbs(trace):
    out=[]
    for c in trace['climbs']:
        op=ce.canonical_frame(9,tuple(c['before'])).adjoint().then(ce.canonical_frame(9,tuple(c['after'])))
        rec,_=ce.lower_child(op);need(rec['rank']==1,'source compiler climb rank')
        out.append(dict(c,recipe=rec))
    return out

def height_bound(w):
    # Public positive-path bound for real component magnitudes and dyadic
    # denominators, not an actual peak after cancellation. Warps are monomial.
    seq,tail=a.program(w);seq+=tail
    regs=set(range(704))-set(w['removed']);regs|={r+704 for r in map(int,w['helper_final'])}
    B={r:F(1)for r in regs};D={r:0 for r in regs};mb=F(1);md=0
    for g in seq:
        kind=g[0];r=g[1]
        if kind in ('add','corr'):
            s=g[2];q=F(g[3],g[4])if kind=='add'else g[4]
            B[r]+=abs(q)*B[s];D[r]=max(D[r],D[s]+(q.denominator.bit_length()-1))
        elif kind=='scale':
            q=F(g[2],g[3]);B[r]*=abs(q);D[r]+=q.denominator.bit_length()-1
        else:need(kind=='warp','height opcode')
        mb=max(mb,B[r]);md=max(md,D[r])
    # Any completed physical frame has <=9 C layers, each at most2 in
    # real-component sup norm, with denominator at most2 per layer.
    return {'logical_positive_component_bound_per_input_unit':str(mb),'logical_common_denominator_exponent':md,'physical_all_cut_denominator_exponent':md+9,'physical_component_bound_per_input_unit':str(512*mb),'all_cut_modulus_sufficient':'M > 2^(D+10) B A, D=logical_common_denominator_exponent+9; B=logical_positive_component_bound; A=input real-component integer bound','helper277_endpoint_denominator_exponent':5,'helper277_endpoint_component_bound_per_input_unit':32,'helper277_endpoint_modulus_sufficient':'M > 2048 A','endpoint_only_reason':'Exact modular cancellation allows endpoint reconstruction without reconstructing the large intermediate rational numerators.'}

if __name__=='__main__':
    trace=source_trace(load('base'));(P/'CLIMBS.json').write_text(json.dumps(generate_climbs(trace),indent=2)+'\n')
    print(json.dumps(height_bound(load('base')),indent=2))
