#!/usr/bin/env python3
"""Actual rank15 partial gathers for one eight-centre H6 Pauli group.

Both ZERO and radical output frames, arbitrary dirty centres, exact private
contracts, complete source/target path differentials and conditional sharing.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name,HERE/file)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


t = load('pauli_tiling_fit','module_tiling.py')
m,b,need = t.m,t.b,t.need
ranker = load('pauli_exact_rank','partial_filter.py').rank


def setup():
    roots = m.canonical_roots()
    packed = t.packed_root_pairs(roots)
    q = [sum((1 if not(j&1) else -1)*x*x for j,x in enumerate(a)) for a in roots]
    selected = [j for j,x in enumerate(q) if x]
    need(len(selected)==24 and {q[j] for j in selected}=={-8,8},'actual24-line Pauli support')
    support = [(i,j) for i in range(120) for j in selected]
    U = m.basis(packed[i][j] for i,j in support)
    radical = m.basis(w for w in range(1<<17)
                      if all(not((w&u).bit_count()%2) for u in U))
    need(len(U)==15 and len(radical)==2 and m.included(radical,U),
         'actual degenerate rank15 frame and radical2')
    need(all(m.included(radical,m.perp(packed[i][j])) for i,j in support),
         'common radical scatter frame lies in every supported cap')
    features = [[roots[i][c]*q[j] for c in range(8)] for i,j in support]
    for c in range(8):
        census = Counter(abs(row[c]) for row in features if row[c])
        need(census=={8:1536,16:336},'half-signed actual feature incidence census')
    need(ranker([roots[i] for i in range(120)])==8,'eight actual linear feature dimensions')
    # A small actual diagnostic has a full rank15 frame witness, all eight
    # feature columns, and two zero-feature ports. It is not the full matrix.
    chosen=[]; span=()
    for i,j in support:
        grown=m.basis(span+(packed[i][j],))
        if len(grown)>len(span):chosen.append((i,j));span=grown
        if len(span)==15:break
    linears=[]
    for i in range(120):
        if ranker([roots[j] for j in linears]+[roots[i]])>len(linears):linears.append(i)
        if len(linears)==8:break
    chosen+= [(i,selected[0]) for i in linears]
    chosen+= [(105,j) for j in selected[:2]]
    chosen+= [(0,j) for j in range(120) if not q[j]][:2]
    chosen=list(dict.fromkeys(chosen))
    return roots,packed,q,support,U,radical,chosen


def fixture(roots,packed,q,U,W,chosen):
    n=len(chosen)
    E=[[F(roots[i][c]*q[j]) for c in range(8)] for i,j in chosen]
    labels=[packed[i][j] for i,j in chosen]
    K=[[sum(E[i][c]*E[j][c] for c in range(8))/8192
        for j in range(n)] for i in range(n)]
    starts={f'x{i}':m.basis([labels[i]]) for i in range(n)}
    starts.update({f'y{i}':() for i in range(n)})
    starts.update({f'c{c}':() for c in range(8)})
    ends={a:m.FULL for a in starts}
    ends.update({f'y{i}':m.perp(labels[i]) for i in range(n)})
    events=[]
    def add(dst,src,v,tag):
        if v:events.append({'op':'add','dst':dst,'src':src,'q':str(v),'tag':tag})
    def climb(reg,frame,tag):
        events.append({'op':'climb','register':reg,'frame':list(frame),'tag':tag})
    for i in range(n):
        for c in range(8):add(f'y{i}',f'c{c}',-E[i][c]/8192,'dirt_prefix')
    for i in range(n):
        if any(E[i]):climb(f'x{i}',U,'source_U')
    for c in range(8):
        climb(f'c{c}',U,'centre_U')
        for i in range(n):add(f'c{c}',f'x{i}',E[i][c],'gather')
    for i in range(n):climb(f'x{i}',m.FULL,'source_FULL')
    for i in range(n):
        if any(E[i]):climb(f'y{i}',W,'target_W')
    for c in range(8):
        events.append({'op':'private','center':f'c{c}','from':list(U),'to':list(W),
                       'targets':[(f'y{i}',str(E[i][c]/8192)) for i in range(n) if E[i][c]],
                       'tag':'private_scatter'})
    for c in range(8):
        climb(f'c{c}',m.FULL,'centre_FULL')
        for i in range(n):add(f'c{c}',f'x{i}',-E[i][c],'cleanup')
    for i in range(n):climb(f'y{i}',m.perp(labels[i]),'target_cap')
    return {'N':n,'ports':chosen,'E':E,'K':K,'starts':starts,'ends':ends,'events':events}


def replay(fix,dual=False,omit=None):
    cols=list(fix['starts']);width=len(cols)
    rows={r:[F(int(i==j)) for j in range(width)] for i,r in enumerate(cols)}
    frames=dict(fix['starts']);paths={r:[] for r in cols}
    private_rank=0;primitive=0;peak=F(1);depth=0
    def add(dst,src,v):
        nonlocal primitive,peak,depth
        need(frames[dst]==frames[src],'literal equal common frame')
        rows[dst]=[x+v*y for x,y in zip(rows[dst],rows[src])]
        peak=max(peak,sum(map(abs,rows[dst])))
        depth=max(depth,max(x.denominator.bit_length()-1 for x in rows[dst]))
        a=abs(v.numerator)
        primitive+=3+a.bit_length()-1+a.bit_count()+v.denominator.bit_length()-1
    for event in fix['events']:
        if event['tag']==omit:continue
        if event['op']=='climb':
            r=event['register'];frame=tuple(event['frame'])
            need(frame==m.basis(frame) and m.included(frames[r],frame),'ordinary monotone frame')
            if len(frame)>len(frames[r]):paths[r].append(len(frame)-len(frames[r]))
            frames[r]=frame
        elif event['op']=='add':
            dst,src,v=event['dst'],event['src'],F(event['q'])
            if dual:dst,src,v=src,dst,-v
            add(dst,src,v)
        else:
            c=event['center'];U,W=tuple(event['from']),tuple(event['to'])
            targets=[(y,F(v)) for y,v in event['targets']]
            need(frames[c]==U and all(frames[y]==W for y,v in targets),'private actual entrance frames')
            need(m.included(W,U),'private nested partial frame')
            private_rank+=len(U)-len(W)
            rows['p']=[F(0)]*width;frames['p']=W if dual else U;primitive+=1
            if dual:
                for y,v in targets:add('p',y,v)
                frames['p']=U;add(c,'p',-F(1))
            else:
                rows['p']=list(rows[c]);primitive+=1
                peak=max(peak,sum(map(abs,rows['p'])))
                frames['p']=W
                for y,v in targets:add(y,'p',v)
            primitive+=1;del rows['p'];del frames['p']
    need(frames==fix['ends'],'every source,target,centre endpoint frame')
    for i,r in enumerate(cols):
        expected=[F(int(i==j)) for j in range(width)]
        if r.startswith('x') and dual:
            s=int(r[1:])
            for target in range(fix['N']):expected[cols.index(f'y{target}')]-=fix['K'][target][s]
        if r.startswith('y') and not dual:
            target=int(r[1:])
            for source in range(fix['N']):expected[cols.index(f'x{source}')]+=fix['K'][target][source]
        need(rows[r]==expected,'all arbitrary input and dirty centre columns')
    return {'orientation':'dual' if dual else 'forward','paths':paths,'private_rank':private_rank,
            'primitive_before_real_doubling':primitive,'logical_prefix_row_l1':str(peak),
            'logical_prefix_denominator_depth':depth,'ordinary_columns':width}


def differential(k,radical,shared=False):
    # Unchanged ordinary role count means unchanged stock/pads. Every
    # difference is in native paths or in the separate private episodes.
    delta=Counter()
    if not shared:
        for count in (5760,)*(2 if radical else 1):
            delta[14]+=count;delta[2]+=count;delta[16]-=count
    delta[15]+=8;delta[2]+=8;delta[17]-=8  # ordinary centre paths
    private=13 if radical else 15
    delta[private]+=8;delta[17]-=8
    saving=8*(17-private)
    need(sum(r*n for r,n in delta.items())==-saving,'complete differential rank mass')
    exponent=k+F(1,10**24)
    pos=[(F(r*n),r) for r,n in delta.items() if n>0]
    neg=[(F(-r*n),r) for r,n in delta.items() if n<0]
    pl,pu=b.oracle.pressure(pos,49,exponent)
    nl,nu=b.oracle.pressure(neg,49,exponent)
    lo,hi=pl-nu-saving,pu-nl-saving
    need((hi<0) if shared else (lo>0),'exact gain/loss sign with all stated transport')
    # Delta(pressure-D)/L =m^b sum_r DeltaH_r*r^(1-b).
    # Its sign is independent of m. The exact m49 interval proves all L.
    return {'target':str(k),'exponent_b':str(exponent),'shared_source_target_transport':shared,
            'private_rank_saving':saving,'per_L_rank_count_delta':{r:n for r,n in sorted(delta.items()) if n},
            'L3_m49_margin_loss_divided_by_L':b.interval(lo,hi),
            'sign_for_every_arity':'IMPROVES_IF_VISITS_ALREADY_PAID' if shared else 'WORSE_WITH_ITS_OWN_DATA_VISITS'}


def main():
    roots,packed,q,support,U,radical,chosen=setup()
    cases=[];controls=[]
    for name,W in (('ZERO',()),('radical2',radical)):
        fix=fixture(roots,packed,q,U,W,chosen)
        forward,dual=replay(fix),replay(fix,True)
        for tag in ('dirt_prefix','gather','private_scatter','cleanup','source_U','centre_U'):
            for inv in (False,True):
                try:replay(fix,inv,tag)
                except ValueError as err:controls.append({'variant':name,'omit':tag,'dual':inv,'gate':str(err)})
                else:raise ValueError('partial centre defect accepted '+tag)
        if W:
            for inv in (False,True):
                try:replay(fix,inv,'target_W')
                except ValueError as err:controls.append({'variant':name,'omit':'target_W','dual':inv,'gate':str(err)})
                else:raise ValueError('radical target visit omitted')
        cases.append({'name':name,'forward':forward,'dual':dual,
                      'full_K_private_C':13872-8*(17-(15-len(W))),
                      'full_source_path':[14,2],
                      'full_supported_target_path':[len(W),16-len(W)] if W else [16],
                      'full_ordinary_selected_centre_path':[15,2],
                      'full_selected_private_path':[15-len(W)],
                      'differentials':[differential(k,bool(W),sharing)
                                       for k in map(F,('.002','.003','.005')) for sharing in (False,True)]})
    # Full support prefix and lowering receipts follow from the separable
    # exact feature values. The full5760 supported ports are not densely replayed.
    dual_prefix=max(F(1)+8*sum(abs(x) for x in a[:k])
                    +F(3,8)*sum(abs(sum(a[i]*z[i] for i in range(k))) for z in roots)
                    for a in roots for k in range(9))
    need(dual_prefix==152,'full support exact dual prefix')
    primitives=8*(2*(3072*7+672*8)+2*(3072*14+672*13)+3)
    need(primitives==1258008,'eight-centre full forward primitive bill')
    out={'status':'PASS_ACTUAL_PARTIAL_PAULI_CENTRE_WORDS_AND_COMPLETE_PATH_DIFFERENTIAL_NO_NEW_KAPPA',
         'source_pin':b.PIN,'source_factor':'research/niemeier-lattices/code/e8_sections.py::evaluate_operator_centers',
         'source_columns':[120+44*i for i in range(8)],'weight':1,'denominator':8192,
         'definition':'E_i(a,b)=a_i*sum_j(-1)^(j&1)*b_j^2 in doubled coordinates; zero on both pure blocks.',
         'support_b_lines':[j for j in range(120) if q[j]],'support_ports':5760,
         'feature_nonzeros_each':3744,'feature_abs8_each':3072,'feature_abs16_each':672,
         'source_support_U':list(U),'radical_U_perp':list(radical),
         'ordinary_centres':8,'new_ordinary_centres':0,'cases':cases,
         'full_component_primitives_forward':primitives,'full_component_primitives_dual':primitives+24,
         'full_scalar_primitive_difference_vs_full_width':0,
         'full_subword_logical_prefix_row_l1_forward':35329,
         'full_subword_logical_prefix_row_l1_dual':str(dual_prefix),
         'full_subword_logical_denominator_depth':10,
         'fixture_actual_ports':chosen,'controls':controls,
         'scope':'Two actual eight-centre partial-frame gather/scatter/restore substitutions, full support geometry and exact all-arity moment differential. Whole K identity is inherited unchanged outside these8 columns. Sources visit U once; radical variant supported targets visit Uperp once. They worsen .002/.003/.005 if these data visits are newly paid, and improve if the same visits are already part of another legal network. No transport sharing, full mixed compensation, physical phases, coefficient temporary lowering, approximate-child precision or kappa is claimed.'}
    (HERE/'PARTIAL-PAULI-RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']+' source_ports=5760 U15 radical2 fixtureN='+str(len(chosen))+' controls='+str(len(controls)))
    for case in cases:
        print(case['name'],'full K C',case['full_K_private_C'])
        for row in case['differentials']:
            if not row['shared_source_target_transport']:
                print(row['target'],'perL margin loss',row['L3_m49_margin_loss_divided_by_L']['lo'])


if __name__=='__main__':main()
