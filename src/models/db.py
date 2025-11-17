"""Main DB logic."""

from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path
from sqlite3 import Connection, Cursor, Row, connect
from typing import Any

from .migrant import init


class Glue:
    """A class for atomizing DB queries."""

    _SHARED_URL = "file::memory:?cache=shared"

    class QueryContext(AbstractContextManager):
        """Manages a somewhat safe context for performing queries."""

        def __init__(self, uri: str, timeout: int = 10, row: bool = True):
            """Manages a somewhat safe context for performing queries.

            Args:
                uri: The `str` URI to the database
                timeout: Timeout (in seconds) of query completion
                row: Whether to use `sqlite3.Row` factory for cursors
            """
            self.uri = uri
            self.timeout = timeout
            self.row = row
            self.conn: Connection
            self.cursor: Cursor

        def __enter__(self):  # noqa: D105
            self.conn = connect(self.uri, uri=True, timeout=self.timeout)
            if self.row:
                self.conn.row_factory = Row
            self.cursor = self.conn.cursor()
            return self

        def __exit__(self, exc_type, exc_value, traceback):  # noqa: D105
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

        def query(self, sql: str, params: tuple | dict = (), fetch: int = 1) -> Any:
            # This method is shamelessly stolen from my other project Chancery.
            """Performs an SQL query.

            Args:
                sql (str): The query to run
                params (tuple | dict): Parameters to pass
                fetch (int): How many results to return.
                    If -1, does not return anything.
                    If 0, returns a list of all.
                    If 1, returns the first row.
                    If >1, returns a list of that many rows or all, whatever is less

            Returns:
                Nothing if ``fetch`` is -1.
                The first row if ``fetch`` is 1.
                A list or rows if ``fetch`` is 0 or >1.
            """
            fetch = max(fetch, -1)
            self.cursor.execute(sql, params)
            match fetch:
                case -1:
                    return None
                case 0:
                    result = self.cursor.fetchall()
                case 1:
                    result = self.cursor.fetchone()
                    return result if not self.row else dict(result)
                case _:
                    result = self.cursor.fetchmany(size=fetch)
            return result if not self.row else tuple(map(dict, result))

    def __init__(self, uri: str = _SHARED_URL):
        """Spawns the DB Glue."""
        self.uri: str = uri
        self._conn: Connection
        self.dirty: bool = False

    def querying(self, timeout: int = 10, row: bool = False) -> QueryContext:
        """Creates a query context for you. Neat!"""
        return self.QueryContext(uri=self.uri, timeout=timeout, row=row)

    @classmethod
    def from_bytes(cls, data: bytes) -> Glue:
        """Spawn the DB Glue on top of a decrypted in-memory database.

        Args:
            data: The `bytes` object containing the unencrypted serialized data.
        """
        instance = cls()
        tmp = connect(":memory:", uri=True)
        tmp.deserialize(data)
        conn = connect("file::memory:?cache=shared", uri=True)
        tmp.backup(conn)
        instance._conn = conn
        return instance

    @classmethod
    def from_bare(cls, uri: str | Path) -> Glue:
        """Spawn the DB Glue on top of a bare SQLite database.

        Args:
            uri: The file path or in-memory mapping to the database.
        """
        instance = cls(str(uri))
        instance._conn = connect(uri, uri=True)
        return instance

    @classmethod
    def new(cls) -> Glue:
        """Initialize the database and spawn the DB Glue on top of it."""
        instance = cls()
        instance._conn = connect("file::memory:?cache=shared", uri=True)
        init(instance._conn)
        return instance

    def to_bytes(self) -> bytes:
        """Serialize the database into a `bytes` object."""
        dest = connect(":memory:")
        self._conn.backup(dest)
        return dest.serialize()

    def query(self, query: str, params: tuple | dict = (), fetch: int = 1) -> Any:
        # This method is shamelessly stolen from my other project Chancery.
        """Performs a synchronous query. Note: Consider using ``QueryContext`` instead.

        Args:
            query (str): The SQL query
            params (tuple | dict): Parameters to pass into the query
            fetch (int): How many results to return.
                    If -1, does not return anything.
                    If 0, returns a list of all.
                    If 1, returns the first row.
                    If >1, returns a list of that many rows or all, whatever is less

        Returns:
            Any: All results of the query.
        """
        fetch = max(fetch, -1)
        conn = connect(self.uri, uri=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        match fetch:
            case -1:
                result = None
            case 0:
                result = cursor.fetchall()
            case 1:
                result = cursor.fetchone()
            case _:
                result = cursor.fetchmany(size=fetch)
        conn.commit()
        cursor.close()
        conn.close()
        return result

    def close(self) -> None:
        """Close up the in-memory connection, letting the GC clear it.

        Changes aren't automatically saved to disk!
        """
        self._conn.close()

    def entries(self, *, text: str | None = None, group: int | None = None) -> tuple[tuple]:
        """Return a tuple of entry tuples, filtered by `group` id if given.

        Args:
            text: The text query to filter for, `str`
            group: The group id to filter for, `int`.

        Returns:
            A list of tuples with values:
                `group(iconId)` `group(name)`
                `secretId` `secret(name)`
                `secret` `login`
                `website` `lastAccess`
            In this exact order.
        """
        with self.querying() as sql:
            query = """
            SELECT
                g.iconId, g.name, e.secretId, e.name,
                e.secret, e.login, e.website, e.lastAccess
            FROM
                secrets e
            LEFT JOIN groups g USING(groupId)

            """
            criteria = []
            params = []
            if group:
                criteria.append("e.groupId = ?")
                params.append(group)
            if text:
                criteria.append("lower(e.name) LIKE ?")
                params.append(text.replace("*", "%").replace("?", "_"))
            if criteria:
                query += "WHERE " + " AND ".join(criteria)
            return sql.query(query, tuple(params), fetch=0)

    def add_entry(
        self,
        name: str,
        secret: str,
        login: str | None = None,
        website: str | None = None,
        group: int | None = None,
    ) -> None:
        """Adds a secret entry.

        Args:
            name: The name of the entry. Required
            secret: The entry's point of existing. Required
            login: The login for the entry. Optional
            website: The website of the entry. Optional
            group: The group ID of the entry. Optional
        """
        with self.querying() as sql:
            sql.query(
                """
                INSERT
                INTO secrets
                    (name, secret, login, website, groupId)
                VALUES
                    (?, ?, ?, ?, ?);
                """,
                (name, secret, login, website, group),
                fetch=-1,
            )
        self.dirty = True

    def edit_entry(  # noqa: PLR0913
        self,
        identifier: int,
        name: str,
        secret: str,
        login: str | None,
        website: str | None,
        group: int | None,
    ) -> None:
        """Edits a secret entry.

        Args:
            identifier: The ID of the entry to change. Required
            name: The name of the entry. Required
            secret: The entry's point of existing. Required
            login: The login for the entry. Optional
            website: The website of the entry. Optional
            group: The group name of the entry. Optional
        """
        with self.querying() as sql:
            sql.query(
                """
                UPDATE secrets
                SET
                    name = ?,
                    secret = ?,
                    login = ?,
                    website = ?,
                    groupId = ?
                WHERE secretId = ?
                """,
                (name, secret, login, website, group, identifier),
                fetch=-1,
            )
        self.dirty = True

    def get_entry(self, identifier: int) -> tuple[str, str, str, str, str] | None:
        """Pull up entry data by its ID.

        Args:
            identifier: The numeric ID of the entry, `int`

        Returns:
            A tuple with `name`, `secret`, `login`, `website`, `name(groupId)` of the entry.
        """
        return self.query(
            """
            SELECT e.name, e.secret, e.login, e.website, g.name
            FROM secrets e
            LEFT JOIN groups g USING (groupId)
            WHERE e.secretId = ?
            """,
            (identifier,),
        )

    def delete_entry(self, identifier: int) -> None:
        """Delete an entry by its ID. Fire-and-forget style.

        Args:
            identifier: The numeric ID of the entry, `int`
        """
        self.query(
            """
            DELETE
            FROM secrets
            WHERE secretId = ?
            """,
            (identifier,),
        )
        self.dirty = True

    def groups(self) -> tuple[tuple[int, str, str]]:
        """Return a tuple of group ID, name and icon ID pairs."""
        with self.querying() as sql:
            return sql.query(
                """
                SELECT
                    groupId, name, iconId
                FROM groups
                """,
                fetch=0,
            )

    def add_group(self, name: str, icon_id: str) -> None:
        """Create a new group with name `name` and icon of `icon_id`."""
        with self.querying() as sql:
            sql.query(
                """
                INSERT
                INTO groups (name, iconId)
                VALUES (?, ?)
                """,
                (name, icon_id),
            )
        self.dirty = True

    def edit_group(self, identifier: int, name: str, icon_id: str) -> None:
        """Edit group's `name` and `icon_id` by its `identifier`."""
        with self.querying() as sql:
            sql.query(
                """
                UPDATE groups
                SET
                    name = ?,
                    iconId = ?
                WHERE groupId = ?
                """,
                (name, icon_id, identifier),
            )
        self.dirty = True

    def get_group(self, identifier: int) -> tuple[str, str] | None:
        """Get group's name and icon ID by its `identifier`.

        Returns `None` if no group is under that ID.
        """
        return self.query(
            """
            SELECT name, iconId
            FROM groups
            WHERE groupId = ?
            """,
            (identifier,),
        )

    def delete_group(self, identifier: int) -> None:
        """Delete a group by its `identifier`, making all its entries orphan T-T."""
        with self.querying() as sql:
            sql.query(
                """
                DELETE
                FROM groups
                WHERE groupId = ?
                """,
                (identifier,),
            )
        self.dirty = True
