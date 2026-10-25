"""Exact-source global physical rebinding for the pooled complex supplier.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
The finite audit and the retained all-width primitive/root contracts are distinct.
"""
import argparse
import ast
from collections import Counter
from contextlib import contextmanager
from fractions import Fraction as Q
from hashlib import sha256
import io
import json
import lzma
from pathlib import Path, PurePosixPath
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
# Replaced once by the package preparation script; these are scientific pins.
BUNDLE_SHA256 = '511ef8e6f9d1519886a8a531d788af6ef51bfcf684172a15890895f66dbcf308'
PINS_SHA256 = '66535e3e7aa509a079ec7bd6ffd3db83f577aa1b22103aaf21f03722e05acf9b'
SOURCE_PINS = {'research/physical-complex-controller/PROOF.md': '471185621c0ecce295ffd327b1244aed234efe5ff05a804aaaa11316f1a8319e', 'research/physical-complex-controller/cover.py': 'd797daec10275f439f6019c596b89afbc32a7716cb657648adfcaae2408949da', 'research/physical-complex-controller/selected_binding.py': 'd6583458d00e4933c3a3fd83cc376f21c059e9fc6aa338c00d66c1deeaa0e985', 'research/t74-physical-layer/binding.py': 'bd05a117aad3f696a108f0ce95287f1ea3a36603e3df8a2811e74138e73e1057', 'research/t74-retuned-physical-layer/PROOF.md': '59da2c3223501da8228fb064201be81a809d4c3da19788692dbd5f5705fe016f', 'research/t74-retuned-physical-layer/active_plan.py': 'e1092fdbb70df43f1d4fdb50f39a07a543d71c4ea9f9e8a50b790b81fd50223e', 'research/t74-retuned-physical-layer/active_root.py': '5496bfeea5955b8b70f380e39461198a121ebc0ce8ad0aa1d0e58a9f3035ebd7', 'research/t74-retuned-physical-layer/active_sources.py': '599c701b15d45f3dfee531a118e11a0aa0997d070e9cce4b6298d5b20defad49', 'research/t74-retuned-physical-layer/retuned_machine.py': 'd4a43288c554704406a355ae95f9cb1bc82d634b652f7e85ffc2269fa5daf87a', 'research/t74-retuned-physical-layer/retuned_native.py': '4b48f4a0d2900195201cdb8eaf715cb22460de391410e66bee5a6302fd1796dc'}
PROFILE = {1:8060040,2:2310120,3:751788,4:327240,5:66420,8:25920,48:138492}
OLD_PROFILE = {1:1645680,2:470196,3:159468,4:71928,5:13716,8:5328,48:28190}
GLOBAL_FIELDS = {'m','live','physical','private_namespace','local_providers',
                 'private_zero_buffer_lowering','calls','execution_schedule','idle_children','bank_padding'}
DELTA = {66304:322560,66813:323069,66312:322568,66720:322976,
         66811:323067,666:3240,2222:10802,8659:6489}
DELTA_COUNTS = {66304: 3, 8659: 1, 66813: 2, 666: 2, 2222: 1, 66720: 3, 66312: 2, 66811: 2, 'providers': 1, 'phases': 1, 'providers_tuple': 1, 'profile': 1}
JOINT_ARITHMETIC_SHA = 'c4740234bee2bab8292aeef7fb561246cff8a060ea6e96f0bc14a7b69c62042c'
LOCAL_BRIDGE_SHA = '590c928e290fe8d7cbaa08bcd73fcac4fee6fe21aca193f5c41e3d612f57fd9a'
_local_bridge = None


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def local_module():
    global _local_bridge
    name = 'pooled_physical_local_bridge'
    path = HERE/'physical_bridge.py'
    need(path.is_file() and not path.is_symlink(), 'regular local bridge')
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == LOCAL_BRIDGE_SHA, 'exact local bridge source bytes')
    if name in sys.modules:
        value = sys.modules[name]
        need(_local_bridge is not None and value is _local_bridge
             and value.__file__ == str(path)
             and value.pooled_source_sha256 == LOCAL_BRIDGE_SHA,
             'only reuse the locally authenticated source-module identity')
        return value
    need(_local_bridge is None, 'authenticated local module alias remains installed')
    value = types.ModuleType(name)
    value.__file__ = str(path)
    sys.modules[name] = value
    try:
        # Never consult an import loader or an existing bytecode cache.
        exec(compile(raw,str(path),'exec',optimize=0),value.__dict__)
    except BaseException:
        if sys.modules.get(name) is value:
            del sys.modules[name]
        raise
    value.pooled_source_sha256 = LOCAL_BRIDGE_SHA
    _local_bridge = value
    return value


