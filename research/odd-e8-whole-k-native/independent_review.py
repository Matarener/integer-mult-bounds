"""Independent read-only emitted-program audit; no import of core/frame tools.

The generic mathematical proof was separately reviewed in REVIEW.md. This
checker replays every emitted scalar instruction and its original input
column, reconstructs K from pinned original root columns, checks all literal
bills, and verifies the two algebraic phase/rank lemmas in exhaustive small
dimensions. It does not pretend to execute all 2744 physical cube words.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from itertools import product
from hashlib import sha256
import argparse, gzip, importlib.util, json, sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
DEFAULT_PACKAGE = ROOT


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def rank(rows):
    pivots = {}
    for v in rows:
        while v:
            i = v.bit_length() - 1
            if i not in pivots:
                pivots[i] = v
                break
            v ^= pivots[i]
    return len(pivots)


def span(rows):
    ans = {0}
    for v in rows:
        ans |= {x ^ v for x in list(ans)}
    return ans


def mv(rows, x):
    return sum(((r & x).bit_count() & 1) << j for j, r in enumerate(rows))


def transpose(rows, n):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def add_row(dst, src, coefficient):
    for key, value in src.items():
        value = dst.get(key, F(0)) + coefficient * value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def check_program(package, expected_cube=(0, 0, 0), bundle=None):
    compressed = (package / 'K-PROGRAM.json.gz').read_bytes() if bundle is None else bundle[1]
    payload = json.loads(gzip.decompress(compressed))
    raw = (json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n').encode()
    receipt = json.loads((package / 'K-MODULE.json').read_bytes()) if bundle is None else bundle[0]
    template = json.loads((package / 'K-TEMPLATE.json').read_bytes()) if bundle is None else bundle[2]
    need(sha256(raw).hexdigest() == receipt['scientific_program_payload_sha256'], 'payload digest')
    need(payload['cube_tuple'] == list(expected_cube), 'requested emitted cube')
    pins = payload['source_pins']
    for name, expected in pins.items():
        need(digest(package / 'inputs' / name) == expected, 'input pin ' + name)
    normal = json.loads((package / 'inputs/NORMALIZERS.json').read_bytes())
    roots = list(zip(*normal['mode_columns']))
    groups = {}
    for i, row in enumerate(roots):
        groups.setdefault(tuple(j for j, v in enumerate(row) if v), []).append(i)
    cubes = [ports for support, ports in sorted(groups.items())]
    need(len(cubes) == 14 and all(len(c) == 8 for c in cubes), 'original 14 cube partition')
    base_K = []
    for ports in cubes:
        K = [[F(int(i == j)) - F(sum(a * b for a, b in zip(roots[ports[i]], roots[ports[j]])), 4)
              for j in range(8)] for i in range(8)]
        need(all(sum(K[i][j] * K[j][k] for j in range(8)) == int(i == k)
                 for i, k in product(range(8), repeat=2)), 'original base involution')
        base_K.append(K)
    selected_cubes = [cubes[i] for i in expected_cube]
    selected_K = [base_K[i] for i in expected_cube]
    local = list(product(range(8), repeat=3))
    def owner(t):
        return sum(selected_cubes[j][t[j]] * 112 ** (2 - j) for j in range(3))
    ports = [owner(t) for t in local]
    need(ports == payload['port_order'], 'original port identity and order')
    expected_K = {}
    for t in local:
        row = {}
        for u in local:
            value = sum(selected_K[a][t[a]][u[a]] * int(all(t[b] == u[b] for b in range(3) if b != a))
                        for a in range(3)) / 2 - selected_K[0][t[0]][u[0]] * selected_K[1][t[1]][u[1]] * selected_K[2][t[2]][u[2]] / 2
            if value:
                row[owner(u)] = value
        need(Counter(abs(x) for x in row.values()) == {F(1, 4): 12, F(1, 16): 64}, 'direct matrix row')
        need(row == {s: F(a, b) for s, a, b in payload['literal_scalar_K_rows'][str(owner(t))]}, 'all 512 by 512 original K entries')
        expected_K[owner(t)] = row
    definitions = payload['definitions']
    for key, word in definitions.items():
        need(sha256(json.dumps(word, separators=(',', ':')).encode()).hexdigest() == key, 'word content address')
    fields = {(role, p) for role in ('X', 'Y') for p in ports}
    need(len(fields) == 1024, 'distinct original fields')
    rows = {f: {f: F(1)} for f in fields}
    charts = {f: ('line:' + str(f[1]) if f[0] == 'X' else 'ground') for f in fields}
    expected_rows = {f: dict(row) for f, row in rows.items()}
    for r, row in expected_K.items():
        expected_rows['Y', r].update({('X', s): value for s, value in row.items()})
    paid, ordinary, paths = Counter(), Counter(), Counter()
    wrappers = Counter()
    add_pairs = Counter()
    program = payload['program']
    need(len(program) == 2048 + 2048 + 38912, 'literal instruction count')
    def monomial(key):
        word = definitions[key]
        need(all(g[0] in ('P', 'D', 'X', 'phase') for g in word), 'executable ordinary word has no Gaussian')
        ordinary.update(g[0] for g in word)
    for index, instruction in enumerate(program):
        opcode = instruction[0]
        if opcode == 'MONOMIAL':
            _, role, p, key, name = instruction
            need((role, p) in fields, 'wrapper references original field')
            need(key == payload['normalization_wrappers'][str(p)][name_to_wrapper(name)], 'actual wrapper association')
            wrappers[role, p, name] += 1
            need((index < 1024) == name.endswith('entry'), 'entry chronological boundary')
            need((index >= len(program) - 1024) == name.endswith(('exit', 'normalization')), 'output chronological boundary')
            monomial(key)
        elif opcode == 'PAID_PATH':
            _, role, p, old, new, path = instruction
            need((role, p) in fields and charts[role, p] == old, 'actual path old chart')
            need(path['rank'] == len(path['child_axes']) == len(set(path['child_axes'])), 'literal child rank and axes')
            need(all(0 <= a < 25 for a in path['child_axes']), 'actual paid axes range')
            if role == 'X':
                needed = payload['source_paths'][str(p)] if old.startswith('line:') else payload['common_paths'][old[-1]]['source_exit']
            else:
                needed = payload['common_paths'][new[-1]]['reader_entry'] if old == 'ground' else payload['reader_paths'][str(p)]
            need(path == needed, 'per-field exact path record')
            monomial(path['before_monomial'])
            monomial(path['after_monomial'])
            charts[role, p] = new
            paid[path['rank']] += 1
            paths[role, p] += 1
        else:
            need(opcode == 'ADD' and len(instruction) == 8, 'no extra opcode, owned field, COPY or CLEAR')
            _, dr, d, sr, s, a, b, chart = instruction
            need(dr == 'Y' and sr == 'X' and (dr, d) in fields and (sr, s) in fields, 'actual source ownership and no source overwrite')
            need(charts[dr, d] == charts[sr, s] == chart, 'same literal frame for actual ADD')
            need(F(a, b) == expected_K[d][s], 'actual scalar coefficient')
            add_pairs[d, s] += 1
            add_row(rows[dr, d], rows[sr, s], F(a, b))
            ordinary['ADD'] += 1
    need(all(count == 1 for count in add_pairs.values()) and len(add_pairs) == 38912, 'each required ADD exactly once')
    need(rows == expected_rows, 'all 1024 original geometric input columns independently replayed')
    need(all(rows['X', p] == {('X', p): 1} for p in ports), 'every original source retained unchanged')
    need(all(paths[f] == 2 for f in fields), 'two paid paths on each original field')
    for p in ports:
        need(charts['X', p] == 'full25' and charts['Y', p] == 'qperp24:' + str(p), 'geometric endpoint chart')
        for role, name in [('X', 'normalized_virtual_Q_entry'), ('Y', 'real_reader_entry'), ('X', 'autonomous_source_D_exit'), ('Y', 'reader_D_normalization')]:
            need(wrappers[role, p, name] == 1, 'all four original-field wrappers present exactly once')
    need(paid == {8: 512, 9: 512, 15: 512, 16: 512}, 'independent paid bill')
    need(ordinary == {'ADD': 38912, 'P': 7680, 'D': 7680, 'X': 3072, 'phase': 3072}, 'independent literal ordinary bill')
    v = 112 ** 3
    need(template['whole_original_inputs'] == 2 * v and template['whole_paid_profile'] == {str(r): v for r in (8, 9, 15, 16)}, 'whole-family structural paid bill')
    need(template['whole_ordinary_profile'] == {k: v * x for k, x in {'ADD': 76, 'P': 15, 'D': 15, 'X': 6, 'phase': 6}.items()}, 'whole-family structural literal ordinary bill')
    # Coefficient-level normalizer proof covers all addresses: the parity
    # cross terms vanish by orthogonality, not by random address sampling.
    for p in ports:
        rec = payload['entry_frames'][str(p)]
        G = rec['normalizer_proof']['G_rows']
        z = rec['normalizer_proof']['Z_after_permutation']
        need(mv(G, 1) == rec['q25'], 'normalizer actually sends distinguished line to q')
        need(all(((G[i] & G[j]).bit_count() & 1) == int(i == j) for i, j in product(range(25), repeat=2)), 'all normalizer orthogonality coefficients')
        need(all((G[i].bit_count() - 1 - 2 * ((z >> i) & 1)) % 4 == 0 for i in range(25)), 'all weight-congruence linear coefficients')
    # Actual scalar mutation from an emitted opcode changes an independent column.
    removed = next(i for i in program if i[0] == 'ADD')
    bad = dict(rows['Y', removed[2]])
    add_row(bad, rows['X', removed[4]], -F(removed[5], removed[6]))
    need(bad != expected_rows['Y', removed[2]], 'emitted omitted-ADD mutation detected')
    return {'payload_sha256': sha256(raw).hexdigest(), 'cube_tuple': list(expected_cube), 'original_fields': 1024, 'matrix_entries_checked': 512 ** 2,
            'replayed_ADD': 38912, 'paid_profile': dict(sorted(paid.items())), 'ordinary_profile': dict(sorted(ordinary.items())),
            'owned_fields': 0, 'helpers': 0, 'ADD_source_overwrites': 0, 'all_normalizer_coefficient_checks': 512,
            'mutation_omitted_actual_ADD': 'DETECTED', 'whole_family_bill': 'generic-constructor-and-proof; not all phase instances executed'}


def name_to_wrapper(name):
    return {'normalized_virtual_Q_entry': 'input_X', 'real_reader_entry': 'input_Y',
            'autonomous_source_D_exit': 'output_X', 'reader_D_normalization': 'output_Y'}[name]


def small_dimension_lemmas(package):
    spec = importlib.util.spec_from_file_location('independent_canonical_clifford', package / 'inputs/clifford_exact.py')
    ce = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ce
    spec.loader.exec_module(ce)
    anchor_checks = frame_checks = nested_checks = 0
    for n in range(1, 4):
        for G in product(range(1 << n), repeat=n):
            if rank(G) != n:
                continue
            A = ce.inv(G, n)
            Acols = transpose(A, n)
            J = tuple((1 << i) ^ sum(((Acols[i] & Acols[j]).bit_count() & 1) << j for j in range(n)) for i in range(n))
            KG = ce.perm(n, G).then(ce.diag(n, J))
            R = ce.fourier(n)
            actual = R.adjoint().then(KG).then(R)
            d = sum(((col.bit_count() // 2) & 1) << j for j, col in enumerate(Acols))
            target = [(0, 0)] * (1 << n)
            target[d] = [(1, 0), (0, 1), (-1, 0), (0, -1)][(-d.bit_count()) % 4]
            need(actual.zero_state() == (target, 0), 'exhaustive small-dimensional analytic absolute anchor')
            anchor_checks += 1
            cols = transpose(G, n)
            flag_frames = []
            for r in range(n + 1):
                op = KG.adjoint().then(ce.fourier(n, range(r))).then(KG)
                image = span([x | (z << n) for x, z, phase in op.tab[n:]])
                S = span(cols[:r])
                Sperp = {t for t in range(1 << n) if all((t & x).bit_count() % 2 == 0 for x in S)}
                formula = {x | ((x ^ t) << n) for x in S for t in Sperp}
                need(image == formula, 'all small-dimensional L_S equalities including degenerate S')
                frame_checks += 1
                flag_frames.append(op)
            for r in range(n + 1):
                for t in range(r, n + 1):
                    transition = flag_frames[r].adjoint().then(flag_frames[t])
                    need(rank([x for x, z, phase in transition.tab[n:]]) == t - r, 'all small-dimensional nested physical ranks')
                    nested_checks += 1
    return {'all_GL_1_2_3_absolute_anchor_checks': anchor_checks, 'small_L_S_checks': frame_checks,
            'small_nested_rank_checks': nested_checks,
            'interpretation': 'exhaustive corroboration of separately reviewed algebraic forall-n proofs; not a substitute for them'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', type=Path, default=DEFAULT_PACKAGE)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--receipt', type=Path, default=ROOT / 'INDEPENDENT-REVIEW.json')
    args = ap.parse_args()
    backward_spec = importlib.util.spec_from_file_location('independent_backward_word', args.package / 'backward_independent.py')
    backward = importlib.util.module_from_spec(backward_spec)
    backward_spec.loader.exec_module(backward)
    result = {'schema': 'whole-K-independent-program-review/v1', 'status': 'PASS',
              'emitted_program': check_program(args.package), 'generic_lemma_corroboration': small_dimension_lemmas(args.package),
              'backward_relative_word': backward.calculate(args.package),
              'limits': ['No H native construction, F3 source acquisition, outer chronology, mixed-Q E interface, precision or kappa claim.',
                         'Independent scalar replay is on the emitted root cube. Generic mathematical proofs plus prior all-family geometry cover the 2744-cube constructor.',
                         'Original physical x,y are independent; logical replay is in invertible u=LQ^-1x and v=Ly coordinates, connected by explicitly emitted ordinary wrappers.']}
    if args.write:
        args.receipt.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads(args.receipt.read_bytes()) == json.loads(json.dumps(result)), 'frozen independent review receipt')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
