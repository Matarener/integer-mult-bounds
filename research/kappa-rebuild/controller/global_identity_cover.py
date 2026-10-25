#!/usr/bin/env python3
"""Bind a complete p2 mixed supplier to native words, owners and exact phases.

Apache-2.0; substantial OpenAI assistance. Native words and endpoint recipes
are attributed and pinned through the independently reconstructed complex
package. This certificate is a finite ideal construction, not the mixed
recursion or the rounded integer-multiplication transfer theorem.
"""
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMPLEX = HERE.parent/'complex'
PAIRS = ((93,8,8),(56,7,9),(56,9,7),(19,5,9))
MIDDLE = ((29,0),(28,5),(18,6),(56,7),(93,8))
STAGES = ((0,'forward'),(0,'backward'),(0,'forward'),(1,'backward'),(1,'forward'))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def gf2_basis(vectors):
    basis = {}
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length()-1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return basis


def coordinate_map(axes, dim=41):
    """An explicit invertible address map with the desired first columns."""
    columns = list(axes)
    need(len(gf2_basis(columns)) == len(columns), 'Independent target axes')
    for j in range(dim):
        if len(gf2_basis(columns+[1 << j])) > len(columns):
            columns.append(1 << j)
    need(len(columns) == dim, 'Full invertible coordinate extension')
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(dim)) for i in range(dim)]
    augmented = [row | (1 << (dim+i)) for i,row in enumerate(rows)]
    for j in range(dim):
        pivot = next(i for i in range(j,dim) if (augmented[i] >> j) & 1)
        augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
        for i in range(dim):
            if i != j and (augmented[i] >> j) & 1:
                augmented[i] ^= augmented[j]
    inverse_rows = [row >> dim for row in augmented]
    need(all((row & ((1 << dim)-1)) == 1 << i for i,row in enumerate(augmented)),
         'Explicit inverse address matrix')
    return dict(columns=columns, inverse_rows=inverse_rows)


def local_bindings():
    receipt_path = COMPLEX/'full-identity-certificates/RESULT.json'
    data = read(receipt_path)
    pins = {str(receipt_path.relative_to(ROOT)):digest(receipt_path)}
    helpers = {}
    for tag,provider in data['providers'].items():
        need(provider['all_408_helpers_autonomous'] and provider['all_632_persistent_inputs_arbitrary'],
             'Complete native arbitrary-input contract')
        need(provider['external_cleanup_fields'] == 0 and provider['owned_C_fields'] == 1,
             'One explicit owned center; no hidden cleanup bank')
        for filename,wanted in provider['artifacts'].items():
            path = receipt_path.parent/filename
            need(digest(path) == wanted, 'Native artifact '+filename)
            pins[str(path.relative_to(ROOT))] = wanted
        path = ROOT/provider['helper_boundary']['certificate']
        need(digest(path) == provider['helper_boundary']['certificate_sha256'], 'Actual helper boundaries')
        pins[str(path.relative_to(ROOT))] = digest(path)
        helpers[tag] = read(path)
    return data,pins,helpers


def main_contacts(n, F, phases):
    """Every complete native entrance and exit, including conjugate B words.

    After the input affine views, all632 local roles share the SAME spectator
    axes9..(9+8s-1). Thus the native internal scalar contacts are unchanged.
    Different port views cancel on the per-port identity response.
    """
    out = []
    for stage,(pair,direction) in enumerate(STAGES):
        sign = 1 if direction == 'forward' else -1
        spectator = n.frame((a,1) for a in n.AXES[9:9+8*stage])
        need(all(a >= 512 and a < 1 << 41 for a,c in spectator), 'Spectators outside native nine axes')
        for port,recipe in enumerate(phases['recipes']):
            q = recipe['q']
            g = n.source_route(phases, stage, port)
            need(all(g[i] == 1 << i for i in range(41,73)) and all(a < 1 << 41 for a in g[:41]),
                 'The ambient41 construction leaves all higher coordinates untouched')
            input_x = n.frame([(q,1)]) if stage == 0 else n.completed(stage-1)
            input_y = () if stage == 0 else n.frame(list(n.completed(stage-1))+[(q,-1)])
            local_start_x = n.frame(list(spectator)+[(q,sign)])
            local_start_y = spectator
            local_end_x = n.frame(list(spectator)+[(a,sign) for a in n.AXES[:9]])
            local_end_y = n.frame(list(local_end_x)+[(q,-sign)])
            output_x = n.completed(stage)
            output_y = n.frame(list(output_x)+[(q,-1)])
            maps = dict(entry_X=F.between(n,input_x,g,local_start_x),
                        entry_Y=F.between(n,input_y,g,local_start_y),
                        exit_X=F.between(n,local_end_x,g,output_x),
                        exit_Y=F.between(n,local_end_y,g,output_y))
            out.append(dict(stage=stage,pair=pair,direction=direction,port=port,
                            common_spectator_frame=list(spectator),maps=maps))
    return out


