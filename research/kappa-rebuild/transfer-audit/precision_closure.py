#!/usr/bin/env python3
"""Explicit semantic-precision constants for a finite compiled native word.

This is an independent accounting audit, not a claim that the small sample
template realizes the limiting mixed exponent. Apache-2.0; substantial
OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def need(value, message):
    if not value:
        raise AssertionError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def ceil_log2(value):
    """Exact ceiling for a positive rational, clipped below at zero."""
    value = Fraction(value)
    need(value > 0, 'Positive logarithm input')
    result = max(0, value.numerator.bit_length()-value.denominator.bit_length())
    if Fraction(1 << result) < value:
        result += 1
    need(Fraction(1 << result) >= value, 'Exact upper dyadic power')
    return result


def scalar_charge(op):
    """Recompute elementary charge and a direct coefficient-height bound."""
    if op[0] in ('clear', 'copy'):
        return 2, 0
    q = Fraction(op[3], op[4]) if op[0] == 'add' else Fraction(op[2], op[3])
    n, d = abs(q.numerator), q.denominator
    need(n > 0 and d & (d-1) == 0, 'Only nonzero Gaussian-dyadic scalar macros')
    denominator_height = d.bit_length()-1
    if op[0] == 'add':
        primitive = 2*(3+n.bit_length()-1+n.bit_count()+denominator_height)
        height = ceil_log2(1+abs(q))+denominator_height
    else:
        need(op[0] == 'scale' and n & (n-1) == 0, 'Only permitted dyadic-unit SCALE')
        primitive = 2*(abs(n.bit_length()-d.bit_length())+int(q < 0))
        height = ceil_log2(max(Fraction(1),abs(q)))+denominator_height
    need(height <= primitive, 'Primitive allowance dominates coefficient height')
    return primitive, height


def constants(rank, productive, paid, units, unit_charge):
    """Conservative allocation: one owned center per finite mixed instance."""
    need(rank >= 2 and min(productive,paid,units) >= 1, 'Nontrivial fixed template')
    owned = units
    fields = productive+owned
    scalar = units*unit_charge
    E = 64*(fields+rank+paid+scalar+1)**3
    old_form_complete_charge = 2*scalar*fields**2+8*paid+4*fields+4+32*rank
    need(E > old_form_complete_charge, 'Fresh cubic constant pays the entire new word')
    B = paid+E
    C0 = 32*rank*B**2
    need(2*B*(rank-1) >= paid+E, 'Semantic induction coefficient')
    need(2*B >= 8 and C0 > 2*B+18, 'Elementary leaves and outer kernels')
    # Evaluate an independent integer recurrence at all small widths and
    # around several large, discontinuous floor boundaries.
    checked = set(range(1,rank*4+1))
    checked.update(rank**j+offset for j in range(1,7) for offset in (-1,0,1))
    memo = {}
    def excess(e):
        if e not in memo:
            memo[e] = 8*e if e < rank else excess(e//rank)+paid*(e//rank)+E
        return memo[e]
    for width in checked:
        need(excess(width) <= 2*B*width, 'Every checked exact semantic recurrence')
    return {'rank':rank,'productive_fields':productive,'paid_rank_one_calls':paid,
            'mixed_unit_instances':units,'owned_fields_uncredited':owned,
            'physical_fields':fields,'complete_elementary_charge_bound':scalar,
            'E':E,'B':B,'C0':C0,'C1':1,
            'old_form_complete_charge':old_form_complete_charge,
            'integer_recurrence_widths_checked':len(checked)}


def threshold(C0, epsilon, dimension_factor=1):
    """Return compressed p0=2^t, never materializing that huge integer."""
    epsilon = Fraction(epsilon)
    need(0 < epsilon < 1 and dimension_factor >= 1, 'Sublinear dimension')
    a,b = epsilon.numerator,epsilon.denominator
    size = 4*C0*dimension_factor
    logarithmic_upper = size.bit_length()
    exponent = max(4,(b*logarithmic_upper+b-a-1)//(b-a))
    need((b-a)*exponent >= b*logarithmic_upper, 'Exact eventual power inequality')
    need((1 << logarithmic_upper) > size, 'Strict dyadic upper bound on 4 C0 c')
    return {'epsilon':str(epsilon),'dimension_bound':'d <= c*p^epsilon',
            'c':dimension_factor,'p0_encoding':'2^exponent','exponent':exponent,
            'conclusion':'For every p >= p0: Delta=C0*d <= p/4 and p+2*Delta+3 <= 2*p.',
            'no_large_integer_materialized':True}


def stock(productive,rank):
    coefficient = ceil_log2(productive)
    ell = (coefficient+1).bit_length()
    d_exponent = 4*ell+8
    need((1 << d_exponent) > 4*coefficient*(d_exponent+1), 'Row prefix eventually below d/4')
    # This check includes exact floor depth, whole-row padding, and division.
    samples=[]
    for width in (rank-1,rank,rank**2-1,rank**2,rank**3+1):
        depth=0
        e=width
        while e >= rank:
            e//=rank
            depth+=1
        q0=coefficient*depth
        Q=productive**depth
        R=1 << q0
        padded=Q*((R+Q-1)//Q)
        need(R >= Q and R <= padded < 2*R, 'Complete-row padding factor below two')
        need(all(padded % productive**j == 0 for j in range(depth+1)), 'Every descendant has exact productive row divisibility')
        samples.append({'width':width,'depth':depth,'q0_for_K_one':q0,
                        'row_stock':Q,'padded_rows':padded})
    return {'productive_log2_ceiling':coefficient,'depth_recurrence':'D(e)=0 for e<N; 1+D(floor(e/N)) otherwise',
            'q0':'ceil(log2 W)*D(d)','root_padding':'next multiple of W^D(d), once, factor < 2',
            'owned_fields_not_in_productive_stock':True,
            'd0_for_q0_less_than_d_over_four':{'encoding':'2^exponent','exponent':d_exponent},
            'samples':samples}


def main():
    cover_path = HERE.parent/'controller/P3-NATIVE-COVER.json.gz'
    audit_path = HERE/'P3-COVER-AUDIT.json'
    native_path = HERE.parent/'complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz'
    cover,audit,native = read(cover_path),read(audit_path),read(native_path)
    need(audit['input_sha256'] == digest(cover_path), 'Independent complete p3 source binding')
    need(cover['sources'][str(native_path.relative_to(ROOT))] == digest(native_path), 'Exact native words')
    local={}
    for direction,events in native.items():
        counts=Counter(event[0] for event in events)
        need(set(counts) == {'scalar','phase','warp','adapter','residual_adapter','climb','center'}, 'Known native grammar')
        charge=height=0
        for event in events:
            if event[0] == 'scalar':
                cost,bound=scalar_charge(event[1]);charge+=cost;height+=bound
        local[direction]={'records':dict(sorted(counts.items())),
                          'real_scalar_allowance':charge,'direct_scalar_height_bound':height}
    need(local['forward']['real_scalar_allowance'] == 158120 and
         local['backward']['real_scalar_allowance'] == 158168, 'Independent exact native arithmetic invoice')
    primitive=4*local['forward']['real_scalar_allowance']+3*local['backward']['real_scalar_allowance']
    primitive+=112*((22+12+9)*8+8*2)
    need(primitive == cover['scalar_invoice']['conservative_real_scalar_primitive_allowance'] == 1147304,
         'All p3 scalar bridges, terminal shears and swap negations charged')
    non_scalar = 4*sum(n for k,n in local['forward']['records'].items() if k!='scalar')
    non_scalar += 3*sum(n for k,n in local['backward']['records'].items() if k!='scalar')
    wrapper_counts={'native_non_scalar_records':non_scalar,
                    'whole_helper_normalizations':len(cover['cover']['helper_bindings']),
                    'main_contact_monomials':4*len(cover['main_contacts']),
                    'whole_main_endpoint_normalizations':len(cover['main_endpoint_normalizers']),
                    'paid_completion_normalizations':len(cover['cover']['paid_residuals'])}
    # At most two native monomial factors surround a child, each requiring
    # at most a sign and an i phase. Eight covers these and pure bookkeeping.
    # Dense binary address permutations have height zero and retain their
    # separate paid movement implementation; they are not called free scans.
    unit_charge=primitive+8*sum(wrapper_counts.values())
    need(unit_charge == 1494376, 'Complete conservative p3 coefficient/unit-phase allowance')
    example=audit['uniform_rank57']
    fixed=constants(57,example['width'],example['leaves'],example['units'],unit_charge)
    outer=read(HERE.parent/'controller/OUTER-PARAMETERS.json')
    eps=Fraction(outer['outer']['parameters']['epsilon']['rational'])
    stop=Fraction(outer['outer']['parameters']['stop']['rational'])
    stop_log=ceil_log2(2*fixed['rank'])
    stop_exponent=(stop_log*stop.denominator+stop.numerator-1)//stop.numerator
    need(stop*stop_exponent >= stop_log, 'Eventually every internal node has e >= d^beta >= 2N')
    sources=[cover_path,audit_path,native_path,HERE.parent/'controller/OUTER-PARAMETERS.json',
             ROOT/'references/semantic-bulk/pr23/semantic-bulk-17-note.tex',
             ROOT/'notes/stopped-product-complex.tex',ROOT/'notes/compact-control-movement.tex',
             ROOT/'notes/batched-complex-rows.tex',ROOT/'notes/general-clifford-frames.tex']
    result={'schema':'finite-native-template-semantic-closure/1',
            'status':'PASS_SOURCE_BOUND_CHARGE_EFFECTIVE_LINEAR_GUARD_AND_COMPLETE_ROWS',
            'source_sha256':digest(__file__),
            'sources':{str(p.relative_to(ROOT)):digest(p) for p in sources},
            'native_local_accounting':local,'p3_real_scalar_allowance':primitive,
            'conservative_unit_phase_wrapper_counts':wrapper_counts,
            'p3_complete_elementary_charge_bound':unit_charge,
            'general_substitution':{'Z':'W+O','O':'at most U, conservatively U',
              'G':'1494376*U','E':'64*(Z+N+P+G+1)^3','B':'P+E','C0':'32*N*B^2','C1':1,
              'semantic_recurrence':'A(e) <= A(floor(e/N))+P*floor(e/N)+E',
              'induction':'A(e) <= 2*B*e',
              'full_layer':'A_layer <= (2*B+18)*d < C0*d'},
            'small_fully_materialized_template_example':fixed,
            'small_example_eventual_precision_threshold':threshold(fixed['C0'],eps),
            'small_example_row_stock':stock(example['width'],57),
            'small_example_stopping_threshold':{'d0_encoding':'2^exponent','exponent':stop_exponent,'stop':str(stop)},
            'limits':['The rank57 example verifies substitution and is not the limiting winning template.',
              'For the effective winning finite N, recompute its finite W,P,U and substitute these formulas.',
              'Native binary movement, fixed-tape execution and outer analytic transfer remain inherited hypotheses, with new finite constants.',
              'No materialization of an enormous winning uniform word is asserted.']}
    (HERE/'PRECISION-CLOSURE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:result[key] for key in ('status','p3_complete_elementary_charge_bound','general_substitution')}))


if __name__ == '__main__':
    main()
