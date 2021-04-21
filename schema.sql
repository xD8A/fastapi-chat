BEGIN;

CREATE TABLE "users" (
    "id"            INTEGER,
    "name"          TEXT NOT NULL UNIQUE,
    "email"         TEXT NOT NULL UNIQUE,
    "password_hash" TEXT,
    "is_banned"     INTEGER NOT NULL DEFAULT 0,
    "avatar"        BLOB,
    PRIMARY KEY("id" AUTOINCREMENT),
    CHECK ("is_banned" IN (0, 1))
);

CREATE TABLE "messages" (
    "id"            INTEGER,
    "author_id"     INTEGER,
    "text"          TEXT NOT NULL,
    "created_at"    INTEGER NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("author_id") REFERENCES "users"("id") ON DELETE SET NULL
);

CREATE TABLE "contacts" (
    "id"	        INTEGER,
    "owner_id"	    INTEGER NOT NULL,
    "friend_id"	    INTEGER,
    "name"	        TEXT NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("owner_id") REFERENCES "users"("id") ON DELETE CASCADE,
    FOREIGN KEY("friend_id") REFERENCES "users"("id") ON DELETE SET NULL
);

CREATE TABLE "contact_messages" (
    "contact_id"	INTEGER,
    "message_id"	INTEGER,
    PRIMARY KEY("contact_id", "message_id"),
    FOREIGN KEY("contact_id") REFERENCES "contacts"("id") ON DELETE CASCADE,
    FOREIGN KEY("message_id") REFERENCES "messages"("id") ON DELETE CASCADE
);

CREATE INDEX "ix_contacts_owner_id" ON "contacts" (
	"owner_id"
);

CREATE INDEX "ix_contacts_friend_id" ON "contacts" (
	"friend_id"
);

COMMIT;
