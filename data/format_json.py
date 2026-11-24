"""
Pretty-print a minified JSON file for easier reading in an editor.

Default use: formats hotpot_dev_fullwiki_v1.json into a new file with
2-space indentation. The formatted file can be much larger than the original.
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load JSON and write a human-readable (indented) version."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="hotpot_dev_fullwiki_v1.json",
        help="Path to the minified JSON file (default: hotpot_dev_fullwiki_v1.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output path (default: <input_stem>_formatted.json next to input)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Spaces per indentation level (default: 2)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="If the root is a list, write only the first N items (handy for a quick preview)",
    )
    return parser.parse_args()


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_formatted{input_path.suffix}")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else default_output_path(input_path)

    print(f"Reading {input_path} ...")
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if args.limit is not None:
        if not isinstance(data, list):
            print("Error: --limit only applies when the JSON root is a list.", file=sys.stderr)
            return 1
        data = data[: args.limit]
        print(f"Writing first {len(data)} item(s) only.")

    print(f"Writing {output_path} (indent={args.indent}) ...")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=args.indent, ensure_ascii=False)
        f.write("\n")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())