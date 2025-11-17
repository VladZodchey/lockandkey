"""An utility for updating the DB."""

from sqlite3 import Connection

# Image an upgrade_or_stall function here.


def init(conn: Connection) -> None:
    """Initialize the DB to the latest version."""
    # mockup, will implement a better solution in later versions.
    sql = """
    -- 0.0.1
    CREATE TABLE secrets (
        secretId INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        secret TEXT NOT NULL,
        login TEXT,
        website TEXT,
        groupId INTEGER,
        lastAccess TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(groupId) REFERENCES groups(groupId) ON DELETE SET NULL
    );
    CREATE TABLE groups (
        groupId INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        iconId TEXT DEFAULT "key"
    );
    CREATE TABLE db_version (
        version TEXT NOT NULL,
        upgradedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    INSERT
    INTO db_version(version)
    VALUES ('0.0.1');
    """
    cursor = conn.cursor()
    cursor.executescript(sql)
    conn.commit()
    cursor.close()
