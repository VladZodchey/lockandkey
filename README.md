[[RU](README.ru.md)|**EN**]

# Lock And Key

## The minimalist password manager.

## Building from source

... write build instructions here ...

## Stack

This project uses:
- QT (Through `PyQT6` Python module) (GUI)
- Material Design 3 (Through `/src/resources/icons`) (the icon set)
- SQLite (Through `sqlite3` Python built-in) (DB structure)

Dev tools:
- `ruff` (code linting)
- `uv` (package management)
- GitHub Workflows (building & releasing)
- QT Designer (widget creation)

## Why not KeePass?

There's not a single reason to use this over KeePass,
as KeePassXC (a community-driven continuation)
has community support, passed the test of time,
and is supported literally everywhere.

However, KeePassXC and KeePass (the original one)
are extremely complicated applications.
They are difficult to reverse-engineer and understand.
This little app was made in [days] days and
I thoroughly documented & commented everything I can
to make picking it apart a breeze.

Btw, some UI solutions are shamelessly stolen from KeePassXC's beautiful interface.

## AI

This project used LLMs only to search up relevant information, no code snippets are AI-generated.
