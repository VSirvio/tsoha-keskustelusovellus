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
