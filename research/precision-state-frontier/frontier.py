#!/usr/bin/env python3
"""Exact precision/recovery-state codec for the pinned 112-owner inverse.

Apache-2.0; substantial OpenAI Codex assistance. Not a priced reversible
circuit. Source arithmetic and same-grid recovery retain predecessor credit.
"""
from pathlib import Path
from itertools import product
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            need(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    with open(path, encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=unique)


def round52(value):
    need(type(value) is int, 'integer numerator required')
    return (1 if value >= 0 else -1)*((abs(value)+26)//52)


def ceildiv(a, b):
    return -((-a)//b)


def intvector(values, size):
    need(isinstance(values, list) and len(values) == size and all(type(x) is int for x in values),
         'exact integer vector required')
    return list(values)


class Geometry:
    def __init__(self):
        sources = load(ROOT/'SOURCES.json')
        raw = (ROOT/'FIXTURE.json').read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sources['fixture_sha256'], 'literal source fixture hash')
        fixture = load(ROOT/'FIXTURE.json')
        columns = fixture['mode_columns']
        need(len(columns) == 8 and all(len(v) == 112 for v in columns), 'eight source columns')
        self.m = list(map(list, zip(*columns)))
        need(all(type(x) is int and x in (-1, 0, 1) for row in self.m for x in row), 'source signs')
        self.fingerprint = sources['fixture_sha256']
        self.binary = [sum((a & 1) << j for j, a in enumerate(row)) for row in self.m]
        self.dual = [z for z in range(256) if all((z & row).bit_count() % 2 == 0 for row in self.binary)]
        need(len(self.dual) == 16, 'source dual dimension')
        self.signatures = {}
        for z in range(256):
            sig = sum(((z & row).bit_count() % 2) << i for i, row in enumerate(self.binary))
            self.signatures.setdefault(sig, []).append(z)
        self.pairs = [None]*8
        for i, a in enumerate(self.m):
            for k in range(i+1, len(self.m)):
                b = self.m[k]
                for ca, cb in product((-1, 1), repeat=2):
                    value = [ca*x+cb*y for x, y in zip(a, b)]
                    support = [j for j, x in enumerate(value) if x]
                    if len(support) == 1 and value[support[0]] == 2:
                        j = support[0]
                        if self.pairs[j] is None:
                            self.pairs[j] = (i, ca, k, cb)
        need(all(p is not None for p in self.pairs), 'source two-unit lattice witnesses')

    def mul(self, q):
        return [sum(a*b for a, b in zip(row, q)) for row in self.m]

    def transpose(self, x):
        return [sum(row[j]*a for row, a in zip(self.m, x)) for j in range(8)]

    @staticmethod
    def guard(g):
        need(type(g) is int and g >= 0, 'nonnegative integer relative guard required')
        need(g <= 16, 'guard budget exceeded: no decision')

    def maximum(self, g):
        self.guard(g)
        if g == 0:
            return 13**8
        step = 1 << (g-1)
        length = ceildiv(13, step)
        a, b = (length+1)//2, length//2
        return sum(a**(8-z.bit_count())*b**z.bit_count() for z in self.dual)

    def forward(self, x, g):
        self.guard(g)
        x = intvector(x, 112)
        scale = 1 << g
        q = [round52(scale*t) for t in self.transpose(x)]
        correction = self.mul(q)
        return [scale*a-b for a, b in zip(x, correction)], q

    def choices(self, y):
        s = self.transpose(y)
        choices = []
        for value in s:
            low, high = ceildiv(-26-value, 4), (26-value)//4
            allowed = [q for q in range(low, high+1) if round52(value+56*q) == q]
            need(len(allowed) <= 13, 'scalar fiber ceiling')
            choices.append(allowed)
        return choices

    def blocks(self, y, g):
        self.guard(g)
        y = intvector(y, 112)
        choices = self.choices(y)
        if g == 0:
            patterns = [None]
            base, step = [0]*8, 0
        else:
            step = 1 << (g-1)
            base = []
            for i, ca, k, cb in self.pairs:
                rhs = -ca*y[i]-cb*y[k]
                if rhs % 2:
                    return []
                base.append((rhs//2) % step)
            mb = self.mul(base)
            residual = [-a-b for a, b in zip(y, mb)]
            if any(a % step for a in residual):
                return []
            signature = sum(((a//step) & 1) << i for i, a in enumerate(residual))
            patterns = self.signatures.get(signature, [])
        blocks = []
        for pattern in patterns:
            if g == 0:
                lists = choices
            else:
                residues = [base[j]+step*((pattern >> j) & 1) for j in range(8)]
                modulus = 1 << g
                lists = [[q for q in values if q % modulus == residue]
                         for values, residue in zip(choices, residues)]
            count = 1
            for values in lists:
                count *= len(values)
            if count:
                blocks.append((lists, count))
        need(sum(count for _, count in blocks) <= self.maximum(g), 'source precision/state ceiling')
        return blocks

    def encode(self, x, g):
        y, q = self.forward(x, g)
        blocks = self.blocks(y, g)
        offset = 0
        for lists, count in blocks:
            if all(v in values for v, values in zip(q, lists)):
                rank = 0
                for v, values in zip(q, lists):
                    rank = rank*len(values)+values.index(v)
                maximum = self.maximum(g)
                return {'source_sha256': self.fingerprint, 'g': g, 'y': y, 'tag': offset+rank,
                        'fiber_states': sum(n for _, n in blocks), 'worst_case_states': maximum,
                        'tag_bits': (maximum-1).bit_length()}
            offset += count
        raise ValueError('true quotient missing from exact fiber')

    def recover(self, y, g, tag):
        need(type(tag) is int and tag >= 0, 'nonnegative integer tag required')
        blocks = self.blocks(y, g)
        for lists, count in blocks:
            if tag < count:
                q = [0]*8
                for j in range(7, -1, -1):
                    q[j] = lists[j][tag % len(lists[j])]
                    tag //= len(lists[j])
                correction = self.mul(q)
                numerator = [a+b for a, b in zip(y, correction)]
                scale = 1 << g
                need(all(v % scale == 0 for v in numerator), 'coarse input lattice')
                x = [v//scale for v in numerator]
                output, original_q = self.forward(x, g)
                need(output == y and original_q == q, 'exact source reconstruction')
                return x
            tag -= count
        raise ValueError('tag outside this output fiber')

    def decode(self, packet):
        need(isinstance(packet, dict) and set(packet) == {'source_sha256', 'g', 'y', 'tag',
             'fiber_states', 'worst_case_states', 'tag_bits'}, 'exact encoding fields required')
        need(packet['source_sha256'] == self.fingerprint, 'source binding')
        g = packet['g']; self.guard(g)
        blocks = self.blocks(packet['y'], g)
        maximum = self.maximum(g)
        need(type(packet['fiber_states']) is int and packet['fiber_states'] == sum(n for _, n in blocks),
             'fiber count binding')
        need(type(packet['worst_case_states']) is int and packet['worst_case_states'] == maximum,
             'worst-case count binding')
        need(type(packet['tag_bits']) is int and packet['tag_bits'] == (maximum-1).bit_length(),
             'tag bit binding')
        return self.recover(packet['y'], g, packet['tag'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('encode', 'decode', 'table'))
    parser.add_argument('file', nargs='?')
    args = parser.parse_args()
    geometry = Geometry()
    if args.mode == 'table':
        result = [{'relative_guard_bits': g, 'states': geometry.maximum(g),
                   'tag_bits': (geometry.maximum(g)-1).bit_length(),
                   'fractional_slots_plus_tag': 112*g+(geometry.maximum(g)-1).bit_length()}
                  for g in range(6)]
    else:
        need(args.file is not None, 'input file required')
        packet = load(args.file)
        if args.mode == 'encode':
            need(isinstance(packet, dict) and set(packet) == {'g', 'x'}, 'encode input fields')
            result = geometry.encode(packet['x'], packet['g'])
        else:
            result = {'status': 'RECOVERED_EXACT_INPUT', 'x': geometry.decode(packet)}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
