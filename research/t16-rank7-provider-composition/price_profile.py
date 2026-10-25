"""Dual-engine finite-profile price; not changed-provider admission."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconstruct  # noqa: E402 - isolated-script bootstrap


def prices(root, profile):
    reconstruct.authenticate(root)
    engine = reconstruct.module(
        "rank7_profile_price",
        root / "research/frontier1094-idle-star-ceiling/analyze.py",
    )
    engine.ROOT = root
    engine.ENGINE_ROOT = (
        root / "research/complex-k492-owner-repair/vendor/multicold/engines"
    )
    engines = tuple(
        engine.load_engine(name) for name in ("moment", "base_two_moment", "outer")
    )
    baseline = reconstruct.read(
        root / "research/community-frontier1094-audit/ASSEMBLY.json"
    )
    return {
        "native": engine.price(Counter(profile), False, baseline, engines),
        "conservative": engine.price(Counter(profile), True, baseline, engines),
        "scope": "Exact two-engine profile price with ancestral outer parameters; new physical/controller invoice and modern outer are separate.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=reconstruct.HERE / "source-inputs", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    _, _, audit = reconstruct.reconstruct(args.root.resolve())
    result = prices(args.root.resolve(), audit["profile"])
    expected = reconstruct.read(reconstruct.HERE / "EXPECTED-PROFILE-PRICE.json")
    reconstruct.need(
        all(result[key] == expected[key] for key in ("native", "conservative")),
        "profile price changed",
    )
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS_DUAL_ENGINE_PROFILE_PRICE", result["native"]["endpoint_decimal"])


if __name__ == "__main__":
    main()
