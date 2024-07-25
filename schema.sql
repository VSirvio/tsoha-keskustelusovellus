CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
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
