#!/usr/bin/env python3
"""Source/control certificate for the pooled physical glue, not every primitive theorem.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Source bodies and their contributor notices are preserved unchanged.
"""
import argparse
import ast
from collections import Counter
from hashlib import sha1, sha256
import io
from itertools import product
import json
from pathlib import Path, PurePosixPath
import tarfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
CANONICAL = '12fa8c5c844be21bfefb38a19503fbd867a11244'
SCIENTIFIC = 'a929a3fa36301bdfcffe82afd37434dd9e3c4887'
PREFIX = 'research/physical-complex-controller/'
RUNTIME = (
    PREFIX+'machine.py', PREFIX+'parking.py', PREFIX+'bank_packets.py',
    PREFIX+'root_layer.py', PREFIX+'root_plan.py', PREFIX+'root_streams.py',
    PREFIX+'grid_boundary.py', PREFIX+'monomial_packets.py', PREFIX+'scalar_packets.py',
    'research/t74-physical-layer/t74_machine.py',
    'research/t74-retuned-physical-layer/active_plan.py',
    'research/t74-retuned-physical-layer/active_root.py',
    'research/t74-retuned-physical-layer/retuned_machine.py')
FORBIDDEN_ATTRIBUTES = {'head','cells','position','to_int','decode','as_int','value','seek'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(body):
    return sha256(body).hexdigest()


def frozen():
    pins = json.loads((HERE/'MACHINE-PINS.json').read_bytes())
    need(pins['schema_version'] == 1 and pins['base_commit'] == CANONICAL
         and pins['scientific_head'] == SCIENTIFIC, 'fixed machine source identities')
    manifest_raw = (HERE/pins['manifest']).read_bytes()
    need(digest(manifest_raw) == pins['manifest_sha256'], 'machine source manifest bytes')
    manifest = json.loads(manifest_raw)
    rows = {r['path']:r for r in manifest['files']}
    need(len(rows) == len(manifest['files']) == pins['files'] == 53, 'complete unique source inventory')
    raw = (HERE/pins['archive']).read_bytes()
    need(len(raw) == pins['archive_bytes'] < 2**20
         and digest(raw) == pins['archive_sha256'], 'exact bounded machine source archive')
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts
                 and path.as_posix() == member.name and '\\' not in member.name
                 and member.name in rows and member.name not in result
                 and member.size < 2**22, 'declared regular contained machine source')
            body = archive.extractfile(member).read()
            row = rows[member.name]
            need(len(body) == member.size == row['bytes'] and digest(body) == row['sha256'],
                 'exact immutable machine member')
            if 'git_blob' in row:
                need(row['commit'] in {CANONICAL,SCIENTIFIC} and
                     sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest() == row['git_blob'],
                     'recorded machine Git blob identity')
            result[member.name] = body
    need(set(result) == set(rows), 'no omitted machine source member')
    for name,row in rows.items():
        if 'origin_archive' not in row:
            continue
        body = result[row['origin_archive']]
        for member_name in row['member_chain']:
            with tarfile.open(fileobj=io.BytesIO(body)) as archive:
                member = archive.getmember(member_name)
                need(member.isfile(), 'exact nested source member')
                body = archive.extractfile(member).read()
        need(body == result[name], 'nested primitive copy equals exact reached source')
    return result, pins


def method(tree, class_name, name):
    classes = [n for n in tree.body if isinstance(n,ast.ClassDef) and n.name == class_name]
    need(len(classes) == 1, 'one reached source class '+class_name)
    values = [n for n in classes[0].body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name == name]
    need(len(values) == 1, 'one reached source method '+class_name+'.'+name)
    return values[0]


