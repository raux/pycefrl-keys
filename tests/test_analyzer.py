"""
Tests for pycefrl-keyword: regex-based Python CEFR proficiency level identifier.

Each test writes a small Python snippet to a temporary file and verifies that
the expected constructs (class name + CEFR level) are detected by
:func:`pycefrl_keyword.analyzer.analyze_file`.
"""

import os
import tempfile

import pytest

from pycefrl_keyword.analyzer import analyze_file, analyze_directory, save_results

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: All keys that must be present in every result record returned by the analyzer.
RESULT_KEYS = ("repo", "file", "class", "start_line", "end_line", "displacement", "level")


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


def _levels(results: list[dict]) -> set[str]:
    return {r["level"] for r in results}


def _classes(results: list[dict]) -> set[str]:
    return {r["class"] for r in results}


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
# A1 – Beginner
# ---------------------------------------------------------------------------

class TestA1:
    def test_print(self):
        results = _analyze('print("Hello, World!")\n')
        assert _has(results, class_name="Print", level="A1")

    def test_simple_return(self):
        results = _analyze("def f():\n    return 42\n")
        assert _has(results, class_name="Simple Return", level="A1")

    def test_simple_function_def_no_args(self):
        results = _analyze("def greet():\n    pass\n")
        assert _has(results, class_name="Simple Function Definition", level="A1")

    def test_simple_if(self):
        results = _analyze("x = 1\nif x > 0:\n    print(x)\n")
        assert _has(results, class_name="Simple If Statement", level="A1")

    def test_simple_for_loop(self):
        results = _analyze("items = [1, 2, 3]\nfor item in items:\n    print(item)\n")
        assert _has(results, class_name="Simple For Loop", level="A1")

    def test_simple_assignment(self):
        results = _analyze("x = 42\n")
        assert _has(results, class_name="Simple Assignment", level="A1")

    def test_simple_list(self):
        results = _analyze("x = [1, 2, 3]\n")
        assert _has(results, class_name="Simple List", level="A1")

    def test_simple_list_no_subscript_false_positive(self):
        """Subscript/index access should NOT be classified as Simple List."""
        results = _analyze("y = items[0]\n")
        assert not _has(results, class_name="Simple List", level="A1")

    def test_simple_tuple(self):
        results = _analyze("t = (1, 2, 3)\n")
        assert _has(results, class_name="Simple Tuple", level="A1")


# ---------------------------------------------------------------------------
# A2 – Elementary
# ---------------------------------------------------------------------------

class TestA2:
    def test_augmented_assignment(self):
        results = _analyze("x = 0\nx += 1\n")
        assert _has(results, class_name="Augmented Assignment", level="A2")

    def test_import(self):
        results = _analyze("import os\n")
        assert _has(results, class_name="Import", level="A2")

    def test_from_import(self):
        results = _analyze("from os import path\n")
        assert _has(results, class_name="From Import", level="A2")

    def test_file_open(self):
        results = _analyze('f = open("data.txt")\n')
        assert _has(results, class_name="File open() call", level="A2")

    def test_file_io_method(self):
        results = _analyze('with open("f.txt") as f:\n    data = f.read()\n')
        assert _has(results, class_name="File I/O method call", level="A2")

    def test_range_call(self):
        results = _analyze("for i in range(10):\n    pass\n")
        assert _has(results, class_name="range() call", level="A2")

    def test_for_loop_with_range(self):
        results = _analyze("for i in range(5):\n    print(i)\n")
        assert _has(results, class_name="For Loop with range()", level="A2")

    def test_for_loop_over_list(self):
        results = _analyze("for x in [1, 2, 3]:\n    print(x)\n")
        assert _has(results, class_name="For Loop over List", level="A2")

    def test_for_loop_tuple_unpacking(self):
        results = _analyze("pairs = [(1, 2)]\nfor x, y in pairs:\n    print(x, y)\n")
        assert _has(results, class_name="For Loop with Tuple Unpacking", level="A2")

    def test_nested_list(self):
        results = _analyze("matrix = [[1, 2], [3, 4]]\n")
        assert _has(results, class_name="Nested List", level="A2")

    def test_simple_dict(self):
        results = _analyze('d = {"key": "value"}\n')
        assert _has(results, class_name="Simple Dictionary", level="A2")

    def test_self_attribute(self):
        results = _analyze(
            "class Foo:\n    def __init__(self):\n        self.x = 1\n"
        )
        assert _has(results, class_name="Attribute Access (self)", level="A2")

    def test_self_dunder_not_a2(self):
        """self.__dict__ and self.__class__ must NOT be classified as A2 Attribute Access."""
        for snippet in ("print(self.__dict__)\n", "print(self.__class__)\n"):
            results = _analyze(snippet)
            assert not _has(results, class_name="Attribute Access (self)", level="A2"), (
                f"self dunder wrongly classified as A2 for: {snippet!r}"
            )


