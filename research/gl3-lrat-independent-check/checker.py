#!/usr/bin/env python3
"""A small, standard-library-only checker for ASCII positive-hint LRAT (RUP).

Accepted grammar is line-oriented LRAT: ``id literals 0 hints 0`` or
``id d deletion_ids 0``. Only positive hints are supported; RAT, binary LRAT,
embedded comments, and tautological additions are rejected. DIMACS clauses
may span lines; duplicates have ordinary set-of-literals semantics. The
deletion record's leading id is metadata, not an addition: it must name a
nonfuture id (zero is allowed), and deletion targets must currently be live.
The empty clause must be the final addition; valid deletions may follow it,
including deleting the empty clause, without undoing its established derivation.

Soundness argument: for each proposed clause C, assume every literal of C
false. Each accepted hint is either a unit clause, whose remaining literal
every model of the live database and the assumptions must satisfy, or a
conflicting clause. A final conflict therefore proves that the live database
entails C. Initial clauses are the DIMACS formula. Inductively all additions
are consequences of that formula; deleting clauses cannot invalidate this
invariant. Deriving the empty clause proves the input formula unsatisfiable.
No solver, proof generator, assertions, or other checker is used for validity.
This is an implementation argument, not a formal verification claim.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import gzip
import hashlib
import json
import os
from pathlib import Path
from typing import BinaryIO, Iterator, Literal
import zlib


@dataclass(frozen=True)
class Limits:
    """Finite resource limits, also applied to decompressed gzip payloads."""

    max_variables: int = 1_000_000
    max_initial_clauses: int = 5_000_000
    max_live_clauses: int = 5_000_000
    max_additions: int = 50_000_000
    max_hints: int = 2_000_000_000
    max_clause_id: int = (1 << 63) - 1
    max_line_bytes: int = 4 * 1024 * 1024
    max_cnf_bytes: int = 512 * 1024**2
    max_proof_bytes: int = 512 * 1024**2

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if type(value) is not int or value <= 0:
                raise CheckError("invalid_limit", f"{name} must be a positive integer")


@dataclass(frozen=True)
class CheckReceipt:
    status: Literal["verified_unsat"]
    variables: int
    clauses: int
    additions: int
    deletions: int
    deletion_records: int
    hints: int
    live_clauses: int
    final_empty: bool
    final_empty_clause: int
    final_empty_live: bool
    cnf_sha256: str
    lrat_sha256: str
    lrat_payload_sha256: str
    cnf_bytes: int
    lrat_bytes: int
    lrat_payload_bytes: int


class CheckError(ValueError):
    """An invalid, unsupported, unreadable, or over-limit input."""

    def __init__(self, code: str, message: str, *, path: str = "", line: int = 0):
        self.code = code
        self.path = path
        self.line = line
        location = f"{path}:{line}: " if path else ""
        super().__init__(f"{location}{code}: {message}")


class _Source:
    """Read bounded lines while hashing exactly the checked source bytes."""

    def __init__(self, path: str | os.PathLike[str], *, compressed: bool,
                 byte_limit: int, line_limit: int):
        self.path = str(path)
        self.compressed = compressed
        self.byte_limit = byte_limit
        self.line_limit = line_limit
        self.raw_bytes = 0
        self.payload_bytes = 0
        self.raw_hash = hashlib.sha256()
        self.payload_hash = hashlib.sha256()
        self.line = 0
        self.raw: BinaryIO | None = None

    def read(self, size: int = -1) -> bytes:
        # gzip.GzipFile reads through this method; no seeking or re-reading.
        if self.raw is None:
            raise CheckError("io_error", "source is not open", path=self.path)
        data = self.raw.read(size)
        self.raw_bytes += len(data)
        if self.raw_bytes > self.byte_limit:
            raise self.error("byte_limit", "source byte limit exceeded")
        self.raw_hash.update(data)
        return data

    def error(self, code: str, message: str) -> CheckError:
        return CheckError(code, message, path=self.path, line=self.line)

    def lines(self) -> Iterator[list[str]]:
        try:
            with open(self.path, "rb") as raw:
                self.raw = raw
                if self.compressed:
                    with gzip.GzipFile(fileobj=self, mode="rb") as payload:
                        yield from self._lines(payload)
                else:
                    # Plain input also goes through read() so source hashes
                    # and byte limits refer to the same bytes that are parsed.
                    yield from self._plain_lines(raw)
        except CheckError:
            raise
        except (OSError, EOFError, UnicodeError, zlib.error) as exc:
            raise self.error("io_error", str(exc)) from exc
        finally:
            self.raw = None

    def _plain_lines(self, raw: BinaryIO) -> Iterator[list[str]]:
        while True:
            data = raw.readline(self.line_limit + 1)
            self.raw_bytes += len(data)
            if self.raw_bytes > self.byte_limit:
                raise self.error("byte_limit", "source byte limit exceeded")
            self.raw_hash.update(data)
            if not data:
                return
            yield self._tokens(data)

    def _lines(self, payload: BinaryIO) -> Iterator[list[str]]:
        while True:
            data = payload.readline(self.line_limit + 1)
            if not data:
                return
            yield self._tokens(data)

    def _tokens(self, data: bytes) -> list[str]:
        self.line += 1
        self.payload_bytes += len(data)
        if self.payload_bytes > self.byte_limit:
            raise self.error("byte_limit", "decompressed byte limit exceeded")
        if len(data) > self.line_limit:
            raise self.error("line_limit", "line byte limit exceeded")
        if any(byte not in (9, 10, 13) and not 32 <= byte <= 126 for byte in data):
            raise self.error("ascii", "only printable ASCII, tabs, and line endings are allowed")
        self.payload_hash.update(data)
        return data.decode("ascii").split()


def _integer(token: str, bound: int, source: _Source, *, signed: bool = False) -> int:
    digits = token[1:] if signed and token.startswith("-") else token
    # Bound token width before integer conversion, including Python's own
    # configurable large-integer parsing limit. Canonical decimal only.
    if (not digits or len(digits) > len(str(bound))
            or any(char < "0" or char > "9" for char in digits)
            or (len(digits) > 1 and digits[0] == "0") or token == "-0"):
        raise source.error("integer", f"invalid integer token {token[:80]!r}")
    value = int(token)
    if abs(value) > bound:
        raise source.error("integer_bound", f"integer exceeds bound {bound}")
    return value


def _read_cnf(source: _Source, limits: Limits) -> tuple[int, int, dict[int, tuple[int, ...]]]:
    header: tuple[int, int] | None = None
    database: dict[int, tuple[int, ...]] = {}
    pending: dict[int, None] = {}
    for tokens in source.lines():
        if not tokens or tokens[0] == "c":
            continue
        if tokens[0] == "p":
            if header is not None or len(tokens) != 4 or tokens[1] != "cnf":
                raise source.error("cnf_header", "expected exactly one 'p cnf variables clauses' header")
            variables = _integer(tokens[2], limits.max_variables, source)
            declared = _integer(tokens[3], limits.max_initial_clauses, source)
            if declared > limits.max_live_clauses or declared > limits.max_clause_id:
                raise source.error("clause_limit", "declared clauses exceed a database or id limit")
            header = variables, declared
            continue
        if header is None:
            raise source.error("cnf_header", "clauses precede the DIMACS header")
        variables, declared = header
        for token in tokens:
            literal = _integer(token, variables, source, signed=True)
            if literal == 0:
                if len(database) >= declared:
                    raise source.error("cnf_count", "more clauses than declared")
                database[len(database) + 1] = tuple(pending)
                pending.clear()
            else:
                if len(database) >= declared:
                    raise source.error("cnf_count", "literals follow the declared clauses")
                pending[literal] = None
    if header is None:
        raise source.error("cnf_header", "missing DIMACS header")
    if pending or len(database) != header[1]:
        raise source.error("cnf_count", "unterminated clause or incorrect clause count")
    return header[0], header[1], database


def _rup(clause: tuple[int, ...], hints: list[int], database: dict[int, tuple[int, ...]],
         source: _Source) -> None:
    assignment: dict[int, bool] = {}
    for literal in clause:
        variable, value = abs(literal), literal < 0
        if variable in assignment and assignment[variable] != value:
            raise source.error("tautology", "tautological additions are unsupported")
        assignment[variable] = value
    if not hints:
        raise source.error("missing_conflict", "an addition requires positive hints ending in conflict")
    for position, hint in enumerate(hints):
        reason = database.get(hint)
        if reason is None:
            raise source.error("missing_hint", f"hint clause {hint} is not live")
        unit = 0
        for literal in reason:
            value = assignment.get(abs(literal))
            if value is None:
                if unit:
                    raise source.error("nonunit_hint", f"hint clause {hint} has multiple open literals")
                unit = literal
            elif value == (literal > 0):
                raise source.error("satisfied_hint", f"hint clause {hint} is already satisfied")
        if unit == 0:
            if position != len(hints) - 1:
                raise source.error("excess_hints", "conflict must occur at the final hint")
            return
        assignment[abs(unit)] = unit > 0
    raise source.error("missing_conflict", "the final hint did not produce a conflict")


def check(cnf_path: str | os.PathLike[str], lrat_path: str | os.PathLike[str], *,
          limits: Limits | None = None, allow_gzip: bool = True) -> CheckReceipt:
    """Verify a positive-hint LRAT proof; raise CheckError on every rejection.

    ``.gz`` LRAT inputs are streamed with the same cap on compressed source
    bytes and decompressed payload bytes. SHA256 fields bind the exact source
    files and the decompressed LRAT payload processed by this invocation.
    """
    limits = limits if limits is not None else Limits()
    limits.validate()
    compressed = str(lrat_path).endswith(".gz")
    if compressed and not allow_gzip:
        raise CheckError("gzip_disabled", "gzip proof input is disabled", path=str(lrat_path))
    cnf = _Source(cnf_path, compressed=False, byte_limit=limits.max_cnf_bytes,
                  line_limit=limits.max_line_bytes)
    variables, initial_count, database = _read_cnf(cnf, limits)
    proof = _Source(lrat_path, compressed=compressed, byte_limit=limits.max_proof_bytes,
                    line_limit=limits.max_line_bytes)
    additions = deletions = deletion_records = hint_count = 0
    last_addition = initial_count
    final_empty = 0
    for tokens in proof.lines():
        if not tokens or tokens[0] == "c":
            continue
        if len(tokens) < 3:
            raise proof.error("lrat_grammar", "record is too short")
        identifier = _integer(tokens[0], limits.max_clause_id, proof)
        if tokens[1] == "d":
            if identifier > last_addition:
                raise proof.error("deletion_label", "deletion record has a future id")
            if tokens[-1] != "0":
                raise proof.error("lrat_grammar", "deletion lacks its terminal zero")
            targets = [_integer(token, limits.max_clause_id, proof) for token in tokens[2:-1]]
            if any(target == 0 or target not in database for target in targets):
                raise proof.error("deletion_target", "deletion targets must be positive live clause ids")
            if len(set(targets)) != len(targets):
                raise proof.error("deletion_target", "a clause is deleted twice in one record")
            for target in targets:
                del database[target]
            deletions += len(targets)
            deletion_records += 1
            continue
        if final_empty:
            raise proof.error("after_empty", "the empty clause must be the final addition")
        if identifier <= last_addition:
            raise proof.error("addition_id", "addition ids must be new and strictly increasing")
        try:
            separator = tokens.index("0", 1)
        except ValueError as exc:
            raise proof.error("lrat_grammar", "addition lacks a clause terminator") from exc
        if tokens[-1] != "0" or separator == len(tokens) - 1:
            raise proof.error("lrat_grammar", "addition requires separate clause and hint terminators")
        literals = [_integer(token, variables, proof, signed=True) for token in tokens[1:separator]]
        # Duplicate literals do not change clause semantics or unit status.
        clause = tuple(dict.fromkeys(literals))
        hints = [_integer(token, limits.max_clause_id, proof) for token in tokens[separator + 1:-1]]
        if any(hint == 0 for hint in hints):
            raise proof.error("lrat_grammar", "zero may only terminate the hint list")
        if additions >= limits.max_additions or len(database) >= limits.max_live_clauses:
            raise proof.error("clause_limit", "addition or live database limit exceeded")
        if hint_count + len(hints) > limits.max_hints:
            raise proof.error("hint_limit", "total hint limit exceeded")
        _rup(clause, hints, database, proof)
        database[identifier] = clause
        last_addition = identifier
        additions += 1
        hint_count += len(hints)
        if not clause:
            final_empty = identifier
    if not final_empty:
        raise proof.error("no_empty_clause", "proof did not derive an empty clause")
    return CheckReceipt(
        status="verified_unsat", variables=variables, clauses=initial_count,
        additions=additions, deletions=deletions, deletion_records=deletion_records,
        hints=hint_count, live_clauses=len(database), final_empty=True,
        final_empty_clause=final_empty, final_empty_live=final_empty in database,
        cnf_sha256=cnf.raw_hash.hexdigest(), lrat_sha256=proof.raw_hash.hexdigest(),
        lrat_payload_sha256=proof.payload_hash.hexdigest(), cnf_bytes=cnf.raw_bytes,
        lrat_bytes=proof.raw_bytes, lrat_payload_bytes=proof.payload_bytes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cnf", type=Path)
    parser.add_argument("lrat", type=Path)
    parser.add_argument("--no-gzip", action="store_true")
    parser.add_argument("--max-proof-bytes", type=int, default=Limits.max_proof_bytes)
    parser.add_argument("--max-line-bytes", type=int, default=Limits.max_line_bytes)
    arguments = parser.parse_args()
    try:
        receipt = check(arguments.cnf, arguments.lrat, allow_gzip=not arguments.no_gzip,
                        limits=replace(Limits(), max_proof_bytes=arguments.max_proof_bytes,
                                       max_line_bytes=arguments.max_line_bytes))
    except CheckError as exc:
        print(json.dumps({"status": "rejected", "code": exc.code,
                          "error": str(exc), "path": exc.path, "line": exc.line}, sort_keys=True))
        return 1
    print(json.dumps(asdict(receipt), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
