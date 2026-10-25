#!/usr/bin/env python3
"""Source-bound exact current-cut endpoint theorem and full-native path replay.

Standard library only. Historical mathematical modules are immutable; their
captured bytes are adapted only at loading/output boundaries. No caller or
positive multiplication exponent is asserted. Apache-2.0 ancestry; substantial
OpenAI Codex assistance. See ORIGINS.json and PROOF.md.
"""
import argparse
import ast
from contextlib import redirect_stdout
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import types

INPUTS_SHA256='a1190281908fff48f06aad136999c9d574e8c6e31e96b34001e70fc29c75c9f2'
DISABLED=frozenset()
ADAPTATIONS=[]


def need(value, label):
    if not value and label not in DISABLED:
        raise ValueError(label)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def normalize(value):
    return json.loads(json.dumps(value,sort_keys=True))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def typed_equal(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(actual,dict):
        return actual.keys()==expected.keys() and all(typed_equal(actual[k],expected[k]) for k in actual)
    if isinstance(actual,list):
        return len(actual)==len(expected) and all(typed_equal(a,b) for a,b in zip(actual,expected))
    return actual==expected


def replace_once(text, old, new):
    need(text.count(old)==1,'unique declared source adaptation')
    return text.replace(old,new)


def replace_function(text, name, replacement):
    nodes=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name]
    need(len(nodes)==1,'unique adapted function '+name)
    node=nodes[0];lines=text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+replacement+'\n'+''.join(lines[node.end_lineno:])


def execute(name, original, adapted=None, bindings=None):
    text=original.decode() if adapted is None else adapted
    module=types.ModuleType('c07_'+name.replace('.','_'))
    module.__file__='<captured '+name+'>'
    if bindings:
        module.__dict__.update(bindings)
    sys.modules[module.__name__]=module
    exec(compile(text,module.__file__,'exec',dont_inherit=True,optimize=0),module.__dict__)
    ADAPTATIONS.append({'source':name,'raw_sha256':digest(original),
                        'executed_sha256':digest(text.encode()),'optimize':0})
    return module


def modules(raw):
    ce=execute('clifford_exact.py',raw['clifford_exact.py'])
    text=raw['canonical_endpoints.py'].decode()
    start=text.index('HERE=Path(__file__).resolve().parent')
    end=text.index('\ndef build(',start)
    text=text[:start]+"# Captured authenticated ce, bus, win and winner are injected.\n"+text[end:]
    text=replace_once(text," ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');arg=ap.parse_args()",' arg=types.SimpleNamespace(write=True)')
    need(text.count('sha256(CP.read_bytes()).hexdigest()')==2,'two compiler provenance reads')
    text=text.replace('sha256(CP.read_bytes()).hexdigest()',"sha256(RAW['clifford_exact.py']).hexdigest()")
    text=replace_once(text,"sha256((HERE/f).read_bytes()).hexdigest()",'sha256(RAW[f]).hexdigest()')
    tail=text.index(" out=json.loads(json.dumps(out));dest=HERE/'CANONICAL-ENDPOINTS.json'")
    text=text[:tail]+" return json.loads(json.dumps(out))\n"
    bus=json.loads(raw['SOURCE-D4-BUS-INPUT.json']);win=json.loads(raw['SOURCE-COMMON-FRAME-INVERSE-SEARCH.json'])
    endpoint=execute('canonical_endpoints.py',raw['canonical_endpoints.py'],text,
                     {'ce':ce,'bus':bus,'win':win,'winner':{r['p']:r for r in win['rows']},'types':types,'RAW':raw})
    text=raw['full_stabilizer_bound.py'].decode()
    text=replace_once(text,"OLD = Path('/Users/ross/git/math/.research-automation/runs/kappa-major-20261018T1330Z/shared-helper-algebra')","OLD = Path('<captured-sources>')")
    text=replace_function(text,'canonical_predecessor','def canonical_predecessor():\n    return CAPTURED_ENDPOINT')
    text=replace_once(text,"json.loads((OLD / 'NONCOMMON-B1.json').read_text())","json.loads(RAW['NONCOMMON-B1.json'])")
    text=replace_once(text,"hashlib.sha256(Path(__file__).read_bytes()).hexdigest()","hashlib.sha256(RAW['full_stabilizer_bound.py']).hexdigest()")
    bound=execute('full_stabilizer_bound.py',raw['full_stabilizer_bound.py'],text,
                  {'CAPTURED_ENDPOINT':endpoint,'RAW':raw})
    text=raw['path_witness.py'].decode()
    text=replace_once(text,'import full_stabilizer_bound as bound','# Captured authenticated bound module is injected.')
    text=replace_once(text,"hashlib.sha256(Path(__file__).read_bytes()).hexdigest()","hashlib.sha256(RAW['path_witness.py']).hexdigest()")
    path=execute('path_witness.py',raw['path_witness.py'],text,{'bound':bound,'RAW':raw})
    return ce,endpoint,bound,path


