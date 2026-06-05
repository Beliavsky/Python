#!/usr/bin/env python3
"""
Convert readable scientific notation in a text file to fixed decimal notation.

Default rule:
    convert x if 1e-4 <= abs(x) < 1e6

Examples:
    1.00000E+00   -> 1.00000
   -3.12042E-01   -> -0.312042
    1.42550E-04   -> 0.000142550
    8.24236E-05   -> kept by default

Usage:
    python fix_sci_notation.py input.txt
    python fix_sci_notation.py input.txt output.txt
    python fix_sci_notation.py input.txt output.txt --fixed-min 1e-6
    python fix_sci_notation.py input.txt output.txt --fixed-min 0 --fixed-max 1e4
"""

import argparse
import re
from decimal import Decimal, InvalidOperation


SCI_RE = re.compile(
    r"""
    (?<![A-Za-z0-9_.])
    [+-]?
    (?:
        (?:\d+\.\d*) |
        (?:\.\d+) |
        (?:\d+)
    )
    [Ee]
    [+-]?
    \d+
    (?![A-Za-z0-9_.])
    """,
    re.VERBOSE,
)


def decimal_arg(s):
    """Parse a command-line argument as Decimal."""
    try:
        x = Decimal(s)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"invalid decimal value: {s}") from exc

    if x < 0:
        raise argparse.ArgumentTypeError("value must be nonnegative")

    return x


def fixed_decimal_string(s):
    """Return the fixed-point decimal representation of a scientific number."""
    try:
        x = Decimal(s)
    except InvalidOperation:
        return s

    out = format(x, "f")

    # Avoid "-0.0000" style output.
    if Decimal(out) == 0:
        out = out.lstrip("-")

    return out


def should_convert(
    s,
    fixed_min=Decimal("1e-4"),
    fixed_max=Decimal("1e6"),
    max_fixed_len=12,
    max_leading_frac_zeros=3,
):
    """
    Decide whether fixed notation is more readable.

    Convert only when:
        fixed_min <= abs(x) < fixed_max

    Also avoid converting when fixed notation is visually too long.
    """
    try:
        x = Decimal(s)
    except InvalidOperation:
        return False

    ax = abs(x)

    if ax == 0:
        return True

    if ax < fixed_min:
        return False

    if ax >= fixed_max:
        return False

    fixed = fixed_decimal_string(s)

    tmp = fixed.lstrip("+-")

    # Count leading zeros after the decimal point.
    leading_frac_zeros = 0
    if tmp.startswith("0."):
        frac = tmp[2:]
        for ch in frac:
            if ch == "0":
                leading_frac_zeros += 1
            else:
                break

    if leading_frac_zeros > max_leading_frac_zeros:
        return False

    # Ignore sign when judging visual length.
    if len(tmp) > max_fixed_len:
        return False

    return True


def convert_text(
    text,
    fixed_min=Decimal("1e-4"),
    fixed_max=Decimal("1e6"),
    max_fixed_len=12,
    max_leading_frac_zeros=3,
):
    def convert_match(match):
        s = match.group(0)

        if not should_convert(
            s,
            fixed_min=fixed_min,
            fixed_max=fixed_max,
            max_fixed_len=max_fixed_len,
            max_leading_frac_zeros=max_leading_frac_zeros,
        ):
            return s

        return fixed_decimal_string(s)

    return SCI_RE.sub(convert_match, text)


def main():
    parser = argparse.ArgumentParser(
        description="Convert selected scientific notation values to fixed notation."
    )

    parser.add_argument("input", help="input text file")
    parser.add_argument("output", nargs="?", help="output text file")

    parser.add_argument(
        "--fixed-min",
        type=decimal_arg,
        default=Decimal("1e-4"),
        help="smallest absolute value to convert to fixed notation; default: 1e-4",
    )

    parser.add_argument(
        "--fixed-max",
        type=decimal_arg,
        default=Decimal("1e6"),
        help="largest absolute value to convert to fixed notation; default: 1e6",
    )

    parser.add_argument(
        "--max-fixed-len",
        type=int,
        default=12,
        help="maximum length of fixed representation, excluding sign; default: 12",
    )

    parser.add_argument(
        "--max-leading-frac-zeros",
        type=int,
        default=3,
        help=(
            "maximum allowed leading zeros after decimal point before first "
            "nonzero digit; default: 3"
        ),
    )

    args = parser.parse_args()

    if args.fixed_min >= args.fixed_max:
        raise SystemExit("--fixed-min must be less than --fixed-max")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    converted = convert_text(
        text,
        fixed_min=args.fixed_min,
        fixed_max=args.fixed_max,
        max_fixed_len=args.max_fixed_len,
        max_leading_frac_zeros=args.max_leading_frac_zeros,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            f.write(converted)
    else:
        print(converted, end="")


if __name__ == "__main__":
    main()