def inspect_runtime(body):
    tree = ast.parse(body)
    report = Counter()
    for cls in (n for n in tree.body if isinstance(n,ast.ClassDef)):
        for fun in (n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name != '__init__'):
            report['runtime_methods'] += 1
            for node in ast.walk(fun):
                if isinstance(node,ast.Attribute):
                    need(node.attr not in FORBIDDEN_ATTRIBUTES, 'no runtime decoded data or head-coordinate service')
                if isinstance(node,ast.Call):
                    need(not (isinstance(node.func,ast.Name) and node.func.id in {'Tape','Arena'}),
                         'no new physical inventory inside runtime method')
                    if isinstance(node.func,ast.Name) and node.func.id == 'int':
                        need(len(node.args) == 1 and
                             (isinstance(node.args[0],ast.Compare) or
                              ast.unparse(node.args[0]) == 'self.root'),
                             'integer conversion only from bounded flag/comparison')
                    need(not (isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name)
                              and node.func.value.id == 'self' and node.func.attr == 'run'),
                         'no recursive public host run call')
                if isinstance(node,ast.While):report['encoded_or_interpreter_while_loops'] += 1
                if isinstance(node,(ast.For,ast.comprehension)):report['source_fixed_iteration_sites'] += 1
    return dict(report)


def source_contracts(files):
    counts = Counter()
    for name in RUNTIME:
        counts.update(inspect_runtime(files[name]))
    machine = ast.parse(files[PREFIX+'machine.py'])
    enter = ast.unparse(method(machine,'Machine','enter_child'))
    returned = ast.unparse(method(machine,'Machine','return_node'))
    prepared = ast.unparse(method(machine,'Machine','prepare_child'))
    need(enter.index('origin(tape)') < enter.index('self.parking.park()'),
         'parent roles rearmed before park')
    need(returned.index('origin(tape)') < returned.index('self.parking.restore()'),
         'child roles rearmed before ancestor restore')
    need('self.mode = \'node\'' in enter and 'self.root = False' in enter
         and 'self.header.write' in prepared and 'self.pc + 1' in prepared,
         'internal node entry and literal parent continuation')
    need("name == 'rows'" in prepared and "name == 'width'" in prepared
         and "name == 'after'" in prepared and 'else self.c(name)' in prepared,
         'only prescribed child shape fields change')
    t74 = ast.parse(files['research/t74-physical-layer/t74_machine.py'])
    release = ast.unparse(method(t74,'T74Machine','release_zero_step'))
    need(release.index('require_zero(') < release.index('.clear()'),
         'checked complete Z release before clearing')
    loop = ast.unparse(method(t74,'T74Machine','run'))
    need('sealed_constructors()' in loop and 'self.pool.empty()' in loop
         and 'self.enter_child()' in loop and 'while True:' in loop,
         'sealed one-interpreter-loop runtime')
    prior='research/complex-pooled-full-admission/'
    bridge=ast.parse(files[prior+'physical_global_bridge.py'])
    factory=next(n for n in bridge.body if isinstance(n,ast.FunctionDef) and n.name=='production_layer')
    roots=[n for n in ast.walk(factory) if isinstance(n,ast.Call)
           and isinstance(n.func,ast.Attribute) and n.func.attr=='ActiveWidthRoot']
    need(len(roots)==1 and len(roots[0].args)==3 and not roots[0].keywords,
         'production root constructor retains observer=None')
    need("self.level_divisor" in files['research/t74-retuned-physical-layer/active_plan.py'].decode(),
         'actual plan uses passed row divisor')
    plan=ast.parse(files['research/t74-retuned-physical-layer/active_plan.py'])
    compute=method(plan,'ActiveWidthPlan','compute')
    def retained_weight(node):
        if isinstance(node,ast.FunctionDef) and node is not compute:return 0
        if isinstance(node,ast.For):
            # The only retained-result loops have source-literal four-name schemas.
            body=sum(retained_weight(x) for x in node.body)
            if body:
                need(isinstance(node.iter,(ast.Tuple,ast.List)),'retained wrappers only in fixed literal loops')
                body*=len(node.iter.elts)
            return retained_weight(node.iter)+body+sum(retained_weight(x) for x in node.orelse)
        if isinstance(node,ast.While):
            need(sum(retained_weight(x) for x in node.body)==0,'no retained wrapper in numerical planning loop')
            return sum(retained_weight(x) for x in node.orelse)
        own=int(isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                and node.func.id in {'keep','literal','plus','times','scaled'})
        return own+sum(retained_weight(x) for x in ast.iter_child_nodes(node))
    retained=retained_weight(compute)
    need(retained==54,'exact conservative all-branch planning wrapper bound')
    counts['planning_retained_wrapper_bound']=retained
    return dict(counts)


