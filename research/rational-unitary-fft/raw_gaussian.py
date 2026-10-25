"""Anchored raw Gaussian circuits compared with one rounded reference.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Raw identities: Jeremy Kothe/IdeaOuter and retained Gaussian
lineage; circuit: Vlado; interval arithmetic: Mason Hale.
"""
from fractions import Fraction as Q

from exact import C, Mat, ceil_log2, need, vector_hash
from full import allocation
from gaussian import Gaussian, rational
from gaussian_reference import ceiling


class RawGaussian:
    def __init__(self, raw, reference, kind, start, n, radius, target, incoming=0):
        need(kind in ("narrow", "broad"), "raw Gaussian direction family")
        radius = rational(radius)
        need(radius >= 1 and type(target) is int and target >= 1
             and type(incoming) is int and incoming >= 0, "raw radius and precision")
        coordinates, center, beta = reference.interior(start, n)
        self.raw, self.reference, self.kind = raw, reference, kind
        self.start, self.n, self.radius, self.target, self.incoming = start, n, radius, target, incoming
        self.coordinates, self.center, self.beta = coordinates, center, beta
        alpha, theta, rho, lam = reference.spec.alpha, reference.theta, reference.rho, reference.lam
        offsets = [Q(j) - center for j in range(start, start + n)]
        if kind == "narrow":
            self.c, self.shift = alpha ** 2 * rho, -beta / rho
            self.a_factors = [alpha ** 2 * theta * x ** 2 for x in offsets]
            self.b_factors = [-x for x in self.a_factors]
            self.a_scale = Q(1)
        else:
            delta, rate = beta / rho, lam * theta / alpha ** 2
            self.c, self.shift = lam / alpha ** 2, -delta * (1 - theta)
            self.a_factors = [-delta ** 2 / alpha ** 2 + rate * (lam * y ** 2 + 2 * delta * y)
                              for y in offsets]
            self.b_factors = [-rate * (x ** 2 + 4 * delta * x) for x in offsets]
            self.a_scale = Q(1, alpha)
        self.gauge_exponent_bound = max(abs(x) for x in self.a_factors + self.b_factors)
        self.gauge_bound = alpha * (1 << ceiling(8 * self.gauge_exponent_bound))
        probe = Gaussian(raw, n, self.c, self.shift, 1, 1)
        self.qbar, self.middle_bound = probe.qbar, max(Q(n), probe.qbar)
        g, h = self.gauge_bound, self.middle_bound
        self.raw_inverse_bound = g ** 2 * h
        tau = Q(1, 1 << target)
        self.reference_error = reference.errors[kind]
        need(self.reference_error <= tau / (8 * (radius + 1) * self.raw_inverse_bound ** 2),
             "common reference accuracy at this raw inverse caller")
        self.diagonal_error = tau / (24 * g * h * (radius + 1))
        self.relative_bits = max(1, ceil_log2(4 * g / self.diagonal_error))
        self.middle_radius = 2 * g * (radius + 1)
        self.middle_target = target + ceil_log2(16 * g)
        provisional = allocation(n, n, 2 * self.qbar, self.middle_radius,
                                 self.middle_target + 1, incoming)
        self.data_bits = max(incoming, target + ceil_log2(24 * n * g * h),
                             provisional["data_bits"])
        self.child = Gaussian(raw, n, self.c, self.shift, self.middle_radius,
                              self.middle_target, self.data_bits)
        need(self.child.qbar == self.qbar, "same normalized conditioning allowance")
        self.decays, self.diagonal_records = {}, []
        self.a_values = [self.coefficient(f, self.a_scale) for f in self.a_factors]
        self.b_values = [self.coefficient(f, Q(1)) for f in self.b_factors]
        if kind == "narrow":
            need(all(a * b == 1 for a, b in zip(self.a_values, self.b_values)),
                 "one stored narrow chirp and its exact reciprocal")
        self.check_identity()
        self.reference_matrix = reference.window(kind, coordinates)
        self.reference_description = reference.description_hash
        self.reference_hash = vector_hash([z for row in self.reference_matrix for z in row])
        self.plan, self.inverse_plan = None, None

    def coefficient(self, factor, scale):
        absolute = abs(factor)
        if absolute not in self.decays:
            self.decays[absolute] = self.reference.exp.relative(
                absolute, self.gauge_exponent_bound, self.relative_bits)
        row = self.decays[absolute]
        if factor >= 0:
            value, lower, upper = 1 / row["value"], 1 / row["upper"], 1 / row["lower"]
        else:
            value, lower, upper = row["value"], row["lower"], row["upper"]
        value, lower, upper = scale * value, scale * lower, scale * upper
        error = max(abs(value - lower), abs(value - upper))
        inverse_error = max(abs(1 / value - 1 / lower), abs(1 / value - 1 / upper))
        need(value > 0 and max(error, inverse_error) <= self.diagonal_error,
             "direct and exact stored reciprocal diagonal errors")
        self.diagonal_records.append(dict(factor=str(factor), scale=str(scale), value=str(value),
                                          direct_error=str(error), inverse_error=str(inverse_error),
                                          precision=row["precision"]))
        return value

    def ideal_factor(self, i, j):
        ref, alpha = self.reference, self.reference.spec.alpha
        row, column = self.start + i, self.start + j
        if self.kind == "narrow":
            return -alpha ** 2 * ((ref.rho * (column - row) + ref.betas[row]) ** 2
                                  - ref.betas[column] ** 2)
        return -(Q(column) - ref.lam * ref.selected[row]) ** 2 / alpha ** 2

    def check_identity(self):
        for i in range(self.n):
            for j in range(self.n):
                u = j - i
                total = (self.a_factors[i] - self.c * (u ** 2 - 2 * self.shift * u)
                         + self.b_factors[j])
                need(total == self.ideal_factor(i, j), "exact anchored raw source identity")

    def compile(self):
        need(self.plan is None, "raw caller executes once")
        need(self.reference.description_hash == self.reference_description
             and self.reference.window(self.kind, self.coordinates) == self.reference_matrix,
             "same common reference at raw execution boundary")
        middle = self.child.compile()
        self.plan = ([[(tuple([i]), Mat([[value]])) for i, value in enumerate(self.b_values)]]
                     + list(middle)
                     + [[(tuple([i]), Mat([[value]])) for i, value in enumerate(self.a_values)]])
        self.inverse_plan = self.child.builder.inverse(self.plan)
        cb = self.child.builder.bound
        need(cb["data_bits"] == self.data_bits, "one raw and normalized data grid")
        g, h, radius = self.gauge_bound, self.middle_bound, self.radius
        self.rounding_error = self.n * Q(1, 1 << self.data_bits)
        need((g + self.diagonal_error) * radius + self.rounding_error <= self.middle_radius,
             "rounded input diagonal fits common normalized radius")
        self.middle_error = max(self.child.forward_error, self.child.inverse_error)
        self.raw_error = (2 * g * self.middle_error + 3 * g * h * self.diagonal_error * radius
                          + 3 * g * h * self.rounding_error)
        self.forward_error = self.raw_error + self.reference_error * radius
        self.inverse_error = self.raw_error + 2 * self.raw_inverse_bound ** 2 * self.reference_error * radius
        tau = Q(1, 1 << self.target)
        need(self.raw_error < 3 * tau / 8
             and max(self.forward_error, self.inverse_error) < tau, "complete raw reference error budget")
        amplitude = max(radius, cb["amplitude_bound"],
                        (g + 1) * (h * self.middle_radius + self.middle_error) + self.rounding_error)
        integer_bits = max(1, ceil_log2(max(Q(1), amplitude))) + 2
        gauge_height = max(row["precision"] for row in self.diagonal_records) + self.reference.spec.alpha.bit_length() + 2
        height = max(gauge_height, cb["coefficient_height_bound"])
        self.bound = dict(n=self.n, data_bits=self.data_bits, integer_bits=integer_bits,
                          coefficient_height_bound=height,
                          temporary_bits=2 * self.data_bits + 8 * height + 2 * integer_bits + 32,
                          amplitude_bound=amplitude,
                          layer_bound=cb["layer_bound"] + 2, gate_bound=cb["gate_bound"] + 2 * self.n)
        need(len(self.plan) <= self.bound["layer_bound"]
             and sum(map(len, self.plan)) <= self.bound["gate_bound"], "raw circuit size")
        return self.plan

    def record(self):
        need(self.plan is not None, "compiled raw receipt")
        return dict(kind=self.kind, start=self.start, n=self.n, coordinates=list(self.coordinates),
                    center=str(self.center), beta=str(self.beta),
                    reference_description_sha256=self.reference.description_hash,
                    reference_matrix_sha256=self.reference_hash,
                    radius=str(self.radius), target_bits=self.target, incoming_bits=self.incoming,
                    gauge_exponent_bound=str(self.gauge_exponent_bound),
                    gauge_bound=str(self.gauge_bound), normalized_bound=str(self.middle_bound),
                    raw_inverse_bound=str(self.raw_inverse_bound),
                    reference_error=str(self.reference_error), diagonal_error=str(self.diagonal_error),
                    diagonal_relative_bits=self.relative_bits, diagonal_coefficients=self.diagonal_records,
                    middle_radius=str(self.middle_radius), middle_error=str(self.middle_error),
                    raw_error=str(self.raw_error), forward_error=str(self.forward_error),
                    inverse_error=str(self.inverse_error),
                    budget={key: str(value) if isinstance(value, Q) else value
                            for key, value in self.bound.items()},
                    child=self.child.record())
