CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);
CREATE TABLE subforums (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT
);
CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    uid INTEGER,
    subforum INTEGER,
    title TEXT
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    uid INTEGER,
    thread INTEGER,
    content TEXT
);
CREATE TABLE message_tree_paths (
    ancestor INTEGER,
    descendant INTEGER,
    depth INTEGER
);
