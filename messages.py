import itertools
from sqlalchemy.sql import text
from db import db

def get_msg(msg_id : int):
    sql = text(
        "SELECT M.id, M.content, M.thread, M.uid, U.username "
        "FROM messages M JOIN users U "
        "ON M.id = :msg_id AND U.id = M.uid"
    )
    return db.session.execute(sql, {"msg_id": msg_id}).fetchone()

def get_replies(msg_id : int):
    sql = text(
        "SELECT descendant AS id "
        "FROM message_tree_paths "
        "WHERE ancestor = :msg_id AND depth = 1"
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

def is_1st_msg_in_thr(msg_id : int):
    sql = text(
        "SELECT COUNT(*) AS paths "
        "FROM message_tree_paths "
        "WHERE descendant = :msg_id"
    )
    path_count = db.session.execute(sql, {"msg_id": msg_id}).fetchone().paths
    return path_count == 1

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

def search(search_terms : str):
    term_combos = itertools.permutations(search_terms)
    combo_patterns = [r"\W(.*\W)?".join(combo) for combo in term_combos]
    pattern = r"(^|\W)" + "|".join(combo_patterns) + r"($|\W)"

    sql = text(
        "SELECT M.id, M.content, U.username, M.thread, T.title AS thr_title "
        "FROM messages M "
        "JOIN users U ON U.id = M.uid "
        "JOIN threads T ON T.id = M.thread "
        "WHERE M.content ~* :pattern"
    )
    return db.session.execute(sql, {"pattern": pattern}).fetchall()