def tape_parking_classes(files, parking_body=None):
    class Meter:
        def __init__(self):
            self.reads=self.writes=self.moves=0
    namespace={'BLANK':4,'LEFT':2,'RIGHT':3,'ZERO':0,'ONE':1,'RETURN':13,'Meter':Meter,'need':need}
    tree=ast.parse(files['nested/records.py'])
    tape=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Tape')
    exec(compile(ast.Module(body=[tape],type_ignores=[]),'authenticated records.Tape','exec',optimize=0),namespace)
    tree=ast.parse(parking_body or files[PREFIX+'parking.py'])
    kept=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.Assign))]
    exec(compile(ast.Module(body=kept,type_ignores=[]),'authenticated parking bodies','exec',optimize=0),namespace)
    return namespace


def read_body(tape):
    tape.rewind();out=[]
    while tape.read()!=4:
        out.append(tape.read());tape.step(1)
    tape.rewind()
    return tuple(out)


def write_body(tape, body):
    need(tape.read()==4,'empty test role')
    for symbol in body:tape.append(symbol)
    tape.rewind()


def parking_case(namespace, frames):
    Tape,Parking=namespace['Tape'],namespace['Parking']
    roles=tuple(Tape() for _ in frames[0]);park=Parking(roles)
    for frame in frames:
        for tape,body in zip(roles,frame):write_body(tape,body)
        park.park()
        need(all(read_body(t)==() for t in roles),'park consumes each role body')
    for expected in reversed(frames):
        park.restore()
        need(tuple(read_body(t) for t in roles)==expected,'restore exact body/order and ancestor frame')
        for tape in roles:tape.clear()
    park.empty()
    need(all(t.head==1 for t in roles) and park.stack.head==park.reverse.head==1,
         'root parking returns physical canonical heads')
    need(all(all(s==4 for s in t.cells[1:]) for t in (*roles,park.stack,park.reverse)),
         'parking scratch is actually erased')
    return sum(t.meter.reads+t.meter.writes+t.meter.moves for t in (*roles,park.stack,park.reverse))


def bounded_parking(files):
    ns=tape_parking_classes(files);alphabet=ns['BODY']
    words=[(),*((s,) for s in alphabet),*((a,b) for a in alphabet for b in alphabet)]
    trials=work=0
    for body in words:
        work+=parking_case(ns,((body,),));trials+=1
    # Nonidentical roles and nested frames expose reversal, delimiter and ownership errors.
    for a in alphabet:
        frames=(( (a,), (13,0,12) ),( (), (a,3) ),( (1,0,a), () ))
        work+=parking_case(ns,frames);trials+=1
    return {'single_role_all_words_length_at_most':2,'body_alphabet':list(alphabet),
            'cases':trials,'nested_depth':3,'observed_tape_actions':work,
            'proof_scope':'Finite regression on actual authenticated Tape/Parking method bodies; arbitrary-length/depth correctness is the written marker and prefix-code induction.'}


def arithmetic_classes(files, scalar_body=None, linear_body=None):
    ns=tape_parking_classes(files)
    def load_nodes(body, names):
        tree=ast.parse(body)
        kept=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
        need(len(kept)==len(names),'complete authenticated arithmetic definition selection')
        exec(compile(ast.Module(body=kept,type_ignores=[]),'authenticated elementary arithmetic','exec',optimize=0),ns)
    load_nodes(files['nested/stream.py'],{'Counter'})
    load_nodes(files['nested/cardinality.py'],{'Natural'})
    load_nodes(files['nested/counts.py'],{'Count'})
    ns['RetainedCount']=ns['Count']
    load_nodes(files['nested/cardinal_counts.py'],{'Count','positive'})
    load_nodes(files['nested/encoded.py'],{'compare','subtract','divide','product','fixed_power','atom_width'})
    load_nodes(files['nested/compact_counts.py'],{'power_two'})
    # ROWS is a fixed source literal, not a test-generated coefficient oracle.
    linear=ast.parse(linear_body or files['research/physical-gaussian-leaf/signed_linear.py'])
    rows=next(n for n in linear.body if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='ROWS' for t in n.targets))
    exec(compile(ast.Module(body=[rows],type_ignores=[]),'authenticated Gaussian row signs','exec'),ns)
    load_nodes(linear_body or files['research/physical-gaussian-leaf/signed_linear.py'],
               {'CoefficientDomainError','transition','linear_word'})
    load_nodes(scalar_body or files['research/physical-scalar-stream/scalar_words.py'],
               {'ScalarContractError','zero_word','require_zero','shifted'})
    return ns


