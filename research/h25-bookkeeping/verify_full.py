"""One complete combined assertion-on correctness replay; no performance-factor claim."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
pins = json.loads((ROOT / "CODE-SOURCES.json").read_text())["files"]
for name in ("verify_full.py", "archive_support.py"):
    if sha256((ROOT / name).read_bytes()).hexdigest() != pins[name]:
        raise ValueError("Publication bootstrap source pin: " + name)
S = types.ModuleType("_h25_full_support")
S.__file__ = str(ROOT / "archive_support.py")
exec(compile((ROOT / "archive_support.py").read_bytes(), S.__file__, "exec"), S.__dict__)


def main():
    S.need(len(sys.argv) == 1 and sys.flags.optimize == 0, "Fixed combined full caller with original assertions")
    S.authenticate()
    temporary = S.temporary_parent()
    try:
        result = S.run("full-all", temporary / "replay")
        S.cleanup_owned(temporary)
    except BaseException as error:
        error.add_note("Failed full publication evidence retained at " + str(temporary))
        raise
    print(json.dumps({"status": "PASS_H25_COMBINED_FULL_CORRECTNESS", "publication": result["publication"],
                      "scientific": result["scientific"], "hosted_performance_factor_claim": False,
                      "fixed_benchmark_sample": False}, sort_keys=True))


if __name__ == "__main__":
    main()