# ---------------------------------------------------------------------------
# B1 – Intermediate
# ---------------------------------------------------------------------------

class TestB1:
    def test_break(self):
        results = _analyze("for i in range(10):\n    if i == 5:\n        break\n")
        assert _has(results, class_name="Break", level="B1")

    def test_continue(self):
        results = _analyze("for i in range(10):\n    if i % 2 == 0:\n        continue\n")
        assert _has(results, class_name="Continue", level="B1")

    def test_pass(self):
        results = _analyze("def todo():\n    pass\n")
        assert _has(results, class_name="Pass", level="B1")

    def test_while_loop(self):
        results = _analyze("n = 0\nwhile n < 10:\n    n += 1\n")
        assert _has(results, class_name="While Loop", level="B1")

    def test_lambda(self):
        results = _analyze("double = lambda x: x * 2\n")
        assert _has(results, class_name="Lambda Expression", level="B1")

    def test_function_with_args(self):
        results = _analyze("def add(a, b):\n    return a + b\n")
        assert _has(results, class_name="Function with Arguments", level="B1")

    def test_function_with_star_args(self):
        results = _analyze("def func(*args):\n    pass\n")
        assert _has(results, class_name="Function with *args", level="B1")

    def test_function_with_kwargs(self):
        results = _analyze("def func(**kwargs):\n    pass\n")
        assert _has(results, class_name="Function with **kwargs", level="B1")

    def test_simple_class(self):
        results = _analyze("class Dog:\n    pass\n")
        assert _has(results, class_name="Simple Class Definition", level="B1")

    def test_class_with_inheritance(self):
        results = _analyze("class Poodle(Dog):\n    pass\n")
        assert _has(results, class_name="Class with Inheritance", level="B1")

    def test_init_method(self):
        results = _analyze(
            "class Foo:\n    def __init__(self, x):\n        self.x = x\n"
        )
        assert _has(results, class_name="__init__ Method", level="B1")

    def test_try_block(self):
        results = _analyze("try:\n    x = 1\nexcept Exception:\n    pass\n")
        assert _has(results, class_name="Try Block", level="B1")

    def test_except_clause(self):
        results = _analyze("try:\n    x = 1\nexcept ValueError:\n    pass\n")
        assert _has(results, class_name="Except Clause", level="B1")

    def test_raise(self):
        results = _analyze("raise ValueError('bad value')\n")
        assert _has(results, class_name="Raise Exception", level="B1")

    def test_with_statement(self):
        results = _analyze('with open("f.txt") as f:\n    pass\n')
        assert _has(results, class_name="With Statement", level="B1")

    def test_ternary_expression(self):
        results = _analyze("x = 1\ny = 'yes' if x > 0 else 'no'\n")
        assert _has(results, class_name="Ternary If Expression", level="B1")

    def test_from_relative_import(self):
        results = _analyze("from . import utils\n")
        assert _has(results, class_name="From Relative Import", level="B1")

    def test_from_star_import(self):
        results = _analyze("from os.path import *\n")
        assert _has(results, class_name="From Star Import", level="B1")

    def test_import_with_alias(self):
        results = _analyze("import numpy as np\n")
        assert _has(results, class_name="Import with Alias", level="B1")

    def test_nested_dict(self):
        results = _analyze('d = {"outer": {"inner": 1}}\n')
        assert _has(results, class_name="Nested Dictionary", level="B1")

    def test_dict_with_list(self):
        results = _analyze('d = {"key": [1, 2, 3]}\n')
        assert _has(results, class_name="Dictionary with List", level="B1")


