from sqlalchemy.sql import text
from db import db

def get_threads(subforum_id : int):
    sql = text("SELECT id, uid, title FROM threads WHERE subforum = :subforum")
    return db.session.execute(sql, {"subforum": subforum_id}).fetchall()

def get_thread(thr_id : int):
    sql = text("SELECT uid, subforum, title FROM threads WHERE id = :thr_id")
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

def delete_thr(thr_id : int):
    sql = text("DELETE FROM threads WHERE id = :thr_id")
    db.session.execute(sql, {"thr_id": thr_id})
    db.session.commit()
