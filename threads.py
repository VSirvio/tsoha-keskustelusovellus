from sqlalchemy.sql import text
from db import db
import messages

def get_thrs(subforum_id : int, order_by : str):
    order = "last_msg DESC"
    match order_by:
        case "oldest":
            order = "last_msg ASC"
        case "most_liked":
            order = "likes DESC"
        case "most_disliked":
            order = "likes ASC"

    sql = text(
        "SELECT T.id, T.uid, T.title, U.username, L.last_msg,"
        " TO_CHAR(L.last_msg, 'DD.MM.YYYY klo HH24:MI') AS time_str,"
        " COALESCE(SUM(I.value),0) AS likes "
        "FROM threads T "
        "LEFT JOIN users U ON U.id = T.uid "
        "LEFT JOIN likes I ON I.message = T.first_msg "
        "LEFT JOIN ("
        " SELECT M.thread, MAX(M.sent) AS last_msg"
        " FROM messages M GROUP BY thread "
        ") L ON L.thread = T.id "
        "WHERE T.subforum = :subforum "
        "GROUP BY T.id, U.username, L.last_msg ORDER BY " + order
    )
    return db.session.execute(sql, {"subforum": subforum_id}).fetchall()

def get_thr(thr_id : int):
    sql = text(
        "SELECT T.id, T.uid, U.username, T.subforum, T.title, T.first_msg "
        "FROM threads T JOIN users U "
        "ON T.id = :thr_id AND U.id = T.uid"
    )
    return db.session.execute(sql, {"thr_id": thr_id}).fetchone()

def get_subforum_id(thr_id : int):
    sql = text("SELECT subforum FROM threads WHERE id = :thr_id")
    return db.session.execute(sql, {"thr_id": thr_id}).fetchone().subforum

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
