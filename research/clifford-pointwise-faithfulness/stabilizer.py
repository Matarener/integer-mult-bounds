"""Exact pointwise residuals for affine-quadratic stabilizer maps.

Map coordinates list the output bits first, then the input bits. Scalars
inside a map are raised to the tensor width. Residual coefficients are not.
The exact quadratic-sum kernel is retained from the pinned predecessor.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
from quadratic import Phase, gauss_sum, rank
from certify import G, scalar, norm2, conjugate, power, require
from bounds import pointwise_bound


class Map:
    def __init__(self, specification):
        require(type(specification) is dict and set(specification) ==
                {"input_axes", "output_axes", "offset", "basis", "linear", "pairs", "scale"},
                "Stabilizer map keys")
        self.specification = specification
        self.input_axes, self.output_axes = specification["input_axes"], specification["output_axes"]
        require(all(type(n) is int and n >= 0 for n in (self.input_axes, self.output_axes)), "Map axes")
        self.n = self.input_axes+self.output_axes
        self.basis = specification["basis"]
        self.offset = specification["offset"]
        require(type(self.basis) is list and all(type(b) is int and 0 < b < 1 << self.n
                for b in self.basis) and rank(self.basis) == len(self.basis), "Independent support basis")
        require(type(self.offset) is int and 0 <= self.offset < 1 << self.n, "Support offset")
        k = len(self.basis)
        linear, pairs = specification["linear"], specification["pairs"]
        require(type(linear) is list and len(linear) == k and
                all(type(a) is int and 0 <= a < 4 for a in linear), "Quadratic linear phase")
        require(type(pairs) is list and all(type(p) is list and len(p) == 2 and
                all(type(j) is int for j in p) and 0 <= p[0] < p[1] < k for p in pairs), "Quadratic pairs")
        require(len(set(map(tuple, pairs))) == len(pairs), "Duplicate quadratic pair")
        self.scale = scalar(specification["scale"])
        require(bool(self.scale), "A map must be nonzero")
        self.phase = Phase(k)
        self.phase.linear = linear.copy()
        self.phase.cross = set(map(tuple, pairs))
        self.coordinates = [((self.offset >> j) & 1) |
                            sum(((b >> j) & 1) << (t+1) for t, b in enumerate(self.basis))
                            for j in range(self.n)]

    def entry(self, coordinate):
        require(type(coordinate) is int and 0 <= coordinate < 1 << self.n, "Map coordinate")
        equations = [value ^ ((coordinate >> j) & 1) for j, value in enumerate(self.coordinates)]
        return self.scale*gauss_sum(self.phase, equations)


def inner(left, right, prefix=()):
    require((left.input_axes, left.output_axes) == (right.input_axes, right.output_axes), "Common map type")
    require(len(prefix) <= left.n and all(type(b) is int and b in (0, 1) for b in prefix), "Map prefix")
    a, b = len(left.basis), len(right.basis)
    phase = Phase(a+b)
    phase.linear = [(-x) % 4 for x in left.phase.linear]+right.phase.linear
    phase.cross = left.phase.cross | {(i+a, j+a) for i, j in right.phase.cross}
    shift = lambda mask: (mask & 1) | ((mask >> 1) << (a+1))
    equations = [x ^ shift(y) for x, y in zip(left.coordinates, right.coordinates)]
    equations += [left.coordinates[j] ^ bit for j, bit in enumerate(prefix)]
    return conjugate(left.scale)*right.scale*gauss_sum(phase, equations)


def analyze(specifications, coefficients, width):
    require(type(specifications) is list and bool(specifications), "Nonempty map list")
    require(type(coefficients) is list and len(specifications) == len(coefficients), "Residual coefficient count")
    maps = [Map(item) for item in specifications]
    require(all((item.input_axes, item.output_axes) == (maps[0].input_axes, maps[0].output_axes)
                for item in maps), "Common map type")
    n = maps[0].n
    require(type(width) is int and width >= 2*n+6, "Width is below the stabilizer threshold")
    values = [scalar(value) for value in coefficients]
    gram = [[inner(a, b) for b in maps] for a in maps]
    diagonal = [row[j].real for j, row in enumerate(gram)]
    require(all(row[j].imag == 0 and diagonal[j] > 0 for j, row in enumerate(gram)), "Positive map norm")
    representatives, grouped = [], []
    for j, value in enumerate(values):
        match = next((i for i, k in enumerate(representatives)
                      if norm2(gram[k][j]) == diagonal[k]*diagonal[j]), None)
        if match is None:
            representatives.append(j)
            grouped.append(value)
        else:
            k = representatives[match]
            ratio = gram[k][j]/diagonal[k]
            grouped[match] += value*power(ratio, width)
    mass = sum(norm2(value)*diagonal[k]**width for k, value in zip(representatives, grouped))
    energy = sum((conjugate(a)*b*power(gram[i][j], width)
                  for i, a in enumerate(values) for j, b in enumerate(values)), G(0))
    lower = pointwise_bound(n, width)
    require(energy.imag == 0 and lower*mass <= energy.real <= (2-lower)*mass,
            "Stabilizer pointwise Gram estimate")
    return {"schema": "stabilizer-pointwise/v1", "input_axes": maps[0].input_axes,
            "output_axes": maps[0].output_axes, "width": width,
            "gram_lower_bound": str(lower), "projective_classes": len(representatives),
            "coefficient_mass": str(mass), "squared_norm": str(energy.real),
            "equal_to_zero": not any(grouped)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    args = parser.parse_args()
    problem = json.loads(args.problem.read_text())
    require(type(problem) is dict and set(problem) == {"maps", "coefficients", "width"}, "Problem keys")
    print(json.dumps(analyze(problem["maps"], problem["coefficients"], problem["width"]),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
