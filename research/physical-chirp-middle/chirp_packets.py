"""Linear borrowed packet admission before allocating decoded data roles."""
from chirp_sources import active
active()
from router_metadata import indices
from words import BLANK, need


def validate(source, bits, label):
    source.rewind()
    try:
        for _ in indices(bits):
            need(source.read() in (0, 1), "complete " + label)
            source.step(1)
        need(source.read() == BLANK, "exact " + label + " extent")
    finally:
        source.rewind()
