"""Checker-only sparse integer model of PR1673's four updates and XOR."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    pairs: tuple
    G: int
    K: int
    H: int
    N: int

    @property
    def widths(self):
        return self.H, self.H, self.N, self.H

    @property
    def position_bits(self):
        return max(1, (self.N-1).bit_length())

    def pack(self, y, sources=False):
        return sum(((y >> pair[0 if sources else 1]) & 1) << (i*self.G)
                   for i, pair in enumerate(self.pairs))

    def mask(self, state, compact=False):
        return sum(((state["u"] >> (i*self.G)) & 1 if compact else (state["y"] >> source) & 1) << target
                   for i, (source, target) in enumerate(self.pairs))

    def offset(self, state, kind):
        if kind in ("selected_x", "selected_y"):
            return self.pack(state["y"], kind == "selected_x")
        if kind == "original_compact":
            return self.pack(state["y"] ^ self.mask(state, True))
        digits = [(state["t"] >> (i*self.G)) & ((1 << self.G)-1) for i in range(len(self.pairs))]
        return sum(((state["u"] >> (i*self.G)) & 1)
                   * (2*digits[i] if kind == "first_compact" else 1-2*digits[i]) * (1 << target)
                   for i, (_source, target) in enumerate(self.pairs))

    def flip(self, state, inverse=False):
        out = dict(state)
        if inverse:
            out["t"] = (out["t"] + self.offset(out, "original_compact")) % (1 << self.H)
            out["y"] = (out["y"] - self.offset(out, "second_compact")) % (1 << self.N)
            out["t"] = (out["t"] - self.pack(out["y"])) % (1 << self.H)
            out["y"] = (out["y"] - self.offset(out, "first_compact")) % (1 << self.N)
        else:
            out["y"] = (out["y"] + self.offset(out, "first_compact")) % (1 << self.N)
            out["t"] = (out["t"] + self.pack(out["y"])) % (1 << self.H)
            out["y"] = (out["y"] + self.offset(out, "second_compact")) % (1 << self.N)
            out["t"] = (out["t"] - self.offset(out, "original_compact")) % (1 << self.H)
        return out

    def raw(self, state, inverse=False):
        out = dict(state)
        if inverse:
            out["u"] = (out["u"] + self.pack(out["y"], True)) % (1 << self.H)
            out = self.flip(out, True)
            out["u"] = (out["u"] - self.pack(out["y"], True)) % (1 << self.H)
            return self.flip(out, True)
        out = self.flip(out)
        out["u"] = (out["u"] + self.pack(out["y"], True)) % (1 << self.H)
        out = self.flip(out)
        out["u"] = (out["u"] - self.pack(out["y"], True)) % (1 << self.H)
        return out

    def ideal(self, state):
        out = dict(state)
        out["y"] ^= self.mask(state)
        return out

    def bad(self, state):
        base, span = 1 << self.G, 1 << (self.K-1)
        return any(any(((state[name] >> (i*self.G)) & (base-1)) == base-1 for name in ("u", "t"))
                   or not 2*base <= (state["y"] >> (target+1)) % span < span-2*base
                   for i, (_source, target) in enumerate(self.pairs))

    def decode(self, ordinal):
        result = {}
        for name, width in reversed(tuple(zip(("u", "t", "y", "b"), self.widths))):
            result[name] = ordinal % (1 << width)
            ordinal >>= width
        if ordinal:
            raise ValueError("complete reference address")
        return result

    def encode(self, state):
        ordinal = 0
        for name, width in zip(("u", "t", "y", "b"), self.widths):
            ordinal = (ordinal << width) + state[name]
        return ordinal

    def good_state(self, rng):
        base, span = 1 << self.G, 1 << (self.K-1)
        if self.pairs and span <= 4*base:
            return None
        state = {name: rng.randrange(1 << width) for name, width in zip(("u", "t", "y", "b"), self.widths)}
        for i, (_source, target) in enumerate(self.pairs):
            for name in ("u", "t"):
                state[name] &= ~((base-1) << (i*self.G))
                state[name] |= rng.randrange(base-1) << (i*self.G)
            state["y"] &= ~((span-1) << (target+1))
            state["y"] |= rng.randrange(2*base, span-2*base) << (target+1)
        return state
