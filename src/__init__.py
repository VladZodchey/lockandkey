"""Main package file."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("lockandkey")
except PackageNotFoundError:
    import pathlib
    import tomllib

    pyproject = pathlib.Path(__file__).resolve().parents[2] / "pyproject.toml"
    if pyproject.is_file():
        data = tomllib.loads(pyproject.read_text())
        __version__ = data["project"]["version"]
    else:
        __version__ = "0.0.0+dev"
