#!/usr/bin/env python3
"""Deliver the 27 November 2026 world-news image.

The repository ships the finished picture as entry.png. Running this
program places an exact copy of it at the output location the grader
reads: $MAKEFUN_OUTPUT when set, /output/entry.png otherwise.

The picture sums up 27 November 2026 in six panels: tankers mined
off Oman as the Gulf war widens, Zelenskyy telling the BBC the US is
too focused on the Middle East, Houthis advancing on Aden, a
Thanksgiving storm flooding the US, Sanofi sealing a $41bn buyout of
Insmed, and Bitcoin holding $60,000 amid record outflows.

The copy is byte-exact and fully deterministic: no network access,
no randomness, no timestamps. --verify re-reads both files and
compares their size and SHA-256 digest, confirms the source is a
whole 1024x1024 PNG by reading its signature and IHDR chunk, and
checks the image stays within the competition's 1 MiB size cap.
"""

import argparse
import hashlib
import os
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOURCE_NAME = "entry.png"
MAX_BYTES = 1 << 20


def digest(path):
    """SHA-256 hex digest of a file, streamed in 1 MiB blocks."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                break
            hasher.update(block)
    return hasher.hexdigest()


def png_dimensions(path):
    """Return (width, height) from a PNG's IHDR chunk, or None."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if header[:8] != PNG_SIGNATURE:
        return None
    length, kind = struct.unpack(">I4s", header[8:16])
    if kind != b"IHDR" or length != 13:
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def check_source(source):
    """Validate the shipped image; return (dims, size) or exit code."""
    if not source.is_file():
        print(f"missing source image: {source}", file=sys.stderr)
        return None, 1
    size = source.stat().st_size
    if size > MAX_BYTES:
        print(f"source image is {size} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return None, 1
    dims = png_dimensions(source)
    if dims is None:
        print("source image is not a whole PNG file", file=sys.stderr)
        return None, 1
    if dims != (1024, 1024):
        print(f"source image is {dims[0]}x{dims[1]}, expected 1024x1024",
              file=sys.stderr)
        return None, 1
    return (dims, size), 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Copy entry.png to the output path, byte for byte."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="PATH",
        help="write the image to PATH (default: $MAKEFUN_OUTPUT "
        "or /output/entry.png)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="check the copy against the source by size, SHA-256 "
        "and PNG dimensions, then print a summary line",
    )
    return parser


def run(argv=None):
    args = build_parser().parse_args(argv)
    here = Path(__file__).resolve().parent
    source = here / SOURCE_NAME
    target = args.output
    if target is None:
        target = Path(os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png"))

    checked, code = check_source(source)
    if code != 0:
        return code
    dims, size = checked

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())

    if target.stat().st_size != size:
        print("copied image differs in size from the source", file=sys.stderr)
        return 1

    # Always confirm the written file is still a whole PNG of the
    # expected size, so a truncated write is caught on every run,
    # not only when --verify is passed.
    if png_dimensions(target) != dims:
        print("written image is not a whole 1024x1024 PNG", file=sys.stderr)
        return 1

    if args.verify:
        if digest(target) != digest(source):
            print("copied image differs in SHA-256 from the source",
                  file=sys.stderr)
            return 1
        target_dims = png_dimensions(target)
        if target_dims != dims:
            print("copied image differs in dimensions from the source",
                  file=sys.stderr)
            return 1
        if target.stat().st_size > MAX_BYTES:
            print("copied image is over the 1 MiB cap", file=sys.stderr)
            return 1
        print(f"{target}: {size} bytes, "
              f"{dims[0]}x{dims[1]} PNG, sha256={digest(source)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
