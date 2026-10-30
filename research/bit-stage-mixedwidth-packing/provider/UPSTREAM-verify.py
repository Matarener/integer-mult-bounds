#!/usr/bin/env python3
"""Authenticate and replay the owner/provider/caller/price certificate.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
The optional C++ replay has its own command and is not claimed by this hook.
"""
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import gzip
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read(path):
    return json.loads(path.read_bytes())


def authenticate():
    manifest = read(ROOT / "MANIFEST.json")
    need(manifest["schema_version"] == 1, "manifest schema")
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()}
    need(actual == set(manifest["files"]) | {"MANIFEST.json"}, "package inventory")
    for name, expected in manifest["files"].items():
        path = PurePosixPath(name)
        need(not path.is_absolute() and ".." not in path.parts
             and path.as_posix() == name, "canonical package path")
        source = ROOT / name
        need(not source.is_symlink() and source.resolve().is_relative_to(ROOT),
             "regular internal package file")
        need(sha256(source.read_bytes()).hexdigest() == expected, "package hash " + name)
    sources = read(ROOT / "INPUT-SOURCES.json")
    seen = set()
    for item in sources["files"]:
        name = item["local_path"]
        need(name not in seen, "duplicate bundled input")
        seen.add(name)
        raw = (ROOT / name).read_bytes()
        need(sha256(raw).hexdigest() == item["sha256"], "bundled SHA256 " + name)
        if item.get("encoding") == "gzip":
            raw = gzip.decompress(raw)
            need(sha256(raw).hexdigest() == item["source_sha256"],
                 "decompressed source SHA256 " + name)
        else:
            need("encoding" not in item, "unknown bundled encoding")
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == item["git_blob"], "bundled Git blob " + name)
    need(seen == {name for name in actual if name.startswith("inputs/")},
         "complete bundled source inventory")
    return manifest


def child(script, manifest, extra=(), *, accepted=True, timeout=180):
    # Authenticate the bytes that are actually compiled. Bypass import caches,
    # reset argv for the child's CLI, and retain optimization mode explicitly.
    bootstrap = (
        "import hashlib,pathlib,sys\n"
        "p=pathlib.Path(sys.argv[1]); b=p.read_bytes()\n"
        "if hashlib.sha256(b).hexdigest()!=sys.argv[2]:\n"
        " raise ValueError('child source hash')\n"
        "sys.argv=[str(p)]+sys.argv[3:]\n"
        "exec(compile(b,str(p),'exec'),"
        "{'__name__':'__main__','__file__':str(p),'__package__':None})\n"
    )
    argv = [sys.executable, "-I", "-B"]
    if sys.flags.optimize:
        argv.append("-O")
    argv += ["-c", bootstrap, str(ROOT / script), manifest["files"][script], *extra]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    if accepted:
        need(result.returncode == 0, script + " failed:\n" + result.stderr)
        need(not result.stderr, script + " unexpected stderr")
    else:
        need(result.returncode != 0, script + " accepted malformed control")
    return result


def price_controls(manifest, owners):
    controls = []
    with tempfile.TemporaryDirectory(prefix="carrier-price-controls-") as temp:
        path = Path(temp) / "owners.json"
        cases = []
        bad = deepcopy(owners)
        bad["idle_per_replica_including_zero"]["8"] -= 1
        cases.append(("omitted returned idle work", bad, "complete idle child and rank counts"))
        bad = deepcopy(owners)
        bad["live_families"] += bad["private_family_reserve"]
        cases.append(("private reserve credited as live stock", bad, "fixed stock"))
        bad = deepcopy(owners)
        bad["routing_invoice"]["selector_G_terms"]["new_complete_chart"] = 0
        cases.append(("unpaid changed chart return", bad, "explicit route tariff components"))
        for name, value, message in cases:
            path.write_text(canonical(value) + "\n")
            result = child("price.py", manifest, ("--owner-result", str(path)), accepted=False)
            need(message in result.stderr, name + " rejected for an unrelated reason")
            controls.append(name)
    return controls


