#!/usr/bin/env python3
"""Regenerate the complete word through its declared, authenticated ancestry."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def semantic(word):
    return {k: v for k, v in word.items() if k not in ("source_word", "signed_from", "parent_word_gzip_sha256")}

def load(name):
    path = HERE / "producer" / (name + ".py")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    ancestry = out / "ancestry"
    ancestry.mkdir()
    expected = json.loads((HERE / "EXPECTED.json").read_bytes())
    source = args.repo.resolve() / expected["source_word"]
    need(hashlib.sha256(source.read_bytes()).hexdigest() == expected["source_sha256"], "original word pin")
    base = load("bit_transvection")
    base.REPO, base.WORD = args.repo.resolve(), source
    base.BUILDER = base.REPO / "research/bit-boundary-persistence/build.py"
    scalar = load("bit_scalar_invoice")
    section = load("bit_section_code")
    signed = load("bit_signed_lift")
    final = load("build_support_code")
    pruner = load("prune")
    section.HERE = signed.HERE = ancestry
    support = out / "support"
    support.mkdir()
    final.SOURCE, final.HERE = ancestry, support
    pruner.SOURCE, pruner.HERE = support, out

    def authenticate(packed, key, parent=None, parent_field="signed_from"):
        word = json.loads(gzip.decompress(packed))
        need(word["source_word"] == str(source), "regenerated original source location")
        need(word["source_gzip_sha256"] == expected["source_sha256"], "regenerated original source hash")
        parent_fields = set(word) & {"signed_from", "parent_word_gzip_sha256"}
        need(parent_fields == ({parent_field} if parent is not None else set()), "unexpected parent metadata")
        if parent is not None:
            need(word[parent_field] == hashlib.sha256(parent).hexdigest(), "regenerated parent identity")
        need(hashlib.sha256(canonical(semantic(word))).hexdigest() == expected[key], "complete regenerated semantic payload")
        return word

    section.main()
    unsigned = (ancestry / "BIT-THREE-ROW-WORD.json.gz").read_bytes()
    authenticate(unsigned, "unsigned_section_semantic_sha256")
    signed.main()
    six = (ancestry / "BIT-SIGNED-WORD.json.gz").read_bytes()
    authenticate(six, "six_copy_semantic_sha256", unsigned)
    final.authenticate_predecessor = lambda packed: authenticate(packed, "six_copy_semantic_sha256", unsigned)
    final.main()
    support_blob = (support / "BIT-SUPPORT-WORD.json.gz").read_bytes()
    authenticate(support_blob, "support_semantic_sha256")
    pruner.authenticate_predecessor = lambda packed: authenticate(packed, "support_semantic_sha256")
    pruner.main()
    packed = (out / "BIT-PRUNED-WORD.json.gz").read_bytes()
    regenerated = authenticate(packed, "semantic_word_sha256", support_blob, "parent_word_gzip_sha256")
    frozen = json.loads(gzip.decompress((HERE / "WORD.json.gz").read_bytes()))
    need(semantic(regenerated) == semantic(frozen), "full regenerated ordered word differs")
    result = {"status": "PASS_COMPLETE_WORD_RECONSTRUCTION", "semantic_sha256": expected["semantic_word_sha256"],
              "normalized_provenance_fields": expected["normalized_fields"],
              "comparison": "complete decompressed payload after checked location and same-run compressed-parent identity", "no_new_kappa": True}
    (out / "RECONSTRUCTION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
