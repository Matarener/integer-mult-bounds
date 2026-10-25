# SPDX-License-Identifier: Apache-2.0
"""Independent cost/guard arithmetic. Caller authenticates frozen inputs first.

No predecessor executable is imported. This is a conditional integer envelope,
not an implementation of the inherited physical Machine.
"""
from collections import Counter
from fractions import Fraction


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def natural(value, reason, positive=False):
    require(type(value) is int and value >= int(positive), reason)
    return value


def depth(width):
    natural(width, 'integer width')
    steps = 0
    while width >= 73:
        width = 48 * (width // 73)
        steps += 1
    return steps


def leaf_entry(width, global_d):
    natural(width, 'positive native width', True)
    natural(global_d, 'positive global width', True)
    require(width <= global_d, 'native width bounded by global d')
    return width < 73 or width**1000 < global_d


def height_choice(width, global_d):
    if leaf_entry(width, global_d):
        return {'kind': 'leaf', 'height': 8*width}
    return {'kind': 'recursive', 'height': '2 B lambda'}


def lift_integer(value, old_bits, reserve):
    natural(old_bits, 'positive component width', True)
    natural(reserve, 'nonnegative reserve')
    require(type(value) is int and -(1 << (old_bits - 1)) <= value < (1 << (old_bits - 1)),
            'coarse component fits')
    # q_work=q_coarse*2^-reserve; reserve+1 high sign bits additionally for Gaussian-norm conversion.
    return value << reserve, old_bits + 2 * reserve + 1


def promote_into_backend(value, coarse_bits, reserve, backend_bits):
    natural(backend_bits, 'positive admitted backend width', True)
    lifted, required = lift_integer(value, coarse_bits, reserve)
    require(backend_bits >= required, 'admitted backend width below guard requirement')
    return lifted, backend_bits


def project_integer(value, coarse_bits, reserve):
    natural(coarse_bits, 'positive component width', True)
    natural(reserve, 'nonnegative reserve')
    require(type(value) is int and value % (1 << reserve) == 0,
            'completed child is exactly on coarse grid')
    result = value // (1 << reserve)
    require(-(1 << (coarse_bits - 1)) <= result < (1 << (coarse_bits - 1)),
            'coarse return headroom')
    return result


def uniform_grid_guard(input_bound, height, reserve, signed_bits):
    """Check strict |input|<input_bound in coarse-grid integer units.

    Height bounds the whole-array Gaussian supremum by factor 2^height and
    denominator debt height in Gaussian modulus. A real/imaginary component
    bound gives Gaussian modulus <2*input_bound. Thus reserve>=height and
    input_bound*2^(height+reserve+1)<=2^(bits-1) suffice.
    This checks a sufficient envelope, never an optimality lower bound.
    """
    natural(input_bound, 'positive integer input bound', True)
    natural(height, 'nonnegative height')
    natural(reserve, 'nonnegative reserve')
    natural(signed_bits, 'positive width', True)
    require(reserve >= height, 'denominator reserve too small for envelope')
    require(input_bound << (height + reserve + 1) <= 1 << (signed_bits - 1),
            'magnitude reserve too small for envelope')
    return True


def census(word):
    require(type(word) is list, 'literal event list')
    counts = Counter()
    for e in word:
        require(type(e) is list and e and type(e[0]) is str, 'event syntax')
        require(e[0] in ('add','clear','line','map','begin','end','checkpoint'), 'unknown work event')
        if e[0] == 'add':
            c = Fraction(e[3])
            require(c in (1, -1, Fraction(1, 4), Fraction(-1, 4)), 'scalar alphabet')
            counts['unit' if abs(c) == 1 else 'quarter'] += 1
        elif e[0] == 'clear': counts['clear'] += 1
        elif e[0] == 'line':
            require(type(e[3]) is int and e[3] in (-1, 1), 'signed line')
            counts['H1'] += 1
        elif e[0] == 'map': counts['map'] += 1
    require(dict(counts) == {'clear': 416, 'unit': 1820, 'H1': 224,
                            'quarter': 896, 'map': 352}, 'frozen candidate census')
    counts['wrappers'] = 2 * counts['H1']
    counts['allowance'] = 8*counts['unit'] + 12*counts['quarter'] + 2*counts['clear']
    return dict(counts)


def controls():
    cases = 0
    for bits in range(2, 8):
        for reserve in range(5):
            for x in range(-(1 << (bits-1)), 1 << (bits-1)):
                lifted, widened = lift_integer(x, bits, reserve)
                require(widened == bits+2*reserve+1, 'width bookkeeping')
                require(project_integer(lifted, bits, reserve) == x, 'exact signed roundtrip')
                cases += 1
    rejection = []
    for name, f in [
        ('nonzero dropped bit', lambda: project_integer(9, 4, 2)),
        ('negative nonzero dropped bit', lambda: project_integer(-9, 4, 2)),
        ('return overflow', lambda: project_integer(32, 4, 2)),
        ('insufficient fractional reserve', lambda: uniform_grid_guard(8, 3, 2, 10)),
        ('insufficient signed reserve', lambda: uniform_grid_guard(8, 3, 3, 10)),
        ('boolean reserve', lambda: lift_integer(1, 3, True)),
        ('backend width shortfall', lambda: promote_into_backend(1,4,3,10)),
    ]:
        try: f()
        except ValueError: rejection.append(name)
        else: raise ValueError('accepted negative control: '+name)
    require(uniform_grid_guard(8, 3, 3, 11), 'positive envelope boundary')
    require(promote_into_backend(-7,4,3,19) == (-56,19), 'surplus sign extension preserves backend width')
    # Equality at the signed capacity is permitted here because the input
    # magnitude bound is strict. The actual maximum signed integer is separate.
    return {'signed_roundtrips': cases, 'rejections': rejection}


def audit(word):
    counts = census(word)
    gamma = (1 << 1296)
    for i in range(1, 37): gamma *= (1 << (2*i))-1
    require(gamma < 1 << 2628, 'orthogonal cover upper bound')
    L = 14336 * gamma
    require(L < 1 << 2642 and L % 7 == 0, 'literal row divisor')
    s = 1041408 * gamma
    require(s < 1 << 2648, 'selected rank-height coefficient')
    B = s + (1 << 100000)
    require(B < 1 << 100001, 'uniform inherited B bound')
    C0 = 1 << 210000
    require(8*B+26 < 2*C0, 'existing physical width dominates callback guard')
    require(2*C0-8*B-6 >= 22, 'even constant supplies strict signed margin')
    # Independent exact arithmetic for inherited stock; proof in COST.md.
    stock_cases = []
    for lam in (1, 2, 72, 73, 74, 146, 1000, 10000, 10**9):
        parent = 73*lam
        dp, dc = depth(parent), depth(lam)
        require(dc <= dp-1, 'parent leaves adequate child stock')
        require(depth(lam) <= lam//73, 'simple stock capacity bound')
        stock_cases.append({'lambda': lam, 'parent_depth': dp, 'child_depth': dc,
                            'reusable_child_stock_exponent': dp-1})
    return {
      'status': 'PASS_CONDITIONAL_RECURSIVE_GUARD_AND_COST_ARITHMETIC',
      'census': counts,
      'height_contract': {
        'inherited': 'A(e)<=2 B e; B=1041408 Gamma+2^100000',
        'Gamma_upper_power_two': 2628, 'B_upper_power_two': 100001,
        'child_height_reserve': 'a=8lambda at admitted direct leaves; a=2 B lambda otherwise',
        'common_coarse_grid': 'q_c=h*2^(-9-3(lambda-1))',
        'common_coarse_width': 'W_c=P+28+6(lambda-1)',
        'working_grid': 'q_w=q_c*2^(-a)',
        'required_width': 'W_req=W_c+2a+1 <= P+29+6(lambda-1)+4B lambda',
        'working_width': 'H=p+2C0d+3; C0=2^210000; retain admitted parent component_bits H',
        'admission': 'H>=W_req; append a low zeros and H-W_c-a high sign bits',
        'sufficient_subdomain': 'P<=p+4Bd+1 and lambda<=d imply W_req<=p+(8B+6)d+24<H by 8B+26<2C0',
        'width_inequality_exact': True,
        'complete_native_error': 'zero, conditional on inherited exact Machine refinement and this guard',
        'asymptotic': 'Actual inherited H and global Compact p,G are unchanged. O(p) alone is not physical width admission.',
        'boundary': 'Inherited height applies to arbitrary correlated bounded input coefficients; Machine exact C endpoint projects to q_c by the authenticated caller grid theorem.'},
      'physical_bill': {
        'decoder': 'sum(j=1..224) T_C(lambda,v_j,p,d,H)+448 T_M+352 T_cover+1820 T_add+896 T_quarter+416 T_clear+T_lift+T_project+T_park+T_restore',
        'units': 'Each T is actual complete physical time on its matching packet/width/layout. Sum over actual owners and invocations; no unknown T is zero.',
        'native_envelope': 'Inherited fixed-source Machine bound, exact C endpoint; direct O(lambda V) only at admitted leaf cuts.',
        'entry_subdomain_status': 'The sufficient P bound is an explicit domain, not a proved QQ16 producer output bound.',
        'conversion': 'For each callback, promote its complete coarse input into the one reusable wide workspace, run exact Machine, verify low-bit divisibility and sign extension, and return the coarse packet. Both224-call words pay these conversions. Only one child workspace is live.',
        'numeric_comparison_only': 'At common caller W_c and common admitted callback H with identical prescribed callback/movement bounds, PR4106 removes exactly100 complex-field ADDs=200 real-component ADDs per coordinate versus PR4015.',
        'unchanged_child_moment': 'Both4015and4106:224*(1/73)^(1-a) before a proved usage/volume coefficient and other charges.',
        'actual_global_credit': None},
      'stock': {'L': '14336 Gamma', 'sufficient_parent': 'L^D0(73lambda) divides R',
                'child': 'rows U=R/L; width lambda; after+=72lambda K',
                'reuse': 'All224 sequential calls reuse U; no factor224 row reservation',
                'samples': stock_cases},
      'leaf_controls': {'lambda1_d73': height_choice(1,73), 'lambda73_equal_cutoff': height_choice(73,73**1000), 'lambda73_above_cutoff': height_choice(73,73**1000+1)},
      'controls': controls(),
      'scope': ['No new recursive provider profile or kappa.',
                'Ordinary backend, native identity, hosting/refinement and long-record premises inherited.',
                'Actual decoder insertion, returned-bank lifetimes and physical wrappers/maps must be established separately.',
                'No six-tape claim; inherited Machine has a much larger fixed tape inventory.',
                'Arithmetic envelopes do not prove tape execution or semantic endpoint identities.']}