def main():
    manifest = authenticate()
    with tempfile.TemporaryDirectory(prefix="carrier-owner-audit-") as temp:
        artifacts = Path(temp) / "artifacts"
        owner_run = child("owner.py", manifest, ("--emit", str(artifacts)))
        need(owner_run.stdout.startswith("PASS_CARRIER_OWNERS "), "owner replay marker")
        independent = json.loads(child("independent_owner.py", manifest,
                                       ("--artifacts", str(artifacts))).stdout)
        need(canonical(independent) == canonical(read(ROOT / "INDEPENDENT-OWNERS.json")),
             "complete independent serialized owner receipt")
    owners = read(ROOT / "OWNERS.json")
    with tempfile.TemporaryDirectory(prefix="carrier-native-audit-") as temp:
        artifacts = Path(temp) / "artifacts"
        native = json.loads(child("native.py", manifest,
                                  ("--output", str(artifacts))).stdout)
        need(canonical(native) == canonical(read(ROOT / "NATIVE.json")),
             "complete typed native receipt")
        cuts = json.loads(child("caller_source_cuts.py", manifest,
                                ("--artifacts", str(artifacts))).stdout)
        need(canonical(cuts) == canonical(read(ROOT / "CALLER-SOURCE-CUTS.json")),
             "complete independent source-cut receipt")
    price = json.loads(child("price.py", manifest).stdout)
    need(canonical(price) == canonical(read(ROOT / "PRICING.json")),
         "complete typed price receipt")
    caller = json.loads(child("caller.py", manifest, timeout=540).stdout)
    need(canonical(caller) == canonical(read(ROOT / "CALLER.json")),
         "complete typed logical caller receipt")
    local = read(ROOT / "inputs/PR4183-RESULT.json")["words"]
    for name, previous in (("baseline", "baseline"), ("candidate", "boolean")):
        word = native["words"][name]
        need(word["literal_word_sha256"] == local[previous]["word_sha256"],
             "native/predecessor literal binding")
        need(word["local_checks"]["forward"]["histogram"] == local[previous]["histogram"],
             "native/predecessor complete histogram")
        need(word["rank_mass"] == local[previous]["rank_mass"], "local rank mass binding")
        for new_key, old_key in (("ADDs", "adds"), ("paid_queries", "queries"),
                                 ("records", "records")):
            need(word[new_key] == local[previous][old_key], "complete local invoice binding")
        need(word["precision"]["forward_majorant"] == local[previous]["positive_majorant"]["forward"]
             and word["precision"]["reverse_majorant"] == local[previous]["positive_majorant"]["inverse"],
             "native/predecessor precision envelope binding")
        need(word["precision"]["local_precision_charge"] == 128
             and word["precision"]["nine_precision_charge"] == 256, "actual precision charge")
    need(price["source_sha256"]["owner"] == sha256((ROOT / "OWNERS.json").read_bytes()).hexdigest(),
         "price binds actual complete owners")
    need(price["W"] == owners["live_families"] == 28416, "live stock binding")
    need(price["profiles"]["frozen"]["children"] - price["profiles"]["candidate"]["children"] == 288,
         "complete recursive saving")
    for name, profile in (("catalogue", "candidate"),
                          ("matched_baseline_catalogue", "frozen")):
        catalogue = caller[name]
        need(catalogue["full_paid_requests"] == price["profiles"][profile]["children"]
             and catalogue["rank_histogram"] == price["profiles"][profile]["profile"],
             "caller/complete recursive profile binding")
    for item, filename in (("native", "NATIVE.json"), ("owner", "OWNERS.json")):
        need(caller["provenance"][item + "_receipt_sha256"]
             == sha256((ROOT / filename).read_bytes()).hexdigest(),
             "caller/" + item + " receipt binding")
    for name in ("baseline", "candidate"):
        need(caller["provenance"]["literal_word_sha256"][name]
             == native["words"][name]["literal_word_sha256"],
             "caller/native literal binding")
    need(cuts["candidate_word_sha256"]
         == caller["provenance"]["literal_word_sha256"]["candidate"]
         and cuts["candidate_native_raw6_sha256"]
         == native["words"]["candidate"]["native_raw6_sha256"],
         "independent source-cut/native/caller binding")
    need(caller["literal_binding"]["complete_calls"] == 288
         and caller["literal_binding"]["ordinary_roles"] == 660
         and caller["literal_binding"]["private_role"] == 660,
         "complete caller role and dispatch census")
    need(caller["split_bases"]["complete_base_labels"]
         == caller["catalogue"]["base_labels"] == 549,
         "complete caller split-basis census")
    controls = price_controls(manifest, owners)
    print("PASS_BIT_CARRIER_OWNER_ADMISSION owners=126144 "
          "queries=902880->902592 logical_caller=p1 precision=128,256,512 "
          "price_controls=%d optional_cpp_not_run no_new_kappa" % len(controls))


if __name__ == "__main__":
    main()
