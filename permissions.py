from sqlalchemy.sql import text
from db import db

def get_permitted_users(subforum_id : int):
    sql = text(
        "SELECT U.id, U.username "
        "FROM permissions P "
        "JOIN users U ON U.id = P.uid AND NOT U.admin "
        "WHERE P.subforum = :subforum "
        "ORDER BY U.username"
    )
    return db.session.execute(sql, {"subforum": subforum_id}).fetchall()

def get_blocked_users(subforum_id : int):
    sql = text(
        "SELECT U.id, U.username "
        "FROM users U "
        "LEFT JOIN permissions P ON P.uid = U.id AND P.subforum = :subforum "
        "WHERE NOT U.admin "
        "GROUP BY U.id HAVING COUNT(P.uid) = 0 "
        "ORDER BY U.username"
    )
    return db.session.execute(sql, {"subforum": subforum_id}).fetchall()

def add_permission(uid : int, subforum : int):
    sql = text(
        "INSERT INTO permissions (uid, subforum) VALUES (:uid, :subforum)"
    )
    db.session.execute(sql, {"uid": uid, "subforum": subforum})
    db.session.commit()

def delete_permission(uid : int, subforum : int):
    sql = text(
        "DELETE FROM permissions WHERE uid = :uid AND subforum = :subforum"
    )
    db.session.execute(sql, {"uid": uid, "subforum": subforum})
    db.session.commit()
