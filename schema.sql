CREATE TABLE subforums (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT
);
CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    subforum INTEGER,
    title TEXT
);
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    thread INTEGER,
    content TEXT
);
CREATE TABLE message_tree_paths (
    ancestor INTEGER,
    descendant INTEGER,
    depth INTEGER
);
