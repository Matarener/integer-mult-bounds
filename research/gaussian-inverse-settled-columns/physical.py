"""Source-bound complete encoded inversion workload and literal output oracle."""
from contextlib import contextmanager, nullcontext
from fractions import Fraction
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/physical-gaussian-core"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    source_path = HERE / "SOURCES.json"
    require(source_path.stat().st_size <= 65536, "bounded source manifest")
    manifest = json.loads(source_path.read_text())
    require(len(manifest["files"]) <= 16, "bounded source inventory")
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(path.resolve().is_relative_to(ROOT.resolve()), "repository-relative input")
        require(path.is_file() and not path.is_symlink(), "regular source input")
        require(path.stat().st_size <= 128 * 1024 * 1024, "bounded source input")
        require(sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "source hash mismatch: " + row["path"])


@contextmanager
def runtime():
    authenticate()
    require(not any(n in sys.modules for n in
                    ("gaussian_sources", "gaussian_matrix", "gaussian_rationals")),
            "cold physical Gaussian namespace")
    sys.path.insert(0, str(SOURCE))
    sources = importlib.import_module("gaussian_sources")
    with sources.opened():
        yield


def fixture(name):
    require(name in ("dense3", "rational3", "dense4", "identity4"), "known workload")
    if name == "rational3":
        return [[Fraction(4), Fraction(-1), Fraction(0)],
                [Fraction(1, 3), Fraction(5), Fraction(-1, 2)],
                [Fraction(0), Fraction(1, 4), Fraction(3)]]
    n = 3 if name == "dense3" else 4
    return [[Fraction((n + 1 if i == j else 1) if name != "identity4"
                      else int(i == j)) for j in range(n)] for i in range(n)]


def run_case(engine, values, instrument=False):
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_matrix import Matrix, inverse as baseline
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK
    from ring_check_words import decode
    from inverse import inverse as candidate

    require(engine in ("baseline", "candidate"), "known inverse engine")
    require(1 <= len(values) <= 4 and 1 <= len(values[0]) <= 4
            and all(len(row) == len(values[0]) for row in values), "bounded rectangular fixture")
    pool = ScratchPool(256)
    scope = OuterScope(pool)
    counts = {"get": 0, "set": 0}
    try:
        with sealed_constructors(), scope.installed():
            with owned(Count.literal(len(values)), Count.literal(len(values[0]))) as (rows, columns):
                matrix = Matrix(rows, columns, pool, lambda i, j: encode(values[decode(i)][decode(j)]))
                try:
                    saved = (bytes(borrowed_tape(matrix.current).cells), borrowed_tape(matrix.current).head)
                    with counted(Matrix, counts) if instrument else nullcontext():
                        with no_decode():
                            result = baseline(matrix) if engine == "baseline" else candidate(matrix)
                    with owned(result):
                        output = decode_matrix(result)
                    require(saved == (bytes(borrowed_tape(matrix.current).cells), borrowed_tape(matrix.current).head), "source preserved")
                finally:
                    matrix.close()
    finally:
        pool.empty()
        require(not pool.live, "empty physical scratch pool")
        for tape in pool.tapes:
            erase_marker(tape)
            require(tape.head == 1 and all(v == BLANK for v in tape.cells), "physical scratch restored")
    if instrument:
        counts["pooled_tape"] = {key: sum(getattr(t.meter, key) for t in pool.tapes)
                                 for key in ("reads", "writes", "moves")}
        counts["pool_peak"] = pool.peak
    return {"output": [[str(v) for v in row] for row in output], "counts": counts}


def encode(value):
    from cardinal_counts import Count
    from gaussian_rationals import Rational
    from ring_words import Signed
    value = Fraction(value)
    require(abs(value.numerator) < 2**16 and value.denominator < 2**16, "bounded fixture scalar")
    return Rational(Signed(Count.literal(abs(value.numerator)), value < 0),
                    Count.literal(value.denominator))


def decode_matrix(matrix):
    from cardinal_counts import Count
    from ring_check_words import decode
    from router_metadata import owned
    output = []
    for i in range(decode(matrix.rows)):
        row = []
        for j in range(decode(matrix.columns)):
            with owned(Count.literal(i), Count.literal(j)) as (a, b):
                with owned(matrix.get(a, b)) as (value,):
                    n, d = decode(value.numerator.magnitude), decode(value.denominator)
                    row.append(Fraction(-n if value.numerator.negative else n, d))
        output.append(row)
    return output


@contextmanager
def counted(matrix_type, counts):
    old_get, old_set = matrix_type.get, matrix_type.set

    def get(self, row, column):
        counts["get"] += 1
        return old_get(self, row, column)

    def set_value(self, row, column, value):
        counts["set"] += 1
        return old_set(self, row, column, value)

    with patch.object(matrix_type, "get", get), patch.object(matrix_type, "set", set_value):
        yield
