#!/usr/bin/env python3
"""Source-bound idle-window cap and all-depth necessary moment screen.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import ast
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import json
from pathlib import Path
import check_moment as M

SOURCE='research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py'
SHA='6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8'

class ActiveAsserts(ast.NodeTransformer):
    def visit_Assert(self,node):
        return ast.copy_location(ast.Expr(value=ast.Call(func=ast.Name(id='need',ctx=ast.Load()),
            args=[node.test,node.msg or ast.Constant('source assertion')],keywords=[])),node)

def extracted_controller(raw):
    tree=ast.parse(raw)
    recipe=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='recipe']
    rules=[n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test)=='s % 2 == 1 and s <= 2 * K - 3']
    M.need(len(recipe)==len(rules)==1,'unique source recipe and idle rule')
    def code(nodes):
        body=ActiveAsserts().visit(ast.Module(body=nodes,type_ignores=[]))
        return compile(ast.fix_missing_locations(body),SOURCE,'exec')
    ns={'need':M.need}
    exec(code(recipe),ns)
    return ns['recipe'],code(rules)

def schedule(L,recipe,rule):
    M.need(L>=3 and L%2==1,'odd recipe domain')
    K=(L-1)//2
    levels=[-1]*K
    events=[]
    for e in recipe(K):
        if e['kind']=='local':
            s,p=e['stage'],e['pair']
            M.need(levels[p]==s-1,'source stage levels')
            levels[p]=s
            events.append(dict(e))
            exec(rule,{'s':s,'K':K,'levels':levels,'schedule':events,'need':M.need})
        elif e['kind']=='bridge':
            M.need(levels[e['dst']]==levels[e['src']],'source bridge levels')
            events.append(dict(e))
        else:
            M.need(e['kind']=='exchange' and levels==[2*K]*K,'source exchange levels')
            events.append(dict(e))
    ranks=Counter(e['rank'] for e in events if e['kind']=='idle' and e['rank'])
    expected=Counter({7:K-1})
    for j in range(1,K):
        expected[14*j]+=2
    expected=+expected
    M.need(ranks==expected,'closed-form public idle multiset')
    M.need(sum(r*n for r,n in ranks.items())*Q(222,L)==777*(L-3),'public idle rank stock')
    M.need(max(ranks,default=0)==7*(L-3),'public maximum window')
    return events

def window_excess(L,b):
    m,w,extra,idle=M.geometry(L)
    q=max(Q(0),M.C-(777*L-714))
    if not idle:
        # Grant every required dedicated idle rank cost one per rank.
        return M.minus(M.local_bill(m,b),(m*w+q,)*2)
    unit=M.power(Q(m,m-22),b)
    return M.minus(M.plus(M.local_bill(m,b),M.times(unit,idle)),(m*w,)*2)

def main():
    M.authenticate()
    raw=M.pinned(SOURCE)
    M.need(M.digest(raw)==SHA,'controller pin')
    recipe,rule=extracted_controller(raw)
    controls={L:schedule(L,recipe,rule) for L in range(3,102,2)}
    cases=[]
    b=Q('0.002')
    for L in (3,5,7,9,11,13):
        v=window_excess(L,b)
        M.need(v[0]>0,'all-depth starting inequality')
        cases.append({'L':L,'max_unsplit_public_idle_rank':7*(L-3),'excess_per_call':M.interval(v)})
    poly=M.poly_after_shift(b,None,13)
    M.need(all(x>=0 for x in poly) and poly[0]>0,'all-L monotone local pressure')
    roots={'native_no_fallback':M.root_bracket(lambda a:M.fixed_excess(a,cap=42,surcharge=False)),
           'inherited_fallback_lower_bound':M.root_bracket(lambda a:M.fixed_excess(a,cap=42))}
    M.need(60>max(e['rank'] for e in controls[9] if e['kind']=='idle'),'rank60 impossible in source windows')
    out={'status':'PASS_FIXED_CONTROLLER_ALL_DEPTH_BIT_TARGET_OBSTRUCTION','checked_at_utc':datetime.now(timezone.utc).isoformat(),
         'scientific_pin':M.PIN,'controller_path':SOURCE,'controller_sha256':SHA,
         'source_domain':'CLI guard is odd L>=5, but NAMES limits named emitted layouts to5,7,9,11,13; all-odd scope is the written recipe proof; formal L=3 is an auxiliary case',
         'nine_stage_events':controls[9],'rank_formula':'two copies of14j for j=1..K-1; K-1 copies of7; L=2K+1',
         'maximum_unsplit_public_idle_rank':'7(L-3)=m-22',
         'finite_source_transcription_controls':list(controls),
         'all_L_proof':'WINDOW-PROOF.md: source formula, dedicated-stock minimization, concavity and positive shifted polynomial',
         'b':str(b),'cases':cases,'derivative_polynomial_at_L13':list(map(str,poly)),
         'fixed_nine_stage_optimistic_roots':roots,
         'extra_stock_relaxation':'public idle=T-C+q>=0, dedicated idle=mX-q>=0; grant dedicated rankm; excess base+q(u-1); minimize q=max(0,C-T)',
         'supersedes':'depth11/rank60 is a favorable arithmetic screen requiring changed chronology; it is unavailable in the pinned public windows',
         'inputs':M.PINS,'no_new_kappa':True}
    here=Path(__file__).resolve().parent
    M.emit_result('WINDOW-RESULT.json',out)
    print(out['status']+' no_new_kappa')
    print('source nine-stage public idle ranks:14,7,28,7,42,7,42,28,14,0')
    print('all inherited odd arities, all depths, any full-progress extra stock: b>=.002 rejected')
    print('rank42 inherited fallback root:',roots['inherited_fallback_lower_bound']['decimal_lower'],roots['inherited_fallback_lower_bound']['decimal_upper'])
    print('b=.002 nine-stage excess:',cases[3]['excess_per_call']['decimal_lower'])

if __name__=='__main__':
    main()
