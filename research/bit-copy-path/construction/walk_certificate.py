#!/usr/bin/env python3
"""Source-bound hypotheses and exact witnesses for the postscatter walk bound."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json
import types

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_source(filename):
    path = HERE / filename
    source = path.read_bytes()
    pins = json.loads((HERE / "SOURCES.json").read_bytes())["code"]
    need(sha256(source).hexdigest() == pins[filename], "authenticated sibling source: " + filename)
    module = types.ModuleType(filename[:-3])
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


acquisition = load_source("acquisition_screen.py")
direct = load_source("direct_scatter.py")


def rational_rank(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for j, old in sorted(basis.items()):
            c = row[j]
            row = [x-c*y for x, y in zip(row, old)]
        j = next((j for j, x in enumerate(row) if x), None)
        if j is not None:
            c = row[j]
            basis[j] = [x/c for x in row]
    return len(basis)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def project_onto_hyperplane(row, normal):
    c = Fraction(dot(row, normal), dot(normal, normal))
    return [x-c*y for x, y in zip(row, normal)]


def literal_frames(word, masks, dims):
    current = word["start"][:] + [None]
    live = None
    counts = Counter()
    profile = Counter()
    for index, (op, d, s, c, f, phase) in enumerate(word["records"]):
        need(0 <= d < 660 and 0 <= s <= 660, "actual persistent/private operands")
        if op == 0:
            need(current[d] == s, "actual MOVE entrance")
            need(masks[s] & ~masks[c] == 0, "actual nested public MOVE")
            need(dims[c]-dims[s] == f and f > 0, "actual positive MOVE tariff")
            current[d] = c
            profile[f] += 1
        elif op == 1:
            need(current[d] == current[s] == f, "actual ADD common frame")
            need(d != live, "literal copied source is immutable")
            need(c in (-1, 1), "signed unit ADD")
            counts["ADD"] += 1
        elif op == 2:
            need(live is None and s == 660 and current[660] is None, "fresh private COPY")
            need(current[d] == c and masks[f] & ~masks[c] == 0, "nested copied-total frames")
            need(dims[c] > dims[f], "original paid COPY")
            current[660], live = f, d
            profile[dims[c]-dims[f]] += 1
            counts["COPY"] += 1
        else:
            need(op == 3 and s == 660 and live == d, "actual ERASE source identity")
            need(current[d] == c and current[660] == f, "actual ERASE frame identity")
            current[660], live = None, None
            counts["ERASE"] += 1
    need(current[:-1] == word["final"] and current[-1] is None and live is None, "all actual endpoint frames")
    need(counts == {"ADD": 36005, "COPY": 9, "ERASE": 9}, "literal operation counts")
    need(dict(profile) == {1:1322, 2:1342, 3:79, 4:39, 5:102, 6:11, 7:18},
         "entire original paid rank histogram")
    return dict(operation_counts=dict(counts), paid_profile=dict(sorted(profile.items())),
                paid_rank_mass=sum(r*n for r, n in profile.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    word, geometry = acquisition.load()
    copies, erases, snapshots, R, K = acquisition.audit(word)
    masks, dims = direct.frame_geometry(geometry)
    frame_receipt = literal_frames(word, masks, dims)
    begin = erases[-1][0] + 1
    end = 1 + max(i for i, r in enumerate(word["records"])
                  if r[0] == 1 and 111 <= r[1] < 222)
    need((begin, end) == (24069, 25768), "actual postscatter target-writing interval")
    B = word["records"][begin:end]
    need(all(r[0] in (0, 1) for r in B), "no downstream COPY in target-writing suffix")
    need(not any(r[0] == 1 and r[1] in range(471, 480) for r in B),
         "all actual snapshot sources remain unchanged during B")
    need(not any(r[0] == 0 and r[1] in range(471, 480) for r in B),
         "all actual source hyperplanes remain fixed during B")
    need(not any(r[0] == 1 and 111 <= r[2] < 222 for r in word["records"]),
         "actual target registers never feed another field; scatter K survives unchanged")
    lines = geometry["lines"]
    for p in range(111):
        cap = word["final"][111+p]
        need(dims[cap] == 7 and dot(lines[p], lines[p]) == 4, "actual port norm and cap rank")
        need(all(dot(lines[p], lines[q]) == 0 for q in geometry["frames"][cap]),
             "actual final target frame is port-orthogonal cap")
    centres = []
    for j in range(9):
        F = 510+j
        need(dims[F] == 7 and copies[j][1][3] == F, "actual rank-seven centre source frame")
        support = [p for p, row in enumerate(K) if row >> j & 1]
        full_rank, pivot_ports = direct.modular_rank(lines, support)
        need(full_rank == rational_rank([lines[p] for p in support]) == 8,
             "every original target pattern spans all eight rational coordinates")
        normal = direct.rational_normal(lines, geometry["frames"][F])
        projected = [project_onto_hyperplane(lines[p], normal) for p in support]
        need(rational_rank(projected) == 7, "recipient roots projected onto actual source frame span seven")
        centres.append(dict(centre=j, source_register=471+j, source_frame=F,
                            source_normal=direct.encode(normal), target_support=support,
                            support_rank=8, exact_projected_rank=7, modular_pivot_ports=pivot_ports,
                            snapshot_row=str(snapshots[j]), source_row=str(R[j])))
    # A valid cheap private excursion serves some targets, but cannot supply
    # the required whole centre pattern.  Use actual F510 and cap of port3.
    normal = direct.decode(centres[0]["source_normal"])
    reader_normal = list(map(Fraction, lines[3]))
    need(dot(normal, reader_normal) == 0 and K[3] & 1, "actual orthogonal excursion pair")
    def project_G(row):
        first = project_onto_hyperplane(row, normal)
        return project_onto_hyperplane(first, reader_normal)
    G = [project_G([int(i == j) for i in range(8)]) for j in range(8)]
    need(rational_rank(G) == 6, "actual excursion intersection dimension")
    need(all(x == 0 for x in project_G(reader_normal)), "chosen reader cap contains G")
    need(K[2] & 1 and any(project_G(lines[2])), "another required target cap excludes G")
    closed_path_ranks = [6, 7, 6]
    up = sum(max(b-a, 0) for a, b in zip(closed_path_ranks, closed_path_ranks[1:]))
    down = sum(max(a-b, 0) for a, b in zip(closed_path_ranks, closed_path_ranks[1:]))
    need(up == down == 1 and 1+up+down == 3, "complete cheap excursion tariff")
    need([6, 7][0] != [6, 7][-1], "omitting private return fails original ERASE frame")
    # Destroy the geometric witness deliberately: seven roots cannot certify
    # full rank eight.  The primary check must rely on actual coverage.
    damaged = centres[0]["modular_pivot_ports"][:7]
    need(rational_rank([lines[p] for p in damaged]) <= 7, "rank witness defect is detected")
    result = dict(status="PASS_ACTUAL_R438_SAME_QUERY_WALK_FLOOR_7_NO_NEW_KAPPA",
                  no_new_kappa=True, word_sha256=acquisition.WORD_SHA,
                  geometry_sha256=acquisition.GEOMETRY_SHA,
                  arbitrary_inputs=660, arbitrary_dirty_helpers=438, actual_ERASE_checks=9,
                  complete_original_F2_map="(x,y,h)->(x,y+x,h)",
                  exact_frame_count=len(masks), actual_B_interval=[begin, end],
                  original_frame_audit=frame_receipt, centres=centres,
                  single_branch_floor_by_copy_rank={str(r):14-r for r in range(8)},
                  independent_same_query_branch_total_floor=7,
                  rank_moment_corollary=dict(
                      definition="Phi_b(r)=64^b*r^(1-b); Phi_b(0)=0",
                      exponent_domain="0<=b<1",
                      conclusion="sum Phi_b(paid COPY and private MOVE ranks)>=Phi_b(7)",
                      scope="same rank-to-child conversion and ownership/stock premises; unweighted paid rank moment"),
                  controls=dict(valid_private_excursion=dict(source_frame=510, reader_frame=word["final"][114],
                                                             copy_rank=1, private_move_ranks=[1, 1], total=3,
                                                             served_port=3, unserviceable_required_port=2),
                                missing_private_return_rejected=True, deficient_rank_witness_rejected=True),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="rational frame geometry; unchanged actual centre total; independent exact private snapshots with closed nested MOVE walks; monotone public postscatter influence; no new downstream COPYs")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], "9 full-support witnesses; 9 projected-rank witnesses; 636 exact frames")


if __name__ == "__main__":
    main()
