from sqlalchemy.sql import text
from db import db

def get_msg(msg_id : int):
    sql = text(
        "SELECT content, thread, uid, username "
        "FROM messages JOIN users "
        "ON messages.id = :msg_id AND users.id = messages.uid"
    )
    return db.session.execute(sql, {"msg_id": msg_id}).fetchone()

def get_replies(msg_id : int):
    sql = text(
        "SELECT descendant AS id "
        "FROM message_tree_paths "
        "WHERE ancestor = :msg_id AND depth = 1"
    )
    return db.session.execute(sql, {"msg_id": msg_id}).fetchall()

def get_thr_id(msg_id : int):
    sql = text("SELECT thread FROM messages WHERE id = :msg_id")
    return db.session.execute(sql, {"msg_id": msg_id}).fetchone().thread

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

def delete_msg(msg_id : int):
    sql = text(
        "DELETE FROM messages WHERE id IN ("
        " SELECT descendant FROM message_tree_paths WHERE ancestor = :msg_id"
        ")"
    )
    db.session.execute(sql, {"msg_id": msg_id})
    db.session.commit()
