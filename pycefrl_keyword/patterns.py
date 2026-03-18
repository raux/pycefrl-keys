"""
Regex patterns for identifying Python CEFR proficiency level constructs.

Each pattern maps a regex to a human-readable class name and a CEFR level code
(A1–C2), mirroring the level assignments from the original PyCerf configuration.

Patterns are applied with re.MULTILINE so ``^``/``$`` match per line.  More
specific patterns are listed first within each level so that callers can rely on
ordering when they want to skip lower-priority matches.
"""

import re
from collections import namedtuple

Pattern = namedtuple("Pattern", ["pattern", "class_name", "level"])

# ---------------------------------------------------------------------------
# A1  – Beginner
# ---------------------------------------------------------------------------
_A1 = [
    # print(...)
    Pattern(r"\bprint\s*\(", "Print", "A1"),
    # Simple return statement
    Pattern(r"^\s*return\b", "Simple Return", "A1"),
    # Simple function definition with no parameters
    Pattern(r"^\s*def\s+[A-Za-z_]\w*\s*\(\s*\)\s*:", "Simple Function Definition", "A1"),
    # Simple for loop (single variable, not tuple unpacking, not range/list/tuple literal)
    Pattern(
        r"^\s*for\s+[A-Za-z_]\w*\s+in\s+(?!\[)(?!\()(?!range\s*\()(?!zip\s*\()(?!map\s*\()(?!enumerate\s*\()\S",
        "Simple For Loop",
        "A1",
    ),
    # Simple if statement (not __name__ guard, not ternary context)
    Pattern(r"^\s*if\s+(?!__name__\s*==)", "Simple If Statement", "A1"),
    # Simple list literal (no nested list/dict/comprehension inside)
    Pattern(r"\[(?:[^\[\]{}\n]*)\](?!\s*for\b)", "Simple List", "A1"),
    # Simple tuple literal (contains at least one comma)
    Pattern(
        r"(?<!\w)\((?:[^()\[\]{}\n]*,)+[^()\[\]{}\n]*\)(?!\s*for\b)",
        "Simple Tuple",
        "A1",
    ),
    # Simple assignment  (not augmented, not comparison ==)
    Pattern(r"^\s*[A-Za-z_]\w*\s*=(?!=)\s*[^\n]", "Simple Assignment", "A1"),
]

# ---------------------------------------------------------------------------
# A2  – Elementary
# ---------------------------------------------------------------------------
_A2 = [
    # Augmented assignment  (+=, -=, *=, …)
    Pattern(
        r"^\s*[A-Za-z_]\w*\s*(?:\+|-|\*{1,2}|\/\/|\/|%|&|\||\^|<<|>>)=\s*",
        "Augmented Assignment",
        "A2",
    ),
    # import <module>
    Pattern(r"^\s*import\s+[A-Za-z_]", "Import", "A2"),
    # from <module> import <name>  (absolute, non-star)
    Pattern(
        r"^\s*from\s+[A-Za-z_]\w*\s+import\s+(?!\*)[A-Za-z_*]",
        "From Import",
        "A2",
    ),
    # open() call
    Pattern(r"\bopen\s*\(", "File open() call", "A2"),
    # File I/O method calls (.write, .read, .readline, .writelines)
    Pattern(r"\.(?:write|writelines|read|readline)\s*\(", "File I/O method call", "A2"),
    # range() call (common in A2 for-loops)
    Pattern(r"\brange\s*\(", "range() call", "A2"),
    # For loop with range()
    Pattern(r"^\s*for\s+[A-Za-z_]\w*\s+in\s+range\s*\(", "For Loop with range()", "A2"),
    # For loop iterating over a list literal
    Pattern(r"^\s*for\s+[A-Za-z_]\w*\s+in\s+\[", "For Loop over List", "A2"),
    # For loop iterating over a tuple literal
    Pattern(r"^\s*for\s+[A-Za-z_]\w*\s+in\s+\(", "For Loop over Tuple", "A2"),
    # For loop with tuple unpacking  (for x, y in ...)
    Pattern(
        r"^\s*for\s+[A-Za-z_]\w*\s*,\s*[A-Za-z_]\w*\s+in\s+",
        "For Loop with Tuple Unpacking",
        "A2",
    ),
    # Nested list literal — one or more inner lists ([…[…]…] or [[…],[…]])
    Pattern(
        r"\[(?:[^\[\]]*\[[^\[\]]*\])+[^\[\]]*\]",
        "Nested List",
        "A2",
    ),
    # Nested tuple  ((…(…,…)…))
    Pattern(
        r"\((?:[^()]*)\((?:[^()]*,)[^()]*\)(?:[^()]*)\)",
        "Nested Tuple",
        "A2",
    ),
    # Simple dict literal  (no nested dict/comprehension)
    Pattern(r"\{(?:[^{}\n]*:[^{}\n]*)\}(?!\s*for\b)", "Simple Dictionary", "A2"),
    # Attribute access on self  (self.attr — not dunder)
    Pattern(r"\bself\.[A-Za-z_]\w*\b(?!__)", "Attribute Access (self)", "A2"),
]