def local_source_controls():
    global LOCAL_BRIDGE_SHA
    value = local_module()
    name = 'pooled_physical_local_bridge'
    controls = []
    sys.modules[name] = types.ModuleType(name)
    try:
        try:
            local_module()
        except ValueError:
            controls.append('unowned_local_module_alias')
        else:
            raise RuntimeError('accepted an unowned local bridge module')
    finally:
        sys.modules[name] = value
    expected = LOCAL_BRIDGE_SHA
    LOCAL_BRIDGE_SHA = '0'*64
    try:
        try:
            local_module()
        except ValueError:
            controls.append('changed_local_source_commitment')
        else:
            raise RuntimeError('accepted mismatched local bridge source bytes')
    finally:
        LOCAL_BRIDGE_SHA = expected
    need(local_module() is value, 'source controls restore the authenticated module')
    return controls


def frozen_global():
    path = HERE/'PHYSICAL-GLOBAL-PINS.json'
    need(path.is_file() and not path.is_symlink(), 'regular global source manifest')
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PINS_SHA256, 'complete global scientific manifest commitment')
    pins = json.loads(raw)
    need(pins['source_sha256'] == SOURCE_PINS, 'global source commitments')
    bundle = pins['bundle']
    need(bundle['path'] == 'frozen/physical-t74/GLOBAL-BINDING.tar.xz'
         and bundle['sha256'] == BUNDLE_SHA256, 'fixed global source archive')
    path = HERE/bundle['path']
    need(path.is_file() and not path.is_symlink(), 'regular global source archive')
    compressed = path.read_bytes()
    need(len(compressed) == bundle['bytes'] and len(compressed) < 8*2**20
         and sha256(compressed).hexdigest() == BUNDLE_SHA256, 'bounded authenticated global source')
    raw = lzma.decompress(compressed)
    need(len(raw) < 128*2**20, 'bounded global source expansion')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
        for member in archive.getmembers():
            name = PurePosixPath(member.name)
            need(member.isfile() and not name.is_absolute() and '..' not in name.parts
                 and '\\' not in member.name and name.as_posix() == member.name
                 and member.name not in files and member.name in bundle['files']
                 and member.size < 100*2**20, 'declared regular global member')
            value = archive.extractfile(member).read()
            expected = bundle['files'][member.name]
            need(len(value) == member.size == expected['bytes']
                 and sha256(value).hexdigest() == expected['sha256'], 'exact global member')
            files[member.name] = value
    need(set(files) == set(bundle['files']) and len(files) == 13, 'complete global source inventory')
    for name, digest in SOURCE_PINS.items():
        need(sha256(files['source/'+name]).hexdigest() == digest, 'global source pin')
    return pins, files


def expand_projection(files, native):
    template = json.loads(files['data/PHYSICAL-PROJECTION.json'])
    routes = template.pop('physical_owner_routes')
    need(len(routes) == len({canonical(route) for route in routes}), 'unique owner route dictionary')
    for call in template['calls']:
        for owner in call['owners']:
            index = owner[1]
            need(type(index) is int and 0 <= index < len(routes), 'complete route dictionary index')
            owner[1] = routes[index]
    for pid, row in template['local_providers'].items():
        programs = native[pid]['programs']
        need(row.pop('physical_program_binding') == sha256(canonical(programs)).hexdigest(),
             'physical projection to exact local program')
        row['local_programs'] = programs
    return template


