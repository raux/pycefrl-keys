"""
pycefrl-keyword: Identifies Python CEFR proficiency levels using regular expressions.

Instead of AST-based analysis, this package uses regex pattern matching to detect
Python language constructs and assign CEFR-inspired proficiency codes (A1–C2).
"""

from .analyzer import analyze_file, analyze_directory, save_results

__version__ = "0.1.0"
__all__ = ["analyze_file", "analyze_directory", "save_results"]
