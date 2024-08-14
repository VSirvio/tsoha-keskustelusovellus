from sqlalchemy.sql import text
from sqlalchemy.engine import Row
from db import db
import config

def get_subforums(cur_user : Row):
    sql = text(
        "SELECT F.id, F.title, F.description, F.secret,"
        " COUNT(DISTINCT T.id) AS threads,"
        " COUNT(M.id) AS messages,"
        " TO_CHAR(MAX(M.sent), :date_format) AS latest "
        "FROM subforums F "
        "LEFT JOIN threads T ON F.id = T.subforum "
        "LEFT JOIN messages M ON T.id = M.thread "
        "LEFT JOIN permissions P ON P.uid = :cur_user AND P.subforum = F.id "
        "GROUP BY F.id HAVING (NOT F.secret) OR :is_admin OR COUNT(P.uid) > 0 "
        "ORDER BY F.id"
    )
    params = {
        "date_format": config.DATE_FORMAT,
        "cur_user": cur_user.id,
        "is_admin": cur_user.admin
    }
    return db.session.execute(sql, params).fetchall()

def get_subforum(subforum_id : int):
    sql = text(
        "SELECT id, title, description, secret FROM subforums WHERE id = :id"
    )
    return db.session.execute(sql, {"id": subforum_id}).fetchone()

def is_permitted(subforum_id : int, user : Row):
    if user.admin:
        return True

    sql = text(
        "SELECT (NOT F.secret) OR COUNT(P.uid) > 0 AS is_permitted "
        "FROM subforums F "
        "LEFT JOIN permissions P ON P.uid = :uid AND P.subforum = F.id "
        "WHERE F.id = :subforum "
        "GROUP BY F.id"
    )
    params = {"uid": user.id, "subforum": subforum_id}
    return db.session.execute(sql, params).fetchone().is_permitted

def new_subforum(title : str, desc : str, is_secret : bool):
    sql = text(
        "INSERT INTO subforums (title, description, secret)"
        " VALUES (:title, :desc, :is_secret)"
    )
    params = {"title": title, "desc": desc, "is_secret": is_secret}
    db.session.execute(sql, params)
    db.session.commit()

def delete_subforum(subforum_id : int):
    sql = text("DELETE FROM subforums WHERE id = :id")
    db.session.execute(sql, {"id": subforum_id})
    db.session.commit()
