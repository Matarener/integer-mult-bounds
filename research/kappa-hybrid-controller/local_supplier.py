#!/usr/bin/env python3
"""Fresh complete replay of the PR4441 retimed arbitrary-input supplier."""
from collections import Counter
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RETIMED = HERE.parent/'fresh-helper-boundary'
DEFAULT_RETIMED_ROOT = HERE.parents[1]
DEFAULT_SOURCE = HERE.parent/'pr4359-p7-padding/source'
MANIFEST_SHA256 = '0305d4730e2dfede834a241099aa6ceeee29444f305dfeb25ae9a1bb8b2df0b6'
FUSER_SHA256 = 'e1ba009d546981e75f0e6468723b9af4c065f5eb6e08390084fbbf9a579cedf1'


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate_upstream(p7):
    manifest_path = p7/'EXPORTED-SOURCES.json'
    need(digest(manifest_path) == MANIFEST_SHA256, 'Exact upstream source manifest')
    manifest = read(manifest_path)
    seen = set()
    for row in manifest['files']:
        relative = PurePosixPath(row['path'])
        need(not relative.is_absolute() and '..' not in relative.parts,
             'Canonical authenticated source path')
        need(str(relative) not in seen, 'Unique authenticated source')
        seen.add(str(relative))
        path = p7/str(relative)
        need(not path.is_symlink(), 'No source file alias')
        data = path.read_bytes()
        need(len(data) == row['bytes'] and sha256(data).hexdigest() == row['sha256'],
             'Exact original source bytes: '+str(relative))
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],
             'Exact original Git blob: '+str(relative))
    return len(seen)


RETIMED_HEAD = 'ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9'
RETIMED_FILES = {
    'native.py':'9b55a2d3c3972148fae9d112e745d9244968166bd89bd900c938f429fc76ab29',
    'CHANGES.json':'cde73b8ff5b3c0d06e69e2293b991b24fd14a16dd4ccab7ff6b3439074a94624',
    'NATIVE-RESULT.json.gz':'37d0848458b289eb50271c47adef6e74014ae30be6363d09394b2337b566b839',
}
RETIMED_SOURCES = {
    'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py':'106b4d5e052427230df452f0c901d5390a0583782960b80a8af94d9a984022c7',
    'research/kappa-function-composition/complex/prune_native.py':'f2b37c183a10922eabc8e0436b426a08866430e96bd0adc7e178951c7fbb5257',
    'research/kappa-rebuild/complex/native_extensions.py':'50ad007d9c386393657e86c99a96ae0a63a8fbc52872579b185002cc626e88e3',
    'research/kappa-rebuild/complex/rebuild_native.py':'f94c527cc02215de49350d477618188c4c0da48bc8fb05b4e37b24c482cad7d5',
    'research/kappa-rebuild/complex/power_two_balance.py':'76929bb3887911ccf100c4593574b8a1c82ee64e96f939a8aca196869438b424',
    'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
    'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz':'6418ec3da24d548a57f5c3fe5b9062c26c9478e638504a61c387f5cfb5f4ed61',
    'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz':'c54b0a3e129d28e6dbf74fa731fc3bb70fe3c6705f07256750fbecddcc842d39',
}