def source_module(name, raw, injected=None, definitions_only=False):
    tree = ast.parse(raw)
    if definitions_only:
        # The only removed syntax is loader/import plumbing. Every retained
        # definition is compiled exactly, including all method bodies.
        tree.body = [node for node in tree.body if isinstance(node,(ast.ClassDef,ast.FunctionDef))]
    value = types.ModuleType(name)
    value.__file__ = name
    if injected:
        value.__dict__.update(injected)
    sys.modules[name] = value
    exec(compile(tree,name,'exec',optimize=0),value.__dict__)
    return value


def binding_class(files, compiler, scalar_type, template, phases, sigmas, native):
    cover = source_module('pooled_physical_cover',files['source/research/physical-complex-controller/cover.py'])
    from dataclasses import dataclass
    injected = dict(Counter=Counter,sha256=sha256,json=json,dataclass=dataclass)
    injected.update({name:getattr(cover,name) for name in
                     ('OrthogonalCover','act','is_orthogonal','multiply','parity','transpose')})
    selected = source_module('pooled_selected_binding',
        files['source/research/physical-complex-controller/selected_binding.py'],injected,True)
    raw = files['source/research/t74-physical-layer/binding.py']
    tree = ast.parse(raw)
    counts = Counter()
    class Change(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value) is int and node.value in DELTA:
                counts[node.value] += 1
                return ast.copy_location(ast.Constant(DELTA[node.value]),node)
            if node.value == 'bound/base/providers':
                counts['providers'] += 1
                return ast.copy_location(ast.Constant('base/providers'),node)
            if node.value == 'bound/base/work/complex-nine-native/DATA-PHASES.json':
                counts['phases'] += 1
                return ast.copy_location(ast.Constant('base/work/complex-nine-native/DATA-PHASES.json'),node)
            return node
        def visit_Tuple(self,node):
            if all(isinstance(v,ast.Constant) for v in node.elts) and [v.value for v in node.elts] == ['gauge44','extra']:
                counts['providers_tuple'] += 1
                node.elts.append(ast.Constant('extra-four'))
            return self.generic_visit(node)
        def visit_Dict(self,node):
            if all(isinstance(v,ast.Constant) for v in node.keys+node.values) and {
                    k.value:v.value for k,v in zip(node.keys,node.values)} == OLD_PROFILE:
                counts['profile'] += 1
                return ast.copy_location(ast.Dict(keys=[ast.Constant(k) for k in PROFILE],
                                                  values=[ast.Constant(v) for v in PROFILE.values()]),node)
            return self.generic_visit(node)
    tree = Change().visit(tree)
    need(dict(counts) == DELTA_COUNTS, 'exact complete T74 source delta')
    classes = [node for node in tree.body if isinstance(node,ast.ClassDef)]
    need(len(classes) == 1 and classes[0].name == 'T74Binding', 'one adapted retained binding class')
    # Reads are capabilities bound to authenticated objects, never arbitrary paths.
    root = Path('authenticated-pooled-source')
    data = {str(root/'hosted/GLOBAL-TEMPLATE.json.gz'):template,
            str(root/'base/work/complex-nine-native/DATA-PHASES.json'):phases,
            str(root/'hosted/ACTUAL-SIGMAS.json.gz'):sigmas}
    def read(path):
        need(str(path) in data,'declared physical snapshot read')
        return data[str(path)]
    def read_native(path):
        path = Path(path)
        need(path.parent == root/'base/providers' and path.name in native,'declared native snapshot read')
        return native[path.name]
    def authenticate_prepared(path):
        need(path == root,'one immutable prepared snapshot')
    injected.update(dict(Path=Path,Compiler=compiler,canonical=canonical,need=need,
                         read=read,read_native=read_native,authenticate_prepared=authenticate_prepared,
                         ScalarProgram=scalar_type))
    injected.update({name:getattr(selected,name) for name in
                     ('Group','Owner','SelectedBinding','data_route','embed','literal','port_basis')})
    transformed = ast.fix_missing_locations(ast.Module(body=classes,type_ignores=[]))
    exec(compile(transformed,'pooled_physical_binding','exec',optimize=0),injected)
    return injected['T74Binding'],root,cover,sha256(ast.dump(transformed,include_attributes=False).encode()).hexdigest()


