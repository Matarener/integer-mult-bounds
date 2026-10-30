#!/usr/bin/env python3
"""Create a minimal draft package with exact source pins; never overwrite a package.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from research_package import ROOT, git, git_blobs, relative_file, symlink_free_relative_path


def source_metadata(root, commit, task_id, sources):
    catalog_path = "docs/research/agent-task-catalog.json"
    # Read the catalogue first so its card and source pin share the same bytes.
    names = [catalog_path] + sorted(set(["certificates/selected-result.json", *sources]) - {catalog_path})
    inventory = []
    with closing(git_blobs(root, [commit + ":" + name for name in names])) as objects:
        # strict also exhausts the reader, including its final process-status check.
        for name, (blob, pinned) in zip(names, objects, strict=True):
            if name == catalog_path:
                catalog = json.loads(pinned)
                cards = [t for tr in catalog["tracks"] for t in tr["tasks"] if t["id"] == task_id]
                if len(cards) != 1:
                    raise ValueError("unknown task in the pinned catalogue")
                card = cards[0]
            live = relative_file(root, name).read_bytes()
            if live != pinned:
                raise ValueError("source has uncommitted changes or differs from chosen base: " + name)
            inventory.append({"path": name, "usage": "input" if name in sources else "provenance",
                              "git_blob": blob, "sha256": hashlib.sha256(pinned).hexdigest()})
    inventory.sort(key=lambda row: row["path"])
    return catalog, card, inventory


def create(root, slug, task_id, author, sources=(), base="HEAD", budget=60):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", slug):
        raise ValueError("use a lowercase hyphenated package slug")
    destination = symlink_free_relative_path(root, "research/" + slug)
    if destination.exists():
        raise ValueError("package already exists; nothing overwritten")
    if not author.strip() or budget <= 0:
        raise ValueError("provide an author and positive time budget")
    commit = git(root, "rev-parse", "--verify", base + "^{commit}").decode().strip()
    catalog, card, inventory = source_metadata(root, commit, task_id, sources)
    task = {"schema_version": 1, "task_id": task_id, "priority_revision": catalog["priority_revision"],
            "base_commit": commit, "original_card": card, "scope_status": "unchanged",
            "actual_scope": card["question"], "scope_change_reason": None,
            "bottleneck_link": "TODO: explain the causal connection or label this as a side result",
            "budget_minutes": budget, "stop_rule": "TODO", "outcome": "in-progress", "evidence": "TODO",
            "author": author, "ai_assistance": "TODO: disclose tools used",
            "open_questions": [{"question": "TODO", "why_it_matters": "TODO", "first_step": "TODO", "blocked_by": "TODO"}]}
    manifest = {"schema_version": 1, "status": "draft", "python": "3.12", "requirements": [],
                "inputs": sorted(set(sources)),
                "commands": [{"argv": ["{python}", "-B", "{package}/verify.py"],
                              "timeout_seconds": 120, "checks": "TODO: identity, positive fixture and failure controls"}]}
    files = {"TASK.json": json.dumps(task, indent=2) + "\n",
             "SOURCES.json": json.dumps({"schema_version": 1, "base_commit": commit, "files": inventory}, indent=2) + "\n",
             "VERIFY.json": json.dumps(manifest, indent=2) + "\n",
             "verify.py": '#!/usr/bin/env python3\n"""Replace this draft with a scoped verifier and meaningful controls."""\nraise SystemExit("DRAFT: no research result has been verified")\n',
             "README.md": f'''# {slug}

**Draft; no new bound claimed.**

## Scope and evidence

Original card: `{task_id}`. Complete [TASK.json](TASK.json), including any scope
change and its connection to the bottleneck. Explain the result and limitations here.
Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance, so later priority
updates do not invalidate this package. Explicit --source files are live inputs
and must match their pins. Full Git history is needed to resolve provenance.

## Reproduce

After completing the verifier and marking VERIFY.json ready, from repo root:

```sh
python3 scripts/research_package.py --package research/{slug} --check-only
python3.12 scripts/research_package.py --package research/{slug}
```

Declare all external inputs and pinned dependencies in VERIFY.json. The generic
hook is bounded; native/Lean or long replays need an explicit dedicated workflow.

## Open next questions

Complete the structured `open_questions` list in TASK.json and explain it here:
the question, why it matters, a feasible first step and any blocker. If no next
question is justified, say so rather than inventing one.

## Credit

Prepared by {author}. Retain predecessor attribution and source-specific notices.
New work is Apache-2.0. Disclose substantial AI assistance in TASK.json.
'''}
    destination.parent.mkdir(exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".research-draft-", dir=destination.parent))
    try:
        for name, content in files.items():
            (temporary / name).write_text(content, encoding="utf-8", newline="\n")
        # mkdir is the exclusive claim; rename alone can replace an empty
        # directory that another agent created after the initial existence check.
        destination.mkdir()
        for child in temporary.iterdir():
            child.rename(destination / child.name)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--task", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--source", action="append", default=[])
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--budget-minutes", type=int, default=60)
    args = ap.parse_args()
    try:
        target = create(ROOT, args.slug, args.task, args.author, args.source, args.base, args.budget_minutes)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        ap.error(str(exc))
    print(str(target))
    print("DRAFT ONLY: complete scope, evidence, open questions and verifier; the stub deliberately fails.")


if __name__ == "__main__":
    main()
