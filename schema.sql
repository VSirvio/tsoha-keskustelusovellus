CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT
);
CREATE TABLE message_tree_paths (
    ancestor INTEGER,
    descendant INTEGER,
    depth INTEGER
);