def run(source_root=DEFAULT_SOURCE,retimed_source_root=None):
    root = Path(source_root).resolve()
    retimed_root = Path(retimed_source_root or DEFAULT_RETIMED_ROOT).resolve()
    p7 = root.parent
    parameters = load(HERE/'parameters.py','hybrid_retimed_supplier_parameters')
    authenticated = authenticate_upstream(p7)
    fuser_path = p7/'dependencies/tensor-strictification/native_inventory.py'
    need(digest(fuser_path) == FUSER_SHA256,'Exact original center phase and helper validator')
    fuser = load(fuser_path,'hybrid_retimed_original_fuser')
    inherited_gate = fuser.run(root)
    for name,expected in RETIMED_FILES.items():
        need(digest(RETIMED/name) == expected,'Exact retained PR4441 artifact '+name)
    for relative,expected in RETIMED_SOURCES.items():
        need(digest(retimed_root/relative) == expected,'Exact original retiming source '+relative)
    F = load(RETIMED/'native.py','hybrid_live_retimed_supplier')
    # Only source locations are rebound; the retained source algorithm,
    # changes and phase recipes remain byte-identical to the PR head.
    F.ROOT = retimed_root
    F.BASE = retimed_root/'research/kappa-rebuild/complex/full-identity-certificates'
    replay,canonical,programs = F.run(phase_check=True)
    need(json.loads(json.dumps(replay)) == read(RETIMED/'NATIVE-RESULT.json.gz'),
         'Exact complete published retiming receipt regenerated')
    need(replay['status'] == 'PASS_RETIMED_BOTH_ORIENTATIONS_ALL_632_COLUMNS',
         'Complete independent arbitrary-input replay in both orientations')
    original_canonical = read(F.BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    original_words = read(F.BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    need(canonical['start'][:224] == original_canonical['start'][:224] and
         canonical['final'][:224] == original_canonical['final'][:224],
         'Every external main input and output reference frame is unchanged')
    checks = {}
    native_edges = []
    for direction,program in programs.items():
        original = original_words[direction]
        need([e for e in original if e[0] == 'warp'] == [e for e in program if e[0] == 'warp'],
             'Every original warp operator and its contact frames are unchanged')
        need([e[1] for e in original if e[0] == 'scalar'] == [e[1] for e in program if e[0] == 'scalar'],
             'Every original scalar action and its chronological ordering are unchanged')
        need(Counter(e[-1] for e in program if e[0] == 'center') == Counter({8:8}),
             'All eight complete original owned-center queries are retained')
        need(not any(e[0] in ('adapter','residual_adapter') and e[2] >= 224 for e in program),
             'Old helper wrapper markers are replaced by the new complete boundary recipes')
        native_edges.append({(e[3],e[4]) for e in program if e[0] == 'climb'})
        literal = replay['native'][direction]
        need(literal['independent_persistent_columns'] == 632 and
             literal['arbitrary_owned_C0_cleared'] and literal['scalar_frames_checked'],
             'All persistent inputs, scalar contact frames and the owned center are checked')
        checks[direction] = literal['second_literal']
        need(checks[direction]['independent_borrowed_input_fields'] == 632 and
             checks[direction]['expected_restored_helpers'] == 408 and
             checks[direction]['free_warp_operator_endpoint_matches'],
             'Second literal interpreter checks every arbitrary source and helper endpoint')
    need(native_edges[0] == native_edges[1],'Both orientations have the same retimed transport edges')
    physical = {(row['old'],row['new']):row for row in replay['new_physical_edges_and_boundaries']}
    for role in range(224,632):
        edge = (canonical['start'][role],canonical['final'][role])
        need(edge in physical,'Every complete helper boundary has a physical phase recipe')
        row = physical[edge]
        width = len(canonical['frames'][edge[1]])-len(canonical['frames'][edge[0]])
        need(width > 0 and row['rank'] == width and
             all(row['recipes'][direction]['rank'] == width for direction in ('forward','backward')),
             'Every arbitrary helper is positively productive with both complete phases')
    helpers = {int(k):v for k,v in replay['helpers'].items()}
    paid = {int(k):v for k,v in replay['paid'].items()}
    need(helpers == parameters.LOCAL_HELPERS and paid == parameters.LOCAL_PAID,
         'Exact current retimed helper and paid profiles')
    need(sum(helpers.values()) == 408,'All helpers retain distinct arbitrary owners')
    need((replay['changed_entrances'],replay['changed_exits'],replay['changed_scalar_frames']) == (117,42,395),
         'Exact inherited retiming scope')
    for direction,expected in (('forward',158120),('backward',158168)):
        need(checks[direction]['conservative_real_scalar_primitive_allowance'] == expected and
             replay['native'][direction]['real_scalar_allowance'] == expected,
             'Both independent scalar invoices equal the unchanged source invoice')
    return {'schema':'source-bound-retimed-arbitrary-native-supplier/1',
            'status':'PASS_ALL_632_INPUTS_BOTH_DIRECTIONS_AND_ALL_RETIMED_HELPER_PHASES',
            'local_helper_profile':helpers,'local_paid_profile':paid,'local_replays':checks,
            'retimed_native_receipt':replay,'retimed_source_head':RETIMED_HEAD,
            'retimed_artifact_sha256':RETIMED_FILES,'retimed_source_sha256':RETIMED_SOURCES,
            'external_main_boundaries_unchanged':True,'all_scalar_actions_and_order_unchanged':True,
            'all_warp_contacts_unchanged':True,'scalar_contact_frames_retimed':395,
            'all_408_helpers_arbitrary':True,'whole_helper_boundary_recipes':408,
            'distinct_physical_edge_and_boundary_recipes':len(physical),
            'fresh_arbitrary_input_fields':632,'authenticated_original_files':authenticated,
            'inherited_native_gate':inherited_gate,
            'boundary_movement_allowance':'Every new whole-helper left/right monomial and transport recipe contributes its full finite route and phase cost.'}