def make_windows(n, phases):
    windows = []
    for kind,pair,stages in (('early',1,[0,1]),('middle',1,[2]),('late',0,[3,4])):
        patterns = [([a,b] if kind != 'middle' else [a])
                    for spec in (PAIRS if kind != 'middle' else MIDDLE)
                    for _ in range(spec[0])
                    for a,b in ([spec[1:]] if kind != 'middle' else [(spec[1],0)])]
        need(len(patterns) == 224, '224 distinct idle owners')
        for index,widths in enumerate(patterns):
            side,port = ('X' if index < 112 else 'Y'),index % 112
            recipe = phases['recipes'][port]
            if kind == 'early':
                axes = recipe['idle_children'][0]['orthogonal_axes']
                shift = recipe['idle_children'][0]['translation_after']
                old = n.frame([(recipe['q'],1)]) if side == 'X' else ()
                target = n.completed(1)
            elif kind == 'middle':
                axes = list(n.AXES[17:25]); shift = 0
                old = n.completed(1); target = n.completed(2)
            else:
                axes = list(n.AXES[25:41]); shift = 0
                old = n.completed(2); target = n.completed(4)
            if side == 'Y':
                if kind != 'early':
                    old = n.frame(list(old)+[(recipe['q'],-1)])
                target = n.frame(list(target)+[(recipe['q'],-1)])
            need(len(axes) == (8 if kind == 'middle' else 16), 'Exact idle window width')
            actual = n.frame(list(old)+[(a,1) for a in axes]+[(shift,2)])
            need(n.polynomial(actual) == n.polynomial(target), 'Whole idle path including absolute phase')
            windows.append(dict(kind=kind,owner=f'{side}{pair}:{port}',pair=pair,port=port,side=side,
                                stages=stages,widths=widths,axes=axes,translation_after=shift))
    return windows


def split_axes(axes, maximum=5):
    return [axes[i:i+maximum] for i in range(0,len(axes),maximum)]