# ---------------------------------------------------------------------------
# B2 – Upper-Intermediate
# ---------------------------------------------------------------------------

class TestB2:
    def test_name_main_guard(self):
        results = _analyze('if __name__ == "__main__":\n    main()\n')
        assert _has(results, class_name='If __name__ == "__main__"', level="B2")

    def test_finally_clause(self):
        results = _analyze(
            "try:\n    x = 1\nexcept Exception:\n    pass\nfinally:\n    cleanup()\n"
        )
        assert _has(results, class_name="Finally Clause", level="B2")

    def test_assert(self):
        results = _analyze("assert x > 0, 'must be positive'\n")
        assert _has(results, class_name="Assert Statement", level="B2")

    def test_dunder_class(self):
        results = _analyze("print(obj.__class__)\n")
        assert _has(results, class_name="__class__ Attribute", level="B2")

    def test_dunder_dict(self):
        results = _analyze("print(obj.__dict__)\n")
        assert _has(results, class_name="__dict__ Attribute", level="B2")

    def test_function_default_args(self):
        results = _analyze("def greet(name='World'):\n    print(name)\n")
        assert _has(results, class_name="Function with Default Arguments", level="B2")


# ---------------------------------------------------------------------------
# C1 – Advanced
# ---------------------------------------------------------------------------

class TestC1:
    def test_yield(self):
        results = _analyze("def gen():\n    yield 1\n")
        assert _has(results, class_name="Generator Function (yield)", level="C1")

    def test_list_comprehension(self):
        results = _analyze("squares = [x**2 for x in range(10)]\n")
        assert _has(results, class_name="List Comprehension", level="C1")

    def test_dict_comprehension(self):
        results = _analyze("d = {k: v for k, v in items}\n")
        assert _has(results, class_name="Dict Comprehension", level="C1")

    def test_generator_expression(self):
        results = _analyze("total = sum(x**2 for x in range(10))\n")
        assert _has(results, class_name="Generator Expression", level="C1")

    def test_property_decorator(self):
        results = _analyze(
            "class Foo:\n    @property\n    def value(self):\n        return self._v\n"
        )
        assert _has(results, class_name="Property Decorator", level="C1")

    def test_classmethod_decorator(self):
        results = _analyze(
            "class Foo:\n    @classmethod\n    def create(cls):\n        pass\n"
        )
        assert _has(results, class_name="Class Method Decorator", level="C1")

    def test_staticmethod_decorator(self):
        results = _analyze(
            "class Foo:\n    @staticmethod\n    def helper():\n        pass\n"
        )
        assert _has(results, class_name="Static Method Decorator", level="C1")

    def test_slots(self):
        results = _analyze("class Foo:\n    __slots__ = ['x', 'y']\n")
        assert _has(results, class_name="__slots__ Attribute", level="C1")

    def test_standard_library_module(self):
        results = _analyze("import re\n")
        assert _has(results, class_name="Standard Library Module Import", level="C1")

    def test_pickle_module(self):
        results = _analyze("import pickle\n")
        assert _has(results, class_name="Standard Library Module Import", level="C1")


# ---------------------------------------------------------------------------
# C2 – Proficiency
# ---------------------------------------------------------------------------

