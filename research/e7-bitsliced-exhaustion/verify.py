"""Check exact bit-lane exhaustion. Ali Romman with OpenAI Codex. Apache-2.0."""
import ast
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
from runpy import run_path

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    prefix = 'research/e7-bitsliced-exhaustion/'
    for row in sources['files']:
        if row['usage'] == 'input':
            need(row['path'].startswith(prefix), 'source path outside package')
            file = HERE / row['path'][len(prefix):]
            need(sha256(file.read_bytes()).hexdigest() == row['sha256'],
                 'source hash mismatch: ' + row['path'])


def unchanged_consumer():
    old = ast.parse((HERE / 'source/verify.py').read_text())
    new = ast.parse((HERE / 'classify.py').read_text())
    need(len(old.body) == len(new.body), 'consumer statement inventory')
    changed = []
    for left, right in zip(old.body, new.body):
        if ast.dump(left) == ast.dump(right):
            continue
        if isinstance(left, ast.Assign):
            need(isinstance(right, ast.Assign)
                 and [ast.dump(x) for x in left.targets] == [ast.dump(x) for x in right.targets]
                 == [ast.dump(ast.Name(id='HERE', ctx=ast.Store()))], 'only source root may change')
            changed.append('HERE')
        else:
            need(isinstance(left, ast.FunctionDef) and isinstance(right, ast.FunctionDef)
                 and left.name == right.name == 'minimum_supports', 'downstream check changed')
            changed.append(left.name)
    need(changed == ['HERE', 'minimum_supports'], 'exact derivative boundary')


def literal_words(rows):
    words = [0]
    for row in rows:
        words += [word ^ row for word in words]
    return words


def small_codes(engine):
    digest = sha256()
    codes = comparisons = 0
    for dimension in range(5):
        for rows in combinations(range(1, 16), dimension):
            full = literal_words(rows)
            if len(set(full)) != len(full):
                continue
            codes += 1
            for maximum in range(5):
                expected = sorted(word for word in full if word.bit_count() <= maximum)
                for batch in range(1, 6):
                    actual = sorted(engine(rows, 4, maximum, batch))
                    need(actual == expected, 'complete four-coordinate code domain')
                    digest.update(json.dumps([rows, maximum, batch, actual]).encode())
                    comparisons += 1
    need(codes == 1381 and comparisons == 34525, 'small-code coverage')
    return dict(independent_generator_sets=codes, comparisons=comparisons,
                sha256=digest.hexdigest())


def wide_codes(engine):
    rng = Random(20261026)
    comparisons = 0
    for width in (0, 1, 7, 31, 63, 64, 65, 127):
        dimension = min(10, width)
        rows = tuple((rng.getrandbits(width - dimension) << dimension) | (1 << i)
                     for i in range(dimension))
        full = literal_words(rows)
        for maximum in sorted({0, width // 3, width // 2, width}):
            expected = sorted(word for word in full if word.bit_count() <= maximum)
            for batch in (1, 3, 7, 16):
                need(sorted(engine(rows, width, maximum, batch)) == expected,
                     'word-width or batch boundary')
                comparisons += 1
    return comparisons


def reject(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError('invalid input accepted')


def controls(engine):
    cases = [([1], -1, 0, 1), ([1], True, 0, 1), ([1], 1, -1, 1),
             ([1], 1, True, 1), ([1], 1, 2, 1), ([True], 1, 1, 1),
             ([-1], 1, 1, 1), ([2], 1, 1, 1), ([0], 1, 1, 1),
             ([1, 2, 3], 2, 1, 1), ([1], 1, 1, 0),
             ([1], 1, 1, 21), ([1], 1, 1, True)]
    for args in cases:
        reject(lambda args=args: list(engine(*args)))
    need(set(engine([1, 2], 3, 1)) == {0, 1, 2}, 'known initial code')
    need(set(engine([1, 4], 3, 1)) == {0, 1, 4}, 'changed generator is not cached')
    need(set(engine([1, 2], 3, 0)) == {0}, 'changed bound is not cached')
    need(set(engine([1, 2], 3, 2)) == {0, 1, 2, 3}, 'full weight bound')
    return len(cases) + 3


def check():
    authenticate()
    unchanged_consumer()
    functions = run_path(str(HERE / 'binary.py'))
    engine = functions['low_weight_words']
    small = small_codes(engine)
    wide = wide_codes(engine)
    rejected = controls(engine)
    current = run_path(str(HERE / 'classify.py'))
    result = current['check']()
    need(result == json.loads((HERE / 'source/RESULT.json').read_text()),
         'complete predecessor scientific result')
    geometry = current['geometry']()
    roots = geometry['intrinsic_e7']()
    frames = geometry['orthogonal_frames'](roots)
    basis, _ = geometry['binary_kernel'](tuple(sum(1 << j for j in row) for row in frames))
    reference = current['minimum_supports'](basis)
    changed = list(reversed(basis))
    changed[0] ^= changed[1]
    need(current['minimum_supports'](changed) == reference, 'full E7 basis change')
    return dict(status='PASS_E7_BITSLICED_EXHAUSTION', small_codes=small,
                wide_comparisons=wide, malformed_and_invalidation_controls=rejected,
                all_nonzero_E7_words=(1 << 27) - 1, minimum_supports=len(reference),
                supports_sha256=sha256(json.dumps(sorted(reference)).encode()).hexdigest(),
                source_result=result, derivative_changes=['HERE', 'minimum_supports'])


if __name__ == '__main__':
    result = check()
    need(result == json.loads((HERE / 'RESULT.json').read_text()), 'fixed result receipt')
    print(json.dumps(result, indent=2, sort_keys=True))
