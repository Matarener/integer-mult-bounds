"""Qualify each frozen arithmetic backend once; compare all retained outputs.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
Arithmetic and every scientific oracle remain Ali Romman's unchanged sources.
"""
import gzip
import importlib.util
import json
import time

from source import baseline, require, sha256
from observe import Observation


def qualify():
    started = time.perf_counter()
    with baseline() as package:
        spec = importlib.util.spec_from_file_location('single_pass_source', package/'verify.py')
        v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v)
        with v.source() as (p, original, reference):
            word = json.loads(gzip.decompress((p/'inputs/WORD.json.gz').read_bytes()))
            expected = json.loads((p/'RESULT.json').read_bytes())
            contract = v.load('explicit_contract', package/'contract.py')
            integer = v.load('integer_backend', package/'integer.py')
            engine = integer.Engine(reference)
            candidate = Observation(engine, reference.digest, word)
            captures = []
            factory = original.module

            def observed_module(name, path):
                value = factory(name, path)
                if name == 'noisy_precision':
                    require(path == p/'precision.py' and not captures, 'one authenticated Fraction module')
                    value = Observation(value, reference.digest, word)
                    captures.append(value)
                return value

            try:
                result = contract.calculate(p, candidate)
                require(result == expected, 'complete candidate source result and controls')
                candidate.finish()
                original.module = observed_module
                fraction = original.calculate()
                require(fraction == expected and result == fraction, 'complete independent Fraction/candidate result')
                require(len(captures) == 1, 'one complete independent Fraction observation')
                captures[0].finish()
            except BaseException:
                candidate.abort()
                for capture in captures:
                    capture.abort()
                raise
            finally:
                original.module = factory
            a, b = captures[0].take(word), candidate.take(word)
            require(a['ideal'] == b['ideal'], 'full independent ideal metadata and local weights')
            require(a['error_trace'] == b['error_trace'], 'all actual trace and signed witness rows')
            ideal, weights = a['ideal']
            receipt = dict(source_result_sha256=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                           events=result['ideal']['events'],coordinates=result['ideal']['n'],
                           source_controls=len(result['rejected_controls']),guards=result['sufficient_guard_bits'])
            receipt['finite_fixtures'] = v.fixtures(reference, engine, integer)
            receipt['coefficient_scale_bits'] = integer.setup(word, weights)[2].bit_length()-1
            receipt['all_actual_witness_rows_equal'] = True
        require(receipt == json.loads((package/'RESULT.json').read_bytes()), 'complete frozen qualification receipt')
    return receipt, time.perf_counter()-started


def main():
    # Qualification entry point includes the new finite observation controls.
    import runpy
    runpy.run_path(str(__import__('pathlib').Path(__file__).with_name('finite.py')),run_name='__main__')
    receipt, seconds = qualify()
    print('PASS_P104_SINGLE_PASS_QUALIFICATION')
    print(json.dumps({'mode':'qualify','receipt':receipt,'seconds':round(seconds,6)},sort_keys=True))


if __name__ == '__main__':
    main()
