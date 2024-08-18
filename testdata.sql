BEGIN;


-- username: User1
-- password: 12345
INSERT INTO users (username, password) VALUES ('User1', 'scrypt:32768:8:1$QZcFXcdiLfhqsAZg$10288da3121ac08d1b133bf50429f5b09060b95dab3f07488f5711eac6e928e00a6eba45c8b1a90dff42c24843aa2f159debeea398b609d3c50a800ba542bc83');

-- username: User2
-- password: 00000
INSERT INTO users (username, password) VALUES ('User2', 'scrypt:32768:8:1$0WHsQVBijRO3ytem$9729bb758e59a21a26aef46d61c753a5d34ee2a307abe5f112121a89b512e19bd134fab49ab6166932ce66a6a3ae59ea15ffb4c15e8fac40077c4e0eb2bee207');

-- username: Admin
-- password: asdasd
INSERT INTO users (username, password, admin) VALUES ('Admin', 'scrypt:32768:8:1$BUVPu9AjiLouxZCP$e8d5795f1f420eb38575b4a82ecd25ee3b3d4556036e16162ffd5e06f796cbc5738da3e40b25897e56f398e9daafdf9d4dc6ac14c955001e6b3618625cd829fb', TRUE);


INSERT INTO subforums (title, description) VALUES ('Yleinen', 'Kaikki yleinen keskustelu');


INSERT INTO threads (uid, subforum, title, first_msg) VALUES (1, 1, 'Joku keskustelu', 1);

INSERT INTO messages (uid, thread, content, sent) VALUES (1, 1, 'Terve, maailma!', '2024-07-31 14:01:38.930457');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 1, 0);
INSERT INTO likes (uid, message, value) VALUES (1, 1, 1);

INSERT INTO messages (uid, thread, content, sent) VALUES (2, 1, 'Jotain muuta...', '2024-08-02 05:23:23.854873');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (2, 2, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 2, 1);

INSERT INTO messages (uid, thread, content, sent) VALUES (1, 1, 'Mitä muuta?', '2024-08-03 23:51:18.993457');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (3, 3, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 3, 2);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (2, 3, 1);
INSERT INTO likes (uid, message, value) VALUES (1, 3, -1);
INSERT INTO likes (uid, message, value) VALUES (2, 3, 1);

INSERT INTO messages (uid, thread, content, sent) VALUES (1, 1, 'Tämä on viesti', '2024-08-05 10:00:04.000128');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (4, 4, 0);
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (1, 4, 1);


INSERT INTO threads (uid, subforum, title, first_msg) VALUES (1, 1, 'Hauki on kala', 5);

INSERT INTO messages (uid, thread, content, sent) VALUES (1, 2, 'Pöö', '2024-08-06 15:55:41.034501');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (5, 5, 0);


INSERT INTO subforums (title, description) VALUES ('Satunnainen', 'Kaikki muu keskustelu');


INSERT INTO threads (uid, subforum, title, first_msg) VALUES (1, 2, 'Satunnainen keskustelu', 6);

INSERT INTO messages (uid, thread, content, sent) VALUES (1, 3, 'Random viesti.', '2024-08-10 13:15:45.055162');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (6, 6, 0);


INSERT INTO subforums (title, description, secret) VALUES ('Salainen', 'Auki vain harvoille ja valituille', TRUE);


INSERT INTO threads (uid, subforum, title, first_msg) VALUES (3, 3, 'Salaisuuksia', 7);

INSERT INTO messages (uid, thread, content, sent) VALUES (3, 4, 'Vastaus perimmäiseen kysymykseen elämästä, maailmankaikkeudesta ja kaikesta on 42.', '2024-08-14 13:52:30.134895');
INSERT INTO message_tree_paths (ancestor, descendant, depth) VALUES (7, 7, 0);


INSERT INTO permissions (uid, subforum) VALUES (2, 3);


COMMIT;