def natural_value(count):
    bits=read_body(count.tape)
    need(bits and bits[-1]==3 and all(b in (0,1) for b in bits[:-1]),'canonical observed test Count')
    need(len(bits)==2 or bits[-2]==1,'minimal observed test Count')
    return sum(b<<i for i,b in enumerate(bits[:-1]))


def bounded_counts(files):
    ns=arithmetic_classes(files);Count=ns['Count'];cases=0
    for a in range(16):
        for b in range(16):
            left,right=Count.literal(a),Count.literal(b)
            need(ns['compare'](left,right)==((a>b)-(a<b)),'actual encoded Count comparison')
            summed=Count(left);summed.add(right)
            multiplied=Count.product(left,right)
            need(natural_value(summed)==a+b and natural_value(multiplied)==a*b,
                 'actual Count binary carry and Horner product')
            if a>=b:
                difference=ns['subtract'](left,right)
                need(natural_value(difference)==a-b,'actual Count borrow difference')
                difference.close()
            if b:
                quotient,remainder=ns['divide'](left,right)
                need((natural_value(quotient),natural_value(remainder))==divmod(a,b),
                     'actual encoded long division')
                quotient.close();remainder.close()
            need(natural_value(left)==a and natural_value(right)==b,'Count borrowed inputs and heads restored')
            for value in (left,right,summed,multiplied):value.close()
            cases+=1
    for a in range(16):
        value=Count.literal(a)
        powered=ns['power_two'](value)
        need(natural_value(powered)==1<<a,'actual counted power-two construction')
        powered.close();value.close();cases+=1
    return {'operand_domain':'0 <= a,b < 16','cases':cases,
            'proof_scope':'Finite source regression for the elementary Count invariants written in MACHINE-ADMISSION.md; no unbounded claim follows from these cases alone.'}


def signed_word(Tape, value, width):
    tape=Tape();write_body(tape,tuple((value>>i)&1 for i in range(width)));return tape


def signed_value(tape,width):
    bits=read_body(tape)
    need(len(bits)==width and all(b in (0,1) for b in bits),'exact test signed output width')
    return sum(b<<i for i,b in enumerate(bits))-(bits[-1]<<width)


def scalar_case(ns,value,width,double):
    Tape=ns['Tape'];source=signed_word(Tape,value,width);target=Tape()
    extent=ns['Count'].literal(width)
    expected=2*value if double else value//2
    valid=(double and -(1<<(width-1))<=expected<(1<<(width-1))) or (not double and value%2==0)
    failed=False
    try:ns['shifted'](source,target,extent,double)
    except ns['CoefficientDomainError']:failed=True
    need(failed!=valid,'scalar exactness/headroom guard matches signed integer domain')
    if valid:need(signed_value(target,width)==expected,'actual scalar exact signed shift')
    need(signed_value(source,width)==value and source.head==1,'scalar source and canonical head restored')
    extent.close()


