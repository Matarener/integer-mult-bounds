#!/usr/bin/env python3
"""Check the depth-three count cone and exceptional weighted optima.

The all-characteristic balanced construction is credited to PR4249. The new
objects are the complete count feasibility classification, exceptional Pareto
profiles and their word multiplicities. No predecessor executable is imported.
All scientific checks use explicit errors and remain active under -O.
"""

import hashlib
import heapq
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MAX_MODULUS = 128
MAX_WORD = 12 * MAX_MODULUS
EXCEPTION_WORDS = {
    2: ("21232123",),
    3: ("112113211323", "212232112233", "121332133233"),
    4: ("1112113211123233", "2122232111222333", "1121323213332333"),
}
EXPECTED_COUNTS = {2: (0, 4, 0), 3: (108, 180, 108),
                   4: (3520, 4288, 3520)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def signature(word, modulus):
    """Chronological counts (N1,N2,N3,N12,N23,N123) modulo m."""
    require(2 <= modulus <= MAX_MODULUS and len(word) <= MAX_WORD,
            "signature domain")
    a = b = c = d = e = f = 0
    for letter in word:
        if letter == "1":
            a = (a + 1) % modulus
        elif letter == "2":
            b, d = (b + 1) % modulus, (d + a) % modulus
        elif letter == "3":
            c, e, f = ((c + 1) % modulus, (e + b) % modulus,
                       (f + d) % modulus)
        else:
            raise ValueError("unknown letter")
    return a, b, c, d, e, f


def is_target(word, modulus, coefficient):
    return signature(word, modulus) == (0, 0, 0, 0, 0, coefficient % modulus)


def pareto(modulus, coefficient):
    require(2 <= modulus <= MAX_MODULUS and 1 <= coefficient < modulus,
            "target domain")
    m = modulus
    if m == 2:
        return ((2, 4, 2),)
    if m in (3, 4) and coefficient == m - 1:
        return ((2*m, m, m), (m, 2*m, m), (m, m, 2*m))
    return ((m, m, m),)


def feasible(counts, modulus, coefficient):
    require(len(counts) == 3 and all(isinstance(n, int) and n >= 0 for n in counts),
            "count domain")
    if any(n % modulus for n in counts):
        return False
    return any(all(n >= v for n, v in zip(counts, p))
               for p in pareto(modulus, coefficient))


def balanced_word(modulus, coefficient):
    """PR4249, Lemma 3, with its small and sporadic balanced witnesses."""
    require((modulus,)*3 in pareto(modulus, coefficient), "not a balanced target")
    small = {(6, 5): "111122133232123233"}
    if (modulus, coefficient) in small:
        return small[modulus, coefficient]
    m, c = modulus, coefficient
    a = 1 if c <= m-2 else next(u for u in range(2, m//2+1) if math.gcd(u, m) == 1)
    t = c if c <= m-2 else (-pow(a, -1, m)) % m
    require(1 <= a <= m//2 and 1 <= t <= m-2, "balanced parameters")
    return ("1"*a + "2" + "3"*t + "1"*(m-2*a) + "2" + "1"*a
            + "2"*(m-t-2) + "3" + "2"*t + "3"*(m-t-1))


def optimal_word(modulus, coefficient, prices):
    require(len(prices) == 3 and all(p > 0 for p in prices), "positive prices")
    profiles = pareto(modulus, coefficient)
    costs = [sum(n*p for n, p in zip(v, prices)) for v in profiles]
    chosen = costs.index(min(costs))
    if modulus == 2 or (modulus in (3, 4) and coefficient == modulus-1):
        word = EXCEPTION_WORDS[modulus][chosen]
    else:
        word = balanced_word(modulus, coefficient)
    require(tuple(word.count(s) for s in "123") == profiles[chosen], "witness counts")
    require(is_target(word, modulus, coefficient), "witness action")
    return word, costs[chosen]


def count_table(modulus):
    """Exact DP over counts <=2m and (N12,N23,N123), at most 46,656 slots."""
    require(2 <= modulus <= 4, "DP domain")
    m, cap = modulus, 2*modulus
    width = m**3
    table = {}
    for i, j, k in itertools.product(range(cap+1), repeat=3):
        values = [0]*width
        if i == j == k == 0:
            values[0] = 1
        if i:
            for code, number in enumerate(table[i-1, j, k]):
                values[code] += number
        if j:
            for code, number in enumerate(table[i, j-1, k]):
                d = code % m
                values[code-d+(d+i) % m] += number
        if k:
            for code, number in enumerate(table[i, j, k-1]):
                d, e, f = code % m, code//m % m, code//(m*m)
                values[d+m*((e+j) % m)+m*m*((f+d) % m)] += number
        expected_total = math.factorial(i+j+k)//(math.factorial(i)*math.factorial(j)*math.factorial(k))
        require(sum(values) == expected_total, "DP loses or duplicates words")
        table[i, j, k] = values
    require(len(table)*width <= 46656, "DP capacity")
    return table


def literal_census(counts, modulus):
    """Independent position-subset enumeration, with integer subword counts."""
    require(2 <= modulus <= 4 and len(counts) == 3, "census domain")
    require(all(n in (modulus, 2*modulus) for n in counts), "census counts")
    require(sum(counts) <= 4*modulus, "census capacity")
    n1, n2, n3 = counts
    length = sum(counts)
    found = [0]*modulus
    checked = 0
    for ones in itertools.combinations(range(length), n1):
        rest = tuple(p for p in range(length) if p not in ones)
        for twos in itertools.combinations(rest, n2):
            word = [3]*length
            for p in ones:
                word[p] = 1
            for p in twos:
                word[p] = 2
            one = two = pairs12 = pairs23 = triples = 0
            for letter in word:
                if letter == 1:
                    one += 1
                elif letter == 2:
                    two += 1
                    pairs12 += one
                else:
                    pairs23 += two
                    triples += pairs12
            if pairs12 % modulus == pairs23 % modulus == 0:
                found[triples % modulus] += 1
            checked += 1
    expected_total = math.comb(length, n1)*math.comb(n2+n3, n2)
    require(checked == expected_total, "census enumeration count")
    return found, checked


def finite_counts():
    report = {}
    checked_vectors = enumerated = 0
    for m in (2, 3, 4):
        table = count_table(m)
        for counts, values in table.items():
            for c in range(1, m):
                actual = all(n % m == 0 for n in counts) and values[c*m*m] > 0
                require(actual == feasible(counts, m, c), "count-cone disagreement")
                checked_vectors += 1
        profiles = ((m,m,m), (2*m,m,m), (m,2*m,m), (m,m,2*m))
        rows = []
        for counts in profiles:
            census, total = literal_census(counts, m)
            dp = [table[counts][c*m*m] for c in range(m)]
            require(census == dp, "independent census disagreement")
            rows.append({"counts": counts, "residue_counts": census, "words": total})
            enumerated += total
        require(tuple(row["residue_counts"][m-1] for row in rows[1:]) == EXPECTED_COUNTS[m],
                "exception multiplicities")
        report[str(m)] = rows
    return {"tables": report, "checked_vectors": checked_vectors,
            "enumerated_words": enumerated}


def weighted_graph(modulus, prices):
    """Independent exact positive-weight shortest paths on the full UT4 group."""
    require(2 <= modulus <= 4 and all(p > 0 for p in prices), "graph domain")
    m = modulus
    size = m**6
    distances = [None]*size
    distances[0] = 0
    queue = [(0, 0)]
    for _ in range(3*size+1):
        if not queue:
            break
        cost, code = heapq.heappop(queue)
        if distances[code] != cost:
            continue
        a, b, c = code % m, code//m % m, code//(m*m) % m
        d, e, f = code//m**3 % m, code//m**4 % m, code//m**5
        successors = (code-a+(a+1) % m,
                      code+((b+1) % m-b)*m+((d+a) % m-d)*m**3,
                      code+((c+1) % m-c)*m*m+((e+b) % m-e)*m**4
                      +((f+d) % m-f)*m**5)
        for nxt, price in zip(successors, prices):
            candidate = cost+price
            if distances[nxt] is None or candidate < distances[nxt]:
                distances[nxt] = candidate
                heapq.heappush(queue, (candidate, nxt))
    require(not queue and all(d is not None for d in distances), "graph exhaustion")
    return tuple(distances[c*m**5] for c in range(1, m))


def weighted_checks():
    cases = 0
    for m in (2, 3, 4):
        for prices in itertools.product(range(1, 5), repeat=3):
            minima = weighted_graph(m, prices)
            for c, minimum in enumerate(minima, 1):
                _, constructed = optimal_word(m, c, prices)
                require(constructed == minimum, "weighted graph disagreement")
                cases += 1
    return cases


def matvec(matrix, vector, modulus):
    return tuple(sum(matrix[i][j]*vector[j] for j in range(2)) % modulus
                 for i in range(2))


def dense_replay(word, modulus, coefficient, seed):
    """Literal dirty action on every input basis column and a mixed input."""
    maps = (((1,1),(0,1)), ((0,1),(1,1)), ((1,0),(1,1)))
    initial = [((seed == 2*i) + (seed == 8)*(i+1),
                (seed == 2*i+1) + (seed == 8)*(i*i+1)) for i in range(4)]
    initial = [tuple(x % modulus for x in row) for row in initial]
    rows = initial.copy()
    for letter in word:
        l = int(letter)
        gain = matvec(maps[l-1], rows[l-1], modulus)
        rows[l] = tuple((rows[l][j]+gain[j]) % modulus for j in range(2))
    gain = initial[0]
    for matrix in maps:
        gain = matvec(matrix, gain, modulus)
    expected = tuple((initial[3][j]+coefficient*gain[j]) % modulus for j in range(2))
    require(rows[:3] == initial[:3] and rows[3] == expected, "dirty dense replay")


def construction_checks():
    price_vectors = [(Fraction(a, 2), Fraction(b, 3), Fraction(c, 5))
                     for a, b, c in itertools.product(range(1, 5), repeat=3)]
    price_vectors += [(Fraction(1), Fraction(1), Fraction(1)),
                      (Fraction(1), Fraction(1), Fraction(7)),
                      (Fraction(7), Fraction(1), Fraction(1))]
    price_cases = dense_cases = 0
    for m in range(2, 33):
        for c in range(1, m):
            for prices in price_vectors:
                word, actual = optimal_word(m, c, prices)
                base = m*sum(prices)
                surcharge = 2*prices[1] if m == 2 else m*min(prices) if (
                    m in (3,4) and c == m-1) else 0
                require(actual == base+surcharge, "price formula")
                price_cases += 1
            words = EXCEPTION_WORDS[m] if m in (2,3,4) and c == m-1 else (word,)
            for witness in words:
                for seed in range(9):
                    dense_replay(witness, m, c, seed)
                    dense_cases += 1
    padded = 0
    for m in (2,3,4):
        for c in range(1, m):
            for profile in pareto(m, c):
                prices = tuple(Fraction(1) if profile[i] > m else Fraction(10) for i in range(3))
                word, _ = optimal_word(m, c, prices)
                for padding in itertools.product(range(3), repeat=3):
                    extra = "".join(s*(m*n) for s, n in zip("123", padding))
                    require(is_target(word+extra, m, c), "identity padding")
                    padded += 1
    return {"price_cases": price_cases, "dense_cases": dense_cases, "padding_cases": padded}


def controls():
    rejected = 0
    for m, words in EXCEPTION_WORDS.items():
        for word in words:
            for pos in range(len(word)):
                require(not is_target(word[:pos]+word[pos+1:], m, m-1), "deletion accepted")
                rejected += 1
    require(not feasible((4,2,4), 2, 1), "binary outer doublings accepted")
    rejected += 1
    for bad in ("0", "4", "x"):
        try:
            signature(bad, 3)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("bad letter accepted")
    for m, c, prices in ((1,1,(1,1,1)), (129,1,(1,1,1)), (3,0,(1,1,1)),
                          (3,3,(1,1,1)), (3,1,(0,1,1)), (3,1,(-1,1,1))):
        try:
            optimal_word(m, c, prices)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("bad domain accepted")
    return rejected


def source_hashes():
    manifest = json.loads((PACKAGE/"SOURCES.json").read_text())
    require(len(manifest["files"]) <= 10, "source manifest capacity")
    result = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (PACKAGE.parent.parent/row["path"]).read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            require(digest == row["sha256"], "input hash mismatch")
            result[row["path"]] = digest
    files = sorted(PACKAGE.iterdir())
    require(len(files) == 6, "package inventory")
    for path in files:
        require(path.is_file() and not path.is_symlink(), "package entry")
        result["package/"+path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    require(len(sys.argv) == 1, "usage: verify.py")
    hashes = source_hashes()
    report = {"claim_type": "scoped proof with finite certificate",
              "finite_counts": finite_counts(), "construction": construction_checks(),
              "negative_controls": controls(), "weighted_graph_cases": weighted_checks(),
              "sha256": hashes}
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":"))
    print(encoded)
    print("PASS_CHAIN_TARIFF", json.dumps({
        "enumerated_words": report["finite_counts"]["enumerated_words"],
        "weighted_graph_cases": report["weighted_graph_cases"],
        **report["construction"], "negative_controls": report["negative_controls"],
        "receipt_sha256": hashlib.sha256(encoded.encode()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
