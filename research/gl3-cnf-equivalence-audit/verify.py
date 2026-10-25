#!/usr/bin/env python3
"""Actual CNF trace adapter; independent semantic checker is loaded after freeze.

No SAT, RUP, UNSAT or minimum-nine claim. Source helpers are deliberately reused
for extraction, while the independent engine checks clauses and Boolean ANFs.
Prepared with OpenAI Codex assistance, Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import gzip
import importlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import tempfile

# Source and independent-oracle imports must never create package bytecode.
sys.dont_write_bytecode = True

HEAD = 'ca0002008b497428f0b651501c4a220a9d2785e7'
PINS = {
 'model.py':'38945ee5997b0b985d3fa461a06451ae91f6a0ac5757e42b74c5e175967a785c',
 'cnf_model.py':'12a02756ee757e5b70507e30fc6b8657f802000945742db5726335e83c56793f',
 'exact_checker.py':'92d7b726d3776012743fbc7713193a8b338ce6ae0d868f3805b9160ebd93efe1',
 'DIRECT_NINE.json':'adc28b1cf52b848875062e9df0abdb2bc4d7b4aa4caa809480c723b571de845a',
 'CERTIFICATES.json':'f5bc7526ca29724a89ea3126cdf4b3780774c3f15a0328f3f91b227c7ad16042',
 'ENCODING_AUDIT.md':'b149c967439acffd458f22c4e480e475c8732249313bd23bd7b55265d72892f0',
 'README.md':'f5e97f74a34d53607eac9802f9cacdb84a39c187c7ee8c7bb2e8fb96c9698294',
 'NOTICE.md':'4e0e33ce73e962a9acd7a41ea3206e93e8ef3d2513deb45980f6596e04f13329',
 'LICENSE':'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4',
}
ORACLE_CODE_SHA256 = '5195b93bd0f6c2f554a105c43542e0a3c95c9220dd13df70fc3d651d9cf461fe'
ORACLE_FREEZE_SHA256 = '5243c8cbe6652a605ad689ccb9c539dbf4bef12fd871e32358b6e9fd5fde2dc3'
ORACLE_TABLE_SHA256 = 'd616ec5c70efc750a973e002985f16ac223f5f0602b9bea354a4df485e68c7d2'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def load_source(source):
    for name,digest in PINS.items():
        need(sha((source/name).read_bytes()) == digest,'source hash '+name)
    sys.path.insert(0,str(source))
    for name in ('model','cnf_model','exact_checker'):
        sys.modules.pop(name,None)
    model = importlib.import_module('model')
    cm = importlib.import_module('cnf_model')
    exact = importlib.import_module('exact_checker')
    return model,cm,exact


def product(a,b):
    return tuple(sum((sum(((a[r]>>j)&1)*((b[j]>>c)&1)for j in range(3))&1)<<c
                     for c in range(3))for r in range(3))


def reference_address_data():
    permutations = tuple(itertools.permutations(range(3)))
    def invertible(rows):
        return sum(all((rows[r]>>p[r])&1 for r in range(3))for p in permutations)&1
    elements = sorted(rows for rows in itertools.product(range(8),repeat=3)if invertible(rows))
    need(len(elements) == 168,'literal determinant enumeration has168 elements')
    index = {g:k for k,g in enumerate(elements)}
    pairs = [(i,j)for i in range(3)for j in range(3)if i != j]
    labels = []
    for i,j in pairs:
        label = list((1,2,4));label[i] ^= 1<<j;labels.append(tuple(label))
    pullbacks = [[index[product(g,h)]for h in elements]for g in labels]
    need(all(p[p[k]] == k for p in pullbacks for k in range(168)),'literal label involutions')
    distance = {index[(1,2,4)]:0}
    queue = deque(distance)
    while queue:
        k = queue.popleft()
        for p in pullbacks:
            h = p[k]
            if h not in distance:
                distance[h] = distance[k]+1;queue.append(h)
    need(len(distance) == 168,'literal Cayley graph covers GL3')
    return elements,index,pairs,labels,pullbacks,distance


def trace_class(original):
    class Trace(original):
        def __init__(self):
            super().__init__()
            self.helper_calls=[];self.xors_calls=[];self.ors_calls=[];self.equalities=[]
        def both(self,a,b):
            value=super().both(a,b)
            self.helper_calls.append(('and',a,b,value));return value
        def xor(self,a,b):
            value=super().xor(a,b)
            self.helper_calls.append(('xor',a,b,value))
            return value
        def xors(self,items):
            seen=[]
            def tapped():
                for item in items:
                    seen.append(item);yield item
            value=super().xors(tapped())
            self.xors_calls.append((tuple(seen),value));return value
        def ors(self,items):
            seen=[]
            def tapped():
                for item in items:
                    seen.append(item);yield item
            value=super().ors(tapped())
            self.ors_calls.append((tuple(seen),value));return value
        def equal(self,a,b):
            self.equalities.append((a,b));super().equal(a,b)
    return Trace


def build_trace(cm,n,support=True,target=None,endpoint_columns=None):
    original=cm.CNF;cm.CNF=trace_class(original)
    try:
        kwargs={'support_bounds':support}
        if target is not None:kwargs['target']=target
        if endpoint_columns is not None:kwargs['endpoint_columns']=endpoint_columns
        return cm.build(n,**kwargs)
    finally:
        cm.CNF=original


def allowed_masks(n,target,elements,index,distance,support):
    allowed=[]
    for t in range(n+1):
        columns=[]
        for c in range(3):
            backward={index[product(x,target[c])]for k,x in enumerate(elements)if distance[k] <= n-t}
            columns.append({k for k in range(168)if not support or (distance[k] <= t and k in backward)})
        allowed.append(columns)
    return allowed


def state_literals(n,allocated,elements,index,distance,target,support,endpoint_columns=None):
    masks=allowed_masks(n,target,elements,index,distance,support)
    state=[]
    expected_keys=set()
    for t in range(n+1):
        matrix=[]
        for r in range(3):
            row=[]
            for c in range(3):
                values=[]
                for k,g in enumerate(elements):
                    if t == 0:value=1 if r == c and g == (1,2,4)else -1
                    elif t == n:
                        expected=(r == c and g == target[c])if endpoint_columns is None else g in endpoint_columns[c][r]
                        value=1 if expected else -1
                    elif k in masks[t][c]:
                        expected_keys.add((t,r,c,k));value=allocated.get((t,r,c,k))
                        need(type(value)is int and value>=2,'every allowed internal coefficient allocated')
                    else:value=-1
                    values.append(value)
                row.append(values)
            matrix.append(row)
        state.append(matrix)
    need(set(allocated)==expected_keys,'actual allocation map equals all necessary support positions')
    return state,masks


def primitive_assignments(model,algebra,word,selectors,allocated,elements):
    assignments={}
    for gate,(u,v,labels)in zip(word,selectors):
        uu,vv,i,j=gate
        assignments.update({x:bool(uu&(1<<k))for k,x in enumerate(u)})
        assignments.update({x:bool(vv&(1<<k))for k,x in enumerate(v)})
        assignments.update({x:model.PAIRS[k]==(i,j)for k,x in enumerate(labels)})
    prefixes={t:algebra.replay(word[:t])for t,_,_,_ in allocated}
    for(t,r,c,k),variable in allocated.items():
        packed=sum(v<<(3*j)for j,v in enumerate(elements[k]))
        assignments[variable]=bool(prefixes[t][3*r+c]&(1<<algebra.index[packed]))
    return assignments


def extend(cnf,assignments):
    values={1:True,**assignments}
    def truth(lit):return values[abs(lit)]==(lit>0)
    for out,op,a,b in cnf.operations:
        need(out not in values,'unique topological extension variable')
        values[out]=(truth(a)and truth(b))if op=='and'else(truth(a)!=truth(b))
    failures=sum(not any(truth(x)for x in clause)for clause in cnf.clauses)
    return values,failures


def literal_capture_summary(cnf,n,support,allocated,metadata,data):
    return {'length':n,'support_bounds':support,'variables':cnf.variables,'clauses':len(cnf.clauses),
            'state_variables':len(allocated),'dag_operations':len(cnf.operations),
            'helper_calls':len(cnf.helper_calls),'q_and_parity_calls':len(cnf.xors_calls),
            'shift_calls':len(cnf.ors_calls),'transition_equalities':len(cnf.equalities),
            'cnf_bytes':len(data),'cnf_sha256':sha(data),
            'dag_canonical_sha256':sha(canonical(cnf.operations)),
            'helper_calls_canonical_sha256':sha(canonical(cnf.helper_calls)),
            'equalities_canonical_sha256':sha(canonical(cnf.equalities))}


def clause_counter(oracle,clauses):
    return Counter(tuple(sorted(c,key=lambda x:(abs(x),x)))for c in oracle.normalize_clauses(clauses))


def audit_trace(oracle,cnf,selectors,allocated,state,pullbacks):
    n=len(selectors)
    need(type(cnf.variables)is int and cnf.variables>=1,'legal declared variable range')
    need(all(type(lit)is int and lit!=0 and abs(lit)<=cnf.variables
             for clause in cnf.clauses for lit in clause),'every actual clause literal is a legal typed signed literal')
    states=set(allocated.values())
    choices={x for triple in selectors for part in triple for x in part}
    outputs=[row[0]for row in cnf.operations]
    need(len(states)==len(allocated)and len(choices)==12*n,'unique state/choice primary variables')
    need(not(states&choices)and len(outputs)==len(set(outputs)),'disjoint unique primary/gate variables')
    need(not((states|choices)&set(outputs))and states|choices|set(outputs)==set(range(2,cnf.variables+1)),
         'exact variable partition into states selectors and gate outputs')
    groups=tuple(frozenset(labels)for _,_,labels in selectors)
    forms={x:oracle.anf_var(x)for x in states|choices}
    forms[1]=oracle.anf_const(True)
    def get(lit):
        need(type(lit)is int and lit!=0 and abs(lit)<=cnf.variables,'legal signed literal')
        need(abs(lit)in forms,'topological auxiliary dependency')
        value=forms[abs(lit)]
        return oracle.anf_not(value)if lit<0 else value
    gates=[]
    operation_cache={}
    max_terms,max_degree=0,0
    for out,op,a,b in cnf.operations:
        need(type(out)is int and 2<=out<=cnf.variables and out not in forms,'unique legal gate output')
        left,right=get(a),get(b)
        if op=='and':
            value=oracle.anf_and(left,right,groups);gates.extend(oracle.and_clauses(a,b,out))
        else:
            need(op=='xor','declared gate kind')
            value=oracle.anf_xor(left,right);gates.extend(oracle.xor_clauses(a,b,out))
        forms[out]=value
        operation_cache[op,a,b]=value
        max_terms=max(max_terms,len(value));max_degree=max(max_degree,max(map(len,value),default=0))
    need(max_degree<=4,'onehot-quotient local DAG degree at most4')
    for op,a,b,out in cnf.helper_calls:
        key=op,a,b
        if key not in operation_cache:
            left,right=get(a),get(b)
            operation_cache[key]=oracle.anf_and(left,right,groups)if op=='and'else oracle.anf_xor(left,right)
        need(get(out)==operation_cache[key],'every actual constant/sign/cache helper call has correct ANF')
    extra=[]
    equal_index=0
    q_count=shift_count=delta_count=0
    call_lookup={(op,a,b):out for op,a,b,out in cnf.helper_calls}
    for t,(u,v,labels)in enumerate(selectors):
        parity_items,parity=cnf.xors_calls[t*505]
        need(len(parity_items)==3,'all scalar projector parity terms present')
        expected_parity=oracle.anf_xor(*(oracle.anf_and(get(a),get(b),groups)for a,b in zip(u,v)))
        need(get(parity)==expected_parity,'actual primary vTu=1 predicate')
        extra.append((parity,));extra.append(tuple(labels))
        extra.extend((-a,-b)for a,b in itertools.combinations(labels,2))
        for c in range(3):
            q_expected=[oracle.anf_xor(*(oracle.anf_and(get(v[r]),get(state[t][r][c][k]),groups)
                                          for r in range(3)))for k in range(168)]
            expected=oracle.expected_column([[get(x)for x in state[t][r][c]]for r in range(3)],
                                            [get(x)for x in u],[get(x)for x in v],
                                            [get(x)for x in labels],pullbacks,groups)
            q_literals=[]
            for k in range(168):
                items,out=cnf.xors_calls[t*505+1+c*168+k]
                need(len(items)==3 and get(out)==q_expected[k],'every actual q coefficient equals independent recurrence')
                q_literals.append(out);q_count+=1
            for k in range(168):
                items,shift=cnf.ors_calls[(t*3+c)*168+k]
                want_shift=oracle.anf_xor(*(oracle.anf_and(get(labels[g]),q_expected[pullbacks[g][k]],groups)
                                             for g in range(6)))
                need(len(items)==6 and get(shift)==want_shift,'every actual selected translation coefficient')
                shift_count+=1
                delta_key=('xor',q_literals[k],shift)
                need(delta_key in call_lookup,'actual q XOR shifted delta call present')
                need(get(call_lookup[delta_key])==oracle.anf_xor(q_expected[k],want_shift),'every actual delta coefficient')
                delta_count+=1
                for r in range(3):
                    lhs,rhs=cnf.equalities[equal_index]
                    need(lhs==state[t+1][r][c][k],'every next-state literal including full constant boundaries')
                    need(get(rhs)==expected[r][k],'every transition RHS equals independent full coefficient recurrence')
                    extra.extend(oracle.equality_clauses(lhs,rhs));equal_index+=1
    need(equal_index==len(cnf.equalities)==n*1512,'complete nine-entry168-coefficient transition coverage')
    # Literal1 is defined by an actual unit clause and must not be simplified away.
    need(cnf.clauses and cnf.clauses[0]==(1,),'actual defining constant-true unit')
    actual=clause_counter(oracle,cnf.clauses[1:]);actual[(1,)]+=1
    wanted=clause_counter(oracle,[*gates,*extra]);wanted[(1,)]+=1
    need(actual==wanted,'complete actual clause MULTISET equals independent gate/choice/equality schema')
    return {'semantic_helper_calls_checked':len(cnf.helper_calls),
            'full_transition_equalities_checked':equal_index,'q_coefficients_checked':q_count,
            'shift_coefficients_checked':shift_count,'delta_coefficients_checked':delta_count,
            'actual_clause_multiset_size':sum(actual.values()),
            'canonical_clause_multiset_sha256':sha(canonical([[list(k),v]for k,v in sorted(actual.items())])),
            'maximum_local_anf_terms':max_terms,'maximum_local_anf_degree':max_degree,
            'complete_variable_partition':True,'full_boundary_coefficients_per_end':1512}


def load_oracle(path):
    base=path.parent
    need(sha(path.read_bytes())==ORACLE_CODE_SHA256,'frozen independent core code hash')
    freeze_bytes=(base/'FREEZE.json').read_bytes()
    need(sha(freeze_bytes)==ORACLE_FREEZE_SHA256,'independent before-source freeze receipt')
    freeze=json.loads(freeze_bytes)
    for name in freeze['public_files']:
        data=(base/name).read_bytes();pin=freeze['files'][name]
        need(len(data)==pin['bytes']and sha(data)==pin['sha256'],'frozen public artifact '+name)
    raw=gzip.decompress((base/'fulltable.json.gz').read_bytes())
    need(sha(raw)==freeze['files']['fulltable.normal.json']['sha256'],'frozen decompressed table bytes')
    table=json.loads(raw)
    need(sha(canonical(table))==ORACLE_TABLE_SHA256,'frozen complete typed table canonical hash')
    spec=importlib.util.spec_from_file_location('independent_cnf_oracle',path)
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    need(canonical(oracle.selftest())==canonical(table),'recomputed independent full typed table matches frozen artifact')
    return oracle,{'code_sha256':ORACLE_CODE_SHA256,'freeze_sha256':ORACLE_FREEZE_SHA256,
                   'complete_typed_table_sha256':ORACLE_TABLE_SHA256,'counts':table['counts']}


def actual_assignment_controls(model,cm,exact,algebra,word,cnf,selectors,allocated,elements,support):
    assignments=primitive_assignments(model,algebra,word,selectors,allocated,elements)
    need(assignments==cm.word_assignments(word,selectors,allocated,elements),'adapter/source primitive assignment agreement')
    values,failures=extend(cnf,assignments)
    need(not failures,'known direct-nine canonical extension satisfies every actual clause')
    bad=list(word);bad[-1]=(bad[-1][0],bad[-1][1],0,1)
    need(bad!=word and algebra.replay(bad)!=algebra.endpoint(),'endpoint mutant is actually different in full group algebra')
    _,bad_failures=extend(cnf,primitive_assignments(model,algebra,bad,selectors,allocated,elements))
    need(bad_failures>0,'same actual formula rejects endpoint-failing word extension')
    return {'length':len(word),'support_bounds':support,'variables_assigned':len(values),
            'clauses_checked':len(cnf.clauses),'positive_failed_clauses':failures,
            'endpoint_mutant_failed_clauses':bad_failures,'mutant_word_uvij':bad}


def bounded_controls(oracle,model,cm,exact,algebra,elements,index):
    controls=[]
    # A complete assignment, not the source's canonical extension: deletion of
    # the backwards implication admits an auxiliary value inconsistent with AND.
    cnf=cm.CNF();a=cnf.variable();b=cnf.variable();z=cnf.both(a,b)
    forbidden={1:True,a:True,b:True,z:False}
    backwards=tuple(sorted((z,-a,-b),key=lambda x:(abs(x),x)))
    weak=[c for c in cnf.clauses if c!=backwards]
    need(len(weak)==len(cnf.clauses)-1,'actual backward AND clause found')
    need(oracle.clauses_hold(weak,forbidden)and not oracle.clauses_hold(cnf.clauses,forbidden),
         'deleted backwards clause admits forbidden AND assignment')
    controls.append({'name':'drop_actual_backward_AND_clause','removed_clause':list(backwards),
                     'forbidden_assignment':{str(k):v for k,v in forbidden.items()},'weak_accepts':True,'actual_accepts':False})
    # Exhaust source helpers and signed cache/fold paths on two primaries.
    cnf=trace_class(cm.CNF)();a=cnf.variable();b=cnf.variable()
    literals=(1,-1,a,-a,b,-b);calls=[]
    for kind in ('and','xor','or'):
        function={'and':cnf.both,'xor':cnf.xor,'or':cnf.either}[kind]
        for left,right in itertools.product(literals,repeat=2):calls.append((kind,left,right,function(left,right)))
    for aa,bb in itertools.product((False,True),repeat=2):
        values,failed=extend(cnf,{a:aa,b:bb});need(failed==0,'actual signed helper gate clauses extend')
        def truth(lit):return values[abs(lit)]==(lit>0)
        for kind,left,right,out in calls:
            x,y=truth(left),truth(right)
            want=(x and y)if kind=='and'else((x!=y)if kind=='xor'else(x or y))
            need(truth(out)==want,'signed source helper/cache/fold truth table')
    controls.append({'name':'source_signed_helper_cache_fold_truth_table','signed_input_pairs':36,
                     'helper_kinds':3,'primary_assignments':4,'evaluations':432,'status':'PASS'})
    # A short arbitrary endpoint uses the caller's full endpoint_columns path.
    small=[(1,1,0,1),(1,1,1,2)]
    columns=[exact.column(small,c)for c in range(3)]
    cnf,selectors,allocated,_,_=build_trace(cm,2,False,endpoint_columns=columns)
    assignment=primitive_assignments(model,algebra,small,selectors,allocated,elements)
    _,failed=extend(cnf,assignment);need(failed==0,'actual arbitrary full endpoint positive')
    original=cm.address_data
    right=[[index[product(h,g)]for h in elements]for g in oracle.LABELS]
    need(right!=[list(p)for p in oracle.PULLBACKS],'right translation control genuinely differs')
    def wrong_address_data():
        data=original();return (*data[:4],right)
    cm.address_data=wrong_address_data
    try:
        mutant,mselect,mallocated,_,_=build_trace(cm,2,False,endpoint_columns=columns)
    finally:cm.address_data=original
    _,wrong_failed=extend(mutant,primitive_assignments(model,algebra,small,mselect,mallocated,elements))
    need(wrong_failed>0,'actual right-translation mutation rejects noncommuting chronological positive')
    controls.append({'name':'actual_left_to_right_translation_source_calibration','word_uvij':small,
                     'correct_failed_clauses':failed,'wrong_failed_clauses':wrong_failed,
                     'scope':'temporary callable replacement; retained source unchanged'})
    # Full dirty third role restoration is a real endpoint obligation.
    dirty=[(4,4,0,1)];identity=((1,2,4),)*3
    dirty_columns=[exact.column(dirty,c)for c in range(3)]
    real,ss,aa,_,_=build_trace(cm,1,False,target=identity)
    _,dirty_failures=extend(real,primitive_assignments(model,algebra,dirty,ss,aa,elements))
    weak,ss,aa,_,_=build_trace(cm,1,False,target=identity,endpoint_columns=dirty_columns)
    _,weak_failures=extend(weak,primitive_assignments(model,algebra,dirty,ss,aa,elements))
    need(dirty_failures>0 and weak_failures==0,'changed dirty-role endpoint control discriminates')
    controls.append({'name':'dirty_third_role_endpoint_control','word_uvij':dirty,
                     'full_identity_endpoint_failed_clauses':dirty_failures,
                     'mutated_endpoint_failed_clauses':weak_failures,
                     'scope':'synthetic endpoint change, not an observed source bug'})
    return controls


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    here=Path(__file__).resolve().parent
    parser.add_argument('--source',type=Path,default=here/'source')
    parser.add_argument('--oracle-code',type=Path,default=here/'oracle.py')
    parser.add_argument('--expected',type=Path,default=here/'INTEGRATION-RESULT.json')
    parser.add_argument('--output',type=Path,help='explicit receipt regeneration; bypass stored-receipt comparison')
    args=parser.parse_args()
    model,cm,exact=load_source(args.source)
    oracle,oracle_receipt=load_oracle(args.oracle_code)
    elements,index,pairs,labels,pullbacks,distance=reference_address_data()
    need(elements==list(oracle.GROUP)and pairs==list(oracle.LABEL_COORDINATES)
         and labels==list(oracle.LABELS)and pullbacks==[list(p)for p in oracle.PULLBACKS],
         'literal group enumeration and all1008 translation rows match frozen independent core')
    balls=oracle.support_balls(9)
    need(all(distance[k]==next(t for t,ball in enumerate(balls)if k in ball)for k in range(168)),
         'all168 literal distances match frozen independent balls')
    source_elements,_,source_distance,_,source_permutations=cm.address_data()
    need(elements==source_elements and pairs==cm.PAIRS,'literal frame/label order equals actual source')
    need(all(source_distance[g]==distance[k]for k,g in enumerate(elements))and source_permutations==pullbacks,
         'actual source distances and all1008 pullbacks equal frozen independent reference')
    certificates={x['length']:x for x in json.loads((args.source/'CERTIFICATES.json').read_bytes())['certificates']}
    records=[];positives=[];algebra=model.Algebra()
    word=json.loads((args.source/'DIRECT_NINE.json').read_bytes())['word_uvij']
    need(algebra.replay(word)==algebra.endpoint(),'known source direct-nine full packed endpoint')
    # Bind the finite predecessor word through the frozen independent recurrence
    # and separate explicit convolution, not just through two reused source paths.
    dense=oracle.identity_state();prefix_hashes=[]
    for t in range(len(word)+1):
        packed=algebra.replay(word[:t])
        observed=[[[int(bool(packed[3*r+c]&(1<<algebra.index[sum(v<<(3*j)for j,v in enumerate(elements[k]))])))for k in range(168)]for c in range(3)]for r in range(3)]
        need(observed==dense,'actual packed direct-nine prefix equals independent full168-coefficient recurrence')
        need(all(exact.column(word[:t],c)[r]=={elements[k]for k in range(168)if dense[r][c][k]}
                 for c in range(3)for r in range(3)),'actual set replay direct-nine prefix equals independent recurrence')
        prefix_hashes.append(sha(canonical(dense)))
        if t<len(word):
            u,v,i,j=word[t];uu=[(u>>r)&1 for r in range(3)];vv=[(v>>r)&1 for r in range(3)]
            label=pairs.index((i,j))
            dense_next=oracle.transition_dense(dense,uu,vv,label)
            need(dense_next==oracle.transition_ring(dense,uu,vv,label),'independent recurrence/convolution agree on actual direct-nine prefix')
            dense=dense_next
    need(dense==oracle.endpoint_state(),'independent direct-nine full endpoint')
    full_action=exact.check(word)
    need(full_action['accepted']and full_action['basis_columns_checked']==504,'source independent regular-action504positive')
    with tempfile.TemporaryDirectory(prefix='cnf-source-audit-')as temporary:
        for n,support in [(n,True)for n in range(1,10)]+[(9,False)]:
            cnf,selectors,allocated,actual_elements,metadata=build_trace(cm,n,support)
            need(actual_elements==elements,'every actual build uses frozen independent group order')
            state,masks=state_literals(n,allocated,elements,index,distance,exact.TARGET,support)
            if support:
                need(masks==[[set(x)for x in cut]for cut in oracle.support_masks(n)],
                     'all actual necessary support masks match frozen independent reference')
            need(len(cnf.equalities)==n*1512,'every transition equality present')
            need(len(cnf.xors_calls)==n*505 and len(cnf.ors_calls)==n*504,'all q/parity/shift call sites present')
            need(metadata['support_counts']==[[len(x)for x in row]for row in masks],'actual support counts')
            path=Path(temporary)/(str(n)+'-'+str(support)+'.cnf');cnf.write(path);data=path.read_bytes()
            record=literal_capture_summary(cnf,n,support,allocated,metadata,data)
            record['semantic_audit']=audit_trace(oracle,cnf,selectors,allocated,state,pullbacks)
            record['matches_authenticated_predecessor_certificate_declarations']=None
            if support and n in certificates:
                certificate=certificates[n]
                need(sha(data)==certificate['cnf_sha256']and len(data)==certificate['cnf_bytes']
                     and cnf.variables==certificate['variables']and len(cnf.clauses)==certificate['clauses'],
                     'regenerated CNF matches authenticated certificate declared counts/hash '+str(n))
                record['matches_authenticated_predecessor_certificate_declarations']=True
            if n==9:
                positives.append(actual_assignment_controls(model,cm,exact,algebra,word,cnf,selectors,allocated,elements,support))
            records.append(record)
    controls=bounded_controls(oracle,model,cm,exact,algebra,elements,index)
    result={'schema':'b4-actual-direct-cnf-equivalence-integration-v1','status':'PASS',
            'source_head':HEAD,'source_sha256':PINS,'independent_core':oracle_receipt,
            'published_cli_length_domain':list(range(1,10)),'instances':records,
            'full_transition_equalities_checked':sum(r['semantic_audit']['full_transition_equalities_checked']for r in records),
            'actual_clause_multiset_entries_checked':sum(r['semantic_audit']['actual_clause_multiset_size']for r in records),
            'source_helpers_reused':True,'instrumentation':'delegating subclass records lazy original helper calls and equality sites',
            'direct_nine_actual_full_action':full_action,'direct_nine_full_coefficient_prefix_sha256':prefix_hashes,
            'actual_cnf_positives_and_endpoint_mutants':positives,
            'controls':controls,'sat_solver_calls':0,'rup_replay':False,'minimum_claim':None,
            'scope':'Full direct-CNF schema and actual CLI1..9 plus unpruned9 binding; normalized paid factors only; no SAT/UNSAT/RUP/minimum certification.'}
    payload=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:args.output.write_text(payload)
    else:need(canonical(json.loads(args.expected.read_bytes()))==canonical(result),'stored typed integration receipt mismatch')
    print(payload,end='')


if __name__=='__main__':main()
