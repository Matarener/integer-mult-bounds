#!/usr/bin/env python3
"""Byte retention versus ledger disposition for the selected frontier's source PRs.

No ledger edit, no frontier replay, and no new kappa.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTIAL = (5398, 5400, 5402)
CERTIFICATE = "certificates/selected-result.json"
REVIEW = "docs/research/pr-intake-evidence/pr4610/PROOF-REVIEW.md"

# integration paths, in ledger order, with the git relationship to current HEAD.
# identical: present at the PR head and byte-identical on HEAD.
# changed: present at both, and the trees differ.
# added: absent at the PR head and present on HEAD.
ROWS = [
    {
        "number": 5413,
        "disposition": "incorporated",
        "head": "0c1fa2f47fb5ea17b93a4b67063d08e49cc38e51",
        "paths": {"research/coupled-helper-neutral-completion": "identical"},
        "unresolved_has": "Five inherited framework assumptions persist",
    },
    {
        "number": 5414,
        "disposition": "incorporated",
        "head": "bc37fb01c58d20e799d3299dec63e654f67d9d1b",
        "paths": {"research/neutral632-independent-verification": "identical"},
        "unresolved_has": "Narrow independent screen",
    },
    {
        "number": 5402,
        "disposition": "partially_reviewed",
        "head": "3348fccea855082786d5f0fc5558b73d4974e745",
        "paths": {"research/native-rank8-helper-provider": "identical"},
        "unresolved_has": "no autonomous credit for its eight coupled outputs",
    },
    {
        "number": 5407,
        "disposition": "incorporated",
        "head": "b62252c61113d2863b36ce2419aa81a07f393c42",
        "paths": {"research/coupled-provider-independent-audit": "identical"},
        "unresolved_has": "Scoped independent audit accepted",
    },
    {
        "number": 5398,
        "disposition": "partially_reviewed",
        "head": "174fb211493b43a42210434083e9702b4fb7a2ce",
        "paths": {"research/kappa-backward-controller-20261023": "identical"},
        "unresolved_has": "does not admit a supplier, outer theorem or improved kappa",
    },
    {
        "number": 5400,
        "disposition": "partially_reviewed",
        "head": "7ea72fb692cbfd64fea556de84327bbf88555986",
        "paths": {"research/direct-backward-independent-validation": "identical"},
        "unresolved_has": "does not admit a supplier, outer theorem or improved kappa",
    },
    {
        "number": 4610,
        "disposition": "incorporated",
        "head": "20bb93cd990d2ff683e4d0fc56b87a42cd5d3296",
        "paths": {
            "research/kappa-interface-round2-20261022": "identical",
            "research/kappa-lean-verification-20261022": "identical",
            "research/kappa-round3-audit-20261022": "identical",
            "research/kappa-round3-warp-20261022": "identical",
            "research/kappa-round3-warp-lean-20261022": "identical",
            "research/kappa-round6-compiler-tightening-20261022": "identical",
            "research/kappa-round7-4610-construction-checkpoint-20261022": "identical",
            "research/kappa-round7-4610-coupled-recursion-20261022": "identical",
            "research/kappa-round7-4610-frontier-review-20261022": "identical",
            "research/kappa-round7-4610-independent-audit-20261022": "identical",
            "research/kappa-round7-4610-phase-debt-audit-20261022": "identical",
            "research/kappa-round7-4610-phase-recursion-20261022": "identical",
            "research/kappa-round7-4610-review-20261022": "identical",
            "research/kappa-round7-4610-scalar-contract-20261022": "identical",
            "research/kappa-round7-rankone-phase-20261022": "identical",
            "research/kappa-search-20261022": "identical",
            "research/query-projector-interface-20261022": "identical",
            "research/scalar-reorder-20261022": "identical",
            "research/warp-interface-20261022": "identical",
            CERTIFICATE: "changed",
            REVIEW: "added",
        },
        "unresolved_has": "No blocking obligation in the admitted change",
    },
    {
        "number": 5241,
        "disposition": "incorporated",
        "head": "13efb5fc5f3b7c14ec2cfa181dd9eb6480972cf2",
        "paths": {
            "research/final4610-independent-admission": "identical",
            CERTIFICATE: "changed",
            REVIEW: "added",
        },
        "unresolved_has": "No blocking obligation in the admitted change",
    },
]


def git(args):
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return subprocess.run(
        ["git", *args], cwd=ROOT, env=env, capture_output=True, check=False,
    )


def exists(spec):
    return git(["cat-file", "-e", spec]).returncode == 0


def relation(head, path):
    at_head = exists(f"{head}:{path}")
    at_now = exists(f"HEAD:{path}")
    if at_head and at_now:
        diff = git(["diff", "--name-only", head, "HEAD", "--", path])
        if diff.returncode != 0:
            return "diff-error"
        names = [line for line in diff.stdout.decode().splitlines() if line]
        return "identical" if not names else "changed"
    if (not at_head) and at_now:
        return "added"
    if at_head and not at_now:
        return "removed"
    return "absent"


def faults(ledger_by, selected, manifest, promotion, contributors):
    problems = []
    prefix = [row["number"] for row in ROWS]
    if selected.get("source_prs", [])[:8] != prefix:
        problems.append("source_prs prefix " + str(selected.get("source_prs", [])[:8]))
    if selected.get("kappa") != "605457647/200000000000":
        problems.append("kappa fraction")
    if selected.get("decimal") != "0.003027288235":
        problems.append("kappa decimal")
    if selected.get("audited_source_head") != ROWS[0]["head"]:
        problems.append("audited_source_head")
    if selected.get("audit_pr") != 5414 or selected.get("audit_head") != ROWS[1]["head"]:
        problems.append("audit binding")
    roots = [
        "research/coupled-provider-independent-audit",
        "research/coupled-helper-neutral-completion",
        "research/neutral632-independent-verification",
    ]
    if manifest.get("package_roots") != roots:
        problems.append("package_roots")
    files = manifest.get("files")
    if not isinstance(files, dict) or len(files) != 1245:
        problems.append("manifest file count " + str(len(files) if isinstance(files, dict) else None))
        files = files if isinstance(files, dict) else {}
    matched = 0
    for path, digest in files.items():
        disk = ROOT / path
        if not disk.is_file():
            problems.append("manifest missing " + path)
            continue
        actual = hashlib.sha256(disk.read_bytes()).hexdigest()
        if actual != digest:
            problems.append("manifest mismatch " + path)
        else:
            matched += 1
    if matched != 1245:
        problems.append("matched manifest files " + str(matched))
    for root in roots:
        if not any(path == root or path.startswith(root + "/") for path in files):
            problems.append("root absent from manifest " + root)
    for number in PARTIAL:
        root = next(iter(ROWS[prefix.index(number)]["paths"]))
        if root in files or any(path.startswith(root + "/") for path in files):
            problems.append("partial package entered the execution closure " + root)
    if "three-package execution closure" not in promotion:
        problems.append("promotion closure sentence")
    if "PR5407" not in promotion or "PR5413" not in promotion or "PR5414" not in promotion:
        problems.append("promotion package names")
    if "the final +5×10^-12 over #5398/#5400 is compiler/outer headroom" not in promotion:
        problems.append("promotion headroom sentence")
    for needle in ("[#5398]", "#5400", "[#5402]", "[#5407]", "[#5413]", "[#5414]", "[#4610]", "#5241"):
        if needle not in contributors:
            problems.append("contributor credit " + needle)
    if "gain over\n#5398/#5400 is 5×10^-12" not in contributors:
        problems.append("contributor headroom sentence")
    for row in ROWS:
        record = ledger_by.get(row["number"])
        if record is None:
            problems.append("ledger missing " + str(row["number"]))
            continue
        if record.get("disposition") != row["disposition"]:
            problems.append(f"{row['number']} disposition {record.get('disposition')}")
        if record.get("current_head") != row["head"]:
            problems.append(f"{row['number']} head")
        if record.get("github_state") != "MERGED":
            problems.append(f"{row['number']} github_state")
        closure = record.get("closure") or {}
        if closure.get("kind") != "merged_for_archive_only":
            problems.append(f"{row['number']} closure {closure.get('kind')}")
        merge = closure.get("merge_commit")
        if not isinstance(merge, str) or git(["merge-base", "--is-ancestor", merge, "HEAD"]).returncode != 0:
            problems.append(f"{row['number']} merge commit")
        if git(["merge-base", "--is-ancestor", row["head"], "HEAD"]).returncode != 0:
            problems.append(f"{row['number']} head is not an ancestor")
        unresolved = record.get("unresolved_question") or ""
        if row["unresolved_has"] not in unresolved:
            problems.append(f"{row['number']} unresolved question")
        locations = record.get("integration_location")
        if locations != list(row["paths"]):
            problems.append(f"{row['number']} integration paths")
            continue
        for path, expect in row["paths"].items():
            found = relation(row["head"], path)
            if found != expect:
                problems.append(f"{row['number']} {path} is {found}, expected {expect}")
        for item in record.get("evidence") or []:
            evidence = item.get("evidence")
            if not isinstance(evidence, str) or not exists(f"HEAD:{evidence}"):
                problems.append(f"{row['number']} evidence path {evidence}")
    return problems


def main():
    ledger = json.loads((ROOT / "docs/research/pr-ledger.json").read_text(encoding="utf-8"))
    selected = json.loads((ROOT / CERTIFICATE).read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "certificates/frontier5413-source.json").read_text(encoding="utf-8"))
    promotion = (ROOT / "docs/research/pr-intake-evidence/pr5413-promotion/PROMOTION.md").read_text(encoding="utf-8")
    contributors = (ROOT / "docs/research/community-neutral5413-contributors.md").read_text(encoding="utf-8")
    by_number = {record["number"]: record for record in ledger["pull_requests"]}
    problems = faults(by_number, selected, manifest, promotion, contributors)
    if problems:
        print("FAIL_FRONTIER_SOURCE_RETENTION")
        print("\n".join(problems))
        return 1
    forged = json.loads(json.dumps(by_number[5398]))
    forged["disposition"] = "incorporated"
    forged_ledger = dict(by_number)
    forged_ledger[5398] = forged
    forged_faults = faults(forged_ledger, selected, manifest, promotion, contributors)
    if not any(item.startswith("5398 disposition") for item in forged_faults):
        print("FAIL_FRONTIER_SOURCE_RETENTION control did not catch a forged incorporated label")
        return 1
    tampered = json.loads(json.dumps(manifest))
    first = next(iter(tampered["files"]))
    tampered["files"][first] = "0" * 64
    tampered_faults = faults(by_number, selected, tampered, promotion, contributors)
    if not any(item.startswith("manifest mismatch") for item in tampered_faults):
        print("FAIL_FRONTIER_SOURCE_RETENTION control did not catch a manifest mismatch")
        return 1
    identical = sum(1 for row in ROWS for kind in row["paths"].values() if kind == "identical")
    print(
        "PASS_FRONTIER_SOURCE_RETENTION"
        f" prs=8 identical_paths={identical} manifest_files=1245"
        " partial_but_named=5398,5400,5402"
        " certificate_moved_after=4610,5241"
        " no_ledger_edit=true no_new_kappa=true"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
