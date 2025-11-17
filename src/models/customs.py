"""This module provides functions for importing/exporting data to/from CSV files."""

from csv import DictWriter, reader
from pathlib import Path

from .db import Glue


def dump_to_file(glue: Glue, file: str | Path) -> None:
    """Dumps DB data of `glue` to `file`."""
    with glue.querying(row=True) as sql:
        entries = sql.query(
            """
            SELECT *
            FROM secrets
            """,
            fetch=0,
        )
        groups = sql.query(
            """
            SELECT *
            FROM groups
            """,
            fetch=0,
        )
    with Path(file).open("w", encoding="utf-8") as output:
        if entries:
            output.write("# Entries:\n")
            entry_writer = DictWriter(output, fieldnames=entries[0].keys())
            entry_writer.writeheader()
            entry_writer.writerows(entries)
            output.write("\n")
        if groups:
            output.write("# Groups:\n")
            group_writer = DictWriter(output, fieldnames=groups[0].keys())
            group_writer.writeheader()
            group_writer.writerows(groups)
            output.write("\n")


def restore_from_file(glue: Glue, file: str | Path) -> None:
    """Populates `glue` from `file`, dumped by `dump_to_file`."""
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError("Dump doesn't exist.")
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    section = None
    header = None
    with glue.querying() as sql:
        for raw_line in lines:
            line = raw_line.strip()

            if line.startswith("# Entries:"):
                section = "secrets"
                header = None
                continue
            if line.startswith("# Groups:"):
                section = "groups"
                header = None
                continue
            if line == "" or line.startswith("#"):
                continue

            if section:
                if header is None:
                    header = line.split(",")
                else:
                    values = next(reader([line]))
                    query = f"""
                    INSERT OR REPLACE INTO {section} ({", ".join(header)})
                    VALUES ({", ".join(["?"] * len(values))})
                    """  # noqa: S608
                    sql.query(query, tuple(values), fetch=-1)
    glue.dirty = True
