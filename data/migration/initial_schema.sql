CREATE TABLE secrets (
    secretId INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    secret TEXT NOT NULL,
    login TEXT,
    website TEXT,
    groupId INTEGER,
    FOREIGN KEY(groupId) REFERENCES groups(groupId)
);
CREATE TABLE groups (
    groupId INTEGER PRIMARY KEY AUTOINCREMENT,
    groupName TEXT NOT NULL,
    groupIconId TEXT DEFAULT "key"
);
