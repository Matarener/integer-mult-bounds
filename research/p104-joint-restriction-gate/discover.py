"""Build a flow certificate. This search is not a replay dependency.

Use PyMaxflow and NetworkX. Ali Romman with Codex assistance. Apache-2.0.
"""
from collections import defaultdict
import gzip
import json
import maxflow
import model as M


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--one-percent", action="store_true")
    args = parser.parse_args()
    kappa = M.LARGE_TARGET if args.one_percent else M.KAPPA
    word = M.source()
    groups, queries = M.supports(word)
    costs, rewards, constant = M.invoice(word, groups, queries, kappa)
    size, main_mask = len(groups), (1 << 104)-1
    nodes = []

    def visit(yes, no):
        index = len(nodes)
        nodes.append(None)
        if yes & main_mask == main_mask:
            nodes[index] = {"empty_main": True}
            return index
        terms = M.relaxation(queries, rewards, yes, no)
        graph = maxflow.Graph[int](size+len(terms), sum(k.bit_count() for k, _ in terms))
        graph.add_nodes(size+len(terms))
        for j, cost in enumerate(costs):
            if not (yes | no) >> j & 1:
                graph.add_tedge(j, 0, cost)
        for i, (key, reward) in enumerate(terms, size):
            graph.add_tedge(i, reward, 0)
            for j in M.bits(key):
                graph.add_edge(i, j, 10**17, 0)
        flow = graph.maxflow()
        upper = constant + sum(v for _, v in terms) - flow - sum(costs[j] for j in M.bits(yes))
        if upper < 0:
            residual = graph.get_nx_graph()
            allocations = []
            for i, (key, _) in enumerate(terms):
                for j in M.bits(key):
                    amount = residual.get_edge_data(j, size+i, {}).get("weight", 0)
                    if amount:
                        allocations.append([i, j, int(amount)])
            M.need(sum(a for _, _, a in allocations) == flow, "Exported dual flow")
            nodes[index] = {"allocations": allocations, "upper": upper}
            return index
        selected = yes | sum(1 << j for j in range(size)
                             if not (yes | no) >> j & 1 and graph.get_segment(j) == 0)
        bad = defaultdict(float)
        for q, reward in zip(queries, rewards):
            a, b = q["input"], q["output"]
            if a & no or b & no:
                continue
            common = (a & b) & ~yes
            if common & selected != common or a & selected == a or b & selected == b:
                continue
            missing = (a | b) & ~selected
            for j in M.bits(missing):
                bad[j] += reward / missing.bit_count() * (2 if j < 104 else 1)
        if bad:
            split = max(bad, key=lambda j: (bad[j], costs[j], -j))
        else:
            free = main_mask & ~(yes | no)
            M.need(bool(free) and not no & main_mask, "Remaining main branch")
            split = next(M.bits(free))
        kept = visit(yes, no | (1 << split))
        removed = visit(yes | (1 << split), no)
        nodes[index] = {"split": split, "kept": kept, "removed": removed}
        return index

    root = visit(0, 0)
    certificate = {"schema": 1, "kappa": str(kappa), "scale": M.SCALE,
                   "groups": len(groups), "queries": len(queries), "root": root, "nodes": nodes}
    data = json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode()
    filename = "ONE-PERCENT.json.gz" if args.one_percent else "CERTIFICATE.json.gz"
    (M.HERE / filename).write_bytes(gzip.compress(data, mtime=0))
    print("CERTIFICATE", len(nodes), "nodes", len(data), "plain bytes")


if __name__ == "__main__":
    main()
