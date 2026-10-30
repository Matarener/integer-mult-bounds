"""Closed, explicit raw-hash rebinding after complete JSON content equality.

Only the invoice serialization and its dependent assembly/score references may
vary. Immutable sources, raw outputs and every scientific field remain intact.
"""

import hashlib
import json
from copy import deepcopy

from swap import need

LIMIT = 2 * 1024 * 1024


def unique_object(pairs):
    need(len(pairs) <= 8192, "JSON object field budget")
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    need(path.is_file() and path.stat().st_size <= LIMIT, "transport input byte budget")
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def canonical(document):
    return json.dumps(
        document, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def sha(path):
    need(path.is_file() and path.stat().st_size <= LIMIT, "transport hash byte budget")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equal(actual, expected, message):
    need(canonical(actual) == canonical(expected), message)


def attest(package, work):
    """Prove the entire input relation before deriving any expected hash."""
    frozen = package / "support/construction/raw"
    actual = work / "strict"
    invoice_name = "global/audit/PREFIX-AND-INVOICE.json"
    invoice = load(actual / invoice_name)
    equal(invoice, load(frozen / invoice_name), "complete invoice content differs")
    for name in ("OWNERS-AND-PROFILE.json", "ASYNC-AUDIT.json"):
        relative = "global/audit/" + name
        need(
            sha(actual / relative) == sha(frozen / relative),
            "fixed owner/controller bytes changed",
        )
    owner_sha = sha(actual / "global/audit/OWNERS-AND-PROFILE.json")
    controller_sha = sha(actual / "global/audit/ASYNC-AUDIT.json")
    need(invoice["owner_audit_sha256"] == owner_sha, "actual invoice owner binding")
    need(
        invoice["controller_audit_sha256"] == controller_sha,
        "actual invoice controller binding",
    )
    invoice_sha = sha(actual / invoice_name)
    expected_assembly = deepcopy(load(frozen / "ASSEMBLY.json"))
    need(
        expected_assembly["input_sha256"]["fresh_invoice"]
        == sha(frozen / invoice_name),
        "frozen invoice dependency",
    )
    expected_assembly["input_sha256"]["fresh_invoice"] = invoice_sha
    assembly = load(actual / "ASSEMBLY.json")
    equal(assembly, expected_assembly, "complete assembly content differs")
    need(
        assembly["input_sha256"]["owner_audit"] == owner_sha,
        "actual assembly owner binding",
    )
    graph = {
        "status": "PASS_EXACT_INVOICE_ASSEMBLY_TRANSPORT_RELATION",
        "invoice_sha256": invoice_sha,
        "assembly_sha256": sha(actual / "ASSEMBLY.json"),
        "frozen_invoice_sha256": sha(frozen / invoice_name),
        "frozen_assembly_sha256": sha(frozen / "ASSEMBLY.json"),
        "invoice_canonical_sha256": hashlib.sha256(canonical(invoice)).hexdigest(),
        "owner_sha256": owner_sha,
        "controller_sha256": controller_sha,
        "invoice_full_content_equal": True,
        "assembly_only_rebound_path": "/input_sha256/fresh_invoice",
    }
    (work / "TRANSPORT.json").write_text(json.dumps(graph, indent=2) + "\n")
    print(graph["status"], json.dumps(graph, sort_keys=True), flush=True)
    return graph


def expected_score(package, work, graph):
    expected = deepcopy(load(package / "support/exact-score/RESULT.json"))
    need(
        expected["assembly_sha256"] == graph["frozen_assembly_sha256"],
        "frozen score assembly",
    )
    need(
        expected["source_sha256"]["PREFIX-AND-INVOICE.json"]
        == graph["frozen_invoice_sha256"],
        "frozen score invoice",
    )
    expected["assembly_sha256"] = graph["assembly_sha256"]
    expected["source_sha256"]["PREFIX-AND-INVOICE.json"] = graph["invoice_sha256"]
    path = work / "EXPECTED-SCORE-TRANSPORT.json"
    path.write_text(json.dumps(expected, indent=2) + "\n")
    return path


def expected_construction(bundle, graph):
    expected = deepcopy(load(bundle / "ADMISSION.json"))
    need(
        expected["artifacts"]["assembly"] == graph["frozen_assembly_sha256"],
        "frozen construction assembly",
    )
    need(
        expected["artifacts"]["invoice"] == graph["frozen_invoice_sha256"],
        "frozen construction invoice",
    )
    expected["artifacts"]["assembly"] = graph["assembly_sha256"]
    expected["artifacts"]["invoice"] = graph["invoice_sha256"]
    return expected


def expected_invoice(package, work, graph, score):
    expected = deepcopy(load(package / "support/invoice/RESULT.json"))
    need(
        expected["assembly_sha256"] == graph["frozen_assembly_sha256"],
        "frozen review assembly",
    )
    need(
        expected["invoice_sha256"] == graph["frozen_invoice_sha256"],
        "frozen review invoice",
    )
    binding = expected["independent_score_binding"]
    need(
        binding["score_sha256"] == sha(package / "support/exact-score/RESULT.json"),
        "frozen review score dependency",
    )
    need(
        binding["assembly_sha256"] == graph["frozen_assembly_sha256"],
        "frozen score-review assembly",
    )
    need(
        binding["source_sha256"]["PREFIX-AND-INVOICE.json"]
        == graph["frozen_invoice_sha256"],
        "frozen score-review invoice",
    )
    expected["assembly_sha256"] = graph["assembly_sha256"]
    expected["invoice_sha256"] = graph["invoice_sha256"]
    binding["assembly_sha256"] = graph["assembly_sha256"]
    binding["source_sha256"]["PREFIX-AND-INVOICE.json"] = graph["invoice_sha256"]
    binding["score_sha256"] = sha(score)
    path = work / "EXPECTED-INVOICE-TRANSPORT.json"
    path.write_text(json.dumps(expected, indent=2) + "\n")
    return path
