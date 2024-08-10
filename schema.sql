CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
);
CREATE TABLE subforums (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE,
    description TEXT
);
CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users ON DELETE CASCADE,
    subforum INTEGER REFERENCES subforums ON DELETE CASCADE,
    title TEXT
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users ON DELETE CASCADE,
    thread INTEGER REFERENCES threads ON DELETE CASCADE,
    content TEXT,
    sent TIMESTAMP DEFAULT NOW()
);
CREATE TABLE message_tree_paths (
    ancestor INTEGER REFERENCES messages ON DELETE CASCADE,
    descendant INTEGER REFERENCES messages ON DELETE CASCADE,
    depth INTEGER CHECK (depth >= 0),
    UNIQUE (ancestor, descendant)
);
CREATE TABLE likes (
    uid INTEGER REFERENCES users ON DELETE CASCADE,
    message INTEGER REFERENCES messages ON DELETE CASCADE,
    value INTEGER CHECK (value = 1 OR value = -1),
    UNIQUE (uid, message)
);
