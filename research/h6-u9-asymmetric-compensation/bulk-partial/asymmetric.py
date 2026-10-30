#!/usr/bin/env python3
"""Dyadic asymmetric pure-bank K factors and paid local partial gathers.

Exact all-coefficient factor identity, all-port incidence invoice, finite
arbitrary-input lifecycle fixtures, and complete abstract rank differential.
The new physical frame/phase recipes remain a separate explicit gate.
"""
from collections import Counter
from fractions import Fraction as F
from functools import reduce
from pathlib import Path
import hashlib, importlib.util, json, math, sys
import numpy as np
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);a=importlib.util.module_from_spec(s);s.loader.exec_module(a);return a

m=load('pure_bank_screen',HERE/'screen.py')
sec=load('pure_bank_sections',m.REPO/'research/niemeier-lattices/code/e8_sections.py')
net=load('pure_bank_old_network',m.REPO/'research/h6-compensation-network/k_encoder/network.py')
Q=8192
GROUPS=[(112+44*i,list(range(113+44*i,120+44*i)),155+44*i) for i in range(16)]
GIDS=[g for g,hs,t in GROUPS]
CHANGED=sorted(c for g,hs,t in GROUPS for c in (g,*hs,t))
FULL=tuple(1<<j for j in reversed(range(17)))

def need(ok,label):
    if not ok:raise ValueError(label)

