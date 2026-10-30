"""Checked package entry: fresh source, exact parameter widths and compatible rows.

This is a new package wrapper, not a patch to SelectedBinding.check_stock.
The named large-prime constructor replaces only exhaustive primality checking
by an exact Lucas-Lehmer certificate; every codebook method is retained.
All guard work here is host finite arithmetic, with no fixed-tape tariff claim.
"""
from dataclasses import dataclass, replace
from collections import Counter
from types import SimpleNamespace
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import types
import compiler
import numerical

HERE=Path(__file__).resolve().parent
Q127=2**127-1


def need(ok,message):
    if not ok:raise ValueError(message)


def prime_certificate(q, exponent=127):
    need(exponent==127 and q==2**exponent-1,'exact named Mersenne prime certificate')
    # 127 is prime: explicit trial division up to its square root.
    need(all(127%d for d in range(2,12)),'prime Mersenne exponent')
    residue=4
    for _ in range(exponent-2):residue=(residue*residue-2)%q
    need(residue==0,'Lucas-Lehmer residue')
    return {'q':str(q),'exponent':127,'modular_square_subtract_steps':125,'residue':0}


def load_certified(variant='D',q=Q127):
    """Exact retained compiler with a named, authenticated primality adapter."""
    certificate=prime_certificate(q)
    compiler.runtime()
    original=sys.modules['low_codes']
    text=Path(original.__file__).read_text()
    old='all(q % p for p in range(2, q))'
    need(text.count(old)==1,'one exact exhaustive primality guard')
    patched=text.replace(old,'certified_prime(q)')
    module=types.ModuleType('low_codes')
    module.__file__=original.__file__
    guard_evaluations=[]
    def certified_prime(p):
        result=prime_certificate(p)
        guard_evaluations.append(result)
        return True
    module.certified_prime=certified_prime
    # Executing an authenticated copy changes one guard; frozen bytes stay put.
    sys.modules['low_codes']=module
    try:
        exec(compile(patched,'<exact named-prime LowCodes adapter>','exec'),module.__dict__)
        cat,top=compiler.load(variant,q)
        base_identity=cat.source_identity
        cat.source_identity=compiler.digest({
            'schema':'r437-exact-prime-admission-v1',
            'base_compiler_identity':base_identity,
            'admission_source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'retained_low_codes_sha256':sha256(text.encode()).hexdigest(),
            'adapted_low_codes_sha256':sha256(patched.encode()).hexdigest(),
            'prime_certificate':certificate,
        })
    finally:sys.modules['low_codes']=original
    cat.admission_provenance={'base_compiler_identity':base_identity,
        'retained_low_codes_sha256':sha256(text.encode()).hexdigest(),
        'adapted_low_codes_sha256':sha256(patched.encode()).hexdigest(),
        'prime_certificate':certificate,
        'constructor_certificate_evaluations':1+len(guard_evaluations),
        'constructor_modular_square_subtract_steps':125*(1+len(guard_evaluations)),
        'source_identity':cat.source_identity}
    return cat,top


def authenticate_certified(cat):
    """Recompute the wrapper binding; provenance is evidence, not authority."""
    import low_codes
    original=Path(low_codes.__file__).read_text()
    old='all(q % p for p in range(2, q))'
    need(original.count(old)==1,'retained exact primality-guard source')
    adapted=original.replace(old,'certified_prime(q)')
    certificate=prime_certificate(cat.q)
    base=compiler.codebook_identity(cat)
    retained_sha=sha256(original.encode()).hexdigest()
    adapted_sha=sha256(adapted.encode()).hexdigest()
    expected=compiler.digest({
        'schema':'r437-exact-prime-admission-v1',
        'base_compiler_identity':base,
        'admission_source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'retained_low_codes_sha256':retained_sha,
        'adapted_low_codes_sha256':adapted_sha,
        'prime_certificate':certificate,
    })
    need(cat.source_identity==expected,'recomputed certified source identity')
    provenance=getattr(cat,'admission_provenance',{})
    for key,value in [('base_compiler_identity',base),('retained_low_codes_sha256',retained_sha),
                      ('adapted_low_codes_sha256',adapted_sha),('prime_certificate',certificate),
                      ('source_identity',expected)]:
        need(provenance.get(key)==value,'recomputed constructor provenance '+key)
    need(cat.codes.q==cat.q and cat.codes.dimension==cat.dimension==64,'actual codec field/dimension context')
    return expected