def build_assignment(n, phases, local, helpers, mask):
    tags = [('FOUR' if mask[s] else 'THREE')+'-base' for s in range(5)]
    windows = make_windows(n, phases)
    # FOUR has one fewer8 and one extra7. Replace the FIRST eight-slot in each
    # stage: the same physical owner in a two-stage window whenever possible.
    for stage in range(5):
        if mask[stage]:
            candidates = [w for w in windows if stage in w['stages'] and w['widths'][w['stages'].index(stage)] == 8]
            need(candidates, 'A hosted width8 exists for FOUR adjustment')
            w = candidates[0]
            w['widths'][w['stages'].index(stage)] = 7
    pools = []
    for tag in tags:
        pool = defaultdict(deque)
        for row in helpers[tag]['recipes']:
            pool[row['width']].append(row['role'])
        pools.append(pool)
    bindings = []; residuals = []; paid = Counter(); targets = Counter({41:448})
    for window in windows:
        cursor = 0
        for stage,width in zip(window['stages'],window['widths']):
            if not width:
                continue
            need(pools[stage][width], 'Actual available helper role')
            role = pools[stage][width].popleft()
            axes = window['axes'][cursor:cursor+width]; cursor += width
            bindings.append(dict(stage=stage,role=role,owner=window['owner'],axes=axes,width=width,
                                 kind='original_idle',window=window['kind']))
        rest = window['axes'][cursor:]
        for axes in split_axes(rest):
            residuals.append(dict(owner=window['owner'],after_stage=max(window['stages']),axes=axes,
                                  rank=len(axes),kind='idle_remnant'))
            paid[len(axes)] += 1
    fresh = []
    for stage,pool in enumerate(pools):
        for width,roles in sorted(pool.items()):
            for role in roles:
                owner = f'G{stage}:{role}'
                target = max(6,width)
                axes = list(n.AXES[:width])
                bindings.append(dict(stage=stage,role=role,owner=owner,axes=axes,width=width,kind='fresh'))
                fresh.append(dict(owner=owner,target_rank=target,native_width=width,stage=stage))
                targets[target] += 1
                for extra in split_axes(list(n.AXES[width:target])):
                    residuals.append(dict(owner=owner,after_stage=stage,axes=extra,rank=len(extra),kind='fresh_topup'))
                    paid[len(extra)] += 1
    for stage,tag in enumerate(tags):
        data = local['providers'][tag]['split_replays'][STAGES[stage][1]]['independent_native_replay']
        paid.update({int(r):count for r,count in data['paid_profile'].items()})
        chosen = [b for b in bindings if b['stage'] == stage]
        need(len(chosen) == 408 and {b['role'] for b in chosen} == set(range(224,632)), 'Every native role exactly once')
        need(len({b['owner'] for b in chosen}) == 408, 'Injective helper physical owners')
        active_pair = STAGES[stage][0]
        active = {f'{side}{active_pair}:{p}' for side in ('X','Y') for p in range(112)}
        need(not active & {b['owner'] for b in chosen}, 'No helper aliases a live data field')
    need(targets == Counter({41:448,6:146,9:803}), 'Complete productive output inventory')
    need(sum(k*v for k,v in targets.items())-sum(k*v for k,v in paid.items()) == 128,
         'Exact conserved rank margin including every completion')
    need(max(paid) < min(targets), 'Strict child hierarchy')
    # Explicit wrappers act only around a WHOLE native invocation. They are
    # never used as permission to retag an intermediate native scalar contact.
    maps = {}
    for b in bindings:
        key = ','.join(map(str,b['axes']))
        if key not in maps:
            maps[key] = coordinate_map(b['axes'])
        b['coordinate_map'] = key
        b['boundary_recipe'] = dict(provider=tags[b['stage']],role=b['role'],
                                   direction=STAGES[b['stage']][1],
                                   selector='certificate.directions.direction.existing_native_boundary_normal_form')
    scalar = sum(local['providers'][tag]['split_replays'][STAGES[s][1]]['independent_native_replay']
                 ['conservative_real_scalar_primitive_allowance'] for s,tag in enumerate(tags))
    scalar += 3*224*8+224*2  # Three bridges, conservative terminal negations.
    return dict(providers=tags,targets=dict(sorted(targets.items())),paid=dict(sorted(paid.items())),
                rank_margin=128,main_fields=448,fresh_fields=len(fresh),productive_fields=448+len(fresh),
                owned_center_fields=1,external_cleanup_fields=0,scalar_allowance=scalar,
                helper_bindings=bindings,owner_coordinate_maps=maps,windows=windows,
                paid_residuals=residuals,fresh_outputs=fresh)


def controller_replay(omit_bridge=False):
    """Four independent per-port data columns, no forced zeros or equality."""
    rows = [[Q(i == j) for j in range(4)] for i in range(4)]
    maximum = Q(1); events = []
    def add(dst,src,c):
        nonlocal maximum
        rows[dst] = [a+c*b for a,b in zip(rows[dst],rows[src])]
        maximum = max(maximum,sum(map(abs,rows[dst])))
    def local(pair,backward):
        x,y = 2*pair,2*pair+1
        add(x if backward else y,y if backward else x,Q(-1 if backward else 1))
        events.append(['local',pair,'backward' if backward else 'forward'])
    def bridge(src,dst,c):
        add(2*dst,2*src,Q(c)); add(2*src+1,2*dst+1,Q(-c))
        events.append(['bridge',src,dst,c])
    local(0,False); local(0,True); bridge(1,0,1); local(0,False)
    if not omit_bridge:
        bridge(1,0,-1)
    local(1,True); local(1,False); bridge(0,1,1)
    before = [row[:] for row in rows]
    for p in range(2):
        x,y = 2*p,2*p+1
        rows[x],rows[y] = rows[y],[-a for a in rows[x]]
    identity = [[Q(i == j) for j in range(4)] for i in range(4)]
    if not omit_bridge:
        need(rows == identity, 'Full controller after signed swap')
        need(before == [[Q(0),Q(-1),Q(0),Q(0)],[Q(1),Q(0),Q(0),Q(0)],
                        [Q(0),Q(0),Q(0),Q(-1)],[Q(0),Q(0),Q(1),Q(0)]], 'Exact preterminal signed swaps')
    return dict(schedule=events,preterminal_matrix=[[str(x) for x in row] for row in before],
                terminal_matrix=[[str(x) for x in row] for row in rows],
                max_logical_prefix_l1=str(maximum),identity=rows == identity)


