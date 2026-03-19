#!/usr/bin/env python3
"""
pycefrl-keyword command-line interface.

Usage
-----
Analyze a local directory::

    python pycefrl_keyword_cli.py directory <path>

Analyze a single Python file::

    python pycefrl_keyword_cli.py file <path>

Results are written to ``data.json`` and ``data.csv`` in the current directory.
Pass ``-v`` / ``--verbose`` to see per-file progress on stderr.
"""

import logging
import os
import sys

from pycefrl_keyword.analyzer import analyze_directory, analyze_file, save_results


def _usage() -> None:
    print(__doc__)
    sys.exit(1)


def main() -> None:
    args = sys.argv[1:]

    # Strip optional verbose flag
    verbose = False
    if "-v" in args or "--verbose" in args:
        verbose = True
        args = [a for a in args if a not in ("-v", "--verbose")]

    if len(args) < 2:
        _usage()

    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="  %(message)s")

    type_option = args[0].lower()
    option = args[1]

    if type_option == "directory":
        if not os.path.isdir(option):
            sys.exit(f"ERROR: '{option}' is not a directory.")
        print(f"Analyzing directory: {option}")
        results = analyze_directory(option)
    elif type_option == "file":
        if not os.path.isfile(option):
            sys.exit(f"ERROR: '{option}' is not a file.")
        repo_name = os.path.basename(os.path.dirname(os.path.abspath(option)))
        print(f"Analyzing file: {option}")
        results = analyze_file(option, repo_name)
    else:
        sys.exit(f"ERROR: Unknown option '{type_option}'. Use 'directory' or 'file'.")

    if not results:
        print("No patterns found.")
        sys.exit(0)

    json_path, csv_path = save_results(results)
    print(f"\nAnalysis complete: {len(results)} pattern match(es) found.")
    print(f"  JSON → {json_path}")
    print(f"  CSV  → {csv_path}")


if __name__ == "__main__":
    main()