def linear_case(ns,values,width,signs):
    Tape=ns['Tape'];sources=tuple(signed_word(Tape,x,width) for x in values);target=Tape()
    extent=ns['Count'].literal(width);numerator=sum(s*x for s,x in zip(signs,values))
    valid=numerator%2==0 and -(1<<(width-1))<=numerator//2<(1<<(width-1))
    failed=False
    try:ns['linear_word'](sources,target,extent,signs,True)
    except ns['CoefficientDomainError']:failed=True
    need(failed!=valid,'Gaussian parity/headroom guards match exact integer domain')
    if valid:need(signed_value(target,width)==numerator//2,'actual Gaussian exact half-linear word')
    need(tuple(signed_value(t,width) for t in sources)==values and all(t.head==1 for t in sources),
         'Gaussian complete borrowed sources and canonical heads restored')
    extent.close()


def bounded_halves(files):
    ns=arithmetic_classes(files);scalar=gaussian=0
    for width in range(2,7):
        for value in range(-(1<<(width-1)),1<<(width-1)):
            for double in (False,True):scalar_case(ns,value,width,double);scalar+=1
    for width in (2,3):
        interval=range(-(1<<(width-1)),1<<(width-1))
        for values in product(interval,repeat=4):
            for signs in ns['ROWS']:linear_case(ns,values,width,signs);gaussian+=1
    return {'scalar_widths':[2,3,4,5,6],'scalar_cases':scalar,
            'Gaussian_widths':[2,3],'Gaussian_all_rows_cases':gaussian,
            'proof_scope':'Finite actual-source regression including every signed input in the declared widths; the all-width proof is the binary-prefix, parity and sign-extension induction.'}


def rejected(label, action):
    try:action()
    except (ValueError,TypeError,IndexError):return label
    raise ValueError('accepted machine-lowering corruption: '+label)


def controls(files):
    body=files[PREFIX+'machine.py'].decode()
    variants={
       'runtime_head_coordinate':body.replace('self.pool.empty()','_ = self.output.head\n        self.pool.empty()',1),
       'runtime_decoded_extent':body.replace('self.pool.empty()','_ = self.c("width").to_int()\n        self.pool.empty()',1),
       'physical_Tape_per_node':body.replace('self.pool.empty()','_ = Tape()\n        self.pool.empty()',1),
       'recursive_public_run':body.replace('self.pool.empty()','self.run(None, None)\n        self.pool.empty()',1)}
    result=[rejected(name,lambda mutant=mutant:inspect_runtime(mutant)) for name,mutant in variants.items()]
    corrupted=dict(files)
    t74='research/t74-physical-layer/t74_machine.py'
    corrupted[t74]=files[t74].replace(b'require_zero(self.packet(target), extent)',b'pass')
    result.append(rejected('unchecked_private_release',lambda:source_contracts(corrupted)))
    parking=files[PREFIX+'parking.py'].decode()
    corrupt=parking.replace('self.stack.write(ROLE_END)','self.stack.write(0)',1)
    result.append(rejected('missing_role_delimiter',lambda:parking_case(tape_parking_classes(files,corrupt),((((13,0,12),),((),))))))
    corrupt=parking.replace('for tape in reversed(self.roles):','for tape in self.roles:',1)
    result.append(rejected('wrong_restore_role_order',lambda:parking_case(tape_parking_classes(files,corrupt),((( (0,), (1,) ),)))))
    scalar=files['research/physical-scalar-stream/scalar_words.py'].decode()
    corrupt=scalar.replace('if bit:\n                    raise CoefficientDomainError("inexact scalar HALF")',
                           'if False:\n                    raise CoefficientDomainError("inexact scalar HALF")',1)
    need(corrupt!=scalar,'scalar HALF guard corruption reaches source')
    result.append(rejected('unchecked_scalar_half_parity',lambda:scalar_case(arithmetic_classes(files,scalar_body=corrupt),1,3,False)))
    linear=files['research/physical-gaussian-leaf/signed_linear.py'].decode()
    corrupt=linear.replace('if digit:\n                    raise CoefficientDomainError("inexact Gaussian halving")',
                           'if False:\n                    raise CoefficientDomainError("inexact Gaussian halving")',1)
    need(corrupt!=linear,'Gaussian HALF guard corruption reaches source')
    result.append(rejected('unchecked_Gaussian_half_parity',lambda:linear_case(arithmetic_classes(files,linear_body=corrupt),(1,0,0,0),3,(1,-1,1,1))))
    return result


def certificate():
    files,pins=frozen()
    contracts=source_contracts(files)
    observations=bounded_parking(files)
    count_observations=bounded_counts(files)
    half_observations=bounded_halves(files)
    negative=controls(files)
    gamma=(1<<1296)
    for i in range(1,37):gamma*= (1<<(2*i))-1
    L=322560*gamma
    header=sum(max(1,(bound-1).bit_length()) for bound in (2,10802,322560,gamma,65536,731,73))
    need(header==2695 and gamma.bit_length()==2628,'actual finite header and cover bounds')
    prior='research/complex-pooled-full-admission/'
    global_receipt=json.loads(files[prior+'evidence/PHYSICAL-GLOBAL.json'])
    need(global_receipt['families']==322560 and global_receipt['inventory']['events']==10802
         and global_receipt['local_packet_roles']==731
         and global_receipt['physical_layer_rate']['header_bits']==header,
         'finite prior source inventory agrees with lowering bounds')
    local_receipt=json.loads(files[prior+'evidence/PHYSICAL-LOCAL.json'])
    need(local_receipt['scalar_prefix_denominator_bits']==3 and
         local_receipt['scalar_prefix_l1']=='9' and local_receipt['scalar_maximum_instructions']==10,
         'source-bound exact scalar prefix allowance')
    mass=23431680;groups=1575720;maximum_group=31632
    need(global_receipt['physical_layer_rate']['rank_mass']==mass and
         global_receipt['physical_layer_rate']['maximum_local_group_instructions']==maximum_group and
         global_receipt['inventory']['subgroups_per_cover']==groups,
         'complete source inventory underlying height induction')
    E=1<<100000;B=mass*gamma+E;C0=1<<210000
    need(groups*(maximum_group+1)*10*gamma<E and 32*73*B*B<C0 and
         2*B+18<C0 and 2*B*(73-48)>=mass*gamma+E,
         'exact all-prefix height and final grid guard')
    return {'status':'PASS_POOLED_SOURCE_SPECIFIC_CONTROLLER_LOWERING_CERTIFICATE',
            'base_commit':CANONICAL,'scientific_head':SCIENTIFIC,
            'source_archive_sha256':pins['archive_sha256'],'source_files':len(files),
            'runtime_sources':list(RUNTIME),'source_control_inspection':contracts,
            'cover_bits':gamma.bit_length(),'header_bits':header,'parked_roles':751,
            'finite_labels':{'events':10802,'maximum_subgroups':322560,'pc':65536,'packet_roles':731,'dimension':73},
            'actual_level_divisor_bits':L.bit_length(),'parking_controls':observations,
            'elementary_Count_controls':count_observations,'exact_half_controls':half_observations,
            'all_prefix_guard':{'rank_mass':mass,'subgroups_per_cover':groups,
                                'maximum_group_instructions':maximum_group,'scalar_prefix_allowance':10,
                                'E_exponent':100000,'common_grid_guard_exponent':210000,
                                'complete_local_allowance_bits':(groups*(maximum_group+1)*10*gamma).bit_length(),
                                'B_bits':B.bit_length(),'required_C0_bits':(32*73*B*B).bit_length()},
            'controls_rejected':negative,
            'all_parameter_result':'Written constructive finite-control/encoded-data lowering of exact pooled controller and wiring, with full bank/stack/head bills on the admitted root and guarded reachable internal calls, relative to the named completed component contracts.',
            'guarded_internal_arithmetic_ABI':'Reachable calls of the admitted ideal root; more generally input height t with t+A(e)<=Delta for the node and separately preserved caller/root-tail reserve. Arbitrary representable h-bit words are not all admitted.',
            'new_source_specific_controller_U_premise_required':False,
            'proved_companion_inputs':['NATIVE-ADMISSION.md: arbitrary-dirty ideal Gaussian-dyadic native/group operator identities under exact child substitution; finite-width height guards are proved in MACHINE-ADMISSION.md','HOSTING-ADMISSION.md: complete common-cover and chronological owner allocation'],
            'remaining_component_contracts':['Completed ordinary B1/Compact endpoints, all-input costs and fixed scratch','Signed scalar, Gaussian leaf and single existing normalization primitive endpoints and complete-return tariffs on their exact representable arithmetic domains'],
            'production_payload_executed':False,'formal_kernel_proof':False,
            'all_primitive_theorems_scientifically_admitted':False,
            'scope':'The finite source and negative controls support the written all-parameter controller theorem; they do not convert every retained primitive or analytic contract into an admitted theorem.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--check',type=Path)
    args=parser.parse_args()
    receipt=certificate()
    if args.check:
        need(json.loads(args.check.read_bytes())==receipt,'fresh machine receipt equals committed evidence')
    if args.out:args.out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(receipt['status'],'sources',receipt['source_files'],'parking cases',receipt['parking_controls']['cases'],
          'controls',len(receipt['controls_rejected']))


if __name__=='__main__':main()
