"""The resources root, providing resource path macros."""

from importlib.resources import files
from importlib.resources.abc import Traversable

BASE_PATH = files("src.resources")


def path(*parts: str) -> Traversable:
    """Get absolute file to resource."""
    return BASE_PATH.joinpath(*parts)


def ui_path(filename: str) -> str:
    """Macro for view resolvement."""
    return str(path("views", filename))


def icon_path(filename: str) -> str:
    """Macro for icon resolvement."""
    return str(path("icons", filename))
