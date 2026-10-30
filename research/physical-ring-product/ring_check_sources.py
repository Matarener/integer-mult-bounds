"""Authenticate the complete predecessor and the single imported tape cohort."""

from hashlib import sha256
import importlib
from pathlib import Path
from unittest.mock import patch
import ring_sources
from ring_sources import HERE, active, require


def run():
    state = active()
    archive = ring_sources.authenticate()
    from cardinal_counts import Count
    from records import Tape
    from session import OuterScope
    modules = ("ring_words", "word_product", "twiddle_setup", "fft_arithmetic",
               "product_plan", "ring_engine", "convolution_engine")
    for name in modules:
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == HERE / (name + ".py"),
                "package-local runtime module: " + name)
        for key, canonical in (("Count", Count), ("Tape", Tape), ("OuterScope", OuterScope)):
            if hasattr(module, key):
                require(getattr(module, key) is canonical, "one shared physical class: " + name + "." + key)
    require(state.fourier.Count is Count and state.fourier.Tape is Tape,
            "product and Fourier share the actual numerical and physical classes")
    root = HERE.parents[1]
    inputs = {
        "research/certified-gaussian-recovery/intervals.py":
            "159d2a7d32a8cc7c8f56632a8ef127308b984a0a6753c9d6bdccacc6e7d6d4df",
        "upstream/build/sections/06-transforms.tex":
            "924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c",
    }
    for path, digest in inputs.items():
        require(sha256((root / path).read_bytes()).hexdigest() == digest,
                "pinned external reference: " + path)
    controls = []
    with patch.object(ring_sources, "DIGEST", "0"*64):
        try:
            ring_sources.authenticate()
        except ValueError as error:
            require("pinned ring-consumer source bytes" in str(error), "changed archive binding rejection")
            controls.append("changed_archive_binding")
        else:
            raise ValueError("missing archive binding rejection")
    try:
        with ring_sources.opened():
            raise ValueError("second cohort opened")
    except ValueError as error:
        require("cold normalized-product namespace" in str(error), "second runtime rejection")
        controls.append("second_runtime")
    return {"predecessor_head": ring_sources.HEAD,
            "export_sha256": sha256(archive.read_bytes()).hexdigest(),
            "predecessor_files": 16, "runtime_modules": list(modules),
            "external_inputs": inputs, "controls": controls}
