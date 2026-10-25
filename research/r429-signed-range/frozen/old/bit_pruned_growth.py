#!/usr/bin/env python3
"""Normalized coefficient growth for the429-helper common-code controller.

All63 added codes and encoded hosted-helper magnitudes are included. Native
child interiors, rounding defects and physical tape work remain separate.
Apache-2.0; substantial OpenAI Codex assistance.
"""

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bit_cap_copy_local as cap
import bit_prune_audit as prune
import bit_signed_audit as scalar

HERE = Path(__file__).resolve().parent
need = cap.need


def coefficients(records,backward=False):
    rows = [{i:1} for i in range(651)]+[{}]
    prefix = 1
    envelope = {(1,0,0),(0,1,0),(0,0,1)}
    for op,d,s,c,f,p in reversed(records) if backward else records:
        if op == 1:
            rows[d] = scalar.add(rows[d],rows[s],-c if backward else c)
            weights = scalar.row_weights(rows[d])
            envelope.add(weights)
            prefix = max(prefix,sum(weights))
        elif op == (3 if backward else 2):
            rows[651] = rows[d].copy()
        elif op == (2 if backward else 3):
            rows[651] = {}
    return rows,prefix,envelope


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    packed = (HERE/'BIT-SUPPORT-INPUT-WORD.json.gz').read_bytes()
    need(sha256(packed).hexdigest() == '6e4e79c3d4fc9f8d01e3c2429d6794c057214f5bae9f8ab86c03d549f01922f1','support input pin')
    program = json.loads(gzip.decompress(packed))
    keep,records,_ = prune.projected(program)
    need(len(keep) == 651,'pruned word arity')
    f,F,ef = coefficients(records)
    r,R,er = coefficients(records,True)
    codes,code_rows,code_prefix,code_norm = scalar.code(records)
    need(len(codes) == 1499 and [F,R] == [34285,5839860],'local literal word changed')
    ordered_path = HERE/'BIT-NATIVE-CONTROLLER-WORD.json'
    ordered = json.loads(ordered_path.read_bytes())['ordered_controller']
    bound = scalar.global_bound(ordered,[scalar.block_norms(f),scalar.block_norms(r)],
                                [F,R],[ef,er],code_prefix,code_norm)
    # Each terminal DATA bank gets exactly the same nine inverse G factors.
    # N is an isometry under the normalized native permutation contract, so
    # adding the two physical N wrappers does not enlarge this external scalar
    # row bound. This deliberately does not bound a child's internal lift.
    terminal = bound['after_easy_completed_bank_decode_upper_bits']
    owner = json.loads((HERE/'BIT-OWNER-PRUNE.json').read_bytes())
    excess = owner['pruned_plus_two_N_mass']-64*28416
    need(excess == 864,'complete terminal rank mass')
    data = {'status':'PASS_PRUNED_CONTROLLER_NORMALIZED_GROWTH_TWO_N_COST_FAILS',
            'input_support_word_sha256':sha256(gzip.decompress(packed)).hexdigest(),
            'projected_records_sha256':sha256(cap.canonical(records)).hexdigest(),
            'ordered_common_code_controller_sha256':sha256(ordered_path.read_bytes()).hexdigest(),
            'source_code_ADDs':len(codes),'source_code_exact_prefix':code_prefix,
            'source_code_endpoint_norm':code_norm,'local_exact_prefix':[F,R],
            'local_block_norms':[scalar.block_norms(f),scalar.block_norms(r)],
            'local_prefix_envelopes':[sorted(ef),sorted(er)],
            'whole63_code_controller':bound,
            'with_all8_terminal_bank_decodes_normalized_prefix_bits':terminal,
            'terminal_normalized_round_up_to64_bits':64*((terminal+63)//64),
            'literal_scalar_ADDs_per_nine_call_replica':{
                'nine_complete_local_words':9*13223,
                '63_extra_source_codes':63*1499,
                '18_ordinary_bank_shears_over111_ports':18*111,
                '72_terminal_bank_code_factors':72*1499,
                'total_including_terminal':9*13223+63*1499+18*111+72*1499},
            'terminal_rank1_children_per_replica':888,
            'whole_rank_mass_exceeds64W_at_beta0_by':excess,
            'all_nonnegative_exponent_failure_proof':'Every complete child tariff is at least its rank for beta>=0. The included local, restricted-owner idle and888-per-replica terminal children already have rank mass64W+864, before fallback. Thus this particular two-N completion cannot pass the modern recurrence at any beta>=0.',
            'limits':['601-bit terminal upper and640-bit reserve cover normalized external scalar coefficients only',
                      'native child internal amplification, rounded MOVE/COPY defects, exact COPY reuse and all-size precision admission are not supplied',
                      'physical source/address access and finite tape return are still paid obligations',
                      'two-N mass failure concerns this complete W28416 construction, not every terminal decoder or changed recursive interface']}
    path = HERE/'BIT-PRUNED-GROWTH.json'
    if args.write:
        path.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == json.loads(cap.canonical(data)),'complete pruned growth receipt differs')
    print(data['status'])
    print('common controller458bits; terminal601bits normalized; rankmass exceeds64W by864')


if __name__ == '__main__':
    main()
