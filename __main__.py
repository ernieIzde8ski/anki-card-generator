#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
from typing import IO, Iterable


def parsed_args():
    parser = argparse.ArgumentParser(
        description="Converts a newline-separated file into an Anki deck"
    )

    parser.add_argument("-n", "--note_type", default="Cloze")
    parser.add_argument("-d", "--deck-name")
    parser.add_argument("-if", "--input-file", dest="input", type=Path, required=True)
    parser.add_argument("-of", "--output-file", dest="output", type=Path, required=False)
    parser.add_argument("--debug", action="store_true")

    resp = parser.parse_args()

    if not resp.input.exists():
        print(f"error: file {resp.input} does not exist", file=sys.stderr)
        exit(1)

    if resp.deck_name is None:
        resp.deck_name = resp.input.name.removesuffix("".join(resp.input.suffixes))

    return resp


_re_comment_pattern = re.compile(r"(?<![^\\])#[^\n]+$")


def read_input(path: Path) -> Iterable[str]:
    with open(path, "r") as file:
        lines = file.readlines()

    for line in lines:
        line = re.sub(_re_comment_pattern, "", line).strip()
        if line:
            yield line.replace("\t", "    ")


_output_header = r"""
#separator:tab
#html:false
#notetype column:1
#deck column:2
#tags column:5
""".strip()


def emit_output(
    stream: IO[str], cards: Iterable[str], deck_name: str, note_type: str
) -> None:
    print(_output_header, file=stream)

    for card in cards:
        print(note_type, deck_name, card, "", "", sep="\t", file=stream)


def main():
    args = parsed_args()

    if args.debug:
        print(args)

    cards = read_input(args.input)

    if args.output is None:
        emit_output(sys.stdout, cards, args.deck_name, args.note_type)
    else:
        with open(args.output, "w") as file:
            emit_output(file, cards, args.deck_name, args.note_type)


main()
