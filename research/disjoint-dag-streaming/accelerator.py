"""Opt-in bounded-memory serialization for the unchanged disjoint-tensor checks.

This contribution was produced by Nick Petalas. Apache-2.0.
The verify body retains Douglas Colkitt's original checker, including Wentao
Li's support-mask optimization. Only its digest expression changes.
"""
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MAX_NODES = 1_000_000
MAX_SUPPORT_BITS = 10_000
CHUNK_BYTES = 65_536


def check_sources(root=ROOT, overrides=None):
    """Authenticate every declared live input before importing its code."""
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    overrides = {} if overrides is None else overrides
    for row in manifest["files"]:
        if row["usage"] == "input":
            name = row["path"]
            data = overrides[name] if name in overrides else (root / name).read_bytes()
            if sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("Source changed: " + name)


check_sources()
# -B prohibits bytecode writes, but does not prohibit old bytecode reads.
sys.dont_write_bytecode = True
cache_prefix = PACKAGE / ".disabled-bytecode-cache"
if cache_prefix.exists():
    raise ValueError("The disabled cache namespace must be absent")
sys.pycache_prefix = str(cache_prefix)
sys.path.insert(0, str(ROOT / "scripts"))
from certify import require
from experiments.disjoint_tensor import DisjointTensor, plan


def chunks(circuit, chunk_bytes=CHUNK_BYTES):
    """Yield the exact compact JSON bytes with a bounded row buffer."""
    require(type(chunk_bytes) is int and 1 <= chunk_bytes <= CHUNK_BYTES,
            "Invalid chunk budget")
    size = len(circuit.support)
    require(size == len(circuit.args) and size <= MAX_NODES,
            "Node-array budget exceeded")
    require(len(circuit.active) <= size, "Invalid active-node count")
    buffer = bytearray(b"[")
    for position, node in enumerate(sorted(circuit.active)):
        require(type(node) is int and 0 <= node < size, "Invalid node")
        support = circuit.support[node]
        require(type(support) is int and support >= 0
                and support.bit_length() <= MAX_SUPPORT_BITS, "Invalid support")
        pair = circuit.args[node]
        if pair is None:
            args = "null"
        else:
            require(type(pair) is tuple and len(pair) == 2
                    and all(type(x) is int and 0 <= x < size for x in pair),
                    "Invalid argument pair")
            args = f"[{pair[0]},{pair[1]}]"
        if position:
            buffer.extend(b",")
        buffer.extend(f'[{node},{args},"{support}"]'.encode("ascii"))
        if len(buffer) >= chunk_bytes:
            yield bytes(buffer)
            buffer.clear()
    buffer.extend(b"]")
    yield bytes(buffer)


def stream_digest(circuit):
    """Consume every chunk before returning the canonical DAG SHA256."""
    digest = sha256()
    for chunk in chunks(circuit):
        digest.update(chunk)
    return digest.hexdigest()


def verify(self):
    for node in sorted(self.active):
        if self.args[node]:
            a, b = self.args[node]
            require(a < node and b < node and not self.support[a]&self.support[b],
                    'An addition uses cancellation or is not acyclic')
            require(self.support[node] == self.support[a]|self.support[b], 'Wrong sum')
    # Expected output support equals the full input mask with every input
    # that meets T cleared. Equivalent to the historical genexpr
    # sum(1<<i for i,S in enumerate(inputs) if not S&T).
    # See research/disjoint-tensor-support-masks/.
    full = (1 << len(self.inputs)) - 1
    vertex = [0] * self.h
    for i, S in enumerate(self.inputs):
        bits = S
        while bits:
            bit = bits & -bits
            bits ^= bit
            vertex[bit.bit_length() - 1] |= 1 << i
    for T, node in self.outputs.items():
        hit = 0
        bits = T
        while bits:
            bit = bits & -bits
            bits ^= bit
            hit |= vertex[bit.bit_length() - 1]
        require(self.support[node] == full ^ hit, 'Wrong integer output coefficient')
    require(self.additions <= plan(self.h,self.k,self.k)[0], 'Interning exceeded recurrence')
    code = self.compile(); values = [0]*code['roles']
    for S, slot in code['sources'].items(): values[slot] = self.support[self.variables[S]]
    for node, ins, outs in code['gates']:
        for slot in ins[1:]:
            require(not values[ins[0]]&values[slot], 'Embedding adds overlapping supports')
            values[ins[0]] |= values[slot]
        for slot in outs[1:]:
            require(values[slot] == 0, 'Fanout destination is not fresh')
            values[slot] = values[ins[0]]
    for T, slot in code['outputs'].items():
        require(values[slot] == self.support[self.outputs[T]], 'Wrong embedded output')
    return dict(h=self.h,k=self.k,inputs=len(self.inputs),outputs=len(self.outputs),
                additions=self.additions,unshared_recurrence_additions=plan(self.h,self.k,self.k)[0],
                roles=code['roles'],integer_coefficient_map_verified=True,
                disjoint_additions_verified=True,embedding_verified=True,
                coefficients=len(self.inputs)*comb(self.h-self.k,self.k),
                dag_sha256=stream_digest(self))
