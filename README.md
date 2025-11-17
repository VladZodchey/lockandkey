[[RU](README.ru.md)|**EN**]

# Lock And Key

## The minimalist password manager.

Are you looking for a password manager, 
but all you can find are either paid or difficult to understand? 
Well, it's the second option.

~~However, if this self-deprecation didn't turn you off, 
you can refer to [docs](./docs/INDEX.md) for further research.~~

## Building from source

```shell
# Clone repo
git clone https://github.com/VladZodchey/lockandkey.git lockandkey && cd lockandkey
# Assuming you have uv installed.
uv venv init
uv sync
uv build
```

## Stack

This project uses:
- QT (Through `PyQT6` Python module) (GUI)
- Material Design 3 (Through `/src/resources/icons`) (the icon set)
- SQLite (Through `sqlite3` Python built-in) (DB structure)
- AES256 + PBKDF (Through `cryptography` Python module) (Encryption)
- QR-Codes (Through `qrcode` Python module) (Link sharing)

Dev tools:
- `ruff` (code linting)
- `uv` (package management)
- `pyinstaller` (executable building)
- QT Designer (widget creation)

## Why use this over KeePass?

Don't. This is a portfolio project, it has some flaws, weird design decisions, etc.
KeePass is time-tested, it's fork KeePassXC is community-driven and modern.
Both are open-source, both have way more features than whatever this is.

## AI

No code snippets are AI-generated. However, LLMs *were* used to perform research.
