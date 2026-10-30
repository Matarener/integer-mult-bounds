#!/usr/bin/env python3
"""All-width native certificate for the selected #5599 word (assumption native_all_columns).

Independent dense check (dense.py: full 512 x 512 exact matrices, no tableau, no sparse
state, no compiler semantics) that every paid chart change, every helper normalizer pair
and every main adapter of the selected word equals the compiler's lowered recipe
(Gaussian monomial, rank-r Fourier child, Gaussian monomial) as an exact operator with
absolute phase, that the child rank is the paid rank, and that every monomial factor is a
fixed f-independent record list (the #5445 record lemma).  PROOF.md gives the lift to
every column multiplicity.  Exit status 0 and the PASS marker mean every check passed;
RESULT.json is rebuilt and compared (regenerate with --write-result).
"""
import gzip
import hashlib
import importlib.util
import json
import multiprocessing
import os
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")          # one BLAS thread per worker process
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import dense as D  # noqa: E402

WORKERS = max(1, min(4, os.cpu_count() or 1))

WORD = "research/p104-helper-subspace-splits/WORD.json.gz"
AUTHOR_RESULT = "research/p104-helper-subspace-splits/RESULT.json"
COMPILER = "research/p104-native-channel/vendor/clifford_exact.py"
LIFT = "research/selected-monomial-tape-lift/lift.py"
SELECTED = "certificates/selected-result.json"
PINS = {
    WORD: "bbb072bced5824a8d9094c49be2fc51fbfdd05fb2b7dab8106e1275053075099",
    AUTHOR_RESULT: "1d92e587915052110dfb3aca8890df5afdaf496164efa5a4a52e69ceeb3c70f3",
    COMPILER: "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    LIFT: "21c77119c004a86a603cca91ce1366629431db18e9e0554942492f1b5afebe4a",
    SELECTED: "2a0220e866417774606e0f991e41b9c1d26b1f43b97857238cf478dbc7d330b5",
}
MARKER = "PASS_P104_ALLWIDTH_NATIVE_CERTIFICATE"


def need(ok, msg):
    if not ok:
        raise SystemExit("FAIL: " + msg)


def log(msg, t0):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record_key(rec):
    return (tuple(rec["matrix_rows"]), rec["offset"], tuple(rec["quadratic_rows"]), tuple(rec["linear_Z4"]), rec["phase"] % 4)


def span(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in out}
    return frozenset(out)


_W = {}


def _worker_init(frames):
    _W["frames"] = frames
    _W["ce"] = load_module(COMPILER, "p104_allwidth_candidate_compiler")


@lru_cache(maxsize=24)
def _frame_matrix(i):
    return D.circuit_matrix(D.frame_circuit(_W["frames"][i]))


@lru_cache(maxsize=None)
def _chart(i):
    return _W["ce"].canonical_frame(9, _W["frames"][i])


def _frame_check(i):
    m = D.circuit_matrix(D.frame_circuit(_W["frames"][i]))
    return bool(m.is_unitary()) and m.support_rank() == len(_W["frames"][i])


def _certify_pair(pair):
    """Dense certificate of one chart change a -> b; returns (a, b, recipe, support rank) or an error string."""
    a, b = pair
    frames, ce = _W["frames"], _W["ce"]
    recipe, _ = ce.lower_child(_chart(a).adjoint().then(_chart(b)))              # candidate only
    target = _frame_matrix(b).matmul(_frame_matrix(a).dagger()).normalize()       # Gamma_b Gamma_a^-1, dense
    got = D.circuit_matrix(D.recipe_circuit(recipe))
    if not target.equals(got):
        return f"chart change {a}->{b} differs from its lowered recipe"
    r = target.support_rank()
    if not (r == recipe["rank"] == abs(len(frames[a]) - len(frames[b]))):
        return f"rank {a}->{b}: support {r}, recipe {recipe['rank']}, invoice {abs(len(frames[a]) - len(frames[b]))}"
    return a, b, recipe, r


def check_pins(pins=PINS):
    for path, digest in pins.items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, "pinned input changed: " + path)


def result_matches(out, path):
    return json.loads(Path(path).read_text(encoding="utf-8")) == out


