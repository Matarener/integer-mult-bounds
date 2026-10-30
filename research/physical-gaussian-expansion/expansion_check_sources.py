"""Complete source exports, live analytic pins and one actual physical cohort."""
import importlib
import json
from pathlib import Path
from unittest.mock import patch
import expansion_sources
from expansion_sources import HERE, active, digest, require


def references(rows):
    root = HERE.parents[1]
    for row in rows:
        if row["usage"] == "input":
            path = root / row["path"]
            require(path.is_file() and not path.is_symlink() and digest(path) == row["sha256"],
                    "pinned expansion live source: " + row["path"])


def run():
    from cardinal_counts import Count
    from records import Tape
    from word_product import WordProduct
    from expansion_tile import Tile
    from expansion_tile_prepare import TilePreparation
    rows = json.loads((HERE / "SOURCES.json").read_text())["files"]
    references(rows)
    modules = ("expansion_records", "expansion_geometry", "expansion_prepare", "expansion_block",
               "expansion_tile_geometry", "expansion_tile_prepare", "expansion_tile")
    for name in modules:
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == HERE / (name + ".py"), "package-local expansion runtime")
        for key, value in (("Count", Count), ("Tape", Tape)):
            if hasattr(module, key):
                require(getattr(module, key) is value, "one expansion Count/Tape cohort")
    tile, producer = Tile(), TilePreparation()
    require(tile.word is tile.block.word is tile.block.convolution.word
            and type(tile.word.base) is WordProduct and type(tile.word.product.word) is WordProduct
            and tile.word.base_bits == 4096, "actual acyclic word and convolution owners")
    tile.idle()
    producer.idle()
    require(tile.closed and producer.closed, "idle complete expansion owners")
    controls = []
    def reject(call, fragment, name):
        try:
            call()
        except ValueError as error:
            require(fragment in str(error), "specific expansion source rejection")
            controls.append(name)
        else:
            raise ValueError("missing expansion source rejection")
    altered = [dict(row) for row in rows]
    next(row for row in altered if row["usage"] == "input")["sha256"] = "0"*64
    reject(lambda: references(altered), "pinned expansion live source", "live_pin")
    with patch.object(expansion_sources, "CORE_DIGEST", "0"*64):
        core_tar = active().core_package.parents[2] / "core.tar"
        reject(lambda: expansion_sources.authenticate_core(core_tar), "complete uncompressed", "core_archive")
    with patch.object(expansion_sources, "ROUNDING_HEAD", "0"*40):
        reject(lambda: expansion_sources.authenticate_rounding(HERE / "inputs/rounding-source.tar"),
               "exact final-grid correction commit", "rounding_head")
    def second():
        with expansion_sources.opened():
            raise ValueError("unexpected second expansion cohort")
    reject(second, "cold expansion namespace", "second_cohort")
    return {"core_head": expansion_sources.CORE_HEAD, "rounding_head": expansion_sources.ROUNDING_HEAD,
            "core_export_files": 43, "live_inputs": sum(row["usage"] == "input" for row in rows),
            "runtime_modules": list(modules), "controls": controls}
