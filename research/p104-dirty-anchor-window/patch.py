"""One dirty-output sharing rewrite on DreamingOfClouds's PR5907 word.

Produced by Nick Petalas. Apache-2.0.
"""
from copy import deepcopy

START = 509
STOP = 672
REMOVED = {
    509: ["ADD", 158, 711, "-2", 3],
    660: ["ADD", 158, 133, "1", 3],
    663: ["ADD", 158, 721, "2", 3],
    664: ["ADD", 158, 21, "1", 3],
}
ANCHOR_START = 667
ANCHOR_END = 671
COMMON = {133: "1", 721: "2", 21: "1", 711: "-2"}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def check_window(program):
    """Check the exact sharing premises, including absence of observations."""
    need(len(program) == 25998, "Expected source event count")
    for index, event in REMOVED.items():
        need(program[index] == event, "Literal removed event")
    anchor_events = []
    for event in program[START:STOP]:
        need(event[0] == "ADD" and event[-1] == 3, "Same-frame ADD window")
        _, destination, source, coefficient, _ = event
        need(source not in (158, 159), "No intermediate output observation")
        need(destination not in COMMON, "Shared sources remain constant")
        if destination == 159:
            anchor_events.append((source, coefficient))
    need(dict(anchor_events) == COMMON and len(anchor_events) == 4,
         "Anchor acquires exactly the shared form")
    need(program[ANCHOR_START][1] == program[ANCHOR_END][1] == 159,
         "Anchor endpoints")
    need(all(event[1] != 159 for event in program[START:ANCHOR_START]),
         "No earlier anchor update")


def rewrite(word):
    check_window(word["program"])
    out = deepcopy(word)
    program = []
    for index, event in enumerate(word["program"]):
        if index == ANCHOR_START:
            program.append(["ADD", 158, 159, "-1", 3])
        if index not in REMOVED:
            program.append(event)
        if index == ANCHOR_END:
            program.append(["ADD", 158, 159, "1", 3])
    out["program"] = program
    return out