def validate_schedule(binding, cover):
    local_events = [event for event in binding.events if event['kind'] == 'local_cover_sweep']
    need(Counter(event['time'] for event in local_events) == Counter(binding.calls.keys()),
         'every complete call dispatched exactly once')
    for event in local_events:
        call = binding.calls[event['time']]
        need(event['provider_id'] == call['provider_id'], 'actual provider at each local event')
    pending = set()
    unique_suffixes = set()
    for event in binding.events:
        kind = event['kind']
        if kind == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                for port in range(112):
                    family = 896*event['replica']+(2*event['pair']+side)*112+port
                    need(0 <= family < binding.families,'idle family within bank')
                    key = (event['replica'],child,port)
                    row = binding.remainders.get(key)
                    if row:
                        need(key not in pending and row['family'] == family, 'one exact pending idle tail')
                        pending.add(key)
                        suffix = (port,child,row['pending_offset'],row['rank'])
                        if suffix not in unique_suffixes:
                            axes = binding.data['phases']['recipes'][port]['idle_children'][child]['orthogonal_axes']
                            active = axes[row['pending_offset']:]
                            need(len(active) == row['rank'] and 0 < len(active) <= binding.maximum_rank,
                                 'complete positive idle suffix')
                            basis = binding.bases[port]
                            chart = tuple(active)+tuple(v for v in basis if v not in active)
                            need(len(chart) == 73 and set(chart) == set(basis), 'orthogonal pending suffix chart')
                            unique_suffixes.add(suffix)
        elif kind == 'bridge':
            need(event['coefficient'] in (-1,1) and 0 <= event['src'] < 4
                 and 0 <= event['dst'] < 4 and event['src'] != event['dst'], 'retained signed bridge')
        else:
            need(kind in {'local_cover_sweep','terminal_Y_translations','terminal',
                          'bank_padding_cover_sweep','translate_every_live_family'}, 'complete global event alphabet')
        if 'replica' in event:
            need(type(event['replica']) is int and 0 <= event['replica'] < 360,'all replica families fit')
    need(pending == set(binding.remainders), 'all positive idle children reached')
    data_charts = {(call['stage'],role%112):owner.sigma_columns
                   for call in binding.calls.values()
                   for role,owner in enumerate(binding.owner_specs[call['time']][:224])}
    need(all(cover.is_orthogonal(value) for value in data_charts.values()),'all exact data route charts orthogonal')
    return {'pending_children':len(pending),'distinct_pending_suffixes':len(unique_suffixes),
            'data_charts':len(data_charts), 'all_owner_entries':sum(map(len,binding.owner_specs.values()))}


def negative_controls(binding, cover):
    controls = []
    def reject(label, change, restore, check):
        change()
        try:
            try:
                check()
            except (ValueError,KeyError):
                controls.append(label)
            else:
                raise RuntimeError('accepted invalid global physical binding: '+label)
        finally:
            restore()
    first = binding.calls[0]
    old_family = first['owners'][0][0]
    reject('duplicate_complete_owner_family',
           lambda:first['owners'][0].__setitem__(0,first['owners'][1][0]),
           lambda:first['owners'][0].__setitem__(0,old_family),binding.bind_owners)
    widths = binding.template['local_providers'][first['provider_id']]['widths']
    width = widths[0]
    reject('misbound_actual_provider_width',lambda:widths.__setitem__(0,width+1),
           lambda:widths.__setitem__(0,width),binding.bind_owners)
    mapping = binding.template['private_zero_buffer_lowering']['provider_maps'][first['provider_id']]
    label = next(iter(mapping)); old_slot = mapping[label]
    reject('private_Z_map_outside_declared_family',lambda:mapping.__setitem__(label,old_slot+1),
           lambda:mapping.__setitem__(label,old_slot),binding.bind_owners)
    first_event = next(event for event in binding.events if event['kind'] == 'local_cover_sweep')
    time = first_event['time']
    reject('missing_or_duplicate_complete_call_dispatch',lambda:first_event.__setitem__('time',(time+1)%3240),
           lambda:first_event.__setitem__('time',time),lambda:validate_schedule(binding,cover))
    pid = first_event['provider_id']
    reject('misbound_local_provider_dispatch',lambda:first_event.__setitem__('provider_id','missing'),
           lambda:first_event.__setitem__('provider_id',pid),lambda:validate_schedule(binding,cover))
    row = next(iter(binding.remainders.values())); offset = row['pending_offset']
    reject('omitted_pending_idle_axis',lambda:row.__setitem__('pending_offset',offset+1),
           lambda:row.__setitem__('pending_offset',offset),lambda:validate_schedule(binding,cover))
    return controls