class TestC2:
    def test_map(self):
        results = _analyze("result = list(map(str, [1, 2, 3]))\n")
        assert _has(results, class_name="map() Function Call", level="C2")

    def test_zip(self):
        results = _analyze("pairs = list(zip([1, 2], [3, 4]))\n")
        assert _has(results, class_name="zip() Function Call", level="C2")

    def test_enumerate(self):
        results = _analyze("for i, v in enumerate([10, 20]):\n    print(i, v)\n")
        assert _has(results, class_name="enumerate() Function Call", level="C2")

    def test_super(self):
        results = _analyze(
            "class Child(Parent):\n    def __init__(self):\n        super().__init__()\n"
        )
        assert _has(results, class_name="super() Function Call", level="C2")

    def test_decorator(self):
        results = _analyze("@my_decorator\ndef func():\n    pass\n")
        assert _has(results, class_name="Decorator", level="C2")

    def test_metaclass(self):
        results = _analyze("class Foo(metaclass=Meta):\n    pass\n")
        assert _has(results, class_name="Metaclass Definition", level="C2")

    def test_new_method(self):
        results = _analyze("class Foo:\n    def __new__(cls):\n        pass\n")
        assert _has(results, class_name="__new__ Method", level="C2")

    def test_private_attribute(self):
        results = _analyze(
            "class Foo:\n    def __init__(self):\n        self.__secret = 42\n"
        )
        assert _has(results, class_name="Private Class Attribute", level="C2")

    def test_dunder_attribute_not_private_c2(self):
        """self.__dict__ / self.__class__ are dunders, not name-mangled private attrs."""
        for snippet in ("x = self.__dict__\n", "x = self.__class__\n"):
            results = _analyze(snippet)
            assert not _has(results, class_name="Private Class Attribute", level="C2"), (
                f"Dunder wrongly classified as Private Class Attribute for: {snippet!r}"
            )

    def test_list_comp_with_if(self):
        results = _analyze("evens = [x for x in range(20) if x % 2 == 0]\n")
        assert _has(results, class_name="List Comprehension with If", level="C2")

    def test_dict_comp_with_if(self):
        results = _analyze("d = {k: v for k, v in data.items() if v > 0}\n")
        assert _has(results, class_name="Dict Comprehension with If", level="C2")

    def test_nested_list_comp(self):
        results = _analyze(
            "flat = [x for row in matrix for x in row]\n"
        )
        assert _has(results, class_name="Nested List Comprehension", level="C2")


# ---------------------------------------------------------------------------
# Integration: analyze_directory + save_results
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_analyze_directory(self, tmp_path):
        """analyze_directory uses relative paths so same-basename files are distinct."""
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "a.py").write_text("print('hello')\n")
        (sub / "b.py").write_text("x = 1\n")

        results = analyze_directory(str(tmp_path))
        files_found = {r["file"] for r in results}
        # Root-level file stored as bare name
        assert "a.py" in files_found
        # Sub-directory file stored as a relative path (OS-appropriate separator)
        expected_sub = os.path.join("sub", "b.py")
        assert expected_sub in files_found

    def test_save_results(self, tmp_path):
        """save_results produces valid data.json and data.csv."""
        import json
        import csv

        code = "print('hi')\nx = 1\n"
        results = _analyze(code)
        json_path, csv_path = save_results(results, str(tmp_path))

        assert os.path.exists(json_path)
        assert os.path.exists(csv_path)

        with open(json_path) as fh:
            data = json.load(fh)
        assert "test_repo" in data

        with open(csv_path, newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
        assert len(rows) == len(results)
        assert "Level" in rows[0]

    def test_result_fields(self):
        """Every result record has the expected keys."""
        results = _analyze("x = 1\n")
        assert results, "Expected at least one match"
        for r in results:
            for key in RESULT_KEYS:
                assert key in r, f"Missing key: {key}"

    def test_line_numbers_are_positive(self):
        results = _analyze("x = 1\ny = 2\n")
        for r in results:
            assert r["start_line"] >= 1
            assert r["end_line"] >= r["start_line"]

    def test_level_values_are_valid(self):
        valid_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
        results = _analyze(
            "import re\nfor x in range(10):\n    print(x)\n"
        )
        for r in results:
            assert r["level"] in valid_levels, f"Unexpected level: {r['level']}"
