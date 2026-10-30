#!/usr/bin/env python3
"""Strict native/owner/operator invoice for PR4076 plus receiver sharing.

No native execution is started here. Both exact five-stage outputs must exist.
Every owner reassignment and original phase-axis window is rechecked. The
owner MOVES file reassigns helpers; it is not a phase-axis transfer overlay.
Credits: PR4076/Rohan Arun, PR3945/Dugongue, PR3638/3734/3815 owner predicates,
the adaptive native recount and the operator-correction gauge proof.
Apache-2.0. Substantial OpenAI assistance. Full outer release is separate.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
P4076 = SCOPE / 'sources/PR4076/research/staged544-triple-entry-fill'
P3945 = SCOPE / 'sources/PR3945/research/staged544-terminal-gap-fill'
sys.path.insert(0, str(SCOPE / 'operator-correction'))
import full_operator as F
import t360_admission as T

PROFILE = {1:2487, 2:713, 3:224, 4:102, 5:20, 8:8}
WIDTHS = {5:28, 6:18, 7:56, 8:93, 9:213}
IDLE = {3:22842, 5:1890, 48:138438}
PAID = {1:8057880, 2:2310120, 3:748602, 4:330480, 5:66690, 8:25920, 48:138438}
LOWER = Q('.001730970419199163702738')
UPPER = Q('.001730970419199163702739')


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, default=HERE / 'candidate')
    ap.add_argument('--native-root', type=Path, default=HERE)
    ap.add_argument('--out', type=Path, default=HERE / 'invoice')
    ap.add_argument('--operator-output', type=Path, default=HERE / 'T360-OPERATOR-ADMISSION.json')
    args = ap.parse_args()
    F.require(__debug__, 'assertions enabled')
    F.require(not args.out.exists(), 'fresh invoice output directory')
    F.require(not args.operator_output.exists(), 'fresh operator output file')
    pins = {}
    def pin(path):
        pins[path.resolve().relative_to(REPO).as_posix()] = F.sha(path)
        return F.read(path)
    inv_path = REPO / 'research/kappa-global-continuation/invoice-analysis/invoice.py'
    native_path = REPO / 'research/kappa-adaptive-continuation/global-budget/native_owner_invoice.py'
    I = module(inv_path, 'late_exact_invoice')
    N = module(native_path, 'late_native_recount')
    construction = pin(args.candidate / 'CONSTRUCTION.json')
    F.require(construction['status'] == 'PASS_FINITE_STAGED_RECEIVER_COMPOSITION_NATIVE_PENDING', 'complete finite construction')
    for rel, digest in construction['input_files'].items():
        F.require(F.sha(REPO / rel) == digest, 'construction source binding')
        pins[rel] = digest
    widths, profiles, provider_bindings, native_receipts = {}, {}, {}, {}
    for tag, pid in [('base','gauge44'), ('extra','extra')]:
        root = args.native_root / ('native-' + tag)
        local = root / 'native/local'
        candidate_path = args.candidate / ('BORROW-WORD-43' + tag + '.json.gz')
        candidate = pin(candidate_path)
        result = pin(root / 'RESULT.json')
        F.require(result['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'completed native provider')
        F.require([s['step'] for s in result['steps']] == ['native','ledgers','local-replay','wrappers','phases']
                  and all(s['exit_code'] == 0 for s in result['steps']), 'every ordered native stage passed')
        F.require(result['word_sha256'] == F.sha(candidate_path) == F.sha(root / 'INPUT.json.gz'), 'exact native input bytes')
        F.require(pin(root / 'INPUT.json.gz') == candidate == pin(local / 'FULL-WORD.json.gz'), 'complete native word equality')
        for rel, digest in result['source_sha256'].items():
            p = root / 'source' / rel
            F.require(F.sha(p) == digest, 'executed compiler source')
            pins[p.resolve().relative_to(REPO).as_posix()] = digest
        word = pin(local / 'CANONICAL-WORD.json.gz')
        programs = pin(local / 'LOCAL-PROGRAMS.json.gz')
        checks = pin(local / 'LOCAL-CHECKS.json')
        replay = pin(local / 'INDEPENDENT-LOCAL-REPLAY.json')
        phases = pin(local / 'CLIFFORD-REVIEW.json')
        adapters = pin(local / 'RESIDUAL-ADAPTERS.json')['recipes']
        F.require(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'independent native semantics')
        F.require(phases['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES', 'exact native phase recipes')
        F.require(replay['canonical_word_sha256'] == phases['canonical_word_sha256'] == F.sha(local / 'CANONICAL-WORD.json.gz'), 'native proof word binding')
        F.require(replay['local_programs_sha256'] == F.sha(local / 'LOCAL-PROGRAMS.json.gz'), 'native emitted stream binding')
        F.require(word['R'] == 408 and word['h'] == 9 and word['v'] == 112
                  and len(word['start']) == len(word['final']) == 632 and len(word['zero_buffers']) == 91, 'native inventory')
        origin = sorted(set(range(224,704)) - set(candidate['removed']))
        F.require(word['helper_origin'] == origin and word['ports'] == candidate['ports'], 'ordered native role and port map')
        full = N.basis([1 << i for i in range(9)])
        for reg, old_reg in enumerate(list(range(224)) + origin):
            start = N.basis([candidate['ports'][old_reg]]) if old_reg < 112 else N.basis(candidate['start_extra'].get(str(old_reg), []))
            if 112 <= old_reg < 224:
                port = candidate['ports'][old_reg-112]
                end = N.basis([x for x in range(512) if not ((x & port).bit_count() & 1)])
            else:
                end = N.basis(candidate['helper_final'].get(str(old_reg), full))
            F.require(N.basis(word['frames'][word['start'][reg]]) == start
                      and N.basis(word['frames'][word['final'][reg]]) == end, 'every actual native endpoint')
        width = [len(N.basis(word['frames'][word['final'][r]])) - len(N.basis(word['frames'][word['start'][r]])) for r in range(224,632)]
        F.require(Counter(width) == WIDTHS and min(width) > 0, 'exact staged width inventory')
        for helper, rank in enumerate(width):
            begin, end = word['start'][224+helper], word['final'][224+helper]
            key = str(begin) + ':' + str(end)
            if key in adapters:
                F.require(adapters[key]['rank'] == rank, 'native residual boundary rank')
            else:
                F.require(end == 1 and word['frames'][1] == [256,128,64,32,16,8,4,2,1], 'only ordinary full completion may omit a residual adapter')
        F.require({int(r):n for r,n in word['local_profile'].items()} == PROFILE, 'actual native local tariff')
        for direction in ('forward','backward'):
            payload = json.dumps(programs[direction], sort_keys=True, separators=(',', ':')).encode()
            F.require(hashlib.sha256(payload).hexdigest() == checks[direction]['sha256'], 'actual orientation payload')
            F.require(N.recount(I, word, programs[direction]) == PROFILE, 'independent native orientation recount')
            F.require(checks[direction]['all_columns'] == 632 and checks[direction]['zero_buffers_returned_to_zero'] == 91, 'complete native scalar/owned checks')
        F.require(sum(r*n for r,n in PROFILE.items()) == 1792+64+sum(width), 'exact local width/rank conservation')
        widths[tag], profiles[tag] = width, PROFILE
        provider_bindings[tag] = {'candidate_sha256':F.sha(candidate_path), 'canonical_native_sha256':F.sha(local / 'CANONICAL-WORD.json.gz'),
            'native_receipt_sha256':F.sha(root / 'RESULT.json'), 'actual_width_inventory':WIDTHS}
        native_receipts[pid] = {'word_sha256':F.sha(candidate_path), 'native_word_sha256':F.sha(local / 'CANONICAL-WORD.json.gz'),
            'programs_sha256':F.sha(local / 'LOCAL-PROGRAMS.json.gz'), 'scalar_checks':checks}
        print('PASS_LATE_NATIVE_BINDING', tag, flush=True)

    F.authenticate()
    for p in F.PINS:
        pins[p.relative_to(REPO).as_posix()] = F.sha(p)
    for rel, digest in F.read(F.CELL)['source_pins'].items():
        pins[rel] = digest
    phases = pin(F.PHASES)
    owner = P4076 / 'owner'
    data = {}
    for name in ('TEMPLATE.json.gz','PLAN.json.gz','ORDER.json','DISPATCH.json'):
        data[name] = pin(owner / 'inputs' / name)
        F.require(data[name] == pin(P3945 / 'owner/inputs' / name), 'unchanged exact T360 controller input')
    template, plan, order, rows_dispatch = [data[n] for n in ('TEMPLATE.json.gz','PLAN.json.gz','ORDER.json','DISPATCH.json')]
    F.require(template['exact_data_phase_recipe_sha256'] == F.sha(F.PHASES), 'unchanged exact global phase recipe')
    F.require(len(order) == 3240 and set(map(tuple,order)) == {(s,r) for s in range(9) for r in range(360)}, 'all stage/replica calls')
    clock = {tuple(call):t for t,call in enumerate(order)}
    F.require(all(clock[s,r] < clock[s+1,r] for s in range(8) for r in range(360)), 'ordered owner stages')
    substitution = {'gauge44':'base', 'extra':'extra'}
    dispatch = {(s,r):substitution[pid] for s,r,pid in rows_dispatch}
    F.require(len(rows_dispatch) == len(dispatch) == 3240 and set(dispatch) == set(clock), 'complete actual dispatch')
    F.require([int(r['q']) for r in phases['recipes']] == candidate['ports'], 'all112 exact ordered port recipes')
    normals = [F.normalize(template, recipe) for recipe in phases['recipes']]
    original = F.normalize(F.read(F.TEMPLATE), phases['recipes'][0])
    F.require(all(n['events'] == original['events'] for n in normals), 'actual normalized controller equals the proved baseline')
    blocks = T.blocks(template)
    pairs = {e['stage']:e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    windows = {}
    for o in range(360):
        last = [(-1,-1)] * 8
        for s in range(9):
            tick = clock[s,o]
            for index, event in enumerate(blocks[s]):
                if event['kind'] == 'idle_cover_sweep':
                    for side, child in enumerate(event['child_indices']):
                        stream = 2*event['pair'] + side
                        if str(child) in plan['pairs']:
                            F.require(stream == 2*plan['pairs'][str(child)] + plan['sides'][str(child)], 'exact owner stream routing')
                        else:
                            F.require(all(r['idle_children'][child]['rank'] == 0 for r in phases['recipes']), 'only unused zero child may omit routing')
                        F.require((o,child) not in windows, 'one physical child window')
                        windows[o,child] = last[stream], (tick,index), stream
                for stream in T.touches(event,pairs):
                    last[stream] = tick,index
    shared = defaultdict(list)
    for (o,c),(lo,hi,stream) in windows.items():
        if str(c) in plan['pairs']:
            shared[o,stream].append((lo,hi))
    F.require(all(all(max(a,c) >= min(b,d) for j,(a,b) in enumerate(xs) for c,d in xs[j+1:]) for xs in shared.values()), 'nonoverlapping physical stream windows')
    fill = pin(owner / 'FILL.json.gz')
    old_fill = pin(owner / 'inputs/PR3945-FILL.json.gz')
    F.require(F.sha(owner / 'inputs/PR3945-FILL.json.gz') == F.sha(P3945 / 'owner/FILL.json.gz'), 'actual PR3945 owner predecessor')
    pins[(P3945 / 'owner/FILL.json.gz').relative_to(REPO).as_posix()] = F.sha(P3945 / 'owner/FILL.json.gz')
    moves = pin(owner / 'MOVES.json.gz')
    F.require(moves['columns'] == ['role_index','owner_replica','child','port'], 'owner-reassignment schema, not phase-axis transfers')
    moved = {}
    for role,o,c,p in moves['moves']:
        F.require(role not in moved and old_fill['rows'][role][2:5] != [o,c,p], 'one real reassignment per moved role')
        moved[role] = [o,c,p]
    F.require(len(moved) == 70876, 'all declared reassigned roles')
    F.require(fill['columns'] == old_fill['columns'] == ['time','helper','owner_replica','child','port','offset']
              and fill['dispatch_overrides'] == old_fill['dispatch_overrides'] == [], 'exact fill schema')
    F.require(len(fill['rows']) == len(old_fill['rows']) == 1321920, 'every helper occurrence')
    occupied, used = defaultdict(int), defaultdict(int)
    width_mass, seen_family = 0, set()
    for j,(row,old_row) in enumerate(zip(fill['rows'],old_fill['rows'])):
        F.require(len(row) == 6 and all(type(x) is int for x in row), 'integer physical record')
        tick,helper,o,c,p,offset = row
        F.require((tick,helper) == divmod(j,408) and row[:2] == old_row[:2], 'complete ordered call/helper identities')
        F.require(row[2:5] == moved.get(j,old_row[2:5]), 'exact declared owner reassignment')
        F.require(0 <= o < 360 and 0 <= p < 112 and (o,c) in windows, 'valid physical child')
        if helper == 0:
            seen_family = set()
        lo,hi,stream = windows[o,c]
        F.require(lo < (tick,-1) < hi, 'hosted phase remains between actual scalar observations')
        physical = 896*o + 112*stream + p
        F.require(physical not in seen_family, 'same-call physical family injection')
        seen_family.add(physical)
        stage,replica = order[tick]
        F.require(physical//224 != 4*replica+pairs[stage], 'productive data/helper nonaliasing')
        width = widths[dispatch[stage,replica]][helper]
        axes = phases['recipes'][p]['idle_children'][c]['orthogonal_axes']
        key = o,c,p
        F.require(offset == used[key] and 0 <= offset and offset+width <= len(axes), 'compact offset and native rank capacity')
        mask = ((1 << width)-1) << offset
        F.require(occupied[key] & mask == 0, 'pairwise disjoint original phase-axis cells')
        occupied[key] |= mask
        used[key] += width
        width_mass += width
    idle = Counter()
    for o in range(360):
        for p,recipe in enumerate(phases['recipes']):
            for c,child in enumerate(recipe['idle_children']):
                rank = len(child['orthogonal_axes']) - occupied[o,c,p].bit_count()
                F.require(rank >= 0, 'nonnegative physical residual')
                if rank:
                    idle[rank] += 1
    F.require(dict(idle) == IDLE, 'independently recounted actual residual profile')
    original_mass = 360*sum(len(c['orthogonal_axes']) for r in phases['recipes'] for c in r['idle_children'])
    residual_mass = sum(r*n for r,n in idle.items())
    F.require(width_mass+residual_mass == original_mass, 'every original phase axis accounted once')
    paid = Counter(idle)
    for stage,replica in order:
        paid.update(profiles[dispatch[stage,replica]])
    F.require(dict(paid) == PAID and sum(r*n for r,n in paid.items()) == 65088*360, 'complete actual profile and raw deficit')
    F.require(max(paid) <= I.C.max_idle_rank(73), 'recursive halving guard')
    print('PASS_LATE_OWNER_AND_PHASE_WINDOWS', len(fill['rows']), 'roles', len(moved), 'reassignments', flush=True)
    root = I.root(paid,73,322560)
    lower,upper = map(Q,root['rational'])
    F.require((lower,upper) == (LOWER,UPPER), 'exact three-entry plus receiver root bracket')
    rational_path = P3945 / 'vendor/rational_price.py'
    moment_path = REPO / 'research/native-complex-moment552/engines/moment.py'
    R = module(rational_path,'late_second_price')
    E = module(moment_path,'late_third_price')
    signed = dict(paid)
    signed[73] = -322560
    F.require(R.interval(signed,lower)[1] < 0 < R.interval(signed,upper)[0], 'second exact rational root signs')
    F.require(E.moment(dict(paid),73,322560,lower)[1] < 1 < E.moment(dict(paid),73,322560,upper)[0], 'third exact rational root signs')
    for p in (Path(__file__),inv_path,native_path,rational_path,moment_path,I.ENGINE_PATH,Path(F.__file__),Path(T.__file__)):
        pins[p.resolve().relative_to(REPO).as_posix()] = F.sha(p)
    result = {'status':'PASS_FRESH_NATIVE_LITERAL_OWNERS_AND_THREE_ENGINE_COMPLEX_INVOICE',
        'root':root, 'profile':dict(sorted(paid.items())), 'local_profile':{'gauge44':PROFILE,'extra':PROFILE},
        'idle_profile':dict(sorted(idle.items())), 'native_receipts':native_receipts,
        'helper_rows':1321920, 'calls':3240, 'replicas':360, 'owner_windows':6480,
        'productive_families':322560, 'physical_families':323069, 'native_orientations_recounted':4,
        'helpers':408, 'width_inventory':WIDTHS, 'owner_roles_reassigned_vs_PR3945':len(moved),
        'gain_over_frozen_primary_complex_lower':str(lower-Q('.001730824595303184580890')),
        'conditional_kappa_if_inherited_interfaces_hold':str(lower-Q(1,10**46)-Q(1,10**70)),
        'full_global_operator_gate':str(args.operator_output.resolve().relative_to(REPO)),
        'full_conditional_release_completed':False,
        'scope':'Fresh source-bound native phase/operator receipts, independent full owner/axis-window recount and three-engine exact price. Full inherited resource/precision/outer release is a separate obligation.',
        'source_pins':dict(sorted(pins.items()))}
    args.out.mkdir(parents=True)
    invoice_path = args.out / 'RESULT.json'
    invoice_path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    pins[invoice_path.resolve().relative_to(REPO).as_posix()] = F.sha(invoice_path)
    operator = {'status':'PASS_ACTUAL_T360_ALL_CHARACTER_OPERATOR_ADMISSION',
        'actual_calls':3240, 'actual_hosted_rows':1321920, 'owner_child_windows':len(windows),
        'actual_provider_bindings':provider_bindings,
        'explicit_source_dispatch_substitution':substitution,
        'original_axis_mass':original_mass, 'hosted_width_mass':width_mass, 'residual_rank_mass':residual_mass,
        'actual_residual_profile':dict(sorted(idle.items())), 'symbolic_ports':len(normals),
        'exact_phase_identities':sum(n['phase_identities'] for n in normals),
        'normalized_graph_equals_historical_proved_graph':True,
        'all_Fourier_characters':True, 'all_positive_tensor_multiplicities':True,
        'no_axis_transfer_overlay':True, 'owner_reassignments':len(moved),
        'owner_MOVES_semantics':'70876 changes of role->(owner,child,port), with compact offsets rebuilt. No original idle phase axis is transferred between child slots.',
        'operator_argument':'Every exact new native helper width occupies disjoint original child axes inside its observer-free physical stream interval. Hosted phases commute to their own original residual endpoint; hosted and complementary phases reassemble the exact original child. The unchanged signed Z4 gauge/controller proof yields C_all I_8 for all characters and positive tensor multiplicities, including arbitrary correlated dirty inputs.',
        'complete_owner_invoice_sha256':F.sha(invoice_path),
        'independent_residual_profile_matches_complete_invoice':True,
        'retained_interfaces':['Exact native endpoint/canonicalization and owner-chart embedding into the common cover','Common-cover conjugation and final all-live translation identity','Uniform physical/tape/precision/recurrence/outer interfaces; full conditional release remains separate'],
        'input_files':dict(sorted(pins.items()))}
    args.operator_output.parent.mkdir(parents=True,exist_ok=True)
    args.operator_output.write_text(json.dumps(operator,sort_keys=True,indent=2)+'\n')
    print(result['status'], root['decimal'], flush=True)
    print(operator['status'],len(normals),'ports',flush=True)


if __name__ == '__main__':
    main()
