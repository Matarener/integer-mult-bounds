#!/usr/bin/env python3
"""A predecessor sentence stays outside a receipt that does not contain it."""

import hashlib
import importlib.util
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("archive_2980_2981_receipt", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    data = b"ab"
    git_oid = subprocess.check_output(["git", "hash-object", "--stdin"], input=data).decode().strip()
    if verify.blob_oid(data) != git_oid:
        raise SystemExit("blob oid left git hash-object")
    if hashlib.sha1(b"blob 2\0ab").hexdigest() != git_oid:
        raise SystemExit("the two-byte vector moved")
    sentence = "PR2899 emits that callee as a ROOT"
    kept = verify.predecessor_gap((sentence,), "readme " + sentence, "receipt", "credit")
    entered = verify.predecessor_gap((sentence,), "readme " + sentence, "receipt " + sentence, "credit")
    if kept != 1 or entered != 0:
        raise SystemExit("the predecessor gap moved")
    print("PASS_ARCHIVE_2980_2981_RECEIPT_TESTS groups=1")


if __name__ == "__main__":
    main()
