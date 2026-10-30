"""One retained B=PR5995-native or C=combined correctness replay; no timing selection."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
pins = json.loads((ROOT / "CODE-SOURCES.json").read_text())["files"]
for name in ("replay.py", "archive_support.py"):
    if sha256((ROOT / name).read_bytes()).hexdigest() != pins[name]:
        raise ValueError("Publication bootstrap source pin: " + name)
S = types.ModuleType("_h25_replay_support")
S.__file__ = str(ROOT / "archive_support.py")
exec(compile((ROOT / "archive_support.py").read_bytes(), S.__file__, "exec"), S.__dict__)


def run(arm, evidence):
    S.need(arm in ("B", "C"), "B=PR5995-native or C=combined required")
    return S.run("full-none" if arm == "B" else "full-all", evidence)


def main():
    S.need(len(sys.argv) == 3 and sys.argv[1] in ("B", "C"),
           "replay.py B|C NEW_EXTERNAL_EVIDENCE_DIRECTORY")
    result = run(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps({"status": "PASS_H25_FRESH_CORRECTNESS_REPLAY", "evidence": result["evidence"],
                      "publication": result["publication"], "science": result["scientific"]["science"],
                      "new_timings_replace_fixed_samples": False}, sort_keys=True))


if __name__ == "__main__":
    main()
