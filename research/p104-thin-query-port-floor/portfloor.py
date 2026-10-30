"""Per-port linear-information floor for the thin QUERY_SHEAR stages of a p16 Laurent controller.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.

Model (one central port).  The 32 banks hold elements of R = K[Q, Q^-1]; the initial content of bank i is the
formal symbol b_i.  The controller alphabet (research/p104-productive-controller/caller.py) is replayed with the
literal rational coefficients.  Free operations are ADD with a scalar, SWAP/SIGNED_SWAP, Q_POWER +-2 (even central
powers) and the stage markers of LOCAL/IDLE.  Markers are specialised to 1 (a ring homomorphism, so every rank
difference below stays a valid lower bound for the marked contents).  Q^2 is specialised to a nonzero scalar theta,
so R becomes the K-space K + K.Q of dimension 2 per bank; this is again a homomorphic image of the Laurent model.

A LOCAL (paid full call, kept by atlas target P8) produces Q^{-1} x for its source content x (Q x in the backward
orientation) for free.  A latent channel of rank one, evaluated on one available content v, produces an element of
R.v, i.e. at most one new generator beyond the free span (Q^{2k} v is already free).  Hence after m channels every
content lies in F + span(q_1..q_m) where F is the K-span of the initial banks and the LOCAL outputs, and the m
channels must reproduce all shear results n_j = Q^{-1} u_j (or -Q u_j) of the QUERY_SHEAR events.  Therefore

    m  >=  dim(F + span{n_j}) - dim(F).

The causal greedy realization (query exactly when the current shear result is outside F + earlier query results)
is an upper bound inside the same model.
"""
from fractions import Fraction as Q
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def plus(dst, src, c):
    for k, v in src.items():
        x = dst.get(k, 0) + c * v
        if x:
            dst[k] = x
        else:
            dst.pop(k, None)


def shiftq(vec, dq):
    return {(b, q + dq): v for (b, q), v in vec.items()}


def embed(vec, theta):
    """K-coordinates after Q^2 -> theta: key (bank, parity)."""
    out = {}
    for (b, q), v in vec.items():
        par = q & 1
        key = (b, par)
        out[key] = out.get(key, 0) + v * theta ** ((q - par) // 2)
    return {k: v for k, v in out.items() if v}


class Space:
    """Reduced row basis of a K-subspace of a sparse coordinate space."""
    def __init__(self):
        self.rows = []

    def reduce(self, v):
        v = dict(v)
        for key, row in self.rows:
            if key in v:
                c = v[key]
                for k2, x in row.items():
                    y = v.get(k2, 0) - c * x
                    if y:
                        v[k2] = y
                    else:
                        v.pop(k2, None)
        return v

    def add(self, v):
        v = self.reduce(v)
        if not v:
            return False
        key = min(v)
        c = 1 / v[key]
        v = {k: x * c for k, x in v.items()}
        new = []
        for key2, row in self.rows:
            if key in row:
                c2 = row[key]
                row = dict(row)
                for k2, x in v.items():
                    y = row.get(k2, 0) - c2 * x
                    if y:
                        row[k2] = y
                    else:
                        row.pop(k2, None)
            new.append((key2, row))
        self.rows = new + [(key, v)]
        return True

    def contains(self, v):
        return not self.reduce(v)

    def dim(self):
        return len(self.rows)

    def copy(self):
        s = Space()
        s.rows = [(k, dict(r)) for k, r in self.rows]
        return s


def analyse(word, theta, free_odd=False, contents_free=False):
    """Replay one port.  Returns the receipt dict.

    free_odd: control, declares Q^{+-1} free as well (R0 = R); the floor must collapse to 0.
    contents_free: control, the flawed model that puts every present content into F (including the queried
    results themselves); the floor must collapse to 0 as well.
    """
    theta = Q(theta)
    need(theta != 0, 'nonzero central square')
    need(word['pairs'] == 16, 'p16 controller')
    if free_odd:
        # control: Q itself free, i.e. the homomorphic image Q -> 1, where R.b_i is one generator.
        def emb(v):
            out = {}
            for (b, q), x in v.items():
                out[(b, 0)] = out.get((b, 0), 0) + x
            return {k: x for k, x in out.items() if x}
    else:
        def emb(v):
            return embed(v, theta)
    banks = [{(i, 0): Q(1)} for i in range(32)]
    F = Space()
    for i in range(32):
        F.add(emb(banks[i]))
    needs, greedy, log = [], Space(), []
    locals_, shears = 0, 0
    for idx, e in enumerate(word['physical_events']):
        op = e[0]
        if op in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, back = e
            x, y = 2 * pair, 2 * pair + 1
            if back:
                x, y = y, x
            shear = shiftq(banks[x], 1 if back else -1)
            sign = Q(-1 if back else 1)
            if op == 'QUERY_SHEAR':
                shears += 1
                n = {k: sign * v for k, v in shear.items()}
                needs.append((idx, stage, pair, n))
                cur = F.copy()
                for r in greedy.rows:
                    cur.add(dict(r[1]))
                if cur.contains(emb(n)):
                    log.append([idx, stage, pair, 'free'])
                else:
                    greedy.add(emb(n))
                    log.append([idx, stage, pair, 'query'])
            plus(banks[y], shear, sign)
            if op == 'LOCAL':
                locals_ += 1
                F.add(emb(shear))
        elif op == 'Q_POWER':
            need(e[2] in (-2, 2), 'only even central powers are free')
            banks[e[1]] = shiftq(banks[e[1]], e[2])
        elif op == 'IDLE':
            pass                      # markers specialised to 1
        elif op == 'ADD':
            plus(banks[e[1]], banks[e[2]], Q(e[3]))
        elif op in ('SWAP', 'SIGNED_SWAP'):
            a, b = banks[e[1]], banks[e[2]]
            banks[e[1]], banks[e[2]] = b, ({k: -v for k, v in a.items()} if op == 'SIGNED_SWAP' else a)
        else:
            raise ValueError('controller opcode ' + op)
        if contents_free:
            for r in range(32):
                F.add(emb(banks[r]))
    dimF = F.dim()
    G = F.copy()
    for _, _, _, n in needs:
        G.add(emb(n))
    # each shear result against the free span plus all the other shear results
    singles = []
    for j in range(len(needs)):
        H = F.copy()
        for k, (_, _, _, n) in enumerate(needs):
            if k != j:
                H.add(emb(n))
        singles.append(int(not H.contains(emb(needs[j][3]))))
    return {'theta': str(theta), 'events': len(word['physical_events']), 'locals': locals_, 'query_shears': shears,
            'dim_free': dimF, 'dim_free_plus_needs': G.dim(), 'floor': G.dim() - dimF,
            'greedy_queries': sum(1 for row in log if row[3] == 'query'), 'greedy_log': log,
            'independent_of_all_others': singles}


def read(path):
    return json.loads(open(path).read())
