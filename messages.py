from sqlalchemy.sql import text
from sqlalchemy.engine import Row
from db import db
import config

def get_msg(msg_id : int):
    sql = text("SELECT id, content, thread, uid FROM messages WHERE id = :id")
    return db.session.execute(sql, {"id": msg_id}).fetchone()

def get_tree(root_msg : int, cur_user : int, order_by : str):
    order = "sent DESC"
    match order_by:
        case "oldest":
            order = "sent ASC"
        case "most_liked":
            order = "likes DESC"
        case "most_disliked":
            order = "likes ASC"

    sql = text(
        "SELECT M.id, M.content, U.username AS user, M.sent,"
        " TO_CHAR(M.sent, :date_format) AS time_str,"
        " ("
        "  SELECT COALESCE(SUM(L.value),0)"
        "  FROM likes L WHERE L.message = M.id "
        " ) AS likes,"
        " ("
        "  SELECT COUNT(I.value) > 0"
        "  FROM likes I WHERE I.message = M.id AND I.uid = :cur_user "
        " ) AS liked,"
        " ("
        "  SELECT COALESCE(ARRAY_AGG(D.descendant),ARRAY[]::INT[])"
        "  FROM message_tree_paths D WHERE D.ancestor = M.id AND D.depth = 1 "
        " ) AS replies "
        "FROM message_tree_paths P "
        "JOIN messages M ON M.id = P.descendant "
        "JOIN users U ON U.id = M.uid "
        "WHERE P.ancestor = :root_msg "
        "GROUP BY M.id, U.username ORDER BY " + order
    )
    params = {
        "date_format": config.DATE_FORMAT,
        "cur_user": cur_user,
        "root_msg": root_msg
    }
    return db.session.execute(sql, params).fetchall()

def new_msg(orig_id : int, uid : int, content : str):
    sql = text(
        "INSERT INTO messages "
        "(uid, thread, content) "
        "SELECT :uid, M.thread, :content"
        " FROM messages M"
        " WHERE M.id = :orig_id "
        "RETURNING id"
    )
    params = {"uid": uid, "orig_id": orig_id, "content": content}
    msg = db.session.execute(sql, params).fetchone()
    db.session.commit()

    sql = text(
        "INSERT INTO message_tree_paths "
        "(ancestor, descendant, depth) VALUES (:msg_id, :msg_id, 0)"
    )
    db.session.execute(sql, {"msg_id": msg.id})
    sql = text(
        "INSERT INTO message_tree_paths "
        "(ancestor, descendant, depth) "
        "SELECT ancestor, :msg_id, depth + 1"
        " FROM message_tree_paths"
        " WHERE descendant = :orig_id"
    )
    db.session.execute(sql, {"msg_id": msg.id, "orig_id": orig_id})
    db.session.commit()

    return msg.id

def edit_msg(msg_id : int, content : str):
    sql = text("UPDATE messages SET content = :content WHERE id = :id")
    db.session.execute(sql, {"content": content, "id": msg_id})
    db.session.commit()

def delete_msg(msg_id : int):
    sql = text(
        "DELETE FROM messages WHERE id IN ("
        " SELECT descendant FROM message_tree_paths WHERE ancestor = :msg_id"
        ")"
    )
    db.session.execute(sql, {"msg_id": msg_id})
    db.session.commit()

def search(search_term : str, cur_username : str):
    sql = text(
        "SELECT M.id, M.content, U.username, M.thread, T.title AS thr_title "
        "FROM messages M "
        "LEFT JOIN users U ON U.id = M.uid "
        "LEFT JOIN users C ON C.username = :cur_username "
        "LEFT JOIN threads T ON T.id = M.thread "
        "LEFT JOIN subforums F ON F.id = T.subforum "
        "LEFT JOIN permissions P ON P.uid = C.id AND P.subforum = F.id "
        "WHERE content LIKE :search_term "
        "GROUP BY M.id, U.id, C.id, T.id, F.id "
        "HAVING (NOT F.secret) OR C.admin OR COUNT(P.uid) > 0"
    )
    params = {"cur_username": cur_username, "search_term": f"%{search_term}%"}
    return db.session.execute(sql, params).fetchall()