def rate_certificate(binding):
    path = HERE/'joint_bound.py'
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == JOINT_ARITHMETIC_SHA,'exact rational moment implementation')
    value = types.ModuleType('pooled_physical_joint_arithmetic')
    value.__file__ = str(path)
    exec(compile(raw,str(path),'exec',optimize=0),value.__dict__)
    sigma,alpha,eta = Q('0.99826995'),Q('0.99827'),Q(1,10**6)
    tau = Q(332353,332929)
    lower,upper = value.moment(PROFILE,73,binding.families,1-sigma)
    need(upper < 0 and tau < sigma < alpha,'strict complete moment and unchanged B1 rate')
    internal = sigma-eta*(sigma-tau)
    leaf = sigma+eta*(1-sigma)
    need(internal < alpha and leaf < alpha and Q(499,500) < alpha,
         'complete internal, stopped-leaf and reservation margins')
    need(500*(1-alpha) < 1,'small-width fallback paid by one logarithm')
    gamma = binding.cover.size
    mass = sum(rank*count for rank,count in PROFILE.items())
    B = mass*gamma+(1<<100000)
    need(32*73*B*B < 1<<210000 and 2*B+18 < 1<<210000
         and 2*B*(73-48) >= mass*gamma+(1<<100000),'unchanged all-width exact coefficient guard')
    # A deliberately coarse complete finite bound, including view adapters.
    maximum_group = max(map(len,binding.codes.values()))+2*632+2*224
    need(maximum_group < 65536,'unchanged physical program counter bound')
    groups = sum(binding.group_count(i) for i in range(len(binding.events)))
    need(groups*(maximum_group+1)*10*gamma < 1<<100000,
         'complete scalar and nonchild literal allowance below inherited E')
    header = sum((bound-1).bit_length() for bound in
                 (2,len(binding.events),binding.families,gamma,65536,731,73))
    need(header == 2695,'derived finite header size')
    return dict(sigma=str(sigma),tau=str(tau),alpha=str(alpha),stopping_power=10**6,
                moment_minus_one=[str(lower),str(upper)],
                internal_exponent=str(internal),leaf_exponent=str(leaf),
                internal_margin=str(alpha-internal),leaf_margin=str(alpha-leaf),
                reserved_margin=str(alpha-Q(499,500)),fallback_log_power=str(500*(1-alpha)),
                rank_mass=mass,cover_bits=gamma.bit_length(),header_bits=header,
                maximum_local_group_instructions=maximum_group,
                exact_guard_exponent=210000,
                joint_arithmetic_sha256=JOINT_ARITHMETIC_SHA)


