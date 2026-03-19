"""
Parametrized tests covering every element in every proficiency level.

Each entry maps a (class_name, level) pair from :mod:`pycefrl_keyword.patterns`
to a minimal Python snippet that should trigger detection of that element.
This ensures that no pattern is accidentally left untested.
"""

import os
import tempfile

import pytest

from pycefrl_keyword.analyzer import analyze_file
from pycefrl_keyword.patterns import PATTERNS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _analyze(code: str, repo: str = "test_repo") -> list[dict]:
    """Write *code* to a temp .py file, analyze it, and return results."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as fh:
        fh.write(code)
        tmp_path = fh.name
    try:
        return analyze_file(tmp_path, repo)
    finally:
        os.unlink(tmp_path)


def _has(results, *, class_name: str = None, level: str = None) -> bool:
    """Return True if any result matches the given class_name and/or level."""
    for r in results:
        if class_name and r["class"] != class_name:
            continue
        if level and r["level"] != level:
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Mapping: (class_name, level) → code snippet
# ---------------------------------------------------------------------------

# Every pattern defined in patterns.py must have an entry here.  The snippet
# must be valid enough for the regex to match; it does NOT need to be
# runnable Python because analysis is regex-based.

ELEMENT_SNIPPETS: list[tuple[str, str, str]] = [
    # ------------------------------------------------------------------
    # A1 – Beginner
    # ------------------------------------------------------------------
    ("Print", "A1", 'print("hello")\n'),
    ("Simple Return", "A1", "def f():\n    return 42\n"),
    ("Simple Function Definition", "A1", "def greet():\n    pass\n"),
    (
        "Simple For Loop",
        "A1",
        "items = [1, 2, 3]\nfor item in items:\n    print(item)\n",
    ),
    ("Simple If Statement", "A1", "x = 1\nif x > 0:\n    print(x)\n"),
    ("Simple List", "A1", "x = [1, 2, 3]\n"),
    ("Simple Tuple", "A1", "t = (1, 2, 3)\n"),
    ("Simple Assignment", "A1", "x = 42\n"),
    # ------------------------------------------------------------------
    # A2 – Elementary
    # ------------------------------------------------------------------
    ("Augmented Assignment", "A2", "x = 0\nx += 1\n"),
    ("Import", "A2", "import os\n"),
    ("From Import", "A2", "from os import path\n"),
    ("File open() call", "A2", 'f = open("data.txt")\n'),
    (
        "File I/O method call",
        "A2",
        'with open("f.txt") as f:\n    data = f.read()\n',
    ),
    ("range() call", "A2", "for i in range(10):\n    pass\n"),
    ("For Loop with range()", "A2", "for i in range(5):\n    print(i)\n"),
    ("For Loop over List", "A2", "for x in [1, 2, 3]:\n    print(x)\n"),
    ("For Loop over Tuple", "A2", "for val in (1, 2, 3):\n    print(val)\n"),
    (
        "For Loop with Tuple Unpacking",
        "A2",
        "pairs = [(1, 2)]\nfor x, y in pairs:\n    print(x, y)\n",
    ),
    ("Nested List", "A2", "matrix = [[1, 2], [3, 4]]\n"),
    ("Nested Tuple", "A2", "coords = ((1, 2), (3, 4))\n"),
    ("Simple Dictionary", "A2", 'd = {"key": "value"}\n'),
    (
        "Attribute Access (self)",
        "A2",
        "class Foo:\n    def __init__(self):\n        self.x = 1\n",
    ),
    # ------------------------------------------------------------------
    # B1 – Intermediate
    # ------------------------------------------------------------------
    ("Break", "B1", "for i in range(10):\n    if i == 5:\n        break\n"),
    (
        "Continue",
        "B1",
        "for i in range(10):\n    if i % 2 == 0:\n        continue\n",
    ),
    ("Pass", "B1", "def todo():\n    pass\n"),
    ("While Loop", "B1", "n = 0\nwhile n < 10:\n    n += 1\n"),
    ("Lambda Expression", "B1", "double = lambda x: x * 2\n"),
    ("Function with *args", "B1", "def func(*args):\n    pass\n"),
    ("Function with **kwargs", "B1", "def func(**kwargs):\n    pass\n"),
    (
        "Function with Keyword-Only Arguments",
        "B1",
        "def func(*, flag=True):\n    return flag\n",
    ),
    ("Function with Arguments", "B1", "def add(a, b):\n    return a + b\n"),
    ("Simple Class Definition", "B1", "class Dog:\n    pass\n"),
    ("Class with Inheritance", "B1", "class Poodle(Dog):\n    pass\n"),
    (
        "__init__ Method",
        "B1",
        "class Foo:\n    def __init__(self, x):\n        self.x = x\n",
    ),
    ("Try Block", "B1", "try:\n    x = 1\nexcept Exception:\n    pass\n"),
    ("Except Clause", "B1", "try:\n    x = 1\nexcept ValueError:\n    pass\n"),
    ("Raise Exception", "B1", "raise ValueError('bad value')\n"),
    ("With Statement", "B1", 'with open("f.txt") as f:\n    pass\n'),
    (
        "Ternary If Expression",
        "B1",
        "x = 1\ny = 'yes' if x > 0 else 'no'\n",
    ),
    ("From Relative Import", "B1", "from . import utils\n"),
    ("From Star Import", "B1", "from os.path import *\n"),
    ("Import with Alias", "B1", "import numpy as np\n"),
    ("Nested Dictionary", "B1", 'd = {"outer": {"inner": 1}}\n'),
    ("Dictionary with List", "B1", 'd = {"key": [1, 2, 3]}\n'),
    # ------------------------------------------------------------------
    # B2 – Upper-Intermediate
    # ------------------------------------------------------------------
    (
        'If __name__ == "__main__"',
        "B2",
        'if __name__ == "__main__":\n    main()\n',
    ),
    (
        "Finally Clause",
        "B2",
        "try:\n    x = 1\nexcept Exception:\n    pass\nfinally:\n    cleanup()\n",
    ),
    ("Assert Statement", "B2", "assert x > 0, 'must be positive'\n"),
    ("__class__ Attribute", "B2", "print(obj.__class__)\n"),
    ("__dict__ Attribute", "B2", "print(obj.__dict__)\n"),
    (
        "Function with Default Arguments",
        "B2",
        "def greet(name='World'):\n    print(name)\n",
    ),
    (
        "Dict of Dict with List",
        "B2",
        'config = {"db": {"hosts": [1, 2, 3]}}\n',
    ),
    # ------------------------------------------------------------------
    # C1 – Advanced
    # ------------------------------------------------------------------
    ("Generator Function (yield)", "C1", "def gen():\n    yield 1\n"),
    ("List Comprehension", "C1", "squares = [x**2 for x in range(10)]\n"),
    ("Dict Comprehension", "C1", "d = {k: v for k, v in items}\n"),
    (
        "Generator Expression",
        "C1",
        "total = sum(x**2 for x in range(10))\n",
    ),
    (
        "Property Decorator",
        "C1",
        "class Foo:\n    @property\n    def value(self):\n        return self._v\n",
    ),
    (
        "Class Method Decorator",
        "C1",
        "class Foo:\n    @classmethod\n    def create(cls):\n        pass\n",
    ),
    (
        "Static Method Decorator",
        "C1",
        "class Foo:\n    @staticmethod\n    def helper():\n        pass\n",
    ),
    ("__slots__ Attribute", "C1", "class Foo:\n    __slots__ = ['x', 'y']\n"),
    ("Standard Library Module Import", "C1", "import re\n"),
    # ------------------------------------------------------------------
    # C2 – Proficiency
    # ------------------------------------------------------------------
    ("map() Function Call", "C2", "result = list(map(str, [1, 2, 3]))\n"),
    ("zip() Function Call", "C2", "pairs = list(zip([1, 2], [3, 4]))\n"),
    (
        "enumerate() Function Call",
        "C2",
        "for i, v in enumerate([10, 20]):\n    print(i, v)\n",
    ),
    (
        "super() Function Call",
        "C2",
        "class Child(Parent):\n    def __init__(self):\n        super().__init__()\n",
    ),
    ("Decorator", "C2", "@my_decorator\ndef func():\n    pass\n"),
    ("Metaclass Definition", "C2", "class Foo(metaclass=Meta):\n    pass\n"),
    (
        "__new__ Method",
        "C2",
        "class Foo:\n    def __new__(cls):\n        pass\n",
    ),
    (
        "__metaclass__ Assignment",
        "C2",
        "class Foo:\n    __metaclass__ = Meta\n",
    ),
    (
        "Private Class Attribute",
        "C2",
        "class Foo:\n    def __init__(self):\n        self.__secret = 42\n",
    ),
    (
        "List Comprehension with If",
        "C2",
        "evens = [x for x in range(20) if x % 2 == 0]\n",
    ),
    (
        "Dict Comprehension with If",
        "C2",
        "d = {k: v for k, v in data.items() if v > 0}\n",
    ),
    (
        "Nested List Comprehension",
        "C2",
        "flat = [x for row in matrix for x in row]\n",
    ),
]


# ---------------------------------------------------------------------------
# Parametrized test: one test per element
# ---------------------------------------------------------------------------


class TestAllElements:
    """Verify that every element in every proficiency level is detected."""

    @pytest.mark.parametrize(
        "class_name, level, code",
        ELEMENT_SNIPPETS,
        ids=[f"{level}-{name}" for name, level, _ in ELEMENT_SNIPPETS],
    )
    def test_element_detected(self, class_name, level, code):
        """The analyzer must detect *class_name* at *level* for the given code."""
        results = _analyze(code)
        assert _has(results, class_name=class_name, level=level), (
            f"Expected ({class_name!r}, {level!r}) not found in results: "
            f"{[(r['class'], r['level']) for r in results]}"
        )


# ---------------------------------------------------------------------------
# Coverage guard: every pattern must have a snippet
# ---------------------------------------------------------------------------


class TestCoverageCompleteness:
    """Ensure every pattern defined in patterns.py has a corresponding test snippet."""

    def test_all_patterns_have_snippets(self):
        """Every (class_name, level) pair in PATTERNS must appear in ELEMENT_SNIPPETS."""
        defined = {(p.class_name, p.level) for p in PATTERNS}
        tested = {(name, level) for name, level, _ in ELEMENT_SNIPPETS}
        missing = defined - tested
        assert not missing, (
            f"The following patterns lack test snippets: {sorted(missing)}"
        )

    def test_no_extra_snippets(self):
        """Every (class_name, level) pair in ELEMENT_SNIPPETS must exist in PATTERNS."""
        defined = {(p.class_name, p.level) for p in PATTERNS}
        tested = {(name, level) for name, level, _ in ELEMENT_SNIPPETS}
        extra = tested - defined
        assert not extra, (
            f"The following snippets reference non-existent patterns: {sorted(extra)}"
        )
