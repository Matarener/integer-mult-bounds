"""Exact premises and controls for the sparse-gain transfer proof.

The quantified graph and common-gauge arguments are written in PROOF.md.
This stdlib replay checks the literal I334 geometry, finite-field controls,
and the complete linear-algebra description of the seven-query bridge.
It performs no coefficient or geometry search.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    'research/p112-rational-decoder-gate/CANDIDATE.json':
        'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
        'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = (ROOT / path).read_bytes()
    need(sha256(raw).hexdigest() == PINS[path], 'authenticated source: ' + path)
    return json.loads(raw)


def transpose(A):
    return list(map(list, zip(*A)))


def multiply(A, B):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*B)] for row in A]


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def rational_rref(A, columns=None):
    B = [list(map(F, row)) for row in A]
    n = columns if columns is not None else (len(B[0]) if B else 0)
    pivots = []
    for j in range(n):
        r = len(pivots)
        k = next((k for k in range(r, len(B)) if B[k][j]), None)
        if k is None:
            continue
        B[r], B[k] = B[k], B[r]
        a = B[r][j]
        B[r] = [x/a for x in B[r]]
        for k in range(len(B)):
            if k != r:
                a = B[k][j]
                B[k] = [x-a*y for x, y in zip(B[k], B[r])]
        pivots.append(j)
    return B, pivots


def rational_rank(A):
    return len(rational_rref(A)[1])


def rational_inverse(A):
    n = len(A)
    B, pivots = rational_rref([row+e for row, e in zip(A, identity(n))], n)
    need(pivots == list(range(n)), 'invertible rational square matrix')
    return [row[n:] for row in B]


def binary_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length()-1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


# GF(4) = {0,1,w,w+1}, with w^2+w+1=0. The independent replay uses
# polynomial reduction instead of this literal multiplication table.
GF4_MUL = ((0,0,0,0), (0,1,2,3), (0,2,3,1), (0,3,1,2))
GF4_INV = (0,1,3,2)


def field_sum(values):
    total = 0
    for value in values:
        total ^= value
    return total


def field_product(A, B):
    return [[field_sum(GF4_MUL[x][y] for x,y in zip(row,col))
             for col in zip(*B)] for row in A]


def field_rref(A, columns=None):
    B = [row[:] for row in A]
    n = columns if columns is not None else (len(B[0]) if B else 0)
    pivots = []
    for j in range(n):
        r = len(pivots)
        k = next((k for k in range(r,len(B)) if B[k][j]), None)
        if k is None:
            continue
        B[r],B[k] = B[k],B[r]
        a = GF4_INV[B[r][j]]
        B[r] = [GF4_MUL[a][x] for x in B[r]]
        for k in range(len(B)):
            if k != r:
                a = B[k][j]
                B[k] = [x ^ GF4_MUL[a][y] for x,y in zip(B[k],B[r])]
        pivots.append(j)
    return B,pivots


def field_inverse(A):
    n = len(A)
    B,pivots = field_rref([row+[int(i==j) for j in range(n)] for i,row in enumerate(A)],n)
    need(pivots == list(range(n)), 'invertible GF4 square matrix')
    return [row[n:] for row in B]


def support(A):
    return [[bool(x) for x in row] for row in A]


def strings(A):
    return [[str(x) for x in row] for row in A]


def geometry():
    candidate,data = [read(p) for p in PINS]
    groups = candidate['groups']
    marks = candidate['factor_supports']
    label = {row['port']:row['q'] for row in data['recipes']}
    owner = {port:g for g,ports in enumerate(groups) for port in ports}
    mark_of = {port:j for j,ports in enumerate(marks) for port in ports}
    need(len(owner) == sum(map(len,groups)) == 112, 'physical groups partition 112 ports')
    need(len(mark_of) == sum(map(len,marks)) == 112 and set(mark_of) == set(owner), 'indicator marks partition all ports')
    need(Counter(map(len,groups)) == {1:1,3:37}, '37 triads and one residual line')
    need(Counter(map(len,marks)) == {1:3,2:53,3:1}, 'all canonical mark sizes, including residual')
    for ports in groups:
        need([[int((label[p]&label[q]).bit_count()%2) for q in ports] for p in ports]
             == [[int(i==j) for j in range(len(ports))] for i in range(len(ports))], 'orthonormal physical group')
    expanded = [(p,q) for p in sorted(owner) for q in groups[owner[p]]]
    need(len(expanded) == 334, 'entire expanded endpoint dimension')
    disagreements = []
    for i,(p,a) in enumerate(expanded):
        for j,(q,b) in enumerate(expanded):
            value = int(mark_of[p] == mark_of[q]) * ((label[a]&label[b]).bit_count()%2)
            if value != int(i==j):
                disagreements.append([i,j])
    need(not disagreements, 'full expanded endpoint is exactly I334')
    free_groups = {(g,h) for g in range(len(groups)) for h in range(g+1,len(groups))
                   if all((label[p]&label[q]).bit_count()%2==0 for p in groups[g] for q in groups[h])}
    need(free_groups==set(map(tuple,candidate['orthogonal_group_pairs'])), 'entire-space strict-mask free pairs')
    free_scalar = {(p,q) for p in owner for q in owner
                   if tuple(sorted((owner[p],owner[q]))) in free_groups}
    need(len(free_groups)==28 and len(free_scalar)==420, 'literal free-mask counts')
    # Every free scalar entry may be an unrelated indeterminate. Its entire
    # physical pairing block is zero; diagonal entries give I, and all other
    # scalar coefficients are forced zero by the strict mask.
    for i,(p,a) in enumerate(expanded):
        for j,(q,b) in enumerate(expanded):
            pairing = (label[a]&label[b]).bit_count()%2
            if p==q:
                need(pairing==int(i==j), 'symbolic strict-fit diagonal expansion')
            elif (p,q) in free_scalar:
                need(pairing==0, 'every arbitrary free coefficient is annihilated')
    def price(source,reader):
        ss = sorted({q for p in source for q in groups[owner[p]]})
        tt = sorted({q for p in reader for q in groups[owner[p]]})
        rows = [sum(((label[p]&label[q]).bit_count()%2)<<j for j,q in enumerate(tt)) for p in ss]
        return binary_rank(rows)
    costs = [price(ports,ports) for ports in marks]
    need(Counter(costs) == {3:3,6:53,7:1} and sum(costs) == 334, 'canonical complete-group invoice')
    residual = next(p for ports in groups if len(ports)==1 for p in ports)
    residual_mark = marks[mark_of[residual]]
    need(len(residual_mark)==3 and costs[mark_of[residual]]==7, 'residual-bearing mark retains H7 charge')
    ordinary_pair = [p for p in residual_mark if p!=residual]
    split_prices = [price(ordinary_pair,residual_mark),price([residual],residual_mark)]
    need(split_prices==[6,1] and sum(split_prices)==7, 'zero-overhead two-port plus unit residual refinement')
    return {'ports':112,'physical_groups':38,'marks':57,
            'mark_size_counts':{str(k):v for k,v in sorted(Counter(map(len,marks)).items())},
            'expanded_dimension':334,'expanded_entries_checked':334*334,
            'canonical_term_cost_counts':{str(k):v for k,v in sorted(Counter(costs).items())},
            'canonical_invoice':334,'residual_port':residual,'residual_mark':residual_mark,
            'singletons':[ports[0] for ports in marks if len(ports)==1],
            'strict_mask_free_group_pairs':len(free_groups),'strict_mask_free_scalar_entries':len(free_scalar),
            'symbolic_strict_fit_expanded_entries_checked':334*334,
            'residual_sparse_refinement_costs':split_prices}


def controls():
    # Three-copy indicator, rational arbitrary-gain tree, and common GF4 gauge.
    rational_tree = [[1,0],[-1,2],[0,1]]
    old_reader = [[1]*3,[1]*3]
    need(multiply(rational_tree,old_reader) == [[1]*3 for _ in range(3)], 'rational three-copy endpoint')
    base = [[1,0],[1,1],[0,1]]
    need(len(field_rref(base)[1])==2 and len(field_rref([row+[1] for row in base])[1])==3, 'ungauged GF4 tree fails odd mark')
    gauge = [1,3,2]
    shifted = [[GF4_MUL[gauge[i]][x] for x in row] for i,row in enumerate(base)]
    new_reader = [[1]*3,[3]*3]
    need(field_product(shifted,new_reader)==[[1]*3 for _ in range(3)], 'gauged GF4 three-copy endpoint')
    need(support(shifted)==support(rational_tree) and support(new_reader)==support(old_reader), 'gauge preserves exact supports in control')
    need(field_sum([1,2,3])==0 and all([1,2,3]), 'nonzero GF4 triple sums to zero')
    # Grounded tree: a literal one-port query retains singleton recoveries.
    rational_grounded = [[F(1),F(1)],[F(-2),F(0)]]
    field_grounded = [[1,1],[2,0]]
    rational_reader = rational_inverse(rational_grounded)
    field_reader = field_inverse(field_grounded)
    need(multiply(rational_grounded,rational_reader)==identity(2), 'rational grounded singleton demands')
    need(field_product(field_grounded,field_reader)==[[1,0],[0,1]], 'GF4 grounded singleton demands')
    need(support(field_grounded)==support(rational_grounded) and support(field_reader)==support(rational_reader), 'grounded recovery support control')
    # A retained unbalanced simple cycle after coefficient-space transfer.
    rational_cycle = [[F(1),F(0),F(1)],[F(1),F(1),F(0)],[F(0),F(1),F(1)]]
    field_cycle = [[1,0,2],[1,1,0],[0,1,1]]
    cycle_reader = field_inverse(field_cycle)
    need(field_product(field_cycle,cycle_reader)==[[int(i==j) for j in range(3)] for i in range(3)], 'GF4 unbalanced cycle singleton demands')
    need(support(field_cycle)==support(rational_cycle) and support(cycle_reader)==support(rational_inverse(rational_cycle)), 'cycle support transfer control')
    # The strongest theorem may change permitted fitting entries and delete
    # individual reader incidences. This integral old endpoint makes that
    # distinction visible even under direct reduction modulo two.
    strict_old_reader = [[1,1,0],[0,1,1]]
    strict_old = multiply(rational_tree,strict_old_reader)
    strict_new_reader = [[1,1,0],[0,0,1]]
    strict_new = field_product(base,strict_new_reader)
    need(all(strict_old[i][i]==strict_new[i][i]==1 for i in range(3)), 'strict transfer preserves diagonal')
    need(strict_old[0][2]==strict_old[2][0]==strict_new[0][2]==strict_new[2][0]==0, 'strict transfer preserves forbidden zeros')
    need(all(not b or a for old,new in zip(strict_old_reader,strict_new_reader) for a,b in zip(old,new)), 'actual reader support shrinks')
    need(support(base)==support(rational_tree), 'strict source supports are unchanged')
    need(strict_old[1][2]%2==0 and strict_new[1][2]==1, 'allowed entry changes rather than preserving old endpoint')
    # Genuine limitation: dependent queries can have incompatible copy readers.
    bad_Q = [[1,1,0],[0,0,1]]
    bad_R = [[1,0],[0,1],[1,1]]
    need(multiply(bad_Q,bad_R)==[[1,1],[1,1]], 'dependent exact endpoint')
    common = [i for i,row in enumerate(bad_R) if all(row)]
    need(common==[2], 'actual reader-support intersection')
    columns = [[bad_Q[i][j] for j in common] for i in range(2)]
    need(rational_rank(columns)==1 and rational_rank([row+[1] for row in columns])==2, 'intersection cannot recover mark')
    return {'three_copy_gauge':{'field':'GF4, w^2+w+1=0','rational_query':rational_tree,'ungauged_query':base,'gauge':gauge,'transferred_query':shifted,'transferred_reader':new_reader,'ungauged_recovery_fails':True},
            'unit_query_singleton_control':{'query':field_grounded,'reader':field_reader},
            'unbalanced_cycle_control':{'query':field_cycle,'reader':cycle_reader},
            'strict_fit_changed_free_control':{'old_query':rational_tree,'old_reader':strict_old_reader,'old_fit':strict_old,
                'new_query':base,'new_reader':strict_new_reader,'new_fit':strict_new,'forbidden_off_diagonal':[[0,2],[2,0]],'reader_incidence_deleted':[1,1]},
            'failed_intersection_control':{'query':bad_Q,'reader':bad_R,'common_support':common,'target_not_in_common_span':True},
            'scope':'Declared exact examples only; these do not replace the quantified written graph and gauge proofs.'}


def bridge():
    Q = [[F(0)]*7 for _ in range(6)]
    for j,(a,b) in enumerate([(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,3)]):
        Q[a][j]=Q[b][j]=1
    C = [[F(i%3==j) for j in range(3)] for i in range(6)]
    M = multiply(C,transpose(C))
    Q6 = [row[:6] for row in Q]
    D = multiply(rational_inverse(Q6),C)
    expected_D = [[F(x,2) for x in row] for row in [[1,1,-1],[-1,1,1],[1,-1,1]]*2]
    need(D==expected_D and rational_rank(Q)==6, 'bridge rank and particular coefficients')
    k = [F(x,2) for x in [-1,1,-1,-1,1,-1,2]]
    need(multiply(Q,[[x] for x in k])==[[0]]*6 and k[6]==1, 'one-dimensional bridge kernel')
    R0 = multiply(D,transpose(C))+[[F(0)]*6]
    need(multiply(Q,R0)==M, 'particular bridge endpoint')
    for i in range(3):
        need(R0[i]==R0[i+3] and k[i]==k[i+3], 'all-reader paired rows from constant and free-parameter coefficients')
    # Equalities of R0 and k prove equal rows for every R0+k z^T, without
    # enumerating z. They also apply to added zero-target reader columns.
    merged = [[row[i]+row[i+3] for i in range(3)]+[row[6]] for row in Q]
    A = [[F(1),F(0),F(1),F(1)], [F(1),F(1),F(0),F(0)], [F(0),F(1),F(1),F(0)]]
    need(merged==multiply(C,A) and all(sum(bool(A[i][j]) for i in range(3))<=2 for j in range(4)), 'coalesced coefficient-two-port family')
    need(multiply(merged,R0[:3]+[R0[6]])==M, 'coalesced particular endpoint')
    return {'query':strings(Q),'marks':strings(C),'particular_coefficients':strings(D),
            'kernel':list(map(str,k)),'query_rank':6,'kernel_dimension':1,
            'all_reader_form':'R=R0+k z^T for arbitrary rational z, including added zero-target columns',
            'paired_rows':[[0,3],[1,4],[2,5]],'coalesced_queries':strings(merged),
            'coefficient_queries':strings(A),'ordinary_three_mark_invoice_floor':18,
            'scope':'The floor follows from the written coalescing and scalar-demand transfer arguments; no claim of attainment or of optimal earlier sample invoices.'}


def run():
    return {'status':'PASS_SPARSE_GAIN_TRANSFER_PREMISES_AND_BRIDGE',
            'input_sha256':PINS,'geometry':geometry(),'controls':controls(),'bridge':bridge(),
            'coefficient_searches':0,'geometry_searches':0,
            'theorem_scope':'Every rational strict fit on the fixed full-group mask, of any rank or term count, has invoice at least334 if all queries or all readers are literal at-most-two-port vectors. The transferred strict fit may change allowed free entries. Endpoint-preserving common-recovery and coefficient-space results are distinct companions.',
            'proof_boundary':'The quantified graph, strict-fit transfer, common-gauge, rank-lift and coalescing deductions are written proofs, independently audited; this executable checks exact premises and controls, not a proof-assistant theorem.'}


if __name__ == '__main__':
    result = run()
    receipt = HERE/'RESULT.json'
    if sys.argv[1:] == ['--write-receipt']:
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(not sys.argv[1:], 'only --write-receipt is accepted')
        need(json.loads(receipt.read_text(encoding='utf-8')) == result, 'committed receipt equals recomputation')
    print(json.dumps({'status':result['status'],'geometry':result['geometry'],
                      'bridge_floor':result['bridge']['ordinary_three_mark_invoice_floor'],
                      'proof_boundary':result['proof_boundary']},indent=2))
