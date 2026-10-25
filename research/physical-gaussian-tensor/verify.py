"""Cold entry point for complete physical Gaussian tensor checks."""
import argparse
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tensor_sources import opened, require

GROUPS = {
    "mechanics": ("moves", "router", "gather", "windows", "plan"),
    "arithmetic_all": ("word", "counts", "twiddles", "arithmetic", "division", "records"),
    "sources": ("sources", "budget"),
}


def check(suite):
    name = "tensor_check_" + ("full" if suite in ("full_opposite", "consumer", "consumer_opposite") else suite)
    module = importlib.import_module(name)
    require(Path(module.__file__).resolve() == Path(__file__).resolve().parent / (name + ".py"),
            "package-local tensor checker")
    if suite == "word":
        from tensor_records import bounded_record_io, original_power_two, preload_record_cohort, record_aliases
        preload_record_cohort()
        aliases = record_aliases()
        require(all(original is original_power_two for _, original in aliases),
                "cold word imports retain original power aliases")
        with bounded_record_io():
            evidence = module.run()
        require(all(namespace["power_two"] is original for namespace, original in aliases),
                "cold word restores direct and private numerical aliases")
        try:
            with bounded_record_io():
                raise RuntimeError("planned cold-word scope interruption")
        except RuntimeError as error:
            require(str(error) == "planned cold-word scope interruption", "specific cold-word interruption")
        require(all(namespace["power_two"] is original for namespace, original in aliases),
                "cold word restores aliases after interruption")
        return evidence
    if suite in ("consumer", "consumer_opposite"):
        from tensor_fixture import prepared_catalogue
        return module.run(opposite=suite == "consumer_opposite", prepared=prepared_catalogue())
    return module.run(opposite=True) if suite == "full_opposite" else module.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    args = parser.parse_args()
    require(args.suite in ("moves", "router", "gather", "windows", "plan", "word", "catalogue", "twiddles", "counts", "arithmetic", "division", "records", "full", "full_opposite", "consumer", "consumer_opposite", "budget")
            or args.suite in GROUPS, "declared tensor check")
    with opened():
        evidence = {name: check(name) for name in GROUPS[args.suite]} if args.suite in GROUPS else check(args.suite)
        print(json.dumps({"status": "PASS_PHYSICAL_GAUSSIAN_TENSOR", "suite": args.suite,
                          "evidence": evidence}, sort_keys=True))


if __name__ == "__main__":
    main()
