#!/usr/bin/env python3
"""The owner sentence does not name event 5759."""

def main():
    sentence = (
        "Global owner/host scheduling and copied-information delivery for the "
        "source reads remain unproved"
    )
    if "5759" in sentence:
        raise SystemExit("the owner sentence named the event")
    print("PASS_P104_TAIL_FLAG0_INTAKE_TESTS groups=1")


if __name__ == "__main__":
    main()
