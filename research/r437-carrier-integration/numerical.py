"""Named numerical/stock admission for the source-bound carrier.

Adapt #3647's finite invoice and #2753's explicit logical-frame reserve;
reuse #4147's independently checked row coefficients. No exponent solver,
no floating-point arithmetic, no physical primitive assumed free.
Chris R / Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W, PHYSICAL, M, REQUESTS = 28416, 28425, 64, 903456
STOCK_MULTIPLIER = math.lcm(W, PHYSICAL)
EPSILON = Fraction(1, 10**16)
PROFILE_C = {1:380160,2:400877,3:22176,4:26592,5:29376,6:17375,7:26496,14:1,42:403}
PROFILE_D = {1:380448,2:400301,3:22464,4:26592,5:29376,6:17375,7:26496,14:1,42:403}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def depth(n):
    need(isinstance(n, int) and n >= 1, 'positive atom width')
    result = 0
    while n >= M:
        n = 42 * (n // M)
        result += 1
    return result


@lru_cache(None)
def gl_order(q):
    need(isinstance(q, int) and q >= 3 and q % 2, 'odd prime domain; primality/source admissibility supplied separately')
    return math.prod(q**64 - q**i for i in range(64))


def stock_unit(q, w):
    need(isinstance(w, int) and w >= 1, 'positive unchanged root precision')
    return STOCK_MULTIPLIER * gl_order(q) * q**(4096*(w-1))


def check_stock_rows(rows, n, q, w):
    """Exact compatible stock, not merely a lower bound on the row count.

    q primality and source denominator admissibility are caller preconditions.
    Applies also to semantic fixtures q<2^80, without numerical admission.
    """
    need(isinstance(rows, int) and rows > 0, 'positive row stock')
    divisor = stock_unit(q,w)**depth(n)
    quotient, remainder = divmod(rows,divisor)
    need(quotient > 0 and remainder == 0, 'compatible original-root stock divisor')
    return quotient


def check_root_domain(e, n, w, h, q, residue_width, index_width, code_width):
    """Exact parameter admission; q primality/source admissibility is a premise."""
    need(all(isinstance(x,int) for x in (e,n,w,h,q,residue_width,index_width,code_width)), 'integer parameter domain')
    need(64 <= e and 1 <= n <= e and w >= 1 and h >= 0, 'internal original root and chronological history')
    need(q > 2**80 and q % 2 == 1, 'admitted numerical prime lower bound')
    need((w-1)**10000 < e**17 <= w**10000, 'root-coupled precision ceil(e^(17/10000))')
    need(2**(h+1) <= 8*e*e and 17*(h+1) <= 20051*w, 'chronological history bound')
    b = q.bit_length()
    expected_L=(q**w).bit_length()+1
    expected_I=e.bit_length()+1
    expected_Q=(2*REQUESTS*gl_order(q)-1).bit_length()
    need(residue_width == expected_L and residue_width <= b*w+2, 'exact canonical residue width')
    need(index_width == expected_I and index_width <= 591*w, 'exact original-root index width')
    need(code_width == expected_Q and code_width <= 4096*b+21, 'exact fresh pooled source vocabulary width')
    return True


def bad_fraction(q, rank):
    """Complementary-minor bound over complete GL64 low classes.

    Requires the authenticated request's split projector and invertible chart,
    and unit diagonal ancestral weights. NUMERICAL.md proves this condition.
    """
    need(q >= 3 and q % 2 and 1 <= rank <= 64, 'split-projector numerical domain')
    return min(Fraction(1), Fraction(64*rank*(q-1), q*(q-2)))


def check_fallback(q, ranks, allowance=32*64*64, epsilon=EPSILON):
    need(ranks and all(isinstance(r,int) and 1 <= r <= 42 for r in ranks), 'actual paid ranks and halving')
    # More conservative than the completed 49,911-call caller. Retain the
    # exact historical 128-row primitive bill so no saving is double counted.
    primitive = 6*128*127+3*128+6*127
    need(primitive <= allowance, 'complete retained fallback children')
    bounds = {r:bad_fraction(q,r) for r in ranks}
    need(all(d <= epsilon for d in bounds.values()), 'per-request complete low-class bad fraction')
    return bounds


def finite_invoice(forward, reverse, local_adds, profile, route_factors=77):
    """Exact #3647 assemble9 finite coefficient with explicit new parameters.

    The retained source/normalizer/physical primitive interface is a premise;
    this formula does not substitute for the actual physical cost ledger.
    """
    E = sum(profile.values())
    need(E == REQUESTS and sum(r*n for r,n in profile.items()) == 1808352, 'source-bound request mass')
    need(forward > 0 and reverse > 0 and local_adds >= 0 and route_factors >= 0, 'finite invoice parameters')
    J = 8*32*9*(222+437)+8*(8*111*32)+2*9*32*437+2*(9*9*32)
    prefix = 2**18 * forward**5 * reverse**4
    parts = {
        'unit_adds_and_bridges':9*32*local_adds+6*3*111*32,
        'J_times_high':J*16*(64*64+1)**2,
        'J_times_physical':J*PHYSICAL,
        'E_times_good':E*(8*64*64+8),
        'E_times_compiler':E*128*128**3,
        'matrix_test':16*64**3,
        'copy_erase_episodes':9*9*32,
        'selectors':2*9*32*((W-1)+437*64*(route_factors+144+2+63+64)),
        'global_prefix':prefix,
        'one':1,
    }
    coefficient = sum(parts.values())
    two = (coefficient+1)**2*(E+1)**2
    row = 2*(64*64+1)+9909+252
    return dict(parts=parts,coefficient=coefficient,two_level=two,J=J,
                prefix_bits=prefix.bit_length(),coefficient_bits=coefficient.bit_length(),
                two_level_bits=two.bit_length(),row=row,requests=E)


def check_finite_envelope(invoice, prefix_cap=2**192, two_cap=2**512, row_cap=20161):
    need(invoice['parts']['global_prefix'] < prefix_cap, 'literal global-prefix envelope')
    need(invoice['two_level'] < two_cap, 'two-level finite coefficient envelope')
    need(invoice['row'] < row_cap, 'logical row coefficient envelope')
    return True


def program_symbols(h,L,I,Q):
    return 2*I+L+6+h*(Q+2*I+90)


def metadata_ledger(V,h,L,I,Q,q):
    need(V>0 and h>=0 and min(L,I,Q)>0, 'metadata ledger domain')
    return ((2**24+1)*(L+I+4)+8*program_symbols(h+1,L,I,Q)
            +16*(h+3)*(2*I+L+8)+2**20*(V.bit_length()+4)
            +2**32*(Q+1)+q*q+2**20)


def metadata_polynomial(b, offset=21):
    """Coefficient of w^2 after replacing each lower degree by w^2.

    L <= (b+2)w, I <=591w, h+1<=1180w, h+3<=1182w,
    Q<=4096b+offset. Excludes only the separately retained Count and q^2.
    """
    Q = 4096*b+offset
    return ((2**24+1)*(b+597)+8*(1182+b+2+6+1180*(Q+1182+90))
            +16*1182*(1182+b+2+8)+2**32*(Q+1)+2**20)


def check_local_reserve(V,h,L,I,Q,q,directory_symbols,table_symbols=0):
    """Unabsorbed logical live-symbol gate; no visited-backing claim."""
    need(directory_symbols>=1 and table_symbols>=0, 'complete directory and table stock')
    E=metadata_ledger(V,h,L,I,Q,q)
    used=8*V+32*directory_symbols+E
    need(used < 11*V, 'explicit local logical reserve')
    return {'payload_allowance':8*V,'directories':32*directory_symbols,'metadata':E,
            'source_tables_separate':table_symbols,'logical_symbols':used+table_symbols}


def bind_compiler(receipts):
    """Bind scalar admission to fresh C/D request/compiler receipts.

    The orchestrator separately runs compiler structural and independent
    all-base/chart checks; a digest receipt alone is not their substitute.
    """
    for variant,expected in [('C',PROFILE_C),('D',PROFILE_D)]:
        row=receipts[variant]
        need(row['variant']==variant and row['requests']==REQUESTS, 'fresh variant/request binding')
        need({int(r):n for r,n in row['profile'].items()}==expected, 'actual pooled C/D profile')
        need(row['rank_mass']==1808352 and row['kinds']=={'COPY':2592,'IDLE':63936,'MOVE':836928}, 'actual native class totals')
        coverage=row['coverage']
        need(coverage['charts']==1235 and coverage['owner_pairs']==179802 and coverage['idle_enumeration']==63936, 'all actual charts, owner pairs and exactly-once idles')
        need(coverage['projectors']['bases']==row['bases'] and row['bases']==(541 if variant=='C' else 542), 'fresh all-base split coverage')
        need(len(coverage['projectors']['sha256'])==64, 'all-base algebra digest')
        need(all(len(row[k])==64 for k in ['input_identity','source_identity','request_sha256']), 'source identity schema')
    need(receipts['C']['source_identity'] != receipts['D']['source_identity'], 'carrier requires fresh source handles')
    need(receipts['C']['request_sha256'] != receipts['D']['request_sha256'], 'changed literal request chronology')
    need(receipts['C']['coverage']['chart_sha256']==receipts['D']['coverage']['chart_sha256'], 'same complete C/D chart inventory')
    need(receipts['D']['code_bits']==receipts['C']['code_bits'], 'no additional carrier vocabulary width; derived C/D equality')
    return {v:{k:receipts[v][k] for k in ('input_identity','source_identity','request_sha256','code_bits','requests','coverage')} for v in ('C','D')}


def rejection_controls():
    old=finite_invoice(49347,1113998,24208,PROFILE_C)
    new=finite_invoice(49347,1123650,24211,PROFILE_D)
    q=2**127-1  # Prime verified below by the exact Lucas-Lehmer recurrence.
    L=(q*q).bit_length()+1;I=(64).bit_length()+1;Q=(2*REQUESTS*gl_order(q)-1).bit_length()
    checks={
      'old_literal_global_prefix':lambda:check_finite_envelope(new,prefix_cap=old['parts']['global_prefix']+1),
      'shortened_prefix_word':lambda:check_finite_envelope(new,prefix_cap=2**176),
      'shortened_two_level_word':lambda:check_finite_envelope(new,two_cap=2**392),
      'understated_row_envelope':lambda:check_finite_envelope(new,row_cap=18355),
      'small_prime_bad_fraction':lambda:check_fallback(3,list(PROFILE_D)),
      'unpaid_fallback':lambda:check_fallback(q,list(PROFILE_D),allowance=98681),
      'zero_bad_event_allowance':lambda:check_fallback(q,list(PROFILE_D),epsilon=Fraction(0)),
      'missing_stock':lambda:check_stock_rows(1,64,3,1),
      'large_but_incompatible_stock':lambda:check_stock_rows(stock_unit(3,1)+1,64,3,1),
      'child_recomputed_precision':lambda:check_root_domain(64,1,1,1,q,L,I,Q),
      'unbounded_history':lambda:check_root_domain(64,64,2,99999,q,L,I,Q),
      'padded_source_width':lambda:check_root_domain(64,64,2,0,q,L,I,Q+1),
      'undersized_residue_word':lambda:check_root_domain(64,64,2,0,q,1,I,Q),
      'undersized_source_word':lambda:check_root_domain(64,64,2,0,q,L,I,1),
      'undersized_root_index':lambda:check_root_domain(64,64,2,0,q,L,1,Q),
      'zero_metadata_reserve':lambda:check_local_reserve(1,0,1,1,1,3,1),
    }
    rejected=[]
    for name,f in checks.items():
        try:f()
        except ValueError:rejected.append(name)
        else:raise ValueError('control unexpectedly admitted: '+name)
    return rejected


def run(receipts=None):
    geo=json.loads((ROOT/'research/bit-p111-r437-gl464-470-20261018/data/GEOMETRY.json').read_text())
    need(geo['max_route_factors']==77, 'retained geometry factor ceiling')
    host=json.loads((ROOT/'research/r437-two-window-carrier/HOST-RESULT.json').read_text())
    need(host['calls']==288 and host['events']=={'old':7814016,'new':7814880}, 'published source word call/event binding')
    for label,reverse,adds in [('old',1113998,24208),('new',1123650,24211)]:
        row=host[label]
        need(row['forward']['l1']==49347 and row['reverse']['l1']==reverse, 'retained independent coefficient coverage')
        need(row['forward']['adds']==row['reverse']['adds']==adds, 'both source orientations scalar invoice')
        need(sum(row['forward']['profile'].values())==sum(row['reverse']['profile'].values())==2915, 'both orientations complete local children')
    old=finite_invoice(host['old']['forward']['l1'],host['old']['reverse']['l1'],host['old']['forward']['adds'],PROFILE_C,geo['max_route_factors'])
    new=finite_invoice(host['new']['forward']['l1'],host['new']['reverse']['l1'],host['new']['forward']['adds'],PROFILE_D,geo['max_route_factors'])
    check_finite_envelope(old);check_finite_envelope(new)
    delta={k:new['parts'][k]-old['parts'][k] for k in old['parts']}
    need(delta['unit_adds_and_bridges']==864 and all(v==0 for k,v in delta.items() if k not in ('unit_adds_and_bridges','global_prefix')),'complete finite coefficient difference')
    # This sample is a numerical domain test, not an executed giant source.
    q=2**127-1;s=4
    for _ in range(125):s=(s*s-2)%q
    need(s==0,'Lucas-Lehmer prime witness q=2^127-1')
    fallback=check_fallback(q,list(PROFILE_D))
    need(STOCK_MULTIPLIER==269241600,'exact compatible stock multiplier')
    need(check_stock_rows(2*stock_unit(3,1),64,3,1)==2,'positive compatible stock control')
    check_root_domain(64,64,2,0,q,(q*q).bit_length()+1,(64).bit_length()+1,(2*REQUESTS*gl_order(q)-1).bit_length())
    need(metadata_polynomial(0)==104541086181 and metadata_polynomial(1)-metadata_polynomial(0)==17592241506793,'coefficientwise pooled metadata polynomial')
    need(1+1180*(8192*81+12311)<2**30,'new full-directory absorption base inequality')
    need(1180*8192 < 3*(1+1180*(8192*81+12311)), 'linear directory numerator grows slower than factor four')
    need((Fraction(10)+Fraction(1,2**125))*W/(W-1)<11, 'whole active-chain geometric reserve')
    need(metadata_polynomial(0)<2**48*597 and metadata_polynomial(1)-metadata_polynomial(0)<2**48,'same named coarse metadata envelope')
    refs=[
      'research/bit-p111-r437-gl464-470-20261018/vendor/assemble9.py',
      'research/bit-p111-r437-gl464-470-20261018/data/GEOMETRY.json',
      'research/bit-p111-r437-gl464-470-20261018/code/invoice_audit.py',
      'research/r437-reverse-row-coefficient/verify.py',
      'research/r437-reverse-row-coefficient/independent.py',
      'research/r437-two-window-carrier/HOST-RESULT.json',
      'research/r437-oq4-caller-binding/RANK26-COST.md',
      'research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/matrices.py',
      'research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/numeric.py',
      'research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/controller.py',
      'research/r437-preparation-composition/vendor/research/selected-bit-physical-caller/inputs/pr2753/PROOF.md',
    ]
    return {'status':'PASS_NAMED_FINITE_COEFFICIENT_AND_CONDITIONAL_LOGICAL_STOCK_BOUNDARY',
      'compiler_binding':bind_compiler(receipts) if receipts is not None else 'NOT_RUN_COMPILER_RECEIPT_REQUIRED_FOR_INTEGRATED_ADMISSION',
      'C':old,'D':new,'exact_component_delta':delta,
      'charged_envelope':{'prefix_bits':192,'two_level_bits':512,'row_cap':20161},
      'bad_event':{'sample_admitted_prime':str(q),'primality':'Lucas-Lehmer 127, 125 exact iterations',
                   'per_rank_fraction':{str(r):str(d) for r,d in fallback.items()},
                   'uniform_q_lower_bound':'q>2^80; q source-admissible odd prime',
                   'per_request_proved_bound':'min(1,64*r*(q-1)/(q*(q-2)))',
                   'required_premises':['fresh split projector and invertible actual chart','complete GL64 low cover','unit diagonal ancestor weights','all high lifts preserve low classification'],
                   'inherited_fallback_children':98682,'charged_allowance_per_request':131072,'all_request_allowance':131072*REQUESTS},
      'stock':{'multiplier':STOCK_MULTIPLIER,'formula':'K=269241600*|GL64(q)|*q^(4096*(w-1)); rows=t*K^D(n), t positive integer',
               'depth':'D(n)=0 below64, else1+D(42*floor(n/64))',
               'metadata_w2_polynomial':{'constant':104541086181,'b':17592241506793},
               'metadata_coarse_envelope':'2^48*(b+597)*w^2 +2^20*(ell(V)+4)+q^2',
               'logical_reserve':'11*V_root+F_q under stated complete-packet/root/lifetime premises',
               'fixed_physical_visited_backing_admitted':False},
      'controls':rejection_controls(),
      'source_sha256':{p:sha256((ROOT/p).read_bytes()).hexdigest() for p in refs},
      'scope':'Exact integer prefix/coefficient and conditional complete-low-class fallback; logical live-symbol reserve, not floating-point error/rounding, fixed-tape visited backing, complete execution time, supplier or selected-kappa admission.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--compiler-receipt',type=Path);args=ap.parse_args()
    receipt=json.loads(args.compiler_receipt.read_text()) if args.compiler_receipt else None
    result=run(receipt)
    if args.write:(HERE/'NUMERICAL-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
