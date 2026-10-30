"""Reusable exact producer-support and loss-space source certificate.

The caller supplies the authenticated decoded PR5569 word. No filesystem,
network, optimizer or predecessor verifier is used here.
"""
from copy import deepcopy
from fractions import Fraction as Q


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def basis_reduce(vectors):
    basis = []
    for original in vectors:
        v = original
        for row in basis:
            v = min(v, v ^ row)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return basis


def span(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    return out


def loss_floor(support_basis, delivery_basis):
    """dim((support+delivery)/delivery), the global descent rank-mass floor."""
    return len(basis_reduce(list(support_basis)+list(delivery_basis))) - len(basis_reduce(delivery_basis))


def verify(word):
    program = word['program']
    frames = word['frames']
    need(word['public'] == 735, 'public role inventory')
    first_init = next((i for i,e in enumerate(program) if e[0] == 'INIT'), None)
    need(first_init == 13377, 'first owned INIT source binding')
    targets = [(i,e[1],e[2],e[-1]) for i,e in enumerate(program) if e[0] == 'COPY']
    need([(o,r) for i,o,r,f in targets] == [(735,173),(736,151),(737,146),(738,133),
                                          (739,256),(740,92),(741,9),(742,240)],
         'exact eight owned producer bindings')
    coefficients = [{role:Q(1)} for _,_,role,_ in targets]
    for event, owned, role, frame in targets:
        need(Q(program[event][-2]) != 0, 'nonzero COPY factor')
        need(not any(e[1] == role and e[0] != 'MOVE' for e in program[first_init:event]),
             'producer row unchanged between public prefix and COPY')
    # Unique pullback through the purely public invertible prefix.
    for event in reversed(program[:first_init]):
        op, dst = event[:2]
        if op == 'MOVE':
            need(not event[-1], 'no owned descent in public prefix')
            need(span(frames[event[2]]) < span(frames[event[3]]), 'ascending public prefix MOVE')
            continue
        need(op in ('ADD','SCALE'), 'invertible public prefix operation')
        q = Q(event[-2])
        need(q != 0, 'nonzero scalar coefficient')
        for covector in coefficients:
            if dst not in covector:
                continue
            if op == 'SCALE':
                covector[dst] *= q
            else:
                src = event[2]
                value = covector.get(src,Q(0)) + q * covector[dst]
                if value:
                    covector[src] = value
                else:
                    covector.pop(src,None)
    results = []
    for target,covector in zip(targets,coefficients):
        event,owned,role,frame = target
        vectors = [v for r in covector for v in frames[word['initial'][r]]]
        basis = basis_reduce(vectors)
        need(len(basis) == 8 and span(basis) == span(frames[frame]),
             'rank-eight entry support equals producer frame')
        end = next((j for j in range(event+1,len(program)) if program[j][0] == 'CLEAR' and program[j][1] == owned), None)
        need(end is not None, 'owned delivery lifetime closes')
        final_frame = program[end][-1]
        current = frame
        multiplier = Q(program[event][-2])
        paid_ranks = []
        final_reads = 0
        for e in program[event+1:end]:
            if e[0] in ('ADD','COPY') and e[2] == owned and e[-1] == final_frame:
                final_reads += 1
            if e[1] != owned:
                continue
            if e[0] == 'SCALE':
                need(e[-1] == current and Q(e[-2]) != 0, 'owned scalar preserves producer support')
                multiplier *= Q(e[-2])
            elif e[0] == 'MOVE':
                need(e[2] == current and e[-1] is True, 'owned paid descent binding')
                need(span(frames[e[3]]) < span(frames[current]), 'strict owned descent')
                paid_ranks.append(len(frames[current])-len(frames[e[3]]))
                current = e[3]
            else:
                raise ValueError('owned producer payload changed before delivery')
        need(current == final_frame and final_reads > 0, 'actual retained delivery frame and read')
        lower = loss_floor(basis,frames[final_frame])
        need(lower == 7 and sum(paid_ranks) == 7 and len(frames[final_frame]) == 1,
             'rank-seven loss-space lower bound and source rank mass')
        witnesses = []
        independent = []
        for r in sorted(covector):
            for v in frames[word['initial'][r]]:
                if len(basis_reduce(independent+[v])) > len(independent):
                    independent.append(v)
                    witnesses.append({'input':r,'coefficient':str(covector[r]),'initial_vector':v})
        results.append({'owned':owned,'copy_event':event,'source_role':role,'copy_frame':frame,
                        'support_count':len(covector),'initial_span_rank':8,
                        'nonzero_chart_inputs':sum(bool(frames[word['initial'][r]]) for r in covector),
                        'independent_witnesses':witnesses,'clear_frame':final_frame,
                        'delivery_factor':str(multiplier),'owned_move_ranks':paid_ranks,
                        'required_global_owned_descent_rank_mass':lower,
                        'initial_covector':{str(k):str(v) for k,v in sorted(covector.items())}})
    return {'status':'PASS_RANK_EIGHT_PRODUCER_AND_LOSS_SPACE_BINDING','first_owned_init':first_init,
            'results':results,'new_bound':False,
            'scope':'One unchanged scalar target at its retained delivery frame; owned descent cost can be shared across targets, so individual bounds must not be summed.'}


def controls(word):
    wrong_entry_support = deepcopy(word)
    original_support = span(word['frames'][559])
    outside = next(v for v in range(1,512) if v not in original_support)
    wrong_entry_support['frames'].append([outside])
    wrong_entry_support['initial'][111] = len(wrong_entry_support['frames'])-1
    wrong_producer = deepcopy(word)
    wrong_producer['program'][13378][2] = 704
    unaccounted_descent = deepcopy(word)
    move = next(e for e in unaccounted_descent['program'][:13377] if e[0] == 'MOVE')
    move[-1] = True
    changed_payload = deepcopy(word)
    changed_payload['program'][13379] = ['ADD',735,111,'1',559]
    rejected = []
    for name,mutant in [('entry_support_outside_producer_frame',wrong_entry_support),
                        ('wrong_producer_value',wrong_producer),
                        ('unaccounted_descent_in_public_prefix',unaccounted_descent),
                        ('changed_owned_payload_before_delivery',changed_payload)]:
        try:
            verify(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('corruption control accepted: '+name)
    # A widened delivery interface genuinely weakens the floor: no universal H7 claim.
    support = word['frames'][559]
    delivery = list(word['frames'][593])
    extra = next(v for v in support if v not in span(delivery))
    widened = delivery+[extra]
    need(loss_floor(support,widened) == 6, 'widened-delivery scope control')
    return {'rejected_corruptions':rejected,'widened_delivery_rank':2,
            'widened_delivery_loss_floor':6,'individual_floors_not_additive':True}


def rational_rank(rows):
    """Exact row reduction, returning independent column indices as a witness."""
    rows = [[Q(x) for x in row] for row in rows]
    if not rows:
        return 0, []
    width = len(rows[0])
    need(all(len(row) == width for row in rows), 'rectangular rational matrix')
    pivots = []
    for column in range(width):
        at = len(pivots)
        pivot = next((j for j in range(at,len(rows)) if rows[j][column]), None)
        if pivot is None:
            continue
        rows[at], rows[pivot] = rows[pivot], rows[at]
        q = rows[at][column]
        rows[at] = [x/q for x in rows[at]]
        for j in range(at+1,len(rows)):
            q = rows[j][column]
            if q:
                rows[j] = [x-q*y for x,y in zip(rows[j],rows[at])]
        pivots.append(column)
        if len(pivots) == len(rows):
            break
    return len(pivots), pivots


def determinant(matrix):
    matrix = [[Q(x) for x in row] for row in matrix]
    n = len(matrix)
    need(all(len(row) == n for row in matrix), 'square minor')
    result = Q(1)
    for column in range(n):
        pivot = next((j for j in range(column,n) if matrix[j][column]), None)
        if pivot is None:
            return Q(0)
        if pivot != column:
            matrix[column],matrix[pivot] = matrix[pivot],matrix[column]
            result = -result
        q = matrix[column][column]
        result *= q
        for j in range(column+1,n):
            factor = matrix[j][column]/q
            for k in range(column+1,n):
                matrix[j][k] -= factor*matrix[column][k]
    return result


def verify_joint_cut(word, producer_receipt):
    """Count shared owned crossings; this does NOT prove an eight-H7 tariff."""
    producers = producer_receipt['results']
    need([r['owned'] for r in producers] == list(range(735,743)), 'joint producer order')
    delivery_frames = [word['frames'][r['clear_frame']] for r in producers]
    need(all(len(frame) == 1 for frame in delivery_frames), 'eight fixed delivery lines')
    W_basis = basis_reduce([v for frame in delivery_frames for v in frame])
    need(len(W_basis) == 8, 'joint delivery subspace rank')
    W = span(W_basis)
    outside = [i for i,f in enumerate(word['initial']) if not span(word['frames'][f]) <= W]
    matrix = [[Q(r['delivery_factor'])*Q(r['initial_covector'].get(str(i),0)) for i in outside]
              for r in producers]
    rank, pivots = rational_rank(matrix)
    need(rank == 8, 'eight independent outside-input observations')
    minor = [[row[k] for k in pivots] for row in matrix]
    det = determinant(minor)
    need(det != 0, 'independent exact minor determinant')
    crossings = []
    for i,e in enumerate(word['program']):
        if e[0] != 'MOVE':
            continue
        before, after = span(word['frames'][e[2]]), span(word['frames'][e[3]])
        if not before <= W and after <= W:
            need(e[-1] is True and after < before, 'every into-W crossing is a paid owned descent')
            crossings.append({'event':i,'owned':e[1],'from':e[2],'to':e[3],
                              'paid_rank':len(word['frames'][e[2]])-len(word['frames'][e[3]])})
    need(len(crossings) == 8 and sorted(r['owned'] for r in crossings) == list(range(735,743)),
         'source attains eight crossing events')
    duplicated = matrix[:-1]+[list(matrix[0])]
    duplicated_rank = rational_rank(duplicated)[0]
    need(duplicated_rank == 7, 'duplicate-observation scope control')
    whole = span([1<<k for k in range(9)])
    whole_outside = [i for i,f in enumerate(word['initial']) if not span(word['frames'][f]) <= whole]
    whole_matrix = [[Q(r['initial_covector'].get(str(i),0)) for i in whole_outside] for r in producers]
    whole_rank = rational_rank(whole_matrix)[0]
    need(whole_rank == 0, 'whole-space scope control')
    return {'status':'PASS_JOINT_OWNED_CROSSING_COUNT_FLOOR',
            'delivery_space_basis':W_basis,'delivery_space_dimension':8,
            'outside_input_count':len(outside),'observation_rank':rank,
            'witness_input_columns':[outside[k] for k in pivots],
            'witness_minor':[[str(x) for x in row] for row in minor],
            'witness_determinant':str(det),'required_owned_crossing_count':8,
            'source_crossings':crossings,
            'scope_controls':{'duplicated_output_rank':duplicated_rank,'whole_space_rank':whole_rank},
            'eight_H7_tariff_claimed':False,'new_bound':False}
