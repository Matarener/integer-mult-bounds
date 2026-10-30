"""Check the exact source, rational tariff and integer dual certificate.

This checker does not import a flow solver. Apache-2.0.
Ali Romman with substantial OpenAI Codex assistance.
"""
from collections import Counter
from copy import deepcopy
import gzip
import json
import model as M


def integer(value):
    M.need(type(value) is int, "Strict integer")
    return value


def check(certificate, groups, queries, costs, rewards, constant, kappa=M.KAPPA):
    M.need(integer(certificate["schema"]) == 1, "Certificate schema")
    M.need(certificate["kappa"] == str(kappa), "Exact tested saving")
    M.need(integer(certificate["scale"]) == M.SCALE, "Tariff scale")
    M.need(integer(certificate["groups"]) == len(groups), "Group count")
    M.need(integer(certificate["queries"]) == len(queries), "Query count")
    nodes, seen, uppers = certificate["nodes"], set(), []
    main_mask = (1 << 104)-1

    def visit(index, yes, no):
        index = integer(index)
        M.need(0 <= index < len(nodes) and index not in seen, "Complete tree")
        seen.add(index)
        node = nodes[index]
        if "split" in node:
            M.need(set(node) == {"split", "kept", "removed"}, "Branch fields")
            split = integer(node["split"])
            M.need(0 <= split < len(groups) and not (yes | no) >> split & 1,
                   "Fresh branch variable")
            visit(node["kept"], yes, no | (1 << split))
            visit(node["removed"], yes | (1 << split), no)
            return
        if "empty_main" in node:
            M.need(node == {"empty_main": True} and yes & main_mask == main_mask,
                   "Empty-main exclusion")
            return
        M.need(set(node) == {"allocations", "upper"}, "Leaf fields")
        terms = M.relaxation(queries, rewards, yes, no)
        sent, received, edges = Counter(), Counter(), set()
        for row in node["allocations"]:
            M.need(type(row) is list and len(row) == 3, "Flow row")
            i, j, amount = map(integer, row)
            M.need(0 <= i < len(terms) and 0 <= j < len(groups), "Flow index")
            M.need(amount > 0 and (i, j) not in edges, "Unique positive allocation")
            edges.add((i, j))
            M.need(terms[i][0] >> j & 1 and not (yes | no) >> j & 1,
                   "Required free group")
            sent[i] += amount
            received[j] += amount
        M.need(all(amount <= terms[i][1] for i, amount in sent.items()), "Source capacity")
        M.need(all(amount <= costs[j] for j, amount in received.items()), "Group capacity")
        upper = constant + sum(v for _, v in terms) - sum(sent.values())
        upper -= sum(costs[j] for j in M.bits(yes))
        M.need(upper == integer(node["upper"]) and upper < 0, "Strict negative upper bound")
        uppers.append(upper)

    visit(certificate["root"], 0, 0)
    M.need(seen == set(range(len(nodes))), "No unused proof nodes")
    return {"nodes": len(nodes), "priced_leaves": len(uppers),
            "largest_upper_numerator": max(uppers), "scale": M.SCALE}


def controls(certificate, data):
    cases = []
    def edit(label, change):
        mutant = deepcopy(certificate)
        change(mutant)
        cases.append((label, mutant))
    leaf = next(i for i, node in enumerate(certificate["nodes"]) if "allocations" in node)
    edit("wrong-saving", lambda c: c.update(kappa=".0034"))
    edit("missing-branch", lambda c: c["nodes"][0].update(removed=c["nodes"][0]["kept"]))
    edit("wrong-upper", lambda c: c["nodes"][leaf].update(upper=0))
    edit("negative-flow", lambda c: c["nodes"][leaf]["allocations"][0].__setitem__(2, -1))
    edit("over-capacity", lambda c: c["nodes"][leaf]["allocations"][0].__setitem__(2, 10**30))
    edit("boolean-flow", lambda c: c["nodes"][leaf]["allocations"][0].__setitem__(2, True))
    edit("false-empty-main", lambda c: c["nodes"].__setitem__(leaf, {"empty_main": True}))
    for label, mutant in cases:
        try:
            check(mutant, *data)
        except ValueError:
            continue
        raise ValueError("Control accepted: " + label)
    return [label for label, _ in cases]


def main():
    word = M.source()
    groups, queries = M.supports(word)
    source_cost = json.loads((M.HERE / "inputs/PR5827-RESULT.json").read_text())["complete_cost"]
    signed = Counter({int(k): v for k, v in source_cost["targets"].items()})
    signed.subtract({int(k): v for k, v in source_cost["paid"].items()})
    from fractions import Fraction
    lower = sum(n*M.power_bounds(r, Fraction(".00312476680"))[0 if n > 0 else 1]
                for r, n in signed.items() if n) / 18
    M.need(lower > 0, "Published source passes its own moment gate")
    tests = []
    for filename, kappa in (("CERTIFICATE.json.gz", M.KAPPA),
                            ("ONE-PERCENT.json.gz", M.LARGE_TARGET)):
        costs, rewards, constant = M.invoice(word, groups, queries, kappa)
        certificate = json.loads(gzip.decompress((M.HERE / filename).read_bytes()))
        data = (groups, queries, costs, rewards, constant, kappa)
        test = check(certificate, *data)
        test.update(kappa=str(kappa), controls=controls(certificate, data))
        tests.append(test)
    result = {"groups": len(groups), "queries": len(queries),
              "program_events": len(word["program"]),
              "source_margin_lower_numerator": (M.SCALE*lower).numerator // (M.SCALE*lower).denominator,
              "tests": tests}
    expected = json.loads((M.HERE / "RESULT.json").read_text())
    M.need(result == expected, "Complete expected receipt")
    print(json.dumps(result, sort_keys=True))
    print("PASS_P104_JOINT_RESTRICTION_GATE")


if __name__ == "__main__":
    main()
