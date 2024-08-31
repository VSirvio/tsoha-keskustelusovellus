from sqlalchemy.sql import text

import config
import messages
from db import db

def get_thrs(subforum_id : int, order_by : str):
    order = "last_msg DESC"
    match order_by:
        case "oldest":
            order = "last_msg ASC"
        case "most_liked":
            order = "first_msg_likes DESC, last_msg DESC"
        case "most_disliked":
            order = "first_msg_likes ASC, last_msg DESC"

    sql = text(
        "SELECT T.id, T.title, MAX(M.sent) AS last_msg,"
        " TO_CHAR(MAX(M.sent), :date_format) AS time_str,"
        " ("
        "  SELECT COALESCE(SUM(L.value),0)"
        "  FROM likes L"
        "  WHERE L.message = T.first_msg "
        " ) AS first_msg_likes "
        "FROM threads T "
        "JOIN messages M ON M.thread = T.id "
        "WHERE T.subforum = :subforum "
        "GROUP BY T.id ORDER BY " + order
    )
    params = {"date_format": config.DATE_FORMAT, "subforum": subforum_id}
    return db.session.execute(sql, params).fetchall()

def get_thr(thr_id : int):
    sql = text(
        "SELECT T.id, T.uid, U.username, T.subforum, T.title, T.first_msg "
        "FROM threads T JOIN users U "
        "ON T.id = :thr_id AND U.id = T.uid"
    )
    return db.session.execute(sql, {"thr_id": thr_id}).fetchone()

def new_thr(uid : int, subforum_id : int, title : str, msg : str):
    sql = text(
        "INSERT INTO threads "
        "(uid, subforum, title) VALUES (:uid, :subforum_id, :title) "
        "RETURNING id"
    )
    params = {"uid": uid, "subforum_id": subforum_id, "title": title}
    thr = db.session.execute(sql, params).fetchone()
    db.session.commit()

    msg_id = messages.new_msg(None, uid, thr.id, msg)

    sql = text("UPDATE threads SET first_msg = :first_msg WHERE id = :id")
    db.session.execute(sql, {"first_msg": msg_id, "id": thr.id})
    db.session.commit()

    return thr.id

def edit_thr(thr_id : int, title : str):
    sql = text("UPDATE threads SET title = :title WHERE id = :id")
    db.session.execute(sql, {"title": title, "id": thr_id})
    db.session.commit()

def delete_thr(thr_id : int):
    sql = text("DELETE FROM threads WHERE id = :thr_id")
    db.session.execute(sql, {"thr_id": thr_id})
    db.session.commit()
