# Installation

# Using uv

[uv] is an extremely fast Python package installer.
You can use it to install `pygatherer` and try it out:

```console
$ uv pip install pygatherer
```

# Using a PEP 621 compliant build backend

[PEP 621] is the standard way to store your dependencies in a `pyproject.toml` file.
You can add `pygatherer` to your `pyproject.toml` file:

```toml
[project]
dependencies = [
    "pygatherer",
    ....
]
```

## Python Version Requirement

Please note that `pygatherer` requires Python 3.9 or higher. If you're not using uv,
please ensure that you have such a version installed in your system.

[uv]: https://github.com/astral-sh/uv
[PEP 621]: https://peps.python.org/pep-0621/