def factors(ports):
    E,W,den=sec.evaluate_operator_centers(ports);need(den==Q,'old dyadic denominator')
    A=E.copy();B=E*W[None,:]
    for i,(g,hs,t) in enumerate(GROUPS):
        numerator=2*E[:,g]+E[:,hs].sum(axis=1)+2*E[:,t]
        need(not(numerator%8).any(),'dyadic unit basis yields integral static source coefficients')
        A[:,g]=numerator//8
        B[:,g]=128*E[:,g]
        for h in hs:B[:,h]=4*E[:,h]-16*E[:,g]
        B[:,t]=-3*E[:,t]-32*E[:,g]
        own=ports[:,8*(i//8):8*(i//8+1)]
        other=ports[:,8*(1-i//8):8*(2-i//8)]
        expected=np.where((other==0).all(axis=1),ports[:,i],0)
        need(np.array_equal(A[:,g],expected),'pure-bank coefficient at every supplied port')
    return A,B,E,W

def polynomial_certificate():
    old,W,cert=net.polynomial_certificate()
    H=8*old.copy();B=8*(W[:,None]*old)
    for g,hs,t in GROUPS:
        H[g]=2*old[g]+old[hs].sum(axis=0)+2*old[t]
        B[g]=1024*old[g]
        for h in hs:B[h]=32*old[h]-128*old[g]
        B[t]=-24*old[t]-256*old[g]
    need(np.array_equal(B.T@H,64*old.T@(W[:,None]*old)),
         'every one of665856 new asymmetric polynomial operator coefficients')
    return {'checked_coefficients':816**2,'old_certificate':cert,
            'common_polynomial_denominator':96,
            'new_source_polynomials_int64_sha256':hashlib.sha256(H.astype('<i8').tobytes()).hexdigest(),
            'new_scatter_numerator_polynomials_int64_sha256':hashlib.sha256(B.astype('<i8').tobytes()).hexdigest(),
            'identity':'B96^T H96 =64 A12^T diag(w) A12, so (B96 M)(H96 M)^T/(8192*96^2)=K on every norm16 pair.'}

def primitive(q):
    q=F(q)
    if not q:return 0
    a=abs(q.numerator);return 3+a.bit_length()-1+a.bit_count()+q.denominator.bit_length()-1

def census(ports):
    gc=Counter();sc=Counter();ac=np.zeros(816,dtype=np.int64);bc=np.zeros(816,dtype=np.int64)
    oldgc=Counter();oldsc=Counter();maxa=maxb=0
    for lo in range(0,len(ports),512):
        A,B,E,W=factors(ports[lo:lo+512])
        for matrix,counter in ((A,gc),(B,sc),(E,oldgc),(E*W[None,:],oldsc)):
            vals,counts=np.unique(matrix,return_counts=True)
            counter.update({int(v):int(n) for v,n in zip(vals,counts) if v})
        ac+=np.abs(A).sum(axis=0);bc+=np.abs(B).sum(axis=0)
        maxa=max(maxa,int(np.max(np.abs(A))));maxb=max(maxb,int(np.max(np.abs(B))))
    gp=sum(n*primitive(v) for v,n in gc.items());sp=sum(n*primitive(F(v,Q)) for v,n in sc.items())
    oldgp=sum(n*primitive(v) for v,n in oldgc.items());oldsp=sum(n*primitive(F(v,Q)) for v,n in oldsc.items())
    old=json.loads((m.REPO/'research/h6-compensation-network/k_encoder/RESULT.json').read_text())
    need(2*oldgp+2*oldsp+3*816==old['K_forward_primitive_bound'],'old full primitive census reproduced')
    forward_bound_num=dual_bound_num=0
    for lo in range(0,len(ports),512):
        A,B,E,W=factors(ports[lo:lo+512])
        forward_bound_num=max(forward_bound_num,int(np.max(Q+np.abs(B)@(1+ac))))
        dual_bound_num=max(dual_bound_num,int(np.max(Q+np.abs(A)@(Q+bc))))
    forward_bound_num=max(forward_bound_num,int(Q*(1+ac.max())))
    dual_bound_num=max(dual_bound_num,int(Q+bc.max()))
    den=max(F(v,Q).denominator.bit_length()-1 for v in sc)
    maxnum=max(max(abs(v) for v in gc),max(abs(F(v,Q).numerator) for v in sc))
    forward=2*gp+2*sp+3*816;dual=forward+3*816
    return {'all_port_rows':len(ports),'ordinary_centres':816,'new_extra_centres':0,
            'nonzero_gather_incidence_count':sum(gc.values()),'nonzero_scatter_incidence_count':sum(sc.values()),
            'gather_coefficient_census':{str(v):n for v,n in sorted(gc.items())},
            'scatter_coefficient_census':{str(F(v,Q)):n for v,n in sorted(sc.items())},
            'gather_abs_column_sums':ac.tolist(),'scatter_numerator_abs_column_sums':bc.tolist(),
            'forward_component_primitives':forward,'dual_component_primitives':dual,
            'forward_component_primitive_change':forward-old['K_forward_primitive_bound'],
            'dual_component_primitive_change':dual-old['K_dual_primitive_bound'],
            'real_component_doubling':'Not applied; these use the pinned K scalar convention before any real/imaginary doubling.',
            'top_level_scalar_additions':2*(sum(gc.values())+sum(sc.values())),
            'max_abs_gather_coefficient':maxa,'max_abs_scatter_coefficient':str(F(maxb,Q)),
            'maximum_reduced_numerator':maxnum,'denominator_depth_above_entrance_grid':den,
            'forward_logical_prefix_l1_upper':str(F(forward_bound_num,Q)),
            'dual_logical_prefix_l1_upper':str(F(dual_bound_num,Q)),
            'forward_Horner_work_l1_upper':str(F(maxnum*forward_bound_num,Q)),
            'dual_Horner_work_l1_upper':str(F(maxnum*dual_bound_num,Q)),
            'prefix_proof':'Forward target prefixes are bounded by1+sum_c |B_tc|*(1+sum_s|A_sc|)/8192; centres by1+sum_s|A_sc|. Dual source prefixes are bounded by1+sum_c|A_sc|*(1+sum_t|B_tc|/8192); centres by1+sum_t|B_tc|/8192. Horner work is cleared and never exceeds maximum reduced numerator times these bounds. All B-weighted sources have integral entrance rows (centres in forward, unchanged targets in dual), so literal fractional depth is at most the displayed denominator depth.'}

def fixtures(ports,packed,frames):
    chosen=[]
    for bank in range(2):
        U=()
        for i in range(1080*bank,1080*(bank+1)):
            V=m.basis(U+(int(packed[i]),))
            if len(V)>len(U):chosen.append(i);U=V
            if len(U)==9:break
    chosen+=list(map(int,np.linspace(2160,30959,14,dtype=int)))
    chosen=list(dict.fromkeys(chosen));A,B,E,W=factors(ports[chosen])
    A=A[:,CHANGED];B=B[:,CHANGED];E=E[:,CHANGED];W=W[CHANGED]
    n=len(chosen);cnum=len(CHANGED);size=2*n+cnum
    labels=[int(packed[i]) for i in chosen]
    cframes=[frames[(c-112)//352] if c in GIDS else FULL for c in CHANGED]
    expected=(E*W[None,:])@E.T

    def replay(dual=False,omit=None,bad_scatter=False):
        rows=np.eye(size,dtype=np.int64)*Q
        state=[m.basis([p]) for p in labels]+[()]*n+[()]*cnum
        paths=[[] for _ in range(size)];live=False;prank=0;peak=Q;depth=0;events=0
        def climb(r,U,phase):
            nonlocal events
            if phase==omit:return
            need(len(m.basis(state[r]+U))==len(U),'nested ordinary frame '+phase)
            if len(U)>len(state[r]):paths[r].append(len(U)-len(state[r]))
            state[r]=U;events+=1
        def add(dst,src,num,den,phase):
            nonlocal peak,depth,events
            if not num or phase==omit:return
            need(state[dst]==state[src],'literal common frame '+phase)
            v=num*rows[src];need(not(v%den).any(),'exact dyadic fixture arithmetic')
            rows[dst]+=v//den;peak=max(peak,int(np.abs(rows[dst]).sum()))
            g=int(np.gcd.reduce(np.abs(rows[dst])));depth=max(depth,0 if not g else max(0,13-((g&-g).bit_length()-1)))
            events+=1
        def orient(dst,src,num,den,phase):
            if dual:dst,src,num=src,dst,-num
            add(dst,src,num,den,phase)
        for c in range(cnum):
            for t in range(n):orient(n+t,2*n+c,-int(B[t,c]),Q,'dirt_prefix')
        for i,p in enumerate(chosen):
            if p<2160:climb(i,frames[p//1080],'source_U')
        for c,fullcol in enumerate(CHANGED):
            if fullcol in GIDS:
                climb(2*n+c,cframes[c],'centre_U')
                for i in range(n):orient(2*n+c,i,int(A[i,c]),1,'gather')
        for i in range(n):climb(i,FULL,'source_FULL')
        for c,fullcol in enumerate(CHANGED):
            if fullcol not in GIDS:
                climb(2*n+c,FULL,'centre_FULL')
                for i in range(n):orient(2*n+c,i,int(A[i,c]),1,'gather')
        for c in range(cnum):
            need(not live,'sequential private lifetime');live=True;prank+=len(cframes[c])
            rows=np.vstack((rows,np.zeros((1,size),dtype=np.int64)));state.append(() if dual else cframes[c])
            if not dual:
                rows[-1]=rows[2*n+c];state[-1]=()
            for t in range(n):
                z=int((E[t,c]*W[c]) if bad_scatter else B[t,c])
                if dual:add(len(state)-1,n+t,z,Q,'private_scatter')
                else:add(n+t,len(state)-1,z,Q,'private_scatter')
            if dual:
                state[-1]=cframes[c];add(2*n+c,len(state)-1,-1,1,'private_copy_dual')
            if omit!='private_erase':
                rows=rows[:-1];state.pop();live=False
        need(not live,'all private copies erased')
        for c,fullcol in enumerate(CHANGED):
            if fullcol in GIDS:climb(2*n+c,FULL,'centre_to_FULL')
        for c in range(cnum):
            for i in range(n):orient(2*n+c,i,-int(A[i,c]),1,'cleanup')
        for i,p in enumerate(labels):climb(n+i,m.perp((p,)),'target_cap')
        want=np.eye(size,dtype=np.int64)*Q
        if dual:want[:n,n:2*n]-=expected.T
        else:want[n:2*n,:n]+=expected
        need(np.array_equal(rows,want),'all arbitrary source/target/centre dirt columns')
        need(all(state[i]==FULL for i in range(n)) and all(state[2*n+c]==FULL for c in range(cnum)),
             'every source and centre FULL endpoint')
        need(all(len(state[n+i])==16 for i in range(n)),'every target cap endpoint')
        return {'dual':dual,'actual_port_count':n,'ordinary_changed_centres':cnum,
                'arbitrary_input_columns':size,'scalar_or_frame_events':events,
                'private_episodes':cnum,'private_rank_mass':prank,
                'fixture_exact_logical_prefix_l1':str(F(peak,Q)),'fixture_exact_denominator_depth':depth,
                'source_paths':paths[:n],'changed_centre_paths':paths[2*n:],
                'all_basis_columns':'PASS'}
    out=[replay(False),replay(True)];controls=[]
    for omit in ('dirt_prefix','gather','private_scatter','cleanup','source_U','centre_U','centre_to_FULL','private_erase'):
        for dual in (False,True):
            try:replay(dual,omit)
            except ValueError as err:controls.append({'dual':dual,'defect':omit,'rejected_by':str(err)})
            else:raise ValueError('omission was accepted: '+omit)
    for dual in (False,True):
        try:replay(dual,bad_scatter=True)
        except ValueError as err:controls.append({'dual':dual,'defect':'retained_old_scatter','rejected_by':str(err)})
        else:raise ValueError('contragredient defect accepted')
    return {'actual_port_indices':chosen,'orientations':out,'negative_controls':controls}

def differential(frames):
    geo={'ports':1080,'U_rank':9,'radical_rank':0};rows=[]
    for k in map(F,('.002','.003','.005')):
        single=m.delta_invoice(geo,8,0,k)
        need(single['all_arity_sign']=='BETTER','own-visit pure bank gain')
        z=single.copy();z['per_stage_histogram_delta']={r:2*n for r,n in single['per_stage_histogram_delta'].items()}
        z['private_rank_saved']=128;z['centres_granted']=16
        z['m49_margin_loss_per_stage']=m.b.interval(2*F(single['m49_margin_loss_per_stage']['lower']),2*F(single['m49_margin_loss_per_stage']['upper']))
        rows.append(z)
    return {'private_C_old':13872,'private_C_new':13744,'private_copy_histogram':{'9':16,'17':800},
            'ordinary_K_role_path_histogram':{'9,8':16,'17':800},
            'source_path_histogram':{'8,8':2160,'16':28800},'target_path_histogram':{'16':30960},
            'extra_ordinary_roles':0,'unchanged_stock_and_pads':True,
            'complete_per_stage_rank_count_delta':{'8':4336,'9':32,'16':-2160,'17':-32},
            'rank_mass_change':-128,'coverage_deficit_change_at_stages_L':'128*L',
            'targets':rows,'all_arity_proof':'Delta(pressure-D)/L=m^b sum_r DeltaH_r r^(1-b), so its sign is independent of m. Exact positive-series intervals at m49 certify every positive arity for each displayed exponent b=k+1e-24.'}

def main():
    roots,fourth,ports,packed=m.setup()
    geos=[m.geometry(packed,range(1080*j,1080*(j+1))) for j in range(2)]
    frames=[tuple(x['U']) for x in geos]
    need(all(x['U_rank']==9 and x['radical_rank']==0 for x in geos),'actual nondegenerate pure frames')
    char=(1<<17)-1
    need(all(len(m.basis(U+(char,)))==9 for U in frames),'pure frame contains characteristic vector')
    cert=polynomial_certificate();counts=census(ports);fix=fixtures(ports,packed,frames);bill=differential(frames)
    paths=[m.REPO/'research/niemeier-lattices/code/e8_sections.py',m.REPO/'research/niemeier-lattices/code/e8_cubed.py',
           m.REPO/'research/h6-compensation-network/k_encoder/network.py',m.OLD/'optimistic_budget.py']
    out={'status':'PASS_EXACT_DYADIC_ASYMMETRIC_PURE_BANK_LOCAL_WORD_AND_ABSTRACT_PAID_GAIN_NO_NEW_KAPPA',
         'source_pin':m.b.PIN,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
         'ring':'Z[1/2] for scalar coefficients; static feature values are integers on all30960 ports.',
         'source_basis_change':'For each coordinate u in either E8 block:8 f=2 g+sum_(7 Fano lines)h+2 t, f=1_[pure own block]u. Replace unary g by f and keep all h,t,other columns. Each block determinant is1/4, with dyadic inverse g=4f-sum(h)/2-t.',
         'scatter_rows_numerator_den8192':{'new_f':'128*g','retained_h':'4*h-16*g','retained_trace':'-3*t-32*g','all_other_columns':'old w*E'},
         'pure_bank_geometries':geos,'polynomial_certificate':cert,'full_scalar_invoice':counts,
         'arbitrary_input_fixtures':fix,'complete_rank_differential':bill,
         'word':'AtZERO precompensate every target by all new scatter rows times arbitrary centre dirt. Pure-bank sources climb to their own U9. The16 replaced centres climb to matching U9 and gather f. All sources climb toFULL; other800 centres climb/gather atFULL. Every centre uses one separately paid private copy toZERO and scatters its new output row, then erases the private stream. The16 partial centres climb toFULL; undo every gather there. Targets climb to their actual caps. Dualize ordinary additions chronologically and replace each private copy by a ZERO target gather, ascent to centre frame, unit subtraction and erasure.',
         'physical_gate':'Each U9 contains the characteristic vector; its perpendicular is alternating8. The norm-one endpoint orthogonal-completion theorem does not itself provide the new U9 transitions. Exact phase-correct two-sided Gaussian monomial recipes for line-to-U9 rank8,U9-toFULL rank8,ZERO-toU9 rank9,and private reverse rank9 remain required before native billing is admitted.',
         'scope':'A new finite all-coefficient dyadic factor identity, restored scalar word, exhaustive incidence/scalar invoice and complete abstract rank differential. The fixtures check all arbitrary source,target,and dirty-helper columns, not all30960 port pairs event-by-event. No full H6 compensation network, compatible shared source chronology, new physical compiler/native admission, whole owner stock allocation, approximate-child/whole-word precision, tape/controller, matchingBIT supplier, or improved kappa follows.'}
    (HERE/'ASYMMETRIC.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print('C',bill['private_C_new'],'component primitives',counts['forward_component_primitives'],counts['dual_component_primitives'],
                                'changes',counts['forward_component_primitive_change'],counts['dual_component_primitive_change'])
    print('prefix',counts['forward_logical_prefix_l1_upper'],counts['dual_logical_prefix_l1_upper'],'depth',counts['denominator_depth_above_entrance_grid'])
    print('fixtures',[(x['dual'],x['arbitrary_input_columns'],x['private_rank_mass']) for x in fix['orientations']],'controls',len(fix['negative_controls']))
    for x in bill['targets']:print('target',x['target'],'per-stage margin loss',x['m49_margin_loss_per_stage']['lo'])

if __name__=='__main__':main()
