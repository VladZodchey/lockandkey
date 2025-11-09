"""Password generation utilities."""

from enum import StrEnum
from math import log2
from secrets import choice

from .characters import DIGITS, EN_LOWERCASE, EN_UPPERCASE, EXTRA, PASSWORD_CHARS, RU


class Security(StrEnum):
    """An enum of password security evaluation."""

    POOR = "poor_password"
    WEAK = "weak_password"
    OK = "ok_password"
    STRONG = "strong_password"


def generate_password(charset: set[str] | frozenset[str] = PASSWORD_CHARS, length: int = 16) -> str:
    """Generate a password of given length from a charset.

    Args:
        charset: The set of characters to use
        length: Length (in symbols) of the resulting password

    Raises:
        ValueError: If length is less than 0.

    Returns:
        A password of given length.
    """
    if length < 0:
        raise ValueError("Password length too short")
    if not charset:
        raise ValueError("Charset cannot be empty")
    return "".join(choice(tuple(charset)) for _ in range(length))


def _estimate_charset(password: str) -> int:
    """Estimates the effective chraset size based on present character types.

    Args:
        password: The password to estimate

    Returns:
        The size of an estimated charset.
    """
    t = 0
    for s in (EN_LOWERCASE, EN_UPPERCASE, DIGITS, EXTRA, RU):
        for c in password:
            if c in s:
                t += len(s)
                break
    if any(c not in set().union(EN_LOWERCASE, EN_UPPERCASE, DIGITS, EXTRA, RU) for c in password):
        t += 255  # for good measure
    return t or 1


def evaluate_password(password: str) -> tuple[Security, float]:
    """Evaluate the password's entropy and return it along with rating.

    Args:
        password: The password to evaluate

    Returns:
        A `tuple` with it's first item being a rating (an item of enum `Security`),
        and a `float` of entropy (0-100).
    """
    p = len(password)
    r = _estimate_charset(password)
    e = p * log2(r)
    e = min(e, 100.0)
    # I'm too of a lazy bastard to handle ranges without magic numbers
    match e:
        case n if n >= 75:  # noqa: PLR2004
            t = Security.STRONG
        case n if 50 <= n < 75:  # noqa: PLR2004
            t = Security.OK
        case n if 25 <= n < 50:  # noqa: PLR2004
            t = Security.WEAK
        case _:
            t = Security.POOR
    return (t, e)
