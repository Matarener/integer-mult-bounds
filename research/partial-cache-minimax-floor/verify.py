"""Check the physical kernel norm and the minimax constant with exact arithmetic."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(test, message):
    if not test:
        raise ValueError(message)


def authenticate(data, row):
    require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256')
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git object')


def program(ops, vector):
    out = list(vector)
    for op in ops:
        if op[0] == 'add':
            out[op[1]] += F(op[3]) * out[op[2]]
        elif op[0] == 'scale':
            require(F(op[2]) != 0, 'zero basis scale')
            out[op[1]] *= F(op[2])
        else:
            raise ValueError('unknown basis operation')
    return out


def inverse(ops):
    out = []
    for op in reversed(ops):
        if op[0] == 'add':
            out.append(['add', op[1], op[2], str(-F(op[3]))])
        elif op[0] == 'scale':
            out.append(['scale', op[1], str(1 / F(op[2]))])
        else:
            raise ValueError('unknown inverse operation')
    return out


def norm2(vector):
    return sum(x * x for x in vector)


def monomial_unitary(word):
    """Check the permutation and fourth-root phases on all 512 addresses."""
    images = []
    for start in range(512):
        x, phase = start, 0
        for op in word:
            if op[0] == 'P':
                require(len(op[1]) == 9, 'matrix size')
                require(all(type(r) is int and 0 <= r < 512 for r in op[1]), 'matrix row')
                x = sum(((x & row).bit_count() % 2) << j for j, row in enumerate(op[1]))
            elif op[0] == 'X':
                require(type(op[1]) is int and 0 <= op[1] < 512, 'translation')
                x ^= op[1]
            elif op[0] == 'D':
                require(len(op[1]) == len(op[2]) == 9, 'phase size')
                require(all(type(r) is int and 0 <= r < 512 for r in op[1]), 'phase row')
                require(all(type(r) is int for r in op[2]), 'phase coefficient')
                phase += sum(op[2][j] for j in range(9) if x >> j & 1)
                phase += 2 * sum((op[1][j] & x & ((1 << j) - 1)).bit_count()
                                 for j in range(9) if x >> j & 1)
            elif op[0] == 'phase':
                require(type(op[1]) is int, 'global phase')
                phase += op[1]
            else:
                raise ValueError('nonmonomial gate')
        require(0 <= phase % 4 < 4, 'unit phase')
        images.append(x)
    require(len(set(images)) == 512, 'nonunitary address map')


def target_image(normalizers, raw):
    y = raw[112:224]
    return [sum(F(a) * b for a, b in zip(row, y)) / 2
            for row in normalizers['mode_columns']]


def audit(provider, normalizers, raw):
    require(sum(bool(x) for x in raw) == 104, 'raw support')
    require([norm2(raw[a:b]) for a, b in [(0,112),(112,224),(224,632)]]
            == [60,12,68], 'raw norm blocks')
    decoded = program(provider['output_basis_program'], raw)
    recovered = program(inverse(provider['input_basis_program']), raw)
    require(decoded == recovered, 'independent inverse program')
    require([(i, x) for i, x in enumerate(decoded[224:], 224) if x] == [(225,F(-4))],
            'helper basis image')
    forward = raw[:224] + [F(0)] * 417
    forward[225] = -4
    require(program(provider['input_basis_program'], forward) == raw, 'forward source binding')
    physical = list(decoded)
    for role in provider['mode_owners']:
        physical[role] /= 2
    require([norm2(physical[a:b]) for a,b in [(0,112),(112,224),(224,632)]]
            == [60,12,4], 'physical norm blocks')
    require(norm2(physical) == 76, 'physical input norm')
    require(sum(bool(x) for x in physical) == 61, 'physical support')
    t = target_image(normalizers, raw)
    require(t == [0,-2,0,0,0,0,0,0], 'actual target coefficient')
    independent = [F(row[2] - row[1] - row[12]) for row in normalizers['mode_columns']]
    require(t == independent, 'three-entry target calculation')
    require(norm2(t) / norm2(physical) == F(1,19), 'minimax squared floor')
    return physical, t


def main():
    controls = 0

    def rejected(call):
        nonlocal controls
        try:
            call()
        except ValueError:
            controls += 1
        else:
            raise ValueError('negative control accepted')

    pins = json.loads((HERE / 'INPUTS.json').read_text())
    for row in pins:
        data = (HERE / row['local']).read_bytes()
        authenticate(data, row)
        rejected(lambda: authenticate(data + b' ', row))
    provider = json.loads((HERE / 'source/provider.json').read_text())
    normalizers = json.loads((HERE / 'source/normalizers.json').read_text())
    kernel = json.loads((HERE / 'source/kernel.json').read_text())
    raw = [F(0)] * 641
    pairs = kernel['original_input_displacement']
    require(len({i for i, _ in pairs}) == len(pairs), 'duplicate role')
    for i, value in pairs:
        require(0 <= i < 632, 'role range')
        raw[i] = F(value)
    physical, target = audit(provider, normalizers, raw)

    # Check both full basis products, not only the selected displacement.
    for role in provider['basis_roles']:
        v = [F(0)] * 641
        v[role] = F(1)
        for first, second in [('input_basis_program','output_basis_program'),
                              ('output_basis_program','input_basis_program')]:
            require(program(provider[second], program(provider[first], v)) == v,
                    'full basis inverse product')

    words = [port['compiled_wrappers'][name]['word'] for port in normalizers['ports']
             for name in ['backward_input_X','backward_input_Y']]
    mode_one = next(x for x in provider['mode_boundaries'] if x['mode'] == 1)
    words.append(mode_one['input_K']['literal_word'])
    for word in words:
        monomial_unitary(word)

    # For G=aI+bX, these are the diagonal and off-diagonal entries of G*G.
    a, b = (F(1,2),F(1,2)), (F(1,2),F(-1,2))
    require(norm2(a)+norm2(b) == 1 and sum(x*y for x,y in zip(a,b)) == 0,
            'native one-axis unitarity')

    for role in [0,113,224]:
        changed = list(raw)
        changed[role] += 1
        rejected(lambda: audit(provider, normalizers, changed))
    changed = deepcopy(provider)
    changed['mode_owners'].remove(225)
    rejected(lambda: audit(changed, normalizers, raw))
    changed = deepcopy(provider)
    changed['input_basis_program'][0][3] = str(F(changed['input_basis_program'][0][3]) + 1)
    v = [F(0)] * 641
    v[changed['input_basis_program'][0][2]] = 1
    rejected(lambda: require(program(changed['output_basis_program'],
                                     program(changed['input_basis_program'],v)) == v,
                             'changed basis coefficient'))
    changed = deepcopy(normalizers)
    changed['mode_columns'][1][1] += 1
    rejected(lambda: audit(provider, changed, raw))
    bad = deepcopy(words[0])
    next(op for op in bad if op[0] == 'P')[1][0] = 0
    rejected(lambda: monomial_unitary(bad))
    rejected(lambda: require(norm2(target)/norm2(raw) == F(1,19), 'raw is not physical norm'))
    rejected(lambda: require(norm2(target)*19 > norm2(physical), 'larger claimed constant'))

    # Check the antipodal square-loss identity with rational complex outputs.
    loss_checks = 0
    for real in range(-6,7):
        for imag in range(-4,5):
            z = (F(real,3),F(imag,5))
            average = ((z[0]-2)**2+z[1]**2+(z[0]+2)**2+z[1]**2)/2
            require(average == norm2(z)+4 and average/76 >= F(1,19), 'antipodal loss')
            loss_checks += 1
    print(json.dumps(dict(status='PASS_PARTIAL_CACHE_MINIMAX_FLOOR',
                          source_copies=len(pins), basis_products=2*len(provider['basis_roles']),
                          monomial_address_checks=512*len(words), loss_checks=loss_checks,
                          raw_norm_squared=str(norm2(raw)), physical_norm_squared='76',
                          target_norm_squared='4', squared_floor='1/19', controls=controls),
                     sort_keys=True))


if __name__ == '__main__':
    main()
