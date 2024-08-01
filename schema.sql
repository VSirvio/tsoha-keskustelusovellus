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
    uid INTEGER REFERENCES users ON DELETE CASCADE,
    subforum INTEGER REFERENCES subforums ON DELETE CASCADE,
    title TEXT
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users ON DELETE CASCADE,
    thread INTEGER REFERENCES threads ON DELETE CASCADE,
    content TEXT
);
CREATE TABLE message_tree_paths (
    ancestor INTEGER REFERENCES messages ON DELETE CASCADE,
    descendant INTEGER REFERENCES messages ON DELETE CASCADE,
    depth INTEGER
);
CREATE TABLE likes (
    uid INTEGER REFERENCES users ON DELETE CASCADE,
    message INTEGER REFERENCES messages ON DELETE CASCADE,
    value INTEGER
);
