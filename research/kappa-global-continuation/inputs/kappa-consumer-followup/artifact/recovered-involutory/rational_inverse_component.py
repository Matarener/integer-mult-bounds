#!/usr/bin/env python3
"""Exact rational J-inverse component and the constant-divisor transducer.

This is a changed arithmetic contract, not an admitted dyadic supplier.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import gzip
import json
import modern_native_component as component


def multiply_code(R, K, bank, frame, divisor):
    out = []
    for k, row in enumerate(R):
        out.append(component.clear(frame))
        for p, value in sorted(row.items()):
            out.append(component.scalar(('C',0),('L',bank+p),value,frame))
        if divisor != 1:
            out.append(['divide_constant',['C',0],divisor,frame])
        for p, image in enumerate(K):
            if k in image:
                out.append(component.scalar(('L',bank+p),('C',0),-image[k],frame))
        out.append(component.clear(0))
    return out


def rational_reference_events(events):
    # This conversion is an exact rational reference semantics only. The new
    # division macro is not passed off as an accepted Gaussian-dyadic SCALE.
    out = []
    for e in events:
        if e[0] == 'divide_constant':
            out.append(['scalar',['scale',e[1],1,e[2]],e[3]])
        else:
            out.append(e)
    return out


def exact_rational_reference(events):
    return component.replay(rational_reference_events(events))


def divide13_unsigned(value):
    quotient, remainder = 0, 0
    for bit in bin(value)[2:]:
        t = 2*remainder+int(bit)
        output = int(t >= 13)
        remainder = t-13*output
        quotient = 2*quotient+output
    return quotient,remainder


def transducer_check():
    transitions = []
    for r in range(13):
        for bit in (0,1):
            t = 2*r+bit
            q, s = int(t >= 13), t-13*int(t >= 13)
            component.need(q in (0,1) and 0 <= s < 13 and t == 13*q+s, 'division transition')
            transitions.append([r,bit,q,s])
    fixtures = [0,1,12,13,14,25,26,27]
    fixtures += [(1<<bits)+r for bits in (8,32,128,512,2048) for r in range(13)]
    for value in fixtures:
        q,r = divide13_unsigned(value)
        component.need(value == 13*q+r and 0 <= r < 13, 'long division fixture')
    return {'remainder_states':13,'binary_transitions':transitions,'exact_integer_fixtures':len(fixtures),
            'signed_rule':'Divide absolute value and restore sign; truncation error is strictly below one output-grid unit.',
            'scan_cost':'One finite-state step per input bit, plus constant sign/output handling; optional guard precision appends a fixed number of zero bits.',
            'compiler_scope':'A concrete finite-state constant-divisor algorithm is supplied. Integration as a pointwise multitape scalar primitive is not yet a retained compiler certificate.'}


def norm_inf(matrix):
    return max(sum(map(abs,row.values()),Q(0)) for row in matrix)


def query_prefix_check(R, K):
    """Exact source and roundoff row norms through every serial query prefix."""
    bank = [{p:Q(1)} for p in range(112)]
    peak_query = peak_query_error = peak_bank = peak_bank_error = Q(0)
    for k,row in enumerate(R):
        query = {}
        for p,a in sorted(row.items()):
            component.add(query,bank[p],a)
            peak_query = max(peak_query,sum(abs(x) for i,x in query.items() if i < 112))
            peak_query_error = max(peak_query_error,sum(abs(x) for i,x in query.items() if i >= 112))
        component.need(query == row, 'earlier divisions changed completed query')
        query = {i:x/13 for i,x in query.items()}
        query[112+k] = Q(1)
        for p,image in enumerate(K):
            if k in image:
                component.add(bank[p],query,-image[k])
                peak_bank = max(peak_bank,sum(abs(x) for i,x in bank[p].items() if i < 112))
                peak_bank_error = max(peak_bank_error,sum(abs(x) for i,x in bank[p].items() if i >= 112))
    component.need((peak_query,peak_query_error,peak_bank,peak_bank_error) ==
                   (Q(56),Q(9,2),Q(77,26),Q(1)), 'exact division prefix bounds')
    return {'query_prefix_input_l1':str(peak_query),'query_prefix_error_l1':str(peak_query_error),
            'source_prefix_input_l1':str(peak_bank),'source_prefix_error_l1':str(peak_bank_error),
            'interpretation':'For input radius B and individual division error <delta, every query prefix has magnitude <=56 B+(9/2)delta and every source prefix <=(77/26)B+delta. Six query integer guard bits suffice when B>=delta.'}


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inputs',type=Path,default=here/'modern-source/inputs')
    ap.add_argument('--out',type=Path,default=here/'rational-inverse-results')
    a = ap.parse_args()
    component.need(component.digest(a.inputs/'NATIVE-RECEIPT.json') == component.NATIVE_RECEIPT_SHA, 'source receipt')
    receipt = component.read(a.inputs/'NATIVE-RECEIPT.json')
    result = {'status':'PASS_EXACT_RATIONAL_COMPONENT_NOT_SUPPLIER','transducer':transducer_check(),'providers':{}}
    a.out.mkdir(exist_ok=True)
    for name, item in receipt['providers'].items():
        local = a.inputs/'native-cache'/item['word_sha256']/'local'
        for basename in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz'):
            component.need(component.digest(local/basename) == item['complete_native_files']['local/'+basename], 'native source '+basename)
        word, programs = [component.read(local/f) for f in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz')]
        R,K,P,J,clean,dirty = component.clean_reconstruction(word,programs)
        KR = component.matmul(K,R)
        inverse = []
        for p,row in enumerate(KR):
            target = {p:Q(1)}
            component.add(target,row,Q(-1,13))
            inverse.append(target)
        identity = [{p:Q(1)} for p in range(112)]
        component.need(component.matmul(J,inverse) == component.matmul(inverse,J) == identity, 'both exact inverse orders')
        component.need(component.matmul(J,K) == [{k:-13*x for k,x in row.items()} for row in K], 'JK=-13K')
        component.need(norm_inf(K) == 1 and norm_inf(R) == 56, 'query error norms')
        query_prefix = query_prefix_check(R,K)
        bills, changed = {}, {}
        for orientation in ('forward','backward'):
            back = orientation == 'backward'
            code = multiply_code(R,K,112 if back else 0,0 if back else 1,13 if back else 1)
            component.boundary_check([e for e in code if e[0] != 'divide_constant'],word,back,'code')
            component.need(all(e == ['divide_constant',['C',0],13,0] for e in code if e[0] == 'divide_constant'), 'division native frame')
            changed[orientation] = code+clean[orientation] if back else clean[orientation]+code
            got = exact_rational_reference(changed[orientation])
            for p in range(632):
                expected = {(p,()):Q(1)}
                if back and p < 112:
                    component.add(expected,{(112+p,()):Q(-1)})
                elif back and p < 224:
                    expected = {(112+j,()):x for j,x in inverse[p-112].items()}
                elif not back and p < 112:
                    expected = {(j,()):x for j,x in J[p].items()}
                elif not back and p < 224:
                    component.add(expected,{(j,()):x for j,x in J[p-112].items()})
                component.need(got['L',p] == expected, 'rational endpoint '+orientation+':'+str(p))
            component.need(all(not row for r,row in got.items() if r[0] in 'CZ'),'private cleanup')
            dyadic = [e for e in changed[orientation] if e[0] != 'divide_constant']
            profile = component.core_frame_check(word,clean[orientation])
            component.need(profile == {1:2440,2:725,3:224,4:102,5:20},'center-free profile')
            bills[orientation] = {'retained_dyadic_scalar_bill':component.scalar_bill(dyadic),
                'complex_divisions_by_13':8 if back else 0,'real_divisions_by_13':16 if back else 0,
                'profile':profile,'rank_mass':sum(k*v for k,v in profile.items()),'extra_native_lines':0,
                'exact_rational_scalar_prefix':component.scalar_prefix(rational_reference_events(changed[orientation]))}
        (a.out/f'PROGRAMS-{name}.json.gz').write_bytes(gzip.compress(json.dumps(changed,sort_keys=True,separators=(',',':')).encode(),mtime=0))
        result['providers'][name] = {'source_word_sha256':item['word_sha256'],'columns':632,'arbitrary_helpers_restored':408,
            'exact_norms':{'R':str(norm_inf(R)),'K':str(norm_inf(K)),'J':str(norm_inf(J)),'J_inverse':str(norm_inf(inverse))},'query_prefix':query_prefix,'local_bills':bills}
        print('PASS_RATIONAL_LOCAL_COMPONENT',name,'columns=632 mass=5070 new_H1=0 scalar=173532 backward_real_div13=16',flush=True)
    result['rounding_theorem'] = {'domain':'Per-real-component sup norm; all dyadic query/scatter operations considered exact for this incremental bound.',
        'division_error':'Each of the eight query divisions has additive error e_k with |e_k|<delta for truncation to output grid delta.',
        'source_error':'-K e, componentwise absolute error < delta because ||K||_infty=1.',
        'target_error':'J K e=-13 K e, componentwise absolute error <13 delta.',
        'noninterference':'R_i K_j=0 for i!=j, so earlier exact dyadic scatters, including division error, do not change later source query rows.',
        'four_extra_fraction_bits':'delta=2^(-p-4) implies added target error <(13/16)*2^-p; source error <(1/16)*2^-p.',
        'input_accumulator_bound':'Every completed query is bounded by 56B; every accumulator prefix including earlier division errors is bounded by 56B+(9/2)delta. Six integer guard bits suffice when B>=delta.',
        'scope_limit':'Rounding in other arithmetic and inherited recursive native calls is additional and must enter a complete precision recurrence.'}
    result['full_field_consumer_screen'] = {'changed_local_calls':9,'removed_H8_calls':72,'deleted_rank_mass':576,
        'literal_terminal_full_queries':72,'assumed_H8_tariff_rank_mass':576,'net_rank_mass_saving':0,
        'conclusion':'The literal 72-query H8 terminal implementation exactly spends the centre deletion allowance before any extra scalar, storage, division, routing or precision costs. This implementation yields no kappa gain.',
        'unresolved':'A different complete terminal implementation or a cheaper observation tariff has not been excluded; no upper bound below72 H8 is constructed here.'}
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
