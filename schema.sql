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
    uid INTEGER REFERENCES users,
    subforum INTEGER REFERENCES subforums,
    title TEXT
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users,
    thread INTEGER REFERENCES threads,
    content TEXT
);
CREATE TABLE message_tree_paths (
    ancestor INTEGER REFERENCES messages,
    descendant INTEGER REFERENCES messages,
    depth INTEGER
);
CREATE TABLE likes (
    uid INTEGER REFERENCES users,
    message INTEGER REFERENCES messages,
    value INTEGER
);