def admitted_compile_node(topology,binding,mode=0):
    """Join the new source tag to the actual explicit-replica macro emitter."""
    need(binding.catalogue is topology.catalogue,'admitted macro source/native context')
    need(getattr(binding.specifications,'catalogue',None) is binding.catalogue,
         'admitted macro Specifications context')
    authenticate_certified(binding.catalogue)
    return compiler.caller_emitter().compile_node(topology,binding,mode)


def regional_emitter(cat,top,domain):
    """One actual native IDLE, full dimension, one low class, actual Cursor."""
    from macro_binding import SelectedBinding
    from catalogue import Specifications
    identifier=next(i for i,r in enumerate(cat.requests) if r.kind=='IDLE' and r.base.rank==14)
    request=cat.requests[identifier]
    region=SimpleNamespace(catalogue=cat,replicas=32,
        schedule=({'kind':'idle','idx':request.stage},),
        idle_identifiers=lambda child,replica:(identifier,) if (child,replica)==(request.stage,request.replica) else (),
        idle_family=top.idle_family)
    specs=Specifications(cat);binding=SelectedBinding(specs)
    low=tuple(tuple(int(i==j) for j in range(64)) for i in range(64))
    handle=compiler.source_handle(cat,identifier,False,low)
    try:compiler.compile_node(region,binding)
    except ValueError:old_rejected=True
    else:raise ValueError('old compiler silently accepted wrapped source')
    original=cat.low_classes;cat.low_classes=lambda:iter((low,))
    try:
        emitted,entry=checked_entry(cat,specs,handle,domain,
            lambda:admitted_compile_node(region,binding),mode='numerical',
            expected_key=handle.request_key,expected_common=False)
    finally:cat.low_classes=original
    residuals=[r[2] for r in emitted.operations if r[0]=='residual_begin']
    need(len(residuals)==1 and residuals[0].identifier==identifier and not residuals[0].common,
         'single actual native IDLE source')
    tags=Counter(r[0] for r in emitted.operations)
    need(tags['gather']==tags['scatter']==tags['clear']==1,'regional gather/return/clear')
    need(emitted.operations[0]==('node',) and emitted.operations[-1]==('return',),'regional terminal control')
    identity=cat.source_identity;cat.source_identity='0'*64
    try:
        try:admitted_compile_node(region,binding)
        except ValueError:context_rejected=True
        else:raise ValueError('mutated wrapped compiler source admitted')
    finally:cat.source_identity=identity
    provenance=dict(cat.admission_provenance)
    cat.admission_provenance=dict(provenance,base_compiler_identity='0'*64)
    try:
        try:admitted_compile_node(region,binding)
        except ValueError:provenance_rejected=True
        else:raise ValueError('forged constructor provenance admitted')
    finally:cat.admission_provenance=provenance
    return {'entry':entry,'request':identifier,'rank':14,'dimension':64,
        'low_classes_executed':1,'native_specification_good':specs[handle.code].good,
        'operations':dict(sorted(tags.items())),
        'old_compiler_wrapped_identity_rejected':old_rejected,
        'mutated_wrapped_context_rejected':context_rejected,
        'forged_provenance_rejected':provenance_rejected,
        'emitter_certificate_modular_square_subtract_steps':125,
        'scope':'Actual SelectedBinding and Cursor macro emission at admitted q127; one native IDLE, one GL64 low class. No packet/tape payload execution.'}


@dataclass(frozen=True)
class RootDomain:
    e:int
    n:int
    w:int
    h:int
    L:int
    I:int
    Q:int
    rows:int


