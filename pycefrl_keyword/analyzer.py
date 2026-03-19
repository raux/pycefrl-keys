"""
Core regex-based analyzer for pycefrl-keyword.

Scans Python source files using the patterns defined in :mod:`patterns` and
produces per-match records that include the repository name, file name,
matched class description, start/end line numbers, column offset, and the
CEFR proficiency level.
"""

import csv
import json
import logging
import os
import re

from .patterns import compiled_patterns


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _line_info(content: str, start: int, end: int) -> tuple[int, int, int]:
    """Return ``(start_line, end_line, col_offset)`` for character indices in *content*.

    Line numbers are 1-based; column offset is 0-based (characters from the
    start of the line).
    """
    line_start = content.rfind("\n", 0, start) + 1  # start of the line containing `start`
    start_line = content.count("\n", 0, start) + 1
    end_line = content.count("\n", 0, end) + 1
    col_offset = start - line_start
    return start_line, end_line, col_offset


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_file(
    file_path: str,
    repo_name: str,
    file_label: str | None = None,
) -> list[dict]:
    """Analyze a single Python file and return a list of match records.

    Each record is a :class:`dict` with the following keys:

    * ``repo``         – repository (or directory) name
    * ``file``         – file label stored in results; defaults to the
                         basename of *file_path* but can be overridden via
                         *file_label* (e.g., to store a relative path when
                         called from :func:`analyze_directory`)
    * ``class``        – human-readable description of the matched construct
    * ``start_line``   – 1-based line number where the match starts
    * ``end_line``     – 1-based line number where the match ends
    * ``displacement`` – 0-based column offset of the match start
    * ``level``        – CEFR proficiency level code (A1–C2)

    Parameters
    ----------
    file_path:
        Absolute or relative path to a ``.py`` file.
    repo_name:
        Label used for the ``repo`` field in every returned record.
    file_label:
        Optional override for the ``file`` field.  When *None* (default),
        ``os.path.basename(file_path)`` is used.
    """
    results: list[dict] = []
    file_name = file_label if file_label is not None else os.path.basename(file_path)

    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except OSError as exc:
        logging.warning("Cannot read %s: %s", file_path, exc)
        return results

    for regex, class_name, level in compiled_patterns():
        for match in regex.finditer(content):
            start_line, end_line, col_offset = _line_info(
                content, match.start(), match.end()
            )
            results.append(
                {
                    "repo": repo_name,
                    "file": file_name,
                    "class": class_name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "displacement": col_offset,
                    "level": level,
                }
            )

    return results


def analyze_directory(dir_path: str) -> list[dict]:
    """Recursively analyze all ``.py`` files under *dir_path*.

    Parameters
    ----------
    dir_path:
        Root directory to scan.

    Returns
    -------
    list[dict]
        Concatenated results from :func:`analyze_file` for every Python file
        found under *dir_path*.  The ``file`` field in each record is a path
        relative to *dir_path*, so files with the same basename but in
        different sub-directories remain distinguishable.
    """
    repo_name = os.path.basename(os.path.abspath(dir_path))
    all_results: list[dict] = []

    for root, _dirs, files in os.walk(dir_path):
        for file_name in sorted(files):
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(file_path, dir_path)
                file_results = analyze_file(file_path, repo_name, file_label=rel_path)
                all_results.extend(file_results)
                logging.debug(
                    "Analyzed %s → %d match(es)", rel_path, len(file_results)
                )

    return all_results


def save_results(results: list[dict], output_dir: str = ".") -> tuple[str, str]:
    """Write analysis results to ``data.json`` and ``data.csv``.

    The JSON structure mirrors the original PyCerf output::

        {
          "<repo>": {
            "<file>": [
              {
                "Class": "...",
                "Start Line": "...",
                "End Line": "...",
                "Displacement": "...",
                "Level": "..."
              },
              ...
            ]
          }
        }

    Parameters
    ----------
    results:
        List of records as returned by :func:`analyze_file` or
        :func:`analyze_directory`.
    output_dir:
        Directory where ``data.json`` and ``data.csv`` are written.
        Defaults to the current working directory.

    Returns
    -------
    tuple[str, str]
        Absolute paths ``(json_path, csv_path)``.
    """
    os.makedirs(output_dir, exist_ok=True)

    # --- JSON ---------------------------------------------------------------
    json_data: dict = {}
    for r in results:
        repo = r["repo"]
        file = r["file"]
        json_data.setdefault(repo, {}).setdefault(file, []).append(
            {
                "Class": r["class"],
                "Start Line": str(r["start_line"]),
                "End Line": str(r["end_line"]),
                "Displacement": str(r["displacement"]),
                "Level": r["level"],
            }
        )

    json_path = os.path.join(output_dir, "data.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(json_data, fh, indent=2)

    # --- CSV ----------------------------------------------------------------
    csv_headers = [
        "Repo",
        "File",
        "Class",
        "Start Line",
        "End Line",
        "Displacement",
        "Level",
    ]
    csv_path = os.path.join(output_dir, "data.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(csv_headers)
        for r in results:
            writer.writerow(
                [
                    r["repo"],
                    r["file"],
                    r["class"],
                    r["start_line"],
                    r["end_line"],
                    r["displacement"],
                    r["level"],
                ]
            )

    return os.path.abspath(json_path), os.path.abspath(csv_path)
