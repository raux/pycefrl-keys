from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pycefrl-keyword",
    version="0.1.0",
    author="Raula Gaikovina Kula",
    description=(
        "Identifies Python CEFR proficiency levels using regular expression "
        "pattern matching instead of AST analysis."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "pycefrl-keyword=pycefrl_keyword_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
