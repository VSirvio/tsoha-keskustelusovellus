INSERT INTO threads (title) VALUES ('Joku keskustelu');

INSERT INTO messages (thread, content) VALUES (1, 'Terve, maailma!');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 1, 0);

INSERT INTO messages (thread, content) VALUES (1, 'Jotain muuta...');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (2, 2, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 2, 1);

INSERT INTO messages (thread, content) VALUES (1, 'Mitä muuta?');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (3, 3, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 3, 2);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (2, 3, 1);

INSERT INTO messages (thread, content) VALUES (1, 'Vielä yksi viesti.');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (4, 4, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 4, 1);


INSERT INTO threads (title) VALUES ('Joku toinen keskustelu');

INSERT INTO messages (thread, content) VALUES (2, 'Pöö');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (5, 5, 0);
