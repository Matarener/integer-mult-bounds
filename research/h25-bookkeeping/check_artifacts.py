"""Authenticate v4 and invoke its unchanged six-payload canonical transport check."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
pins = json.loads((ROOT / "CODE-SOURCES.json").read_text())["files"]
for name in ("check_artifacts.py", "archive_support.py"):
    if sha256((ROOT / name).read_bytes()).hexdigest() != pins[name]:
        raise ValueError("Publication bootstrap source pin: " + name)
S = types.ModuleType("_h25_transport_support")
S.__file__ = str(ROOT / "archive_support.py")
exec(compile((ROOT / "archive_support.py").read_bytes(), S.__file__, "exec"), S.__dict__)


def main():
    S.need(len(sys.argv) == 1, "Fixed complete canonical transport input")
    before = S.authenticate()
    relative = "baseline/check_artifacts.py"
    checker = S.source_module("_h25_unchanged_canonical_checker", S.PAYLOAD / relative,
                              before["stage"]["files"][relative]["sha256"])
    old_argv = sys.argv[:]
    try:
        sys.argv = [str(S.PAYLOAD / relative)]
        checker.main()
        S.need(S.authenticate() == before, "Publication bytes/modes changed during transport check")
    finally:
        sys.argv = old_argv
    print(json.dumps({"status": "PASS_H25_V4_AND_CANONICAL_TRANSPORT", "stage_sha256": S.STAGE_SHA256,
                      "scientific_replay": False, "new_performance_factor_claim": False}, sort_keys=True))


if __name__ == "__main__":
    main()