def main():
    t0 = time.time()
    write = "--write-result" in sys.argv
    quick = "--quick" in sys.argv          # development only: subsample the pairs; never passes RESULT.json
    check_pins()
    selected = json.loads((ROOT / SELECTED).read_text(encoding="utf-8"))
    need(selected["kappa"]["decimal"] == ".00310045" if isinstance(selected.get("kappa"), dict) else True, "selected kappa")
    need([a["id"] for a in selected["assumptions"]] == ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"],
         "the five selected assumption IDs")
    ce = load_module(COMPILER, "p104_allwidth_candidate_compiler")      # supplies candidate recipes only
    L = load_module(LIFT, "p104_allwidth_record_lift")                  # the #5445 record grammar
    w = json.loads(gzip.open(ROOT / WORD).read().decode("utf-8"))
    author = json.loads((ROOT / AUTHOR_RESULT).read_text(encoding="utf-8"))
    frames = [tuple(v) for v in w["frames"]]
    program = w["program"]
    public, live, ports = w["public"], list(w["live"]), list(w["ports"])
    need(w["schema"] == "p104-productive-source/1" and public == 748 and len(frames) == 1089, "selected word shape")
    need(len(program) == 25475 and Counter(e[0] for e in program) == Counter(ADD=21247, MOVE=3447, SCALE=757, INIT=8, COPY=8, CLEAR=8),
         "selected opcode census")
    moves = [e for e in program if e[0] == "MOVE"]
    pairs = sorted({(e[2], e[3]) for e in moves})
    paid = Counter(abs(len(frames[b]) - len(frames[a])) for _, _, a, b, _ in moves)
    need(len(pairs) == 2887 and dict(paid) == {int(k): v for k, v in author["local"]["paid"].items()}
         and sum(r * c for r, c in paid.items()) == author["local"]["paid_rank_mass"] == 6014, "paid rank histogram of the invoice")
    main_rows = set(live) | {r + 112 for r in live}
    helpers = [r for r in range(public) if r not in main_rows]
    need(len(live) == len(ports) == 104 and len(helpers) == 540, "104 live ports and 540 helpers")
    log("inputs pinned; word census agrees with the author's invoice", t0)

    # ---- frames: dense canonical charts, all unitary (worker pool)
    pool = multiprocessing.get_context("fork").Pool(WORKERS, initializer=_worker_init, initargs=(frames,))
    unitary = 0
    for i, ok in enumerate(pool.imap(_frame_check, range(len(frames)), chunksize=16)):
        need(ok, f"frame {i} is unitary with column support 2^|W|")
        unitary += 1
    log(f"{unitary} frames built densely; all unitary with column support 2^|W| ({WORKERS} workers)", t0)
    _worker_init(frames)
    frame_matrix = _frame_matrix
    chart = _chart
    ce = _W["ce"]
    f9 = D.circuit_matrix(D.fourier(9))

    def cgate(q, sgn=1):
        return D.circuit_matrix([("C", q, sgn)])

    @lru_cache(maxsize=None)
    def chart(i):
        return ce.canonical_frame(9, frames[i])

    recipes = {}
    monomials = {}        # record key -> (record, first use)

    def note_monomial(rec, use):
        k = record_key(rec)
        if k not in monomials:
            monomials[k] = (rec, use)

    def accept(result, use):
        need(not isinstance(result, str), f"{use}: {result}")
        a, b, recipe, r = result
        note_monomial(recipe["left"], (use, a, b, "left"))
        if r:
            note_monomial(recipe["right"], (use, a, b, "right"))
        recipes[a, b] = recipe
        return recipe

    # ---- every distinct paid chart change
    sample = pairs if not quick else sorted(set(pairs[::97]) | {(3, 0)})
    for n, result in enumerate(pool.imap(_certify_pair, sample, chunksize=8)):
        accept(result, "MOVE")
        if n % 500 == 499:
            log(f"{n + 1}/{len(sample)} MOVE pairs certified", t0)
    rank_pairs = Counter(recipes[p]["rank"] for p in sample)
    log(f"{len(sample)} distinct MOVE chart changes certified; ranks {dict(sorted(rank_pairs.items()))}", t0)

    # ---- helper normalizer pairs (initial -> final frame of each helper row)
    helper_pairs = [(w["initial"][r], w["final"][r]) for r in helpers]
    fresh = sorted({p for p in helper_pairs if p not in recipes})
    for result in pool.imap(_certify_pair, fresh, chunksize=4):
        accept(result, "helper")
    pool.close()
    pool.join()
    helper_profile = Counter()
    for r, (a, b) in zip(helpers, helper_pairs):
        rec = recipes[a, b]
        need(rec["rank"] == len(frames[b]) - len(frames[a]) > 0, f"helper row {r} is strictly productive")
        helper_profile[rec["rank"]] += 1
    need(dict(helper_profile) == {int(k): v for k, v in author["native"]["helpers"].items()}, "helper rank profile")
    need(not quick and len(recipes) == author["native"]["distinct_maps"] == 2923 or quick, "2923 distinct maps")
    log(f"540 helper normalizer pairs certified; profile {dict(sorted(helper_profile.items()))}", t0)

    # ---- main adapters: intrinsic charts C_q and F9 C_q^-1 against the literal boundary frames
    adapters = []
    for r, q in zip(live, ports):
        i0, i1 = w["initial"][r], w["final"][r + 112]
        need(frames[i0] == (q,), f"port {q}: literal central input frame")
        need(span(frames[i1]) == frozenset(x for x in range(512) if not D.parity(x & q)), f"port {q}: literal output hyperplane")
        cq = cgate(q)
        tests = [("source", ce.cgate(9, q, 1).adjoint().then(chart(i0)), frame_matrix(i0).matmul(cq.dagger())),
                 ("target", chart(i1).adjoint().then(ce.cgate(9, q, -1).then(ce.fourier(9))),
                  f9.matmul(cq.dagger()).matmul(frame_matrix(i1).dagger()))]
        for kind, candidate, target in tests:
            recipe, _ = ce.lower_child(candidate)
            got = D.circuit_matrix(D.recipe_circuit(recipe))
            need(recipe["rank"] == 0 and target.normalize().equals(got) and got.is_monomial(), f"port {q} {kind} adapter is a Gaussian monomial")
            note_monomial(recipe["left"], ("adapter", kind, q, "left"))
            adapters.append(recipe)
    need(len(adapters) == 208, "208 main adapters")
    payload = [[a, b, recipes[a, b]] for a, b in sorted(recipes)] + adapters
    payload_sha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    need(quick or payload_sha == author["native"]["recipe_payload_sha256"], "the certified recipes are byte-identical to the author's registered payload")
    log("208 main adapters certified; recipe payload bound to the author's registered hash", t0)

    # ---- tensor-power control on the first MOVE (event 9589: frame [] -> [11]); U acts on axes 0,1,3,
    #      its two monomial factors act on axes 0,1,2,3 (axis 2 cancels between them)
    a, b = program[9589][2], program[9589][3]
    need(program[9589][:4] == ["MOVE", 224, 3, 0] and frames[a] == () and frames[b] == (11,), "event 9589 is the first MOVE")
    rec = recipes[a, b]
    need(rec["rank"] == 1, "first MOVE has rank one")
    axes3, axes4 = (0, 1, 3), (0, 1, 2, 3)
    U3 = D.small_matrix(D.frame_circuit(frames[b]), axes3)
    xz = D.small_matrix([("X", 11), ("D", (0,) * 9, (2, 2, 0, 0, 0, 0, 0, 0, 0))], axes3)   # X_11 Z_3: X^{11} then (-1)^{x0+x1}
    ident = D.Dense(D.np.eye(8, dtype=D.np.complex128), 0)
    closed = D.Dense((1 + 1j) * ident.num + (1 - 1j) * xz.num, 1)
    need(U3.support_rank() == 1 and U3.equals(closed), "U = ((1+i) I + (1-i) X_11 Z_3)/2")
    for f in (2, 3):
        termwise = D.Dense((1 + 1j) * D.tensor_power(ident, f).num + (1 - 1j) * D.tensor_power(xz, f).num, 1)
        need(not D.tensor_power(U3, f).equals(termwise), f"termwise lift of the two-term sum differs from U^(x){f}")
    U4 = D.small_matrix(D.frame_circuit(frames[b]), axes4)
    Lm, R = D.small_matrix(D.monomial_circuit(rec["left"]), axes4), D.small_matrix(D.monomial_circuit(rec["right"]), axes4)
    Fr = D.small_matrix(D.fourier(1), axes4)
    need(U4.equals(Lm.matmul(Fr).matmul(R)), "U = L C_1 R on axes 0,1,2,3")
    need(D.tensor_power(U4, 2).equals(D.tensor_power(Lm, 2).matmul(D.tensor_power(Fr, 2)).matmul(D.tensor_power(R, 2))),
         "factorwise lift equals U^(x)2")
    log("tensor controls: factorwise lift holds at width 2, termwise lift of the closed form fails at widths 2 and 3", t0)

    # ---- record-level lift of every distinct monomial factor (#5445 grammar)
    stats, mx, tot = Counter(), Counter(), Counter()
    for n, (key, (rec, use)) in enumerate(monomials.items()):
        m = L.Monomial.from_recipe(rec)
        ok, info = L.check_monomial(m, 1, L.all_addresses(9, 1))
        need(ok, f"monomial {n} ({use}): f=1 exhaustive, {info}")
        need(info["total"] <= 171 and info["XROW"] <= 96, f"monomial {n}: within the s2 grammar bound")
        for f in (2, 3):
            ok, _ = L.check_monomial(m, f, L.random_addresses(9, f, 24, 5000 * f + n))
            need(ok, f"monomial {n} ({use}): f={f} sampled")
        for k, v in info.items():
            mx[k] = max(mx[k], v)
            tot[k] += v
        stats[info["total"]] += 1
    log(f"{len(monomials)} distinct monomial factors realized as record lists", t0)

    out = {"status": MARKER, "selected_kappa": "62009/20000000",
           "word": {"events": len(program), "frames": len(frames), "public": public, "live_ports": len(live), "helpers": len(helpers),
                    "move_occurrences": len(moves), "paid_rank_histogram": dict(sorted(paid.items())), "paid_rank_mass": 6014},
           "frames_unitary": unitary,
           "chart_changes": {"distinct_move_pairs": len(pairs), "rank_histogram": dict(sorted(rank_pairs.items())),
                             "helper_pairs": 540, "helper_rank_profile": dict(sorted(helper_profile.items())),
                             "distinct_maps": len(recipes), "main_adapters": len(adapters), "recipe_payload_sha256": payload_sha},
           "tensor_control": {"event": 9589, "frames": [a, b], "closed_form_axes": list(axes3), "factor_axes": list(axes4),
                              "factorwise_lift_width_2": "equal", "termwise_closed_form_lift_widths_2_3": "differs"},
           "monomial_factors": {"distinct": len(monomials), "max_records": dict(mx), "sum_records": dict(tot),
                                "histogram_total": dict(sorted(stats.items())), "bound_s2": 171,
                                "checks": {"f1_exhaustive": len(monomials), "sampled_f": [2, 3], "addresses_per_sample": 24}},
           "method": "dense 512x512 exact Gaussian-dyadic matrices (NumPy complex128 integers); candidate recipes from the pinned compiler; no tableau or sparse-state comparison",
           "scope": "Algebraic half of native_all_columns for the selected #5599 word, plus the record lists of its monomial factors. Physical tariff of the records, spectator layout, whole-job adapters and the other four assumptions remain inherited."}
    out = json.loads(json.dumps(out))
    path = HERE / "RESULT.json"
    if quick:
        print(json.dumps({**out, "seconds": round(time.time() - t0, 1), "QUICK": True}, indent=1))
        return
    if write:
        path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    else:
        need(result_matches(out, path), "RESULT.json differs from the fresh computation")
    print(json.dumps({**out, "seconds": round(time.time() - t0, 1)}, indent=1))
    print(f"{MARKER} pairs={len(pairs)} distinct_maps={len(recipes)} helpers=540 adapters={len(adapters)} monomials={len(monomials)} frames={unitary}")


if __name__ == "__main__":
    main()
