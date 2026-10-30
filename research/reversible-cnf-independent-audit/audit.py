"""Independent source-compiler checks. Hiroki KUMAZAKI / OpenAI Codex.

Apache-2.0. Source compilation is the system under review, never the oracle.
"""
from copy import deepcopy
from itertools import combinations, permutations, product
from functools import reduce
from operator import xor

IDENTITY = (0, 1, 2, 3, 4)
TARGET = (1, 2, 3, 4, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def group_endpoint(word, assignment):
    # Follow each source role through the chronological instruction list.
    # No source compose, evaluate, inverse or swaps helper is used.
    paths = list(range(5))
    for variable, zero, one in word:
        branch = one if variable is not None and ((assignment >> variable) & 1) else zero
        paths = [branch[position] for position in paths]
    return tuple(paths)


def branch_census(source, literal):
    perms = list(permutations(range(5)))
    endpoints = 0
    maximum = 0
    for zero in perms:
        constant = source.lower_word(1, [(None, zero, zero)])
        need(len(constant['program']) <= 4, 'constant permutation swap bound')
        need(literal.endpoint(constant, (0,)) == literal.permutation_matrix(zero),
             'literal constant-permutation endpoint')
        for one in perms:
            problem = source.lower_word(1, [(0, zero, one)])
            literal.strict_standard_generators(problem)
            maximum = max(maximum, len(problem['program']))
            need(len(problem['program']) <= 24, 'single-branch instruction bound')
            for bit, wanted in enumerate((zero, one)):
                need(literal.endpoint(problem, (bit,)) == literal.permutation_matrix(wanted),
                     'literal two-branch complete dirty endpoint')
                endpoints += 1
    return {'all_permutations': len(perms), 'branch_pairs': len(perms)**2,
            'literal_branch_endpoints': endpoints, 'constant_endpoints': len(perms),
            'maximum_emitted_instructions': maximum}


def five_cycle_conjugation(source, literal):
    cycles = []
    for tail in permutations(range(1, 5)):
        sequence = (0,) + tail
        images = [0]*5
        for a, b in zip(sequence, sequence[1:] + sequence[:1]):
            images[a] = b
        cycles.append(tuple(images))
    cases = 0
    for target in cycles:
        word = source.formula_word(('and', 1, 2), target)
        problem = source.lower_word(2, word)
        literal.strict_standard_generators(problem)
        for assignment in range(4):
            expected = target if assignment == 3 else IDENTITY
            need(group_endpoint(word, assignment) == expected, 'conjugated AND group endpoint')
            need(literal.endpoint(problem, (assignment,)) == literal.permutation_matrix(expected),
                 'conjugated AND literal endpoint')
            cases += 1
    return {'target_five_cycles': len(cycles), 'complete_dirty_endpoints': cases}


def formula_census(source, literal):
    # Canonical clauses of up to three distinct signed literals, including
    # tautologies and the empty clause. All ordered pairs are included.
    literals = (-3, -2, -1, 1, 2, 3)
    clauses = [list(c) for size in range(4) for c in combinations(literals, size)]
    formulas = [[]] + [[c] for c in clauses] + [[a,b] for a in clauses for b in clauses]
    checks = 0
    for cnf in formulas:
        word = source.cnf_word(3, cnf)
        for assignment in range(8):
            target = TARGET if literal.direct_clauses(cnf, assignment) else IDENTITY
            need(group_endpoint(word, assignment) == target, 'CNF truth versus branch program')
            checks += 1
    lengths = [len(source.cnf_word(3, [list(range(1,size+1))])) for size in range(4)]
    need(lengths == [0,1,9,25], 'clause-length base cases')
    return {'canonical_clauses': len(clauses), 'formulas': len(formulas),
            'assignment_checks': checks, 'clause_lengths_0_to_3': lengths}


def native_cnf(source, literal):
    fixtures = [
        ('empty-conjunction',1,[]), ('empty-clause',1,[[]]),
        ('tautology',1,[[1,-1]]), ('contradiction',1,[[1],[-1]]),
        ('mixed-two-axis',2,[[1,-2],[2]]),
        ('mixed-three-axis',3,[[1,-2,3],[-1,2]]),
        ('sparse-label',5,[[5]]),
    ]
    counts = {}
    maximum_instructions = 0
    for name, n, cnf in fixtures:
        problem = source.cnf_problem(n, cnf)
        literal.strict_standard_generators(problem)
        need(problem['reference'] == [], 'identity reference')
        maximum_instructions = max(maximum_instructions, len(problem['program']))
        domain = range(2**n)
        tuples = [(a,) for a in domain]
        if n <= 3:
            tuples += list(product(domain, repeat=2)) + list(product(domain, repeat=3))
        else:
            tuples += [(a,a) for a in domain] + [(a,a,a) for a in domain]
        for addresses in tuples:
            assignment = reduce(xor, addresses, 0)
            target = TARGET if literal.direct_clauses(cnf, assignment) else IDENTITY
            need(literal.endpoint(problem, addresses) == literal.permutation_matrix(target),
                 'literal CNF endpoint at full tensor address: ' + name)
        counts[name] = len(tuples)
    return {'fixtures': counts, 'literal_tensor_blocks': sum(counts.values()),
            'dirty_input_columns_per_block': 5, 'tensor_widths': [1,2,3],
            'max_program_instructions': maximum_instructions,
            'oracle_assignment': 'XOR of every tensor column address'}


def size_checks(source):
    sizes = list(range(18)) + [31,32,33,63,64,65]
    rows = []
    for m in sizes:
        cnf = [[1,2,3] for _ in range(m)]
        word = source.cnf_word(3, cnf)
        tighter = 1 if m == 0 else 25*m*2**((m-1).bit_length())
        need(len(word) <= tighter <= 50*max(1,m)**2, 'balanced-tree size bound')
        rows.append({'clauses':m, 'branch_instructions':len(word), 'proved_upper':tighter})
    return {'cases':len(rows), 'rows':rows,
            'native_bound': '24 per branch; at most 1200*max(1,m)^2 instructions',
            'bit_encoding_qualification': 'generator-table O(n^3) bits; renumber used variables before reduction'}


def renaming_control(source, literal):
    # This audit's explicit preprocessing step, not a claim that the source
    # compiler itself already compacts its caller's declared axis domain.
    u, v, w = 2**200+3, 2**128+1, 2**65+7
    original = [[u, -v, w], [-u, v], [-w, u]]
    names = sorted({abs(x) for clause in original for x in clause})
    positions = {name:i for i,name in enumerate(names)}
    compact = [[(1 if x > 0 else -1)*(positions[abs(x)]+1) for x in clause]
               for clause in original]
    need(len(names) <= 3*len(original), 'used-variable bound')
    problem = source.cnf_problem(len(names), compact)
    literal.strict_standard_generators(problem)
    for assignment in range(2**len(names)):
        values = {name:bool((assignment >> positions[name]) & 1) for name in names}
        expected_truth = all(any(values[abs(x)] if x > 0 else not values[abs(x)]
                                 for x in clause) for clause in original)
        need(literal.direct_clauses(compact, assignment) == expected_truth, 'renaming preserves truth')
        target = TARGET if expected_truth else IDENTITY
        need(literal.endpoint(problem, (assignment,)) == literal.permutation_matrix(target),
             'compact encoding has the required complete dirty endpoint')
    return {'largest_original_variable_bits':max(names).bit_length(),
            'compact_axes':len(names), 'clauses':len(original),
            'complete_dirty_endpoints':2**len(names),
            'source_compiler_auto_renaming_claimed':False}


def first_difference(left, right):
    for i in range(5):
        for j in range(5):
            if left[i][j] != right[i][j]:
                return {'output_role':i, 'dirty_input_role':j,
                        'actual':str(left[i][j]), 'required':str(right[i][j])}
    return None


def mutation_checks(source, literal, mutated_source):
    outcomes = []
    def reject(name, problem, addresses, target):
        wrong = literal.endpoint(problem, addresses)
        delta = first_difference(wrong, literal.permutation_matrix(target))
        need(delta is not None, 'semantic mutation survived: ' + name)
        outcomes.append({'mutation':name, 'tensor_addresses':list(addresses), 'differing_entry':delta})
    inverse_bad = mutated_source('for variable, zero, one in reversed(word)',
                                'for variable, zero, one in word')
    reject('omit inverse-word reversal', inverse_bad.cnf_problem(2, [[1,2]]), (0,), IDENTITY)
    quotient_bad = mutated_source('swaps(compose(one, inverse(zero)))',
                                 'swaps(compose(inverse(zero), one))')
    zero, one = (1,2,3,4,0), (1,3,0,4,2)
    reject('reverse relative permutation product', quotient_bad.lower_word(1, [(0,zero,one)]), (1,), one)
    swap_bad = mutated_source('for i, j in swaps(zero)', 'for i, j in reversed(swaps(zero))')
    reject('reverse cycle swap chronology', swap_bad.lower_word(1, [(None,TARGET,TARGET)]), (0,), TARGET)
    empty_bad = mutated_source("for clause in clauses], True)", "for clause in clauses], False)")
    reject('empty conjunction made false', empty_bad.cnf_problem(1, []), (0,), TARGET)
    original = source.cnf_problem(1, [[1]])
    bad = deepcopy(original)
    query = next(gate for gate in bad['program'] if gate['op'] == 'query')
    query['coefficient'] = '1/2'
    reject('flip controlled-query sign', bad, (0,), IDENTITY)
    bad = deepcopy(original)
    need(bad['program'][4] == {'op':'add','src':1,'dst':0}, 'expected first controlled swap end')
    del bad['program'][4]
    reject('omit final controlled-swap ADD', bad, (0,), IDENTITY)
    bad = deepcopy(original)
    next(iter(bad['generators'].values()))['linear_Z4'] = [0]
    reject('erase variable sign', bad, (1,), TARGET)
    bad = deepcopy(original)
    next(iter(bad['generators'].values()))['phase'] = 2
    need(literal.endpoint(bad, (1,0)) == literal.endpoint(original, (1,0)),
         'constant-phase mutation must pass this even-width control')
    reject('extra constant phase hidden at even widths', bad, (1,), TARGET)
    return {'semantic_rejections':len(outcomes), 'witnesses':outcomes,
            'constant_phase_even_width_control_passes':True}


def invalid_inputs(source):
    cases = [(0, []), (True, []), (1.0, []), (1, [[0]]), (1, [[True]]),
             (1, [[2]]), (1, [[1,1,1,1]])]
    for n, clauses in cases:
        try:
            source.cnf_problem(n, clauses)
        except ValueError:
            continue
        raise ValueError('invalid compiler input was accepted')
    return {'rejected_inputs':len(cases)}


def run(source, literal, mutated_source):
    return {'local_controls':literal.run_local_controls(),
            'branches':branch_census(source,literal),
            'conjugation':five_cycle_conjugation(source,literal),
            'formula_truth':formula_census(source,literal),
            'native_cnf':native_cnf(source,literal),
            'sizes':size_checks(source),
            'variable_renaming':renaming_control(source,literal),
            'mutations':mutation_checks(source,literal,mutated_source),
            'invalid_inputs':invalid_inputs(source)}
