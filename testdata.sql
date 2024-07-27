-- username: Test user 1
-- password: 12345
INSERT INTO users (username, password) VALUES ('Test user 1', 'scrypt:32768:8:1$QZcFXcdiLfhqsAZg$10288da3121ac08d1b133bf50429f5b09060b95dab3f07488f5711eac6e928e00a6eba45c8b1a90dff42c24843aa2f159debeea398b609d3c50a800ba542bc83');

-- username: Test user 2
-- password: 00000
INSERT INTO users (username, password) VALUES ('Test user 2', 'scrypt:32768:8:1$0WHsQVBijRO3ytem$9729bb758e59a21a26aef46d61c753a5d34ee2a307abe5f112121a89b512e19bd134fab49ab6166932ce66a6a3ae59ea15ffb4c15e8fac40077c4e0eb2bee207');


INSERT INTO subforums (title, description) VALUES ('Yleinen', 'Kaikki yleinen keskustelu');


INSERT INTO threads (uid, subforum, title) VALUES (1, 1, 'Joku keskustelu');

INSERT INTO messages (uid, thread, content) VALUES (1, 1, 'Terve, maailma!');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 1, 0);

INSERT INTO messages (uid, thread, content) VALUES (2, 1, 'Jotain muuta...');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (2, 2, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 2, 1);

INSERT INTO messages (uid, thread, content) VALUES (1, 1, 'Mitä muuta?');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (3, 3, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 3, 2);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (2, 3, 1);

INSERT INTO messages (uid, thread, content) VALUES (1, 1, 'Vielä yksi viesti.');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (4, 4, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 4, 1);


INSERT INTO threads (uid, subforum, title) VALUES (1, 1, 'Joku toinen keskustelu');

INSERT INTO messages (uid, thread, content) VALUES (1, 2, 'Pöö');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (5, 5, 0);


INSERT INTO subforums (title, description) VALUES ('Satunnainen', 'Kaikki muut keskustelut');


INSERT INTO threads (uid, subforum, title) VALUES (1, 2, 'Satunnainen keskustelu');

INSERT INTO messages (uid, thread, content) VALUES (1, 3, 'Random viesti.');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (6, 6, 0);
