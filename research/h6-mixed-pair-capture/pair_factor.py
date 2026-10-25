"""Exact mixed-source two-column factors and independently priced entries."""
from fractions import Fraction as F
from e8_exact import need,dot


def binary_rank(values):
    basis={}
    for v in values:
        while v:
            p=v.bit_length()-1
            if p not in basis:basis[p]=v;break
            v^=basis[p]
    return len(basis)


def kernel(pairing):
    return F(pairing**3-4*pairing,48)


def coefficient(target,source,same=False):
    value=dot(target,source)
    need(value%4==0,'integral H6 pairing')
    return F(int(same))-kernel(value//4)


def mixed_block(A,B):
    # A,B are the two normalized root pairings. Identity applies only when
    # the two root lines are both equal, i.e. A=B=2 in canonical orientation.
    diagonal=(A==B==2)
    return [[F(int(diagonal and row==col))-kernel(A+(-1 if row^col else 1)*B)
             for col in range(2)] for row in range(2)]


def rank(matrix):
    a=[list(map(F,row)) for row in matrix];pivot=0
    for col in range(len(a[0]) if a else 0):
        at=next((i for i in range(pivot,len(a)) if a[i][col]),None)
        if at is None:continue
        a[pivot],a[at]=a[at],a[pivot];q=a[pivot][col]
        a[pivot]=[x/q for x in a[pivot]]
        for i in range(len(a)):
            if i!=pivot and a[i][col]:
                q=a[i][col];a[i]=[x-q*y for x,y in zip(a[i],a[pivot])]
        pivot+=1
    return pivot


def factor_columns(matrix,sigma=None):
    need(len(matrix)>0 and all(len(row)==2 for row in matrix),'complete two-column bucket')
    if not any(any(row) for row in matrix):return [],[[] for _ in matrix]
    if sigma is not None:
        need(sigma in (-1,1) and all(row[1]==sigma*row[0] for row in matrix),'exact signed column relation')
        return [[F(1),F(sigma)]],[[row[0]] for row in matrix]
    return [[F(1),F(0)],[F(0),F(1)]],[list(row) for row in matrix]


def product(D,G):
    return [[sum((D[i][k]*G[k][j] for k in range(len(G))),F(0)) for j in range(2)] for i in range(len(D))]


def primitive(value):
    q=F(value)
    if not q:return 0
    a=abs(q.numerator)
    return 3+(a.bit_length()-1)+a.bit_count()+(q.denominator.bit_length()-1)


def invoice():
    old_R=14400*2*7312+270*8*7744
    removed=14400*(2*63*56+2*72)
    new_R=old_R-removed
    D_removed=14400*(2*63*56*2+2*72*8)
    old_D=480337920;new_D=old_D-D_removed;D5=3363840
    G_entries=old_R  # Two captures into one bank: no deleted source read.
    old_scalar=16*old_D+6*D5+8*G_entries
    new_scalar=16*new_D+6*D5+8*G_entries
    histogram={1:2*new_R,8:4336,9:32,15:new_R,16:59760,17:1600}
    need(old_R==227312640 and new_R==123632640,'exact helper invoice')
    need(old_scalar-new_scalar==2*primitive(F(1,16))*D_removed,'complete changed scalar invoice')
    hosted=[]
    for stages in (3,5,7):
        m=16*stages+1;q,pad=divmod(m,17)
        stock=F(stages*removed,q)
        terms=[(F(2*stages*removed),1),(F(15*stages*removed),15)]
        if pad:terms.append((F(stages*removed*pad,q),pad))
        mass=sum(v for v,r in terms)
        need(mass==m*stock,'removed complete helper mass equals m times formal stock')
        hosted.append({'stages':stages,'m':m,'replication_q':q,'pad':pad,
                       'formal_stock_removed':str(stock),'rank_mass_removed':str(mass),
                       'mass_rank_terms_removed':[[str(v),r] for v,r in terms],
                       'coverage_deficit_change':'0',
                       'scope':'Existing fractional row-stock/padding convention only; not a physical reserve proof.'})
    return {'old_helpers':old_R,'new_helpers':new_R,'helpers_removed':removed,
            'old_scatter_entries':old_D,'new_scatter_entries':new_D,'scatter_entries_removed':D_removed,
            'capture_entries_old_and_new':G_entries,'abs5_over16_entries_old_and_new':D5,
            'old_compensation_component_primitives':old_scalar,'new_compensation_component_primitives':new_scalar,
            'component_primitive_saving':old_scalar-new_scalar,
            'new_asymmetric_combined_forward':new_scalar+243600112,
            'new_asymmetric_combined_dual':new_scalar+243602560,
            'new_full_local_histogram':{str(k):v for k,v in histogram.items()},
            'old_full_local_rank_mass':3865333216,
            'new_full_local_rank_mass':sum(k*v for k,v in histogram.items()),
            'helper_path':[1,15,1],'positive_rank_helper_transitions_removed':3*removed,
            'conditional_hosted_helper_deltas':hosted,'new_fractional_denominator':False,
            'capture_range_old':'E+X','capture_range_new':'E+2X',
            'capture_range_scope':'Forward logical mixed-source capture cut only; full and dual precision remain open.',
            'physical_precision_allocator_tape_stock_joint_kappa':'unresolved, not inferred from semantic invoices'}
