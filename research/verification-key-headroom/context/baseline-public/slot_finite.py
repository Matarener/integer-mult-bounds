"""Inherited complete key/table/entry tests plus getter/fallback controls."""
import importlib.util,json,sys
from fractions import Fraction as F
import compact_finite
from frozen import baseline,require
from compact_finite import types_of
import fraction_table as table
import slot_binding as binding


def main():
    inherited=compact_finite.main();controls=[]
    token=binding.bind(strict=True);require(binding.fresh(token),'known getter binding')
    numerator=F.__dict__['numerator'];slot=F.__dict__['_numerator']
    F.numerator=property(lambda self:self._numerator+1)
    try:require(binding.bind() is None and not binding.fresh(token),'getter replacement invalidates')
    finally:F.numerator=numerator
    controls.append('changed-getter-invalidates')
    code=numerator.fget.__code__;numerator.fget.__code__=code.replace(co_consts=code.co_consts+('drift',))
    try:require(binding.bind() is None and not binding.fresh(token),'live getter code invalidates')
    finally:numerator.fget.__code__=code
    controls.append('changed-live-getter-code')
    calls=[]
    class Foreign:
        def __get__(self,*args):calls.append(True);raise RuntimeError('foreign descriptor must not run')
    F._numerator=Foreign()
    try:require(binding.bind() is None and not binding.fresh(token) and not calls,'foreign slot rejected without invocation')
    finally:F._numerator=slot
    controls.append('foreign-slot-probe-is-pure')
    F.__getattribute__=lambda self,name:object.__getattribute__(self,name)
    try:require(binding.bind() is None and not binding.fresh(token),'custom attribute lookup rejected')
    finally:del F.__getattribute__
    controls.append('changed-attribute-lookup')
    F.__getattr__=None
    try:require(binding.bind() is None and not binding.fresh(token),'present None getattr rejected')
    finally:del F.__getattr__
    controls.append('missing-attribute-handler-presence')
    require(binding.fresh(token),'runtime fully restored')
    controls.append('binding-restored')
    with baseline() as package:
        sys.path.insert(0,str(package));spec=importlib.util.spec_from_file_location('slot_bundle',package/'source.py')
        source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
        with source.baseline() as p:
            spec=importlib.util.spec_from_file_location('slot_finite_source',p/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
            with v.source() as (_,_,ref):
                original=ref.error_trace
                fixture=(dict(public=4,owned_fields=0,program=[['INIT',0,0],['INIT',1,0],['ADD',2,0,1,0],['ADD',3,1,1,0]]),[(F(1),F(2)),(F(3),F(5)),(F(7),F(11)),(F(13),F(17))],{'INIT'})
                fast=table.derive(ref);a=fast(*fixture);b=original(*fixture)
                require(a==b and types_of(a)==types_of(b) and fast.compacted_selected() is True,'slot path used with all outputs preserved')
                controls.append('slot-path-selected')
                getter_calls=[]
                def observed_getter(self):
                    getter_calls.append(True);return self._numerator
                F.numerator=property(observed_getter)
                try:
                    a=fast(*fixture);count_a=len(getter_calls);getter_calls.clear()
                    b=original(*fixture);count_b=len(getter_calls)
                    require(a==b and count_a==count_b and fast.compacted_selected() is False,'post-derive getter drift uses literal source and same calls')
                finally:F.numerator=numerator
                controls.append('post-derive-getter-drift-literal-fallback')
                uninitialized=object.__new__(F)
                word=dict(public=1,owned_fields=0,program=[]);weights=[(uninitialized,F(1))]
                fast=table.derive(ref)
                require(fast(word,weights,set())==original(word,weights,set()) and fast.compacted_selected() is False,'unused malformed Fraction does not introduce an exception')
                controls.append('uninitialized-unused-weight-fallback')
                class ForeignInteger:
                    def __hash__(self):raise RuntimeError('foreign key hash must not run')
                corrupt=object.__new__(F);corrupt._numerator=ForeignInteger();corrupt._denominator=1
                weights=[(corrupt,F(1))]
                require(fast(word,weights,set())==original(word,weights,set()) and fast.compacted_selected() is False,'corrupt unused slot values do not run custom hash')
                controls.append('foreign-slot-value-fallback')
    result=dict(status='PASS_SLOT_KEY_FINITE_ONLY',inherited=inherited,new_controls=controls,new_control_count=len(controls),all_coverage_preserved=True)
    print(json.dumps(result,sort_keys=True));return result

if __name__=='__main__':main()