# ---------------------------------------------------------------------------
# B1  – Intermediate
# ---------------------------------------------------------------------------
_B1 = [
    # break
    Pattern(r"^\s*break\b", "Break", "B1"),
    # continue
    Pattern(r"^\s*continue\b", "Continue", "B1"),
    # pass
    Pattern(r"^\s*pass\b", "Pass", "B1"),
    # while loop
    Pattern(r"^\s*while\s+", "While Loop", "B1"),
    # lambda expression
    Pattern(r"\blambda\b[^:]*:", "Lambda Expression", "B1"),
    # Function with *args
    Pattern(
        r"^\s*def\s+[A-Za-z_]\w*\s*\([^)]*\*[A-Za-z_]\w+[^)]*\)\s*:",
        "Function with *args",
        "B1",
    ),
    # Function with **kwargs
    Pattern(
        r"^\s*def\s+[A-Za-z_]\w*\s*\([^)]*\*\*[A-Za-z_]\w+[^)]*\)\s*:",
        "Function with **kwargs",
        "B1",
    ),
    # Function with keyword-only arguments  (*, param)
    Pattern(
        r"^\s*def\s+[A-Za-z_]\w*\s*\([^)]*,\s*\*\s*,",
        "Function with Keyword-Only Arguments",
        "B1",
    ),
    # Function with any arguments (catch-all after more specific patterns above)
    Pattern(
        r"^\s*def\s+[A-Za-z_]\w*\s*\([^)]*[A-Za-z_]\w*[^)]*\)\s*:",
        "Function with Arguments",
        "B1",
    ),
    # Simple class definition (no base classes)
    Pattern(r"^\s*class\s+[A-Za-z_]\w*\s*(?::\s*$|\(\s*\)\s*:)", "Simple Class Definition", "B1"),
    # Class with inheritance
    Pattern(
        r"^\s*class\s+[A-Za-z_]\w*\s*\([A-Za-z_][^)]+\)\s*:",
        "Class with Inheritance",
        "B1",
    ),
    # __init__ method definition
    Pattern(r"^\s*def\s+__init__\s*\(", "__init__ Method", "B1"),
    # try block
    Pattern(r"^\s*try\s*:", "Try Block", "B1"),
    # except clause
    Pattern(r"^\s*except\b", "Except Clause", "B1"),
    # raise statement
    Pattern(r"^\s*raise\b", "Raise Exception", "B1"),
    # with statement
    Pattern(r"^\s*with\s+", "With Statement", "B1"),
    # Ternary (inline if-else) expression
    Pattern(
        r"\S.*\s+if\s+\S.*\s+else\s+\S",
        "Ternary If Expression",
        "B1",
    ),
    # From relative import  (from . import / from .pkg import)
    Pattern(r"^\s*from\s+\.+", "From Relative Import", "B1"),
    # From star import
    Pattern(r"^\s*from\s+\S+\s+import\s+\*", "From Star Import", "B1"),
    # Import / from-import with alias  (as …)
    Pattern(
        r"\b(?:import\s+\S+|from\s+\S+\s+import\s+\S+)\s+as\s+[A-Za-z_]\w*",
        "Import with Alias",
        "B1",
    ),
    # Nested dict literal  ({…{…:…}…})
    Pattern(r"\{[^{}]*\{[^{}]*:[^{}]*\}[^{}]*\}", "Nested Dictionary", "B1"),
    # Dict with list value  ({…: […]…})
    Pattern(r"\{[^{}]*:\s*\[[^\[\]]*\][^{}]*\}", "Dictionary with List", "B1"),
]

# ---------------------------------------------------------------------------
# B2  – Upper-Intermediate
# ---------------------------------------------------------------------------
_B2 = [
    # if __name__ == '__main__'
    Pattern(
        r"""\bif\s+__name__\s*==\s*['"]__main__['"]""",
        'If __name__ == "__main__"',
        "B2",
    ),
    # finally clause
    Pattern(r"^\s*finally\s*:", "Finally Clause", "B2"),
    # assert statement
    Pattern(r"^\s*assert\b", "Assert Statement", "B2"),
    # __class__ dunder attribute
    Pattern(r"\b__class__\b", "__class__ Attribute", "B2"),
    # __dict__ dunder attribute
    Pattern(r"\b__dict__\b", "__dict__ Attribute", "B2"),
    # Function with default parameter values  (def f(a=1):)
    Pattern(
        r"^\s*def\s+[A-Za-z_]\w*\s*\([^)]*=[^)]*\)\s*:",
        "Function with Default Arguments",
        "B2",
    ),
    # Dict of dicts containing a list  ({k: {k2: […]}})
    Pattern(
        r"\{[^{}]*:\s*\{[^{}]*:\s*\[[^\[\]]*\][^{}]*\}[^{}]*\}",
        "Dict of Dict with List",
        "B2",
    ),
]

