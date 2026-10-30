"""Bind the three pooled native providers to an exact free-word and recipe proof.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
The free-word result is PR4184 (ToikY with Codex assistance), following
Cinna Davis's PR4100/PR4088 and the credited retained free-algebra engines.
This checker supplies source equality and exact native recipe substitution;
the unbounded tensor argument is written in NATIVE-ADMISSION.md.
"""
from pathlib import Path, PurePosixPath
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
import argparse
import ast
import contextlib
import copy
import gzip
import hashlib
import io
import json
import sys
import tarfile
import tempfile
import types

HERE = Path(__file__).resolve().parent
PROVIDERS = {'gauge44': 'THREE-base', 'extra': 'THREE-extra', 'extra-four': 'FOUR-extra'}
NATIVE_FILES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
                'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def recipe_bytes(record):
    # Frame/port/operator metadata is checked at the source binding. The exact
    # operator certificate is deduplicated only on its mathematical content.
    return packed({key: record[key] for key in ('rank', 'left', 'right')})


def load_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate_file(path, digest):
    require(not path.is_symlink(), 'source symlink: ' + str(path))
    raw = path.read_bytes()
    require(sha(raw) == digest, 'source digest mismatch: ' + str(path))
    return raw


def unpack(raw, inventory, root):
    """Authenticate complete regular-file inventory before private extraction."""
    seen = set()
    contents = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:*') as archive:
        for member in archive.getmembers():
            name = member.name
            p = PurePosixPath(name)
            require(member.isfile() and not p.is_absolute() and '..' not in p.parts,
                    'unsafe archive member: ' + name)
            require(name not in seen and name in inventory, 'unexpected archive member: ' + name)
            seen.add(name)
            data = archive.extractfile(member).read()
            row = inventory[name]
            require(len(data) == row['bytes'] and sha(data) == row['sha256'],
                    'archive member changed: ' + name)
            if 'git_blob' in row:
                require(blob(data) == row['git_blob'], 'archive Git blob changed: ' + name)
            contents[name] = data
    require(seen == set(inventory), 'incomplete archive inventory')
    for name, data in contents.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return contents


