#!/usr/bin/env python3
"""One source-bound PR5580 native interface; credited PR5548 dense arithmetic.

Prepared for Chris R/Clear1nsight with OpenAI Codex assistance. Apache-2.0.
No complete caller, source constructor, funding engine or native universe runs.
"""
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

B = Path(__file__).resolve().parent
S = B/'sources'
HEAD = '6efa248cf456d6101d757e9d09ba29711d18a13a'
COMPILER = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
LITERAL = '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38'
DENSE = '43fd40847a0853c0ac511d58ce77ef822a5c6dd1b25f662f01cefaa3196a2f7d'
CAPSULE = '59768da554e11b11fae52d07f520f50684cc7a9ee0bec2873edbcd6b63814837'
WORD = 'b2a98c4bd0dbe86c09e9d15ee060dcf1aab09dbef90aa1e2127676f4039f406b'
AUTHOR_RESULT = 'aab659f8cfed61fb5e2dca1f5bff1cdd7a493733a4b36d5433d7c332c5ccf78c'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(name):
    raw = (S/name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def authenticate_bytes(raw, digest):
    need(sha(raw) == digest, 'source authentication before scientific import')


def authenticate():
    manifest = json.loads((B/'INPUTS.json').read_bytes())
    need(manifest['head'] == HEAD and manifest['target_pair'] == [3,737] and manifest['rank'] == 4,
         'one frozen native interface')
    for row in manifest['files']:
        raw = (B/row['file']).read_bytes()
        authenticate_bytes(raw,row['sha256'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(blob == row['git_blob'], 'source Git blob '+row['file'])
    for file, digest in [('compiler.py',COMPILER),('literal.py',LITERAL),('dense.py',DENSE),
                         ('WORD5580.json.gz',WORD),('5580-RESULT-raw.json',AUTHOR_RESULT),
                         ('pr5545-source-closure.tar.gz',CAPSULE)]:
        authenticate_bytes((S/file).read_bytes(),digest)
    need(read('5580-SOURCES.json')['retained_source']['sha256'] == CAPSULE,
         '5580 retains exact source capsule')
    with tarfile.open(S/'pr5545-source-closure.tar.gz') as archive:
        for fixture, path in [('compiler.py','research/p104-native-channel/vendor/clifford_exact.py'),
                              ('literal.py','research/p104-native-channel/vendor/native_verify.py'),
                              ('local.py','research/p104-productive-controller/local.py')]:
            need(archive.extractfile(path).read() == (S/fixture).read_bytes(), 'actual source recipe convention '+fixture)
    for pairfile, resultfile in [('dense-QUALIFIED-PAIR.json','dense-QUALIFIED-RESULT.json'),
                                  ('old182-PAIR.json','old182-RESULT.json')]:
        pair = read(pairfile)
        need(pair['complete_output_equal'] and pair['scientific_fields_excluded'] == 0,
             'retained complete qualification pair')
        authenticate_bytes((S/resultfile).read_bytes(),pair['result_sha256'])
    # Source-currentness is a frozen curator statement, not an inference from age.
    gate = json.loads((B/'SOURCE-GATE.json').read_bytes())
    need(gate['status'] == 'CLEAR_FOR_ROOT_TO_FREEZE_ONE_SCOPED_NATIVE_PAIR_REQUEST' and
         gate['source']['head'] == HEAD and gate['source']['current_head_equals_frozen'] is True and
         gate['pair']['from_basis'] == [] and gate['pair']['to_basis'] == [11,21,33,455] and
         gate['pair']['event'] == 12658 and gate['pair']['register'] == 451 and gate['pair']['rank'] == 4 and
         gate['ownership']['no_new_explicit_competing_pair_audit_observed'] is True,
         'fresh exact-head and owner/scope source gate')
    return manifest, gate


def load(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            j = v.bit_length()-1
            if j not in pivots:
                pivots[j] = v
                break
            v ^= pivots[j]
    return len(pivots)


def target_contract(word):
    need(word['public'] == 735 and word['frames'][3] == [] and word['frames'][737] == [11,21,33,455],
         'exact ordered source frame bytes')
    need(rank(word['frames'][737]) == len(word['frames'][737]) == 4, 'independent literal rank-four frame')
    occurrences = [[i,e[1],e[4]] for i,e in enumerate(word['program'])
                   if e[0] == 'MOVE' and e[2:4] == [3,737]]
    need(occurrences == [[12658,451,False]], 'all actual paid occurrences of nominated map')
    need(word['program'][12658] == ['MOVE',451,3,737,False], 'literal paid register451 binding')
    return occurrences


def existing_receipt_check(word):
    a,b = word['frames'][3],word['frames'][737]
    refword = read('WORD5551.json.gz')
    full = read('5572-FULL-CHECK.json')['maps']
    hits5572 = [r for r in full if r[0][0] in ('move','helper') and
                refword['frames'][r[0][1]] == a and refword['frames'][r[0][2]] == b]
    oldword = read('WORD5545.json.gz')
    old = read('old182-RESULT.json')['maps']
    hits182 = [r for r in old if oldword['frames'][r['old_frame']] == a and oldword['frames'][r['new_frame']] == b]
    successor = read('WORD5569.json.gz')
    bindings = read('5585-PR5585-BINDINGS.json')
    canonical = json.dumps(bindings,sort_keys=True,separators=(',',':')).encode()
    need(sha(canonical) == read('5585-RESULT.json')['bindings_sha256'], '5585 canonical receipt hash; not raw-byte hash')
    hits5585 = [r for r in bindings['occurrences'] if r['task'][0] in ('move','helper') and
                successor['frames'][r['task'][1]] == a and successor['frames'][r['task'][2]] == b]
    need(not hits5572 and not hits182 and not hits5585, 'scope changed: exact existing receipt transfer now available')
    return {'5572_MOVE_helper_exact_ordered_frame_hits':hits5572,'old182_exact_ordered_frame_hits':hits182,
            '5585_MOVE_helper_exact_ordered_frame_hits':hits5585,
            '5585_evidence_head':'a21a5af71581d678476b882b4b8f27339a2e067d',
            '5585_boundary_match_rule':'descriptor includes exact ordered boundary, complete recipe, actual and expected circuits; no identical boundary candidate exists',
            'rank_zero_main_adapter_reuse_excluded_by_rank':True,
            'scope':'Only these exact receipt sets; no universal absence or old224-count transfer.'}


def compare(actual, literal, C, V, D, charged_rank):
    signed = V.tableau(literal)
    independent = rank([x for x,z,p in signed[9:]])
    need(independent == charged_rank == 4, 'independent literal B-block and charged rank')
    need(V.tableau(actual) == signed, 'all eighteen exact signed Pauli images')
    need(sum(g[0] == 'C' for g in actual) == charged_rank and
         all(g[2] == 1 for g in actual if g[0] == 'C'), 'positive canonical Gaussian child')
    left, right = D.compile_circuit(actual), D.compile_circuit(literal)
    digest = hashlib.sha256()
    for column in range(512):
        a,b = D.dense_column(left,column),D.dense_column(right,column)
        need(a == b, 'exact absolute-phase matrix column '+str(column))
        real,imag,denominator = a
        need(sum(x*x for x in real)+sum(x*x for x in imag) == 1 << (2*denominator), 'unit column norm')
        need(sum(bool(x or y) for x,y in zip(real,imag)) == 1 << charged_rank, 'measured Gaussian support rank')
        digest.update(json.dumps([column,denominator,real,imag],separators=(',',':')).encode())
        digest.update(b'\n')
    return {'columns':512,'complex_entries':512*512,'matrix_sha256':digest.hexdigest(),
            'signed_Pauli_images':signed,'independent_B_block_rank':independent,
            'each_column_support':1 << charged_rank,'each_column_squared_norm':1}


def reject(name, work, expected):
    try:
        work()
    except ValueError as error:
        need(expected in str(error), 'unexpected rejecting predicate '+name+': '+str(error))
        return str(error)
    raise ValueError('mutation accepted: '+name)


def main():
    manifest,gate = authenticate()
    word = read('WORD5580.json.gz')
    occurrences = target_contract(word)
    previous = existing_receipt_check(word)
    C = load(S/'compiler.py','p5580_native_compiler')
    V = load(S/'literal.py','p5580_literal_definitions')
    D = load(S/'dense.py','p5580_credited_dense_engine')
    operation = C.canonical_frame(9,tuple(word['frames'][3])).adjoint().then(C.canonical_frame(9,tuple(word['frames'][737])))
    recipe,_ = C.lower_child(operation)
    need(recipe['rank'] == 4 and recipe['right'] is not None, 'actual source-compiled rank-four recipe')
    actual = V.recipe(recipe)
    literal = V.adjoint(V.frame(word['frames'][3],9))+V.frame(word['frames'][737],9)
    checked = compare(actual,literal,C,V,D,4)
    phased = actual+(('phase',1),)
    need(V.tableau(phased) == V.tableau(actual), 'phase-only fault is invisible to signed tableau')
    phase_column = D.first_difference(phased,literal)
    flipped = list(actual)
    at = next(i for i,g in enumerate(flipped) if g[0] == 'C')
    flipped[at] = ('C',flipped[at][1],-flipped[at][2])
    sign_column = D.first_difference(tuple(flipped),literal)
    boundary_column = D.first_difference(actual+(('X',1),),literal)
    orientation_column = D.first_difference(actual,V.adjoint(literal))
    bad_word = deepcopy(word)
    bad_word['program'][12658][3] = 3
    omitted = reject('paid occurrence',lambda:target_contract(bad_word),'all actual paid occurrences')
    rank_fault = reject('rank',lambda:compare(actual,literal,C,V,D,3),'independent literal B-block and charged rank')
    compiler_fault = reject('compiler corruption',lambda:authenticate_bytes((S/'compiler.py').read_bytes()+b'\n',COMPILER),'source authentication')
    literal_fault = reject('literal corruption',lambda:authenticate_bytes((S/'literal.py').read_bytes()+b'\n',LITERAL),'source authentication')
    result = {'status':'PASS_PR5580_SINGLE_NATIVE_PAIR', 'reviewed_head':HEAD,'target_pair':[3,737],
              'ordered_frame_bytes':[word['frames'][3],word['frames'][737]],'rank':4,
              'paid_occurrences':occurrences,'public_occurrences':1,'private_occurrences':0,
              'actual_source_recipe':recipe,'actual_gate_count':len(actual),'literal_gate_count':len(literal),
              'native_result':checked,'existing_receipt_lookup':previous,
              'controls':{'global_phase':{'first_rejected_column':phase_column,'signed_tableau_unchanged':True},
                'wrong_child_sign':{'first_rejected_column':sign_column},
                'wrong_boundary_correction':{'first_rejected_column':boundary_column},
                'reverse_orientation':{'first_rejected_column':orientation_column},
                'wrong_rank':rank_fault,'omitted_paid_occurrence':omitted,
                'compiler_source_corruption':compiler_fault,'literal_source_corruption':literal_fault},
              'source_gate_observed_utc':gate['observed_utc'],
              'source_hashes':{r['file']:r['sha256'] for r in manifest['files']},
              'positive_width_implication':'Factorwise tensor substitution only, conditional on retained native implementation and monomial cost conventions.',
              'complete_raw_dual_checked':False,'actual_dual_boundary':'This is one forward paid MOVE. Its reversed-orientation fault control is not a whole-caller raw inverse transpose.',
              'all_input_local_743row_ABI_checked':False,'full_caller_checked':False,'full_native_universe_checked':False,
              'parent_autonomy_and_owned_erasure_inherited':True,'precision_tape_storage_admitted':False,
              'compiler_outer_admitted':False,'new_kappa':None,'selected_kappa_unchanged':'.003027288235'}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