# ---------------------------------------------------------------------------
# C1  – Advanced
# ---------------------------------------------------------------------------
_C1 = [
    # yield / yield from  → generator function
    Pattern(r"\byield\b", "Generator Function (yield)", "C1"),
    # List comprehension  ([expr for var in iter])
    Pattern(
        r"\[[^\[\]]+\s+for\s+[A-Za-z_]\w*\s+in\s+[^\[\]]+\]",
        "List Comprehension",
        "C1",
    ),
    # Dict comprehension  ({k: v for var in iter})
    Pattern(
        r"\{[^{}]+:\s*[^{}]+\s+for\s+[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)?\s+in\s+[^{}]+\}",
        "Dict Comprehension",
        "C1",
    ),
    # Generator expression — lazy .+? allows nested calls like range(n)
    Pattern(
        r"\(.+?\s+for\s+[A-Za-z_]\w*\s+in\s+.+?\)",
        "Generator Expression",
        "C1",
    ),
    # @property decorator
    Pattern(r"^\s*@property\b", "Property Decorator", "C1"),
    # @classmethod decorator
    Pattern(r"^\s*@classmethod\b", "Class Method Decorator", "C1"),
    # @staticmethod decorator
    Pattern(r"^\s*@staticmethod\b", "Static Method Decorator", "C1"),
    # __slots__ class attribute
    Pattern(r"\b__slots__\b", "__slots__ Attribute", "C1"),
    # Standard library module imports that signal advanced usage
    Pattern(
        r"^\s*(?:import|from)\s+(struct|pickle|shelve|dbm|re|importlib)\b",
        "Standard Library Module Import",
        "C1",
    ),
]

# ---------------------------------------------------------------------------
# C2  – Proficiency
# ---------------------------------------------------------------------------
_C2 = [
    # map() built-in
    Pattern(r"\bmap\s*\(", "map() Function Call", "C2"),
    # zip() built-in
    Pattern(r"\bzip\s*\(", "zip() Function Call", "C2"),
    # enumerate() built-in
    Pattern(r"\benumerate\s*\(", "enumerate() Function Call", "C2"),
    # super() call
    Pattern(r"\bsuper\s*\(", "super() Function Call", "C2"),
    # General decorator (any @name not already captured by @property/@classmethod/@staticmethod)
    Pattern(r"^\s*@[A-Za-z_]\w*(?:\(.*\))?\s*$", "Decorator", "C2"),
    # Metaclass keyword argument  (class Foo(metaclass=Meta):)
    Pattern(r"\bmetaclass\s*=\s*", "Metaclass Definition", "C2"),
    # __new__ method
    Pattern(r"^\s*def\s+__new__\s*\(", "__new__ Method", "C2"),
    # __metaclass__ class variable (Python 2 style, still detectable)
    Pattern(r"^\s*__metaclass__\s*=", "__metaclass__ Assignment", "C2"),
    # Private attribute access via self  (self.__name)
    Pattern(r"\bself\.__[A-Za-z_]\w*\b", "Private Class Attribute", "C2"),
    # List comprehension with conditional filter  ([expr for var in iter if cond])
    Pattern(
        r"\[[^\[\]]+\s+for\s+[A-Za-z_]\w*\s+in\s+[^\[\]]+\s+if\s+[^\[\]]+\]",
        "List Comprehension with If",
        "C2",
    ),
    # Dict comprehension with conditional filter  ({k: v for var in iter if cond})
    Pattern(
        r"\{[^{}]+:\s*[^{}]+\s+for\s+[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)?\s+in\s+[^{}]+\s+if\s+[^{}]+\}",
        "Dict Comprehension with If",
        "C2",
    ),
    # Nested list comprehension  ([expr for v1 in iter for v2 in iter])
    Pattern(
        r"\[[^\[\]]+\s+for\s+[A-Za-z_]\w*\s+in\s+[^\[\]]+\s+for\s+[A-Za-z_]\w*\s+in\s+[^\[\]]+\]",
        "Nested List Comprehension",
        "C2",
    ),
]

# ---------------------------------------------------------------------------
# Full ordered pattern list (most-specific first within each level)
# ---------------------------------------------------------------------------
PATTERNS: list[Pattern] = _A1 + _A2 + _B1 + _B2 + _C1 + _C2

# Compile patterns once for performance
_COMPILED: list[tuple] = [
    (re.compile(p.pattern, re.MULTILINE), p.class_name, p.level)
    for p in PATTERNS
]


def compiled_patterns() -> list[tuple]:
    """Return a list of ``(compiled_regex, class_name, level)`` tuples."""
    return _COMPILED