def integer_receipt(n):
    need(isinstance(n,int) and n>=0,'nonnegative encoded integer receipt')
    packed=n.to_bytes(max(1,(n.bit_length()+7)//8),'big')
    return {'bit_length':n.bit_length(),'big_endian_sha256':sha256(packed).hexdigest()}


def checked_entry(cat,specifications,handle,domain,callback,*,mode,
                  expected_key,expected_common):
    """Validate BEFORE a zero-argument continuation may prepare/consume data.

    `domain.rows` is a host parameter certificate, not evidence that the giant
    row payload was materialized. Semantic mode checks finite fixtures but
    cannot set numerical_admitted. The continuation owns actual execution.
    """
    need(mode in ('numerical','semantic'),'explicit entry domain')
    need(isinstance(domain,RootDomain),'typed original-root domain')
    need(isinstance(handle,compiler.SourceHandle),'typed fresh source handle')
    # The fresh identity authenticates the algorithm and source bytes. Check
    # the expected boundary too: another valid code is not this caller request.
    need(handle.identity==cat.source_identity,'fresh source codebook identity')
    if mode=='semantic':
        need(cat.source_identity==compiler.codebook_identity(cat),'current semantic compiler source identity')
    need(tuple(handle.request_key)==tuple(expected_key),'expected caller request identity')
    identifier,common,_low=cat.codes.decode(handle.code)
    need(common is expected_common,'expected common/native source view')
    need(cat.requests[identifier].key==tuple(expected_key),'decoded source request identity')
    spec=compiler.resolve_handle(cat,specifications,handle)
    need(spec.template.rank==cat.requests[identifier].base.rank,'source/native rank agreement')
    need(domain.e>=64 and 1<=domain.n<=domain.e and domain.w>=1 and domain.h>=0,'root/descendant parameter domain')
    need(domain.L==(cat.q**domain.w).bit_length()+1,'actual canonical residue width')
    need(domain.I==domain.e.bit_length()+1,'actual canonical root-index width')
    need(domain.Q==cat.codes.bits==(2*len(cat.requests)*numerical.gl_order(cat.q)-1).bit_length(),'actual complete codebook width')
    quotient=numerical.check_stock_rows(domain.rows,domain.n,cat.q,domain.w)
    if mode=='numerical':
        need(domain.n==domain.e and domain.h==0,'executable original-root entry; descendant path certificate required')
        # The only large-prime executable certificate supported by this package.
        need(getattr(cat,'admission_provenance',None) is not None,'certified prime source constructor')
        authenticate_certified(cat)
        numerical.check_root_domain(domain.e,domain.n,domain.w,domain.h,cat.q,domain.L,domain.I,domain.Q)
        numerical.check_fallback(cat.q,[spec.template.rank])
    value=callback()
    return value,{'mode':mode,'numerical_admitted':mode=='numerical',
        'source_identity':cat.source_identity,'request':identifier,'request_key':list(expected_key),
        'common':common,'rank':spec.template.rank,'q':str(cat.q),
        'domain':{k:getattr(domain,k) for k in ('e','n','w','h','L','I','Q')},
        'compatible_rows':integer_receipt(domain.rows),'row_multiplier':integer_receipt(quotient),
        'stock_certificate_scope':'original root' if mode=='numerical' else 'local semantic rows; no ancestor stock certificate',
        'guard_before_continuation':True,
        'entry_certificate_modular_square_subtract_steps':125 if mode=='numerical' else 0,
        'guard_implementation':'host finite arithmetic; exact source/parameter guard, physical encoded guard tariff open',
        'production_payload_execution':False}


def run():
    cat,top=load_certified()
    rt=compiler.runtime();specs=rt.catalogue.Specifications(cat)
    source=compiler.early_source87(cat,top,0,0)
    low=tuple(tuple(int(i==j) for j in range(64)) for i in range(64))
    handle=compiler.source_handle(cat,source['identifier'],False,low)
    domain=RootDomain(64,64,2,0,(cat.q**2).bit_length()+1,(64).bit_length()+1,
                      cat.codes.bits,numerical.stock_unit(cat.q,2))
    reached=[]
    def continuation():
        spec=compiler.resolve_handle(cat,specs,handle)
        need(spec.good and spec.template.rank==2,'actual admitted SOURCE87 good native specification')
        preparation=rt.catalogue.oracle.reduce_rational(spec.template.preparation,cat.q)
        inverse=rt.catalogue.oracle.inverse(preparation,cat.q)
        product=rt.catalogue.oracle.multiply(preparation,inverse,cat.q)
        need(tuple(map(tuple,product))==low,'actual native preparation inverse over admitted field')
        reached.append('actual source specification consumed')
        return {'good':spec.good,'rank':spec.template.rank,'specification_bound':True,
            'native_preparation_sha256':compiler.digest(preparation),
            'native_preparation_inverse_sha256':compiler.digest(inverse),
            'preparation_inverse_product_is_identity':True,
            'literal_source_code':integer_receipt(handle.code)}
    value,receipt=checked_entry(cat,specs,handle,domain,continuation,mode='numerical',
        expected_key=handle.request_key,expected_common=False)
    need(len(reached)==1,'single checked continuation')
    rejected=[]
    def reject(name,action):
        before=len(reached)
        try:action()
        except (ValueError,KeyError):pass
        else:raise ValueError('mutation admitted: '+name)
        need(len(reached)==before,'rejected gate must not delegate')
        rejected.append(name)
    def enter(h=handle,d=domain,sp=specs,expected=handle.request_key,view=False):
        return checked_entry(cat,sp,h,d,continuation,mode='numerical',expected_key=expected,expected_common=view)
    reject('stale_codebook_handle',lambda:enter(h=replace(handle,identity='0'*64)))
    reject('wrong_prime_certificate',lambda:prime_certificate(cat.q-2))
    reject('composite_named_parameter',lambda:load_certified(q=9))
    from low_codes import LowCodes
    reject('retained_constructor_composite_control',lambda:LowCodes(9,2,1))
    reject('wrong_common_native_view',lambda:enter(view=True))
    reject('wrong_caller_request_key',lambda:enter(expected=('MOVE',0,1,source['position'])))
    other=compiler.early_source87(cat,top,0,1)
    wrong_code=cat.codes.encode(other['identifier'],False,low)
    reject('wrong_replica_code_with_original_key',lambda:enter(h=replace(handle,code=wrong_code)))
    reject('mismatched_specifications_context',lambda:enter(sp={}))
    reject('untyped_integer_source',lambda:enter(h=handle.code))
    reject('insufficient_stock',lambda:enter(d=replace(domain,rows=1)))
    reject('large_but_incompatible_stock',lambda:enter(d=replace(domain,rows=domain.rows+1)))
    reject('undersized_residue_width',lambda:enter(d=replace(domain,L=1)))
    reject('padded_residue_width',lambda:enter(d=replace(domain,L=domain.L+1)))
    reject('undersized_source_width',lambda:enter(d=replace(domain,Q=1)))
    reject('wrong_root_index_width',lambda:enter(d=replace(domain,I=domain.I+1)))
    reject('wrong_root_precision',lambda:enter(d=replace(domain,w=1,L=cat.q.bit_length()+1,rows=numerical.stock_unit(cat.q,1))))
    reject('unrelated_history',lambda:enter(d=replace(domain,h=999)))
    reject('descendant_without_root_path_certificate',lambda:enter(d=replace(domain,e=2048,h=1,I=13)))
    # Actual retained small-prime constructor and fresh handle: cross-prime
    # rejection is against a real q=3 context, not an invented digest string.
    small,small_top=compiler.load('D',3)
    small_source=compiler.early_source87(small,small_top,0,0)
    small_handle=compiler.source_handle(small,small_source['identifier'],False,low)
    reject('actual_q3_cross_prime_handle',lambda:enter(h=small_handle))
    small_specs=rt.catalogue.Specifications(small)
    reject('actual_cross_prime_specifications_context',lambda:enter(sp=small_specs))
    fixture=RootDomain(2048,64,1,1,3,13,small.codes.bits,numerical.stock_unit(3,1))
    _,semantic=checked_entry(small,small_specs,small_handle,fixture,lambda:None,
        mode='semantic',expected_key=small_handle.request_key,expected_common=False)
    try:checked_entry(small,small_specs,small_handle,fixture,lambda:None,
        mode='numerical',expected_key=small_handle.request_key,expected_common=False)
    except ValueError:rejected.append('semantic_fixture_is_not_numerically_admitted')
    else:raise ValueError('q3 fixture numerically admitted')
    regional=regional_emitter(cat,top,domain)
    return {'status':'PASS_CHECKED_SOURCE_PARAMETER_ENTRY','admitted_entry':receipt,
        'regional_emitter':regional,
        'actual_specification':value,'constructor_adapter':cat.admission_provenance,
        'semantic_fixture_entry':semantic,'controls':rejected,
        'source_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'compiler.py',HERE/'numerical.py']},
        'scope':'Actual q127 source/codebook/native specification and checked numerical+stock entry; guarded specification continuation and one actual native IDLE macro emission; no high-field directory or giant production payload executed. q3 fixture entry is semantic only. Physical encoded guard/compiler cost remains open.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=run()
    if args.write:(HERE/'ADMISSION-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
