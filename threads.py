from sqlalchemy.sql import text
from db import db

def get_thrs(subforum_id : int):
    sql = text(
        "SELECT T.id, T.uid, U.username, T.title "
        "FROM threads T JOIN users U "
        "ON T.subforum = :subforum AND U.id = T.uid "
        "ORDER BY T.id"
    )
    return db.session.execute(sql, {"subforum": subforum_id}).fetchall()

def get_thr(thr_id : int):
    sql = text(
        "SELECT T.uid, U.username, T.subforum, T.title "
        "FROM threads T JOIN users U "
        "ON T.id = :thr_id AND U.id = T.uid"
    )
    return db.session.execute(sql, {"thr_id": thr_id}).fetchone()

def get_subforum_id(thr_id : int):
    sql = text("SELECT subforum FROM threads WHERE id = :thr_id")
    return db.session.execute(sql, {"thr_id": thr_id}).fetchone().subforum

def get_1st_msg_id(thr_id : int):
    sql = text(
        "SELECT id FROM messages WHERE thread = :thr_id AND"
        " (SELECT COUNT(*) FROM message_tree_paths WHERE descendant = id) = 1"
    )
    return db.session.execute(sql, {"thr_id": thr_id}).fetchone().id

def new_thr(uid : int, subforum_id : int, title : str):
    sql = text(
        "INSERT INTO threads "
        "(uid, subforum, title) VALUES (:uid, :subforum_id, :title) "
        "RETURNING id"
    )
    params = {"uid": uid, "subforum_id": subforum_id, "title": title}
    thr = db.session.execute(sql, params).fetchone()
    db.session.commit()
    return thr.id

def delete_thr(thr_id : int):
    sql = text("DELETE FROM threads WHERE id = :thr_id")
    db.session.execute(sql, {"thr_id": thr_id})
    db.session.commit()
