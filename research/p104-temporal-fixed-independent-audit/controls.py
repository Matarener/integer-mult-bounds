#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""IMPLEMENTED, UNRUN: explicit in-memory controls for the fixed portable audit.

Every control result is SYNTHETIC_CONTROL_ONLY. Original source files are never
written. The original fixed input must pass authenticated normal verification
before any derivative is made. Raw verifier bytes are authenticated and compiled;
no import of verify.py or its cached bytecode occurs. No assert-based acceptance.
"""
import contextlib
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import time
import types

HERE = Path(__file__).resolve().parent
LABEL = 'SYNTHETIC_CONTROL_ONLY'
VERIFY_SHA256 = 'bce6cdf82cb1492d209c241670df894548a485b89622a39851f26352f61e999b'
FIXTURES_SHA256 = '494736481a4722b76ca94584df74fec1f58d54d62abe86a4b11ec89da5421c5b'
REFERENCE_SHA256 = '1fe52b928ebd27e61aad9384785d163abe765a98aa6e84b4f6901a0384141e35'
PROJECTION_SHA256 = '8ad201fe2ce3ebcbb0a081774790fd4511d3ecce1b5b5c1cee3dd9bde033895c'
PASS_STATUS = 'PASS_FIXED_CAUSAL_LEDGER_AND_TYPED_CONTACTS_ONLY'
EXCLUDED_PROJECTION_FIELDS = {'binding', 'source', 'elapsed_seconds_internal',
                              'runtime_memory_and_termination_evidence'}
MAX_FILE_BYTES = 1048576
MAX_METADATA_TOTAL = 8388608
CHILD_SECONDS = 60
START = time.monotonic()
METADATA_BYTES = 0
EXPECTED_MUTANT_IDS = ['HIDDEN715_READ', 'CHANGED747_VALUE_WRITE', 'CHANGED747_LIFETIME',
                       'PROSPECTIVE_ONLY_715_CONTACT', 'UNKNOWN_SEMANTICS',
                       'NONBLOCKING11202_WRITE', 'MINIMAL340_INTERVAL_WRITE']


class ControlFailure(Exception):
    def __init__(self, check, detail=None):
        self.check, self.detail = check, detail


class ControlsIncomplete(Exception):
    pass


def require(ok, check, detail=None):
    if not ok:
        raise ControlFailure(check, detail)


def deadline():
    if time.monotonic() - START >= CHILD_SECONDS:
        raise ControlsIncomplete('Control phase deadline; no retries or incomplete pass')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_pinned(path, expected):
    global METADATA_BYTES
    with path.open('rb') as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    require(len(raw) <= MAX_FILE_BYTES, 'CONTROL_METADATA_FILE_CAP', path.name)
    METADATA_BYTES += len(raw)
    require(METADATA_BYTES <= MAX_METADATA_TOTAL, 'CONTROL_METADATA_TOTAL_CAP')
    require(sha(raw) == expected, 'CONTROL_METADATA_SHA256', path.name)
    return raw


def unique_pairs(items):
    out = {}
    for key, value in items:
        require(key not in out, 'ENVELOPE_DUPLICATE_KEY')
        out[key] = value
    return out


def output_preflight(text):
    """Before JSON allocation: source-sized caps, permitting finite elapsed floats.

    The scientific verifier's integer-only input preflight is unchanged. This
    separate envelope lexer handles its bounded runtime presentation fields.
    """
    require(type(text) is str and len(text.encode('utf-8')) <= MAX_FILE_BYTES,
            'ENVELOPE_BYTE_CAP')
    n, i, depth, nodes = len(text), 0, 0, 0
    while i < n:
        if i % 16384 == 0:
            deadline()
        ch = text[i]
        if ch.isspace() or ch in ',:':
            i += 1
            continue
        if ch in ']}':
            depth -= 1
            require(depth >= 0, 'ENVELOPE_UNBALANCED_JSON')
            i += 1
            continue
        nodes += 1
        require(nodes <= 500000, 'ENVELOPE_NODE_CAP')
        if ch in '[{':
            depth += 1
            require(depth <= 16, 'ENVELOPE_DEPTH_CAP')
            i += 1
        elif ch == '"':
            i += 1
            length = 0
            while i < n and text[i] != '"':
                require(ord(text[i]) >= 32, 'ENVELOPE_STRING_CONTROL')
                if text[i] == '\\':
                    i += 1
                    require(i < n, 'ENVELOPE_INCOMPLETE_ESCAPE')
                    if text[i] == 'u':
                        require(i+4 < n and all(c in '0123456789abcdefABCDEF' for c in text[i+1:i+5]),
                                'ENVELOPE_UNICODE_ESCAPE')
                        i += 4
                    else:
                        require(text[i] in '"\\/bfnrt', 'ENVELOPE_ESCAPE')
                length += 1
                require(length <= 256, 'ENVELOPE_STRING_CAP')
                i += 1
            require(i < n, 'ENVELOPE_UNTERMINATED_STRING')
            i += 1
        elif ch in '-0123456789':
            start = i
            while i < n and text[i] not in ' \t\r\n,]}:':
                i += 1
                require(i-start <= 64, 'ENVELOPE_NUMBER_CAP')
            token = text[start:i]
            require(re.fullmatch(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?', token) is not None,
                    'ENVELOPE_NUMBER_GRAMMAR')
        elif text.startswith('true', i):
            i += 4
        elif text.startswith('false', i):
            i += 5
        elif text.startswith('null', i):
            i += 4
        else:
            raise ControlFailure('ENVELOPE_UNKNOWN_TOKEN')
    require(depth == 0, 'ENVELOPE_UNBALANCED_JSON')


def finite_float(token):
    require(len(token) <= 64, 'ENVELOPE_FLOAT_CAP')
    value = float(token)
    require(math.isfinite(value), 'ENVELOPE_NONFINITE_FLOAT')
    return value


def bounded_integer(token):
    require(len(token.lstrip('-')) <= 24, 'ENVELOPE_INTEGER_CAP')
    return int(token)


def reject_constant(token):
    raise ControlFailure('ENVELOPE_NONFINITE_CONSTANT', token)


def decode_output(text):
    output_preflight(text)
    return json.loads(text, object_pairs_hook=unique_pairs, parse_float=finite_float,
                      parse_int=bounded_integer, parse_constant=reject_constant)


def projection(receipt):
    return {key: value for key, value in receipt.items() if key not in EXCLUDED_PROJECTION_FIELDS}


def validate_envelope(text, exit_code, expected_status, expected_projection=None):
    envelope = decode_output(text)
    require(type(envelope) is dict and set(envelope) == {'receipt', 'receipt_sha256'}, 'ENVELOPE_SHAPE')
    receipt = envelope['receipt']
    require(type(receipt) is dict and sha(canonical(receipt)) == envelope['receipt_sha256'],
            'RECEIPT_DIGEST_MISMATCH')
    if receipt.get('status') == 'INCOMPLETE' or exit_code == 4:
        raise ControlsIncomplete('Verifier returned incomplete; no control acceptance')
    require(receipt.get('status') == expected_status, 'UNEXPECTED_VERIFIER_STATUS', receipt.get('status'))
    expected_exit = 0 if expected_status == PASS_STATUS else 3
    require(exit_code == expected_exit, 'UNEXPECTED_VERIFIER_EXIT', exit_code)
    if expected_projection is not None:
        require(projection(receipt) == expected_projection, 'FULL_SCIENTIFIC_PROJECTION_MISMATCH')
    return envelope


class CappedCapture(io.StringIO):
    def write(self, text):
        require(self.tell() + len(text) <= MAX_FILE_BYTES, 'CAPTURE_BYTE_CAP')
        return super().write(text)


def invoke_main(module, source_path):
    prior = sys.argv
    buffer = CappedCapture()
    try:
        sys.argv = ['verify.py', str(source_path)]
        with contextlib.redirect_stdout(buffer):
            exit_code = module.main()
    finally:
        sys.argv = prior
    return buffer.getvalue(), exit_code


def load_verifier():
    raw = read_pinned(HERE/'verify.py', VERIFY_SHA256)
    module = types.ModuleType('authenticated_fixed_verifier_under_controls')
    module.__file__ = str(HERE/'verify.py')
    module.__package__ = None
    # Compile exactly authenticated source bytes; never import a cached verify.pyc.
    code = compile(raw, 'authenticated-portable-verify.py', 'exec')
    exec(code, module.__dict__)
    return module


def labelled(test_id, **facts):
    return {'label': LABEL, 'id': test_id, 'control_status': 'PASS', **facts}


def prerequisites(fixture, baseline):
    kind = fixture['prerequisite']
    if kind == 'CUT823_715_FRAME3':
        require(baseline['cuts']['823']['state']['715']['frame'] == 3, 'PREREQ_CUT823')
    elif kind == '747_LIVE_598':
        item = next(x for x in baseline['ledgers'] if x['index'] == 13574)
        require(item['transition']['tracked_frames_before']['747'] == 598
                and baseline['747_read_lifetimes']['13572']['live'] is True, 'PREREQ747')
    elif kind == '715_AND747_LIVE_598_AFTER13578':
        state = baseline['anchors']['13578']['state_after']
        require(state['715']['frame'] == state['747']['frame'] == 598 and state['747']['live'] is True,
                'PREREQ_PROSPECTIVE_ONLY_CONTACT')
    elif kind == '340_FRAME396_AT11202':
        require(baseline['anchors']['11202']['state_before']['340']['frame'] == 396,
                'PREREQ_NONBLOCKING340')
    elif kind == '340_AND525_FRAME396_AFTER14654':
        state = baseline['anchors']['14654']['state_after']
        require(state['340']['frame'] == state['525']['frame'] == 396, 'PREREQ_MINIMAL340')
    else:
        raise ControlFailure('UNKNOWN_FIXTURE_PREREQUISITE')


def event_control(module, original, fixture, baseline):
    deadline()
    prerequisites(fixture, baseline)
    index = fixture['index']
    require(original['program'][index] == fixture['original_expected'], 'FIXTURE_ORIGINAL_EVENT_MISMATCH', index)
    derivative = dict(original)
    derivative['program'] = list(original['program'])
    derivative['program'][index] = list(fixture['replacement'])
    try:
        result = module.Audit(derivative).scan()
    except module.Falsified as error:
        require(fixture['expected_kind'] == 'fixed_premise', 'WRONG_CONTROL_EXCEPTION_KIND')
        require(error.predicate == fixture['expected_predicate'] and error.index == index,
                'WRONG_FIXED_PREDICATE_OR_SITE', {'predicate':error.predicate,'index':error.index})
        if 'expected_frame' in fixture:
            require(error.expected == fixture['expected_frame'] and error.actual == fixture['expected_actual'],
                    'PROSPECTIVE_CONTROL_DID_NOT_REACH_EXPECTED_STATE')
        return labelled(fixture['id'], data_derivative=True, event_index=index,
                        expected_predicate=error.predicate, actual_outcome='FIXED_SUFFICIENT_PREMISE_NOT_ESTABLISHED',
                        intended_gate_reached=True, no_identity_counterexample_claim=True)
    except module.Unresolved as error:
        require(fixture['expected_kind'] == 'unresolved', 'UNEXPECTED_BINDING_FAILURE', error.reason)
        require(error.reason == fixture['expected_reason'] and error.index == index,
                'WRONG_UNRESOLVED_REASON_OR_SITE')
        return labelled(fixture['id'], data_derivative=True, event_index=index,
                        actual_outcome='BINDING_UNRESOLVED', scientific_falsifier=False)
    except module.Incomplete as error:
        raise ControlsIncomplete(str(error))
    require(fixture['expected_kind'] == 'pass' and fixture['id'] == 'NONBLOCKING11202_WRITE',
            'UNEXPECTED_MUTANT_ACCEPTANCE')
    require(result.get('status') == PASS_STATUS and result['coverage']['complete_program_scan'] is True,
            'NONBLOCKING_CONTROL_NOT_COMPLETE')
    require(result['predicates'] == baseline['predicates'] and all(v == 'PASS' for v in result['predicates'].values()),
            'NONBLOCKING_CONTROL_CHANGED_REQUIRED_PREMISES')
    require(result['anchors']['11202']['event'] == fixture['replacement']
            and result['write_census']['340'] == [11202]
            and result['340_stronger_provenance_observation']['blocking'] is False,
            'NONBLOCKING_CONTROL_NOT_RECORDED_AS_PROVENANCE')
    return labelled(fixture['id'], data_derivative=True, actual_outcome=PASS_STATUS,
                    required_minimal_interval='[14654,14983)', historical_projection_comparison='NOT_APPLICABLE_TO_MUTANT')


class MemoryInput:
    name = 'WORD.json.gz'

    def __init__(self, raw):
        self.raw = raw

    def open(self, mode):
        require(mode == 'rb', 'SYNTHETIC_INPUT_OPEN_MODE')
        return io.BytesIO(self.raw)


def source_mismatch_control(module, source_path, original_raw):
    derivative = bytearray(original_raw)
    derivative[0] ^= 1
    mutated = bytes(derivative)
    authentic = module.authenticate_blob
    decode, gzip_open = module.decode, module.gzip.GzipFile
    counts = {'decode':0,'gzip':0}

    def substituted_input(path, pin):
        if pin == module.SOURCE:
            return authentic(MemoryInput(mutated), pin)
        return authentic(path, pin)

    def forbidden_decode(*args, **kwargs):
        counts['decode'] += 1
        raise ControlFailure('MISMATCH_REACHED_DECODE')

    def forbidden_gzip(*args, **kwargs):
        counts['gzip'] += 1
        raise ControlFailure('MISMATCH_REACHED_GZIP')

    try:
        module.authenticate_blob = substituted_input
        module.decode = forbidden_decode
        module.gzip.GzipFile = forbidden_gzip
        text, exit_code = invoke_main(module, source_path)
    finally:
        module.authenticate_blob = authentic
        module.decode = decode
        module.gzip.GzipFile = gzip_open
    envelope = validate_envelope(text, exit_code, 'BINDING_UNRESOLVED')
    require(envelope['receipt'].get('reason') == 'Pinned input length/SHA256 mismatch: WORD.json.gz',
            'SOURCE_MISMATCH_WRONG_REJECTION')
    require(counts == {'decode':0,'gzip':0}, 'SOURCE_MISMATCH_NOT_PREDECODE')
    return labelled('SOURCE_BYTE_MISMATCH_PREDECODE', data_derivative=True,
                    actual_outcome='BINDING_UNRESOLVED', decoder_calls=counts,
                    synthetic_compressed_sha256=sha(mutated), original_file_written=False)


def envelope_controls(baseline_envelope, expected_projection):
    cases = []
    bad_hash = copy.deepcopy(baseline_envelope)
    bad_hash['receipt_sha256'] = '0'*64
    cases.append(('BAD_ENVELOPE_HASH',bad_hash,'RECEIPT_DIGEST_MISMATCH'))
    bad_status = copy.deepcopy(baseline_envelope)
    bad_status['receipt']['status'] = 'PASS_UNSCOPED'
    bad_status['receipt_sha256'] = sha(canonical(bad_status['receipt']))
    cases.append(('UNSCOPED_PASS_STATUS',bad_status,'UNEXPECTED_VERIFIER_STATUS'))
    missing = copy.deepcopy(baseline_envelope)
    del missing['receipt']['cuts']
    missing['receipt_sha256'] = sha(canonical(missing['receipt']))
    cases.append(('MISSING_SCIENTIFIC_PROJECTION_FIELD',missing,'FULL_SCIENTIFIC_PROJECTION_MISMATCH'))
    out = []
    for test_id, envelope, expected in cases:
        try:
            validate_envelope(canonical(envelope).decode('ascii'), 0, PASS_STATUS, expected_projection)
        except ControlFailure as error:
            require(error.check == expected, 'WRONG_ENVELOPE_CONTROL_REJECTION', error.check)
            out.append(labelled(test_id, data_derivative=False, envelope_derivative=True,
                                intended_validator_rejection=expected))
        else:
            raise ControlFailure('BAD_ENVELOPE_ACCEPTED', test_id)
    return out


def run():
    require(len(sys.argv) == 2, 'EXACTLY_ONE_FIXED_SOURCE_DATA_PATH_REQUIRED')
    source_path = Path(sys.argv[1])
    require(source_path.name == 'WORD.json.gz', 'EXACT_SOURCE_BASENAME_REQUIRED')
    module = load_verifier()
    fixture_raw = read_pinned(HERE/'CONTROL-FIXTURES.json', FIXTURES_SHA256)
    reference_raw = read_pinned(HERE/'evidence/SCIENTIFIC-RECEIPT-EXTRACT.json', REFERENCE_SHA256)
    fixtures, reference = module.decode(fixture_raw), module.decode(reference_raw)
    require(fixtures['schema'] == 'portable5713-explicit-synthetic-control-fixtures/v2'
            and fixtures['label'] == LABEL and fixtures['verifier_sha256'] == VERIFY_SHA256,
            'FIXTURE_HEADER_MISMATCH')
    require([f['id'] for f in fixtures['event_mutants']] == EXPECTED_MUTANT_IDS, 'FIXTURE_SET_MISMATCH')
    expected_projection = reference['scientific_data']
    require(sha(canonical(expected_projection)) == PROJECTION_SHA256, 'REFERENCE_FULL_PROJECTION_HASH')
    captured = {}
    authentic_decode = module.decode

    def capture_original(raw):
        word = authentic_decode(raw)
        require(not captured, 'MULTIPLE_ORIGINAL_WORD_DECODES')
        captured['word'] = word
        return word

    try:
        module.decode = capture_original
        text, exit_code = invoke_main(module, source_path)
    finally:
        module.decode = authentic_decode
    baseline_envelope = validate_envelope(text, exit_code, PASS_STATUS, expected_projection)
    baseline = baseline_envelope['receipt']
    require(baseline['binding']['checker_sha256'] == VERIFY_SHA256 and set(captured) == {'word'},
            'BASELINE_AUTHENTICATED_CODE_OR_CAPTURE_MISSING')
    # Normal run authenticated all original bytes before capture; no derivative
    # was constructed earlier. Authenticate compressed bytes again for byte test.
    original = captured['word']
    original_digest = sha(canonical(original))
    original_raw = module.authenticate_blob(source_path, module.SOURCE)
    results = [labelled('ORIGINAL_BASELINE_ENVELOPE_AND_FULL_PROJECTION', data_derivative=False,
                        context='Original fixed input reference inside synthetic-control harness',
                        actual_outcome=PASS_STATUS, full_scientific_projection_sha256=PROJECTION_SHA256)]
    results.append(source_mismatch_control(module, source_path, original_raw))
    for fixture in fixtures['event_mutants']:
        deadline()
        results.append(event_control(module, original, fixture, baseline))
    results.extend(envelope_controls(baseline_envelope, expected_projection))
    require(len(results) == 12, 'INCOMPLETE_CONTROL_SET')
    require(sha(canonical(original)) == original_digest and sha(original_raw) == module.SOURCE['sha256'],
            'ORIGINAL_IN_MEMORY_INPUT_CHANGED')
    deadline()
    return {'status':'PASS_EXPLICIT_PORTABLE_CONTROL_SET_ONLY','label':LABEL,
            'controls':results,'control_count':len(results),'verifier_sha256':VERIFY_SHA256,
            'fixtures_sha256':FIXTURES_SHA256,'reference_sha256':REFERENCE_SHA256,
            'full_scientific_projection_sha256':PROJECTION_SHA256,
            'source':module.SOURCE,'original_source_authenticated_before_derivatives':True,
            'original_file_written':False,'original_in_memory_data_unchanged':True,
            'raw_verifier_compiled_without_cached_pyc':True,'assert_acceptance_used':False,
            'no_actual_source_counterexample_or_new_kappa':True}


def main():
    try:
        result = run()
        code = 0
    except (ControlsIncomplete, MemoryError, TimeoutError, KeyboardInterrupt) as error:
        result = {'status':'INCOMPLETE','label':LABEL,'control_set_complete':False,
                  'reason':type(error).__name__+': resource/interruption; no acceptance'}
        code = 4
    except ControlFailure as error:
        result = {'status':'CONTROL_FAILURE','label':LABEL,'control_set_complete':False,
                  'check':error.check,'detail':error.detail}
        code = 2
    except Exception as error:
        result = {'status':'BINDING_UNRESOLVED','label':LABEL,'control_set_complete':False,
                  'reason':type(error).__name__+': control input/runtime failure; private paths omitted'}
        code = 3
    result['elapsed_seconds_internal'] = time.monotonic()-START
    try:
        body = canonical(result)
        if len(body)+256 > MAX_FILE_BYTES:
            result = {'status':'BINDING_UNRESOLVED','label':LABEL,'reason':'CONTROL_RECEIPT_CAP',
                      'control_set_complete':False}
            body = canonical(result)
            code = 3
        envelope = canonical({'receipt':result,'receipt_sha256':sha(body)})
    except MemoryError:
        result = {'status':'INCOMPLETE','label':LABEL,'reason':'Control receipt allocation failed',
                  'control_set_complete':False}
        body = canonical(result)
        envelope = canonical({'receipt':result,'receipt_sha256':sha(body)})
        code = 4
    print(envelope.decode('ascii'))
    return code


if __name__ == '__main__':
    sys.exit(main())
