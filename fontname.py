#!/usr/bin/env python3

# ==========================================================================
# fontname.py (modified for output files)
# Copyright 2019 Christopher Simpkins
# MIT License
#
# Dependencies:
#   1) Python 3.6+ interpreter
#   2) fonttools Python library (https://github.com/fonttools/fonttools)
#         - install with `pip3 install fonttools`
#
# Usage:
#   python3 fontname.py "Font Family:Weight" path/to/font.{ttf,otf} \
#                       "Font Family:Weight" path/to/font.{ttf,otf}
#
# Notes:
#   - Quotes required if family or weight contains spaces
#   - Multiple family/font pairs supported in one run
#   - Output is saved as: NewFontFamily-Weight.{ttf,otf}
# ===========================================================================

import os
import sys
from fontTools import ttLib


def main(argv):
    print(" ")

    # Check args length (must be even: family+style, font path)
    if len(argv) < 2 or len(argv) % 2 != 0:
        sys.stderr.write(
            f"[fontname.py] ERROR: arguments must be pairs of \"Font Family:Weight\" and font path.{os.linesep}"
        )
        sys.stderr.write(
            f"Usage: python3 fontname.py \"Font Family:Weight\" path/to/font.{ttf,otf} ...{os.linesep}"
        )
        sys.exit(1)

    # Process in pairs
    for i in range(0, len(argv), 2):
        try:
            family_style = str(argv[i])
            font_path = argv[i + 1]
        except Exception as e:
            sys.stderr.write(
                f"[fontname.py] ERROR: Unable to parse arguments. {e}{os.linesep}"
            )
            sys.exit(1)

        # Split family and style
        if ":" not in family_style:
            sys.stderr.write(
                f"[fontname.py] ERROR: '{family_style}' must be in 'Font Family:Weight' format.{os.linesep}"
            )
            sys.exit(1)

        font_name, style = family_style.split(":", 1)
        font_name, style = font_name.strip(), style.strip()

        # Verify font file exists
        if not file_exists(font_path):
            sys.stderr.write(
                f"[fontname.py] ERROR: the path '{font_path}' does not appear to be a valid file path.{os.linesep}"
            )
            sys.exit(1)

        tt = ttLib.TTFont(font_path)
        namerecord_list = tt["name"].names

        # Strings to update
        postscript_font_name = font_name.replace(" ", "")
        nameID1_string = font_name
        nameID16_string = font_name
        nameID4_string = f"{font_name} {style}"
        nameID6_string = f"{postscript_font_name}-{style.replace(' ', '')}"

        # Update OpenType name records
        for record in namerecord_list:
            if record.nameID == 1:
                record.string = nameID1_string
            elif record.nameID == 4:
                record.string = nameID4_string
            elif record.nameID == 6:
                record.string = nameID6_string
            elif record.nameID == 16:
                record.string = nameID16_string
            elif record.nameID == 2:  # Style name
                record.string = style

        # CFF table naming (if present)
        if "CFF " in tt:
            try:
                cff = tt["CFF "]
                cff.cff[0].FamilyName = nameID1_string
                cff.cff[0].FullName = nameID4_string
                cff.cff.fontNames = [nameID6_string]
            except Exception as e:
                sys.stderr.write(
                    f"[fontname.py] ERROR: unable to write new names to CFF table: {e}"
                )

        # Build new filename
        ext = os.path.splitext(font_path)[1]
        safe_style = style.replace(" ", "")
        new_filename = f"{postscript_font_name}-{safe_style}{ext}"

        # Save updated font as new file
        try:
            tt.save(new_filename)
            print(
                f"[OK] Saved '{new_filename}' with family '{font_name}' and style '{style}'"
            )
        except Exception as e:
            sys.stderr.write(
                f"[fontname.py] ERROR: unable to save new font file '{new_filename}'. {os.linesep}"
            )
            sys.stderr.write(f"{e}{os.linesep}")
            sys.exit(1)


def file_exists(filepath):
    """Tests for existence of a file on the string filepath"""
    return os.path.exists(filepath) and os.path.isfile(filepath)


if __name__ == "__main__":
    main(sys.argv[1:])
