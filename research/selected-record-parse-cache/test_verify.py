#!/usr/bin/env python3
"""A cache hit keeps the parsed object, and a second digest does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("selected_record_parse_cache", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    cache = verify.ParseCache()
    first, hit = cache.load(b'{"kappa": "1/2"}')
    if hit or first["kappa"] != "1/2":
        raise SystemExit("the first load was not a miss")
    second, hit = cache.load(b'{"kappa": "1/2"}')
    if not hit or second is not first:
        raise SystemExit("the second load did not reuse the object")
    third, hit = cache.load(b'{"kappa": "1/3"}')
    if hit or third["kappa"] != "1/3":
        raise SystemExit("the changed payload hit")
    print("PASS_SELECTED_RECORD_PARSE_CACHE_TESTS groups=1")


if __name__ == "__main__":
    main()
