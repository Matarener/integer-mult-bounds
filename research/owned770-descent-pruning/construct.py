"""Coalesce one exact P104 owned lifetime. Produced by Nick Petalas. Apache-2.0."""
from copy import deepcopy


def need(condition, message):
    if not condition:
        raise ValueError(message)


def roles(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def compact(event):
    """Delete old role 770 after replacing its uses by old role 791."""
    result = event.copy()
    indices = (1, 2) if event[0] in ("ADD", "COPY") else (1,)
    for index in indices:
        value = 791 if result[index] == 770 else result[index]
        result[index] = value - int(value > 770)
    return result


def construct(source):
    need(source["public"] == 770 and source["owned_fields"] == 29,
         "Exact predecessor inventory")
    program = source["program"]
    need(len(program) == 22818, "Exact predecessor length")
    anchors = {
        13473: ["INIT", 791, 549],
        13474: ["COPY", 791, 173, "1", 549],
        13475: ["ADD", 121, 791, "1/2", 549],
        13658: ["INIT", 770, 549],
        13659: ["COPY", 770, 791, "1", 549],
        13660: ["SCALE", 770, "1/2", 549],
        13661: ["MOVE", 770, 549, 553, True],
        15424: ["CLEAR", 770, 593],
        15591: ["CLEAR", 791, 549],
    }
    need(all(program[i] == event for i, event in anchors.items()),
         "Exact coalescence anchors")
    uses = [i for i, event in enumerate(program) if 791 in roles(event)]
    need(uses == [13473, 13474, 13475, 13659, 15591],
         "Source lifetime has no hidden use")
    uses = [i for i, event in enumerate(program) if 770 in roles(event)]
    need(uses[0] == 13658 and uses[-1] == 15424,
         "Duplicate role has one enclosed lifetime")
    need(sum(program[i][0] == "INIT" for i in uses) == 1,
         "No second duplicate initialization")
    output = []
    for index, event in enumerate(program):
        if index in (13658, 13659, 13660, 15591):
            continue
        if index == 13661:
            output.append(compact(["SCALE", 791, "1/2", 549]))
        output.append(compact(event))
    result = deepcopy(source)
    result["program"] = output
    result["owned_fields"] = 28
    need(len(output) == 22815, "Exact edited length")
    return result
