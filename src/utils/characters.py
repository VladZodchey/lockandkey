"""A set table for password-related characters."""

EN_LOWERCASE = frozenset("abcdefghijklmnopqrstuvwxyz")
EN_UPPERCASE = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
RU_LOWERCASE = frozenset("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
RU_UPPERCASE = frozenset("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
DIGITS = frozenset("0123456789")
EXTRA = frozenset("!@#$%^&*()_+-=[]{}|;:,.<>?")

EN = frozenset(EN_LOWERCASE | EN_UPPERCASE)
RU = frozenset(RU_LOWERCASE | RU_UPPERCASE)

ALPHANUMERIC = frozenset(EN | DIGITS)
PASSWORD_CHARS = frozenset(ALPHANUMERIC | EXTRA)
URLSAFE = frozenset(EN | set("-_~."))
