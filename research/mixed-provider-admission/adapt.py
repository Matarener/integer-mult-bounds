"""Exact, reviewable extensions of a freshly reconstructed PR4085 source.

SPDX-License-Identifier: Apache-2.0
Prepared for yssite with substantial OpenAI Codex assistance.
Predecessor code and notices are retained in the generated external tree.
"""
import json
from pathlib import Path
import shutil

from binding import need, read, sha

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MIXED = REPO / "research/staged544-mixed-fourth-entry"
TAGS = {"gauge44": "base", "extra": "extra",
        "gauge44-four": "base-four", "extra-four": "extra-four"}
BASE_MANIFEST = "4116ef61479e509811b60b5fd4e84db8811dae079092f2f83bdcc2c80052c0da"
BASE_ENGINE = "e69184d235d8790a3c520977dd44dcfb73a99d56989825485f922ff61059c8b1"


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def tree(path, exclude=()):
    result = {}
    for p in sorted(path.rglob("*")):
        need(not p.is_symlink(), "unbound source symlink")
        if p.is_file() and p.relative_to(path).as_posix() not in exclude:
            result[p.relative_to(path).as_posix()] = sha(p)
    return result


class Patches:
    def __init__(self, root):
        self.root = root
        self.rows = []

    def replace(self, name, old, new, count=1):
        p = self.root / name
        before = sha(p)
        body = p.read_text()
        need(body.count(old) == count, "exact patch preimage: " + name + ": " + old[:70])
        p.write_text(body.replace(old, new))
        self.rows.append(dict(path=name, before_sha256=before, after_sha256=sha(p),
                              old=old, new=new, occurrences=count))


def extend_source(baseline, destination):
    source = baseline / "inputs/source"
    need(sha(source / "MANIFEST.json") == BASE_MANIFEST, "exact PR4085 source manifest")
    need(tree(source, ("MANIFEST.json",)) == read(source / "MANIFEST.json"),
         "complete PR4085 source inventory")
    shutil.copytree(source, destination)
    p = Patches(destination)
    registry = read(destination / "new/BORROW-PROVIDERS.json")
    contract = {"providers": {}, "dispatch": read(MIXED / "owner/MIXED-DISPATCH.json")}
    for pid, tag in TAGS.items():
        base = tag.split("-")[0]
        kind = "FOUR" if tag.endswith("-four") else "THREE"
        word = MIXED / f"inputs/{kind}-{base}.json.gz"
        value = read(word)
        native = read(MIXED / f"owner/old-NATIVE-{base}.json.gz")
        widths = [len(value["helper_final"].get(str(r), [1 << i for i in range(9)]))
                  - len(value["start_extra"].get(str(r), [])) for r in native["helper_origin"]]
        relative = f"new/borrow/words/BORROW-WORD-43{tag}.json.gz"
        if kind == "THREE":
            need(sha(destination / relative) == sha(word), "unchanged THREE source")
        else:
            shutil.copyfile(word, destination / relative)
            registry[pid] = {"widths": widths, "actual_paid_profile": value["report"]["local_profile"]}
        need(registry[pid]["widths"] == widths
             and registry[pid]["actual_paid_profile"] == value["report"]["local_profile"],
             "complete native-order registry")
        contract["providers"][pid] = dict(word=relative, word_sha256=sha(word),
                                          widths=widths, profile=value["report"]["local_profile"])
    write(destination / "new/BORROW-PROVIDERS.json", registry)
    write(destination / "new/MIXED-CONTRACT.json", contract)
    shutil.copyfile(HERE / "binding.py", destination / "new/mixed_binding.py")
    p.replace("new/rebind.py",
              "pkg, loc_g, loc_e, out = map(Path, sys.argv[1:5]);",
              "pkg, loc_g, loc_e, loc_g4, loc_e4, out = map(Path, sys.argv[1:7]);")
    p.replace("new/rebind.py", "locs = {'gauge44': loc_g, 'extra': loc_e};",
              "locs = {'gauge44': loc_g, 'extra': loc_e, 'gauge44-four': loc_g4, 'extra-four': loc_e4};")
    p.replace("new/rebind.py",
              "idle = {int(r): v for r, v in rd(pkg / 'CONSTRUCTION.json')['idle'].items()}   # exact idle ranks of the shipped owner fill",
              "from mixed_binding import validate_rebind\nidle = validate_rebind(pkg, plan, locs)")
    # Both native entrypoints and both inherited replay call sites receive all providers.
    p.replace("verify.py",
              "new_words={'base':P/'new/borrow/words/BORROW-WORD-43base.json.gz','extra':P/'new/borrow/words/BORROW-WORD-43extra.json.gz'}",
              "new_words={tag:P/'new/borrow/words'/('BORROW-WORD-43'+tag+'.json.gz') for tag in ('base','extra','base-four','extra-four')}")
    p.replace("verify.py", "reuse=getattr(a,'new_%s_native_from'%key)",
              "reuse=getattr(a,'new_%s_native_from'%key,None)")
    p.replace("verify.py",
              "P,nat['base']/'local',nat['extra']/'local',work/'data-rebound'",
              "P,nat['base']/'local',nat['extra']/'local',nat['base-four']/'local',nat['extra-four']/'local',work/'data-rebound'")
    p.replace("verify.py", "nat['base'],nat['extra'],*[p_",
              "nat['base'],nat['extra'],nat['base-four'],nat['extra-four'],*[p_")
    p.replace("verify.py", "shutil.copytree(nat['extra'],runtime/'native-extra')",
              "for pid,tag in [('extra','extra'),('gauge44-four','base-four'),('extra-four','extra-four')]:shutil.copytree(nat[tag],runtime/('native-'+pid))")
    p.replace("replay.py", "g=work/'global'",
              "provider_dirs={'gauge44':local, **{pid:P/('native-'+pid)/'local' for pid in rd(data/'PLAN.json')['provider_registry'] if pid!='gauge44'}}\n"
              "assert set(provider_dirs)==set(rd(data/'PLAN.json')['provider_registry'])\n"
              "provider_args=[arg for pid,directory in sorted(provider_dirs.items()) for arg in ('--provider',pid+'='+str(directory))]\n"
              "g=work/'global'")
    p.replace("replay.py",
              "'--provider','gauge44='+str(local),'--provider','extra='+str(P/'native-extra/local')",
              "*provider_args", count=2)
    after = tree(destination, ("MANIFEST.json",))
    before = read(source / "MANIFEST.json")
    patched = {row["path"] for row in p.rows}
    for name in sorted(set(before) | set(after)):
        if name not in patched and before.get(name) != after.get(name):
            p.rows.append(dict(path=name, kind="file_inventory_change",
                               before_sha256=before.get(name), after_sha256=after.get(name)))
    write(destination / "MANIFEST.json", after)
    return contract, p.rows