def terminal_phases(n, phases):
    records = []
    for port,r in enumerate(phases['recipes']):
        q = r['q']; full = n.completed(4)
        # Initial logicalX=Cq^-1 rawX, logicalY=rawY. Signed exchange puts
        # F41*Cq^-2 on the originalX output and F41 on originalY.
        doubled = n.frame(list(full)+[(q,-2),(q,2)])
        need(n.polynomial(doubled) == n.polynomial(full), 'Final translation restores exact full41 transform')
        need(n.polynomial(n.frame(list(full)+[(q,-2)])) != n.polynomial(full),
             'Omitting terminal phase repair is actually wrong')
        records.append(dict(port=port,original_X_output_translation=q,original_Y_output_translation=0,
                            both_final_ranks=41,full_phase_equality=True))
    return records


def run():
    F = load(HERE/'frame_exchange.py','global_identity_contacts')
    n = load(F.NATIVE,'global_identity_native_common')
    packet,phases = n.load_sources()
    local,pins,helpers = local_bindings()
    contacts = main_contacts(n,F,phases)
    cases = []
    for mask in product((0,1),repeat=5):
        case = build_assignment(n,phases,local,helpers,mask)
        cases.append(case)
    all_three = cases[0]
    need(all_three['paid'] == {1:12565,2:3621,3:1217,4:510,5:169}, 'Independently regenerated complete invoice')
    main = controller_replay()
    need(not controller_replay(True)['identity'], 'Missing inverse bridge negative control')
    phases_final = terminal_phases(n,phases)
    for path in (HERE/'frame_exchange.py',F.NATIVE):
        pins[str(path.relative_to(ROOT))] = digest(path)
    return dict(schema='complete-native-p2-mixed-identity-owner-cover/1',
                status='PASS_FINITE_IDEAL_NATIVE_OWNER_PHASE_AND_COMPLETE_INVOICE',
                generator_sha256=digest(__file__),sources=pins,immutable_phase_sources=n.PINS,
                main_contacts=contacts,contact_count=5*112*4,terminal_phases=phases_final,
                controller=main,all_three=all_three,
                provider_cases=[{k:v for k,v in case.items() if k in ('providers','targets','paid','rank_margin','scalar_allowance')}
                                for case in cases],
                all32_finite_provider_sequences_have_native_owners=True,
                arbitrary_productive_input_fields=1397,owned_center_arbitrary_at_entry_zero_at_return=True,
                helper_normalization='Apply the pinned whole-helper pre/post monomials and the listed coordinate inverse/map around each whole native call. The internal native word is unchanged.',
                spectator_argument='After main input views each local word has common spectator axes9..9+8s-1. A helper is arbitrary under its independent input permutation; native autonomous return cancels all intermediate helper dependence on main outputs.',
                negative_controls={'omitted_inverse_bridge_rejected':True,'omitted_terminal_translation_rejected_all112':True},
                limits=['Finite ideal circuit, not a rounded implementation.',
                        'Mixed-size recursion and uniform fixed-tape compilation require separate proof.',
                        'All32 finite provider choices are covered; arbitrary layer-dependent provider dispatch is not proved here.',
                        'Owned-center acquisition and precision stock must be paid by the outer caller.'],new_kappa=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=HERE/'GLOBAL-IDENTITY-COVER.json.gz')
    args = ap.parse_args()
    result = run()
    args.out.write_bytes(gzip.compress(json.dumps(result,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(dict(status=result['status'],contacts=result['contact_count'],
                         targets=result['all_three']['targets'],paid=result['all_three']['paid'],
                         fields=result['arbitrary_productive_input_fields'],scalar=result['all_three']['scalar_allowance'],
                         receipt_sha256=digest(args.out)),sort_keys=True))


if __name__ == '__main__':
    main()
