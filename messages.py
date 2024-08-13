from sqlalchemy.sql import text
from db import db

def get_msg(msg_id : int):
    sql = text(
        "SELECT M.id, M.content, M.thread, M.uid, U.username "
        "FROM messages M JOIN users U "
        "ON M.id = :msg_id AND U.id = M.uid"
    )
    return db.session.execute(sql, {"msg_id": msg_id}).fetchone()

def get_replies(msg_id : int, order_by : str):
    order = "sent DESC"
    match order_by:
        case "oldest":
            order = "sent ASC"
        case "most_liked":
            order = "likes DESC"
        case "most_disliked":
            order = "likes ASC"

    sql = text(
        "SELECT descendant AS id, M.sent, COALESCE(SUM(L.value),0) AS likes "
        "FROM message_tree_paths "
        "LEFT JOIN messages M ON M.id = descendant "
        "LEFT JOIN likes L ON L.message = M.id "
        "WHERE ancestor = :msg_id AND depth = 1 "
        "GROUP BY descendant, M.sent ORDER BY " + order
    )
    return db.session.execute(sql, {"msg_id": msg_id}).fetchall()

def new_msg(orig_id : int, uid : int, thr_id : int, content : str):
    sql = text(
        "INSERT INTO messages "
        "(uid, thread, content) VALUES (:uid, :thr, :content) "
        "RETURNING id"
    )
    params = {"uid": uid, "thr": thr_id, "content": content}
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

def is_1st_msg_in_thr(msg_id : int):
    sql = text(
        "SELECT M.id = T.first_msg AS is_first FROM messages M "
        "JOIN threads T ON T.id = M.thread "
        "WHERE M.id = :msg_id"
    )
    return db.session.execute(sql, {"msg_id": msg_id}).fetchone().is_first

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

def search(search_terms : list[str]):
    sql = text(
        "SELECT M.id, M.content, U.username, M.thread, T.title AS thr_title "
        "FROM messages M "
        "JOIN users U ON U.id = M.uid "
        "JOIN threads T ON T.id = M.thread "
        "WHERE regexp_split_to_array(lower(content), '\\W+') @> :search_terms"
    )
    return db.session.execute(sql, {"search_terms": search_terms}).fetchall()
