-- 0.0.1
CREATE TABLE secrets (
    secretId INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    secret TEXT NOT NULL,
    login TEXT,
    website TEXT,
    groupId INTEGER,
    lastAccess TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(groupId) REFERENCES groups(groupId)
);
CREATE TABLE groups (
    groupId INTEGER PRIMARY KEY AUTOINCREMENT,
    groupName TEXT NOT NULL,
    groupIconId TEXT DEFAULT "key"
);
CREATE TABLE db_version (
    version TEXT NOT NULL,
    upgradedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT
INTO db_version(version)
VALUES ('0.0.1');
