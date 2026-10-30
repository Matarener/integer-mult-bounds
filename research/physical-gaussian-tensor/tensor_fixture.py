"""Executable q2 physical cohort, distinct from the enormous production prime."""
from types import SimpleNamespace
from contextlib import contextmanager
from unittest.mock import patch
from tensor_sources import require

CATALOGUE_SHA256 = "46dbbc4b4aff71548e8203fa5837762ea3f78117564952e8087a339e55ef208a"
CATALOGUE_ARCHIVE_SHA256 = "7e10a7344d19674c68cc64537cbec48b2ff038a907ca00f92fab1c41aaae9af8"


def prepared_catalogue():
    """Authenticate the immutable return of the checked p48/P80 producer."""
    from hashlib import sha256
    from pathlib import Path
    import tarfile
    path = Path(__file__).resolve().parent / "inputs/p48-catalogue-v2.tar.gz"
    require(path.is_file() and not path.is_symlink()
            and sha256(path.read_bytes()).hexdigest() == CATALOGUE_ARCHIVE_SHA256,
            "exact prepared-catalogue archive")
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        require(len(members) == 1 and members[0].isfile() and not members[0].issym()
                and not members[0].islnk() and members[0].name == "gaussian-tensor-p48-page-20261019.bin"
                and members[0].size == 113537, "single bounded prepared-catalogue member")
        raw = archive.extractfile(members[0]).read()
    require(len(raw) == 113537 and sha256(raw).hexdigest() == CATALOGUE_SHA256,
            "exact serialized physical coefficient return")
    return raw


def literal_native():
    from macro_code import Code
    from retuned_native import active, retune
    state = active()
    # Retain the fresh-native recipe from check_composed.fixture. Literal
    # routing does not execute the selected production macro program.
    return retune(state.ordinary.Ordinary(
        2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
        (Code((("unreachable",),), 0),), capacity=64))


def finite_chirp():
    from check_composed import fixture
    from chirp_engine import Chirp
    from convolution_engine import Convolution
    from cyclic_engine import Cyclic
    from fourier_engine import Fourier
    return Chirp(Cyclic(Convolution(Fourier(fixture()[0]))))


@contextmanager
def p48_setup():
    """Exact constant metadata for the declared two-axis p48 witness only."""
    from cardinal_counts import Count
    from encoded import compare
    from router_metadata import owned
    require(50**1000 <= 51**997 < 51**1000 and 51**1000 <= 52**997 < 52**1000
            and 1**500 == 1, "exact p48 fractional-power metadata certificates")
    calls = {"51^(.997)": 0, "52^(.997)": 0, "1^(.002)": 0}
    def floor_power(value, numerator, denominator):
        if (numerator, denominator) == (997, 1000):
            for incoming, output in ((51, 50), (52, 51)):
                with owned(Count.literal(incoming)) as (constant,):
                    if compare(value, constant) == 0:
                        calls[str(incoming)+"^(.997)"] += 1
                        return Count.literal(output)
        elif (numerator, denominator) == (1, 500):
            with owned(Count.literal(1)) as (one,):
                if compare(value, one) == 0:
                    calls["1^(.002)"] += 1
                    return Count.literal(1)
        raise ValueError("outside the certified two-axis p48 setup fixture")
    with patch("composed_plan.floor_power", floor_power), patch("active_plan.floor_power", floor_power):
        yield calls
