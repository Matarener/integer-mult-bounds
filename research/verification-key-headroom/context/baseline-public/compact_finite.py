"""All inherited coverage plus token, q-context, collision and FIFO controls."""
import importlib.util
import json
import sys
from fractions import Fraction as F
import entry_finite
import entry_parent as entry
from entry_finite import fixtures,types_of
from frozen import baseline,require
import fraction_table as table


def main():
    inherited=entry_finite.main();controls=[]
    weights=[(F(1),F(2)),(F(3),F(5)),(F(2,2),F(4,2))]
    tokens=table.weight_tokens(weights)
    require(tokens==[0,1,0],'canonical equal pairs share a token')
    controls.append('canonical-full-pair-tokens')
    modulus=sys.hash_info.modulus
    collision=[(F(0),F(1)),(F(modulus),F(1))]
    keys=lambda w:(w[0].numerator,w[0].denominator,w[1].numerator,w[1].denominator)
    require(hash(keys(collision[0]))==hash(keys(collision[1])) and keys(collision[0])!=keys(collision[1]),'real canonical hash collision')
    require(table.weight_tokens(collision)==[0,1],'full equality after hash collision')
    controls.append('weight-token-hash-collision')
    require(table.weight_tokens(weights,1) is None,'context overflow rejects compression')
    require(table.weight_tokens([],0)==[],'empty zero-capacity context')
    controls.append('bounded-context-overflow')
    # Same exact equality relation and global FIFO sequence at each capacity.
    word=dict(public=1,owned_fields=0,program=[])
    for capacity in (1,2,16):
        old=entry.Contributions(capacity);old.certify(word,weights,set())
        new=table.CompactContributions(capacity,weights,tokens)
        for q in (F(1),F(-1),F(2),F(1,2),F(2,4),F(1)):
            step=new.event(q)
            for index,i in enumerate((0,1,2,0,2,1,0,1,2)):
                a,b=F(index%2),F((index%3)-1)
                require(step(a,b,i)==old.step(a,q,b,*weights[i]),'same exact contribution')
                require(new.statistics()==old.statistics(),'same complete FIFO/counters')
    controls.append('event-q-canonical-equality-and-FIFO-counters')
    with baseline() as package:
        sys.path.insert(0,str(package))
        spec=importlib.util.spec_from_file_location('compact_bundle',package/'source.py')
        source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
        with source.baseline() as p:
            spec=importlib.util.spec_from_file_location('compact_finite_source',p/'verify.py')
            v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
            with v.source() as (_,_,ref):
                original=ref.error_trace;fast=table.derive(ref);parent=entry.derive(ref)
                for index,c in enumerate(fixtures()):
                    if index in (0,23,71,142,200,239):
                        a=parent(*c);b=fast(*c)
                        require(a==b and types_of(a)==types_of(b),'complete parent/compact trace types')
                        require(fast.compacted_selected() is True,'compact route actually executed')
                        require(parent.statistics()==fast.statistics(),'full finite actual counter sequence')
                controls.append('six-complete-trace-counter-and-type-comparisons')
                fixture=(dict(public=4,owned_fields=0,program=[['INIT',0,0],['INIT',1,0],['ADD',2,0,1,0],['ADD',3,1,1,0]]),[(F(1),F(2)),(F(3),F(5)),(F(7),F(11)),(F(13),F(17))],{'INIT'})
                require(fast(*fixture)==original(*fixture),'source weights vary by i, not event')
                controls.append('source-site-weight-ownership')
                factory=table.weight_tokens
                table.weight_tokens=lambda w:[0]*len(w)
                try:require(table.derive(ref)(*fixture)!=original(*fixture),'wrong token merges rejected')
                finally:table.weight_tokens=factory
                controls.append('wrong-token-alias-detected')
                table.weight_tokens=lambda w:factory(w,1)
                try:
                    fallback=table.derive(ref)
                    require(fallback(*fixture)==original(*fixture) and fallback.compacted_selected() is False,'whole-call overflow fallback')
                finally:table.weight_tokens=factory
                controls.append('overflow-fallback-preserves-original')
                # Reusing token numbers in a later trace cannot reuse an answer.
                a=fast(*fixture);counts=fast.statistics();changed=(fixture[0],list(reversed(fixture[1])),fixture[2])
                require(fast(*changed)==original(*changed),'new trace tokens independent')
                require(fast(*fixture)==a and fast.statistics()==counts,'fresh table on each call')
                controls.append('fresh-token-and-cache-lifetimes')
    result=dict(status='PASS_COMPACT_KEY_FINITE_ONLY',inherited=inherited,new_controls=controls,new_control_count=len(controls),all_coverage_preserved=True)
    print(json.dumps(result,sort_keys=True));return result

if __name__=='__main__':main()
