"""A list of project-wide custom exceptions."""


class IncorrectError(RuntimeError):
    """The supplied value is wrong."""


class ExistsError(RuntimeError):
    """A value already exists."""
