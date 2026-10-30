"""All unchanged predecessor finite coverage plus entry/fallback controls."""
from copy import deepcopy
import importlib.util
import json
import sys
from fractions import Fraction as F
import fraction_table as table
import parent_finite
from parent_finite import types_of,fixtures
from frozen import baseline,require


def main():
    inherited=parent_finite.main()
    controls=[]
    cases=list(fixtures())
    base=cases[0]
    require(table.certified_domain(*base),'ordinary fixture certified')
    require(all(table.certified_domain(*c) for c in cases),'all inherited fixtures certified')
    controls.append('all-241-fixtures-take-certified-domain')
    class DictSubclass(dict):
        def __getitem__(self,key):
            log.append(('word-get',key));return super().__getitem__(key)
    class ListSubclass(list):
        def __iter__(self):
            log.append('list-iter');return super().__iter__()
        def __getitem__(self,key):
            log.append(('list-get',key));return super().__getitem__(key)
    class TupleSubclass(tuple):
        def __iter__(self):
            log.append('tuple-iter');return super().__iter__()
        def __getitem__(self,key):
            log.append(('tuple-get',key));return super().__getitem__(key)
    class SetSubclass(set):
        def __contains__(self,key):
            log.append(('set-contains',key));return super().__contains__(key)
    class FractionSubclass(F):
        pass
    log=[]
    bad_domains=[]
    def changed_word(key,value):
        w=deepcopy(base[0]);w[key]=value;return w,deepcopy(base[1]),set(base[2])
    bad_domains.append(('dict-subclass',(DictSubclass(base[0]),deepcopy(base[1]),set(base[2]))))
    bad_domains.append(('program-subclass',changed_word('program',ListSubclass(base[0]['program']))))
    bad_domains.append(('event-subclass',changed_word('program',[TupleSubclass(e) for e in base[0]['program']])) )
    bad_domains.append(('weights-subclass',(deepcopy(base[0]),ListSubclass(base[1]),set(base[2]))))
    bad_domains.append(('row-subclass',(deepcopy(base[0]),[TupleSubclass(r) for r in base[1]],set(base[2]))))
    bad_domains.append(('rounded-subclass',(deepcopy(base[0]),deepcopy(base[1]),SetSubclass(base[2]))))
    bad_domains.append(('Fraction-subclass',(deepcopy(base[0]),[(FractionSubclass(a),c) for a,c in base[1]],set(base[2]))))
    bad_domains.append(('integer-weights',(deepcopy(base[0]),[(1,2)]*len(base[1]),set(base[2]))))
    bad_domains.append(('boolean-public',changed_word('public',True)))
    for label,c in bad_domains:
        log.clear();require(not table.certified_domain(*c),'fallback domain '+label)
        require(not log,'gate invokes no custom methods '+label)
    controls.append('subtypes-and-foreign-types-fall-back-without-custom-methods')
    class HostileMeta(type):
        def __eq__(cls,other):
            log.append('metaclass-equality');return False
    class Foreign(metaclass=HostileMeta):pass
    for label,c in [('metaclass-container',(deepcopy(base[0]),Foreign(),set(base[2]))),('metaclass-scalar',changed_word('program',[['ADD',0,1,Foreign(),0]]))]:
        log.clear();require(not table.certified_domain(*c),'foreign metaclass falls back')
        require(not log,'no foreign metaclass equality methods')
        controls.append(label)
    with baseline() as package:
        sys.path.insert(0,str(package))
        source_spec=importlib.util.spec_from_file_location('type_gate_additional_bundle',package/'source.py')
        source=importlib.util.module_from_spec(source_spec);source_spec.loader.exec_module(source)
        with source.baseline() as p:
            spec=importlib.util.spec_from_file_location('type_gate_finite_source',p/'verify.py')
            v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
            with v.source() as (_,_,ref):
                old=ref.error_trace;fast=table.derive(ref)
                for label,c in bad_domains:
                    outcomes=[]
                    for fn in (old,fast):
                        log.clear()
                        try:
                            value=fn(*c);outcome=('value',value,types_of(value))
                        except (IndexError,ValueError,TypeError,KeyError) as e:
                            outcome=('error',type(e).__name__,str(e))
                        outcomes.append((outcome,list(log)))
                    require(outcomes[0]==outcomes[1],'original outcome and custom-method order '+label)
                    controls.append('original-fallback-'+label)
                # Audit the invariant on a representative complete mixed-operation
                # trace and dyadic cancellation/large-rational fixtures. This extra
                # checking exists only in this finite control, never in timing runs.
                normal=table.Contributions
                checked_calls=[0]
                class Checked(normal):
                    def _certified_step(self,*operands):
                        require(all(type(x) is F for x in operands),'certified operands exact Fraction')
                        checked_calls[0]+=1
                        out=super()._certified_step(*operands)
                        require(all(type(x) is F for x in out),'certified results exact Fraction')
                        return out
                table.Contributions=Checked
                try:
                    checked=table.derive(ref)
                    for c in [base,cases[71],cases[142],cases[239]]:
                        require(checked(*c)==old(*c),'inductive type instrumentation preserves values')
                finally:table.Contributions=normal
                require(checked_calls[0]>0,'certified path actually executed')
                controls.append('exact-internal-type-preservation-at-certified-updates')
                for label,c in [
                    ('missing-weight',(dict(public=2,owned_fields=0,program=[['ADD',0,1,1,0]]),[],{'ADD'})),
                    ('bad-role',(dict(public=2,owned_fields=0,program=[['ADD',99,0,1,0]]),[(F(1),F(1))],{'ADD'})),
                    ('bad-scalar',(dict(public=2,owned_fields=0,program=[['ADD',0,1,'bad',0]]),[(F(1),F(1))],{'ADD'})),
                    ('short-event',(dict(public=2,owned_fields=0,program=[['ADD']]),[(F(1),F(1))],{'ADD'}))]:
                    outcomes=[]
                    for fn in (old,fast):
                        try:fn(*c)
                        except (IndexError,ValueError,TypeError) as e:outcomes.append((type(e).__name__,str(e)))
                        else:outcomes.append(('no-error',None))
                    require(outcomes[0]==outcomes[1],'same malformed-input outcome '+label)
                    controls.append('malformed-outcome-'+label)
    # Invalidation if a table is explicitly certified a second time.
    c=table.Contributions(2);c.certify(*base)
    require(c.certified,'entry selected certified path')
    foreign=(deepcopy(base[0]),[(1,2)]*len(base[1]),set(base[2]))
    c.certify(*foreign);require(not c.certified,'recertification removes fast path')
    require(c.step(F(0),F(1),F(1),1,2)==c.compute(F(0),F(1),F(1),1,2) and c.bypasses==1,'recertified fallback preserves non-Fraction operands')
    controls.append('recertification-invalidates-certified-method')
    c=table.Contributions(0);c.certify(*base)
    require(not c.certified,'disabled table stays checked');controls.append('disabled-capacity-not-certified')
    result=dict(status='PASS_TYPE_GATE_FINITE_FEASIBILITY',inherited=inherited,new_controls=controls,new_control_count=len(controls),all_coverage_preserved=True)
    print(json.dumps(result,sort_keys=True));return result

if __name__=='__main__':main()