@contextmanager
def bound_inputs(scalar_module=None, release_global=None):
    local = local_module()
    pins, files = frozen_global()
    with local.frozen_inputs() as (repo,providers):
        compiler = local.module('pooled_global_compiler',(repo/'research/t74-physical-layer/compile_word.py').read_bytes())
        if scalar_module is None:
            scalar_module = local.module('pooled_global_scalar',(repo/'research/physical-complex-controller/scalar_program.py').read_bytes())
        else:
            path = Path(scalar_module.__file__)
            need(path.is_file() and sha256(path.read_bytes()).hexdigest() ==
                 local.SOURCE_PINS['research/physical-complex-controller/scalar_program.py'],
                 'same authenticated physical ScalarProgram cohort')
        native = {pid:compiler.read_native(providers/pid) for pid in local.NATIVE_PINS}
        template = expand_projection(files,native)
        need(sha256(canonical(template)).hexdigest() == pins['projection_sha256'],
             'lossless global physical projection')
        phases,sigmas = (json.loads(files['data/'+name]) for name in ('DATA-PHASES.json','ACTUAL-SIGMAS.json'))
        if release_global:
            import gzip
            release_global = Path(release_global)
            for relative,pin in pins['release_inputs'].items():
                raw = (release_global/relative).read_bytes()
                value = json.loads(gzip.decompress(raw) if relative.endswith('.gz') else raw)
                need(sha256(canonical(value)).hexdigest() == pin['canonical_sha256'],
                     'fresh complete release semantic binding: '+relative)
                if relative.endswith('GLOBAL-TEMPLATE.json.gz'):
                    need({name:value[name] for name in GLOBAL_FIELDS} == template,
                         'every consumed physical field matches fresh release')
            for pid,paths in local.NATIVE_PINS.items():
                for name,digest in paths.items():
                    local.checked(release_global/'base/providers'/pid/name,digest)
        cls,root,cover,ast_digest = binding_class(files,compiler.Compiler,scalar_module.ScalarProgram,
                                                template,phases,sigmas,native)
        yield cls(root),cover,ast_digest


def production_layer():
    """Bind the new dispatcher to the actual existing PR3599 B1 root factory.

    The caller must already be inside active_sources.opened(). This does not
    create another tape cohort or replace its Ordinary/Profile constructors.
    Production geometry is enormous; the standalone audit does not execute it.
    """
    import active_sources
    state = active_sources.active()
    import scalar_program
    import active_root
    import active_plan
    import retuned_machine
    import retuned_native
    for name,module in (('active_sources',active_sources),('active_root',active_root),
                        ('active_plan',active_plan),('retuned_machine',retuned_machine),
                        ('retuned_native',retuned_native)):
        need(sha256(Path(module.__file__).read_bytes()).hexdigest() ==
             SOURCE_PINS['research/t74-retuned-physical-layer/'+name+'.py'],
             'exact retained active physical factory: '+name)
    need(active_root.ActiveWidthPlan is active_plan.ActiveWidthPlan
         and active_root.RetunedMachine is retuned_machine.RetunedMachine
         and active_root.build_native is retuned_native.build_native,
         'one actual root planner, machine and ordinary factory cohort')
    need(Path(scalar_program.__file__).resolve().parent == state.controller.resolve(),
         'scalar compiler belongs to the existing physical cohort')
    with bound_inputs(scalar_program) as (binding,_,_):
        native = retuned_native.build_native()
        return active_root.ActiveWidthRoot(binding,native,binding.catalogue)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-global',type=Path)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.out:
        need(HERE not in args.out.resolve().parents,'receipt outside published package')
    with bound_inputs(release_global=args.release_global) as (binding,cover,digest):
        audit = validate_schedule(binding,cover)
        controls = local_source_controls()+negative_controls(binding,cover)
        rates = rate_certificate(binding)
        need(binding.check_profile() == PROFILE,'full positive-child physical invoice')
        inventory = binding.inventory()
        need(inventory['owner_entries'] == 2047680 and inventory['helper_charts'] == 6489,
             'complete new owner and chart inventory')
        result = dict(status='PASS_POOLED_GLOBAL_PHYSICAL_BINDING_WITH_RETAINED_PRIMITIVE_CONTRACTS',
                      source_bundle_sha256=BUNDLE_SHA256,source_sha256=SOURCE_PINS,
                      local_bridge_sha256=LOCAL_BRIDGE_SHA,
                      retained_binding_ast_sha256=digest,inventory=inventory,schedule=audit,
                      positive_children=PROFILE,families=binding.families,
                      local_packet_roles=binding.slots+binding.private,
                      negative_controls=controls,physical_layer_rate=rates,
                      scope='All finite global owner/event/child bindings; all-cover and all-width endpoint and cost are written compositional proofs under the retained primitive/root contracts. No production physical payload execution or formal kernel proof.')
    if args.out:
        args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'calls',inventory['calls'],'owners',inventory['owner_entries'])


if __name__ == '__main__':
    main()