def module_from(path, name):
    """Always retain source assertions, including under python -O."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        exec(compile(path.read_bytes(), str(path), 'exec', optimize=0), module.__dict__)
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    return module


class Recipes:
    """Decode supplied recipes; never invoke their synthesis routine."""
    def __init__(self, source):
        self.m = module_from(source, '_pooled_native_exact_clifford')
        self.checked = Counter()

    @lru_cache(None)
    def frame(self, vectors):
        return self.m.canonical_frame(9, vectors)

    @lru_cache(None)
    def amplitude(self, circuit):
        # Equal Pauli conjugation implies equality up to a scalar. A single
        # exact nonzero amplitude of U|0> fixes that scalar, including phase.
        vec, den = self.m.Op(9, self.m.identity(9), list(circuit)).zero_state()
        for index, (real, imag) in enumerate(vec):
            if real or imag:
                while den and not (real & 1) and not (imag & 1):
                    real //= 2
                    imag //= 2
                    den -= 1
                return index, real, imag, den
        raise ValueError('zero column of a Clifford operator')

    def equal(self, left, right):
        return (left.tab == right.tab and
                self.amplitude(tuple(left.circuit)) == self.amplitude(tuple(right.circuit)))

    @lru_cache(None)
    def decode_bytes(self, raw):
        record = json.loads(raw)
        require(set(record) == {'quadratic_rows', 'linear_Z4', 'matrix_rows', 'offset', 'phase'},
                'malformed monomial fields')
        require(all(len(record[k]) == 9 for k in ('quadratic_rows', 'linear_Z4', 'matrix_rows')),
                'monomial dimension')
        require(0 <= record['offset'] < 512 and record['phase'] in range(4), 'monomial scalar range')
        m = self.m
        return (m.diag(9, tuple(record['quadratic_rows']), tuple(record['linear_Z4']))
                .then(m.perm(9, tuple(record['matrix_rows'])))
                .then(m.xgate(9, record['offset']))
                .then(m.Op(9, m.identity(9), [('phase', record['phase'])])))

    def decode(self, record):
        return self.decode_bytes(packed(record))

    @lru_cache(None)
    def k(self, columns):
        m = self.m
        rows = m.transpose(columns, 9)
        inverse = m.inv(rows, 9)
        it = m.transpose(inverse, 9)
        quadratic = tuple((1 << i) ^ sum(m.parity(a & b) << j for j, b in enumerate(it))
                          for i, a in enumerate(it))
        return m.perm(9, rows).then(m.diag(9, quadratic))

    @lru_cache(None)
    def child(self, old, new, raw):
        record = json.loads(raw)
        rank = abs(len(new) - len(old))
        require(record['rank'] == rank and rank > 0, 'child rank mismatch')
        target = self.frame(old).adjoint().then(self.frame(new))
        actual = (self.decode(record['right']).then(self.m.fourier(9, range(rank)))
                  .then(self.decode(record['left'])))
        require(self.equal(actual, target), 'exact child recipe mismatch')
        self.checked['children'] += 1
        return True

    @lru_cache(None)
    def endpoint(self, q, vectors, role, raw):
        record = json.loads(raw)
        require(record['rank'] == 0 and record['right'] is None, 'endpoint is not monomial')
        old = self.m.cgate(9, q)
        if role == 'target':
            old = old.adjoint().then(self.m.fourier(9))
        else:
            require(role == 'source', 'unknown endpoint role')
        target = old.adjoint().then(self.frame(vectors))
        require(self.equal(self.decode(record['left']), target), 'exact endpoint recipe mismatch')
        self.checked['endpoint_adapters'] += 1
        return True

    @lru_cache(None)
    def warp(self, sign, columns, old, new, raw):
        record = json.loads(raw)
        require(record['rank'] == 0 and record['right'] is None, 'warp is not monomial')
        k = self.k(columns)
        k = k if sign == 1 else k.adjoint()
        target = self.frame(old).adjoint().then(k).then(self.frame(new))
        require(self.equal(self.decode(record['left']), target), 'exact warp recipe mismatch')
        self.checked['warp_recipes'] += 1
        return sha(raw)

    @lru_cache(None)
    def residual(self, entrance, terminal, raw):
        record = json.loads(raw)
        width = len(terminal) - len(entrance)
        require(record['rank'] == width > 0, 'residual width mismatch')
        residual = self.frame(entrance).adjoint().then(self.frame(terminal))
        actual = (self.decode(record['right']).adjoint().then(residual)
                  .then(self.decode(record['left']).adjoint()))
        require(self.equal(actual, self.m.fourier(9, range(width))), 'exact residual wrapper mismatch')
        self.checked['residual_pairs'] += 1
        return True

    @lru_cache(None)
    def warp_generator(self, columns, raw):
        require(self.equal(self.decode(json.loads(raw)), self.k(columns)), 'warp generator recipe mismatch')
        self.checked['warp_generator_recipes'] += 1
        return True


def replay_environment(source, canonical, recipes, checker):
    # Preserve these four original function definitions verbatim as AST nodes.
    # The omitted module plumbing loads NumPy and runs a separate 512-column
    # matrix engine. Here each warp callback calls the separately exact recipe
    # certificate above, including global phase. No algebraic rule is replaced.
    wanted = {'contains', 'add_row', 'warp_row', 'local'}
    tree = ast.parse(source.read_bytes())
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    require({node.name for node in definitions} == wanted, 'original local function inventory')
    v, R = canonical['v'], canonical['R']
    n = 2 * v + R
    entering = [r for r, f in enumerate(canonical['start']) if r >= 2 * v and f != 0]
    hpe = {r for r in range(2 * v, n) if canonical['final'][r] != 1}
    wrapped = sorted(set(entering) | hpe)
    warp_table = {(r['sign'], r['op'], r['old'], r['new']): r for r in recipes['warps']}

    def warp_columns(op, f0, f1, columns, qmut=None):
        require(qmut is None, 'unexpected warp mutation')
        record = warp_table[(1 if op > 0 else -1, abs(op), f0, f1)]
        require(record['G_columns'] == columns, 'warp callback columns mismatch')
        return checker.warp(1 if op > 0 else -1, tuple(columns), tuple(canonical['frames'][f0]),
                            tuple(canonical['frames'][f1]), recipe_bytes(record))

    env = dict(c=canonical, v=v, R=R, h=canonical['h'], n=n, frames=canonical['frames'],
               levels={int(t): f for t, f in canonical.get('target_levels', {}).items()},
               entering=entering, hpe=hpe, wrapped=wrapped, plain=set(range(n)) - set(wrapped),
               zb=canonical.get('zero_buffers', []), Q=Q, Counter=Counter,
               hashlib=hashlib, json=json, warp_columns=warp_columns)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(source), 'exec', optimize=0), env)
    return env


def check_provider(canonical, programs, recipes, residuals, checker, source):
    c = canonical
    require((c['v'], c['R'], c['h']) == (112, 408, 9), 'native provider dimensions')
    require(set(programs) == {'forward', 'backward'}, 'both native orientations required')
    frames = c['frames']
    edges = set(map(tuple, c['edges'])) | {(a, b) for f in c['center_frames'] for a, b in ((f, 0), (0, f))}
    child_records = {(r['old'], r['new']): r for r in recipes['children']}
    require(len(child_records) == len(recipes['children']) and set(child_records) == edges,
            'complete child recipe inventory')
    for (old, new), r in child_records.items():
        checker.child(tuple(frames[old]), tuple(frames[new]), recipe_bytes(r))
    adapters = {(r['port'], r['role']): r for r in recipes['endpoint_adapters']}
    require(len(adapters) == len(recipes['endpoint_adapters']) == 224 and
            set(adapters) == {(i, role) for i in range(112) for role in ('source', 'target')},
            'complete endpoint adapter inventory')
    for (i, role), r in adapters.items():
        f = c['start'][i] if role == 'source' else c['final'][112 + i]
        require(r['frame'] == f, 'endpoint frame mismatch')
        checker.endpoint(c['ports'][i], tuple(frames[f]), role, recipe_bytes(r))
    wrecords = {(r['sign'], r['op'], r['old'], r['new']): r for r in recipes['warps']}
    require(len(wrecords) == len(recipes['warps']) and set(wrecords) == set(map(tuple, c['warp_edges'])),
            'complete warp recipe inventory')
    generator_columns = {r['op']: r['G_columns'] for r in c['warps']}
    for (sign, op, old, new), r in wrecords.items():
        require(r['G_columns'] == generator_columns[op], 'warp recipe generator mismatch')
        checker.warp(sign, tuple(generator_columns[op]), tuple(frames[old]), tuple(frames[new]), recipe_bytes(r))
    expected_residuals = {}
    for r in range(224, 632):
        entrance, terminal = c['start'][r], c['final'][r]
        if terminal != 1:
            expected_residuals['%d:%d' % (entrance, terminal)] = entrance, terminal
        elif entrance != 0:
            expected_residuals[str(entrance)] = entrance, terminal
    require(set(residuals['recipes']) == set(expected_residuals), 'complete residual recipe inventory')
    for key, (entrance, terminal) in expected_residuals.items():
        r = residuals['recipes'][key]
        require(r['frame'] == entrance and r['vectors'] == frames[entrance] and
                r['entrance_rank'] == len(frames[entrance]), 'residual entrance metadata')
        if terminal != 1:
            require(r['terminal'] == terminal and r['terminal_vectors'] == frames[terminal] and
                    r['terminal_rank'] == len(frames[terminal]), 'residual terminal metadata')
        checker.residual(tuple(frames[entrance]), tuple(frames[terminal]), recipe_bytes(r))
    require(set(residuals['warps']) == {str(op) for op in generator_columns}, 'warp generator inventory')
    for op, columns in generator_columns.items():
        r = residuals['warps'][str(op)]
        original = next(w for w in c['warps'] if w['op'] == op)
        require(all(r[k] == original[k] for k in ('op', 'G_columns', 'from_frame', 'to_frame')),
                'residual warp metadata')
        checker.warp_generator(tuple(columns), packed(r['K']))
    env = replay_environment(source, c, recipes, checker)
    local_results = {}
    for name, back in (('forward', False), ('backward', True)):
        profile, result = env['local'](programs[name], back)
        require(dict(profile) == {int(r): count for r, count in c['local_profile'].items()}, 'native paid profile')
        # This callback uses a phase-inclusive exact recipe certificate, not the
        # original NumPy 512-column matrix hash. Name its evidence accurately.
        result.pop('warp_columns_each_exact')
        result['warp_recipe_event_certificate_sha256'] = result.pop('warp_product_sha256')
        result['warp_recipe_equality_method'] = 'all Pauli generators plus exact nonzero zero-column amplitude'
        local_results[name] = result
    reached = set()
    for events in programs.values():
        for e in events:
            if e[0] == 'climb':
                reached.add((e[3], e[4]))
            elif e[0] == 'center':
                reached.add((e[2], e[3]))
    require(reached <= edges, 'uncovered reached native edge')
    return {'persistent_inputs_each_orientation': 632, 'owned_centres': len(c['centers']),
            'owned_zero_buffers': len(c['zero_buffers']), 'frames': len(frames),
            'listed_directed_child_recipes': len(edges), 'reached_directed_child_edges': len(reached),
            'endpoint_adapters': len(adapters), 'listed_warp_recipes': len(wrecords),
            'residual_recipe_pairs': len(expected_residuals), 'local': local_results,
            'child_profile': c['local_profile']}, env


def negative_controls(canonical, programs, recipes, residuals, checker, env):
    rejected = []

    def reject(name, function):
        try:
            function()
        except (AssertionError, ValueError, KeyError):
            rejected.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)

    child = copy.deepcopy(recipes['children'][0])
    child['left']['phase'] = (child['left']['phase'] + 1) % 4
    reject('child_global_phase_invisible_to_tableau', lambda: checker.child(
        tuple(canonical['frames'][child['old']]), tuple(canonical['frames'][child['new']]), packed(child)))
    r = copy.deepcopy(next(iter(residuals['recipes'].values())))
    entrance = tuple(canonical['frames'][r['frame']])
    terminal = tuple(canonical['frames'][r.get('terminal', 1)])
    r['left'], r['right'] = r['right'], r['left']
    reject('residual_wrapper_sides_swapped', lambda: checker.residual(entrance, terminal, packed(r)))
    for name, predicate in (
            ('missing_private_zero_release', lambda e: e[0] == 'zero_buffer' and e[1] == 'free'),
            ('missing_warp_inverse_cleanup', lambda e: e[0] == 'warp' and e[2] < 0 and e[3] == e[4] == 1),
            ('missing_helper_post_wrapper', lambda e: e[0] == 'residual_adapter' and e[1] == 'post')):
        events = copy.deepcopy(programs['forward'])
        events.pop(next(i for i, e in enumerate(events) if predicate(e)))
        reject(name, lambda events=events: env['local'](events, False))
    # The actual pre-wrapper order is a needed boundary premise. Move an actual
    # wrapped-helper scalar read before its pre-wrapper without altering it.
    wrapped = set(env['wrapped'])
    events = copy.deepcopy(programs['forward'])
    index = next(i for i, e in enumerate(events) if e[0] == 'scalar' and e[1][0] in ('add', 'copy') and
                 any(r[0] == 'L' and r[1] in wrapped for r in e[1][1:3]))
    e = events.pop(index)
    helper = next(r[1] for r in e[1][1:3] if r[0] == 'L' and r[1] in wrapped)
    insert = next(i for i, e in enumerate(events) if e[0] == 'residual_adapter' and e[1] == 'pre' and e[2] == helper)
    events.insert(insert, e)
    reject('helper_read_before_pre_wrapper', lambda: env['local'](events, False))
    return rejected


def compute():
    pins = load_json(HERE / 'NATIVE-PINS.json')
    require(pins['provider_map'] == PROVIDERS, 'active provider source map changed')
    manifest_raw = authenticate_file(HERE / pins['source_manifest'], pins['source_manifest_sha256'])
    manifest = json.loads(manifest_raw)
    inventory = {row['path']: row for row in manifest['files']}
    require(len(inventory) == len(manifest['files']) == 29, 'native source closure inventory')
    source_raw = authenticate_file(HERE / pins['source_archive'], pins['source_archive_sha256'])
    prior = HERE.parent.parent / pins['prior_package']
    prior_pins = json.loads(authenticate_file(prior / 'PHYSICAL-PINS.json', pins['prior_inputs']['PHYSICAL-PINS.json']))
    prior_raw = authenticate_file(prior / 'frozen/physical-t74/SOURCE-BUNDLE.tar.gz',
                                 pins['prior_inputs']['frozen/physical-t74/SOURCE-BUNDLE.tar.gz'])
    with tempfile.TemporaryDirectory(prefix='pooled-native-') as temporary:
        root = Path(temporary)
        unpack(source_raw, inventory, root / 'source')
        unpack(prior_raw, prior_pins['bundle']['files'], root / 'prior')
        source = root / 'source'
        independent = module_from(source / 'pr4184/independent.py', '_pooled_native_pr4184')
        formal = independent.compute()
        require(formal == load_json(source / 'pr4184/INDEPENDENT.json'), 'fresh PR4184 pullback receipt differs')
        transport = module_from(source / 'native-source/bw_transport.py', '_pooled_native_transport')
        checker = Recipes(source / 'native-source/vendor/clifford/clifford_exact.py')
        reports = {}
        active = {}
        for provider, export in PROVIDERS.items():
            actual = root / 'prior/native' / provider
            generated = root / 'regenerated' / provider
            with contextlib.redirect_stdout(io.StringIO()):
                transport.run(source / 'pr4184/source/inputs' / (export + '.json.gz'), generated)
            previous_argv, previous_path = sys.argv, sys.path.copy()
            sys.argv = ['bw_emit.py', str(generated)]
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    module_from(source / 'native-source/bw_emit.py', '_pooled_native_emitter')
            finally:
                sys.argv, sys.path[:] = previous_argv, previous_path
            equality = {}
            for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
                require(load_json(generated / name) == load_json(actual / name), 'active native source equality: ' + provider + '/' + name)
                equality[name] = sha(packed(load_json(actual / name)))
            c, programs, recipes, residuals = (load_json(actual / name) for name in NATIVE_FILES)
            result, env = check_provider(c, programs, recipes, residuals, checker, source / 'native-source/bw_audit_local.py')
            result['pr4184_export'] = export
            result['regenerated_scientific_json_sha256'] = equality
            reports[provider] = result
            active[provider] = c, programs, recipes, residuals, env
        controls = negative_controls(*active['extra'][:4], checker, active['extra'][4])
        require(sum(row['outputs'] for rows in formal['providers'].values() for row in rows) == 5784,
                'complete PR4184 coverage')
        return {'schema': 1, 'status': 'PASS_SOURCE_SPECIFIC_NATIVE_ALL_PARAMETER_ADMISSION',
                'source_archive_sha256': pins['source_archive_sha256'],
                'prior_physical_bundle_sha256': sha(prior_raw),
                'pr4184_head': '94b9ca9cf59ea6de346a59c92b414454bdde1de4',
                'reused_formal_pullback': {'output_functionals': 5784, 'endpoint_terms': 6680,
                                         'nonempty_surviving_words': 0, 'providers': 4,
                                         'orientations_each': 2, 'controls': formal['controls']},
                'active_providers': reports, 'unique_exact_recipe_checks': dict(checker.checked),
                'negative_controls_rejected': controls,
                'all_parameter_argument': 'Q[F_72] substitution into unary tensor powers; fixed scalar role coefficients; exact frame/recipe tensor products, including scalar phases',
                'written_proof': 'NATIVE-ADMISSION.md',
                'discharged': ['exact source equality for three pooled native providers and both orientations',
                               'arbitrary dirty persistent inputs and complete private-work cleanup',
                               'phase-inclusive directed child, endpoint, warp and residual recipes',
                               'every positive tensor multiplicity under exact child substitution'],
                'retained_premises': ['exact reversible scalar/monomial/private-work implementation on a common grid',
                                     'inductively correct child supplier on its actual hosted coordinate set',
                                     'whole-call placement, paid hosting/controller/restoration and outer cost proofs'],
                'scope': 'Written all-parameter native algebra proof plus finite complete recipe certificates; no formal-kernel proof or standalone outer/kappa assertion.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = compute()
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.check:
        require(args.check.read_text() == raw, 'native admission receipt differs')
    if args.out:
        require(not args.out.exists(), 'refuse to overwrite evidence')
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(raw)
    print(result['status'])
    print(json.dumps(result['unique_exact_recipe_checks'], sort_keys=True))


if __name__ == '__main__':
    main()
