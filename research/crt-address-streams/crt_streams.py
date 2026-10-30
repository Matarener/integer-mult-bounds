"""Owned countdowns on complete opaque Boolean records, including failure exit."""
import crt_sources
crt_sources.activate()
from stream import Counter
from words import need


def copy_record(source, output, width):
    counter = Counter(width)
    try:
        while not counter.finished:
            bit = source.read()
            need(bit in (0, 1), 'complete Boolean CRT payload record')
            output.append(bit)
            source.step(1)
            counter.decrement()
    finally:
        counter.close()


def copy_rows(source, output, rows, width):
    counter = Counter(rows)
    try:
        while not counter.finished:
            copy_record(source, output, width)
            counter.decrement()
    finally:
        counter.close()


def zero_record(source, output, width, remove=False):
    counter = Counter(width)
    try:
        while not counter.finished:
            if remove:
                need(source.read() == 0, 'zero CRT address padding')
                source.step(1)
            else:
                output.append(0)
            counter.decrement()
    finally:
        counter.close()
