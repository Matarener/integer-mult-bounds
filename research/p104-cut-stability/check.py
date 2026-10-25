"""Exact scalar cut norms for the actual P104 contact word.

No author constructor, scalar interpreter or pricing engine is imported.
COPY is explicitly implemented as ADD into the freshly initialized owned row.
This agrees on the exact trace and carries arbitrary injected owned residuals.
Prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORD_SHA='48f8734ca9c5adf5d60ded3a5fefbc24894d2c358ed7cb30fcc0d71718599446'

def need(ok,why):
    if not ok:
        raise ValueError(why)

def normal(v,e):
    if not v:
        return {},0
    combo=0
    for n in v.values():
        combo |= abs(n)
    shift=min(e,(combo&-combo).bit_length()-1)
    return ({i:n>>shift for i,n in v.items()},e-shift) if shift else (v,e)

def plus(a,b,c):
    av,ae=a;bv,be=b
    k=c.denominator.bit_length()-1
    need(c.denominator==1<<k,'Dyadic coefficient')
    e=max(ae,be+k)
    aa=1<<(e-ae)
    bb=c.numerator<<(e-be-k)
    out={i:aa*n for i,n in av.items()}
    for i,n in bv.items():
        z=out.get(i,0)+bb*n
        if z:
            out[i]=z
        else:
            out.pop(i,None)
    return normal(out,e)

def scaled(a,c):
    v,e=a
    k=c.denominator.bit_length()-1
    need(c.denominator==1<<k,'Dyadic SCALE')
    return normal({i:c.numerator*n for i,n in v.items()},e+k)

def norm(a):
    v,e=a
    return Q(sum(abs(n) for n in v.values()),1<<e)

def values(a):
    v,e=a
    return {i:Q(n,1<<e) for i,n in v.items()}

def encode(x):
    if isinstance(x,Q):
        return str(x)
    if isinstance(x,dict):
        return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):
        return [encode(v) for v in x]
    return x

def ceil_log2(q):
    q=Q(q)
    need(q>0,'Positive logarithm argument')
    b=q.numerator.bit_length()-q.denominator.bit_length()
    if b>=0:
        return b if q.numerator<=q.denominator*(1<<b) else b+1
    return b if q.numerator*(1<<(-b))<=q.denominator else b+1

def residual_word(w):
    out=json.loads(json.dumps(w))
    sites=[]
    for t,e in enumerate(out['program']):
        if e[0]=='COPY':
            need(e[-2]=='1','The eight literal COPY coefficients are one')
            e[0]='ADD';sites.append(t)
    need(len(sites)==8,'Eight concrete ADD implementations')
    return out,sites

def calculate():
    raw=(HERE/'inputs/WORD.json.gz').read_bytes()
    need(hashlib.sha256(raw).hexdigest()==WORD_SHA,'Exact published input before replay')
    w=json.loads(gzip.decompress(raw))
    implemented,implemented_sites=residual_word(w)
    need(json.loads(gzip.decompress((HERE/'RESIDUAL-WORD.json.gz').read_bytes()))==implemented,
         'Concrete residual-preserving word equals the eight-site implementation')
    public=w['public'];n=public+8;p=w['program'];basis=w['frames']
    need(public==735 and n==743 and len(p)==25310,'Actual finite input ABI')
    dim=list(map(len,basis))
    spans=[]
    for b in basis:
        s={0}
        for v in b:
            need(v not in s,'Independent chart basis')
            s|={x^v for x in tuple(s)}
        spans.append(s)
    rows=[({i:1},0) for i in range(public)]+[({},0) for _ in range(8)]
    frames=w['initial'][:]+[None]*8
    own=set();paid=Counter();ops=Counter();copy_sites=[]
    interval_levels=[0]*n;interval_den=[0]*n
    interval_power=0;interval_witness=None;interval_den_power=0
    maxp=Q(1);wp={'cut':0,'role':0,'l1':Q(1),'row':{0:Q(1)}}
    ep=0;ep_witness=None;maxcoef=Q(0);maxden=0
    imax=max(dim[f] for f in w['initial'])
    fmax=max(dim[f] for f in w['final'])
    taup=imax+max(dim);taus=fmax+max(dim)
    for t,e in enumerate(p):
        op,r=e[:2];ops[op]+=1
        if op=='MOVE':
            _,r,a,b,private=e
            need(frames[r]==a and ((r in own)==private),'Current chart/owner')
            need(spans[b]<spans[a] if private else spans[a]<spans[b],'Nested typed edge')
            rank=abs(dim[b]-dim[a]);paid[rank]+=1
            taup=max(taup,imax+dim[a]+rank)
            taus=max(taus,fmax+dim[b]+rank)
            frames[r]=b
            continue
        if op=='INIT':
            need(r>=public and r not in own,'Owned INIT only')
            own.add(r);rows[r]=({},0);frames[r]=e[2]
            interval_levels[r]=0;interval_den[r]=0
        elif op=='CLEAR':
            need(r in own and frames[r]==e[2],'Owned CLEAR only')
            own.remove(r);rows[r]=({},0);frames[r]=None
            interval_levels[r]=0;interval_den[r]=0
        else:
            c=Q(e[-2]);maxcoef=max(maxcoef,abs(c));maxden=max(maxden,c.denominator.bit_length()-1)
            need(frames[r]==e[-1],'Scalar destination chart')
            if op=='SCALE':
                rows[r]=scaled(rows[r],c)
                interval_levels[r]=max(0,interval_levels[r]+ceil_log2(abs(c)))
                interval_den[r]+=c.denominator.bit_length()-1
            else:
                need(op in ('ADD','COPY'),'Known opcode')
                s=e[2];need(s!=r and frames[s]==e[-1],'Common scalar chart')
                if op=='COPY':
                    need(r in own and not rows[r][0],'COPY has exact owned zero')
                    copy_sites.append(t)
                rows[r]=plus(rows[r],rows[s],c)
                interval_levels[r]=max(interval_levels[r],interval_levels[s]+ceil_log2(abs(c)))+1
                interval_den[r]=max(interval_den[r],interval_den[s]+c.denominator.bit_length()-1)
        if interval_levels[r]>interval_power:
            interval_power=interval_levels[r]
            interval_witness=[t+1,r,interval_power]
        interval_den_power=max(interval_den_power,interval_den[r])
        magnitude=norm(rows[r])
        if magnitude>maxp:
            maxp=magnitude
            wp={'cut':t+1,'role':r,'l1':magnitude,'row':values(rows[r])}
        if rows[r][1]>ep:
            ep=rows[r][1];ep_witness=[t+1,r,ep]
    need(not own and frames[:public]==w['final'],'All declared exits')
    live=set(w['live'])
    for r,a in enumerate(rows):
        expected={r:Q(1)} if r<public else {}
        if r-112 in live:
            expected[r-112]=Q(1)
        need(values(a)==expected,'Every arbitrary-input endpoint '+str(r))

    # Columns of the public-output response matrix at each backward cut.
    columns=[({i:1},0) for i in range(public)]+[({},0) for _ in range(8)]
    row_sums=[Q(1) for _ in range(public)]
    maxs=Q(1);ws={'cut':len(p),'output':0,'l1':Q(1),'row':{0:Q(1)}}
    es=0;es_witness=None;copy_controls=[]
    def change(r,new,cut):
        nonlocal maxs,ws,es,es_witness
        old=columns[r];ov,oe=old;nv,ne=new;columns[r]=new
        for out in ov.keys()|nv.keys():
            row_sums[out]+=Q(abs(nv.get(out,0)),1<<ne)-Q(abs(ov.get(out,0)),1<<oe)
            need(row_sums[out]>=0,'Nonnegative exact row sum')
            if row_sums[out]>maxs:
                maxs=row_sums[out]
                witness={i:Q(v[out],1<<level) for i,(v,level) in enumerate(columns) if v.get(out)}
                need(sum(map(abs,witness.values()))==maxs,'Suffix maximizer row sum')
                ws={'cut':cut,'output':out,'l1':maxs,'row':witness}
        if ne>es:
            es=ne;es_witness=[cut,r,ne]
    for t in range(len(p)-1,-1,-1):
        e=p[t];op,r=e[:2]
        if op=='MOVE':
            continue
        if op in ('INIT','CLEAR'):
            change(r,({},0),t)
        elif op=='SCALE':
            change(r,scaled(columns[r],Q(e[-2])),t)
        else:
            c=Q(e[-2]);s=e[2]
            if op=='COPY':
                need(columns[r][0],'Injected owned COPY residual reaches a public output')
                out=min(columns[r][0]);coefficient=Q(columns[r][0][out],1<<columns[r][1])
                copy_controls.append({'event':t,'owned':r,'output':out,'residual_response':coefficient,
                                      'assignment_COPY_response':Q(0),'ADD_COPY_retains_residual':True})
            change(s,plus(columns[s],columns[r],c),t)
            # Actual COPY implementation is ADD, so columns[r] is retained.
    for i,a in enumerate(columns):
        expected={i:Q(1)} if i<public else {}
        if i in live:
            expected[i+112]=Q(1)
        need(values(a)==expected,'Independent reverse whole endpoint '+str(i))
    need(len(copy_controls)==8 and len(copy_sites)==8,'Eight residual controls')
    need(sum(paid.values())==3624 and sum(r*m for r,m in paid.items())==5894,'Actual Gaussian jobs and rank sum')
    need(maxcoef==Q(65537,2) and maxden==16,'Actual scalar height')
    need(1+maxcoef<2**16,'Exact scalar accumulator guard')
    ks=len(p)+2
    kd0=len(p)-ops['MOVE']+2
    kd1=sum(r*m for r,m in paid.items())
    return encode({'status':'PASS_EXACT_P104_ALL_CUT_SCALAR_STABILITY',
        'source_head':'1123635a6f63f23638df9459c994160e5e649d30','word_sha256':WORD_SHA,
        'cuts':len(p)+1,'public_inputs':public,'state_roles':n,'op_counts':dict(ops),
        'COPY_implementation':'ADD into an exactly initialized owned zero; injected residual is retained',
        'residual_word':{'canonical_sha256':hashlib.sha256((json.dumps(implemented,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest(),
                         'COPY_to_ADD_sites':implemented_sites,'new_Gaussian_calls':0,
                         'ordinary_scalar_tariff_change':0,
                         'reason':'Source ADD and COPY have the same literal coefficient tariff; all eight coefficients are one.'},
        'prefix_max_row_l1':maxp,'prefix_max_witness':wp,'prefix_max_entry_denominator_exponent':ep,
        'prefix_denominator_witness':ep_witness,
        'suffix_max_row_l1':maxs,'suffix_max_witness':ws,'suffix_max_entry_denominator_exponent':es,
        'suffix_denominator_witness':es_witness,
        'owned_residual_controls':list(reversed(copy_controls)),
        'geometry':{'input_max_chart_dimension':imax,'output_max_chart_dimension':fmax,
                    'current_max_chart_dimension':max(dim),'endpoint_prefix_N_exponent':imax+max(dim),
                    'endpoint_suffix_N_exponent':fmax+max(dim),
                    'native_recipe_prefix_N_exponent':taup,'native_recipe_suffix_N_exponent':taus},
        'scalar_guard':{'max_abs_coefficient':maxcoef,'max_denominator_exponent':maxden,
                        'accumulator_magnitude_factor_upper':2**16,'extra_accumulator_bits_upper':35},
        'all_interval_majorant':{'scalar_amplification_power_of_two':interval_power,
                                 'power_witness':interval_witness,
                                 'scalar_denominator_exponent_upper':interval_den_power,
                                 'semantic_chart_N_exponent':2*max(dim),
                                 'native_factor_interior_N_exponent':4*max(dim),
                                 'meaning':'Upper bound for every scalar interval, not an exact maximum; each row recurrence restarts at identity at every cut.'},
        'active_fiber_corollary':{'norm':'Maximum of individual field Hilbert norms, then one real-component active-fiber conversion',
                                  'local_active_axes':9,'local_coordinate_conversion_power':'ceil((9*f+1)/2)',
                                  'Hilbert_prefix_bound':maxp,'Hilbert_final_suffix_bound':maxs,
                                  'Hilbert_all_interval_power':interval_power,
                                  'external_spectator_factor':1,
                                  'method_credit':'Retained Ross Richardson / Adam Gall unitary active-fiber argument; new source-specific complete-word binding.'},
        'error_interfaces':{'completed_service_layers_including_input_output':ks,
                            'completed_service_suffix_guard_bits':ceil_log2(ks*maxs),
                            'literal_butterfly_layers_base_including_input_output':kd0,
                            'literal_butterfly_layers_slope_in_f':kd1,
                            'literal_butterfly_runtime_in_recursive_invoice':False},
        'scope':'Exact all-cut scalar matrices and elementary diagram norm bounds for this finite word. No uniform recursive-child internal implementation, full 265-axis caller precision/tape closure, new kappa, scientific admission or selected promotion is claimed.'})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    if args.write:
        word=json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))
        implemented,_=residual_word(word)
        raw=(json.dumps(implemented,sort_keys=True,separators=(',',':'))+'\n').encode()
        (HERE/'RESIDUAL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    out=calculate();path=HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text())==out,'Saved exact all-cut receipt')
    brief={k:out[k] for k in ['status','cuts','prefix_max_row_l1','suffix_max_row_l1','geometry','error_interfaces']}
    print(json.dumps(brief,sort_keys=True))

if __name__=='__main__':
    main()
