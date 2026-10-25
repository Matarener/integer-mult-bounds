#!/usr/bin/env python3
"""Bounded exact checks for the written integer outer join.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
These are algebra/arithmetic checks, not execution of the physical tensor.
"""
import argparse
import ast
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import io
from itertools import product
import json
from math import gcd, isqrt, prod
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
BUNDLE_SHA256 = "a93f3e4df06a8ee18c69f68697cec463bbb86ddff642cc1df652d87ba642f046"
MANIFEST_SHA256 = "cc5c879b5c28c9d2d4191c1ac2c5563213c1b58ffd1e4d25a3e6c0a6a6dbeb18"
SOURCE_PINS = {
    "f687fa171ef760fa98a4be1289717b47dd4ee0b3": {
        "research/physical-gaussian-tensor/PROOF.md": "1e3450344552e744e0187cf1115c7b470bbe1babc9a2414586ff8ffc8f84476e",
        "research/physical-gaussian-tensor/tensor_plan.py": "474730f42fcd2bd24720af4e08c71fb51cc374c3e16b8b6d7e565900f1a9e7c3",
        "research/physical-gaussian-tensor/tensor_engine.py": "1a5a766426b16718e168619d5988cc18711b4574f0041ec7f3877c1024de59d1",
        "research/physical-gaussian-tensor/tensor_word.py": "6ad8a2b9c9661ac42c727caefd8b4c4acf9f8bffedb5fe5f8a6e74675e85aa26",
        "research/physical-gaussian-tensor/ARITHMETIC.md": "bf809380781faf39227b363aa1abd388694a4c26cac48548a3595d1aa0673440",
    },
    "12fa8c5c844be21bfefb38a19503fbd867a11244": {
        "research/crt-address-streams/PROOF.md": "7b141475955cc372c5936118ff16e8748b589b93de2d26b76da28feec9b45de4",
        "research/crt-address-streams/crt_converter.py": "b81fe8b266af59f5c5354cf53276c36a16b3a4e5a2ec015e8c8969ee22a17fea",
        "research/physical-synthetic-fourier/PROOF.md": "b2a6da7501a04848d0a42930da91f15b6653fccf42ed7a018cf602fc12a1d4f7",
        "research/physical-synthetic-fourier/fourier_engine.py": "7ef404f4a758a67d9ebe111bbedf501aa8bab223c54d61704cdec629c1f07ad9",
    },
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def checked_blob(raw, expected, label):
    need(sha256(raw).hexdigest() == expected, label)
    return raw


def bundle_inventory(raw, manifest):
    expected = {row["path"]: row for row in manifest["files"]}
    need(len(expected) == len(manifest["files"]) == 35, "complete 35-file source references")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        for entry in archive.getmembers():
            path = PurePosixPath(entry.name)
            need(entry.isfile() and not path.is_absolute() and ".." not in path.parts
                 and "\\" not in entry.name and path.as_posix() == entry.name
                 and entry.name not in files and entry.name in expected,
                 "unique regular declared source reference")
            row = expected[entry.name]
            need(entry.size == row["bytes"] and entry.size < 2**20, "source reference extent")
            value = archive.extractfile(entry).read()
            need(len(value) == entry.size, "complete source reference bytes")
            files[entry.name] = checked_blob(value, row["sha256"], "source reference digest")
    need(set(files) == set(expected), "no omitted source reference")
    return files


def source_contracts(files):
    tensor = ast.parse(files["research/physical-gaussian-tensor/tensor_plan.py"])
    calls = {ast.unparse(node) for node in ast.walk(tensor) if isinstance(node, ast.Call)}
    for expression in ("self.keep('dimensions', Count(axes))", "self.dimensions.increment()",
                       "self.keep('d', Count(self.dimensions))", "self.d.increment()",
                       "self.keep('gamma', Count.product(self.dimensions, scale))",
                       "scale.multiply_small(2)", "scale.add(self.j)", "scale.increment()"):
        need(expression in calls, "literal TensorPlan dimension/normalization contract")
    converter = ast.parse(files["research/crt-address-streams/crt_converter.py"])
    methods = [node for node in ast.walk(converter)
               if isinstance(node, ast.FunctionDef) and node.name == "run_plan"]
    expected = ast.parse("""def run_plan(self, payload, plan, rows, inverse=False, record_bits=None):
    return self.run(payload, None, plan.dimensions, plan.p,
        plan.record_bits if record_bits is None else record_bits, rows,
        inverse=inverse, tensor_plan=plan)
""").body[0]
    need(len(methods) == 1 and ast.dump(methods[0]) == ast.dump(expected),
         "actual inverse CRT opaque-width override")
    need(b"gamma=D(2u+ceil(log2(32p))+1)" in files["research/physical-gaussian-tensor/PROOF.md"],
         "Gaussian complete inverse normalization reference")
    need(b"F+ F- = F- F+ = I/M" in files["research/physical-synthetic-fourier/PROOF.md"],
         "both synthetic Fourier transforms normalized")
    need(b"three completed Karatsuba children" in files["research/physical-ring-product/word_product.py"],
         "actual scalar three-child continuation")
    need(b"[y-y^(21/40),y]" in
         files["references/semantic-bulk/rad20/reports/review-reusable-banded-inverse.md"],
         "retained short-interval prime premise")
    return ["TensorPlan_dimensions_and_gamma", "CRT_explicit_record_width",
            "normalized_Fourier_pair", "scalar_Karatsuba_continuation", "BHP_21_over_40"]


def frozen_sources():
    pins = json.loads((HERE / "OUTER-PINS.json").read_bytes())
    need(pins["archive"] == "frozen/outer-source/SOURCE-CONTRACTS.tar.gz"
         and pins["archive_sha256"] == BUNDLE_SHA256 and pins["bytes"] == 116428
         and pins["manifest"] == "frozen/outer-source/MANIFEST.json"
         and pins["manifest_sha256"] == MANIFEST_SHA256 and pins["files"] == 35,
         "fixed outer proof-reference bundle")
    for relative in (pins["archive"], pins["manifest"]):
        need((HERE / relative).is_file() and not (HERE / relative).is_symlink(),
             "regular proof-reference artifact")
    manifest = json.loads(checked_blob((HERE / pins["manifest"]).read_bytes(),
                                      MANIFEST_SHA256, "immutable reference manifest"))
    need(manifest["canonical_base"] == "12fa8c5c844be21bfefb38a19503fbd867a11244"
         and manifest["gaussian_head"] == "f687fa171ef760fa98a4be1289717b47dd4ee0b3",
         "exact source commit family")
    compressed = checked_blob((HERE / pins["archive"]).read_bytes(), BUNDLE_SHA256,
                              "immutable reference archive")
    need(len(compressed) == 116428, "fixed compressed reference extent")
    raw = gzip.decompress(compressed)
    need(len(raw) < 2**20, "bounded reference archive")
    files = bundle_inventory(raw, manifest)
    overlap = 0
    for paths in SOURCE_PINS.values():
        for path, digest in paths.items():
            if path in files:
                checked_blob(files[path], digest, "independent cited source pin")
                overlap += 1
    need(overlap == 7, "all seven shared independent source references")
    facts = source_contracts(files)
    reduced = dict(manifest, files=manifest["files"][:-1])
    for label, check in (
            ("omitted_source_manifest_row", lambda: bundle_inventory(raw, reduced)),
            ("changed_source_bytes", lambda: checked_blob(
                files["research/physical-gaussian-tensor/tensor_plan.py"]+b"\n",
                SOURCE_PINS["f687fa171ef760fa98a4be1289717b47dd4ee0b3"][
                    "research/physical-gaussian-tensor/tensor_plan.py"], "changed source"))):
        try:
            check()
        except ValueError:
            pass
        else:
            raise ValueError("accepted invalid source binding: "+label)
    return {"archive_sha256": BUNDLE_SHA256, "manifest_sha256": MANIFEST_SHA256,
            "reference_files": len(files), "source_contract_checks": facts,
            "controls": ["omitted_source_manifest_row", "changed_source_bytes"],
            "scope": "Exact proof/constructor references; no source imports or physical execution"}


def trim(a):
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def divide_exact(a, b):
    """Monic integer polynomial division, coefficients in increasing order."""
    a = list(a)
    need(b[-1] == 1, "monic polynomial divisor")
    q = [0] * (len(a) - len(b) + 1)
    while len(a) >= len(b):
        k, c = len(a) - len(b), a[-1]
        q[k] = c
        for j, v in enumerate(b):
            a[k + j] -= c * v
        trim(a)
    need(a == [0], "exact cyclotomic division")
    return trim(q)


def roots_of_unity(n):
    """Exact powers of z in Z[z]/Phi_n, with no floating point."""
    phis = {}
    for k in range(1, n + 1):
        if n % k:
            continue
        polynomial = [-1] + [0] * (k - 1) + [1]
        for d, earlier in phis.items():
            if k % d == 0:
                polynomial = divide_exact(polynomial, earlier)
        phis[k] = polynomial
    phi = phis[n]
    degree = len(phi) - 1
    one = (1,) + (0,) * (degree - 1)
    powers = [one]
    for _ in range(n):
        row = [0] + list(powers[-1])
        high = row.pop()
        for i in range(degree):
            row[i] -= high * phi[i]
        powers.append(tuple(row))
    need(powers[-1] == one, "root order divides n")
    for d in range(1, n):
        if n % d == 0:
            need(powers[d] != one, "primitive root order")
    need(all(sum(row[i] for row in powers[:-1]) == 0 for i in range(degree)),
         "exact character orthogonality")
    return powers[:-1], phi


def normalization(shape, targets):
    """Every bilinear coefficient of RF+((RF-x)(RF-y))."""
    S = prod(shape)
    need(len(shape) == len(targets) and
         all(gcd(s, t) == 1 for s, t in zip(shape, targets)), "unit R map")
    roots, phi = roots_of_unity(S)
    addresses = list(product(*(range(s) for s in shape)))
    zero = (0,) * len(roots[0])
    hit = (S,) + zero[1:]
    def triple(a, b, z, final_R=True, final_sign=1):
        answer = [0] * len(zero)
        for j in addresses:
            exponent = sum((S // s) * jv *
                           (final_sign * (t if final_R else 1) * zv - t * (av + bv))
                           for s, t, jv, av, bv, zv in zip(shape, targets, j, a, b, z))
            row = roots[exponent % S]
            for i, value in enumerate(row):
                answer[i] += value
        return tuple(answer)
    cases = 0
    controls = {"omitted_final_R": False, "wrong_final_Fourier_sign": False,
                "S_instead_of_S_squared": False}
    for a in addresses:
        for b in addresses:
            location = tuple((x + y) % s for x, y, s in zip(a, b, shape))
            for z in addresses:
                expected = hit if z == location else zero
                value = triple(a, b, z)
                need(value == expected, "complete bilinear Fourier coefficient")
                cases += 1
                if not controls["omitted_final_R"]:
                    controls["omitted_final_R"] = triple(a, b, z, False) != expected
                if not controls["wrong_final_Fourier_sign"]:
                    controls["wrong_final_Fourier_sign"] = triple(a, b, z, True, -1) != expected
                if z == location:
                    # The three normalized transforms contribute S^-3.
                    controls["S_instead_of_S_squared"] |= Q(value[0], S**2) != 1
    return {"source_axes": shape, "target_axes": targets, "S": S,
            "cyclotomic_polynomial": phi, "bilinear_coefficients": cases,
            "mutation_witnesses": controls}


def crt_map(shape):
    prefix, mus = 1, []
    for s in shape:
        need(s >= 3 and s % 2 == 1 and gcd(prefix, s) == 1, "coprime odd CRT axes")
        mus.append(pow(prefix, -1, s))
        prefix *= s
    mapping = [tuple(mu * k % s for mu, s in zip(mus, shape)) for k in range(prefix)]
    need(len(set(mapping)) == prefix, "all CRT coefficient addresses")
    for k in range(prefix):
        for l in range(prefix):
            need(tuple((a + b) % s for a, b, s in zip(mapping[k], mapping[l], shape))
                 == mapping[(k + l) % prefix], "CRT convolution homomorphism")
    return mapping, mus


def rounded(x):
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def recovery():
    cases = 0
    for shape in ((3, 5), (3, 7), (5, 7)):
        mapping, _ = crt_map(shape)
        S = len(mapping)
        for b in (2, 3, 5):
            B = 1 << b
            m = (S + 1) // 2
            need(2 * m - 2 < S, "no cyclic alias")
            for mode in range(3):
                x = [B - 1 if mode == 0 else (i * 3 + mode) % B for i in range(m)]
                y = [B - 1 if mode == 0 else (i * 5 + 2 * mode) % B for i in range(m)]
                convolution = [0] * S
                for i, a in enumerate(x):
                    for j, c in enumerate(y):
                        convolution[i + j] += a * c
                tensor = {mapping[k]: convolution[k] for k in range(S)}
                restored = []
                for k, address in enumerate(mapping):
                    exact = Q(tensor[address], S * S * (1 << (2*b + 4)))
                    scale = S * S * (1 << (2*b + 4))
                    error = Q(1 if k % 2 else -1, 4)
                    recovered = rounded(scale * exact + error)
                    need(recovered == convolution[k] and rounded(error) == 0,
                         "integer and imaginary recovery under strict margin")
                    restored.append(recovered)
                carry, digits = 0, []
                for c in restored:
                    digits.append((c + carry) % B)
                    carry = (c + carry) // B
                while carry:
                    digits.append(carry % B)
                    carry //= B
                value = sum(digit * B**i for i, digit in enumerate(digits))
                need(value == sum(a * B**i for i, a in enumerate(x)) *
                     sum(a * B**i for i, a in enumerate(y)), "complete carry recovery")
                cases += 1
    # A nonproduction format witness: 18 on a p-grid cannot use p+2 signed bits.
    p = 12
    need(18 * (1 << p) >= 1 << (p + 1), "old disk-grid width rejects scaled integer")
    # Degree four aliases to one at cyclic length three.
    need(4 % 3 != 4, "insufficient padding mutation witness")
    need(rounded(Q(1, 2)) != 0, "half-unit error cannot certify unique rounding")
    try:
        crt_map((3, 3))
    except ValueError:
        pass
    else:
        raise ValueError("accepted duplicate CRT prime")
    return {"complete_round_scale_CRT_carry_cases": cases,
            "controls": ["disk_width_after_scaling", "cyclic_alias_without_padding",
                         "non_strict_half_unit_margin", "duplicate_CRT_prime"]}


def exact_arithmetic():
    C = Q("0.001730980255989036959962")
    sigma, alpha, eta = Q("0.99826995"), Q("0.99827"), Q(1, 10**6)
    tau, epsilon = Q(332353, 332929), Q(997, 1000)
    need(1-C < sigma and tau < sigma < alpha < 1, "root strict exponent ordering")
    internal, leaf = (1-eta)*sigma + eta*tau, (1-eta)*sigma + eta
    need(internal < alpha and leaf < alpha, "complete recurrence exponent margins")
    need(500*(1-alpha) < 1 and Q("0.998") < alpha, "fallback and reserved bill")
    beta = 1-epsilon*(1-tau)
    Phi = 1-epsilon*(1-alpha)
    kappa = Q(1, 580)
    need(beta < Phi and Q("0.9981") < Phi and Q(3, 5) < Phi, "complete outer cost gaps")
    need(epsilon < Phi and 1-Phi > kappa, "strict target kappa allowance")
    need(3**5 < 2**8, "log2(3) < 8/5 exact scalar exponent")
    need(not tau < 1-C, "raw complex moment endpoint fails tau ordering")
    old_Phi = 1-epsilon*(1-Q("0.99827101"))
    need(not kappa < 1-old_Phi, "old root does not certify this kappa")
    # Uniform gamma/p bound in blocks 2^(1000m)<=p<2^(1000(m+1)), m>=7.
    gamma_ratio = Q(2, 2**7) + Q(8007, 2**21)
    need(gamma_ratio < Q(1, 12), "eventual gamma <= p/12")
    need(9007 < 8*8007, "logarithmic gamma term decreases between blocks")
    margins = []
    for b in (32, 33):
        p, gamma = 6*b, b//2
        need(216*b**3 + 12*b + 32 <= 2**b, "polynomial error coefficient bound")
        E = Q(7, 2**(5*b-gamma))
        h = Q(1, 2**p)
        scale = Q(2**(4*b+10), b*b)
        output_error = scale * (Q(3, 2)*E + E*E + 2*h)
        input_norm = (Q(1, 4)+E)**2 + 2*h
        need(E < Q(1, 256) and input_norm < Q(1, 2) and output_error < Q(1, 2),
             "sufficient recovery and third-call admission margins")
        margins.append({"b": b, "gamma_cap": gamma, "E_upper": str(E),
                        "scaled_error_upper": str(output_error),
                        "third_input_norm_upper": str(input_norm)})
    need(Q(33, 32)**3 < 2, "polynomial coefficient bound propagates")
    # For b -> b+2 the three positive scaled error terms decrease by at least
    # factors 1/2, 1/1024, 1/16, respectively, even before the b^-2 decrease.
    need(2**8 * Q(1, 2**9) == Q(1, 2) and
         2**8 * Q(1, 2**18) == Q(1, 1024) and
         2**8 * Q(1, 2**12) == Q(1, 16), "all-b recovery bound propagation")
    D, u, j = 4, 4, 13
    gamma = D*(2*u+j+1)
    need(gamma == 88 and gamma != 2*D*u and gamma != (D-1)*(2*u+j+1),
         "normalization includes inverse factors and actual dimensions")
    need(Q(2**(2*D*u), 2**gamma) != 1, "old restoration produces the wrong amplitude")
    gate_cases = []
    for b, gamma, H in ((32, 8, 2**8), (48, 16, 2**12), (64, 24, 2**20-1)):
        log_H = (H-1).bit_length()
        need(b >= gamma+log_H+9, "encoded recovery gate")
        E = Q(H, 2**(5*b-gamma))  # T<=2^b, p=6b.
        h = Q(1, 2**(6*b))
        scale = 2**(4*b+4)  # S<T<=2^b.
        exact_bound = scale*(2*E+2*h)
        coarse_bound = Q(64*H, 2**(b-gamma))
        need(E < Q(1, 256) and exact_bound <= coarse_bound <= Q(1, 8),
             "outer join encoded recovery gate bound")
        need(6*b >= gamma+b+log_H+8, "recovery gate also supplies TensorPlan margin")
        gate_cases.append({"b": b, "gamma": gamma, "H": H, "ceil_log2_H": log_H,
                           "coarse_recovery_upper": str(coarse_bound)})
    return {"complex_rate_lower": str(C), "sigma": str(sigma), "tau": str(tau),
            "alpha": str(alpha), "eta": str(eta), "internal": str(internal),
            "leaf": str(leaf), "beta": str(beta), "Phi": str(Phi), "kappa": str(kappa),
            "saving_gap": str(1-Phi-kappa), "router_gap": str(Phi-beta),
            "gamma_ratio_upper_for_p_ge_2_pow_7000": str(gamma_ratio),
            "sufficient_margin_base_cases_not_production_plans": margins,
            "encoded_recovery_gate_cases_not_production_plans": gate_cases,
            "controls": ["sigma_without_router_slack", "old_root_target_kappa",
                         "omitted_inverse_normalization", "axes_dimensions_off_by_one"]}


def prime_fixture():
    D, d, targets = 4, 5, (2048, 2048, 4096, 4096)
    used, sources = set(), []
    for t in targets:
        lower, upper = Q((2*d-1)*t, 2*d), Q((4*d-1)*t, 4*d)
        selected = None
        for s in range(lower.numerator//lower.denominator+1, (upper.numerator-1)//upper.denominator+1):
            if s not in used and s >= 3 and s % 2 and all(s % k for k in range(3, isqrt(s)+1, 2)):
                selected = s
                break
        need(selected is not None, "bounded distinct-prime fixture")
        s = selected
        need(lower < s < upper and 4*d*(t-s) > s and (2*d-1)*(t-s) < s,
             "interior prime interval implies actual TensorPlan ratio guards")
        used.add(s)
        sources.append(s)
    need(prod(sources)*2 > prod(targets), "complete prime product exceeds T/2")
    return {"scope": "finite interval and ratio fixture, not a production TensorPlan",
            "dimensions": D, "d": d, "source_axes": sources, "target_axes": targets}


def verify_sources(repo):
    rows = []
    for commit, paths in SOURCE_PINS.items():
        for path, expected in paths.items():
            raw = subprocess.run(["git", "-C", str(repo), "show", commit+":"+path],
                                 check=True, stdout=subprocess.PIPE).stdout
            need(sha256(raw).hexdigest() == expected, "exact cited source: "+path)
            rows.append({"commit": commit, "path": path, "sha256": expected})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path, help="Additionally hash the nine cited exact Git source blobs")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    bundle = frozen_sources()
    reports = [normalization(s, t) for s, t in
               (((3,), (4,)), ((5,), (8,)), ((3, 5), (4, 8)), ((3, 7), (4, 8)))]
    controls = {name: any(row["mutation_witnesses"][name] for row in reports)
                for name in reports[0]["mutation_witnesses"]}
    need(all(controls.values()), "normalization mutants distinguished")
    arithmetic = exact_arithmetic()
    recovered = recovery()
    receipt = {
        "status": "PASS_EXACT_OUTER_ALGEBRA_AND_ARITHMETIC_NOT_PHYSICAL_EXECUTION",
        "normalization": reports, "normalization_controls": controls,
        "arithmetic": arithmetic, "recovery": recovered, "prime_interval_fixture": prime_fixture(),
        "immutable_source_references": bundle,
        "source_pins": SOURCE_PINS,
        "source_blob_checks": verify_sources(args.source_repo) if args.source_repo else [],
        "source_blob_checks_performed": args.source_repo is not None,
        "controls": list(controls) + arithmetic["controls"] + recovered["controls"] + bundle["controls"],
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "Complete bilinear coefficient checks only on four stated finite groups; exact rational exponent and sufficient-margin certificates. Written eventual prime supply, Gaussian/CRT/Fourier source contracts, replacement-root binding, tape execution and all-size restoration are not proved by this checker.",
    }
    if args.out:
        args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(receipt["status"], "bilinear coefficients",
          sum(row["bilinear_coefficients"] for row in reports), "controls", len(receipt["controls"]))


if __name__ == "__main__":
    main()
