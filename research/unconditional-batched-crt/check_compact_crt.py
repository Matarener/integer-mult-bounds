"""Compose actual raw compact words, keyed repair and CRT switch layers.

Complete 12-bit fixture, arbitrary dirty controls and spectator bits.
This checks the composition endpoint, not an asymptotic machine tariff.
"""
import json
from check_batched_crt import benes, compact, good, need, rotation

BITS = 12
SIZE = 1 << BITS


def unpack(x):
    return x >> 10, (x >> 8) & 3, x & 255


def pack(u, t, y):
    return (u << 10) | (t << 8) | y


def ideal(x, target, source):
    u, t, y = unpack(x)
    return pack(u, t, y ^ (source(y)[0] << target))


def layer(values, target, source):
    inverse = [None] * SIZE
    raw = [None] * SIZE
    for x in range(SIZE):
        out = pack(*compact(*unpack(x), source, positions=(target,), ybits=8))
        need(inverse[out] is None, 'raw complete-word injection')
        inverse[out] = x
        raw[out] = values[x]
    holes = [not good(*unpack(q), positions=(target,), guard=6) for q in range(SIZE)]
    exceptional, ordinary = [], []
    for q, is_bad in enumerate(holes):
        if is_bad:
            exceptional.append((ideal(inverse[q], target, source), raw[q]))
        else:
            need(ideal(inverse[q], target, source) == q, 'raw good endpoint')
            ordinary.append(raw[q])
    # Actual increasing-low-bit stable passes on whole key/payload pairs.
    for bit in range(BITS):
        exceptional = ([pair for pair in exceptional if not ((pair[0] >> bit) & 1)] +
                       [pair for pair in exceptional if (pair[0] >> bit) & 1])
    final = []
    bad_index = good_index = 0
    for q, is_bad in enumerate(holes):
        if is_bad:
            key, payload = exceptional[bad_index]
            need(key == q, 'keyed repair must fill the next actual hole')
            final.append(payload)
            bad_index += 1
        else:
            final.append(ordinary[good_index])
            good_index += 1
    need(bad_index == len(exceptional) and good_index == len(ordinary), 'stream exhaustion')
    oracle = [None] * SIZE
    for x in range(SIZE):
        oracle[ideal(x, target, source)] = values[x]
    need(final == oracle, 'complete layer on current payload')
    return final, bad_index


def main():
    # a has width2 with modulus3; b has width3 with modulus5.
    # The three upper y bits and all u/t bits are arbitrary dirty spectators.
    networks = [benes(rotation(8, 5, (2*a) % 5 if a < 3 else 0)) for a in range(4)]
    values = list(range(SIZE))
    repairs = 0
    schedule = []
    for index in range(5):
        target = networks[0][index][0]
        need(all(net[index][0] == target for net in networks), 'control-independent schedule')
        def source(y, index=index):
            return (networks[(y >> 3) & 3][index][1][y & 7],)
        need(all(source(y) == source(y ^ (1 << target)) for y in range(256)),
             'network function omits its active target')
        values, count = layer(values, target, source)
        repairs += count
        schedule.append((target, source))
    oracle = [None] * SIZE
    valid = 0
    for x in range(SIZE):
        u, t, y = unpack(x)
        a, b = (y >> 3) & 3, y & 7
        new_b = (b+2*a) % 5 if a < 3 and b < 5 else b
        destination = pack(u, t, (y & ~7) | new_b)
        oracle[destination] = x
        valid += a < 3 and b < 5
    need(values == oracle, 'full padded CRT endpoint after five repaired layers')
    for target, source in reversed(schedule):
        values, count = layer(values, target, source)
        repairs += count
    need(values == list(range(SIZE)), 'full inverse returns every dirty input column')
    return {'status': 'PASS_COMPLETE_COMPACT_CRT_FIXTURE', 'addresses': SIZE,
            'valid_addresses': valid, 'repaired_layers': 10,
            'exceptional_pair_visits': repairs,
            'all_dirty_controls_and_spectators': True,
            'machine_cost_verified': False, 'multiplication_kappa_claimed': False}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2, sort_keys=True))
