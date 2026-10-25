#!/usr/bin/env python3
"""Concrete full root-product tiling and exact residual invoice.

This is a construction/cost receipt for disjoint r3 dynamic modules. It
does not rule out overlapping or composed dynamic-reader networks.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE/path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


d = load('tiling_dynamic', 'dynamic_cyclic.py')
m, b, need = d.m, d.b, d.need
TRIPLES = [(0,62,66),(1,17,92),(2,10,76),(3,56,68),(4,36,50),
           (5,42,101),(6,12,109),(7,88,96),(8,89,112),(9,78,116),
           (11,51,99),(13,108,115),(14,29,31),(15,83,103),(16,71,117),
           (18,52,91),(19,32,73),(20,41,107),(21,49,55),(22,38,67),
           (23,27,28),(24,87,113),(25,26,65),(30,35,106),(33,45,94),
           (34,98,119),(37,48,72),(39,59,69),(40,63,85),(43,77,114),
           (44,60,64),(46,54,93),(47,79,81),(53,90,102),(57,74,105),
           (58,70,111),(61,97,118),(75,95,110),(80,86,104),(82,84,100)]


def packed_root_pairs(roots):
    # Same exact lattice-to17-bit fit as mixed_rectangle.actual_labels,
    # but without its quadratic all-pairs diagnostic on the whole domain.
    gram = [sum((m.dot(a,c)&1) << j for j,c in enumerate(roots)) for a in roots]
    work = list(gram)
    available, selected = list(range(120)), []
    while any(work[a] >> c & 1 for a in available for c in available):
        a,c = next((a,c) for a in available for c in available if work[a] >> c & 1)
        selected.extend((a,c))
        left, right = work[a], work[c]
        work = [row ^ (right if left >> i & 1 else 0)
                    ^ (left if right >> i & 1 else 0)
                for i,row in enumerate(work)]
        available.remove(a)
        available.remove(c)
    small = [sum(((gram[i] >> j)&1) << k for k,j in enumerate(selected))
             for i in selected]
    inverse = m.inv(small)
    form = inverse+[row << 8 for row in inverse]
    even = [((1 << 16)-1) ^ (1 << i) for i in range(16)]
    change = m.mm(m.inv(m.symp(form)), m.symp(even))
    need(m.cong(change, even) == form, 'pinned standard-dot isometry')
    mapping = m.mm(change, [(1 << i)|(1 << 16) for i in range(16)])
    coordinates = [sum(((gram[i] >> j)&1) << k for k,j in enumerate(selected))
                   for i in range(120)]
    return [[((1 << 17)-1) ^ m.mm([x|(y << 8)], mapping)[0]
             for y in coordinates] for x in coordinates]


def orthogonal_involution(roots):
    position = {a:i for i,a in enumerate(roots)}
    mates = []
    for a in roots:
        c = list(a)
        if all(x % 2 == 0 for x in a):
            nonzero = [i for i,x in enumerate(a) if x]
            c[nonzero[1]] *= -1
        else:
            for i in range(4,8):
                c[i] *= -1
        mates.append(position[tuple(c)])
    need(all(i != j and mates[j] == i and m.dot(roots[i], roots[j]) == 0
             for i,j in enumerate(mates)), 'explicit120-root orthogonal involution')
    pairs = [(i,j) for i,j in enumerate(mates) if i < j]
    need(len(pairs) == 60, 'sixty orthogonal b-pairs')
    return pairs


def tiling():
    roots = m.canonical_roots()
    need(sorted(i for row in TRIPLES for i in row) == list(range(120)),
         'explicit disjoint acute-triple partition')
    signs = []
    for row in TRIPLES:
        sigma = [1]+[m.dot(roots[row[0]], roots[i]) for i in row[1:]]
        need(all(abs(x) == 1 for x in sigma), 'triple gauge signs')
        need(all(sigma[i]*sigma[j]*m.dot(roots[row[i]], roots[row[j]]) == 1
                 for i in range(3) for j in range(i)), 'acute triple after gauge')
        signs.append(sigma)
    pairs = orthogonal_involution(roots)
    packed = packed_root_pairs(roots)
    assigned = set()
    examples = []
    coefficient_census = Counter()
    for ti, aa in enumerate(TRIPLES):
        sigma = signs[ti]
        for bi, bb in enumerate(pairs):
            labels = [packed[a][bb[z]] for a in aa for z in range(2)]
            planes = [m.basis(labels[2*g:2*g+2]) for g in range(3)]
            arcs = [m.basis(planes[g]+planes[(g+1)%3]) for g in range(3)]
            need(all(len(x) == 2 for x in planes) and all(len(x) == 3 for x in arcs),
                 'actual r3 module source and final reader frames')
            need(all(m.included(arcs[g], m.perp(labels[2*((g-1)%3)+z]))
                     for g in range(3) for z in range(2)), 'actual module final target caps')
            need(all(m.included(planes[j], arcs[(j-1)%3]) for j in range(3)),
                 'actual mutable source nested visits')
            if ti == 0 and bi < 2:
                examples.append({'triple': ti, 'b_pair': bi, 'labels': labels,
                                 'planes': [list(x) for x in planes],
                                 'final_arcs': [list(x) for x in arcs]})
            for epsilon in (-1,1):
                ports = []
                indices = []
                for group,a in enumerate(aa):
                    sign = epsilon*sigma[group]
                    for bj in bb:
                        ports.append(roots[a]+tuple(sign*x for x in roots[bj]))
                        indices.append(2160+240*a+2*bj+int(sign < 0))
                need(not (assigned & set(indices)), 'disjoint module source/target IDs')
                assigned.update(indices)
                for i in range(6):
                    for j in range(6):
                        t = m.dot(ports[i], ports[j])
                        cij = F(int(i == j))-F(t**3-4*t,48)
                        expected = F(0) if i//2 == j//2 else F(
                            sigma[i//2]*sigma[j//2]*(-5 if i%2 == j%2 else 1),16)
                        need(cij == expected, 'literal actual coefficient equals gauged cyclic module')
                        need((labels[i]&labels[j]).bit_count()%2 == (1+t)%2,
                             'literal actual source address parity')
                        if cij:
                            coefficient_census[abs(cij)] += 1
    need(assigned == set(range(2160,30960)), 'all28800 root-product ports tiled exactly once')
    need(coefficient_census == {F(1,16):57600, F(5,16):57600},
         'exact115200 compensated ordered pairs')
    return roots, pairs, signs, examples, coefficient_census


def actual_edge_completion_model(L, residual_edges):
    row = b.model(L, [16], [16], [17], 0)
    census = Counter(row['H'])
    # Replace residual16 source/target paths only for the28800 tiled ports.
    for path in ([1,1,14], [3,13]):
        census[16] -= L*28800
        for rank in path:
            census[rank] += L*28800
    for count,path in ((28800,[2,1,14]), (residual_edges,[1,15,1])):
        for rank in path:
            census[rank] += L*count
    roles = 28800+residual_edges
    if row['pad']:
        for rank in b.oracle.partition(row['pad'], row['cap']):
            census[rank] += F(L*roles, row['q'])
    row.update(H=census, W=row['W']+F(L*roles,row['q']), R=roles)
    need(sum(rank*n for rank,n in census.items()) == row['m']*row['W']-row['D'],
         'complete tiled-plus-edge full H6 histogram')
    return row


def main():
    roots, pairs, signs, examples, coefficient_census = tiling()
    path = 'research/h6-independent-audit/walsh/results.json'
    raw = subprocess.check_output(['git','show',b.PIN+':'+path],cwd=b.REPO)
    inherited = json.loads(raw)
    need(inherited['compensation_nonzeros'] == 480337920
         and inherited['exceptional_abs_t_3_pairs'] == 3363840,
         'pinned all-pair support receipt')
    residual_exceptional = 3363840-57600
    residual_unit = 480337920-3363840-57600
    residual = residual_exceptional+residual_unit
    need(residual == 480222720, 'exact residual ordered support count')
    # An actual complete local word exists by using initial-line residual
    # edge readers and delivering them at final caps after module delivery.
    component_comp = 4800*396+24*residual_unit+30*residual_exceptional
    forward = 247217040+component_comp
    dual = 247219488+component_comp
    old = 247217040+24*(480337920-3363840)+30*3363840
    need(old-forward == 1209600, 'actual component primitive saving')
    row = actual_edge_completion_model(5,residual)
    price = b.target_row(row,F('.002'))
    need(price['verdict'].startswith('FAILS'), 'complete edge completion fails target')
    # C-D=(I-D)-K. Every actual r3 K block is invertible; pure2160 I
    # gives rank(I-D)=30960. Hence rank residual >=30960-816.
    private_floor = 30960-816
    need(13872+private_floor > 30960, 'actual module private residual coverage fails all L')
    # Even if each module's coefficients are redesigned arbitrarily, keeping
    # zero own-group2x2 blocks forces rank(I-D_module)>=2. The most favorable
    # disjoint-module rank floor is2*4800+2160=11760, residual>=10944.
    redesigned_A = 2*4800+2160
    redesigned_residual = redesigned_A-816
    need(redesigned_residual == 10944, 'redesigned disjoint-module residual rank floor')
    # Grant free residual banks and ideal rank1 private descents. Active data
    # pressure alone/NL >32*.002*log L. Its excess against D is bounded by
    # min_(L>0) [.064 log L+1/L] -(1-(13872+10944)/30960).
    constant = F(8,125)
    tail = constant*(1+b.oracle.log_interval(1/constant)[0])-(1-F(13872+10944,30960))
    need(tail > 0, 'all positive L redesigned private residual fails .002')
    out = {'status':'PASS_ACTUAL_FULL_ROOT_PRODUCT_DYNAMIC_TILING_AND_PAID_RESIDUAL_NO_NEW_KAPPA',
           'source_pin':b.PIN,'inherited_support_source':path,
           'inherited_support_sha256':hashlib.sha256(raw).hexdigest(),
           'canonical_roots':roots,'a_triples':TRIPLES,'triple_gauge_signs':signs,
           'b_orthogonal_involution_pairs':pairs,'module_count':4800,
           'module_rule':'For each acute a-triple, orthogonal b-pair, epsilon=+-1, port(group,z)=(a_group,epsilon*sigma_group*b_z). Source product ID2160+240*a+2*b+int(sign<0).',
           'actual_tiled_ports':28800,'untiled_ports':{'indices':[0,2159], 'meaning':'Both1080-port pure norm4 blocks; complete interval0<=i<2160.'},
           'actual_module_frame_cases':2400,'frame_examples':examples,
           'covered_ordered_nonzero_entries':115200,
           'covered_unit_entries':57600,'covered_exceptional_entries':57600,
           'uncovered_ordered_nonzero_entries':residual,
           'uncovered_unit_entries':residual_unit,
           'uncovered_exceptional_entries':residual_exceptional,
           'exact_uncovered_set':'All ordered pairs(t,s) with actual odd Gram t_ts and with t,s not belonging to the same six-port module above. Every pair involving a pure port is outside the modules; within-module C equals D exactly.',
           'actual_full_completion':{'module_readers':28800,'residual_edge_readers':residual,
                                    'ordinary_K_centres':816,'K_private_C':13872,
                                    'total_ordinary_compensation_roles':28800+residual,
                                    'component_primitives_forward':forward,
                                    'component_primitives_dual':dual,
                                    'component_saving_against_full_edge_word':old-forward,
                                    'L5_stock_W':str(row['W']),'L5_q_replica_banks':5*(row['R']+816),
                                    'L5_complete_histogram':{r:str(n) for r,n in sorted(row['H'].items())},
                                    'L5_target_002':price,
                                    'word_contract':'AtZERO precompensate K,module and residual dirt. Load every residual edge helper at its original source line before module source climbs. Execute changing module gathers on disjoint nested arcs; sources reachFULL. Run unchanged816-centre K while targetsZERO. Deliver modules at their rank3 arcs, then targets finish caps. Deliver each residual edge helper at its rank16 target cap. Restore all compensation helpers atFULL. Same-order dual has separate K private episodes. Full billion-event stream is mathematically specified/counted, not materialized.'},
           'actual_private_residual':{'rank_I_minus_D':30960,'rank_lower':private_floor,
                                      'best_private_rank_floor':private_floor,
                                      'total_private_C_lower':13872+private_floor,
                                      'all_L_coverage_deficit_upper':'-30960-13056*L'},
           'redesigned_disjoint_r3_private_residual':{'rank_I_minus_D_lower':redesigned_A,
                                                    'rank_residual_lower':redesigned_residual,
                                                    'total_private_C_lower':13872+redesigned_residual,
                                                    'all_positive_L_active_data_gap_lower':str(tail),
                                                    'assumptions':'Arbitrary weights per disjoint6-port r3 module, no within-own-group coefficient, D=0 on pure ports. All residual dependence returns through private episodes, each granted ideal rank1 and free ordinary banks.'},
           'controls':{'tile_signs_required':any(x<0 for row in signs for x in row),
                       'b_mates_are_distinct':all(i!=j for i,j in pairs),
                       'pure_ports_not_claimed_tiled':len(roots)*240 == 28800,
                       'dropping_residual_changes_operator':residual>0},
           'scope':'Actual disjoint r3 tiling with exact residual set, actual edge-helper completion and scoped private-residual failures. Overlapping/composed dynamic modules, mutable residual networks, changed source/target schedules and different centre interfaces remain open. No new kappa or full physical/approximate supplier admission.'}
    (HERE/'MODULE-TILING-RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']+' modules=4800 root_ports=28800 pure_ports=2160 residual_edges='+str(residual))
    print('actual private residual rank>=',private_floor,'Ctotal>=',13872+private_floor)
    print('redesigned private residual rank>=',redesigned_residual,'active gap lower',b.dec(tail))
    print('full edge completion primitives',forward,dual,'L5 M',price['normalized_moment']['lo'])


if __name__ == '__main__':
    main()
