"""Complete old/new finite-control union in deliberate normal or -O mode."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
pins = json.loads((ROOT / "CODE-SOURCES.json").read_text())["files"]
for name in ("verify.py", "archive_support.py"):
    if sha256((ROOT / name).read_bytes()).hexdigest() != pins[name]:
        raise ValueError("Publication bootstrap source pin: " + name)
S = types.ModuleType("_h25_finite_support")
S.__file__ = str(ROOT / "archive_support.py")
exec(compile((ROOT / "archive_support.py").read_bytes(), S.__file__, "exec"), S.__dict__)


def main():
    S.need(len(sys.argv) == 1 and sys.flags.optimize in (0, 1), "Fixed finite union in normal or -O mode")
    S.authenticate()
    temporary = S.temporary_parent()
    try:
        result = S.run("finite-O-all" if sys.flags.optimize else "finite-all", temporary / "replay")
        S.cleanup_owned(temporary)
    except BaseException as error:
        error.add_note("Failed finite publication evidence retained at " + str(temporary))
        raise
    print(json.dumps({"status": "PASS_H25_COMPLETE_FINITE_UNION", "optimization": sys.flags.optimize,
                      "publication": result["publication"], "scientific": result["scientific"],
                      "complete_cli_not_run": True}, sort_keys=True))


if __name__ == "__main__":
    main()
