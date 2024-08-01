from sqlalchemy.sql import text
from db import db

def unlike(uid : int, msg_id : int):
    sql = text("DELETE FROM likes WHERE uid = :uid AND message = :msg_id")
    db.session.execute(sql, {"uid": uid, "msg_id": msg_id})
    db.session.commit()

def like(uid: int, msg_id : int):
    unlike(uid, msg_id)

    sql = text(
        "INSERT INTO likes (uid, message, value) VALUES (:uid, :msg_id, 1)"
    )
    db.session.execute(sql, {"uid": uid, "msg_id": msg_id})
    db.session.commit()

def dislike(uid: int, msg_id : int):
    unlike(uid, msg_id)

    sql = text(
        "INSERT INTO likes (uid, message, value) VALUES (:uid, :msg_id, -1)"
    )
    db.session.execute(sql, {"uid": uid, "msg_id": msg_id})
    db.session.commit()

def get_total_likes(msg_id : int):
    sql = text(
        "SELECT COALESCE(SUM(value),0) AS total "
        "FROM likes WHERE message = :msg_id"
    )
    return db.session.execute(sql, {"msg_id": msg_id}).fetchone().total

def voted_by_user(msg_id : int, uid : int):
    sql = text("SELECT * FROM likes WHERE uid = :uid AND message = :msg_id")
    params = {"uid": uid, "msg_id": msg_id}
    own_likes = db.session.execute(sql, params).fetchone()
    return own_likes is not None