def rejected(name, thunk, label):
    global DISABLED
    try:
        thunk()
    except ValueError as error:
        need(str(error)==label,'intended control error '+name)
    else:
        raise ValueError('mutation survived: '+name)
    before=DISABLED
    try:
        DISABLED=before|{label}
        thunk()
    finally:
        DISABLED=before
    return {'name':name,'intended_rejection':label,'executed_named_guard_deletion':'ACCEPTED'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    need(args.output.is_absolute(),'output must be absolute')
    output=args.output.resolve()
    for protected in (Path(__file__).resolve().parent,args.inputs.resolve()):
        need(not output.is_relative_to(protected),'output must be external to code and inputs')
    need(not args.output.exists() and not args.output.is_symlink(),'output must be new')
    manifest_bytes=(args.inputs/'INPUTS.json').read_bytes()
    need(digest(manifest_bytes)==INPUTS_SHA256,'authenticated input manifest')
    manifest=json.loads(manifest_bytes);raw={}
    for name,entry in manifest.items():
        transport=(args.inputs/entry['storage']).read_bytes()
        need(digest(transport)==entry['transport_sha256'] and len(transport)==entry['transport_bytes'],
             'authenticated transport '+name)
        value=gzip.decompress(transport) if entry['storage'].endswith('.gz') else transport
        need(digest(value)==entry['raw_sha256'] and len(value)==entry['raw_bytes'],
             'authenticated raw source '+name)
        raw[name]=value
    ce,endpoint,bound,path=modules(raw)
    phase_pool={};evaluations=[];phase_stage='historical'
    sparse=bound.sparse_column

    def phase_witness(operator,basis=0):
        state,denominator=sparse(operator,basis)
        record={'denominator_depth':denominator,
                'nonzero_amplitudes':[[key,*state[key]] for key in sorted(state)]}
        key=digest(canonical(record))
        if key in phase_pool:
            need(typed_equal(phase_pool[key],record),'exact phase inventory collision guard')
        else:
            phase_pool[key]=record
        evaluations.append({'stage':phase_stage,'n':operator.n,'basis':basis,'signed_tableau':operator.tab,
                            'circuit':operator.circuit,'phase_witness':key})
        return state,denominator

    bound.sparse_column=phase_witness
    with redirect_stdout(io.StringIO()):
        canonical_result=normalize(endpoint.main())
        phase_stage='stabilizer'
        bound_result=normalize(bound.run())
        phase_stage='path'
        path_result=normalize(path.run())
    dense={stage:[e for e in evaluations if e['stage']==stage and e['n']==17
                  and len(phase_pool[e['phase_witness']]['nonzero_amplitudes'])>1]
           for stage in ('stabilizer','path')}
    need(len(dense['stabilizer'])==6 and len(dense['path'])==4,
         'complete original global phase pair coverage')
    global_phase_pairs=[(stage,dense[stage][i],dense[stage][i+1])
                        for stage,indices in [('stabilizer',(0,3)),('path',(0,2))]
                        for i in indices]
    for filename,result in [('CANONICAL-ENDPOINTS.json',canonical_result),
                            ('FULL-STABILIZER-BOUND.json',bound_result),
                            ('FULL-NATIVE-PATH.json',path_result)]:
        need(typed_equal(result,json.loads(raw[filename])),'complete original receipt '+filename)

    def accept_operator(actual,expected,label):
        need(actual.tab==expected.tab,label+': signed Pauli images')
        need(phase_witness(actual)==phase_witness(expected),label+': exact global phase')

    controls=[];local=[];phase_stage='local_lowerings_and_controls'
    # Independently retain every local lowering, with complete phase witnesses.
    for group in range(3):
        for coordinate,p in enumerate(endpoint.bus['groups7'][group]):
            q=endpoint.bus['groups7'][(group+1)%3][coordinate]
            r=endpoint.bus['groups7'][(group+2)%3][coordinate]
            chart=ce.perm(7,ce.transpose(endpoint.completion(p,q),7))
            if group==2:
                pre=endpoint.build(7,endpoint.winner[p]['pre_events'])
            else:
                v=q^r
                pre=ce.perm(7,[(1<<i)^(v if v>>i&1 else 0) for i in range(7)])
            canon,recipe=ce.monomial(chart.then(pre).then(chart.adjoint()))
            first=bound.standard_product(ce,ce.fourier(7,range(2,7)),canon.adjoint(),
                                         ce.cgate(7,1),ce.cgate(7,2).adjoint())
            native,lowered=ce.lower_child(first)
            label='first factor '+str(p)
            accept_operator(first,lowered,label)
            need(native['rank']==(3 if group==2 else 5),label+': native rank')
            # Right input Z fixes |0> but changes signed Pauli images.
            z=ce.diag(7,[0]*7,[2]+[0]*6)
            wrong_signed=bound.standard_product(ce,first,z)
            controls.append(rejected(label+' wrong signed tableau',
                lambda a=wrong_signed,b=first,l=label:accept_operator(a,b,l),label+': signed Pauli images'))
            wrong_phase=first.then(ce.Op(7,ce.identity(7),[('phase',1)]))
            controls.append(rejected(label+' omitted global i',
                lambda a=wrong_phase,b=first,l=label:accept_operator(a,b,l),label+': exact global phase'))
            local.append({'group':group,'coordinate':coordinate,'p':p,'q':q,
                          'canonical_pre_monomial':recipe,'first_factor_signed_tableau':first.tab,
                          'native_recipe':native,'literal_lowering':lowered.circuit,
                          'first_factor_circuit':first.circuit})

    for index,(stage,a,b) in enumerate(global_phase_pairs):
        actual=ce.Op(a['n'],a['signed_tableau'],a['circuit'])
        expected=ce.Op(b['n'],b['signed_tableau'],b['circuit'])
        label=stage+' global phase pair '+str(index)
        accept_operator(actual,expected,label)
        wrong=actual.then(ce.Op(17,ce.identity(17),[('phase',1)]))
        controls.append(rejected(label+' omitted global i',
            lambda a=wrong,b=expected,l=label:accept_operator(a,b,l),label+': exact global phase'))

    # Explicit production rank-zero admission, including the two old defects.
    def accept_zero_native(operator,label):
        need(bound.native_rank(operator)==0,label)

    n=4;cp,cq,past=ce.cgate(n,1),ce.cgate(n,2),ce.cgate(n,4)
    dx=bound.standard_product(ce,cp,past)
    swap=ce.perm(n,[1,2,8,4])
    dressed=bound.standard_product(ce,dx.adjoint(),swap,dx)
    admit=bound.standard_product(ce,dx,dressed,dx.adjoint())
    accept_zero_native(admit,'current-cut X monomial admission')
    undressed=bound.standard_product(ce,dx,swap,dx.adjoint())
    controls.append(rejected('undressed logical swap',
        lambda:accept_zero_native(undressed,'current-cut X monomial admission'),
        'current-cut X monomial admission'))
    common=bound.standard_product(ce,cq,cp.adjoint())
    chirped=ce.perm(n,[2,3,4,8]).then(ce.diag(n,[3,1,0,0]))
    accept_zero_native(bound.standard_product(ce,common,chirped,common.adjoint()),
                       'current-cut Y monomial admission')
    omitted=bound.standard_product(ce,common,ce.perm(n,[2,3,4,8]),common.adjoint())
    controls.append(rejected('omitted common quadratic chirp',
        lambda:accept_zero_native(omitted,'current-cut Y monomial admission'),
        'current-cut Y monomial admission'))
    need(len(controls)==30,'complete current-cut control inventory')
    # This exact invoice is conditional on the old paired bank stock model.
    invoice=[]
    for length in (3,5,9):
        banks=(length-1)//2
        direct=32*banks
        before=8*length-24
        need(before-direct==-8*length-8,'conditional direct completion identity')
        invoice.append({'L':length,'Y_banks':banks,'pre_completion_deficit':before,
                        'unary_completion_minimum_rank':direct,'completed_deficit':before-direct})
    result={'schema':'c07_current_cut_endpoint.v1',
            'status':'PASS_CURRENT_CUT_THEOREM_AND_FULL_NATIVE_PATH_NO_NEW_KAPPA',
            'scientific_pin':bound.PIN,'input_inventory':manifest,'source_adaptations':ADAPTATIONS,
            'canonical_endpoints':canonical_result,'full_stabilizer_bound':bound_result,
            'full_native_path':path_result,'local_signed_native_lowerings':normalize(local),
            'phase_evaluations':normalize(evaluations),'complete_phase_witnesses':phase_pool,
            'operator_controls':controls,'production_rejections':30,'executed_guard_deletions':30,
            'conditional_direct_completion_invoice':invoice,
            'domain':{'theorem':'L>=1, f>=1, common2/own-fresh5 current-cut unary insertion model',
                      'free_word':'Exact two-column free group algebra B1 identity at L=3 only',
                      'finite_global_cases':'all 12 ports at L=1,3,5,9; canonical baseline also L=7',
                      'global_phase_scope':'Exact sparse complete columns for original n17 witnesses; all-L phases from written telescoping identity',
                      'direct_invoice':'stipulated odd L=2B+1>=3 paired schedule only, B>=1, W=12(L-1), D=8L-24; no optimal completion recipe asserted',
                      'L1_scope':'generic endpoint fixture only; no zero-bank caller construction is asserted'},
            'limits':['Arbitrary physical monomial insertions are covered by the written row-support theorem, not a finite generator search.',
                      'No absorbing-past-support premise is used; legal dressed swaps can transfer to future support.',
                      'Full-native coefficient path is not a complete clearing caller or a raw reverse-source interface.',
                      'All actual monomial address/phase scans remain paid; zero native rank does not mean zero work.',
                      'No whole caller, owner admission, physical controller, rounded precision or stronger multiplication bound.']}
    encoded=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
    transport=gzip.compress(encoded,compresslevel=9,mtime=0) if args.output.suffix=='.gz' else encoded
    with args.output.open('xb') as stream:
        stream.write(transport)
    print(json.dumps({'status':result['status'],'receipt_raw_sha256':digest(encoded),
                      'phase_evaluations':len(evaluations),'unique_complete_phase_columns':len(phase_pool),
                      'controls':len(controls)}))


if __name__=='__main__':
    main()