def extend_engine(baseline, source, output):
    need(sha(baseline / "admit_composed.py") == BASE_ENGINE, "exact inherited admission engine")
    shutil.copyfile(baseline / "admit_composed.py", output)
    p = Patches(output.parent)
    name = output.name
    manifest = sha(source / "MANIFEST.json")
    p.replace(name, "manifest='" + BASE_MANIFEST + "'", "manifest='" + manifest + "'")
    p.replace(name, "helpers=408,source_file_count=676",
              f"helpers=408,source_file_count={len(read(source / 'MANIFEST.json'))}")
    p.replace(name, "commit='triple-staged-entry-and-receiver-share-20261019'",
              "commit='pr4088-four-provider-admission-v1'")
    p.replace(name, "for tag in ('base', 'extra'):",
              "for tag in ('base', 'extra', 'base-four', 'extra-four'):", count=2)
    p.replace(name,
              "natives['extra'] / 'local', work / 'rebound'",
              "natives['extra'] / 'local', natives['base-four'] / 'local', natives['extra-four'] / 'local', work / 'rebound'")
    p.replace(name, "shutil.copytree(natives['extra'], runtime / 'native-extra')",
              "for pid, tag in [('extra','extra'),('gauge44-four','base-four'),('extra-four','extra-four')]:\n"
              "        shutil.copytree(natives[tag], runtime / ('native-'+pid))")
    p.replace(name, "    write(work / 'RUNTIME-PATCHES.json', patches)",
              "    patch('verify.py', [(\"controller=15,independent_owner=8,geometry=6\", "
              "\"controller=rd(P/'new/SPEC.json')['expected']['mutations_rejected'],independent_owner=8,geometry=6\")])\n"
              "    write(work / 'RUNTIME-PATCHES.json', patches)")
    # New provider IDs inherit the unchanged interface descriptor, never an averaged width.
    old = "P.require(pid in plan['provider_registry'],'provider in retained registry')"
    new = ("if pid not in plan['provider_registry']:\n"
           "            P.require(pid.endswith('-four') and pid[:-5] in plan['provider_registry'], 'declared fourth provider')\n"
           "            plan['provider_registry'][pid]=copy.deepcopy(plan['provider_registry'][pid[:-5]])\n"
           "        " + old)
    helper = output.parent / "helpers"
    shutil.copytree(baseline / "inputs/helpers", helper)
    hp = Patches(output.parent)
    hp.replace("helpers/lift_parent.py", old, new)
    return p.rows + hp.rows
