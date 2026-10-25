"""Complete immutable inputs, shared loader cohort and source-fault controls."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
import tensor_sources as source
from tensor_sources import require


def run():
    import chirp_sources
    import expansion_sources
    import gaussian_sources
    import tensor_fixture
    from tensor_arithmetic import NarrowArithmetic
    from tensor_engine import Tensor
    from tensor_fixture import finite_chirp, literal_native, prepared_catalogue
    from tensor_router import FullRouter
    from tensor_twiddles import SmallPhaseBasis, SmallTwiddles
    state = source.active()
    require(chirp_sources.active() is state and expansion_sources.active() is state
            and gaussian_sources.active() is state, "one authenticated tensor numerical type cohort")
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((Path(__file__).resolve().parent / "SOURCES.json").read_text())
    require(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90", "declared tensor research base")
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        path = root / item["path"]
        require(path.is_file() and not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == item["sha256"],
                "complete live tensor source pin: "+item["path"])
    prepared_catalogue()
    root_archive = state.expansion_package.parents[2]
    source.authenticate_expansion(root_archive / "expansion.tar")
    source.authenticate_chirp(root_archive / "chirp.tar")
    controls = []
    def reject(label, action, expected):
        try:
            action()
        except ValueError as error:
            require(expected in str(error), "specific tensor source rejection: "+label)
        else:
            raise ValueError("missing tensor source rejection: "+label)
        controls.append(label)
    with patch.object(source, "EXPANSION_DIGEST", "0"*64):
        reject("expansion payload", lambda: source.authenticate_expansion(root_archive / "expansion.tar"), "complete uncompressed")
    with patch.object(source, "EXPANSION_HEAD", "0"*40):
        reject("expansion head", lambda: source.authenticate_expansion(root_archive / "expansion.tar"), "source identity")
    with patch.object(source, "CHIRP_RECEIPT", "0"*64):
        reject("chirp receipt", lambda: source.authenticate_chirp(root_archive / "chirp.tar"), "dependency receipt")
    with patch.object(source, "HEADROOM_HEAD", "0"*40):
        reject("headroom head", lambda: source.authenticate_headroom(source.HERE / "inputs/headroom-source.tar"), "exact headroom proof commit")
    with patch.object(tensor_fixture, "CATALOGUE_ARCHIVE_SHA256", "0"*64):
        reject("prepared archive", prepared_catalogue, "prepared-catalogue archive")
    with patch.object(tensor_fixture, "CATALOGUE_SHA256", "0"*64):
        reject("prepared payload", prepared_catalogue, "serialized physical coefficient return")
    machine = Tensor(finite_chirp(), FullRouter(literal_native()))
    require(isinstance(machine.chirp.kernel.basis, SmallPhaseBasis)
            and isinstance(machine.chirp.cyclic.twiddles, SmallTwiddles)
            and isinstance(machine.chirp.cyclic.convolution.product.twiddles, SmallTwiddles),
            "actual small-order producers on the complete chirp path")
    tile, core = machine.lines.expansion, machine.lines.compression
    require(tile.word is tile.block.word is tile.block.convolution.word
            and core.word is core.interior.word is core.boundary.word is core.interior.convolution.word,
            "original shared exact-word owner links")
    require(all(isinstance(owner.arithmetic, NarrowArithmetic) and owner.arithmetic.word is owner.word
                for owner in (tile, tile.block, core, core.interior, core.boundary)),
            "guarded scalar adapters retain their actual child owners")
    machine.idle()
    return {"base": manifest["base_commit"], "live_inputs": sum(row["usage"] == "input" for row in manifest["files"]), "controls": controls,
            "expansion_head": source.EXPANSION_HEAD, "chirp_head": source.CHIRP_HEAD,
            "headroom_head": source.HEADROOM_HEAD, "catalogue_sha256": tensor_fixture.CATALOGUE_SHA256,
            "scope": "source identity and actual factory wiring; no independent scientific review"}
