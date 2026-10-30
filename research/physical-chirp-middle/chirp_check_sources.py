"""Whole predecessor binding and attribution-bearing source inputs."""
from hashlib import sha256
import importlib
from pathlib import Path
from unittest.mock import patch
import chirp_sources
from chirp_sources import HERE, active, require


def run():
    from cardinal_counts import Count
    from records import Tape
    state = active()
    chirp_sources.authenticate()
    modules = ("chirp_packets", "chirp_plan", "chirp_odometer", "phase_basis",
               "chirp_kernel", "phase_streams", "cyclic_engine", "chirp_engine")
    for name in modules:
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == HERE / (name + ".py"), "local chirp runtime: " + name)
        for key, canonical in (("Count", Count), ("Tape", Tape)):
            if hasattr(module, key):
                require(getattr(module, key) is canonical, "one chirp physical class: " + name + "." + key)
    require(state.convolution.Count is Count and state.convolution.Tape is Tape,
            "shared product/chirp physical cohort")
    inputs = {
        "research/chirp-symbolic-seed80/vendor/stream.py": "04647a2c8fa6ec5a2f3cd091ca076249aaa7b655ffe868d68995469a0b53142d",
        "research/chirp-symbolic-seed80/vendor/PROOF.md": "0c4438e09ec34ec8208dff90851fbc05bee0cbbefcac4d90208cfc63facc0207",
        "upstream/build/sections/07-resampling.tex": "8a6b91670f9163afb54892489fa2210c77fe1b058f0325ec7d18b44b94be6e2c",
        "upstream/build/sections/08-assembly.tex": "763d7945b1e1ec4ebae9b799bcefcc45fa9bae6e2ffad799868a9c3d513dbd4a",
    }
    for path, digest in inputs.items():
        require(sha256((HERE.parents[1] / path).read_bytes()).hexdigest() == digest,
                "pinned chirp source: " + path)
    with patch.object(chirp_sources, "DIGEST", "0"*64):
        try:
            chirp_sources.authenticate()
        except ValueError as error:
            require("pinned chirp source bytes" in str(error), "changed chirp binding rejection")
        else:
            raise ValueError("missing chirp binding rejection")
    try:
        with chirp_sources.opened():
            raise ValueError("second chirp runtime opened")
    except ValueError as error:
        require("cold chirp namespace" in str(error), "second chirp cohort rejection")
    return {"predecessor_head": chirp_sources.HEAD, "export_sha256": chirp_sources.DIGEST,
            "predecessor_files": 26, "runtime_modules": list(modules), "inputs": inputs,
            "controls": ["changed_archive_binding", "second_runtime"]}
