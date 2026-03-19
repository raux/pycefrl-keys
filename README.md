# pycefrl-keyword

A Python tool that identifies [CEFR-inspired](https://en.wikipedia.org/wiki/Common_European_Framework_of_Reference_for_Languages) proficiency levels in Python 3 source code using **regular expression** pattern matching — rather than Abstract Syntax Tree (AST) analysis as used in the original [PyCerf](https://github.com/raux/pycefrl) project.

## What is this project about?

The goal is to analyse Python source files and assign each detected language construct a CEFR-inspired proficiency code:

| Level | Description          | Example constructs                                       |
|-------|----------------------|----------------------------------------------------------|
| A1    | Beginner             | `print`, simple assignment, simple `if`, simple `for`, simple list/tuple |
| A2    | Elementary           | `import`, `range()`, file I/O, augmented assignment, nested list, simple dict |
| B1    | Intermediate         | `break`/`continue`/`pass`, `while`, `lambda`, classes, `try/except`, `with`, relative imports |
| B2    | Upper-Intermediate   | `if __name__ == "__main__"`, `finally`, `assert`, `__class__`/`__dict__`, default args |
| C1    | Advanced             | `yield`, list/dict comprehensions, generator expressions, `@property`, `@classmethod`, `__slots__`, stdlib modules |
| C2    | Proficiency          | `map`, `zip`, `enumerate`, `super`, decorators, metaclass, `__new__`, private attributes |

## How it differs from the original PyCerf

| Aspect | Original PyCerf | pycefrl-keyword |
|--------|----------------|----------------|
| Analysis engine | Python `ast` module (parse tree traversal) | `re` module (regex pattern matching) |
| Accuracy | High — operates on the AST | Good — text-level matching with heuristic patterns |
| Speed | Slower (full parse required) | Fast (regex scan) |
| Dependencies | `ast` (stdlib) | `re` (stdlib) — no external dependencies |

## Installation

```bash
pip install -e .
```

Or simply clone the repository and run directly.

## Usage

### Analyze a directory

```bash
python pycefrl_keyword_cli.py directory <path_to_directory>
```

### Analyze a single file

```bash
python pycefrl_keyword_cli.py file <path_to_file.py>
```

Results are written to:
- **`data.json`** — nested by repository → file → list of matches
- **`data.csv`** — flat table with columns: Repo, File, Class, Start Line, End Line, Displacement, Level

### Python API

```python
from pycefrl_keyword import analyze_file, analyze_directory, save_results

# Analyze one file
results = analyze_file("my_script.py", repo_name="my_project")

# Analyze a whole directory
results = analyze_directory("/path/to/project")

# Save results
json_path, csv_path = save_results(results, output_dir=".")

# Each result is a dict:
# {
#   "repo": "my_project",
#   "file": "my_script.py",
#   "class": "Simple For Loop",
#   "start_line": 5,
#   "end_line": 5,
#   "displacement": 0,
#   "level": "A1"
# }
```

## Running the tests

```bash
pip install pytest
pytest tests/
```

## Output format

### data.json

```json
{
  "my_project": {
    "my_script.py": [
      {
        "Class": "Print",
        "Start Line": "1",
        "End Line": "1",
        "Displacement": "0",
        "Level": "A1"
      }
    ]
  }
}
```

### data.csv

```
Repo,File,Class,Start Line,End Line,Displacement,Level
my_project,my_script.py,Print,1,1,0,A1
```

## Limitations

- Regex patterns may occasionally match inside string literals or comments.
- Complex constructs (e.g. recursive functions) that require semantic understanding cannot be reliably detected by regex alone.
- Patterns are applied independently, so a single line of code may produce multiple matches at different levels.

## License

MIT License — see [LICENSE](LICENSE).